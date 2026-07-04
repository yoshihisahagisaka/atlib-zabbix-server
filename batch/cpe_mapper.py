"""CPE マッピング。

優先度:
  1. cpe_overrides.json の手動マッピング
  2. NVD CPE Suggest API による自動検索
  3. None（CVE 検索をキーワードフォールバックに委ねる）
"""
import json
import time
import requests
from pathlib import Path


class CpeMapper:
    _NVD_CPE_URL = "https://services.nvd.nist.gov/rest/json/cpes/2.0"

    def __init__(self, overrides_path: Path, nvd_api_key: str = ""):
        with open(overrides_path, encoding="utf-8") as f:
            self._overrides: dict[str, str] = json.load(f)
        self._api_key = nvd_api_key or ""
        self._headers = {"apiKey": self._api_key} if self._api_key else {}
        self._rate_delay = 0.6 if self._api_key else 6.0
        self._last_req = 0.0
        self._cache: dict[str, str | None] = {}

    def get_cpe(self, device_key: str) -> str | None:
        """デバイスキー（"Vendor Model"）に対応する CPE 文字列を返す。"""
        if device_key in self._overrides:
            return self._overrides[device_key]
        if device_key in self._cache:
            return self._cache[device_key]

        cpe = self._search_nvd(device_key)
        self._cache[device_key] = cpe
        return cpe

    def _search_nvd(self, device_key: str) -> str | None:
        self._rate_wait()
        try:
            r = requests.get(
                self._NVD_CPE_URL,
                params={"keywordSearch": device_key, "resultsPerPage": 5},
                headers=self._headers,
                timeout=30,
            )
            r.raise_for_status()
            products = r.json().get("products", [])
            if products:
                return products[0]["cpe"]["cpeName"]
        except Exception as e:
            print(f"  [警告] CPE 検索失敗 ({device_key}): {e}")
        return None

    def _rate_wait(self):
        elapsed = time.monotonic() - self._last_req
        if elapsed < self._rate_delay:
            time.sleep(self._rate_delay - elapsed)
        self._last_req = time.monotonic()
