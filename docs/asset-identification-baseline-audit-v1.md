# Asset Identification Baseline Audit v1

Date: 2026-09-19  
Scope: current repository implementation before new vendor expansion.

## Executive result

現行InfraVisionには、顧客オンボーディングからGeneric SNMPをリンクし、特定ベンダーでは追加識別テンプレートをリンクし、Host InventoryをCVE/EoLバッチへ渡す骨格が既に存在する。

最大の不足は「Discoveryそのもの」ではなく次の4点。

1. Vendor Template resolverが`setup_discovery.py`内のハードコード配列。
2. Asset identityのEvidence/Confidenceを永続化していない。
3. CVEはhardware CPEまたはkeyword検索が中心で、実機Firmwareのaffected range判定が未完成。
4. Coverage/Unknown/Human review timeを商用判断用KPIとして計測していない。

従ってv1では既存フローを置換せず、観測可能性とresolverの一般化から行う。

## Current pipeline evidence

| Stage | Current implementation | Assessment |
|---|---|---|
| Customer scoped discovery | `setup_discovery.py` | Existing |
| Generic SNMP link | `TEMPLATE_ID_SNMP=10226` | Existing |
| Discovery identity evidence | sysObjectID + sysDescr | Existing |
| Vendor conditional link | `VENDOR_TEMPLATE_RULES` | Existing, hardcoded |
| Ubiquiti identification | vendor/model/software_full | Verified in runbook |
| Brother identification | vendor/model/software_full | Verified in runbook |
| NETGEAR identification | vendor only | Model/FW gap |
| Inventory API input | `get_hosts_inventory()` | Existing |
| CPE mapping | `cpe_mapper.py` | Existing |
| CVE lookup | NVD + CISA KEV | Existing |
| HW/SW EoL | `eol_client.py` | Existing |
| Confidence semantics | EoL confirmed/fuzzy/unknown | Partial |
| Asset identity confidence | none | Missing |
| Firmware applicability | limited/manual fixed_in_version | Missing as generic mechanism |
| Commercial coverage metrics | vendor_census only | Partial |

## Generic SNMP conclusion

Generic SNMP is suitable as the mandatory L1 onboarding template because it provides a stable common discovery/monitoring base and the existing onboarding already links it automatically.

However, Generic SNMP alone must not be assumed to provide normalized Vendor + Model + Firmware for every device. Current production evidence already proves both outcomes:

- Ubiquiti/Brother can be normalized using SNMP evidence plus preprocessing.
- NETGEAR WAX625 returns insufficient standard information for Model/Firmware in the currently tested OIDs.

Therefore success criterion is not “Generic SNMP alone identifies everything”; it is “Generic SNMP automatically establishes the evidence and routing point from which the best available identification method is selected.”

## Existing resolver assessment

Current `VENDOR_TEMPLATE_RULES` contains NETGEAR, Brother and Ubiquiti UniFi.

Strengths:
- Customer onboarding automatically creates conditional Discovery Actions.
- sysObjectID enterprise number is preferred where unique.
- sysDescr fallback exists for devices exposing generic Net-SNMP sysObjectID.
- Missing vendor template fails safely by skipping that vendor.

Limitations:
- Rules require Python code edits.
- No rule priority/conflict policy.
- No explicit distinction between official Zabbix vendor templates and atLIB identification templates.
- No supported-model scope metadata.
- No evidence/confidence metadata.
- No coverage telemetry.

## v1 resolver contract

Each rule should eventually expose:

```yaml
id: vendor-or-family-id
vendor: canonical vendor
match:
  source: sysobjectid | sysdescr
  operator: prefix | contains | regex
  value: ...
template:
  type: zabbix_official | atlib_identification
  name: ...
identity:
  vendor: expected confidence
  model: expected confidence
  firmware: expected confidence
support:
  families: []
  verified_models: []
  evidence: []
```

The first implementation may remain Python-backed, but rule data must be separable from orchestration logic.

## Coverage measurement definition

For every inventory-enabled host record:

- vendor_present
- model_present
- firmware_present
- identity_complete = all three present
- lifecycle_determined
- vulnerability_lookup_succeeded
- vulnerability_applicability_determined
- manual_review_required

Aggregate per customer and globally:

- vendor coverage %
- model coverage %
- firmware coverage %
- complete identity %
- lifecycle determined %
- vulnerability applicability determined %
- unknown %
- manual review %

Do not count a keyword CVE hit as “applicability determined”.

## Immediate implementation order

1. Add a read-only asset coverage audit command.
2. Output per-host missing fields and aggregate metrics.
3. Refactor vendor rule definitions away from orchestration.
4. Add evidence/confidence persistence without changing customer-facing reports.
5. Audit official Zabbix vendor templates against initial vendor matrix.
6. Add YAMAHA only after L1/L2 audit identifies the exact gap.
7. Harden CVE version applicability.
8. Measure real operational cost before plan/price decision.

## Commercial decision gate

No decision is made here on whether lifecycle/vulnerability belongs in the 9,800-yen plan.

Before pricing review, collect:
- complete identity rate,
- lifecycle determined rate,
- vulnerability applicability rate,
- unknown/manual review rate,
- new adapter engineering hours,
- monthly human review minutes/customer,
- external data/API cost/customer,
- support/remediation workload.

The commercial layer can then choose which capabilities to expose without redesigning the collection engine.
