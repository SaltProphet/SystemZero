import asyncio
import time
from statistics import mean
from typing import Dict, Any, List

import httpx

from interface.api.server import app


ENDPOINTS = [
    ("GET", "/status"),
    ("GET", "/health"),
    ("GET", "/dashboard"),
    ("GET", "/templates"),
]


async def bench_once(client: httpx.AsyncClient, method: str, path: str) -> float:
    start = time.perf_counter()
    resp = await client.request(method, path)
    resp.raise_for_status()
    return (time.perf_counter() - start) * 1000.0


async def bench(rounds: int = 20) -> Dict[str, Any]:
    results: Dict[str, List[float]] = {f"{m} {p}": [] for m, p in ENDPOINTS}
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        for _ in range(rounds):
            for method, path in ENDPOINTS:
                try:
                    t = await bench_once(client, method, path)
                    results[f"{method} {path}"].append(t)
                except Exception:
                    results[f"{method} {path}"].append(float("inf"))
    summary = {}
    for k, vals in results.items():
        if not vals:
            continue
        summary[k] = {
            "count": len(vals),
            "min_ms": min(vals),
            "avg_ms": mean(vals),
            "p95_ms": sorted(vals)[int(0.95 * len(vals)) - 1],
            "max_ms": max(vals),
        }
    return summary


def main():
    summary = asyncio.run(bench())
    print("Endpoint Performance (ms):")
    for k, v in summary.items():
        print(f"- {k}: min={v['min_ms']:.2f} avg={v['avg_ms']:.2f} p95={v['p95_ms']:.2f} max={v['max_ms']:.2f}")


if __name__ == "__main__":
    main()
