# InfraVision Automation Baseline & Service Menu Input v1

Date: 2026-09-19
Status: PROVISIONALLY APPROVED (仮確定)
Next gate: real-device validation later; service-menu design may proceed now.

## 1. Product decision
The current automation architecture is accepted as the provisional technical baseline for service-menu and LP design. Real-device end-to-end validation is intentionally deferred and is not a blocker for business/service design.

## 2. Base technical baseline
Customer input is minimized to network range, SNMP credentials/community, and minimum Sensor Edge/network setup information.

Flow:
Sensor Edge -> discovery -> host registration -> Generic SNMP -> family/template resolution -> monitoring -> asset identification -> EoL/CVE screening -> existing monthly report -> atLIB operator review -> approval -> customer delivery.

The existing report generation, PDF/PPTX storage, operator review/approval and customer delivery workflow remains canonical and should be extended rather than rebuilt.

## 3. Evidence rules
Asset intelligence is evidence-gated.
- Supported: real-device validated.
- Prototype: implementation exists; real-device validation pending.
- Evidence Pending: research/probe prepared; implement when a real device appears.
- Unsupported/Out of Scope: not part of current network intelligence scope.

Unknown devices do not block monitoring. Generic SNMP/ICMP continues and Unknown / Detailed confirmation recommended is a valid output.

## 4. Vulnerability semantics
A product/CPE search hit is not equivalent to an affected device.
States:
- confirmed_affected
- potentially_affected
- not_affected
- not_assessable
- lookup_failed

Base reports may call a vulnerability confirmed only when deterministic applicability is proven. Keyword-only or ambiguous/complex applicability remains potential/review-required. Missing evidence is never presented as safe.

## 5. Lifecycle semantics
Prefer manufacturer primary lifecycle evidence, then curated atLIB evidence, then supplemental sources. Unknown/fuzzy evidence is not presented as confirmed EoL.

## 6. Human review
Base report generation is automated, but the existing atLIB operator review/approval step remains. This is quality control, not recurring per-device investigation. Manual product/FW/EoL/CVE research belongs to an upper service level unless separately agreed.

## 7. Commercial principle already fixed
- Base monthly price remains JPY 9,980.
- Initial price remains JPY 30,000.
- Existing managed-operations concept/price is retained for later menu refinement.
- Base promise: almost plug-and-play monitoring; customer asset ledger is not a prerequisite.
- Value ladder:
  1. Base: 見つける
  2. Upper Intelligence: 確かめる・判断する
  3. Managed Operations: 対応する

Detailed inclusions, limits, naming and upper-tier pricing are to be finalized next. Do not embed plan entitlement decisions into the intelligence engine.

## 8. Deferred validation
Later real-device validation should cover at least:
- NETGEAR WAX625
- Ubiquiti UCG-Ultra
- model/firmware acquisition
- CPE mapping
- NVD version applicability
- Zabbix sec_* tags
- generated monthly PDF/PPTX
- operator approval/delivery path

Failure or material false-positive findings at that gate can revise the service wording or included intelligence level.

## 9. Next business-design sequence
1. Finalize service menu and customer-facing boundaries.
2. Define plan names, inclusions, limits, options and upper-tier pricing.
3. Translate into LP messaging and comparison structure.
4. Build LP.
5. Perform real-device validation before making stronger confirmed-accuracy claims in production.
