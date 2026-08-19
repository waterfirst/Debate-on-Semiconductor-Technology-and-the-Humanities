"""Regenerate selected chart SVG files without overwriting manuscripts."""

import argparse
import re

from enrich_content import CHAPTERS, EVIDENCE, FIGURES, svg_chart, svg_qualitative


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weeks", nargs="*", type=int, help="Only rebuild these weeks")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selected = set(args.weeks or range(1, 31))
    FIGURES.mkdir(parents=True, exist_ok=True)
    written = 0
    for week in sorted(selected):
        manuscript = (CHAPTERS / f"week{week:02d}.qmd").read_text(encoding="utf-8")
        match = re.search(r'^title:\s*["\'](.+?)["\']\s*$', manuscript, re.M)
        if not match:
            raise ValueError(f"missing title for week{week:02d}")
        title = match.group(1)
        evidence = EVIDENCE[week]
        output = FIGURES / f"week{week:02d}.svg"
        output.write_text(
            svg_chart(week, title, evidence["unit"], evidence["chart"])
            if evidence["chart"]
            else svg_qualitative(week, title),
            encoding="utf-8",
        )
        written += 1
    print(f"rendered figure SVGs: {written}")


if __name__ == "__main__":
    main()
