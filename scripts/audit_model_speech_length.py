"""Check that every published model speech fits a practical 90-second range."""

from __future__ import annotations

import re

from book_config import ROOT, selected_chapters


def strip_inline_footnotes(text: str) -> str:
    output: list[str] = []
    index = 0
    while index < len(text):
        if text.startswith("^[", index):
            depth = 1
            index += 2
            while index < len(text) and depth:
                if text[index] == "[":
                    depth += 1
                elif text[index] == "]":
                    depth -= 1
                index += 1
            continue
        output.append(text[index])
        index += 1
    return "".join(output)


def main() -> None:
    failures: list[str] = []
    results: list[str] = []
    for week in selected_chapters():
        path = ROOT / "book" / "chapters" / f"week{week:02d}.qmd"
        text = path.read_text(encoding="utf-8")
        section = text.split("## 90초 발언 예시", 1)[1]
        section = re.split(r"\n##\s+", section, maxsplit=1)[0]
        spoken = strip_inline_footnotes(section)
        syllables = len(re.findall(r"[가-힣]", spoken))
        results.append(f"week{week:02d}={syllables}")
        if not 300 <= syllables <= 450:
            failures.append(f"week{week:02d}: {syllables} Hangul syllables")
    if failures:
        raise SystemExit("model speech length outside 300-450:\n" + "\n".join(failures))
    print("PASS: " + ", ".join(results))


if __name__ == "__main__":
    main()
