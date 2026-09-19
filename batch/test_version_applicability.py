"""Unit tests for conservative CVE firmware applicability."""
import unittest
from version_applicability import compare_versions, evaluate_version
from main import _classify_cves

class VersionApplicabilityTests(unittest.TestCase):
    def test_range_including_excluding_affected(self):
        r=evaluate_version("9.4.13",{"criteria":"cpe:2.3:a:x:y:*:*:*:*:*:*:*:*","versionStartIncluding":"9.4.0","versionEndExcluding":"9.4.14"})
        self.assertEqual(r.status,"confirmed_affected")

    def test_range_end_excluding_not_affected(self):
        r=evaluate_version("9.4.14",{"criteria":"cpe:2.3:a:x:y:*:*:*:*:*:*:*:*","versionStartIncluding":"9.4.0","versionEndExcluding":"9.4.14"})
        self.assertEqual(r.status,"not_affected")

    def test_exact_version(self):
        self.assertEqual(evaluate_version("16.7.1",{"criteria":"cpe:2.3:a:x:y:16.7.1:*:*:*:*:*:*:*"}).status,"confirmed_affected")
        self.assertEqual(evaluate_version("16.7.2",{"criteria":"cpe:2.3:a:x:y:16.7.1:*:*:*:*:*:*:*"}).status,"not_affected")

    def test_missing_firmware(self):
        self.assertEqual(evaluate_version("",{"versionEndExcluding":"2.0"}).status,"not_assessable")

    def test_ambiguous_version_is_potential(self):
        self.assertEqual(evaluate_version("release-x",{"versionEndExcluding":"2.0"}).status,"potentially_affected")

    def test_keyword_never_confirms(self):
        c=[{"configurations":[]}]
        counts=_classify_cves(c,"1.0","keyword")
        self.assertEqual(counts["potentially_affected"],1)
        self.assertEqual(counts["confirmed_affected"],0)

    def test_complex_and_never_confirms(self):
        c=[{"configurations":[{"operator":"AND","nodes":[{"cpeMatch":[{"vulnerable":True,"criteria":"cpe:2.3:a:x:y:*:*:*:*:*:*:*:*","versionEndExcluding":"2.0"}]}]}]}]
        counts=_classify_cves(c,"1.0","cpe")
        self.assertEqual(counts["potentially_affected"],1)

    def test_simple_range_confirms(self):
        c=[{"configurations":[{"operator":"OR","nodes":[{"cpeMatch":[{"vulnerable":True,"criteria":"cpe:2.3:a:x:y:*:*:*:*:*:*:*:*","versionStartIncluding":"1.0","versionEndExcluding":"2.0"}]}]}]}]
        counts=_classify_cves(c,"1.5","cpe")
        self.assertEqual(counts["confirmed_affected"],1)

if __name__=="__main__":
    unittest.main()
