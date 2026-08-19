"""Portable structural audit for a Quarto book project."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


CHAPTER_LINE = re.compile(r"^\s*-\s+([^#]+\.qmd)\s*$")
URL = re.compile(r"https?://")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", nargs="?", default=".")
    parser.add_argument("--require-sections", nargs="*", default=[])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.project).resolve()
    config = root / "_quarto.yml"
    if not config.exists():
        raise SystemExit(f"missing {config}")

    chapter_paths: list[Path] = []
    for line in config.read_text(encoding="utf-8").splitlines():
        match = CHAPTER_LINE.match(line)
        if match:
            chapter_paths.append(root / match.group(1).strip())

    failures: list[str] = []
    seen_titles: dict[str, Path] = {}
    for chapter in chapter_paths:
        if not chapter.exists():
            failures.append(f"missing chapter: {chapter}")
            continue
        text = chapter.read_text(encoding="utf-8")
        title_match = re.search(
            r'^title:\s*(?:["\'](.+?)["\']|([^#\r\n]+?))\s*$', text, re.MULTILINE
        )
        if not title_match and chapter.parent.name == "chapters":
            failures.append(f"missing YAML title: {chapter}")
        elif title_match:
            title = (title_match.group(1) or title_match.group(2)).strip()
            if title in seen_titles:
                failures.append(f"duplicate title: {title} ({seen_titles[title]}, {chapter})")
            seen_titles[title] = chapter
        for heading in args.require_sections:
            if f"## {heading}" not in text:
                failures.append(f"missing section '{heading}': {chapter}")
        if "fig-alt=" not in text and re.search(r"!\[[^\]]*\]\([^)]+\)", text):
            failures.append(f"image without explicit fig-alt: {chapter}")
        if "## 출처" in text and not URL.search(text.split("## 출처", 1)[1]):
            failures.append(f"source section without direct URL: {chapter}")

    if failures:
        print("FAIL")
        print("\n".join(f"- {item}" for item in failures))
        raise SystemExit(1)
    print(f"PASS: {len(chapter_paths)} qmd files, {len(seen_titles)} unique YAML titles")


if __name__ == "__main__":
    main()
