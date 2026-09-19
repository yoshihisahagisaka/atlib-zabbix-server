# InfraVision Asset Identification Job v1

Date: 2026-09-19
Status: implementation ready; production schedule activation requires dry-run validation.

## Purpose

Complete the automatic loop behind the Base-plan "plug in and monitor" promise without requiring a customer asset ledger.

## Runtime sequence

1. Sensor Edge / Zabbix network discovery creates the host and links Generic SNMP.
2. Generic/identity items collect sysObjectID/sysDescr.
3. asset_identification_cycle.py evaluates accumulated host evidence.
4. family_resolver.py returns only evidence-backed resolver candidates.
5. apply_family_templates.py links a template only when the result is unique.
6. linked template collects richer Model/Firmware/Serial inventory.
7. existing CVE/EoL batch evaluates the enriched inventory separately.

## Safety

- default execution is dry-run
- --apply is explicit
- no template is unlinked
- ambiguous devices are not modified
- unresolved devices are not modified
- rules requiring evidence from multiple discovery checks are resolved post-discovery, not in a single Discovery Action
- Brother/printer scope is disabled in the active resolver registry

## Production rollout

Stage 1: dry-run against atLIB/known test hosts and inspect MATCH/AMBIGUOUS/UNRESOLVED.
Stage 2: --apply against a dedicated test host group.
Stage 3: confirm linked templates collect expected inventory and do not create item-key conflicts.
Stage 4: enable periodic execution for MSP host groups.
Stage 5: measure identification coverage and unknown rate.

## Scheduling

Do not couple this to customer onboarding synchronously. Discovery and SNMP item collection are asynchronous.

Recommended operational model:
- onboarding starts discovery immediately;
- periodic asset-identification job re-evaluates hosts after evidence arrives;
- repeated runs are idempotent for already-linked templates.

The exact scheduler platform/cadence should follow the existing production batch deployment mechanism. Do not introduce a second scheduler until the current deployment path is confirmed.

## Acceptance metrics

- unique resolver match rate
- template-link success rate
- ambiguous rate
- unresolved rate
- Vendor completeness
- Model completeness
- Firmware completeness
- complete Vendor+Model+Firmware rate
- recurring human intervention required by Base plan
