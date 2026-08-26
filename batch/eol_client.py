"""EoL クライアント。H/W（機器本体）とS/W（現在搭載中のファームウェア/OS）を独立に判定する。

「機器本体はまだ販売・サポート中だが、現在搭載中のファームウェアバージョンは
サポート切れ」というケース（逆もあり得る）を区別できるようにするための分離。
endoflife.dateのカタログ自体、機種単位のプロダクト(例: netgear)とOS/ファームウェア
単位のプロダクト(例: cisco-ios)が混在しているため、_VENDOR_SLUG_MAPで各スラグに
kind("hw"/"sw")を付与し、hw系はmodelで、sw系はfirmwareでマッチングする。

get_hw_eol()・get_sw_eol()は常にdictを返す（Noneは返さない）。statusキーで
確信度を明示する:
  "confirmed"    - eol_overrides.jsonの手動データ（人間が一次情報を確認済み）
  "fuzzy_match"  - endoflife.dateの型番/バージョン部分一致による自動判定。
                   誤爆しうる（例:「625」を含む無関係なcycle文字列に一致）ため、
                   "confirmed"とは区別して「要確認」として扱うこと
  "unknown"      - reasonキー: "no_source"（対応ソースなし）/
                   "lookup_failed"（API呼び出し失敗）/ "no_match"（スラグはあるが一致なし）

優先度:
  1. eol_overrides.json の手動データ（hw/sw別）
  2. endoflife.date API（自動、fuzzy_match）
  3. unknown
"""
import json
import re
import requests
from datetime import datetime, date
from pathlib import Path


_EOL_API_BASE = "https://endoflife.date/api"

# ベンダー名（小文字）→ (endoflife.dateスラグ, kind) の対応表
# kind="hw": 機種単位のプロダクト。modelでマッチングする
# kind="sw": OS/ファームウェア単位のプロダクト。firmware(software_full)でマッチングする
# 対応製品は https://endoflife.date/api/all.json で確認できる
# Ubiquiti/UniFiはendoflife.dateに掲載なし → eol_overrides.jsonで手動管理
_VENDOR_SLUG_MAP: dict[str, tuple[str, str] | None] = {
    "netgear":  ("netgear", "hw"),
    "cisco":    ("cisco-ios", "sw"),
    "juniper":  ("junos", "sw"),
    "fortinet": ("fortigate", "sw"),
    "paloalto": ("pan-os", "sw"),
    "hp":       ("hpe-oneview", "sw"),
    "brother":  None,   # endoflife.dateに未掲載。overridesで管理
    "ubiquiti": None,   # endoflife.dateに未掲載。overridesで管理
    "ui":       None,   # Ubiquiti社ブランド別名
}


class EolClient:
    def __init__(self, overrides_path: Path):
        with open(overrides_path, encoding="utf-8") as f:
            self._overrides: dict[str, dict] = json.load(f)

    def get_hw_eol(self, device_key: str, model: str = "") -> dict:
        """機器本体（H/W）の販売・サポート終了状況を返す。"""
        override = self._overrides.get(device_key, {}).get("hw")
        if override:
            return self._enrich(override, status="confirmed")

        slug_info = self._guess_slug(device_key)
        if slug_info is None or slug_info[1] != "hw":
            return self._unknown("no_source")

        return self._lookup_endoflife(slug_info[0], model or device_key)

    def get_sw_eol(self, device_key: str, firmware: str = "") -> dict:
        """現在搭載中のファームウェア/OS（S/W）のサポート終了状況を返す。"""
        override = self._overrides.get(device_key, {}).get("sw")
        if override:
            return self._enrich(override, status="confirmed")

        slug_info = self._guess_slug(device_key)
        if slug_info is None or slug_info[1] != "sw":
            return self._unknown("no_source")
        if not firmware:
            return self._unknown("no_source")

        return self._lookup_endoflife(slug_info[0], firmware)

    # ------------------------------------------------------------------

    def _lookup_endoflife(self, slug: str, match_str: str) -> dict:
        cycles = self._fetch_cycles(slug)
        if cycles is None:
            return self._unknown("lookup_failed")
        cycle = self._match_cycle(cycles, match_str)
        if cycle is None:
            return self._unknown("no_match")
        # endoflife.date側の部分一致であり、CPEマッチング同様に誤爆しうるため
        # "confirmed"ではなく"fuzzy_match"として区別する（要確認）。
        return self._enrich(cycle, status="fuzzy_match")

    def _guess_slug(self, device_key: str) -> tuple[str, str] | None:
        key_lower = device_key.lower()
        for vendor, slug_info in _VENDOR_SLUG_MAP.items():
            if vendor in key_lower:
                return slug_info  # Noneの場合は呼び出し元がNoneチェック済み
        return None

    def _fetch_cycles(self, slug: str) -> list[dict] | None:
        try:
            r = requests.get(f"{_EOL_API_BASE}/{slug}.json", timeout=10)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return None

    def _match_cycle(self, cycles: list[dict], value: str) -> dict | None:
        """型番/バージョン文字列が最も近いサイクルエントリを返す。"""
        normalized = re.sub(r"[-_ ]", "", value).lower()
        for cycle in cycles:
            cycle_str = re.sub(r"[-_ ]", "", str(cycle.get("cycle", ""))).lower()
            if cycle_str and (cycle_str in normalized or normalized in cycle_str):
                return cycle
        return None

    def _enrich(self, data: dict, status: str) -> dict:
        result = dict(data)
        result["status"] = status
        eol_raw = data.get("eol")
        if eol_raw is None:
            eol_raw = data.get("eol_date")

        if isinstance(eol_raw, bool):
            result["is_eol"] = eol_raw
            result["days_until_eol"] = -1 if eol_raw else None
            result["eol_date"] = None
            return result

        if isinstance(eol_raw, str):
            try:
                eol_dt = datetime.strptime(eol_raw, "%Y-%m-%d").date()
                today = date.today()
                days = (eol_dt - today).days
                result["eol_date"] = eol_raw
                result["days_until_eol"] = days
                result["is_eol"] = days < 0
                return result
            except ValueError:
                pass

        # eol/eol_dateが無い(null)場合でも、手動overridesはis_eolを明示的な真偽値で
        # 持っていることがある(例: {"eol_date": null, "is_eol": false} = EoL未発表)。
        # その場合はそれを尊重する。
        if isinstance(data.get("is_eol"), bool):
            result["is_eol"] = data["is_eol"]
            result["days_until_eol"] = None
            result["eol_date"] = data.get("eol_date")
            return result

        result["is_eol"] = None
        result["days_until_eol"] = None
        result["eol_date"] = str(eol_raw) if eol_raw else None
        return result

    def _unknown(self, reason: str) -> dict:
        return {
            "status": "unknown",
            "reason": reason,
            "is_eol": None,
            "eol_date": None,
            "days_until_eol": None,
        }
