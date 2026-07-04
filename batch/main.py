"""CVE / EoL 突合バッチ

使い方:
  python main.py [--config config.yaml] [--dry-run]

出力:
  reports/health_check_YYYYMMDD_HHMMSS.json
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml

from zabbix_client import ZabbixClient
from cpe_mapper import CpeMapper
from nvd_client import NvdClient
from eol_client import EolClient

HERE = Path(__file__).parent


def main():
    args = _parse_args()
    config = _load_config(args.config)

    reports_dir = HERE / config.get("output", {}).get("dir", "./reports").lstrip("./")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # ---- 初期化 ----
    nvd_api_key = config.get("nvd", {}).get("api_key", "")

    print("[1/5] Zabbix からホスト情報を取得中...")
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

    print("[2/5] CISA KEV + NVD クライアントを初期化中...")
    nvd = NvdClient(nvd_api_key)
    print(f"  → CISA KEV: {len(nvd._kev)} 件の悪用確認済み CVE を読み込み済み")

    print("[3/5] CPE マッパーを初期化中...")
    cpe_mapper = CpeMapper(HERE / "cpe_overrides.json", nvd_api_key)

    print("[4/5] EoL クライアントを初期化中...")
    eol_client = EolClient(HERE / "eol_overrides.json")

    # ---- デバイスごとに突合 ----
    print("[5/5] 各デバイスを CVE / EoL と突合中...")
    results = []
    for host in hosts:
        inv = host.get("inventory") or {}
        vendor = inv.get("vendor", "").strip()
        model = inv.get("model", "").strip()
        fw = inv.get("software_full", "").strip()

        if not vendor and not model:
            continue

        device_key = f"{vendor} {model}".strip()
        print(f"  処理中: {host['host']} ({device_key})")

        cpe = cpe_mapper.get_cpe(device_key)

        if cpe:
            cves = nvd.get_cves_by_cpe(cpe)
            cve_source = "cpe"
        else:
            cves = nvd.get_cves_by_keyword(device_key)
            cve_source = "keyword"

        eol_info = eol_client.get_eol(device_key, model)
        risk = _calc_risk(cves, eol_info)

        results.append({
            "host": host["host"],
            "name": host["name"],
            "vendor": vendor,
            "model": model,
            "firmware": fw,
            "cpe": cpe,
            "cve_source": cve_source,
            "eol": eol_info,
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
                zabbix.write_back_risk(hostid, r["risk_level"], r["eol"], r["cves"])
                print(f"  書き戻し完了: {r['host']} → {r['risk_level']}")
            except Exception as e:
                print(f"  [警告] 書き戻し失敗 ({r['host']}): {e}")
    elif args.dry_run and writeback_enabled:
        print("\n[ドライラン] Zabbix 書き戻しはスキップ")

    _print_summary(results)


# ------------------------------------------------------------------
# リスク判定
# ------------------------------------------------------------------

def _calc_risk(cves: list[dict], eol_info: dict | None) -> str:
    if eol_info and eol_info.get("is_eol"):
        return "critical"

    exploited = [c for c in cves if c.get("actively_exploited")]
    critical_cves = [c for c in cves if (c.get("cvss_score") or 0) >= 9.0]
    high_cves = [c for c in cves if 7.0 <= (c.get("cvss_score") or 0) < 9.0]

    if exploited or critical_cves:
        return "critical"
    if high_cves:
        return "high"
    if cves:
        return "medium"
    if eol_info and eol_info.get("days_until_eol") is not None and eol_info["days_until_eol"] <= 90:
        return "warning"
    return "ok"


# ------------------------------------------------------------------
# サマリー表示
# ------------------------------------------------------------------

def _print_summary(results: list[dict]):
    labels = {
        "critical": "🔴 CRITICAL",
        "high":     "🟠 HIGH    ",
        "medium":   "🟡 MEDIUM  ",
        "warning":  "⚠️  WARNING ",
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

    flagged = [r for r in results if r["risk_level"] in ("critical", "high")]
    if flagged:
        print("\n要対応デバイス:")
        for r in flagged:
            eol_str = ""
            if r["eol"] and r["eol"].get("eol_date"):
                eol_str = f"  [EoS: {r['eol']['eol_date']}]"
            exploited = [c for c in r["cves"] if c.get("actively_exploited")]
            cve_str = f"  [{len(r['cves'])} CVE"
            if exploited:
                cve_str += f"、うち {len(exploited)} 件は CISA KEV 掲載"
            cve_str += "]" if r["cves"] else ""
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
    ]


# ------------------------------------------------------------------

def _parse_args():
    p = argparse.ArgumentParser(description="CVE/EoL 突合バッチ")
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
