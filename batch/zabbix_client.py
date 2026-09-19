import re
from datetime import date
import requests


# バッチが管理するタグのプレフィックス。既存の業務タグとの衝突を避ける。
_TAG_PREFIX = "sec_"


class ZabbixClient:
    def __init__(
        self,
        url: str,
        user: str | None = None,
        password: str | None = None,
        token: str | None = None,
        host_header: str | None = None,
    ):
        """user+password（従来の日次バッチ用）または token（APIトークン、失効・ローテーションが
        容易なため管理系スクリプトではこちらを推奨）のいずれかで認証する。

        host_header: VPCコネクタ経由でzabbix-serverの内部IPへ直接接続する場合のみ指定する
        （urlに内部IPを指定した上で、TLS証明書はFQDN向けのためホスト名検証は失敗する。
        msp-customer-portal/src/services/zabbixClient.ts の同名の仕組みと同じ対応で、
        SSL検証を無効化しHostヘッダーでFQDNを送る。公開ホスト名で到達できる環境
        （msp-frontend-server上での従来運用等）では未指定のままでよい）。
        """
        self.url = url
        self.auth = None
        self._token = token
        self._id = 0
        self._host_header = host_header
        if not token:
            self._login(user, password)

    def _req(self, method: str, params: dict):
        self._id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self._id,
        }
        headers = {"Content-Type": "application/json-rpc"}
        # apiinfo.version は仕様上 auth パラメータ付きでは呼び出せない
        if method == "apiinfo.version":
            pass
        elif self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        elif self.auth:
            payload["auth"] = self.auth
        if self._host_header:
            headers["Host"] = self._host_header
        r = requests.post(
            self.url, json=payload, headers=headers, timeout=30,
            verify=not self._host_header,  # 内部IP直結時のみ自己署名証明書のためSSL検証を無効化
        )
        r.raise_for_status()
        body = r.json()
        if "error" in body:
            raise RuntimeError(f"Zabbix API error [{method}]: {body['error']}")
        return body["result"]

    def call(self, method: str, params: dict):
        """任意のZabbix API呼び出し用の公開ラッパー（管理系スクリプトから利用）。"""
        return self._req(method, params)

    def _login(self, user: str, password: str):
        self.auth = self._req("user.login", {"username": user, "password": password})

    def get_hosts_inventory(self) -> list[dict]:
        """インベントリが設定済みの全ホストを取得する。

        返却フィールド:
          host           - ホスト名
          name           - 表示名
          inventory.vendor        - ベンダー
          inventory.model         - モデル
          inventory.software_full - FW / ソフトウェア (Full details)
        """
        hosts = self._req("host.get", {
            "output": ["hostid", "host", "name"],
            "selectInventory": ["vendor", "model", "software_full"],
        })
        # インベントリが空配列（インベントリ無効ホスト）を除外
        return [h for h in hosts if isinstance(h.get("inventory"), dict)]

    def write_back_risk(
        self,
        hostid: str,
        risk_level: str,
        cve_status: str,
        hw_eol_info: dict,
        sw_eol_info: dict,
        cves: list[dict],
        cve_counts: dict | None = None,
    ) -> None:
        """セキュリティリスク情報をホストタグ・インベントリに書き戻す。

        管理タグ（sec_ プレフィックス）のみ更新し、既存の業務タグは保持する。
        cve_status・hw_eol_info["status"]・sw_eol_info["status"]は
        "confirmed"/"fuzzy_match"/"unknown"のいずれか（"unknown"は「未確認」であり
        「問題なし」ではないことを、レポート側で区別するために書き戻す）。
        """
        # 既存タグを取得して業務タグを保持
        existing = self._req("host.get", {
            "hostids": hostid,
            "output": ["hostid"],
            "selectTags": "extend",
        })
        current_tags: list[dict] = existing[0].get("tags", []) if existing else []
        # host.get(selectTags="extend")は"automatic"(テンプレート由来か手動かを示す読み取り専用
        # フィールド)を含むが、host.updateへ送り返すtagsにはこれを含められない(Invalid parameter
        # エラーになる)。tag/valueのみに絞って渡す。テンプレートリンクでタグが自動付与される
        # ホストが増えるまで顕在化しなかった不具合(2026-08-26判明)。
        preserved = [
            {"tag": t["tag"], "value": t["value"]} for t in current_tags if not t["tag"].startswith(_TAG_PREFIX)
        ]

        # 新しいセキュリティタグを構築
        today = date.today().isoformat()
        cve_counts = cve_counts or {}
        confirmed_count = int(cve_counts.get("confirmed_affected", len(cves)))
        potential_count = int(cve_counts.get("potentially_affected", 0))
        not_assessable_count = int(cve_counts.get("not_assessable", 0))
        relevant_cves = [c for c in cves if c.get("applicability_status") == "confirmed_affected"] or cves
        exploited_count = sum(1 for c in relevant_cves if c.get("actively_exploited"))
        new_tags = [
            {"tag": f"{_TAG_PREFIX}risk",          "value": risk_level},
            # Backward-compatible: existing report reads sec_cve_count. It now means confirmed affected only.
            {"tag": f"{_TAG_PREFIX}cve_count",     "value": str(confirmed_count)},
            {"tag": f"{_TAG_PREFIX}cve_confirmed_count", "value": str(confirmed_count)},
            {"tag": f"{_TAG_PREFIX}cve_potential_count", "value": str(potential_count)},
            {"tag": f"{_TAG_PREFIX}cve_not_assessable_count", "value": str(not_assessable_count)},
            {"tag": f"{_TAG_PREFIX}cve_status",    "value": cve_status},
            {"tag": f"{_TAG_PREFIX}kev_count",     "value": str(exploited_count)},
            {"tag": f"{_TAG_PREFIX}checked_date",  "value": today},
            {"tag": f"{_TAG_PREFIX}hw_eol_status", "value": hw_eol_info.get("status", "unknown")},
            {"tag": f"{_TAG_PREFIX}sw_eol_status", "value": sw_eol_info.get("status", "unknown")},
        ]
        if hw_eol_info.get("eol_date"):
            new_tags.append({"tag": f"{_TAG_PREFIX}hw_eol_date", "value": hw_eol_info["eol_date"]})
        if hw_eol_info.get("is_eol"):
            new_tags.append({"tag": f"{_TAG_PREFIX}hw_is_eol", "value": "true"})
        if sw_eol_info.get("eol_date"):
            new_tags.append({"tag": f"{_TAG_PREFIX}sw_eol_date", "value": sw_eol_info["eol_date"]})
        if sw_eol_info.get("is_eol"):
            new_tags.append({"tag": f"{_TAG_PREFIX}sw_is_eol", "value": "true"})

        # インベントリ notes にサマリーテキストを書き込む
        def _eol_summary(label: str, eol_info: dict) -> str:
            if eol_info.get("status") == "unknown":
                return ""
            suffix = "(要確認)" if eol_info.get("status") == "fuzzy_match" else ""
            if eol_info.get("is_eol"):
                return f" | {label}EoL: 済み{suffix}"
            if eol_info.get("eol_date"):
                return f" | {label}EoS: {eol_info['eol_date']}{suffix}"
            return ""

        eol_str = _eol_summary("HW", hw_eol_info) + _eol_summary("SW", sw_eol_info)
        cve_note = (f"CVE影響確認:{confirmed_count}件 / 可能性:{potential_count}件 / 判定不能:{not_assessable_count}件"\n                    if cve_status == "ok" else "CVE:検索失敗")
        kev_str = f" (KEV:{exploited_count}件)" if exploited_count else ""
        notes = f"[セキュリティ] リスク:{risk_level} | {cve_note}{kev_str}{eol_str} | 確認:{today}"

        inventory = {"notes": notes}
        if hw_eol_info.get("eol_date"):
            inventory["date_hw_expiry"] = hw_eol_info["eol_date"]

        self._req("host.update", {
            "hostid": hostid,
            "tags": preserved + new_tags,
            "inventory": inventory,
        })

    def get_lldp_neighbors(self, hostids: list[str]) -> dict[str, list[dict]]:
        """LLDPネイバー情報（lldp.rem.sysname系アイテム）をホストごとに取得する。

        新規機器検知（未知のLLDPネイバーの新規出現検知）専用。atlib_monthly_report.html の
        バカハブ検出・トポロジー図で既に使われているのと同じ lldp.rem.sysname 系アイテムを流用する。
        """
        if not hostids:
            return {}
        items = self._req("item.get", {
            "hostids": hostids,
            "output": ["itemid", "hostid", "key_", "lastvalue"],
            "search": {"key_": "lldp.rem"},
        })
        neighbors: dict[str, list[dict]] = {}
        for item in items:
            if "sysname" not in item["key_"] or not item.get("lastvalue"):
                continue
            m = re.search(r"\[(\d+)", item["key_"])
            port = m.group(1) if m else item["key_"]
            neighbors.setdefault(item["hostid"], []).append({
                "port": port,
                "sysname": item["lastvalue"].strip(),
            })
        return neighbors

    def push_trapper_value(self, hostid: str, key: str, value: str) -> bool:
        """Trapperアイテムへ値を書き込む（history.push）。

        アイテムが対象ホストにまだ作成されていない場合は何もせず False を返す
        （Trapperアイテム・Triggerの新設はZabbix管理画面側で行う前提のため、
        未作成時にバッチを異常終了させない）。
        """
        items = self._req("item.get", {
            "hostids": hostid,
            "output": ["itemid"],
            "filter": {"key_": key},
        })
        if not items:
            return False
        self._req("history.push", {"itemid": items[0]["itemid"], "value": value})
        return True
