"""Prevent the published model speeches from collapsing into one answer type."""

from __future__ import annotations

import re
from collections import Counter

from book_config import ROOT, selected_chapters


def model_choice(week: int) -> str:
    path = ROOT / "book" / "chapters" / f"week{week:02d}.qmd"
    text = path.read_text(encoding="utf-8")
    marker = "## 90초 발언 예시"
    if marker not in text:
        raise SystemExit(f"week{week:02d}: missing 90-second model speech")
    section = text.split(marker, 1)[1]
    section = re.split(r"\n##\s+", section, maxsplit=1)[0]
    match = re.search(r"답안\s*([ABC])", section)
    if not match:
        raise SystemExit(f"week{week:02d}: explicit A/B/C choice missing in model speech")
    return match.group(1)


def main() -> None:
    selected = selected_chapters()
    sequence = [model_choice(week) for week in selected]
    counts = Counter(sequence)
    if counts["A"] < 3 or counts["B"] < 2 or counts["C"] > 14:
        raise SystemExit(f"model-answer distribution is too concentrated: {dict(counts)}")

    longest_c_run = max(
        (len(run) for run in re.findall(r"C+", "".join(sequence))), default=0
    )
    if longest_c_run > 4:
        raise SystemExit(f"too many consecutive C answers: {longest_c_run}")
    print(
        f"PASS: model-answer distribution A={counts['A']}, B={counts['B']}, "
        f"C={counts['C']}; longest C run={longest_c_run}"
    )


if __name__ == "__main__":
    main()
