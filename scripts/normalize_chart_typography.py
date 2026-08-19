"""Raise small chart type to the A5 print minimum without changing chart data."""

from __future__ import annotations

import re
from pathlib import Path

from book_config import selected_chapters


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "book" / "figures"
MIN_PX = 20.0


def clamp(match: re.Match[str]) -> str:
    prefix, value, suffix = match.groups()
    return f"{prefix}{max(float(value), MIN_PX):g}{suffix}"


def main() -> None:
    changed = 0
    patterns = (
        re.compile(r"(font-size\s*[:=]\s*[\"']?)([0-9.]+)(px)?"),
        re.compile(r"(font\s*:\s*(?:[0-9]+\s+)?)([0-9.]+)(px)"),
    )
    for week in selected_chapters():
        path = FIGURES / f"week{week:02d}.svg"
        original = path.read_text(encoding="utf-8")
        updated = original
        for pattern in patterns:
            updated = pattern.sub(clamp, updated)
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    print(f"normalized_chart_svgs={changed}")


if __name__ == "__main__":
    main()
