#!/usr/bin/env python3
import argparse
import json
import math
import sys
from collections import Counter


def _route_from_record(record):
    for key in ("route", "path", "endpoint"):
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _status_from_record(record):
    for key in ("status", "status_code", "code"):
        value = record.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def _latency_from_record(record):
    for key in ("latency_ms", "duration_ms", "latency", "duration"):
        value = record.get(key)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                continue
    return None


def parse_jsonl(stream):
    records = []
    for raw_line in stream:
        line = raw_line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records


def p95(values):
    if not values:
        return None
    sorted_values = sorted(values)
    rank = max(0, math.ceil(0.95 * len(sorted_values)) - 1)
    return sorted_values[rank]


def build_metrics(records):
    route_volume = Counter()
    latencies = []
    total_requests = len(records)
    error_requests = 0

    for record in records:
        route = _route_from_record(record)
        if route:
            route_volume[route] += 1

        status = _status_from_record(record)
        if status is not None and status >= 400:
            error_requests += 1

        latency = _latency_from_record(record)
        if latency is not None:
            latencies.append(latency)

    error_rate = (error_requests / total_requests) if total_requests else 0.0
    return {
        "total_requests": total_requests,
        "error_requests": error_requests,
        "error_rate": error_rate,
        "p95_latency_ms": p95(latencies),
        "route_volume": dict(sorted(route_volume.items())),
    }


def _open_input(path):
    if path == "-":
        return sys.stdin
    return open(path, "r", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Transforma logs JSON Lines em métricas de volume, erro e p95."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="Arquivo JSON Lines de entrada (ou - para stdin).",
    )
    args = parser.parse_args(argv)

    if args.input == "-":
        records = parse_jsonl(sys.stdin)
    else:
        with _open_input(args.input) as stream:
            records = parse_jsonl(stream)

    json.dump(build_metrics(records), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
