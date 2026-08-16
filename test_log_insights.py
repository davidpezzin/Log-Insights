import io
import json
import unittest

from log_insights import build_metrics, parse_jsonl


class LogInsightsTests(unittest.TestCase):
    def test_build_metrics_with_mixed_records(self):
        records = [
            {"route": "/users", "status": 200, "latency_ms": 100},
            {"path": "/users", "status_code": "500", "duration_ms": "350.5"},
            {"endpoint": "/health", "code": 204, "latency": 20},
            {"route": "/users", "status": 404, "duration": 150},
        ]

        metrics = build_metrics(records)

        self.assertEqual(metrics["total_requests"], 4)
        self.assertEqual(metrics["error_requests"], 2)
        self.assertEqual(metrics["error_rate"], 0.5)
        self.assertEqual(metrics["route_volume"], {"/health": 1, "/users": 3})
        self.assertEqual(metrics["p95_latency_ms"], 350.5)

    def test_parse_jsonl_skips_invalid_lines(self):
        stream = io.StringIO(
            '\n{"route":"/a","status":200,"latency_ms":10}\ninvalid\n[1,2,3]\n{"route":"/b"}\n'
        )
        records = parse_jsonl(stream)
        self.assertEqual(
            records,
            [
                {"route": "/a", "status": 200, "latency_ms": 10},
                {"route": "/b"},
            ],
        )

    def test_cli_shape_via_metrics_json(self):
        records = [
            {"route": "/x", "status": 200, "latency_ms": 5},
            {"route": "/x", "status": 503, "latency_ms": 100},
        ]
        metrics = build_metrics(records)
        parsed = json.loads(json.dumps(metrics))
        self.assertIn("route_volume", parsed)
        self.assertIn("error_rate", parsed)
        self.assertIn("p95_latency_ms", parsed)


if __name__ == "__main__":
    unittest.main()
