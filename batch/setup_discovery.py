"""MSP標準ディスカバリルール・アクション セットアップスクリプト

顧客ごとにProxy・IPレンジでスコープされたディスカバリルール（プリンター・サーバー・
ネットワーク機器を検出する標準チェックリスト）と、それに対応する3つのディスカバリ
アクション（SNMP応答機器登録／ICMPフォールバック登録／新規機器検知通知）を、同じ
テンプレートから複製生成する。

新規機器検知通知アクションは検出ステータス「Discovered」（今回のスキャンで初めて
検出された場合のみ1回発火、想定値=2）を使う。他の2アクションが使う「Up」（毎サイク
ル再評価、想定値=0）とは異なる値のため、取り違えると既知の機器に対して毎サイクル
誤通知が飛ぶ事故になりうる。安全策として、このアクションは作成時 status=1（無効）
にしておき、Zabbix管理画面で条件（特にDiscoveredの表示）を目視確認したうえで、
人間が手動で有効化することを前提とする。

顧客（notify_{customer_code}）への配信有無は、本スクリプトではなく顧客ポータルの
通知設定トグル（msp-customer-portal側、zabbixClient.tsのsetUnknownDeviceAlertEnabled）
が専任で管理する。本スクリプトは常に社内ユーザー（--notify-user、デフォルトatladmin）
のみを送信先として作成する。

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
    --ip-range 192.168.0.1-254 [--proxy-id <zabbix_proxy_id>] [--notify-user atladmin]

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
SOURCE_RULE_NAME = "テストルール"  # snmp_communityとdcheck構造の複製元（動作実績あり）。
# 新規ルール作成時のみ参照する。既存ルールの再利用時は参照しないため、このルール
# 自体が削除済みでも既存顧客に対する再実行（--applyの冪等性チェック等）は影響を受けない。

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

    rule_name = f"MSP_インフラ自動検知_{args.customer_code}"
    snmp_action_name = f"MSP_SNMP機器登録_{args.customer_code}"
    icmp_action_name = f"MSP_ICMPフォールバック登録_{args.customer_code}"
    new_device_action_name = f"MSP_新規機器検知通知_{args.customer_code}"

    existing_rule = _find_rule_by_name(zabbix, rule_name)
    print(f"\nディスカバリルール「{rule_name}」: {'既に存在します（druleid=' + existing_rule['druleid'] + '）' if existing_rule else '未作成'}")

    # 複製元ルールの参照は、新規にルールを作成する場合（＝SNMPチェックを複製する必要が
    # ある場合）のみ必要。既に対象ルールが存在する場合は参照不要（テストルールは
    # クリーンアップで削除済みのため、無条件に参照するとエラーになる）。
    snmp_dchecks: list[dict] = []
    if not existing_rule:
        source_rule = _find_source_rule(zabbix)
        if not source_rule:
            print(f"[エラー] 複製元ルール「{SOURCE_RULE_NAME}」が見つかりません。")
            sys.exit(1)
        snmp_dchecks = [dc for dc in source_rule["dchecks"] if dc["type"] == "11"]
        print(f"複製元ルール「{SOURCE_RULE_NAME}」: druleid={source_rule['druleid']}  SNMPチェック{len(snmp_dchecks)}件を複製")
    existing_snmp_action = _find_action_by_name(zabbix, snmp_action_name)
    print(f"アクション「{snmp_action_name}」: {'既に存在します' if existing_snmp_action else '未作成'}")
    existing_icmp_action = _find_action_by_name(zabbix, icmp_action_name)
    print(f"アクション「{icmp_action_name}」: {'既に存在します' if existing_icmp_action else '未作成'}")
    existing_new_device_action = _find_action_by_name(zabbix, new_device_action_name)
    print(f"アクション「{new_device_action_name}」: {'既に存在します' if existing_new_device_action else '未作成'}")

    notify_user = _find_user(zabbix, args.notify_user)
    if notify_user:
        print(f"通知先ユーザー「{args.notify_user}」: userid={notify_user['userid']}")
    else:
        print(f"通知先ユーザー「{args.notify_user}」: [警告] 見つかりません。新規機器検知通知アクションは作成できません。")

    customer_notify_username = f"notify_{args.customer_code}"
    customer_notify_user = _find_user(zabbix, customer_notify_username) if args.customer_code else None
    if customer_notify_user:
        print(f"顧客通知ユーザー「{customer_notify_username}」: userid={customer_notify_user['userid']}（送信先への追加は顧客ポータルの通知設定トグルで管理されます。本スクリプトでは操作しません）")
    else:
        print(f"顧客通知ユーザー「{customer_notify_username}」: 見つかりません（オンボーディング未実施、または顧客コード未指定）")

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

    # 顧客(notify_{code})の送信先追加/除外は顧客ポータルの通知設定トグルが専任で管理する
    # （zabbixClient.ts の setUnknownDeviceAlertEnabled）。本スクリプトが同時に書き込むと
    # 競合するため、ここでは内部ユーザー（--notify-user）のみを対象にする。
    notify_userids = [u["userid"] for u in (notify_user,) if u]

    if existing_new_device_action:
        print(f"  [スキップ] アクション「{new_device_action_name}」は既に存在します")
    elif not notify_userids:
        print(f"  [スキップ] アクション「{new_device_action_name}」は通知先ユーザーが見つからないため作成しませんでした")
    else:
        _create_new_device_action(zabbix, new_device_action_name, druleid, notify_userids)
        print(f"  [作成] アクション「{new_device_action_name}」を作成しました（無効状態、社内送信先のみ: {len(notify_userids)}名）")

    print("\n完了。Zabbix管理画面でルール・アクションの内容を確認してください。")
    print("既知の機器に対して実際に正しく検出・分類されることを確認したのち、")
    print("旧テスト用ルール・アクションの削除を検討してください（本スクリプトでは削除しません）。")
    print("\n[既知の制約] ICMPにのみ応答しSNMP/TCP各ポートいずれにも応答しない機器は、")
    print("今回のフォールバックアクションの対象外です（将来の拡張課題）。")
    print("\n[重要] 新規機器検知通知アクションは安全のため無効状態で作成されています。")
    print("Zabbix管理画面で条件（検出ステータス=Discovered）を確認したうえで、")
    print("手動で有効化してください。誤って毎スキャンサイクル通知が飛ばないか、")
    print("有効化後は数サイクル分様子を見ることを推奨します。")


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


def _find_user(zabbix: ZabbixClient, username: str) -> dict | None:
    users = zabbix.call("user.get", {"output": ["userid", "username"], "filter": {"username": username}})
    return users[0] if users else None


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
        # Zabbix 7.0でdruleオブジェクトのproxy_hostidはproxyidに変更された（公式APIリファレンスで確認済み）。
        # 旧フィールド名のままだとAPIがエラーを返さず黙って無視するため、Proxyが設定されないまま
        # Zabbixサーバーが直接ディスカバリを試み、顧客のプライベートネットワークに到達できなかった。
        params["proxyid"] = proxy_id

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


def _create_new_device_action(zabbix: ZabbixClient, name: str, druleid: str, userids: list[str]) -> None:
    # 検出ステータス=Discovered（今回のスキャンで初めて検出、想定値=2）でのみ発火する。
    # SNMP機器登録／ICMPフォールバック登録が使う Up(0)/Down(1) とは異なる値のため、
    # 取り違えると既知の機器に対して毎サイクル誤通知が飛ぶ。安全のため status=1（無効）
    # で作成し、Zabbix管理画面での目視確認・手動有効化を必須とする。
    # mediatypeid=0（受信者ごとに設定済みの全メディアで送信）にしているため、
    # 社内ユーザー(Slack)・顧客ユーザー(メール)が混在していてもそれぞれの設定通りに届く。
    zabbix.call("action.create", {
        "name": name,
        "eventsource": 1,
        "status": 1,  # 無効（手動確認後に人間が有効化する）
        "filter": {
            "evaltype": 0,
            "conditions": [
                {"conditiontype": 18, "operator": 0, "value": druleid},   # ディスカバリルール
                {"conditiontype": 8,  "operator": 0, "value": "11"},     # サービスタイプ=SNMPv2
                {"conditiontype": 10, "operator": 0, "value": "2"},      # 検出ステータス=Discovered(想定値)
            ],
        },
        "operations": [
            {
                "operationtype": 0,
                "opmessage_usr": [{"userid": uid} for uid in userids],
                "opmessage": {"default_msg": 1, "mediatypeid": 0},
            },
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
    p.add_argument("--notify-user", default="atladmin", help="新規機器検知通知の送信先Zabbixユーザー名（デフォルト atladmin）")
    return p.parse_args()


if __name__ == "__main__":
    main()
