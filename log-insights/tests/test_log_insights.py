import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from log_insights import analyze


class LogInsightsTests(unittest.TestCase):
    def test_calculates_metrics_and_ignores_bad_lines(self) -> None:
        report = analyze([
            '{"path":"/a","status":200,"duration_ms":10}\n',
            '{"path":"/a","status":503,"duration_ms":20}\n',
            '{"path":"/b","status":200,"duration_ms":30}\n',
            'bad json\n',
        ])
        self.assertEqual(3, report.total_requests)
        self.assertEqual(1, report.invalid_lines)
        self.assertAlmostEqual(1 / 3, report.error_rate)
        self.assertEqual(30, report.p95_duration_ms)
        self.assertEqual({"/a": 2, "/b": 1}, report.requests_by_path)

    def test_handles_empty_input(self) -> None:
        report = analyze([])
        self.assertEqual(0, report.total_requests)
        self.assertEqual(0.0, report.p95_duration_ms)
