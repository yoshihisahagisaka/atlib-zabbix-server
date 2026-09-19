# BUFFALO Capability Audit v1

Date: 2026-09-19
Status: primary-source audit; no resolver/template enabled yet.

## Scope
First target: BUFFALO business managed switches, especially BS-GS20/BS-GS21 families.
Do not treat consumer/unmanaged BUFFALO products as automatically supported.

## Primary-source findings
- BS-GS21 business smart switches support SNMP v1/v2c/v3, MIB-II, Bridge/EtherLike/P/Q-Bridge, Interface/RMON/RADIUS MIB and LLDP.
- BUFFALO publishes a downloadable "Business Switch Private MIB" for BS-GS20/BS-GS20P families.
- BUFFALO publishes model-specific firmware pages with current version and update date.
- 2025 security-related firmware changes explicitly discuss SNMP management-interface behavior for BS-GS21 products.
- Older BS-GS20/20P products also expose SNMP and have public firmware/support records.

## InfraVision implication
BUFFALO managed business switches are technically promising for Base automatic asset identification.
However, the exact private-MIB objects for model/firmware/serial have not yet been verified from the MIB file itself.

Therefore:
- Generic SNMP monitoring: supported candidate
- vendor identification: pending exact enterprise/sysObjectID evidence
- model: pending private-MIB/sysDescr verification
- firmware: pending private-MIB/sysDescr verification
- serial: pending
- lifecycle/latest firmware: public BUFFALO support pages are usable intelligence sources

## Family strategy
Initial families:
1. BS-GS21 / BS-GS21P
2. BS-GS20 / BS-GS20P / BS-GS20P-HP
Then evaluate:
- BS-MS
- BS-XM/XS
- business AP WAPM/WAPS
- business VPN routers

## Safety
Do not add a BUFFALO auto-link resolver based only on brand assumptions.
Next gate is to inspect the official private MIB and/or collect read-only SNMP evidence from a real BUFFALO business switch.

## Recommended PoC
For one BS-GS21 or BS-GS20 device collect:
- sysObjectID.0
- sysDescr.0
- sysName.0
- ENTITY-MIB identity objects where supported
- BUFFALO private-MIB identity/firmware objects

Then define:
- exact vendor enterprise match
- family match
- model source
- firmware source
- serial source
- confidence
