# InfraVision Asset Identification Engine v1

Status: Draft / implementation baseline  
Date: 2026-09-19

## 1. Purpose

InfraVisionのEoL・脆弱性判定に必要な Vendor / Model / Firmware を、顧客オンボーディングから可能な限り自動収集・正規化する共通基盤を定義する。

価格プランとは分離する。Asset Identification / Lifecycle / Vulnerability / Remediation を独立Capabilityとして実装し、将来プランごとに公開範囲を変更できることを前提とする。

## 2. Existing assets

現行実装には以下が存在する。

- `setup_discovery.py`: 顧客単位Discovery、Generic SNMP templateリンク、Vendor識別Action。
- Generic base: `Network Generic Device by SNMP` (templateid=10226)。
- Discovery evidence: sysObjectID / sysDescr。
- Vendor templates: Ubiquiti UniFi / Brother / NETGEAR。
- Zabbix Host Inventory: vendor / model / software_full。
- `main.py`: Inventoryを入力にCPE、NVD/CISA KEV、EoL判定を実行。
- `cpe_mapper.py`, `nvd_client.py`, `eol_client.py`: Intelligence pipeline。

従って新規に別システムを作るのではなく、既存パイプラインを一般化・品質向上する。

## 3. Target flow

```text
Customer Onboarding
  -> Host Group / Proxy
  -> Network Discovery
  -> Generic SNMP
  -> Raw Evidence (sysObjectID, sysDescr, standard MIB)
  -> Vendor Identification
  -> Best Template Selection
       -> Zabbix official vendor template where suitable
       -> atLIB vendor identification template otherwise
  -> Canonical Asset Inventory
       vendor
       model
       firmware
       serial (when available)
  -> Identity Quality
  -> Lifecycle Intelligence
  -> Vulnerability Intelligence
  -> Report / Alert / Remediation
```

## 4. Layering rule

### L1 Standard
全SNMP機器にGeneric SNMPを適用する。sysObjectID / sysDescr等を共通Evidenceとして保持する。

### L2 Official Vendor Template
Zabbix公式Vendor Templateが対象製品に適合し、必要なInventory情報を安定取得できる場合は優先する。ただし「公式テンプレートが存在する」ことだけで自動採用せず、取得項目と対象製品範囲を検証する。

### L3 atLIB Vendor Adapter
L1/L2でVendor/Model/Firmwareが揃わない場合のみ追加する。可能な限りSNMP標準MIB、次にPrivate MIBを使用する。SSH/API等はSNMPで不足する場合の拡張手段とする。

Vendor Adapterは顧客固有コードにせず、メーカー/製品ファミリ単位の再利用可能資産として実装する。

## 5. Canonical asset fields

最低限:
- vendor
- model
- firmware

推奨:
- serial
- sysObjectID
- sysDescr
- source_template
- evidence_source
- last_identified_at

Raw EvidenceとCanonical値は分離する。正規化後の値だけを保存して元情報を失わない。

## 6. Identity quality

各ホストについて以下を独立評価する。

- vendor_status: confirmed / probable / unknown
- model_status: confirmed / probable / unknown
- firmware_status: confirmed / probable / unknown

単一の総合confidenceだけに集約しない。EoLはModel、CVE applicabilityはModel+Firmwareへの依存が強いため、不足項目を明示できる必要がある。

初期ルール:
- confirmed: 一意なenterprise sysObjectID、機種固有OID、公式/検証済みtemplate extraction等。
- probable: sysDescr文字列等から高確度で推定できるが一意性を保証できない。
- unknown: 必要Evidence不足、取得失敗、矛盾。

## 7. Intelligence safety rules

### Lifecycle
- confirmed: メーカー一次情報または人間が一次情報確認済みoverride。
- probable/fuzzy: 補助DBや曖昧一致。
- unknown: 判定材料不足。

probableを顧客向けに「EoL確定」と表示しない。

### Vulnerability
CVEの存在と「当該実機が影響を受ける」を分離する。

- Product matchのみ: candidate。
- Product + affected version range match: affected。
- Version不明: potentially affected / unknown。
- NVD/API検索失敗: unknown。0件として扱わない。
- CISA KEV: exploitation priority enrichmentであり、CVEの主ソースにはしない。

Keyword fallbackの結果をconfirmed affectedとして扱わない。

## 8. Capability separation

内部Capability:
- asset_inventory
- lifecycle_intelligence
- vulnerability_intelligence
- remediation_guidance
- managed_remediation

料金プランはこのCapabilityの公開設定として扱い、収集・判定エンジンに価格条件を埋め込まない。

これにより将来、
- Base: monitoring + asset inventory
- Upper: lifecycle/vulnerability intelligence
- Managed: remediation
等へ変更しても基盤を作り直さない。

## 9. Vendor expansion policy

優先順位:
1. Generic SNMPで完結する機器
2. Zabbix公式Vendor Templateで完結する機器
3. atLIB Vendor Adapter追加で完結する主要SMB機器
4. SNMP以外の補助取得が必要な機器
5. 自動判定困難 -> unknown + 手動/非対応判断

初期検証対象:
- YAMAHA
- Cisco
- Fortinet
- Aruba/HPE
- NETGEAR
- Ubiquiti
- Brother

新Vendor対応時に記録するもの:
- enterprise OID
- 実機sysObjectID/sysDescr
- Model取得OID/方法
- Firmware取得OID/方法
- Serial取得OID/方法
- 対応Template
- 検証機種
- EoL source
- CVE/CPE mapping notes

## 10. Measurement for service/pricing decision

技術完成後、価格判断のため最低限以下を計測する。

- asset identification automatic coverage
- vendor/model/firmware confirmed率
- unknown率
- false-positive / false-match件数
- Vendor Adapter新規追加工数
- 顧客1社あたり月次human review時間
- 外部API/データ費用
- report生成・運用工数
- remediation問い合わせ/対応工数

9,800円プランでEoL/CVEを提供するかは、この計測後に決定する。技術仕様上はBase/Upperを固定しない。

## 11. Implementation phases

### Phase A — Baseline audit
既存Generic SNMPとVendor templatesについて、実機Inventory取得結果を一覧化する。

### Phase B — Template resolver
sysObjectID/sysDescrをEvidenceとして、最適Templateを選択するルールを共通化する。既存Discovery Action方式を活かしつつ、ルール定義をデータ駆動化する。

### Phase C — Identity quality
Host Inventory取得時にvendor/model/firmwareのstatusとEvidenceを保持できるようにする。

### Phase D — Intelligence hardening
CPE/CVEでFirmware version applicabilityを判定し、keyword fallbackをcandidate扱いへ変更する。EoLもconfirmed/fuzzy/unknownを顧客表示まで一貫させる。

### Phase E — Vendor coverage
YAMAHAを含む初期対象メーカーを順次検証し、不足分だけVendor Adapterを追加する。

### Phase F — Commercial review
実測値を基にBase/Upper/Managedの提供範囲・価格を決定する。

## 12. Acceptance criteria for v1

- 新規顧客オンボーディングでGeneric SNMPが自動リンクされる既存動作を維持。
- Vendor判定後の追加Template選択を顧客個別作業なしで実行できる。
- vendor/model/firmwareについて判定可否を明示できる。
- 未判定を安全/脆弱性なし/EoLなしとして扱わない。
- Vendor追加が共通資産として再利用できる。
- Capabilityと料金プランが疎結合。
- 商用プラン判断に必要なcoverage/工数を測定できる。
