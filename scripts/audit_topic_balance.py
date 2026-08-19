"""Audit the published table of contents for engineering-job relevance.

The mapping is an editorial classification, not a claim about the only way to
read a chapter.  It exists to prevent a future rebuild from drifting back to a
book dominated by planning, finance, or general-management questions.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from book_config import BOOK, selected_chapters


DIRECT_ENGINEERING = {
    3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 21, 22, 24, 25, 26, 28, 30
}

DOMAINS = {
    "research": {5, 10, 11, 13, 24},
    "process": {4, 8, 9, 13, 15, 19, 21},
    "design": {12, 25, 30},
    "equipment": {6, 15},
    "infrastructure": {3, 19, 22, 26},
    "security_and_talent": {2, 18, 24, 28},
    "organization": {7, 14, 21, 24},
}


def chapter_title(chapter_id: int) -> str:
    path = BOOK / "chapters" / f"week{chapter_id:02d}.qmd"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("title:"):
            return line.split(":", 1)[1].strip().strip('"')
    raise ValueError(f"missing YAML title: {path}")


def main() -> None:
    selected = selected_chapters()
    selected_set = set(selected)
    direct = selected_set & DIRECT_ENGINEERING
    if len(selected) != 22:
        raise SystemExit(f"expected 22 published chapters, found {len(selected)}")
    if len(direct) < 19:
        raise SystemExit(
            f"engineering/workplace relevance fell below target: {len(direct)}/22"
        )

    coverage = Counter()
    for domain, members in DOMAINS.items():
        coverage[domain] = len(selected_set & members)
        if coverage[domain] == 0:
            raise SystemExit(f"missing editorial domain: {domain}")

    titles = [chapter_title(chapter_id) for chapter_id in selected]
    if len(titles) != len(set(titles)):
        raise SystemExit("duplicate published chapter titles")

    print(f"PASS: {len(direct)}/22 chapters are direct engineering/workplace judgments")
    print("domain coverage: " + ", ".join(f"{k}={v}" for k, v in coverage.items()))
    for number, (chapter_id, title) in enumerate(zip(selected, titles), 1):
        marker = "engineering" if chapter_id in DIRECT_ENGINEERING else "current-affairs"
        print(f"{number:02d}. week{chapter_id:02d} [{marker}] {title}")


if __name__ == "__main__":
    main()
