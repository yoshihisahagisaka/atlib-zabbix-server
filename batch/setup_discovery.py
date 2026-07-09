"""MSP標準ディスカバリルール・アクション セットアップスクリプト

顧客ごとにProxy・IPレンジでスコープされたディスカバリルール（プリンター・サーバー・
ネットワーク機器を検出する標準チェックリスト）と、それに対応する2つのディスカバリ
アクション（SNMP応答機器登録／ICMPフォールバック登録）を、同じテンプレートから複製生成する。

背景: 本番Zabbixに「テストルール」「テストアクション」〜「テストアクション3」等、
場当たり的に作られた複数のディスカバリルール・アクションが混在し、どれが正しいか
判別できなくなっていた。これを解消するため、実際に動作実績のある「テストルール」
（druleid=7）の内容を土台に、汎用的に複製できる形へ正式化する。

SNMPチェックに必要なコミュニティ文字列は、既存の「テストルール」から実行時に取得して
そのまま流用する（値は一切表示・ログ出力しない）。

使い方:
  # 1. まず必ずdry-runで現状を確認する（書き込みは一切行わない）
  python setup_discovery.py --dry-run --company-name "atLIB株式会社様"

  # 2. 内容を確認したうえで実際に作成する
  python setup_discovery.py --apply \
    --customer-code atlib --company-name "atLIB株式会社様" \
    --ip-range 192.168.0.1-254 [--proxy-id <zabbix_proxy_id>]

接続情報（環境変数、どちらか一方）:
  ZABBIX_URL + ZABBIX_TOKEN
  ZABBIX_URL + ZABBIX_USER + ZABBIX_PASSWORD
"""
import argparse
import os
import sys

from zabbix_client import ZabbixClient

TEMPLATE_ID_SNMP = "10226"   # Network Generic Device by SNMP
TEMPLATE_ID_ICMP = "10564"   # ICMP Ping
SOURCE_RULE_NAME = "テストルール"  # snmp_communityとdcheck構造の複製元（動作実績あり）

# 標準チェックリスト（type, ports, 用途）。SNMPチェックのkey_・snmp_communityは
# SOURCE_RULE_NAMEから複製するため、ここではTCP/ICMPチェックのみ定義する。
STANDARD_TCP_CHECKS = [
    (9100, "プリンター (RAW/JetDirect)"),
    (515,  "プリンター (LPR)"),
    (631,  "プリンター (IPP)"),
    (22,   "Linuxサーバー/SSH管理機器"),
    (445,  "Windowsサーバー (SMB)"),
    (3389, "Windowsサーバー (RDP)"),
    (3493, "UPS (NUT)"),
    (10050, "Zabbixエージェント導入済み機器"),
    (443,  "汎用Web管理機器フォールバック"),
]


def main():
    args = _parse_args()
    zabbix = _connect()

    print(f"Zabbix APIバージョン: {zabbix.call('apiinfo.version', {})}\n")

    group = _find_hostgroup(zabbix, args.company_name)
    if not group:
        print(f"[エラー] ホストグループ「MSP/{args.company_name}」が見つかりません。")
        print("先にオンボーディングスクリプト（npm run onboard）でホストグループを作成してください。")
        sys.exit(1)
    print(f"ホストグループ「MSP/{args.company_name}」: groupid={group['groupid']}")

    source_rule = _find_source_rule(zabbix)
    if not source_rule:
        print(f"[エラー] 複製元ルール「{SOURCE_RULE_NAME}」が見つかりません。")
        sys.exit(1)
    snmp_dchecks = [dc for dc in source_rule["dchecks"] if dc["type"] == "11"]
    print(f"複製元ルール「{SOURCE_RULE_NAME}」: druleid={source_rule['druleid']}  SNMPチェック{len(snmp_dchecks)}件を複製")

    rule_name = f"MSP_インフラ自動検知_{args.customer_code}"
    snmp_action_name = f"MSP_SNMP機器登録_{args.customer_code}"
    icmp_action_name = f"MSP_ICMPフォールバック登録_{args.customer_code}"

    existing_rule = _find_rule_by_name(zabbix, rule_name)
    print(f"\nディスカバリルール「{rule_name}」: {'既に存在します（druleid=' + existing_rule['druleid'] + '）' if existing_rule else '未作成'}")
    existing_snmp_action = _find_action_by_name(zabbix, snmp_action_name)
    print(f"アクション「{snmp_action_name}」: {'既に存在します' if existing_snmp_action else '未作成'}")
    existing_icmp_action = _find_action_by_name(zabbix, icmp_action_name)
    print(f"アクション「{icmp_action_name}」: {'既に存在します' if existing_icmp_action else '未作成'}")

    print("\n作成予定のTCP/ICMPチェック:")
    print("  - ICMP ping（基本疎通）")
    for port, desc in STANDARD_TCP_CHECKS:
        print(f"  - TCP {port}（{desc}）")

    if not args.apply:
        print("\n[dry-run] 書き込みは行っていません。内容を確認のうえ --apply で実行してください。")
        return

    if not args.customer_code or not args.ip_range:
        print("\n[エラー] --apply には --customer-code と --ip-range が必須です。")
        sys.exit(1)

    print("\n=== 構成投入を開始します ===")

    if existing_rule:
        druleid = existing_rule["druleid"]
        print(f"  [スキップ] ルール「{rule_name}」は既に存在します（druleid={druleid}）")
    else:
        druleid = _create_discovery_rule(zabbix, rule_name, args.ip_range, args.proxy_id, snmp_dchecks)
        print(f"  [作成] ルール「{rule_name}」を作成しました（druleid={druleid}）")

    if existing_snmp_action:
        print(f"  [スキップ] アクション「{snmp_action_name}」は既に存在します")
    else:
        _create_snmp_action(zabbix, snmp_action_name, druleid, group["groupid"])
        print(f"  [作成] アクション「{snmp_action_name}」を作成しました")

    if existing_icmp_action:
        print(f"  [スキップ] アクション「{icmp_action_name}」は既に存在します")
    else:
        _create_icmp_fallback_action(zabbix, icmp_action_name, druleid, group["groupid"])
        print(f"  [作成] アクション「{icmp_action_name}」を作成しました")

    print("\n完了。Zabbix管理画面でルール・アクションの内容を確認してください。")
    print("既知の機器に対して実際に正しく検出・分類されることを確認したのち、")
    print("旧テスト用ルール・アクションの削除を検討してください（本スクリプトでは削除しません）。")
    print("\n[既知の制約] ICMPにのみ応答しSNMP/TCP各ポートいずれにも応答しない機器は、")
    print("今回のフォールバックアクションの対象外です（将来の拡張課題）。")


# ------------------------------------------------------------------
# 接続
# ------------------------------------------------------------------

def _connect() -> ZabbixClient:
    url = os.environ.get("ZABBIX_URL")
    token = os.environ.get("ZABBIX_TOKEN")
    user = os.environ.get("ZABBIX_USER")
    password = os.environ.get("ZABBIX_PASSWORD")

    if not url:
        print("[エラー] 環境変数 ZABBIX_URL が未設定です。")
        sys.exit(1)
    if not token and not (user and password):
        print("[エラー] 環境変数 ZABBIX_TOKEN、または ZABBIX_USER + ZABBIX_PASSWORD を設定してください。")
        sys.exit(1)

    return ZabbixClient(url, user=user, password=password, token=token)


# ------------------------------------------------------------------
# 現状確認（読み取りのみ）
# ------------------------------------------------------------------

def _find_hostgroup(zabbix: ZabbixClient, company_name: str) -> dict | None:
    groups = zabbix.call("hostgroup.get", {
        "output": ["groupid", "name"],
        "filter": {"name": f"MSP/{company_name}"},
    })
    return groups[0] if groups else None


def _find_source_rule(zabbix: ZabbixClient) -> dict | None:
    rules = zabbix.call("drule.get", {
        "output": ["druleid", "name"],
        "filter": {"name": SOURCE_RULE_NAME},
        "selectDChecks": "extend",
    })
    return rules[0] if rules else None


def _find_rule_by_name(zabbix: ZabbixClient, name: str) -> dict | None:
    rules = zabbix.call("drule.get", {"output": ["druleid"], "filter": {"name": name}})
    return rules[0] if rules else None


def _find_action_by_name(zabbix: ZabbixClient, name: str) -> dict | None:
    actions = zabbix.call("action.get", {"output": ["actionid"], "filter": {"name": name}})
    return actions[0] if actions else None


# ------------------------------------------------------------------
# 作成
# ------------------------------------------------------------------

def _create_discovery_rule(zabbix: ZabbixClient, name: str, ip_range: str, proxy_id: str | None, snmp_dchecks: list[dict]) -> str:
    dchecks = [{"type": "12", "ports": "0"}]  # ICMP ping
    for dc in snmp_dchecks:
        # snmp_communityを含む既存チェックをそのまま複製する（値は表示しない）
        entry = {k: v for k, v in dc.items() if k not in ("dcheckid", "druleid")}
        dchecks.append(entry)
    for port, _desc in STANDARD_TCP_CHECKS:
        dchecks.append({"type": "8", "ports": str(port)})

    params = {
        "name": name,
        "iprange": ip_range,
        "delay": "5m",
        "dchecks": dchecks,
    }
    if proxy_id:
        params["proxy_hostid"] = proxy_id

    result = zabbix.call("drule.create", params)
    return result["druleids"][0]


def _create_snmp_action(zabbix: ZabbixClient, name: str, druleid: str, groupid: str) -> None:
    zabbix.call("action.create", {
        "name": name,
        "eventsource": 1,  # ディスカバリイベント
        "status": 0,
        "filter": {
            "evaltype": 0,  # AND/OR（型が異なる条件は自動的にAND）
            "conditions": [
                {"conditiontype": 18, "operator": 0, "value": druleid},   # ディスカバリルール
                {"conditiontype": 10, "operator": 0, "value": "0"},      # デバイスステータス=Up
                {"conditiontype": 8,  "operator": 0, "value": "11"},     # サービスタイプ=SNMPv2
            ],
        },
        "operations": [
            {"operationtype": 2},  # ホスト追加
            {"operationtype": 4, "opgroup": [{"groupid": groupid}]},
            {"operationtype": 6, "optemplate": [{"templateid": TEMPLATE_ID_SNMP}]},
        ],
    })


def _create_icmp_fallback_action(zabbix: ZabbixClient, name: str, druleid: str, groupid: str) -> None:
    # SNMPが応答しない(down)、かつTCPチェックのいずれかのポートが応答した場合のみ発火する。
    # SNMP応答機器と重複してテンプレートが付与される（=同一ホストに10226と10564が両方付き、
    # ICMPアイテムのキー衝突を起こす）ことを避けるための排他条件。
    conditions = [
        {"conditiontype": 18, "operator": 0, "value": druleid,  "formulaid": "A"},  # ディスカバリルール
        {"conditiontype": 8,  "operator": 0, "value": "11",     "formulaid": "B"},  # サービスタイプ=SNMPv2
        {"conditiontype": 10, "operator": 0, "value": "1",      "formulaid": "C"},  # デバイスステータス=Down
        {"conditiontype": 8,  "operator": 0, "value": "8",      "formulaid": "D"},  # サービスタイプ=TCP
    ]
    port_letters = []
    letters = "EFGHIJKLMNOPQRSTUVWXYZ"
    for i, (port, _desc) in enumerate(STANDARD_TCP_CHECKS):
        letter = letters[i]
        conditions.append({"conditiontype": 9, "operator": 0, "value": str(port), "formulaid": letter})
        port_letters.append(letter)

    formula = "A and B and C and D and (" + " or ".join(port_letters) + ")"

    zabbix.call("action.create", {
        "name": name,
        "eventsource": 1,
        "status": 0,
        "filter": {
            "evaltype": 3,  # カスタム式
            "formula": formula,
            "conditions": conditions,
        },
        "operations": [
            {"operationtype": 2},
            {"operationtype": 4, "opgroup": [{"groupid": groupid}]},
            {"operationtype": 6, "optemplate": [{"templateid": TEMPLATE_ID_ICMP}]},
        ],
    })


def _parse_args():
    p = argparse.ArgumentParser(description="MSP標準ディスカバリルール・アクションセットアップ")
    p.add_argument("--apply", action="store_true", help="実際に作成する（指定しなければdry-run）")
    p.add_argument("--dry-run", action="store_true", help="現状確認のみ（デフォルト動作、明示指定も可）")
    p.add_argument("--customer-code", default="", help="顧客コード（ルール・アクション名のサフィックスに使用）")
    p.add_argument("--company-name", required=True, help="ホストグループ解決用の会社名（MSP/{company-name}）")
    p.add_argument("--ip-range", default="", help="スキャン対象のIPレンジ（例: 192.168.0.1-254）")
    p.add_argument("--proxy-id", default=None, help="スコープするZabbix Proxy ID（省略時はZabbix Server直下）")
    return p.parse_args()


if __name__ == "__main__":
    main()
