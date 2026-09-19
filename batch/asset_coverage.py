"""Asset identification coverage audit.

Read-only command for measuring whether Zabbix Host Inventory contains enough
identity data for lifecycle/vulnerability intelligence. It does not modify
hosts, templates, discovery actions, or customer-facing reports.

Usage:
  python asset_coverage.py [--config config.yaml] [--json]
"""
import argparse
import json
from collections import Counter
from pathlib import Path

from main import _load_config
from zabbix_client import ZabbixClient

HERE = Path(__file__).parent


def _present(value) -> bool:
    return bool(str(value or "").strip())


def audit_hosts(hosts: list[dict]) -> dict:
    rows = []
    totals = Counter()

    for host in hosts:
        inv = host.get("inventory") or {}
        vendor = str(inv.get("vendor") or "").strip()
        model = str(inv.get("model") or "").strip()
        firmware = str(inv.get("software_full") or "").strip()

        vp = _present(vendor)
        mp = _present(model)
        fp = _present(firmware)
        complete = vp and mp and fp

        missing = []
        if not vp:
            missing.append("vendor")
        if not mp:
            missing.append("model")
        if not fp:
            missing.append("firmware")

        totals["hosts"] += 1
        totals["vendor_present"] += int(vp)
        totals["model_present"] += int(mp)
        totals["firmware_present"] += int(fp)
        totals["identity_complete"] += int(complete)
        totals["manual_review_required"] += int(not complete)

        rows.append({
            "hostid": host.get("hostid"),
            "host": host.get("host"),
            "name": host.get("name"),
            "vendor": vendor,
            "model": model,
            "firmware": firmware,
            "identity_complete": complete,
            "missing": missing,
        })

    n = totals["hosts"]

    def pct(key: str) -> float:
        return round((totals[key] / n * 100.0), 1) if n else 0.0

    metrics = {
        "hosts": n,
        "vendor_present": totals["vendor_present"],
        "vendor_coverage_pct": pct("vendor_present"),
        "model_present": totals["model_present"],
        "model_coverage_pct": pct("model_present"),
        "firmware_present": totals["firmware_present"],
        "firmware_coverage_pct": pct("firmware_present"),
        "identity_complete": totals["identity_complete"],
        "identity_complete_pct": pct("identity_complete"),
        "manual_review_required": totals["manual_review_required"],
        "manual_review_pct": pct("manual_review_required"),
    }

    by_vendor = Counter(r["vendor"] or "(unknown)" for r in rows)

    return {
        "metrics": metrics,
        "vendor_distribution": [
            {"vendor": vendor, "hosts": count}
            for vendor, count in by_vendor.most_common()
        ],
        "hosts": rows,
    }


def main():
    args = _parse_args()
    config = _load_config(args.config)

    zcfg = config["zabbix"]
    zabbix = ZabbixClient(
        zcfg["url"],
        zcfg.get("user"),
        zcfg.get("password"),
        token=zcfg.get("token"),
    )
    result = audit_hosts(zabbix.get_hosts_inventory())

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    m = result["metrics"]
    print("=== Asset Identification Coverage ===")
    print(f"Hosts:              {m['hosts']}")
    print(f"Vendor:             {m['vendor_present']} ({m['vendor_coverage_pct']}%)")
    print(f"Model:              {m['model_present']} ({m['model_coverage_pct']}%)")
    print(f"Firmware:           {m['firmware_present']} ({m['firmware_coverage_pct']}%)")
    print(f"Complete identity:  {m['identity_complete']} ({m['identity_complete_pct']}%)")
    print(f"Manual review:      {m['manual_review_required']} ({m['manual_review_pct']}%)")

    print("\n=== Vendor Distribution ===")
    for row in result["vendor_distribution"]:
        print(f"{row['vendor']}: {row['hosts']}")

    incomplete = [r for r in result["hosts"] if not r["identity_complete"]]
    print("\n=== Incomplete Identity ===")
    if not incomplete:
        print("(none)")
    for row in incomplete:
        print(f"{row['host']}: missing={','.join(row['missing'])}")


def _parse_args():
    p = argparse.ArgumentParser(
        description="Measure Vendor/Model/Firmware coverage in Zabbix Host Inventory"
    )
    p.add_argument("--config", default=str(HERE / "config.yaml"))
    p.add_argument("--json", action="store_true")
    return p.parse_args()


if __name__ == "__main__":
    main()
