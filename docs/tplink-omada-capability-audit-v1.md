# TP-Link Omada Capability Audit v1

Date: 2026-09-19
Status: Evidence Pending

## Scope
TP-Link Omada business networking. Start with managed/smart switches; then gateway/AP families when a real device is encountered.

## Primary-source findings
- Omada is explicitly positioned for small/mid-size offices and unifies gateways, switches and APs.
- Multiple current Omada managed/smart switch families support SNMP v1/v2c/v3, RMON and LLDP/LLDP-MED.
- Current product specifications explicitly list TP-Link private MIB support.
- Hardware version matters: the same commercial model can have V1/V2/V3/V4/V5 variants with feature differences.

## InfraVision assessment
Generic monitoring: strong candidate.
Private-MIB identity enrichment: promising but exact Model/Firmware/Serial OIDs must be verified from MIB/real-device evidence.
Family/hardware-version normalization is mandatory before lifecycle/CVE matching.

## Initial target families
- SG2xxx smart/access switches
- SG3xxx/SX3xxx managed/L2+ switches
Then evidence-triggered:
- ER/Omada gateways
- EAP/Omada access points

## State
Evidence Pending. Do not create/enable a production resolver until one real device is available.

## Real-device gate
Collect:
- sysObjectID.0
- sysDescr.0
- sysName.0
- ENTITY-MIB identity where supported
- TP-Link private-enterprise subtree/items
- commercial model + hardware version shown by device/controller
- firmware version shown by device/controller

Then determine exact model, hardware-version and firmware normalization rules.

## Important lifecycle/CVE rule
TP-Link model alone is insufficient. Preserve hardware revision (for example V4/V5) as part of canonical product identity whenever available because firmware/support applicability can differ by hardware version.
