"""ベンダー分布調査スクリプト（日次バッチとは別、単発/再実行可能）。

実際の顧客機器のベンダー分布を集計し、EoLデータソース（endoflife.date自動対応 /
eol_overrides.json手動対応 / 未対応）のカバレッジを判断するための材料を出力する。

未対応ベンダーについては、endoflife.dateの全プロダクト一覧(all.json、単純な
スラグ文字列の配列)から名前が近い候補を参考表示するが、これはあくまで人間が
判断するための「候補」であり、そのままeol_client.pyの自動判定には使わない
（そのプロダクトが実際にハードウェアかソフトウェアか(kind)・型番の一致基準が
妥当かは、人間が実際にendoflife.dateのページを確認して判断する必要がある。
機械的な自動採用は誤ったEoL判定の原因になるため行わない）。

使い方:
  python vendor_census.py [--config config.yaml]
"""
import argparse
import json
from collections import Counter
from pathlib import Path

import requests

from main import _load_config
from zabbix_client import ZabbixClient
from eol_client import _VENDOR_SLUG_MAP

HERE = Path(__file__).parent
_ALL_PRODUCTS_URL = "https://endoflife.date/api/all.json"


def main():
    args = _parse_args()
    config = _load_config(args.config)

    print("Zabbixからホストインベントリを取得中...")
    zabbix = ZabbixClient(config["zabbix"]["url"], config["zabbix"]["user"], config["zabbix"]["password"])
    hosts = zabbix.get_hosts_inventory()
    print(f"  → インベントリ設定済み {len(hosts)} 件のホスト\n")

    vendor_counts: Counter[str] = Counter()
    blank_count = 0
    for h in hosts:
        vendor = (h.get("inventory") or {}).get("vendor", "").strip()
        if not vendor:
            blank_count += 1
            continue
        vendor_counts[vendor] += 1

    with open(HERE / "eol_overrides.json", encoding="utf-8") as f:
        overrides = json.load(f)
    override_vendors = {k.split()[0].lower() for k in overrides.keys() if not k.startswith("_")}
    auto_vendors = {v for v, slug_info in _VENDOR_SLUG_MAP.items() if slug_info is not None}

    auto_covered: list[tuple[str, int]] = []
    manual_covered: list[tuple[str, int]] = []
    uncovered: list[tuple[str, int]] = []

    for vendor, count in vendor_counts.most_common():
        v_lower = vendor.lower()
        if any(av in v_lower for av in auto_vendors):
            auto_covered.append((vendor, count))
        elif any(ov in v_lower for ov in override_vendors):
            manual_covered.append((vendor, count))
        else:
            uncovered.append((vendor, count))

    print("=== ✅ endoflife.dateで自動カバー済み（eol_client.pyの_VENDOR_SLUG_MAP収載） ===")
    for v, c in auto_covered:
        print(f"  {v}: {c}台")
    if not auto_covered:
        print("  (なし)")

    print("\n=== 📝 eol_overrides.jsonで手動カバー済み ===")
    for v, c in manual_covered:
        print(f"  {v}: {c}台")
    if not manual_covered:
        print("  (なし)")

    print("\n=== ⚠️  未対応ベンダー（台数順。手動調査・_VENDOR_SLUG_MAP追加の優先度付けに使う） ===")
    if not uncovered:
        print("  (なし。全ベンダーが何らかの形でカバーされています)")
    else:
        candidates = _fetch_all_products()
        for v, c in uncovered:
            suggestion = _suggest_slugs(v, candidates) if candidates else []
            suggestion_str = f"  候補: {', '.join(suggestion)}" if suggestion else ""
            print(f"  {v}: {c}台{suggestion_str}")
        if candidates is None:
            print("\n  (endoflife.dateの全プロダクト一覧取得に失敗したため候補提示なし)")

    print("\n=== ❌ インベントリのvendor未入力 ===")
    print(f"  {blank_count}台（この台数がそのまま日次バッチの「未確認(unknown)」の原因になる。"
          f"Sensor Edge/Zabbixテンプレート側でのインベントリ入力を優先すべき機器）")

    print("\n注意: 「候補」はendoflife.date上のスラグ名の文字列類似度による参考情報に過ぎない。")
    print("      ハードウェアかソフトウェアかの区別(kind)・型番の一致基準の妥当性は、人間が実際に")
    print("      endoflife.dateの該当ページを確認したうえでeol_client.pyの_VENDOR_SLUG_MAPに")
    print("      追加すること。誤った追加はEoL誤判定の原因になるため、機械的な自動採用はしない。")


def _fetch_all_products() -> list[str] | None:
    """endoflife.dateの全プロダクト一覧を取得する。レスポンスは単純なスラグ文字列の配列。"""
    try:
        r = requests.get(_ALL_PRODUCTS_URL, timeout=15)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else None
    except Exception as e:
        print(f"[警告] endoflife.date全プロダクト一覧の取得に失敗: {e}")
        return None


def _suggest_slugs(vendor: str, slugs: list[str], limit: int = 3) -> list[str]:
    v_norm = vendor.lower().replace(" ", "").replace("-", "")
    if not v_norm:
        return []
    hits = [s for s in slugs if v_norm in s.replace("-", "")]
    return hits[:limit]


def _parse_args():
    p = argparse.ArgumentParser(description="実際の顧客機器のベンダー分布を集計し、EoLデータソースのカバレッジを判断する")
    p.add_argument("--config", default=str(HERE / "config.yaml"), help="設定ファイルパス")
    return p.parse_args()


if __name__ == "__main__":
    main()
