# InfraVision Service Plan Principle v1

Date: 2026-09-19
Status: DECIDED baseline; detailed plan contents may be refined later.

## Decision

InfraVision keeps the current price setting. The service-plan architecture is fixed around three responsibility levels:

1. Base (9,800/9,980-yen current price tier): **find / screen automatically**
2. Upper intelligence service: **verify facts / assess / support decision**
3. Managed operations: **execute remediation/operations**

Detailed entitlements and wording will be reviewed later. This decision intentionally does not change current prices.

## Base principle: "plug in and monitoring starts"

The Base plan must preserve InfraVision's existing product promise: deployment should require almost no customer-side asset preparation.

Expected customer inputs are limited to connection/discovery prerequisites such as:
- network range(s)
- SNMP community/credentials as applicable
- minimum installation/network information needed for Sensor Edge

The Base plan must NOT require the customer to prepare a complete device ledger, firmware list, purchase history, or support-contract inventory before monitoring can begin.

Target flow:

Sensor Edge -> network/SNMP settings -> automatic discovery -> host registration -> Generic SNMP -> vendor/family/template resolution -> monitoring -> automated asset/lifecycle/vulnerability screening.

## Base intelligence semantics

Base outputs only what can be produced automatically with defensible evidence.

Examples:
- automatically identified network devices
- Vendor/Model/Firmware where obtainable
- possible lifecycle concern
- possible vulnerability concern
- devices requiring detailed confirmation
- unknown/unassessable state

Base must not convert incomplete evidence into a confirmed EoL or confirmed affected-CVE statement.

Unknown is a valid result, not a system failure.

## Upper intelligence principle

For the upper service, customer-provided device information may be requested and treated as an input Fact after validation/cross-checking.

Possible Fact inputs:
- manufacturer
- model
- firmware/OS version
- serial
- purchase/installation date
- maintenance/support contract and expiry

atLIB may use human review to reconcile:
- automatically observed SNMP/device evidence
- customer-provided facts
- manufacturer primary lifecycle/security information
- CVE/version applicability data

The upper service therefore provides a higher responsibility level than automated screening.

## Product language

Base: **find / notice**
Upper: **verify / assess / decide**
Managed operations: **act**

Japanese working expression:
- Base: 「見つける」
- Upper: 「確かめる・判断する」
- Managed: 「対応する」

## Engineering consequence

Asset Intelligence remains one common engine. Commercial plans are entitlement/presentation layers.

Engineering priority for Base:
- maximize useful automatic output with no extra customer asset-data collection;
- maximize identity coverage;
- minimize false positives;
- expose Unknown explicitly;
- minimize recurring human labor.

Engineering priority for Upper:
- make automated evidence reusable for human verification;
- preserve provenance/evidence;
- support customer-supplied Fact reconciliation;
- support deterministic lifecycle/CVE applicability assessment.

## Scope note

Brother laser multifunction printers are outside the current network-device EoL/vulnerability automation scope. Existing Brother implementation may remain in the repository, but it is not a priority in the current InfraVision network-equipment automation roadmap.

Current priority vendors/families:
- Fortinet
- Cisco
- NETGEAR
- Ubiquiti
- Aruba/HPE
- YAMAHA

## Deferred

The following are deliberately NOT finalized in this decision:
- exact upper-plan price
- exact upper-plan name
- detailed entitlement boundary
- report layout/wording
- device-count limits
- SLA/human-review cadence
- relationship to the existing managed-operations plan

These will be refined after automation coverage and operating-cost measurements.
