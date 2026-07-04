"""EoL クライアント。

優先度:
  1. eol_overrides.json の手動データ（調査済み実機情報）
  2. endoflife.date API（自動。スラグが解決できた場合のみ）
  3. None（情報なし）
"""
import json
import re
import requests
from datetime import datetime, date
from pathlib import Path


_EOL_API_BASE = "https://endoflife.date/api"

# ベンダー名（小文字）→ endoflife.date スラグの対応表
# 対応製品は https://endoflife.date/api/all.json で確認できる
# Ubiquiti/UniFiはendoflife.dateに掲載なし → eol_overrides.jsonで手動管理
_VENDOR_SLUG_MAP: dict[str, str] = {
    "netgear":  "netgear",
    "cisco":    "cisco-ios",
    "juniper":  "junos",
    "fortinet": "fortigate",
    "paloalto": "pan-os",
    "hp":       "hpe-oneview",
    "brother":  None,   # endoflife.dateに未掲載。overridesで管理
    "ubiquiti": None,   # endoflife.dateに未掲載。overridesで管理
    "ui":       None,   # Ubiquiti社ブランド別名
}


class EolClient:
    def __init__(self, overrides_path: Path):
        with open(overrides_path, encoding="utf-8") as f:
            self._overrides: dict[str, dict] = json.load(f)

    def get_eol(self, device_key: str, model: str = "") -> dict | None:
        """デバイスキー（"Vendor Model"）の EoL 情報を返す。"""
        if device_key in self._overrides:
            return self._enrich(self._overrides[device_key])

        slug = self._guess_slug(device_key)
        if slug is not None:
            cycles = self._fetch_cycles(slug)
            if cycles:
                cycle = self._match_cycle(cycles, model or device_key)
                if cycle:
                    return self._enrich(cycle)

        return None

    # ------------------------------------------------------------------

    def _guess_slug(self, device_key: str) -> str | None:
        key_lower = device_key.lower()
        for vendor, slug in _VENDOR_SLUG_MAP.items():
            if vendor in key_lower:
                return slug  # None の場合は呼び出し元が None チェック済み
        return None

    def _fetch_cycles(self, slug: str) -> list[dict] | None:
        try:
            r = requests.get(f"{_EOL_API_BASE}/{slug}.json", timeout=10)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return None

    def _match_cycle(self, cycles: list[dict], model: str) -> dict | None:
        """モデル文字列が最も近いサイクルエントリを返す。"""
        normalized = re.sub(r"[-_ ]", "", model).lower()
        for cycle in cycles:
            cycle_str = re.sub(r"[-_ ]", "", str(cycle.get("cycle", ""))).lower()
            if cycle_str and (cycle_str in normalized or normalized in cycle_str):
                return cycle
        return None

    def _enrich(self, data: dict) -> dict:
        result = dict(data)
        eol_raw = data.get("eol") or data.get("eol_date")

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

        result["is_eol"] = None
        result["days_until_eol"] = None
        result["eol_date"] = str(eol_raw) if eol_raw else None
        return result
