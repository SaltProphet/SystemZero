#!/usr/bin/env python3
"""Compare current Locust metrics against baseline and detect regressions."""
import json
import sys
from pathlib import Path
from typing import Dict
import csv

REGRESSION_THRESHOLD_PCT = 10.0  # 10% regression threshold


def parse_locust_csv(stats_csv: Path) -> Dict[str, Dict[str, float]]:
    """Parse Locust CSV and return metrics dict."""
    metrics = {}
    with open(stats_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('Name', '')
            if name == "Aggregated" or not name:
                continue
            endpoint = f"{name} ({row.get('Type', 'GET')})"
            metrics[endpoint] = {
                'count': int(row.get('Request Count', row.get('# Requests', row.get('Count', 0)))),
                'avg_ms': float(row.get('Average Response Time', row.get('Average', 0))),
                'p95_ms': float(row.get('95%', 0)),
                'failure_rate': float(row.get('Failure Rate', '0').rstrip('%')),
            }
    return metrics


def load_baseline(baseline_path: Path) -> Dict:
    """Load baseline metrics from JSON."""
    if not baseline_path.exists():
        return {}
    with open(baseline_path) as f:
        return json.load(f)


def save_baseline(metrics: Dict, baseline_path: Path):
    """Save metrics as new baseline."""
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    with open(baseline_path, 'w') as f:
        json.dump(metrics, f, indent=2)


def detect_regressions(current: Dict, baseline: Dict) -> list:
    """Detect performance regressions."""
    regressions = []
    for endpoint, curr_metrics in current.items():
        if endpoint not in baseline:
            continue
        base_metrics = baseline[endpoint]
        
        # Check p95 regression
        if base_metrics['p95_ms'] > 0:
            p95_change = ((curr_metrics['p95_ms'] - base_metrics['p95_ms']) / base_metrics['p95_ms']) * 100
            if p95_change > REGRESSION_THRESHOLD_PCT:
                regressions.append(
                    f"{endpoint}: p95 increased by {p95_change:.1f}% "
                    f"({base_metrics['p95_ms']:.2f}ms → {curr_metrics['p95_ms']:.2f}ms)"
                )
        
        # Check failure rate increase
        fail_increase = curr_metrics['failure_rate'] - base_metrics['failure_rate']
        if fail_increase > 0.5:  # 0.5% increase
            regressions.append(
                f"{endpoint}: failure rate increased by {fail_increase:.1f}% "
                f"({base_metrics['failure_rate']:.1f}% → {curr_metrics['failure_rate']:.1f}%)"
            )
    
    return regressions


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Compare Locust metrics against baseline")
    parser.add_argument('--current', type=Path, default=Path('locust_stats.csv'))
    parser.add_argument('--baseline', type=Path, default=Path('.baseline/locust_baseline.json'))
    parser.add_argument('--save-baseline', action='store_true', help="Save current as new baseline")
    args = parser.parse_args()
    
    # Parse current metrics
    current_metrics = parse_locust_csv(args.current)
    
    if args.save_baseline:
        save_baseline(current_metrics, args.baseline)
        print(f"✓ Baseline saved to {args.baseline}")
        return
    
    baseline = load_baseline(args.baseline)
    if not baseline:
        print("⚠ No baseline found. Run with --save-baseline to create one.")
        return
    
    regressions = detect_regressions(current_metrics, baseline)
    if regressions:
        print("### 📉 Performance Regressions Detected")
        for r in regressions:
            print(f"- {r}")
        sys.exit(1)
    else:
        print("✓ No regressions detected")


if __name__ == "__main__":
    main()
