"""Apply post-discovery family/template resolution to existing Zabbix hosts.

Default is dry-run. --apply links only a uniquely resolved template and never
unlinks existing templates. Cross-dcheck evidence is read from actual host items,
not from one network-discovery event.
"""
import argparse
import os
import sys

from family_resolver import AssetEvidence, resolve_asset
from zabbix_client import ZabbixClient

SYSOBJECTID_KEYS = ("system.objectid[sysObjectID.0]", "system.objectid", "sysObjectID")
SYSDESCR_KEYS = ("system.descr[sysDescr.0]", "system.descr", "sysDescr")


def _connect() -> ZabbixClient:
    url = os.environ.get("ZABBIX_URL")
    token = os.environ.get("ZABBIX_TOKEN")
    user = os.environ.get("ZABBIX_USER")
    password = os.environ.get("ZABBIX_PASSWORD")
    host_header = os.environ.get("ZABBIX_HOST_HEADER")
    if not url or (not token and not (user and password)):
        raise RuntimeError("ZABBIX_URL and ZABBIX_TOKEN or ZABBIX_USER/ZABBIX_PASSWORD are required")
    return ZabbixClient(url, user=user, password=password, token=token, host_header=host_header)


def _evidence(z: ZabbixClient, hostid: str) -> AssetEvidence:
    items = z.call("item.get", {
        "hostids": hostid,
        "output": ["key_", "lastvalue"],
        "search": {"key_": "system."},
    })
    values = {i["key_"]: i.get("lastvalue", "") for i in items}
    def first(keys):
        for key in keys:
            if values.get(key):
                return values[key].strip()
        return ""
    return AssetEvidence(sysobjectid=first(SYSOBJECTID_KEYS), sysdescr=first(SYSDESCR_KEYS))


def _template(z: ZabbixClient, name: str) -> dict | None:
    rows = z.call("template.get", {"output": ["templateid", "host"], "filter": {"host": name}})
    return rows[0] if rows else None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true")
    p.add_argument("--host-group", default="", help="optional exact host-group name")
    args = p.parse_args()
    z = _connect()

    params = {
        "output": ["hostid", "host", "name"],
        "selectParentTemplates": ["templateid", "host"],
        "status": 0,
    }
    if args.host_group:
        groups = z.call("hostgroup.get", {"output": ["groupid"], "filter": {"name": args.host_group}})
        if not groups:
            raise RuntimeError(f"host group not found: {args.host_group}")
        params["groupids"] = [groups[0]["groupid"]]

    hosts = z.call("host.get", params)
    changed = ambiguous = unresolved = 0
    for host in hosts:
        evidence = _evidence(z, host["hostid"])
        resolutions = resolve_asset(evidence)
        if len(resolutions) != 1:
            if len(resolutions) > 1:
                ambiguous += 1
                print(f"[AMBIGUOUS] {host['name']}: {[r.rule_id for r in resolutions]}")
            else:
                unresolved += 1
            continue

        resolution = resolutions[0]
        template = _template(z, resolution.template_name)
        if not template:
            print(f"[MISSING TEMPLATE] {host['name']}: {resolution.template_name}")
            continue

        linked = {t["templateid"] for t in host.get("parentTemplates", [])}
        if template["templateid"] in linked:
            print(f"[OK] {host['name']}: {resolution.rule_id} already linked")
            continue

        print(f"[MATCH] {host['name']}: {resolution.rule_id} -> {resolution.template_name}; evidence={resolution.matched}")
        if args.apply:
            z.call("host.massadd", {
                "hosts": [{"hostid": host["hostid"]}],
                "templates": [{"templateid": template["templateid"]}],
            })
            changed += 1

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{mode}] hosts={len(hosts)} linked={changed} ambiguous={ambiguous} unresolved={unresolved}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
