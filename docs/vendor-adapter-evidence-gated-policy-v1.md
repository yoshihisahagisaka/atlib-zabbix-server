# Vendor Adapter Evidence-Gated Policy v1

Date: 2026-09-19
Status: DECIDED

## Decision
InfraVision will not attempt to fully implement every vendor/family in advance.

For vendors/families without real-device evidence:
1. Research primary documentation and record likely SNMP/MIB/lifecycle/security sources.
2. Add a read-only capability probe where useful.
3. Mark the family as Evidence Pending.
4. Do not enable production auto-linking or claim support.
5. Continue to the next high-value vendor/family.

When a real device is encountered in an internal/customer environment:
1. Collect read-only evidence (sysObjectID, sysDescr, standard MIB, private MIB candidates).
2. Confirm family/model/firmware/serial extraction.
3. Validate official Zabbix template compatibility where applicable.
4. Implement or finalize the smallest reusable adapter/template.
5. Test in dry-run/test host group.
6. Promote to Supported only after validation.
7. Preserve the resulting logic as reusable InfraVision technical capital.

## Coverage states
- Supported: real-device validated and safe for production automation.
- Prototype: implementation exists but real-device validation is pending.
- Evidence Pending: documentation/probe prepared; implementation waits for a real device.
- Unsupported/Out of Scope: technically unsuitable or outside current network-intelligence scope.

## Base plan behavior
Unknown vendors/families do not block monitoring.
Base continues Generic SNMP/ICMP discovery and reports identity/security intelligence only to the confidence supported by evidence.
Unknown / Detailed confirmation recommended is a valid result.

## Economics
This policy prevents speculative engineering from consuming the economics of the Base ¥9,980 service while ensuring every real-world exception can become reusable automation.

## Current examples
- YAMAHA RTX/SWX/WLX: Prototype; real-device validation pending.
- BUFFALO business managed switches: Evidence Pending; capability audit + read-only probe prepared.
- Brother printer/MFP: Out of Scope for current network EoL/CVE intelligence.
- FortiGate: official-template candidate; validation pending.
- Ubiquiti UniFi/UCG: existing atLIB real-device evidence exists for selected models.

## Next research behavior
Apply the same evidence-gated method to TP-Link Omada, Fortinet families, NETGEAR families, Allied Telesis, Cisco/Meraki, Aruba/HPE and later vendors.
