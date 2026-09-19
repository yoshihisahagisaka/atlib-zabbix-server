# atLIB InfraVision — Partner Sales Material v1

Status: APPROVED CONTENT CANONICAL — 01–13 narrative/direction approved; final artwork and release-gate verification remain  
Audience: 販売代理店 / 協業パートナー  
Purpose: 代理店担当者がNWの専門家でなくても、対象顧客を見つけ、価値を説明し、案件化できる資料にする。

## Design principle

This material is not a technical product manual.

Primary objective:
**代理店担当者が「誰に・何を・どう売ればよいか」を理解し、翌日から既存顧客へ提案できること。**

Information hierarchy:
1. 顧客課題・営業機会
2. InfraVisionが生む顧客価値
3. 代理店にとっての販売価値
4. 商品・料金・売り分け
5. 技術的な裏付け

Do not require the partner salesperson to understand SNMP/Zabbix/network architecture before they can sell the service.

---

# 01. FV

## Main message
**納品して終わりにしない。  
機器を売った、その先も。  
お客様とつながり続けるビジネスへ。**

### Sub message
ネットワーク機器を販売したあと、その環境を誰が見ていますか？

atLIB InfraVisionは、顧客ネットワークを継続的に見守り、  
異常・機器の老朽化・セキュリティリスクを見える化。  
代理店様の既存商材に、継続的な顧客接点とストック収益を加えます。

### Visual
販売・構築
→ InfraVision
→ 継続監視
→ 月次レポート
→ 相談・改善
→ 次の提案

### Partner takeaway
**「納品後」が、新しい営業機会になる。**

---

# 02. 対象企業

## Heading
**こんなお客様、いませんか？**

- ネットワークは数年前に構築したまま
- Wi-Fiやインターネットが止まると業務に影響する
- 専任の情シス / NW担当者がいない
- 総務や兼任担当者がITも見ている
- 保守契約が切れている / そもそも入っていない
- どんな機器があるか正確には分からない
- 機器が古いか、安全かも把握できていない
- 障害が起きてから販売店や業者へ連絡している

## ICP
**ネットワーク機器はある。  
しかし、それを継続的に管理する人・契約・仕組みがない中小企業。**

### Sales cue
顧客から以下の言葉が出たら提案機会:
- 「ネットワークはよく分からない」
- 「前の業者が作ったまま」
- 「誰が管理しているのか分からない」
- 「Wi-Fiが遅いと言われる」
- 「壊れたら業者に電話している」
- 「ルーターが何年前のものか分からない」

---

# 03. 取りこぼしている市場・課題

## Heading
**機器を売ったあとに、空白期間が生まれていませんか？**

Typical current model:
ルーター・UTM・スイッチ・Wi-Fi等の販売・構築
→ 納品
→ 数年間ほぼ接点なし
→ 障害 / 更改時に再接触

Problems:
- 顧客の状態変化を把握できない
- 更改時期を逃す
- 他社へ相談される
- 営業接点が障害時だけになる
- 売上がスポット中心になる

InfraVision model:
機器販売 / NW構築
→ InfraVision
→ 継続監視
→ 毎月状態を把握
→ レポート / 相談
→ 更改・改善提案

Key message:
**「次の更改まで待つ」のではなく、毎月顧客とつながる。**

---

# 04. 協業モデル

## Heading
**代理店様の商流はそのまま。継続管理の部分をatLIBが支えます。**

Roles:
- Partner: 顧客関係、既存商材、販売、提案
- atLIB: InfraVision導入、監視基盤、運用、レポート、必要に応じたNW支援
- Customer: 自社の必要レベルに応じたプランを利用

Recommended diagram:
顧客
↕ 既存の営業関係
代理店
↕ InfraVision連携
atLIB

Partner message:
**NW運用の専門部隊を自社で新設しなくても、継続サービスを提案できる。**

Commercial/contract details that are partner-program specific remain separate from the product-service canonical until finalized.

---

# 05. 提供サービス

## Heading
**お客様の管理レベルに合わせて、3段階で提案できます。**

### モニター
月額 **9,980円** / 初期 **30,000円**

**まず、見えるようにする。**
- 24時間自動監視
- 異常通知
- ネットワーク構成の可視化
- EoL / 脆弱性自動チェック
- 月次レポート
- 顧客自身で通知・監視抑止設定

Recommended customer:
**自社で対応はできる。でも放置はしたくない。**

### オペレーション
月額 **29,800円** / 初期 **50,000円**

**決まった運用も任せる。**
- モニター全機能
- 定期運用の自動化
- VPNアカウント追加・削除
- Wi-Fi / NW機器パスワード変更
- 軽微なリモート作業 月2回まで

Recommended customer:
**監視だけでなく、日常作業も減らしたい。**

### マネージド
月額 **79,800円** / 初期 **80,000円**

**ネットワーク管理そのものを任せる。**
- オペレーション全機能
- 営業時間内の障害一次切り分け
- 異常の調査 / 対応方針案内
- EoL / 脆弱性の詳細確認
- NW台帳・運用履歴の継続管理
- NW相談窓口
- 通常利用範囲の日常運用

Recommended customer:
**NW担当者がいない。調査・相談・判断まで支援してほしい。**

### Upgrade
- Monitor -> Operation: 20,000円
- Operation -> Managed: 30,000円
- Monitor -> Managed: 50,000円

Existing reusable setup is not charged twice.

---

# 06. 技術の仕組み

## Heading
**専門知識がなくても使える。その裏側は、専門技術で支えています。**

This is the dedicated technical block. Do not spread implementation jargon across sections 01–05.

### Simple architecture
顧客ネットワーク
→ **Sensor Edge**
→ 暗号化されたアウトバウンド通信
→ **atLIB監視基盤**
→ ポータル / 自動通知 / 月次レポート

### What happens automatically
1. NW機器を検出
2. 死活 / SNMP等で状態を監視
3. 構成・機器情報を取得できる範囲で自動収集
4. 異常を検知して通知
5. EoL / 脆弱性リスクを自動チェック
6. 月次レポートへ集約

### Technical detail for partner Q&A
- monitoring foundation uses Zabbix
- Sensor Edge / Zabbix Proxy provides customer-side monitoring connection
- customer portal supports notification destination, severity, notification period and maintenance/suppression settings
- topology uses automatically obtainable information such as LLDP where available and can be supplemented manually
- EoL/CVE output is evidence-gated; unknown or detailed-confirmation-needed is a valid result

### Communication rule
Customer-facing explanation first:
**「小型の監視環境を設置し、外向きの安全な通信でatLIBの監視基盤につなぎます。」**

Technical terms are supporting evidence, not the opening sales pitch.

---

# 07. エンドユーザー価値

## Heading
**見えないリスクを、「見える安心」に。**

InfraVisionは、ネットワークの状態・機器の老朽化・リスクを継続的に見える化。
トラブルへの備えと、計画的なIT運用を支える。

### Value 1
**異常やトラブルに早く気づける**
24時間の自動監視で、異常の兆候を早期に把握しやすくする。

### Value 2
**ネットワークの全体像がひと目で分かる**
構成や機器の状態を見える化し、調査や新規機器検討にも活用できる。

### Value 3
**古い機器・リスクを把握し、計画的な予算化ができる**
EoLや脆弱性情報を継続的に確認。更改時期を事前に把握し、更新計画・予算化につなげる。

Value phrase:
**「突然の更改から、計画的なIT投資へ。」**

### Value 4
**専門のIT担当者がいなくても管理できる**
分かりやすいポータルと月次レポートで状態を把握できる。

### Value 5
**必要に応じて運用・管理まで任せられる**
企業の状態に合わせて段階的にアップグレードできる。

Core phrase:
**構築したままのネットワークを、管理されているネットワークへ。**

---

# 08. パートナーにとっての3つの価値

## 1. ストック収益
スポット販売だけでなく、月額サービスを既存顧客へ追加できる。

Partner monthly revenue baseline (approximately 25%):
- Monitor: **JPY 2,480 / customer / month**
- Operation: **JPY 7,480 / customer / month**
- Managed: **JPY 19,800 / customer / month**

## 2. 継続接点
月次の状態把握により、更改・増設・改善のタイミングを捉えやすくなる。

## 3. 提案力
自社にNW運用専門部隊がなくても、監視・運用・管理まで含めた提案が可能になる。

Key message:
**InfraVisionそのものの売上だけでなく、「次の商談が生まれる状態」を作る。**

---

## Partner portal / customer visibility

External-material position: **include as a standard partner value, provided implementation is completed before release.**

Authorized sales partners can review the status of customers under their responsibility, complementing cases where end customers do not routinely open the portal.

Business value:
- understand customer status without waiting for an inquiry
- identify changes and risks proactively
- use monitoring facts as triggers for follow-up, renewal, replacement and improvement proposals
- turn InfraVision into a continuous existing-customer engagement mechanism

Partner view target:
- customer list / portfolio overview
- normal / attention-needed status
- important alerts and recent changes
- EoL / replacement candidates
- vulnerability / detailed-confirmation-needed items
- newly detected devices / configuration changes where supported
- monthly-report status
- direct navigation to each authorized customer's detail view

Target sales experience:
**「今月、どのお客様に連絡すべきかが分かる。」**

Mandatory release gate:
- implementation and validation complete before external material release
- explicit customer agreement / authorization
- partner-to-customer tenancy and scope mapping
- least-privilege / role-based permissions
- no cross-customer data leakage
- access/audit logging
- revocation when authorization ends

---

# 09. 既存商材 + InfraVision

## Heading
**いま販売している商材に、そのまま組み合わせられます。**

Examples:
- UTM / Firewall + InfraVision
- Switch + InfraVision
- Wi-Fi / AP + InfraVision
- Router / Internet line + InfraVision
- Office relocation / NW construction + InfraVision
- Security proposal + InfraVision

Before:
**機器を販売して終了**

After:
**機器販売 + 継続監視 + レポート + 改善提案**

Sales phrase:
**「この機器、納品後の状態も継続して見えるようにしませんか？」**

---

# 10. Before / After

## Before
- 機器が何台あるか曖昧
- 障害が起きてから気づく
- 古い機器を把握できない
- 問題があるたび販売店へ問い合わせ
- 販売店側も顧客環境を普段は把握できない

## After
- 監視対象と構成が見える
- 異常を自動検知
- EoL / リスクを継続確認
- 月次レポートで状態を把握
- 上位プランなら運用・相談・一次切り分けまで支援
- 代理店も次の改善提案につなげやすい

Headline:
**「何かあったら連絡」から、「何かある前から分かる」へ。**

---

# 11. 支援体制

## Heading
**パートナー様のビジネスを、atLIBが最後まで支えます。**

Important representation rule:
Support categories are **functions/roles**, not a claim that separate dedicated departments currently exist.
Use:
**「少数精鋭のatLIBスタッフが、提案・導入・運用・レポート・継続フォローまで一貫して対応。」**
Do not imply a current organization made up of independent Sales Support / Technical / Operations / Report / Customer Success departments.

Partner does not need to become the monitoring-engineering team.

atLIB support areas:
- 提案時のサービス説明支援
- 技術確認
- 導入設計 / 初期設定
- 監視基盤運用
- 月次レポート
- 上位プランの運用 / 一次切り分け
- 必要に応じた改善・更改検討

Boundary:
- automated monitoring can continue 24h subject to system/connectivity availability
- standard staffed Managed triage is business-hours based
- 24/365 staffed response is not included in the standard service
- VLAN/IP/FW redesign, equipment replacement/addition, new-site construction and onsite work are separately quoted

---

# 12. 販売までの流れ

## Heading
**難しい準備は不要。シンプルな5ステップで始められます。**

1. パートナー登録
2. 提案準備 — 資料・技術情報をatLIBが提供
3. 販売・ご契約 — 必要に応じて提案同行・技術支援
4. 導入・初期設定 — atLIBが監視環境をセットアップ
5. 運用・継続フォロー — 監視・月次レポート・改善/更改フォロー

Partner discovery questions:
- NWを普段見ている担当者はいますか？
- 保守契約はありますか？
- 機器一覧は最新ですか？
- 障害が起きたら誰に連絡しますか？
- 機器の更改時期を把握していますか？

These questions are for discovery, not a technical assessment.

---

# 13. まとめ / 最終CTA

## Heading
**既存顧客への提案から、継続収益と新たなビジネスチャンスを。**

Five-point close:
1. 既存顧客にすぐ提案できる
2. 月額の継続収益になる
3. 販売後も顧客の状態が見える
4. 次の提案機会が生まれる
5. 技術・運用はatLIBが支える

Primary CTA:
**「まずは既存顧客1社から始めてみませんか？」**

Sub:
NWに詳しくなくても構いません。  
顧客の状況をatLIBと一緒に整理し、提案方法から支援します。

CTA:
**代理店・協業について相談する**

Secondary message:
**既存顧客への継続提案を、atLIBと一緒に。**

---

# Visual / editorial rules

- 16:9 horizontal, flyer-like, readable without presenter narration
- bright base; Deep Navy as structure/accent rather than full dark background
- diagrams over dense prose
- one primary message per section/page
- explain customer/business value before technical detail
- section 06 is the dedicated technical block
- use Japanese business language; avoid unexplained acronyms in primary copy
- plan colors may differentiate Monitor / Operation / Managed, but pricing hierarchy must remain visually clear
- partner-facing copy should answer: 誰に売る / 何が嬉しい / どう売る / どう支援される
- technical appendix can later expand Zabbix/SNMP/security architecture if required

# Open items before external release

- finalize contractual/accounting treatment of the approved approximately-25% partner revenue baseline (Monitor JPY 2,480 / Operation JPY 7,480 / Managed JPY 19,800 per customer/month)
- exact partner support and escalation contact process
- exact business-day definition for Managed staffed response
- validation of 50+ device and additional-site pricing
- legal/contract wording for fair use and upgrade eligibility
- partner portal must be implemented and validated before this material is externally released
- real-device E2E technical validation remains deferred; do not overclaim unsupported device identification/EoL/CVE certainty
