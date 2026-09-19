"""CVE / EoL 突合 ＋ LLDP新規ネイバー検知バッチ

使い方:
  python main.py [--config config.yaml] [--dry-run]

出力:
  reports/health_check_YYYYMMDD_HHMMSS.json
  lldp_snapshot.json （LLDPネイバーの前回スナップショット、次回実行時のdiff用）
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

from zabbix_client import ZabbixClient
from cpe_mapper import CpeMapper
from nvd_client import NvdClient, NvdLookupError
from eol_client import EolClient
from version_applicability import evaluate_version

HERE = Path(__file__).parent


def main():
    args = _parse_args()
    config = _load_config(args.config)

    reports_dir = HERE / config.get("output", {}).get("dir", "./reports").lstrip("./")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # ---- 初期化 ----
    nvd_api_key = config.get("nvd", {}).get("api_key", "")

    print("[1/6] Zabbix からホスト情報を取得中...")
    if args.dry_run:
        hosts = _dummy_hosts()
        print("  → ドライランモード: ダミーデータを使用")
    else:
        zabbix = ZabbixClient(
            config["zabbix"]["url"],
            config["zabbix"]["user"],
            config["zabbix"]["password"],
        )
        hosts = zabbix.get_hosts_inventory()
    print(f"  → {len(hosts)} 件のホスト")

    print("[2/6] CISA KEV + NVD クライアントを初期化中...")
    nvd = NvdClient(nvd_api_key)
    print(f"  → CISA KEV: {len(nvd._kev)} 件の悪用確認済み CVE を読み込み済み")

    print("[3/6] CPE マッパーを初期化中...")
    cpe_mapper = CpeMapper(HERE / "cpe_overrides.json", nvd_api_key)

    print("[4/6] EoL クライアントを初期化中...")
    eol_client = EolClient(HERE / "eol_overrides.json")

    # ---- デバイスごとに突合 ----
    print("[5/6] 各デバイスを CVE / EoL と突合中...")
    results = []
    for host in hosts:
        inv = host.get("inventory") or {}
        vendor = inv.get("vendor", "").strip()
        model = inv.get("model", "").strip()
        fw = inv.get("software_full", "").strip()

        if not vendor and not model:
            # 以前はここでcontinueして結果から完全に除外していたが、それだと
            # 「インベントリ未入力で判定できなかった」ホストが集計上どこにも
            # 現れず見落とされる。risk_level="unknown"として結果に含める。
            print(f"  [警告] インベントリ未入力のためスキップ: {host['host']}（unknown扱いで記録）")
            results.append({
                "host": host["host"], "name": host["name"],
                "vendor": vendor, "model": model, "firmware": fw,
                "cpe": None, "cve_source": None, "cve_status": "unknown",
                "hw_eol": {"status": "unknown", "reason": "no_inventory", "is_eol": None, "eol_date": None, "days_until_eol": None},
                "sw_eol": {"status": "unknown", "reason": "no_inventory", "is_eol": None, "eol_date": None, "days_until_eol": None},
                "cves": [], "risk_level": "unknown",
            })
            continue

        device_key = f"{vendor} {model}".strip()
        print(f"  処理中: {host['host']} ({device_key})")

        cpe = cpe_mapper.get_cpe(device_key)

        cve_status = "ok"
        try:
            if cpe:
                cves = nvd.get_cves_by_cpe(cpe)
                cve_source = "cpe"
            else:
                cves = nvd.get_cves_by_keyword(device_key)
                cve_source = "keyword"
        except NvdLookupError:
            # 検索が失敗しただけであり「脆弱性0件」ではない。空リストと区別するため
            # cve_statusを別立てし、_calc_riskが「不明」判定に使う。
            cves = []
            cve_source = None
            cve_status = "lookup_failed"

        cve_counts = _classify_cves(cves, fw, cve_source) if cve_status == "ok" else {\n            "confirmed_affected": 0, "potentially_affected": 0, "not_affected": 0, "not_assessable": 0\n        }\n\n        hw_eol_info = eol_client.get_hw_eol(device_key, model)
        sw_eol_info = eol_client.get_sw_eol(device_key, fw)

        # eol_overrides.jsonのsw.fixed_in_versionが分かっている場合、実機ファームウェアが
        # それ以上かを判定して付記する（表示用の参考情報。risk_levelの自動判定には使わない。
        # 手動overridesの既知CVE件数と、NVD検索結果のCVE件数が必ずしも一致しないため）。
        fixed_in = sw_eol_info.get("fixed_in_version")
        if fixed_in and fw:
            sw_eol_info["patched"] = _version_at_least(fw, fixed_in)

        risk = _calc_risk(cves, cve_status, hw_eol_info, sw_eol_info)

        results.append({
            "host": host["host"],
            "name": host["name"],
            "vendor": vendor,
            "model": model,
            "firmware": fw,
            "cpe": cpe,
            "cve_source": cve_source,
            "cve_status": cve_status,
            "cve_counts": cve_counts,
            "hw_eol": hw_eol_info,
            "sw_eol": sw_eol_info,
            "cves": cves,
            "risk_level": risk,
        })

    # ---- レポート出力 ----
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = reports_dir / f"health_check_{timestamp}.json"
    report = {
        "generated_at": datetime.now().isoformat(),
        "host_count": len(results),
        "results": results,
    }
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n完了: {out_path}")

    # ---- Zabbix 書き戻し ----
    writeback_enabled = config.get("writeback", {}).get("enabled", False)
    if not args.dry_run and writeback_enabled:
        print("\nZabbix にリスク情報を書き戻し中...")
        hostid_map = {h["host"]: h["hostid"] for h in hosts}
        for r in results:
            hostid = hostid_map.get(r["host"])
            if not hostid:
                continue
            try:
                zabbix.write_back_risk(
                    hostid, r["risk_level"], r["cve_status"], r["hw_eol"], r["sw_eol"], r["cves"], r.get("cve_counts"),
                )
                print(f"  書き戻し完了: {r['host']} → {r['risk_level']}")
            except Exception as e:
                print(f"  [警告] 書き戻し失敗 ({r['host']}): {e}")
    elif args.dry_run and writeback_enabled:
        print("\n[ドライラン] Zabbix 書き戻しはスキップ")

    # ---- LLDP新規ネイバー検知 ----
    print("\n[6/6] LLDPネイバーの新規出現を確認中...")
    if args.dry_run:
        print("  → ドライランモード: スキップ（Zabbix接続なしのため）")
    else:
        snapshot_path = HERE / config.get("lldp", {}).get("snapshot_path", "lldp_snapshot.json")
        hostid_map = {h["hostid"]: h["host"] for h in hosts}
        new_neighbors = _detect_new_lldp_neighbors(hosts, zabbix, snapshot_path)
        if new_neighbors:
            print(f"  → {len(new_neighbors)} 台のホストで新規LLDPネイバーを検出:")
            for hostid, fresh in new_neighbors.items():
                names = ", ".join(f"IF{n['port']}:{n['sysname']}" for n in fresh)
                print(f"    - {hostid_map.get(hostid, hostid)}: {names}")
        else:
            print("  → 新規ネイバーなし")

    _print_summary(results)



def _walk_cpe_matches(nodes: list[dict]):
    """Yield vulnerable cpeMatch entries while preserving whether complex logical nodes exist."""
    for node in nodes or []:
        for match in node.get("cpeMatch", []) or []:
            if match.get("vulnerable"):
                yield match
        yield from _walk_cpe_matches(node.get("nodes", []) or [])


def _classify_cves(cves: list[dict], firmware: str, source: str | None) -> dict:
    """Attach conservative firmware applicability to each CVE and return aggregate counts.

    Keyword-only discovery cannot prove product applicability, so it never becomes confirmed.
    Complex NVD AND/negate configuration is intentionally downgraded to potential.
    """
    counts = {"confirmed_affected": 0, "potentially_affected": 0, "not_affected": 0, "not_assessable": 0}
    for cve in cves:
        if source != "cpe":
            status, reason = "potentially_affected", "keyword-only product match"
        elif not firmware:
            status, reason = "not_assessable", "installed firmware missing"
        else:
            configs = cve.get("configurations", []) or []
            complex_logic = any(cfg.get("operator") == "AND" or cfg.get("negate") for cfg in configs)
            matches = list(_walk_cpe_matches(configs))
            if complex_logic:
                status, reason = "potentially_affected", "complex NVD configuration requires review"
            elif not matches:
                status, reason = "potentially_affected", "no evaluable vulnerable CPE criterion"
            else:
                evaluated = [evaluate_version(firmware, m) for m in matches]
                statuses = {e.status for e in evaluated}
                if "confirmed_affected" in statuses:
                    status, reason = "confirmed_affected", "installed firmware satisfies vulnerable NVD criterion"
                elif statuses == {"not_affected"}:
                    status, reason = "not_affected", "installed firmware outside vulnerable NVD criteria"
                elif "potentially_affected" in statuses:
                    status, reason = "potentially_affected", "version comparison or applicability is ambiguous"
                else:
                    status, reason = "not_assessable", "applicability could not be assessed"
        cve["applicability_status"] = status
        cve["applicability_reason"] = reason
        counts[status] += 1
    return counts


# ------------------------------------------------------------------
# リスク判定
# ------------------------------------------------------------------

def _calc_risk(cves: list[dict], cve_status: str, hw_eol_info: dict, sw_eol_info: dict) -> str:
    """risk_levelの出力空間: critical|high|medium|warning|unknown|ok

    "unknown"は、CVE検索が失敗(cve_status!="ok")またはEoL判定がいずれも
    "confirmed"/"fuzzy_match"に至らなかった(status=="unknown")場合に返す。
    ただし確定的な問題(critical/high/medium/warning)が他方から出ていれば、
    そちらを優先する（一部不明が確定済みの危険を覆い隠さないようにするため）。
    "fuzzy_match"は「不明」ではなく「一定の根拠あり」として扱い、is_eol/
    days_until_eolがあれば従来通りcritical/warning判定に使う（ただし
    hw_eol_info/sw_eol_info自体のstatusは呼び出し側でそのまま保持され、
    書き戻し・レポート側で「fuzzy_matchに基づく判定である」旨を表示できる）。
    """
    def _is_determined(eol_info: dict) -> bool:
        return eol_info.get("status") in ("confirmed", "fuzzy_match")

    if _is_determined(hw_eol_info) and hw_eol_info.get("is_eol"):
        return "critical"
    if _is_determined(sw_eol_info) and sw_eol_info.get("is_eol"):
        return "critical"

    if cve_status == "ok":
        confirmed = [c for c in cves if c.get("applicability_status") == "confirmed_affected"]\n        potential = [c for c in cves if c.get("applicability_status") in ("potentially_affected", "not_assessable")]\n        exploited = [c for c in confirmed if c.get("actively_exploited")]\n        critical_cves = [c for c in confirmed if (c.get("cvss_score") or 0) >= 9.0]\n        high_cves = [c for c in confirmed if 7.0 <= (c.get("cvss_score") or 0) < 9.0]\n
        if exploited or critical_cves:
            return "critical"
        if high_cves:
            return "high"
        if confirmed:\n            return "medium"\n        if potential:\n            return "unknown"\n
    for eol_info in (hw_eol_info, sw_eol_info):
        if _is_determined(eol_info) and eol_info.get("days_until_eol") is not None \
                and eol_info["days_until_eol"] <= 90:
            return "warning"

    if cve_status != "ok" or not _is_determined(hw_eol_info) or not _is_determined(sw_eol_info):
        return "unknown"

    return "ok"


def _version_at_least(current: str, minimum: str) -> bool | None:
    """バージョン文字列current がminimum以上かを判定する。単純な数値ドット区切り
    比較で十分なユースケース（ファームウェアバージョン比較）のみ対応する。
    複雑なセマンティックバージョニング（プレリリース識別子等）は非対応で、
    比較できない場合はNoneを返す（「不明」として扱われる）。"""
    def _parse(v: str) -> list[int] | None:
        parts = re.findall(r"\d+", v)
        if not parts:
            return None
        return [int(p) for p in parts]

    cur = _parse(current)
    minv = _parse(minimum)
    if cur is None or minv is None:
        return None
    return cur >= minv


# ------------------------------------------------------------------
# LLDP新規ネイバー検知
# ------------------------------------------------------------------

def _detect_new_lldp_neighbors(hosts: list[dict], zabbix: ZabbixClient, snapshot_path: Path) -> dict[str, list[dict]]:
    """前回実行時のLLDPネイバー一覧との差分から、新規に出現したネイバーを検知する。

    「未知の機器検知」要件のうち、Zabbix Discoveryではカバーできない範囲
    （監視対象スイッチの配下に新規接続されたがまだSNMP監視対象として
    登録されていない機器）を補完する。検知したホストには sec.lldp.new_neighbor
    Trapperアイテムへ 1 を、それ以外には 0 を書き込み、Zabbix Trigger側の
    アラート（Zabbix管理画面側で別途設定）が発火・自動解消するようにする。
    """
    hostids = [h["hostid"] for h in hosts]
    current = zabbix.get_lldp_neighbors(hostids)

    previous: dict[str, list[dict]] = {}
    if snapshot_path.exists():
        previous = json.loads(snapshot_path.read_text(encoding="utf-8"))

    new_by_host: dict[str, list[dict]] = {}
    for hostid, neighbors in current.items():
        known = {(n["port"], n["sysname"]) for n in previous.get(hostid, [])}
        fresh = [n for n in neighbors if (n["port"], n["sysname"]) not in known]
        if fresh:
            new_by_host[hostid] = fresh

    snapshot_path.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")

    # Trapperアイテムが未作成のホストは push_trapper_value が False を返すだけで、
    # Zabbix側のアイテム・Trigger新設（別途対応）が終わるまでは静かにスキップされる
    for hostid in current:
        value = "1" if hostid in new_by_host else "0"
        zabbix.push_trapper_value(hostid, "sec.lldp.new_neighbor", value)

    return new_by_host


# ------------------------------------------------------------------
# サマリー表示
# ------------------------------------------------------------------

def _print_summary(results: list[dict]):
    labels = {
        "critical": "🔴 CRITICAL",
        "high":     "🟠 HIGH    ",
        "medium":   "🟡 MEDIUM  ",
        "warning":  "⚠️  WARNING ",
        "unknown":  "❓ UNKNOWN ",
        "ok":       "✅ OK      ",
    }
    counts: dict[str, int] = {}
    for r in results:
        k = r["risk_level"]
        counts[k] = counts.get(k, 0) + 1

    print("\n=== サマリー ===")
    for level, label in labels.items():
        if counts.get(level):
            print(f"  {label}: {counts[level]} 件")

    # "unknown"は確定的な危険ではないが、データが取れておらず要対応（原因調査）という
    # 意味でcritical/highと合わせて一覧表示する（運用者が見落とさないようにするため）。
    flagged = [r for r in results if r["risk_level"] in ("critical", "high", "unknown")]
    if flagged:
        print("\n要対応/要確認デバイス:")
        for r in flagged:
            eol_parts = []
            for label, eol_info in (("HW-EoS", r.get("hw_eol")), ("SW-EoS", r.get("sw_eol"))):
                if eol_info and eol_info.get("eol_date"):
                    tag = "(要確認)" if eol_info.get("status") == "fuzzy_match" else ""
                    eol_parts.append(f"{label}:{eol_info['eol_date']}{tag}")
            eol_str = f"  [{', '.join(eol_parts)}]" if eol_parts else ""
            exploited = [c for c in r["cves"] if c.get("actively_exploited")]
            cve_str = f"  [{len(r['cves'])} CVE"
            if exploited:
                cve_str += f"、うち {len(exploited)} 件は CISA KEV 掲載"
            cve_str += "]" if r["cves"] else ""
            if r["cve_status"] == "lookup_failed":
                cve_str += "  [CVE検索失敗]"
            elif r["cve_status"] == "unknown":
                cve_str += "  [CVE未検索]"
            print(f"  - {r['host']} ({r['vendor']} {r['model']} FW:{r['firmware']}){eol_str}{cve_str}")


# ------------------------------------------------------------------
# ドライラン用ダミーデータ
# ------------------------------------------------------------------

def _dummy_hosts() -> list[dict]:
    return [
        {
            "hostid": "1", "host": "atl-router02", "name": "atl-router02",
            "inventory": {"vendor": "Ubiquiti", "model": "UCG-Ultra", "software_full": "5.1.19"},
        },
        {
            "hostid": "2", "host": "atLIB-printer01", "name": "atLIB-printer01",
            "inventory": {"vendor": "Brother", "model": "MFC-L3780CDW", "software_full": "1.35"},
        },
        {
            "hostid": "3", "host": "atLIB-ap01", "name": "atLIB-ap01",
            "inventory": {"vendor": "NETGEAR", "model": "WAX625", "software_full": "11.8.0.9"},
        },
        {
            "hostid": "4", "host": "atLIB-ap02", "name": "atLIB-ap02",
            "inventory": {"vendor": "NETGEAR", "model": "WAX625", "software_full": "11.8.0.9"},
        },
        {
            # インベントリ未入力ホスト。risk_level="unknown"として記録される
            # （以前はcontinueで結果から完全に消えていたケース）ことの動作確認用。
            "hostid": "5", "host": "atLIB-unknown01", "name": "atLIB-unknown01",
            "inventory": {},
        },
    ]


# ------------------------------------------------------------------

def _parse_args():
    p = argparse.ArgumentParser(description="CVE/EoL 突合 ＋ LLDP新規ネイバー検知バッチ")
    p.add_argument("--config", default=str(HERE / "config.yaml"), help="設定ファイルパス")
    p.add_argument("--dry-run", action="store_true", help="Zabbixに接続せずダミーデータで動作確認")
    return p.parse_args()


def _load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 環境変数でクレデンシャルを上書き（CI/スケジューラ実行時に使用）
    env_map = {
        ("zabbix", "url"):      "ZABBIX_URL",
        ("zabbix", "user"):     "ZABBIX_USER",
        ("zabbix", "password"): "ZABBIX_PASSWORD",
        ("nvd",    "api_key"):  "NVD_API_KEY",
    }
    for (section, key), env_var in env_map.items():
        val = os.environ.get(env_var)
        if val:
            config.setdefault(section, {})[key] = val

    return config


if __name__ == "__main__":
    main()
