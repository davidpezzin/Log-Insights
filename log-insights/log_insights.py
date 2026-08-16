"""Análise determinística de logs de requisições no formato JSON Lines."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Report:
    total_requests: int
    invalid_lines: int
    error_rate: float
    p95_duration_ms: float
    requests_by_path: dict[str, int]


def analyze(lines: Iterable[str]) -> Report:
    total = invalid = errors = 0
    durations: list[float] = []
    paths: Counter[str] = Counter()
    for line in lines:
        try:
            record = json.loads(line)
            path = record["path"]
            status = int(record["status"])
            duration = float(record["duration_ms"])
            if not isinstance(path, str) or duration < 0:
                raise ValueError("invalid event shape")
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            invalid += 1
            continue
        total += 1
        errors += status >= 500
        durations.append(duration)
        paths[path] += 1

    p95 = 0.0 if not durations else sorted(durations)[math.ceil(len(durations) * 0.95) - 1]
    return Report(
        total_requests=total,
        invalid_lines=invalid,
        error_rate=0.0 if total == 0 else errors / total,
        p95_duration_ms=p95,
        requests_by_path=dict(paths.most_common()),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize JSONL HTTP logs")
    parser.add_argument("log_file", type=Path)
    args = parser.parse_args()
    with args.log_file.open(encoding="utf-8") as file:
        report = analyze(file)
    print(f"requests={report.total_requests} invalid_lines={report.invalid_lines}")
    print(f"error_rate={report.error_rate:.1%} p95_ms={report.p95_duration_ms:.1f}")
    for path, count in report.requests_by_path.items():
        print(f"{path}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
