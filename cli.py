"""Command-line interface."""
from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .core import GitError, load_commits, summarize


def bar(value: int, maximum: int, width: int = 24) -> str:
    return "█" * (round(value / maximum * width) if maximum else 0)


def render(s: dict) -> str:
    lines = [f"Commits analysed: {s['total_commits']}", f"Bus factor: {s['bus_factor']}", ""]
    lines.append("Top authors")
    top_n = max((n for _, n in s["authors"]), default=0)
    for name, n in s["authors"][:10]:
        lines.append(f"  {name:<22} {n:>5}  {bar(n, top_n)}")
    lines += ["", "Activity by weekday"]
    peak = max(s["weekdays"].values(), default=0)
    for day, n in s["weekdays"].items():
        lines.append(f"  {day}  {n:>5}  {bar(n, peak)}")
    lines += ["", "Hotspot files"]
    for path, n in s["hotspots"]:
        lines.append(f"  {n:>5}  {path}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="repo-pulse", description="Health stats for a git repo.")
    p.add_argument("path", nargs="?", default=".", help="path to a git repository")
    p.add_argument("--since", help='only commits after this date, e.g. "6 months ago"')
    p.add_argument("--top", type=int, default=10, help="number of hotspot files to show")
    p.add_argument("--json", action="store_true", help="print machine-readable JSON")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = p.parse_args(argv)

    try:
        summary = summarize(load_commits(args.path, args.since), args.top)
    except GitError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2) if args.json else render(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
