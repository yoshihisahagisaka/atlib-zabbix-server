# InfraVision Service Positioning & LP/Sales Messaging Canonical v1

Date: 2026-09-19
Status: APPROVED DIRECTION
Purpose: Canonical input for service-menu finalization, LP, and sales materials.

## 1. Plan names
Customer-facing Japanese plan names:
- atLIB InfraVision モニタープラン — JPY 9,980/month
- atLIB InfraVision オペレーションプラン — JPY 29,800/month
- atLIB InfraVision マネージドプラン — JPY 79,800/month

Current initial fee: JPY 30,000. Detailed inclusions/limits are still under refinement.

## 2. Plan responsibility model
Plan differences are defined by responsibility, not merely feature quantity.

### モニタープラン
Customer manages; InfraVision provides the mechanism to see and notice.
Concept: 「見える・気づける・自分で管理できる」
Self-service MSP characteristics are important.

### オペレーションプラン
atLIB executes predefined/previously agreed network operations.
Concept: 「決まった運用を任せる」
This is an execution/service-work contract, not broad IT management.

### マネージドプラン
atLIB supports operational judgment and management within the NETWORK domain.
Concept: 「ネットワーク運用を任せる」
Do not expand this into general 情シス代行 or company-wide IT consulting.

## 3. Monitor plan differentiators
The JPY 9,980 plan is not “monitoring only.” Current/target value includes:
- almost plug-and-play onboarding
- automatic device discovery
- ICMP/SNMP monitoring
- customer self-service portal
- host management
- maintenance settings
- notification settings
- topology visualization
- LLDP-based topology where available
- customer-entered connection/uplink information when LLDP is unavailable, allowing topology completion
- monthly automatically generated report
- automated asset / EoL / vulnerability risk screening within evidence available automatically

LP message should not overclaim definitive diagnosis. Use wording such as automatic screening/checking and show Unknown / detailed-confirmation-required when evidence is insufficient.

## 4. ICP
Core InfraVision ICP:
「ネットワーク機器はある。しかし、それを継続的に管理する人・契約・仕組みがない中小企業」

Typical conditions:
- no dedicated IT function, or only a busy part-time/single IT person
- no vendor/MSP maintenance contract
- network was built and is mostly unattended afterward
- asset list/configuration diagram is absent or stale
- devices are checked only after an incident
- firmware/EoL/vulnerability status is not routinely reviewed

Key insight:
Do not define ICP only as “no IT department.” Even a company with an IT person is a fit if nobody continuously manages the network.

Possible LP problem statement:
「そのネットワーク、今も誰かが見ていますか？」
and concept:
「構築したままのネットワークを、管理されているネットワークへ。」

Non-priority ICP:
- mature NOC/network team already operating the environment
- comprehensive MSP/vendor management already in place
- very small/low-impact networks where failure has little business impact

## 5. InfraVision vs IT経営KAIZEN boundary
Do not differentiate only by company size or price.

InfraVision:
- vertically deep in NETWORK
- makes unmanaged network infrastructure managed/visible
- monitoring, topology, network intelligence, operations, and network managed service

IT経営KAIZEN:
- horizontally broad across company IT and reaches management decisions
- IT strategy, identity, endpoints, SaaS, network, security, IT operations, DX/AI, investment, organizational design and continuous improvement
- current business-design direction assumes roughly JPY 500k/month, but pricing is not yet final

Canonical boundary:
「ネットワークの課題ならInfraVision。IT全体・組織・経営の課題になったらIT経営KAIZEN。」

InfraVision Managed must not become a low-priced substitute for IT経営KAIZEN.

## 6. FACTACT relationship
FACTACT is an execution/fact/decision infrastructure, not the service boundary itself.

InfraVision Managed may ingest network configuration, incident history, changes and device facts into FACTACT. This does not make it IT経営KAIZEN.

Conceptual layering:
- InfraVision = Network operational service/infrastructure
- FACTACT = Fact / Decision / Execution infrastructure
- IT経営KAIZEN = company-wide IT management / improvement service

## 7. Customer growth path
InfraVision can support companies in an earlier IT-management stage. As the company grows and IT becomes a management/organizational issue, IT経営KAIZEN becomes relevant.

Do not frame this only as “small company -> large company.”
Use IT-management maturity and problem layer.

Examples of transition signals:
- employee/site/SaaS growth
- need for dedicated IT governance
- ISMS/IPO/customer security requirements
- increasing IT spend
- DX/AI initiatives
- onboarding/offboarding/helpdesk overload
- need to redesign IT responsibilities and investment

InfraVision does not necessarily disappear after transition. It can remain the network operational foundation while IT経営KAIZEN uses its facts as management input.

The broader “atLIB customer growth support story” is intentionally deferred for a later project.

## 8. LP / sales-material rules
Carry this positioning into future LP and sales materials:
- Lead with the unmanaged-network problem, not technology.
- Present JPY 9,980 as self-service-capable managed visibility, not cheap monitoring.
- Emphasize low onboarding burden and “almost plug-and-play.”
- Explain topology self-completion even for non-LLDP devices as a customer-control advantage.
- Explain EoL/CVE as automated risk screening at Base; do not imply guaranteed exhaustive diagnosis.
- Differentiate the three InfraVision plans by who manages/executes/decides.
- Keep IT経営KAIZEN as a separate company-wide IT management service; optional growth-path messaging can be added later.

## 9. Next task
Finalize the detailed service contents for the three InfraVision plans:
- included functions
- target device count / limits
- alert/support boundaries
- operation quotas
- human investigation scope
- FACTACT/config scope for Managed
- initial setup scope
- options/exclusions
- exact customer-facing wording

After this is fixed, translate directly into LP structure and sales materials.
