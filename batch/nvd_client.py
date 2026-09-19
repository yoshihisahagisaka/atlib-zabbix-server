"""NVD CVE API v2 クライアント + CISA KEV 照合。

CVE 取得の優先度:
  1. CPE 名で完全検索
  2. CPE なし → キーワード検索（フォールバック）

CISA KEV（Known Exploited Vulnerabilities）はバッチ起動時に一括取得し、
CVE ごとに "actively_exploited" フラグを付与する。
"""
import time
import requests


_NVD_CVE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"


class NvdLookupError(Exception):
    """NVD API呼び出し失敗（タイムアウト・レート制限・不正レスポンス等）。
    「検索したがCVE 0件」と区別するための専用例外。呼び出し側(main.py)はこれを
    捕捉してcve_status="lookup_failed"とし、risk_level="unknown"につなげる
    （検索失敗を「脆弱性なし」と誤認しないため）。"""


class NvdClient:
    def __init__(self, nvd_api_key: str = ""):
        self._api_key = nvd_api_key or ""
        self._headers = {"apiKey": self._api_key} if self._api_key else {}
        self._rate_delay = 0.6 if self._api_key else 6.0
        self._last_req = 0.0
        self.kev_unavailable = False
        self._kev: set[str] = self._fetch_kev()

    # ------------------------------------------------------------------
    # 公開 API
    # ------------------------------------------------------------------

    def get_cves_by_cpe(self, cpe: str, max_results: int = 20) -> list[dict]:
        return self._search({"cpeName": cpe, "resultsPerPage": max_results})

    def get_cves_by_keyword(self, keyword: str, max_results: int = 20) -> list[dict]:
        return self._search({"keywordSearch": keyword, "resultsPerPage": max_results})

    # ------------------------------------------------------------------
    # 内部処理
    # ------------------------------------------------------------------

    def _search(self, params: dict) -> list[dict]:
        self._rate_wait()
        try:
            r = requests.get(_NVD_CVE_URL, params=params, headers=self._headers, timeout=30)
            r.raise_for_status()
            return [self._parse_item(v) for v in r.json().get("vulnerabilities", [])]
        except Exception as e:
            print(f"  [警告] NVD CVE 取得失敗 ({params}): {e}")
            raise NvdLookupError(str(e)) from e

    def _parse_item(self, item: dict) -> dict:
        cve = item["cve"]
        cve_id: str = cve["id"]

        score, severity = self._extract_cvss(cve.get("metrics", {}))
        description = next(
            (d["value"] for d in cve.get("descriptions", []) if d["lang"] == "en"),
            "",
        )

        return {
            "cve_id": cve_id,
            "description": description,
            "cvss_score": score,
            "severity": severity,
            "published": cve.get("published", ""),
            "modified": cve.get("lastModified", ""),
            "actively_exploited": cve_id in self._kev,
            # Keep NVD applicability configuration so the caller can evaluate the installed firmware.
            "configurations": cve.get("configurations", []),
            "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
        }

    @staticmethod
    def _extract_cvss(metrics: dict) -> tuple[float | None, str | None]:
        for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            entries = metrics.get(key)
            if entries:
                m = entries[0]
                data = m["cvssData"]
                score = data["baseScore"]
                severity = data.get("baseSeverity") or m.get("baseSeverity")
                return score, severity
        return None, None

    def _fetch_kev(self) -> set[str]:
        # KEVは既存CVE結果への"actively_exploited"付与用のenrichmentであり、これ自体が
        # CVEの主ソースではないため、失敗してもバッチ全体は止めない(空集合で継続)。
        # ただしkev_unavailableフラグでmain.py側が「今回の実行はKEV照合なし」と
        # 記録できるようにする(CVE自体が0件のケースと区別するため)。
        try:
            r = requests.get(_KEV_URL, timeout=15)
            r.raise_for_status()
            return {v["cveID"] for v in r.json().get("vulnerabilities", [])}
        except Exception as e:
            print(f"  [警告] CISA KEV 取得失敗: {e}")
            self.kev_unavailable = True
            return set()

    def _rate_wait(self):
        elapsed = time.monotonic() - self._last_req
        if elapsed < self._rate_delay:
            time.sleep(self._rate_delay - elapsed)
        self._last_req = time.monotonic()
