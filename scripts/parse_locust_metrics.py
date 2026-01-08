#!/usr/bin/env python3
"""Parse Locust CSV stats and extract key metrics for reporting."""
import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def parse_stats(stats_csv: Path) -> Dict[str, Dict[str, float]]:
    """Parse locust_stats.csv and return endpoint metrics."""
    metrics: Dict[str, Dict[str, float]] = {}
    with open(stats_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            endpoint = f"{row['Name']} ({row['Type']})" if 'Type' in row else row['Name']
            metrics[endpoint] = {
                'count': int(row.get('Count', 0)),
                'avg_ms': float(row.get('Average', 0)) / 1000.0,  # Convert from ms to s then back
                'min_ms': float(row.get('Min', 0)) / 1000.0,
                'max_ms': float(row.get('Max', 0)) / 1000.0,
                'median_ms': float(row.get('Median', 0)) / 1000.0,
                'p95_ms': float(row.get('95%', 0)) / 1000.0,
                'failure_rate': float(row.get('Failure Rate', 0)),
            }
    return metrics


def format_report(metrics: Dict[str, Dict[str, float]]) -> str:
    """Format metrics as markdown table."""
    lines = [
        "| Endpoint | Count | Avg (ms) | Median (ms) | p95 (ms) | Max (ms) | Fail % |",
        "|----------|-------|---------|------------|---------|---------|--------|",
    ]
    for endpoint, m in metrics.items():
        lines.append(
            f"| {endpoint} | {m['count']} | {m['avg_ms']:.2f} | {m['median_ms']:.2f} | "
            f"{m['p95_ms']:.2f} | {m['max_ms']:.2f} | {m['failure_rate']:.1f} |"
        )
    return "\n".join(lines)


def main():
    stats_csv = Path("locust_stats.csv")
    if not stats_csv.exists():
        print(f"Warning: {stats_csv} not found", file=sys.stderr)
        sys.exit(1)
    
    metrics = parse_stats(stats_csv)
    report = format_report(metrics)
    print(report)


if __name__ == "__main__":
    main()
