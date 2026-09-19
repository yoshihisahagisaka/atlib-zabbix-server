"""Read-only BUFFALO business-switch identity probe.

Use on one known BS-GS20/21 family host before creating a production resolver.
It intentionally relies on standard identity OIDs first and prints candidate
BUFFALO private-enterprise items already present in Zabbix.
"""
import argparse, os
from zabbix_client import ZabbixClient

IDENTITY_OIDS = {
    "sysDescr": "1.3.6.1.2.1.1.1.0",
    "sysObjectID": "1.3.6.1.2.1.1.2.0",
    "sysName": "1.3.6.1.2.1.1.5.0",
}
BUFFALO_ENTERPRISE = "1.3.6.1.4.1.5227"


def connect():
    return ZabbixClient(
        os.environ["ZABBIX_URL"],
        user=os.environ.get("ZABBIX_USER"),
        password=os.environ.get("ZABBIX_PASSWORD"),
        token=os.environ.get("ZABBIX_TOKEN"),
        host_header=os.environ.get("ZABBIX_HOST_HEADER"),
    )


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--host", required=True, help="exact Zabbix host or visible name")
    args=p.parse_args()
    z=connect()
    hosts=z.call("host.get",{"output":["hostid","host","name"],"filter":{"host":[args.host]}})
    if not hosts:
        hosts=z.call("host.get",{"output":["hostid","host","name"],"filter":{"name":[args.host]}})
    if len(hosts)!=1:
        raise RuntimeError(f"expected one host, got {len(hosts)}")
    h=hosts[0]
    items=z.call("item.get",{"hostids":h["hostid"],"output":["name","key_","snmp_oid","lastvalue"]})
    print(f"host={h['host']} name={h['name']}")
    for label,oid in IDENTITY_OIDS.items():
        hits=[i for i in items if oid in (i.get("snmp_oid") or "")]
        print(f"{label}: "+(hits[0].get("lastvalue","") if hits else "<not collected>"))
    private=[i for i in items if BUFFALO_ENTERPRISE in (i.get("snmp_oid") or "")]
    print(f"buffalo_private_items={len(private)}")
    for i in private:
        print(f"  {i['snmp_oid']} | {i['name']} | {i.get('lastvalue','')}")
    print("NOTE: absence here means 'not currently collected by Zabbix', not 'OID unsupported'.")
    print("Next: if private identity OIDs are not already items, perform a read-only snmpwalk from the monitoring network using the official BUFFALO MIB.")


if __name__=="__main__":
    main()
