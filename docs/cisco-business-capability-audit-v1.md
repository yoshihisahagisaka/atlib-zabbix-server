# Cisco Business / Catalyst SMB Capability Audit v1
Date: 2026-09-19
Status: Evidence Pending; Cisco IOS enterprise families remain separately audited

## Findings
Cisco publishes SNMP configuration and common OID documentation for CBS250/CBS350 and Catalyst 1200/1300. Cisco also publishes model-object-ID mappings for Small Business switch families.

## Family separation
Do not use one broad Cisco resolver.
- Cisco Business CBS250/350
- Catalyst 1200/1300
- IOS/IOS-XE enterprise Catalyst/router
- Meraki cloud-managed products
must remain separate capability families.

## InfraVision assessment
CBS/Catalyst SMB switches are promising for sysObjectID-based model resolution. Firmware/serial extraction and lifecycle normalization wait for real-device evidence.

## State
Evidence Pending for CBS/Catalyst SMB. Existing official Zabbix Cisco IOS template remains a separate Prototype candidate.
