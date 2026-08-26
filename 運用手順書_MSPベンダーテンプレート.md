# 運用手順書: MSPベンダー識別テンプレート（インベントリ自動反映）

最終更新: 2026-08-26

## これは何か

`zabbixserver/batch/setup_discovery.py`の`VENDOR_TEMPLATE_RULES`は、顧客オンボーディング時に`sysObjectID`/`sysDescr`の内容でベンダーを自動判定し、対応するテンプレートを条件付きでリンクするDiscovery Actionを自動生成する仕組みを持つ（コード側コメント参照）。ただしテンプレート自体はZabbix管理画面（API）側で事前に作成しておく必要があり、2026-08-26時点で以下3つを作成・実機（atLIB社内4台）で検証済み。

| テンプレート名 | templateid | ベンダー判定 | 検証状況 |
|---|---|---|---|
| `MSP - NETGEAR Device Identification` | 10807 | sysObjectID `1.3.6.1.4.1.4526` | vendorのみ自動反映確認済み。model/software_fullは未対応（下記「既知の課題」参照） |
| `MSP - Brother Device Identification` | 10806 | sysObjectID `1.3.6.1.4.1.2435` | vendor/model/software_full全て自動反映確認済み |
| `MSP - Ubiquiti UniFi Device Identification` | 10805 | sysDescr `Ubiquiti UniFi` | vendor/model/software_full全て自動反映確認済み |

いずれも「Templates/Network devices」テンプレートグループ（groupid=9、既存の`Network Generic Device by SNMP`と同じ）に所属。

## 設計パターン

各テンプレートは、SNMP経由で取得した生の文字列（`sysDescr`や`hrDeviceDescr`等）を、Zabbixの**依存アイテム(dependent item)**＋**プリプロセッシング**（正規表現/JavaScript）で加工し、ホストインベントリの`vendor`（inventory_link=31）・`model`（29）・`software_full`（17）へ自動反映する。ベンダーはテンプレート自体が既にベンダー確定済みの文脈でリンクされるため、JavaScriptプリプロセッシング`return 'ベンダー名';`で固定文字列を出力する。

**重要な制約（実装時に判明）**:
- Zabbixの依存アイテムの`master_itemid`は**同一テンプレート内のアイテムでなければならない**（他テンプレートのアイテムをmasterに指定するとAPIエラーになる）。そのため各ベンダーテンプレートは、ベーステンプレート（`Network Generic Device by SNMP`）の既存アイテムを流用せず、**同じOIDを取得する独立したSNMPアイテム**（キー名を`msp.sysdescr.raw`等、ベーステンプレートと重複しないものにする）を自テンプレート内に持つ。これはホストへの複数テンプレートリンク時、同じキーのアイテムが2つの独立テンプレートに存在すると衝突する（`setup_discovery.py`はベンダーテンプレートをベーステンプレートの「兄弟」として直接リンクする設計のため）ことへの対応でもある。sysDescr等はほぼ不変な値のため、1時間間隔の再ポーリングによる実害はない。
- 依存アイテムのmaster側アイテムを削除すると、それに依存する子アイテムも連動して削除される（カスケード削除）。既存アイテムのOID修正時は`item.update`ではなく削除→再作成の方が確実（`item.update`では次回ポーリング時刻がリセットされず、変更が反映されるまで最大で元のポーリング間隔分待つことになる）。
- Zabbix APIの`item.inventory_link`数値ID: `vendor`=31、`model`=29、`software_full`=17（公式ドキュメント「Host inventory」テーブルで確認。`contact`=23・`location`=24・`name`=3は既存アイテムの実値と突き合わせ済み）。
- プリプロセッシングのtype数値: 5=正規表現（params: `パターン\n出力テンプレート`、`\1`等でキャプチャグループ参照）、21=JavaScript（params: JSコード文字列）。

## 各テンプレートのアイテム定義

### MSP - Ubiquiti UniFi Device Identification
実機`sysDescr`例: `"Ubiquiti UniFi UCG-Ultra 5.1.31 Linux 5.4.213 ipq5322"`

| キー | 種別 | 内容 |
|---|---|---|
| `msp.sysdescr.raw` | SNMP GET | OID `get[1.3.6.1.2.1.1.1.0]` |
| `msp.vendor` | 依存(master=上記) | JS: `return 'Ubiquiti';` → inventory_link=31 |
| `msp.model` | 依存(master=上記) | 正規表現: `Ubiquiti UniFi (\S+) [\d.]+ Linux` → inventory_link=29 |
| `msp.software_full` | 依存(master=上記) | 正規表現: `Ubiquiti UniFi \S+ ([\d.]+) Linux` → inventory_link=17 |

### MSP - Brother Device Identification
実機`sysDescr`例: `"Brother NC-9200w, Firmware Ver.1.35  ,MID 8CE-963FID 2"`（ネットワークカード自体の型番のみでプリンタ製品名を含まない）。実機`hrDeviceDescr`（標準Printer-MIB、OID `1.3.6.1.2.1.25.3.2.1.3.1`）例: `"Brother MFC-L3780CDW series"`（`eol_overrides.json`の"Brother MFC-L3780CDW"キーと一致する製品名）。**modelは`sysDescr`ではなく`hrDeviceDescr`から取得すること。**

| キー | 種別 | 内容 |
|---|---|---|
| `msp.hrdevicedescr.raw` | SNMP GET | OID `get[1.3.6.1.2.1.25.3.2.1.3.1]` |
| `msp.sysdescr.raw` | SNMP GET | OID `get[1.3.6.1.2.1.1.1.0]` |
| `msp.vendor` | 依存(master=sysdescr.raw) | JS: `return 'Brother';` → inventory_link=31 |
| `msp.model` | 依存(master=hrdevicedescr.raw) | 正規表現: `Brother (.+?)(?: series)?$` → inventory_link=29 |
| `msp.software_full` | 依存(master=sysdescr.raw) | 正規表現: `Firmware Ver\.([\d.]+)` → inventory_link=17 |

### MSP - NETGEAR Device Identification
実機`sysDescr`例: `"Linux atLIB-ap01 4.4.60 #1 SMP PREEMPT Sat Mar 28 13:24:22 UTC 2026 armv7l"`（汎用Linuxカーネル情報のみで、ベンダー・機種情報を一切含まない）。

| キー | 種別 | 内容 |
|---|---|---|
| `msp.sysdescr.raw` | SNMP GET | OID `get[1.3.6.1.2.1.1.1.0]`（vendor固定値の依存元トリガーとしてのみ使用） |
| `msp.vendor` | 依存(master=上記) | JS: `return 'NETGEAR';` → inventory_link=31 |

**既知の課題**: model/software_fullを自動取得するSNMP OIDが未特定。ENTITY-MIB（`entPhysicalModelName` OID `1.3.6.1.2.1.47.1.1.1.1.13.1`、`entPhysicalSoftwareRev` OID `1.3.6.1.2.1.47.1.1.1.1.10.1`）を試したが、実機（NETGEAR WAX625、`atLIB-ap01`/`ap02`）では両方とも`"No Such Object available on this agent at this OID"`エラーとなり非対応と判明、アイテムは削除済み。現状は`host.inventory.model`を手動入力するか（`eol_overrides.json`の"NETGEAR WAX625"キーと一致させる必要がある）、NETGEAR製品の別OID（プライベートMIB等）を別途調査する必要がある。次にNETGEAR製品を追加する際は、この課題を先に解決するか、vendor固定のみで運用し手動でmodelを補完する運用を継続すること。

## 新しいベンダーへの対応手順（将来）

1. 対象機器のZabbixホストで、実機の`system.descr[sysDescr.0]`・`system.objectid[sysObjectID.0]`の値を確認する（`item.get`）。ベンダー固有の標準MIB（Printer-MIB `hrDeviceDescr`、ENTITY-MIB `entPhysicalModelName`等）が使えないか確認する。
2. `sysObjectID`のenterprise number（`.1.3.6.1.4.1.<番号>`部分）でベンダーが一意に確定できるか確認する（できない場合はUbiquitiと同様`sysDescr`の文字列一致で判定する）。
3. 上記「設計パターン」に沿って新規テンプレート`MSP - <ベンダー名> Device Identification`をAPI（`template.create`→`item.create`）で作成する。作成用スクリプトの実例は本手順書のGit履歴（2026-08-26のコミット）に一時的に使ったコードを参照（リポジトリには恒久保存していない。`zabbix_client.py`の`call()`汎用ラッパーで同様に組める）。
4. `setup_discovery.py`の`VENDOR_TEMPLATE_RULES`に1エントリ追加する。
5. 実機（または新規顧客の実際の機器）へテンプレートをリンクし、`host.get`でインベントリが正しく反映されることを確認する。

## 検証コマンド例

```python
# host.getでインベントリと該当アイテムの値を確認
z._req("host.get", {
    "hostids": "<hostid>",
    "output": ["host"],
    "selectInventory": ["vendor", "model", "software_full"],
    "selectItems": ["key_", "lastvalue", "state", "error"],
})
```

`setup_discovery.py`（`--dry-run`）を実行すると「ベンダー横断デバイス識別」セクションで各テンプレートの`templateid`が表示され、「テンプレート未作成」警告が出なくなっていることを確認できる。
