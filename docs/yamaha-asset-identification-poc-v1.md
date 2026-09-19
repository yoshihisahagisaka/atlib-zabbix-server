# YAMAHA Asset Identification PoC v1

Date: 2026-09-19
Status: design validated from Yamaha primary documentation; real-device verification pending.

## Conclusion

YAMAHA is a strong L3 atLIB adapter candidate for the Base-plan "plug in and monitor" model.

Primary documentation confirms:
- Yamaha network products support SNMP.
- sysObjectID returns a device OID defined in Yamaha private MIB.
- On SWX2210P, sysDescr contains device name and firmware revision.
- Yamaha switch private MIB exposes firmware revision (ysfRevision).
- Yamaha publishes firmware and release-note information.

Therefore the first PoC should not require customer-provided asset data. It should derive model/family and firmware from SNMP evidence and mark unresolved fields Unknown.

## Enterprise

Yamaha enterprise number observed in official private-MIB documentation:
- 1.3.6.1.4.1.1182

Candidate first-stage resolver:
- sysObjectID contains/prefix 1.3.6.1.4.1.1182 -> canonical vendor YAMAHA.

Do not auto-link one family-specific monitoring template solely from the enterprise prefix. Family resolution is a separate step.

## SWX path

Official SWX documentation provides particularly strong evidence:

- sysDescr: device name + firmware revision
- sysObjectID: Yamaha private-MIB device OID
- ysfRevision: 1.3.6.1.4.1.1182.3.2.3, firmware version

PoC extraction:
1. vendor = YAMAHA from enterprise sysObjectID
2. model = parse device name from sysDescr and/or map exact sysObjectID
3. firmware = ysfRevision where supported; sysDescr fallback
4. serial = Unknown until a verified OID is selected
5. preserve raw sysObjectID/sysDescr/ysfRevision evidence

Expected initial confidence after real-device verification:
- vendor: confirmed
- model: probable -> confirmed once exact sysObjectID mapping is verified
- firmware: confirmed when ysfRevision succeeds
- serial: unknown

## RTX path

Yamaha router product specifications confirm SNMP v1/v2c/v3 support. Yamaha also publishes SNMP/private-MIB technical information.

The current evidence is sufficient to create a Yamaha-vendor resolver, but not yet sufficient to hard-code a universal RTX model/firmware OID across the family.

PoC order:
1. collect actual RTX1300/RTX1220/RTX830 sysObjectID
2. collect sysDescr
3. walk Yamaha private-MIB identity subtree read-only
4. identify stable model/firmware objects
5. compare with Yamaha firmware/release-note page
6. only then promote RTX extraction to confirmed.

## Family resolver

Target:
YAMAHA enterprise
 -> SWX / RTX / WLX / other
 -> family-specific identity collector
 -> canonical Vendor/Model/Firmware

The Base plan should stop safely at:
- YAMAHA / model unknown / firmware unknown
when family evidence is insufficient.

## Base-plan output

Automatic only:
- identified vendor/family/model/firmware where supported
- possible EoL/lifecycle concern
- possible vulnerability concern
- detailed-confirmation-required
- unknown

No customer asset ledger is required for Base.

## Upper-plan reuse

The same observed SNMP evidence becomes corroborating evidence against customer-supplied Facts. Human review may then confirm model/firmware/lifecycle/CVE applicability.

## Implementation gate

Safe to implement now:
- Yamaha enterprise vendor resolver
- evidence collection design
- SWX firmware collector/template prototype

Requires real-device evidence before broad production enablement:
- exact family classification rules
- RTX model/firmware extraction
- WLX model/firmware extraction
- serial extraction
- exact lifecycle/CVE applicability.
