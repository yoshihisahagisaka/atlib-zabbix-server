# InfraVision Service Specification v1

Date: 2026-09-19
Status: WORKING CANONICAL — service design substantially fixed; SLA/contract wording and some Managed limits remain to be finalized.

## 1. Product boundary

InfraVision is a NETWORK-focused managed service.

Canonical responsibility ladder:
- モニタープラン: **自分で管理できる**
- オペレーションプラン: **日常運用を任せられる**
- マネージドプラン: **ネットワーク管理そのものを任せられる**

Do not expand InfraVision into company-wide IT consulting. Company-wide IT, organization, strategy, SaaS/ID/endpoints, DX/AI and management improvement belong to IT経営KAIZEN.

## 2. Pricing

| Plan | Monthly | Initial |
|---|---:|---:|
| モニタープラン | JPY 9,980 | JPY 30,000 |
| オペレーションプラン | JPY 29,800 | JPY 50,000 (working baseline) |
| マネージドプラン | JPY 79,800 | JPY 50,000+ (working baseline) |

Monitor initial fee means monitoring-start setup.
Upper-plan initial fee additionally covers operation/management design.
Complex/multi-site environments may require separate/additional quotation.

Current target-device baseline remains up to 50 devices; 50+ is separately handled. Exact overage pricing remains subject to final confirmation.

## 3. Common monitoring foundation

All plans inherit the InfraVision monitoring foundation:
- Sensor Edge / customer Zabbix Proxy based monitoring
- automatic device discovery
- ICMP availability monitoring
- SNMP monitoring
- unknown/new-device detection where configured
- customer portal
- network topology visualization
- LLDP-based relationship discovery where available
- manual connection/uplink completion by customer when LLDP is unavailable
- monthly report
- automatic asset identification where obtainable
- automated EoL/vulnerability risk screening with evidence/confidence semantics
- Unknown / detailed-confirmation-required is a valid result and must not be presented as safe

## 4. Existing customer self-service portal — confirmed implementation

The Monitor plan is not “alerts only.” Existing portal implementation already allows customers to operate key monitoring controls themselves.

### Notification settings
Customer can:
- add/delete notification email addresses
- select notification severity:
  - 重大のみ
  - 警告以上
  - すべて
- select notification period:
  - 24時間
  - 営業時間のみ（平日 9:00-18:00）
- enable/disable customer notification for unknown SNMP-capable device detection when available

Important wording:
This is **通知レベル**, not a change to the underlying monitoring level/scope.

### Maintenance / suppression settings
Customer can:
- create/edit/delete maintenance windows
- choose start/end time
- choose all devices or selected devices
- choose:
  - 停止通知のみ
  - 監視停止

The backend applies these settings through the Zabbix API and checks customer ownership boundaries.

### Product implication
Monitor positioning:
「普段は自分で管理できる。でも、監視・検知・可視化・レポートはInfraVisionが自動でやる。」

## 5. モニタープラン — JPY 9,980/month

Concept:
**見える・気づける・自分で管理できる。**

Included:
- all common monitoring foundation capabilities
- self-service notification settings
- self-service maintenance/suppression settings
- self-service host/device management
- self-service topology management/completion
- automatic monthly reporting
- automated EoL/CVE screening

Human investigation of individual EoL/CVE applicability is not included as a recurring obligation.

Customer is responsible for operational judgment and execution.

Initial fee JPY 30,000 covers monitoring-start setup such as:
- Sensor Edge/customer environment registration
- network range
- SNMP prerequisites
- proxy/host-group/discovery setup as applicable
- initial monitoring confirmation

Commercial promise:
Almost plug-and-play; a complete customer asset ledger is not required before monitoring starts.

## 6. オペレーションプラン — JPY 29,800/month

Concept:
**日常運用を自動化し、軽微な作業を任せる。**

Includes Monitor plus:

### A. Automated / semi-automated routine operations
The service should be designed so recurring human work is minimized.

Examples:
- scheduled periodic device reboot, e.g. every 3 months, where technically supported and agreed
- default use of manufacturer/device automatic-update settings where appropriate
- periodic review/collection of manufacturer vulnerability information
- automated InfraVision screening and exception surfacing

These are not counted as customer request-work occurrences when they run as predefined automated operations.

### B. Customer-requested light remote work
Working limit: **up to 2 requests/month**.

Primary standard scope:
- VPN account add/remove
- Wi-Fi password change
- network-device password change

A “request” is a customer-initiated light remote operation within the predefined standard scope. Exact time/complexity ceiling and carry-over rules remain to be finalized.

Not included as light operations:
- VLAN addition/change
- IP address-plan management/change
- DHCP design/change
- routing change
- firewall policy design/change
- device replacement/addition
- network redesign
- onsite work

These require separate maintenance/change/project quotation as appropriate.

Responsibility principle:
**The required action is already defined; atLIB executes it.**
Operation is not a broad network-management responsibility.

Initial fee JPY 50,000 baseline covers Monitor setup plus operation-automation design, including applicable schedules, maintenance windows, automatic-update policy and execution boundaries.

## 7. マネージドプラン — JPY 79,800/month

Concept:
**ネットワークの状態・リスク・構成をatLIBが継続管理する。**

Includes Operation plus:

### A. Managed network state
- ongoing network configuration/inventory awareness
- network ledger maintenance
- configuration information collection/management where technically supported
- incident/change/response history management
- periodic network health/risk review

### B. Network ledger / operational history
- atLIB maintains the customer network ledger and relevant operational history as an internal service capability.
- Managed service records may include device/network facts, configuration facts, incident history, change history, response history, and operational decisions/evidence.
- The implementation platform is an internal atLIB concern and is not part of the customer-facing InfraVision product proposition.

### C. Incident triage / response support
- first-level investigation when monitoring detects an issue
- identify likely affected device/area and impact where evidence permits
- recommend response path
- execute actions that are within the agreed monthly managed-operation scope
- design/construction/replacement work remains separately quoted

Do not promise unconditional restoration or a full hardware/vendor maintenance SLA unless separately contracted.

### D. EoL / vulnerability human verification
When automatic screening surfaces material issues or ambiguity, atLIB may perform human verification using available manufacturer/authoritative information and observed/customer-provided facts.

This is a higher responsibility level than Monitor/Operation automatic screening.

### E. Network consultation desk
Customer can submit NETWORK-related questions through the designated inquiry form.

atLIB answers with reference to InfraVision monitoring data and atLIB-held customer network facts/history where available.

Examples:
- Wi-Fi/network performance concern
- whether an AP/device should be added or replaced
- connection/location questions for a new network-connected device
- whether a device/firmware issue requires action

Consultation and execution are separate:
- consultation/advice: intended to be available without consuming a light-work request
- light remote execution: subject to Managed operation limits
- design/build/change projects: separate quotation

Exact Managed customer-request work limit is not yet finalized. Do not advertise “unlimited work.”

### F. Explicit exclusions / separately quoted
Even under Managed, the following are not automatically unlimited monthly-fee work:
- VLAN design/addition/change
- IP/DHCP redesign
- routing redesign/change
- firewall policy design/change
- hardware replacement/addition
- network expansion/renewal
- onsite work
- vendor/hardware maintenance obligations not separately contracted

## 8. Monthly-scope boundary

The commercial boundary is based on **maintaining the existing network** versus **changing/building the network**, not simply on the number of clicks or commands.

### A. Monitor

Customer performs operational actions themselves through the portal where supported.

Included service-side work:
- automated monitoring/detection
- automated reporting
- automated EoL/CVE screening
- operation of the customer self-service platform

Customer-requested remote operations are not included.

### B. Operation

In addition to predefined automated operations, customer-requested light remote work is included up to **2 requests/month**.

Standard in-scope examples:
- VPN account add/remove
- Wi-Fi password change
- network-device administrator/user password change

The request must be executable under the existing agreed network design and procedure.

The following principle determines whether a request remains a light operation:

> **No design decision, topology change, policy redesign, or new equipment implementation is required.**

If investigation or design is required before the requested change can safely be executed, it is not automatically an Operation-plan light request.

### C. Managed

Managed uses a fair-use operational model rather than advertising a fixed number of work requests.

#### Included in the monthly fee — normal operation of the existing network
- network-related consultation through the designated inquiry channel
- checking current network configuration/inventory/history before answering
- first-level incident triage
- investigation of monitoring alerts and operational anomalies
- response recommendation
- EoL/vulnerability detailed confirmation when operationally relevant
- maintenance of the network ledger and relevant operational history
- VPN account add/remove
- Wi-Fi/network-device password change
- other low-risk remote operational work that does not change the agreed network design
- necessary operational follow-up initiated by atLIB from InfraVision monitoring findings

These activities should not be marketed as “unlimited work.” They are included when reasonably required for ordinary ongoing management of the contracted network.

#### Separately quoted — change/build/project work
Examples:
- new VLAN or segmentation design/change
- IP addressing or DHCP redesign/change
- routing design/change
- firewall policy design/change
- new AP/switch/router/firewall installation
- device replacement/migration
- new site/network construction
- major wireless redesign/site survey
- large-scale firmware migration requiring project planning
- cabling/physical construction
- onsite work
- work requiring coordination with third-party vendors beyond normal first-line liaison
- any company-wide IT work outside the network boundary

### D. Decision rule for ambiguous requests

Use these questions in order:

1. Is the request within the contracted network scope?
   - No -> outside InfraVision / separate service.
2. Is it necessary to maintain or restore the existing agreed network state?
   - Yes -> Managed monthly scope in principle.
3. Can it be executed safely under an existing procedure without a new design decision?
   - Yes -> light operation; Operation request slot or Managed monthly scope.
4. Does it alter architecture, security policy, segmentation, addressing, capacity, equipment or physical layout?
   - Yes -> separate quotation/change project.
5. Is the work unusually high-volume, repetitive due to customer-side process, or materially beyond ordinary management effort?
   - Yes -> fair-use review and possible separate quotation.

### E. Fair-use policy for Managed

Customer-facing sales material should say:
**「日常的なネットワーク運用・相談は月額内」**

Contract/terms should reserve the right to scope and quote separately when:
- request volume materially exceeds normal ongoing network management
- a single request requires substantial investigation/engineering time
- bulk account/device changes are requested
- repeated work results from a customer-controlled recurring process that should be redesigned/automated
- third-party/vendor work or onsite attendance is required

Do not lead with an arbitrary monthly request count for Managed. If operational data later shows the need for quantitative thresholds, define them from actual delivery workload.

### F. Examples

| Customer request / event | Monitor | Operation | Managed |
|---|---|---|---|
| Change notification email/severity/time | Customer self-service | Customer self-service | Customer self-service |
| Planned maintenance suppression | Customer self-service | Customer self-service | Customer self-service / atLIB support as needed |
| VPN account add/remove | Not included | Light-work slot | Monthly scope |
| Wi-Fi/NW password change | Not included | Light-work slot | Monthly scope |
| “Wi-Fi seems slow; can you check?” | Not included | Separate investigation | Monthly consultation/triage |
| Monitoring alert investigation | Automated alert only | Automated alert; human investigation not standard | atLIB first-level triage |
| EoL/CVE ambiguous result detailed check | Not standard | Not standard | Monthly scope when relevant |
| Add a VLAN | Separate | Separate | Separate change work |
| Redesign IP/DHCP | Separate | Separate | Separate change work |
| Add/replace an AP | Separate | Separate | Advice/need assessment may be monthly scope; implementation separately quoted |
| Replace a switch/firewall | Separate | Separate | Advice/need assessment may be monthly scope; migration/replacement separately quoted |
| Build a new office/site network | Separate project | Separate project | Separate project |

## 9. Plan comparison — current working version

| Capability | Monitor | Operation | Managed |
|---|---|---|---|
| Automatic discovery / ICMP / SNMP | Yes | Yes | Yes |
| Customer portal | Yes | Yes | Yes |
| Notification destination settings | Self-service | Self-service | Self-service |
| Notification severity/time settings | Self-service | Self-service | Self-service |
| Maintenance / monitoring suppression | Self-service | Self-service | Self-service |
| Topology + manual completion | Yes | Yes | Yes |
| Monthly report | Yes | Yes | Yes |
| Automatic EoL/CVE screening | Yes | Yes | Yes |
| Human EoL/CVE verification | No recurring obligation | No recurring obligation | Yes, when operationally relevant |
| Scheduled routine automation | No | Yes | Yes |
| VPN account add/remove | No | Up to 2 request slots/month | Included subject to Managed limits |
| Wi-Fi/NW password change | No | Up to 2 request slots/month | Included subject to Managed limits |
| Incident first-level triage | No | No | Yes |
| Network ledger/history managed by atLIB | Customer self-manages | Customer self-manages | Yes |
| FACTACT operational facts | No | Not standard | Yes |
| Network consultation desk | No | No | Yes |
| Network design/change project | Separate | Separate | Separate |
| Company-wide IT strategy/consulting | No | No | No — IT経営KAIZEN |

## 10. LP / sales wording

Recommended ladder:
- モニター: 「見える・気づける・自分で管理できる」
- オペレーション: 「日常運用を自動化し、軽微な作業を任せる」
- マネージド: 「ネットワーク管理そのものを任せる」

Monitor should be positioned as a self-service network-management foundation, not cheap alerting.

Operation should emphasize automation rather than recurring manual labor.

Managed should emphasize environmental understanding, environmental facts/history, triage and consultation rather than “unlimited work.”

## 11. Remaining decisions before FINAL

1. Managed fair-use wording / contract threshold after operational validation
2. Exact definition of one Operation request: time/complexity/target-device limits
3. Whether unused Operation requests expire or carry over
4. Managed staffed support hours and response target
5. Exact after-hours behavior: automated notification vs atLIB human escalation
6. Phone/Slack/email/form channel policy
7. Exact 50+ device overage pricing and multi-site rules
8. Contract/SLA wording for best-effort triage, vendor dependencies and separately quoted work
