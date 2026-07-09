import re
from datetime import date
import requests


# バッチが管理するタグのプレフィックス。既存の業務タグとの衝突を避ける。
_TAG_PREFIX = "sec_"


class ZabbixClient:
    def __init__(self, url: str, user: str | None = None, password: str | None = None, token: str | None = None):
        """user+password（従来の日次バッチ用）または token（APIトークン、失効・ローテーションが
        容易なため管理系スクリプトではこちらを推奨）のいずれかで認証する。
        """
        self.url = url
        self.auth = None
        self._token = token
        self._id = 0
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
        r = requests.post(self.url, json=payload, headers=headers, timeout=30)
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

    def write_back_risk(self, hostid: str, risk_level: str, eol_info: dict | None, cves: list[dict]) -> None:
        """セキュリティリスク情報をホストタグ・インベントリに書き戻す。

        管理タグ（sec_ プレフィックス）のみ更新し、既存の業務タグは保持する。
        """
        # 既存タグを取得して業務タグを保持
        existing = self._req("host.get", {
            "hostids": hostid,
            "output": ["hostid"],
            "selectTags": "extend",
        })
        current_tags: list[dict] = existing[0].get("tags", []) if existing else []
        preserved = [t for t in current_tags if not t["tag"].startswith(_TAG_PREFIX)]

        # 新しいセキュリティタグを構築
        today = date.today().isoformat()
        exploited_count = sum(1 for c in cves if c.get("actively_exploited"))
        new_tags = [
            {"tag": f"{_TAG_PREFIX}risk",          "value": risk_level},
            {"tag": f"{_TAG_PREFIX}cve_count",     "value": str(len(cves))},
            {"tag": f"{_TAG_PREFIX}kev_count",     "value": str(exploited_count)},
            {"tag": f"{_TAG_PREFIX}checked_date",  "value": today},
        ]
        if eol_info and eol_info.get("eol_date"):
            new_tags.append({"tag": f"{_TAG_PREFIX}eol_date", "value": eol_info["eol_date"]})
        if eol_info and eol_info.get("is_eol"):
            new_tags.append({"tag": f"{_TAG_PREFIX}is_eol", "value": "true"})

        # インベントリ notes にサマリーテキストを書き込む
        eol_str = ""
        if eol_info:
            if eol_info.get("is_eol"):
                eol_str = " | EoL: 済み"
            elif eol_info.get("eol_date"):
                eol_str = f" | EoS: {eol_info['eol_date']}"
        kev_str = f" (KEV:{exploited_count}件)" if exploited_count else ""
        notes = f"[セキュリティ] リスク:{risk_level} | CVE:{len(cves)}件{kev_str}{eol_str} | 確認:{today}"

        inventory = {"notes": notes}
        if eol_info and eol_info.get("eol_date"):
            inventory["date_hw_expiry"] = eol_info["eol_date"]

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
