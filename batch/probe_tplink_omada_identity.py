"""Read-only TP-Link Omada identity probe for a known Zabbix host."""
import argparse, os
from zabbix_client import ZabbixClient

IDENTITY_OIDS={"sysDescr":"1.3.6.1.2.1.1.1.0","sysObjectID":"1.3.6.1.2.1.1.2.0","sysName":"1.3.6.1.2.1.1.5.0"}
TP_LINK_ENTERPRISE="1.3.6.1.4.1.11863"

def main():
    p=argparse.ArgumentParser(); p.add_argument("--host",required=True); a=p.parse_args()
    z=ZabbixClient(os.environ["ZABBIX_URL"],user=os.environ.get("ZABBIX_USER"),password=os.environ.get("ZABBIX_PASSWORD"),token=os.environ.get("ZABBIX_TOKEN"),host_header=os.environ.get("ZABBIX_HOST_HEADER"))
    hs=z.call("host.get",{"output":["hostid","host","name"],"filter":{"host":[a.host]}})
    if not hs: hs=z.call("host.get",{"output":["hostid","host","name"],"filter":{"name":[a.host]}})
    if len(hs)!=1: raise RuntimeError(f"expected one host, got {len(hs)}")
    h=hs[0]; items=z.call("item.get",{"hostids":h["hostid"],"output":["name","key_","snmp_oid","lastvalue"]})
    print(f"host={h['host']} name={h['name']}")
    for label,oid in IDENTITY_OIDS.items():
        hits=[i for i in items if oid in (i.get("snmp_oid") or "")]
        print(f"{label}: "+(hits[0].get("lastvalue","") if hits else "<not collected>"))
    private=[i for i in items if TP_LINK_ENTERPRISE in (i.get("snmp_oid") or "")]
    print(f"tplink_private_items={len(private)}")
    for i in private: print(f"  {i['snmp_oid']} | {i['name']} | {i.get('lastvalue','')}")
    print("Record the device hardware revision (Vx) separately; it is part of lifecycle/security identity.")
    print("Absence here means not currently collected, not unsupported.")

if __name__=="__main__": main()
