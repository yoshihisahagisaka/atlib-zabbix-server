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

## 10. Monitoring, notification and staffed-response policy

### A. Separate monitoring from human response

InfraVision monitoring runs continuously where the customer's Sensor Edge / Zabbix monitoring path is available.

Customer-facing wording must distinguish:
- **24-hour automated monitoring/detection**
- **customer-configurable automated notification**
- **atLIB staffed investigation/response**

Do not use wording that can reasonably be read as “24/365 staffed support” unless a separate contract explicitly provides it.

### B. Automated notification

The existing customer portal is the standard control surface for customer alert delivery.

Customer can configure:
- notification destination email addresses
- severity threshold: 重大のみ / 警告以上 / すべて
- notification period: 24時間 / 営業時間のみ（平日 9:00-18:00）
- unknown-device notification where available
- maintenance windows and notification/monitoring suppression

Therefore automated notification is primarily **customer-policy-driven**, not hard-coded per service plan.

### C. Staffed response by plan

#### Monitor
- no routine atLIB human triage obligation
- customer receives/observes automated monitoring information according to configured notification settings
- customer makes the operational decision or requests separately quoted support

#### Operation
- no general incident-triage obligation
- predefined automated operations continue according to agreed design
- customer-requested standard light work is handled within the Operation request allowance
- incident investigation outside a predefined operation is not automatically included

#### Managed
- atLIB performs first-level incident triage for relevant InfraVision monitoring events
- atLIB checks current monitoring/configuration/history facts, assesses likely scope/cause where possible, and determines/recommends the next action
- actions within ordinary existing-network management may be performed within monthly scope
- hardware/vendor maintenance, onsite work, redesign and project work remain separate

### D. Standard staffed window — working baseline

Unless a separate option/contract states otherwise:

**atLIB staffed Managed response: business days 9:00-18:00 (Japan time).**

This is the current service-design baseline and must be aligned with actual company operating days/holiday definitions before FINAL contract wording.

Outside the staffed window:
- automated monitoring continues
- automated customer notification follows the customer's portal settings
- no standard promise of immediate atLIB human investigation or phone escalation
- unresolved events are reviewed in the next staffed window according to severity/operational priority

This keeps the JPY 79,800 Managed plan economically distinct from a 24/365 NOC/maintenance contract.

### E. Communication channels

Working channel design:
- **Portal**: monitoring status, customer self-service settings, topology/monitoring controls
- **Email**: automated alert delivery
- **Inquiry form**: standard Managed network consultation / support request
- **Phone**: escalation channel for atLIB when a material ongoing incident requires direct customer coordination during staffed hours

Do not position Slack as the default unlimited Managed consultation channel. If Slack is offered for specific customers, treat it as an optional communication interface rather than a broader service scope.

### F. Response target versus restoration SLA

InfraVision Managed should define an **initial review/response target**, not a guaranteed restoration time.

Reason:
- restoration may depend on customer access, ISP, carrier, hardware vendor, replacement stock, onsite work or third-party configuration
- the JPY 79,800 standard Managed plan is not a hardware/vendor maintenance SLA

Recommended commercial structure:
- automated detection/notification: continuous according to system availability and customer settings
- staffed first review: within the standard staffed window
- response target: define after validating actual support capacity
- restoration time: no standard guarantee
- urgent/after-hours staffed response: future separate option if commercially required

Do not publish a numerical first-response SLA until delivery staffing and escalation operations are validated.

### G. Incident lifecycle for Managed

1. InfraVision detects an event.
2. Automated notification is sent according to customer settings.
3. During the staffed window, atLIB reviews relevant Managed events.
4. atLIB checks monitoring data and known network configuration/history.
5. atLIB classifies the situation:
   - informational / recovered
   - customer action required
   - atLIB in-scope remote operation
   - third-party/vendor action required
   - separate change/project work required
6. atLIB records the relevant operational history.
7. atLIB communicates the result/next action through the appropriate channel.

### H. Sales wording

Recommended:
**「24時間の自動監視と、営業時間内の有人一次切り分け。」**

Supporting wording:
**「夜間・休日も監視と自動通知は継続。マネージドプランでは、営業時間内にatLIBが障害状況を確認し、対応方針をご案内します。」**

Avoid:
- 「24時間365日サポート」
- 「いつでもすぐ対応」
- 「障害を必ず復旧」
- 「24時間有人監視」

unless separately contracted and operationally staffed.

## 11. Customer-facing final comparison

The customer-facing comparison should explain the **reason to upgrade**, not enumerate every backend function.

| | モニタープラン | オペレーションプラン | マネージドプラン |
|---|---|---|---|
| Monthly | **JPY 9,980** | **JPY 29,800** | **JPY 79,800** |
| Initial | **JPY 30,000** | **JPY 50,000** | **JPY 50,000+** |
| Core value | **見える・気づける・自分で管理** | **日常運用まで任せる** | **NW管理そのものを任せる** |
| Best fit | NWを放置したくない | 定型運用の手間を減らしたい | NW担当者がいない／管理まで任せたい |
| 24h automated monitoring | Yes | Yes | Yes |
| Automatic alert | Yes | Yes | Yes |
| Customer notification settings | Yes | Yes | Yes |
| Maintenance/suppression settings | Yes | Yes | Yes |
| Topology / monthly report | Yes | Yes | Yes |
| Automatic EoL/CVE screening | Yes | Yes | Yes |
| Routine operation automation | — | Yes | Yes |
| Light remote requests | — | Up to 2/month | Normal ongoing operation included |
| Human incident triage | — | — | Business hours |
| Human EoL/CVE confirmation | — | — | When operationally relevant |
| Network ledger/history maintained by atLIB | — | — | Yes |
| Network consultation desk | — | — | Yes |
| Design/build/change projects | Separate | Separate | Separate |

### Upgrade story

#### Monitor -> Operation
Customer trigger:
**「見えるようにはなった。でも、毎回自分で作業するのが面倒。」**

Value added:
- predefined operations are automated
- light standard operations can be delegated
- customer operational workload is reduced

Sales phrase:
**「監視するだけでなく、決まった運用まで自動化・代行します。」**

#### Operation -> Managed
Customer trigger:
**「作業だけでなく、障害時の調査や日々の判断も任せたい。」**

Value added:
- atLIB understands the customer's network state/history
- atLIB performs first-level incident triage
- atLIB performs relevant detailed EoL/vulnerability confirmation
- customer can consult about network issues
- ordinary ongoing network management is handled without reducing the service to a simple request-count model

Sales phrase:
**「作業を任せるだけでなく、ネットワークを把握しているatLIBが、日々の管理・相談・一次切り分けまで担います。」**

### Do not sell by feature-count alone

The plans should not appear as:
- cheap = few features
- expensive = more buttons/features

The responsibility level changes:
1. Monitor: **customer decides and operates**
2. Operation: **customer decides; atLIB/automation executes predefined operations**
3. Managed: **atLIB also supports operational assessment, triage and ongoing management**

This responsibility ladder is the primary commercial differentiator.

### Recommended plan-card copy

#### モニタープラン
**ネットワークを、まず「見える状態」へ。**

24時間の自動監視、異常通知、構成可視化、月次レポート。通知先や通知レベル、メンテナンス時の監視抑止もポータルから自分で設定できます。

CTA/supporting phrase:
**「NWは自社で管理する。でも、放置はしたくない企業へ。」**

#### オペレーションプラン
**監視だけでなく、日常運用の手間も減らす。**

モニターの全機能に加え、定期再起動などの運用自動化と、VPNアカウント追加・削除やパスワード変更などの軽微なリモート作業を月2回まで依頼できます。

CTA/supporting phrase:
**「判断は自社で。決まった運用はatLIBへ。」**

#### マネージドプラン
**ネットワーク担当者がいなくても、管理されている状態へ。**

atLIBがネットワークの構成・履歴を継続的に把握。24時間の自動監視に加え、営業時間内の障害一次切り分け、NW相談、EoL・脆弱性の詳細確認、日常的な運用まで支援します。

CTA/supporting phrase:
**「ネットワークの管理そのものをatLIBへ。」**

### Scope note for customer materials

Use a short note rather than filling the comparison table with exclusions:

> ※ 各プランの月額範囲は既存ネットワークの監視・運用を対象とします。VLAN/IP/FW等の設計変更、機器増設・交換、新拠点構築、現地作業等は別途お見積りとなります。

For Managed:

> ※ マネージドプランの日常運用・NW相談は通常利用の範囲で月額に含まれます。大規模・高頻度な変更作業や設計・構築を伴う対応は別途お見積りとなります。

## 12. Commercial operating rules — working baseline

### A. Initial fee scope

#### Monitor — JPY 30,000
The initial fee covers standard onboarding required to start InfraVision monitoring.

Standard scope:
- customer/environment registration
- Sensor Edge / monitoring connection setup guidance and registration
- target network range registration
- customer Zabbix Proxy / host-group / discovery setup as applicable
- SNMP prerequisite confirmation
- initial automatic discovery execution
- initial monitoring-status confirmation
- customer portal account/setup
- standard notification baseline setup
- initial topology/asset-data acquisition where technically available

The initial fee does **not** mean a full network audit, network redesign, remediation, onsite survey, cabling, or manual creation of a complete legacy asset ledger.

Commercial principle:
**The customer should not need to prepare a perfect asset ledger before onboarding.**

#### Operation — JPY 50,000
Includes Monitor onboarding plus **operation-automation design**.

Additional standard scope:
- identify devices/actions eligible for predefined operation
- agree periodic reboot schedule where used
- agree automatic-update / patch-operation policy where applicable
- define maintenance window
- define actions safe for automatic execution
- define actions requiring customer approval
- confirm standard light-request scope and execution prerequisites
- initial setup/test of agreed automated operations where technically supported

#### Managed — JPY 50,000 baseline
Includes Monitor onboarding plus **managed-operation handoff/setup**.

Additional standard scope:
- establish initial network management ledger from automatically obtained and customer-provided facts
- confirm important network roles/topology
- define incident contact/escalation path
- confirm inquiry/support channel
- define known third-party/vendor dependencies
- confirm operational boundaries and separately quoted change areas
- create the initial managed baseline used for future triage and consultation

If the customer has multiple sites, unusually complex topology, large device volume, undocumented legacy equipment, or requires material manual investigation, additional onboarding/design work may be quoted separately.

### B. Definition of one Operation request

Operation includes up to **2 customer-requested light remote work requests per month**.

One request means:
**one customer instruction, for one operational purpose, executable as one standard work unit under the existing agreed design/procedure.**

Typical one-request examples:
- add one VPN account
- remove one VPN account
- change one Wi-Fi password under the agreed standard procedure
- change one network-device password under the agreed standard procedure

The following are not automatically one light request:
- bulk user/account changes
- changes spanning many devices/sites
- work requiring investigation before execution
- work requiring a new design/security decision
- repeated retries caused by external/customer-side conditions
- configuration migration or replacement work

For unusual but still lightweight requests, atLIB may agree the request count before execution.

### C. Operation request accounting

Working commercial rule:
- 2 requests are available per contract month
- unused requests **expire at month-end**
- requests do **not carry over**
- predefined scheduled/automated operations do **not** consume request slots
- work required to correct an atLIB execution error does **not** consume an additional slot
- separately quoted work does not consume slots

Reason:
The monthly fee pays for continuous service readiness and automation, not a prepaid bank of labor hours.

### D. Device-count rule

Current standard package baseline:
**up to 50 monitored devices per customer contract.**

For 50+ devices:
- do not automatically promise a fixed per-device increment until actual monitoring/storage/support cost is validated
- quote separately based on device count, monitoring-item volume, site count and management complexity
- keep the 50-device standard easy to understand in customer-facing material

Do not publish an unverified “per 10 devices +JPY X” rule as canonical pricing.

### E. Multi-site rule

A second site is not automatically equivalent to “more devices” because it may require:
- additional Sensor Edge / proxy deployment
- separate network ranges
- separate topology
- separate ISP/vendor context
- separate onsite/remote onboarding coordination
- more incident-isolation complexity

Working rule:
- **one standard contract includes one primary site/environment**
- additional sites are individually assessed during onboarding
- if an additional site only adds a small, technically simple monitored segment, it may be absorbed or priced as an add-on
- if it requires an additional Sensor Edge/proxy or materially separate operational management, charge an additional site/setup fee and, where appropriate, recurring add-on

Exact additional-site price should be set only after infrastructure and support-cost validation.

### F. What counts toward the 50-device limit

Count network/infrastructure endpoints intentionally registered as InfraVision monitored hosts, such as:
- router
- firewall/UTM
- switch
- wireless AP/controller
- server or infrastructure appliance included in the agreed monitoring scope

Do not automatically count:
- employee PCs
- smartphones/tablets
- transient unknown discovery results
- devices detected but not intentionally enrolled as monitored hosts

Printers/IoT/other SNMP devices may be technically detectable; whether they count as contracted monitored devices depends on whether they are intentionally enrolled in the monitoring scope.

### G. Customer-facing commercial notes

Recommended short pricing notes:

> ※ 標準料金は監視対象50台までを想定しています。50台を超える場合や複数拠点・大規模ネットワークは個別にお見積りします。

> ※ オペレーションプランの依頼作業は月2回までです。未使用分の翌月繰越はありません。あらかじめ設定した定期・自動運用は回数に含みません。

> ※ 初期費用には標準的な監視開始設定を含みます。ネットワーク再設計、現地調査、機器交換・構築等は別途となります。

## 13. LP / sales wording

Recommended ladder:
- モニター: 「見える・気づける・自分で管理できる」
- オペレーション: 「日常運用を自動化し、軽微な作業を任せる」
- マネージド: 「ネットワーク管理そのものを任せる」

Monitor should be positioned as a self-service network-management foundation, not cheap alerting.

Operation should emphasize automation rather than recurring manual labor.

Managed should emphasize environmental understanding, environmental facts/history, triage and consultation rather than “unlimited work.”

## 14. Remaining decisions before FINAL

1. Managed fair-use wording / contract threshold after operational validation
2. Validate the working one-request definition against actual delivery cases
3. Validate the no-carry-over rule against sales/customer feedback
4. Confirm company business-day/holiday definition for the working 9:00-18:00 staffed window
5. Validate delivery capacity before setting any numerical first-response target
6. Decide whether paid after-hours staffed response will be offered as a future option
7. Validate infrastructure/support cost before setting 50+ device and additional-site add-on prices
8. Contract/SLA wording for best-effort triage, vendor dependencies and separately quoted work
