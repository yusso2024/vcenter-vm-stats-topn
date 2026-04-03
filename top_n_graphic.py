#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


SUPPORTED_METRICS = {"cpu_usage", "memory_usage", "storage_usage"}


def load_stats(path: Path) -> dict[str, dict]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("Stats JSON must be an object of VM name -> stats")
    return data


def filter_rows(data: dict[str, dict], metric: str, prefix: str | None) -> list[tuple[str, float]]:
    rows: list[tuple[str, float]] = []
    for vm_name, stats in data.items():
        if prefix and not vm_name.startswith(prefix):
            continue
        value = stats.get(metric)
        if value is None:
            continue
        rows.append((vm_name, float(value)))
    rows.sort(key=lambda x: x[1], reverse=True)
    return rows


def build_chart(rows: list[tuple[str, float]], metric: str, top_n: int, output: Path, title: str | None) -> None:
    selected = rows[:top_n]
    if not selected:
        raise ValueError("No rows available after filtering")

    names = [name for name, _ in selected]
    values = [value for _, value in selected]

    fig_height = max(6, int(len(selected) * 0.45))
    fig, ax = plt.subplots(figsize=(14, fig_height))
    bars = ax.barh(names, values)
    ax.invert_yaxis()
    ax.set_xlabel(metric)
    ax.set_title(title or f"Top {len(selected)} VMs by {metric}")

    for bar, value in zip(bars, values):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f" {value:.2f}", va="center")

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Top-N VM statistics chart")
    parser.add_argument("--stats", default="data/vm_stats.json", help="Input stats JSON file")
    parser.add_argument("--metric", default="cpu_usage", choices=sorted(SUPPORTED_METRICS), help="Metric to rank")
    parser.add_argument("--top-n", type=int, default=10, help="Number of top VMs")
    parser.add_argument("--prefix", default=None, help="Optional VM name prefix filter (example: FL)")
    parser.add_argument("--output", default="graphics/top_n.png", help="Output PNG path")
    parser.add_argument("--title", default=None, help="Custom chart title")
    args = parser.parse_args()

    if args.top_n <= 0:
        raise ValueError("--top-n must be greater than zero")

    stats = load_stats(Path(args.stats))
    rows = filter_rows(stats, args.metric, args.prefix)
    build_chart(rows, args.metric, args.top_n, Path(args.output), args.title)

    print(f"Generated chart: {args.output} ({args.metric}, top {args.top_n})")


if __name__ == "__main__":
    main()
