"""Read-only Fortinet family identity probe."""
import argparse, os
from zabbix_client import ZabbixClient
OIDS={"sysDescr":"1.3.6.1.2.1.1.1.0","sysObjectID":"1.3.6.1.2.1.1.2.0","sysName":"1.3.6.1.2.1.1.5.0"}
FORTINET="1.3.6.1.4.1.12356"
def main():
 p=argparse.ArgumentParser();p.add_argument("--host",required=True);a=p.parse_args()
 z=ZabbixClient(os.environ["ZABBIX_URL"],user=os.environ.get("ZABBIX_USER"),password=os.environ.get("ZABBIX_PASSWORD"),token=os.environ.get("ZABBIX_TOKEN"),host_header=os.environ.get("ZABBIX_HOST_HEADER"))
 hs=z.call("host.get",{"output":["hostid","host","name"],"filter":{"host":[a.host]}})
 if not hs: hs=z.call("host.get",{"output":["hostid","host","name"],"filter":{"name":[a.host]}})
 if len(hs)!=1: raise RuntimeError(f"expected one host, got {len(hs)}")
 h=hs[0];items=z.call("item.get",{"hostids":h["hostid"],"output":["name","key_","snmp_oid","lastvalue"]})
 print(f"host={h['host']} name={h['name']}")
 vals={}
 for label,oid in OIDS.items():
  hits=[i for i in items if oid in (i.get("snmp_oid") or "")]; vals[label]=hits[0].get("lastvalue","") if hits else ""
  print(f"{label}: {vals[label] or '<not collected>'}")
 d=(vals.get("sysDescr") or "").lower()
 fam="FortiGate" if ("fortigate" in d or "fortios" in d) else ("FortiSwitch" if "fortiswitch" in d else ("FortiAP" if "fortiap" in d else "unknown"))
 print(f"family_hint={fam}")
 private=[i for i in items if FORTINET in (i.get("snmp_oid") or "")]
 print(f"fortinet_private_items={len(private)}")
 for i in private: print(f"  {i['snmp_oid']} | {i['name']} | {i.get('lastvalue','')}")
 print("family_hint is diagnostic only; production resolution still requires evidence-gated rules.")
if __name__=="__main__":main()
