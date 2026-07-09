"""内部運用向けアラート基盤 セットアップスクリプト（一回限りの構成投入用）

長時間稼働機器の検出（Trigger）とLLDP新規ネイバー検知（Trapperアイテム＋Trigger）を
「Network Generic Device by SNMP」テンプレートに追加し、両方をまとめて通知する
内部運用向けAction（トリガーアクション）を作成する。

未知の機器検知（Zabbix Discovery Action、B-1）は、Discoveryアクションの条件コードが
Zabbixバージョンに依存し誤りやすいため、このスクリプトでは自動作成しない。
--dry-run の出力（ディスカバリルール名・各dcheckのtype/ports）を確認のうえ、
本ファイル末尾のコメント「B-1: Discovery Actionの手動作成手順」を参照して
Zabbix管理画面から作成すること。

使い方:
  # 1. まず必ずdry-runで現状を確認する（書き込みは一切行わない）
  python setup_alerts.py --dry-run

  # 2. dry-runの出力を見て --uptime-item-key を確認したうえで実際に作成する
  python setup_alerts.py --apply --uptime-item-key "net.if.uptime" --uptime-days 365 --notify-user atladmin

接続情報（環境変数、どちらか一方）:
  ZABBIX_URL + ZABBIX_TOKEN            （推奨: 失効・ローテーションが容易なAPIトークン）
  ZABBIX_URL + ZABBIX_USER + ZABBIX_PASSWORD
"""
import argparse
import os
import sys

from zabbix_client import ZabbixClient

TEMPLATE_NAME = "Network Generic Device by SNMP"
DISCOVERY_RULE_NAME = "ユーザー用インフラ自動判別"
LLDP_ITEM_KEY = "sec.lldp.new_neighbor"
LLDP_ITEM_NAME = "LLDP新規ネイバー検知"
LLDP_TRIGGER_NAME = "LLDPネイバー新規検知"
ACTION_NAME = "内部運用アラート（長時間稼働・LLDPネイバー新規検知）"


def main():
    args = _parse_args()
    zabbix = _connect()

    version = zabbix.call("apiinfo.version", {})
    print(f"Zabbix APIバージョン: {version}\n")

    template = _find_template(zabbix)
    if not template:
        print(f"[エラー] テンプレート「{TEMPLATE_NAME}」が見つかりません。名称を確認してください。")
        sys.exit(1)
    templateid = template["templateid"]
    print(f"テンプレート「{TEMPLATE_NAME}」: templateid={templateid}")

    _report_uptime_candidates(zabbix, templateid)
    lldp_item_exists = _report_item_status(zabbix, templateid, LLDP_ITEM_KEY)
    uptime_trigger_exists, lldp_trigger_exists = _report_trigger_status(zabbix, templateid, args.uptime_days)
    _report_user_media(zabbix, args.notify_user)
    _report_discovery_rule(zabbix)
    _report_existing_action(zabbix)

    if not args.apply:
        print("\n[dry-run] 書き込みは行っていません。内容を確認のうえ --apply で実行してください。")
        return

    if not args.uptime_item_key:
        print("\n[エラー] --apply には --uptime-item-key が必須です（上記の候補一覧から選んで指定）。")
        sys.exit(1)

    print("\n=== 構成投入を開始します ===")

    if lldp_item_exists:
        print(f"  [スキップ] アイテム {LLDP_ITEM_KEY} は既に存在します")
    else:
        zabbix.call("item.create", {
            "hostid": templateid,
            "name": LLDP_ITEM_NAME,
            "key_": LLDP_ITEM_KEY,
            "type": 2,        # Zabbix trapper
            "value_type": 3,  # unsigned int
        })
        print(f"  [作成] アイテム {LLDP_ITEM_KEY} を作成しました")

    uptime_trigger_name = f"長時間稼働（{args.uptime_days}日超過）"
    if uptime_trigger_exists:
        print(f"  [スキップ] トリガー「{uptime_trigger_name}」は既に存在します")
    else:
        threshold_sec = args.uptime_days * 86400
        zabbix.call("trigger.create", {
            "description": uptime_trigger_name,
            "expression": f"last(/{TEMPLATE_NAME}/{args.uptime_item_key})>={threshold_sec}",
            "priority": 2,  # warning
        })
        print(f"  [作成] トリガー「{uptime_trigger_name}」を作成しました")

    if lldp_trigger_exists:
        print(f"  [スキップ] トリガー「{LLDP_TRIGGER_NAME}」は既に存在します")
    else:
        zabbix.call("trigger.create", {
            "description": LLDP_TRIGGER_NAME,
            "expression": f"last(/{TEMPLATE_NAME}/{LLDP_ITEM_KEY})=1",
            "priority": 2,  # warning
        })
        print(f"  [作成] トリガー「{LLDP_TRIGGER_NAME}」を作成しました")

    _create_or_report_action(zabbix, args.notify_user, uptime_trigger_name)

    print("\n完了。Zabbix管理画面でトリガー・アクションの内容を確認してください。")
    print("未知の機器検知（Discovery Action）はこのスクリプトでは作成していません。")
    print("本ファイル末尾のコメント「B-1: Discovery Actionの手動作成手順」を参照してください。")


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
# 現状確認（dry-run・apply共通で実行、常に読み取りのみ）
# ------------------------------------------------------------------

def _find_template(zabbix: ZabbixClient) -> dict | None:
    templates = zabbix.call("template.get", {
        "output": ["templateid", "name"],
        "filter": {"name": TEMPLATE_NAME},
    })
    return templates[0] if templates else None


def _report_uptime_candidates(zabbix: ZabbixClient, templateid: str) -> None:
    items = zabbix.call("item.get", {
        "hostids": templateid,
        "output": ["itemid", "name", "key_"],
        "search": {"key_": "uptime"},
    })
    print("\n稼働時間アイテムの候補（--uptime-item-key にはこの中のkey_を指定）:")
    if not items:
        print("  見つかりませんでした。テンプレートのアイテム一覧を直接確認してください。")
    for it in items:
        print(f"  - name=\"{it['name']}\"  key_=\"{it['key_']}\"")


def _report_item_status(zabbix: ZabbixClient, templateid: str, key: str) -> bool:
    items = zabbix.call("item.get", {
        "hostids": templateid,
        "output": ["itemid"],
        "filter": {"key_": key},
    })
    exists = len(items) > 0
    print(f"\nアイテム {key}: {'既に存在します' if exists else '未作成'}")
    return exists


def _report_trigger_status(zabbix: ZabbixClient, templateid: str, uptime_days: int) -> tuple[bool, bool]:
    triggers = zabbix.call("trigger.get", {
        "hostids": templateid,
        "output": ["triggerid", "description"],
    })
    names = {t["description"] for t in triggers}
    uptime_name = f"長時間稼働（{uptime_days}日超過）"
    uptime_exists = uptime_name in names
    lldp_exists = LLDP_TRIGGER_NAME in names
    print(f"トリガー「{uptime_name}」: {'既に存在します' if uptime_exists else '未作成'}")
    print(f"トリガー「{LLDP_TRIGGER_NAME}」: {'既に存在します' if lldp_exists else '未作成'}")
    return uptime_exists, lldp_exists


def _report_user_media(zabbix: ZabbixClient, username: str) -> None:
    users = zabbix.call("user.get", {
        "output": ["userid", "username"],
        "filter": {"username": username},
        "selectMedias": "extend",
    })
    print(f"\n通知先ユーザー「{username}」:")
    if not users:
        print(f"  [エラー] ユーザーが見つかりません。--notify-user で正しいユーザー名を指定してください。")
        return
    medias = users[0].get("medias", [])
    if not medias:
        print("  [警告] Media（通知手段）が未設定です。このユーザーへは通知が届きません。")
    for m in medias:
        status = "有効" if m.get("active") == "0" else "無効"
        print(f"  - mediatypeid={m.get('mediatypeid')} sendto={m.get('sendto')} status={status}")


def _report_discovery_rule(zabbix: ZabbixClient) -> None:
    rules = zabbix.call("drule.get", {
        "output": ["druleid", "name"],
        "filter": {"name": DISCOVERY_RULE_NAME},
        "selectDChecks": "extend",
    })
    print(f"\nディスカバリルール「{DISCOVERY_RULE_NAME}」:")
    if not rules:
        print("  見つかりませんでした。名称を確認してください。")
        return
    rule = rules[0]
    print(f"  druleid={rule['druleid']}")
    print("  dcheck一覧（B-1のDiscovery Action作成時にSNMPのdcheckidを確認するために使用）:")
    for dc in rule.get("dchecks", []):
        print(f"    - dcheckid={dc.get('dcheckid')} type={dc.get('type')} ports={dc.get('ports')} key_={dc.get('key_', '')}")


def _report_existing_action(zabbix: ZabbixClient) -> None:
    actions = zabbix.call("action.get", {
        "output": ["actionid", "name", "eventsource"],
        "filter": {"name": ACTION_NAME},
    })
    print(f"\nAction「{ACTION_NAME}」: {'既に存在します（actionid=' + actions[0]['actionid'] + '）' if actions else '未作成'}")


# ------------------------------------------------------------------
# 作成
# ------------------------------------------------------------------

def _create_or_report_action(zabbix: ZabbixClient, notify_user: str, uptime_trigger_name: str) -> None:
    existing = zabbix.call("action.get", {"output": ["actionid"], "filter": {"name": ACTION_NAME}})
    if existing:
        print(f"  [スキップ] Action「{ACTION_NAME}」は既に存在します")
        return

    users = zabbix.call("user.get", {"output": ["userid"], "filter": {"username": notify_user}})
    if not users:
        print(f"  [エラー] 通知先ユーザー「{notify_user}」が見つからないため、Actionの作成をスキップしました。")
        return
    userid = users[0]["userid"]

    zabbix.call("action.create", {
        "name": ACTION_NAME,
        "eventsource": 0,  # トリガーイベント
        "status": 0,       # 有効
        "esc_period": "1h",
        "filter": {
            "evaltype": 2,  # OR
            "conditions": [
                {"conditiontype": 3, "operator": 2, "value": uptime_trigger_name},  # トリガー名 like
                {"conditiontype": 3, "operator": 2, "value": LLDP_TRIGGER_NAME},    # トリガー名 like
            ],
        },
        "operations": [{
            "operationtype": 0,  # メッセージ送信
            "opmessage_usr": [{"userid": userid}],
            "opmessage": {"default_msg": 1, "mediatypeid": 0},
        }],
    })
    print(f"  [作成] Action「{ACTION_NAME}」を作成しました（通知先: {notify_user}）")


def _parse_args():
    p = argparse.ArgumentParser(description="内部運用向けアラート基盤セットアップ")
    p.add_argument("--apply", action="store_true", help="実際に作成する（指定しなければdry-run）")
    p.add_argument("--dry-run", action="store_true", help="現状確認のみ（デフォルト動作、明示指定も可）")
    p.add_argument("--uptime-item-key", default="", help="長時間稼働Triggerに使うアイテムキー（dry-run出力の候補から選ぶ）")
    p.add_argument("--uptime-days", type=int, default=365, help="長時間稼働とみなす日数（デフォルト365）")
    p.add_argument("--notify-user", default="atladmin", help="通知先Zabbixユーザー名（デフォルト atladmin）")
    return p.parse_args()


if __name__ == "__main__":
    main()


# ====================================================================
# B-1: Discovery Actionの手動作成手順（Zabbix管理画面）
#
# このスクリプトのdry-run出力（ディスカバリルールのdcheck一覧）で、
# type がSNMPv2エージェントに該当するdcheckのdcheckidを確認したうえで、
# Zabbix管理画面（設定 > アクション > 検出アクション）から以下を作成する。
#
#   名前: 新規機器検知（SNMP）
#   条件:
#     - ディスカバリルール = ユーザー用インフラ自動判別
#     - サービスタイプ = SNMPv2エージェント（上記dcheckに対応するもの）
#     - デバイスのステータス = 稼働中（Up）
#   実行内容:
#     - メッセージの送信 → 対象ユーザー: atladmin（または--notify-userで指定したユーザー）
#
# ※ 上記条件で「ユーザー用インフラ自動判別」ルールにSNMPチェックが
#    含まれていない場合、このアクションは何も検知できない。その場合は
#    ディスカバリルール自体にSNMPv2エージェントのチェックを追加する
#    必要があるが、これは既存の顧客自動登録フローに影響する変更のため、
#    別途影響範囲を確認してから行うこと。
# ====================================================================
