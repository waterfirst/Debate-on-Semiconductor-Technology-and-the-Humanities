"""Check that chart text remains legible when 920 px SVGs are printed at A5 width."""

from __future__ import annotations

import re
from pathlib import Path

from book_config import selected_chapters


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "book" / "figures"
MIN_PX = 20.0  # about 7 pt when a 920 px viewBox is printed at 113 mm


def sizes(text: str) -> list[float]:
    matches = re.findall(r"font-size\s*[:=]\s*[\"']?([0-9.]+)", text)
    matches += re.findall(r"font\s*:\s*(?:[0-9]+\s+)?([0-9.]+)px", text)
    return [float(value) for value in matches]


def main() -> None:
    errors: list[str] = []
    for week in selected_chapters():
        path = FIGURES / f"week{week:02d}.svg"
        values = sizes(path.read_text(encoding="utf-8"))
        if not values:
            errors.append(f"week{week:02d}: no explicit SVG type sizes")
        elif min(values) < MIN_PX:
            errors.append(f"week{week:02d}: minimum {min(values):g}px < {MIN_PX:g}px")
    if errors:
        print("CHART TYPOGRAPHY AUDIT FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"PASS: {len(selected_chapters())} published charts use at least {MIN_PX:g}px type")


if __name__ == "__main__":
    main()
