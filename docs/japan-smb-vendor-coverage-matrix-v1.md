# Japan SMB Vendor Coverage Matrix v1

Date: 2026-09-19
Status: research baseline; implementation priority decision input.

## Purpose
Select InfraVision v1 vendor coverage from Japanese SMB encounter probability and automation economics, rather than adding adapters in arbitrary order.

## Scoring dimensions
1. Japan SMB encounter probability
2. Product breadth relevant to InfraVision (router/firewall/switch/AP)
3. SNMP/identity automation feasibility
4. Lifecycle/security intelligence feasibility
5. Existing Zabbix/atLIB implementation leverage

A/B/C are implementation waves, not claims of exact market-share ordering.

## Wave A — build/validate proactively
- YAMAHA: router/switch/AP/UTM. Strong Japan SOHO/SMB evidence; adapters for RTX/SWX/WLX are already prototyped.
- BUFFALO: switch/AP/VPN router. Strong Japanese corporate presence; managed switches support SNMP; public support-policy and firmware data exist. High priority new audit.
- TP-Link Omada: gateway/switch/AP. Explicit SMB product family; managed switches expose SNMP v1/v2c/v3. High priority new audit.
- Fortinet: firewall/switch/AP. Explicit SMB portfolio and strong relevance to security reporting; official Zabbix FortiGate template already audited.
- NETGEAR: switch/AP. Explicit SMB portfolio; smart/managed families support SNMP but unmanaged/Plus families may not. Family segmentation required.

## Wave B — support deliberately after A coverage
- Cisco / Meraki: router/switch/AP/security. Important business installed base, but product-family/template differences make safe automatic matching more complex.
- HPE Aruba: switch/AP. Important business WLAN/switching vendor; official Zabbix coverage is family-specific.
- Allied Telesis: switch/AP/router. Japanese enterprise/business relevance and SNMP support; investigate actual SMB encounter rate and identity MIBs.
- Ubiquiti UniFi: gateway/switch/AP. Existing atLIB UCG identification asset can be reused; maintain rather than prioritize net-new work.

## Wave C — evidence/customer-triggered
- NEC network products
- I-O DATA business network products
- D-Link
- WatchGuard
- SonicWall
- Sophos
- Check Point
- Juniper/Ruckus and other enterprise-heavy families

Security appliances in Wave C may be promoted when actual customer inventory shows meaningful frequency.

## Important segmentation
Vendor support must be family/capability based. A vendor logo does not imply all products are SNMP-identifiable.
Examples:
- NETGEAR unmanaged/Plus switches may not support SNMP while Smart/Managed do.
- BUFFALO managed business switch lines expose SNMP, but capability differs by family.
- Fortinet must distinguish FortiGate/FortiSwitch/FortiAP.
- TP-Link must distinguish Omada managed products from consumer/unmanaged products.

## Proposed implementation order
Do not use the previous fixed NETGEAR -> Fortinet -> Cisco order.

1. Finish real-device validation of existing YAMAHA RTX/SWX/WLX prototypes.
2. BUFFALO capability audit: enterprise OID, model, firmware, serial, lifecycle sources.
3. TP-Link Omada capability audit: gateway/switch/AP identity and lifecycle sources.
4. Fortinet: harden FortiGate family detection, then assess FortiSwitch/FortiAP.
5. NETGEAR: test WAX625 and Smart/Managed switch private MIB capability; explicitly classify unsupported unmanaged families.
6. Allied Telesis capability audit.
7. Cisco/Meraki and HPE Aruba family matrix.
8. Ubiquiti: expand only where current UniFi/UCG coverage is insufficient.

## Base-plan rule
Base ¥9,980 does not promise universal vendor coverage. It promises automatic discovery/monitoring plus automatic asset/security screening where evidence is defensible.
Unsupported or insufficiently identified devices remain Unknown / Detailed confirmation recommended.

## Measurement loop
Add actual-customer telemetry before expanding beyond Wave A:
- host count by vendor
- network-device count by family
- Vendor/Model/Firmware completeness
- unresolved/ambiguous rate
- number of customer environments containing each vendor
- human investigation minutes caused by each unsupported family

Promote vendors/families based on observed demand and reusable automation value.
