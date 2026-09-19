# Zabbix Official Template Coverage Matrix v1

Date: 2026-09-19  
Reference: official Zabbix repository, release/7.4.  
Purpose: determine what InfraVision can obtain from L1 Generic SNMP and L2 official vendor templates before adding L3 atLIB adapters.

## Rating

- ◎: official template directly collects and inventory-links the field needed by InfraVision.
- ○: official template collects usable data, but normalization/inventory mapping is needed.
- △: template is limited to a product family or does not provide the required identity field reliably; custom logic/validation needed.
- ×: required identity field was not found in the inspected official template.
- —: not yet audited.

A template's existence does not mean it is safe to auto-link to every device from that vendor. Product-family scope is part of the resolver decision.

## Matrix

| Vendor / template | Vendor detect | Model | Firmware/OS | Serial | InfraVision decision |
|---|---:|---:|---:|---:|---|
| Generic: Network Generic Device by SNMP | ○ | × | △ | × | Mandatory L1 only. sysDescr is evidence, not normalized identity. |
| Cisco IOS by SNMP | ◎* | ◎ | ○ | ◎ | Strong L2 candidate for IOS devices. Validate supported family before auto-link. |
| Fortinet FortiGate by SNMP | ◎* | ◎ | ◎ | ◎ | Strong L2 candidate. Best current official fit for Asset Intelligence. |
| NETGEAR Fastpath by SNMP | ◎* | ◎ | ○ | ◎ | L2 only for Fastpath-compatible devices. Do not assume WAX625 compatibility. |
| Ubiquiti AirOS by SNMP | △ | ◎ | ○ | × | Product-family scoped. Not a replacement for current UniFi/UCG atLIB template. |
| Aruba CX 8300s by SNMP | △ | × | △ | × | Monitoring template is useful, but inspected identity fields are insufficient for InfraVision canonical identity. |
| Brother | — | — | — | — | No current official L2 selected; existing atLIB adapter remains baseline. |
| YAMAHA | × | × | × | × | No official Zabbix 7.4 network template found in official network template directory; L3 candidate after MIB validation. |

* Vendor detection is expected to be driven primarily by InfraVision discovery evidence (enterprise sysObjectID/sysDescr) rather than by an inventory field in the vendor template.

## Evidence by template

### Generic SNMP

The official Generic template collects sysDescr, sysName, sysLocation, contact and generic health/interface data. In the inspected 7.4 template it does not inventory-link Model or Serial and does not expose a normalized firmware field.

Conclusion: keep it mandatory for discovery/monitoring, but never interpret successful Generic SNMP monitoring as complete asset identification.

### Cisco IOS

Official 7.4 template:
- Hardware model: ENTITY-MIB, inventory_link MODEL.
- Hardware serial: ENTITY-MIB, inventory_link SERIALNO_A.
- Operating system: parsed from sysDescr, inventory_link OS.
- ENTITY-MIB serial-number discovery is also present.

Conclusion: Cisco IOS can often reach the identity level required for lifecycle/CVE work without an atLIB-specific identification template. Firmware/version semantics must be normalized from the OS value and tested against representative IOS/IOS-XE devices.

### Fortinet FortiGate

Official 7.4 template:
- Firmware: FORTINET-FORTIGATE-MIB OID 1.3.6.1.4.1.12356.101.4.1.1.0, inventory_link SOFTWARE.
- Model: ENTITY-MIB, inventory_link MODEL.
- Serial: ENTITY-MIB, inventory_link SERIALNO_A.

Conclusion: this is the strongest L2 candidate inspected. InfraVision should prefer the official template rather than duplicate these identity OIDs in a custom template, subject to real-device validation.

### NETGEAR Fastpath

Official 7.4 template:
- Model: FASTPATH-SWITCHING-MIB OID 1.3.6.1.4.1.4526.10.1.1.1.3.0, inventory_link MODEL.
- Serial: private MIB OID ending .4.0, inventory_link SERIALNO_A.
- Operating system: private MIB OID ending .10.0, inventory_link OS.

Important: current atLIB WAX625 evidence showed that previously tested ENTITY-MIB model/software OIDs were unavailable. The official template uses NETGEAR Fastpath private MIB instead, but the template itself is Fastpath-scoped. We have not established that WAX625 implements these Fastpath OIDs.

Conclusion: add a capability probe before selecting official NETGEAR template. Keep current atLIB NETGEAR identification as fallback until WAX625 is tested against the official private-MIB OIDs.

### Ubiquiti AirOS

Official 7.4 template:
- Firmware item from IEEE802dot11-MIB.
- Model from IEEE802dot11-MIB, inventory_link MODEL.
- Firmware is collected but was not inventory-linked in the inspected template.
- Template is AirOS-oriented.

Current atLIB UniFi/UCG implementation derives vendor/model/software from sysDescr and is verified on UCG-Ultra. AirOS and UniFi/UCG must not be treated as one homogeneous template family.

Conclusion: retain atLIB UniFi identification. Official AirOS template may be used for compatible AirOS devices after family detection.

### Aruba CX 8300s

The inspected official template is explicitly CX 8300s-scoped. It collects sysDescr and generic system information, but the inspected identity-item scan did not find inventory-linked Model/Serial or a dedicated normalized firmware field.

Conclusion: do not generalize this template to all Aruba/HPE. Aruba requires product-family-specific audit and likely an InfraVision identity extension for the SMB models we actually encounter.

## Resolver policy resulting from audit

Template selection must become capability-aware, not vendor-only:

1. Identify vendor/family from discovery evidence.
2. Determine candidate official template.
3. Verify that candidate applies to the product family.
4. Prefer official template when it supplies the required identity capability.
5. Add a small atLIB identity extension when official monitoring is good but identity fields are missing.
6. Use a full atLIB vendor adapter only when official template/private MIB coverage is insufficient.
7. If identity remains incomplete, mark the exact field unknown; do not guess.

## Registry changes to make next

Add candidate entries only when their match rule is safe:
- Fortinet/FortiGate -> official FortiGate by SNMP.
- Cisco/IOS -> official Cisco IOS by SNMP, but family identification must be validated before broad auto-link.
- NETGEAR -> do not replace existing rule yet; add Fastpath capability/family test first.
- Ubiquiti -> keep UniFi rule; add AirOS separately only with reliable family match.
- Aruba -> do not add broad Aruba rule yet.
- YAMAHA -> L3 adapter PoC after exact MIB/OID audit.

## Commercial relevance

This audit materially improves the likely unit economics: Cisco IOS and especially FortiGate can reuse official Zabbix identity collection rather than requiring atLIB to maintain duplicate per-vendor parsers. The remaining cost driver is not raw monitoring but identity exceptions, lifecycle-source maintenance, and version-aware CVE applicability.

Pricing should therefore be gated on measured exception/manual-review rates, not simply on the existence of EoL/CVE functionality.
