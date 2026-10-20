import json
import tempfile
import unittest
from pathlib import Path

from springfleetbench.benchmark import SuiteError, _check, load_suite, run_suite


class BenchmarkTests(unittest.TestCase):
    def test_file_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "pom.xml").write_text("<java.version>17</java.version>", encoding="utf-8")
            result = _check({"type": "file_contains", "path": "pom.xml", "value": "17"}, root)
            self.assertTrue(result["passed"])

    def test_rejects_path_traversal_in_check(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(SuiteError):
                _check({"type": "file_contains", "path": "../secret", "value": "x"}, Path(temp))

    def test_rejects_duplicate_task_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            suite_path = Path(temp) / "suite.json"
            suite_path.write_text(json.dumps({"tasks": [
                {"id": "same", "fixture": "a"}, {"id": "same", "fixture": "b"}
            ]}), encoding="utf-8")
            with self.assertRaises(SuiteError):
                load_suite(suite_path)

    def test_runner_reports_fleet_failure_for_bad_candidate(self):
        suite = Path(__file__).parents[1] / "suites/pilot/suite.json"
        result = run_suite(suite, "true")
        self.assertEqual(2, result["tasks_total"])
        self.assertFalse(result["fleet_success"])
        self.assertEqual(0.0, result["success_rate"])


if __name__ == "__main__":
    unittest.main()
