"""Fail-fast structural and editorial checks for the curated manuscript."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from book_config import selected_chapters


ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "book" / "chapters"
REQUIRED = (
    "## 왜 지금 이 질문인가",
    "## 데이터로 보기",
    "## 대립 답안",
    "## AI 조사 설계",
    "### AI에게 물어볼 프롬프트",
    "### 데이터 취득",
    "### 정보 판정",
    "### 토론의 핵심",
    "## 사례형 토론",
    "## 90초 발언 예시",
    "## 꼬리 질문",
    "## 출처",
)
FORBIDDEN = (
    "공급망의 비용은 구매팀만",
    "첫 번째 숫자는 문제의 규모를",
    "downstream",
    "override",
    "도달기간를",
    "오탐를",
    "중단가",
    "□",
)
PLAIN_FORMULA_PATTERNS = (
    re.compile(r"(?<!\$)\^\{?"),
    re.compile(r"×"),
    re.compile(r"`[^`]*(?:=|×|÷|\^|≈)[^`]*`"),
    re.compile(r"\b\d+(?:\.\d+)?\s*[×÷]\s*\d+(?:\.\d+)?\s*(?:=|≈)"),
    re.compile(r"\bP\s*/\s*\d"),
    re.compile(r"\b\d+(?:\.\d+)?\s*/\s*\([^)]*\)"),
    re.compile(r"\b\d+(?:\.\d+)?\s*/\s*\d+(?:\.\d+)?\s*≈"),
)


def main() -> None:
    errors: list[str] = []
    titles: list[str] = []
    questions: list[str] = []
    long_paragraphs: list[tuple[str, int]] = []

    published = selected_chapters()
    for week in published:
        path = CHAPTERS / f"week{week:02d}.qmd"
        if not path.exists():
            errors.append(f"week{week:02d}: file missing")
            continue
        text = path.read_text(encoding="utf-8")
        title = re.search(r'^title:\s*["\'](.+?)["\']\s*$', text, re.M)
        question = re.search(r'^description:\s*["\'](.+?)["\']\s*$', text, re.M)
        if not title or not question:
            errors.append(f"week{week:02d}: YAML title/description missing")
            continue
        titles.append(title.group(1))
        questions.append(question.group(1))
        if re.match(r"^\d+[.\s]", title.group(1)):
            errors.append(f"week{week:02d}: title has manual chapter number")
        for heading in REQUIRED:
            if heading not in text:
                errors.append(f"week{week:02d}: missing {heading}")
        if "{.book-question}" not in text or "book-question-image" not in text:
            errors.append(f"week{week:02d}: book-question box/image missing")
        # 한자에 별도 Quarto 클래스를 붙이지 않은 장도 있으므로, 각주 안의
        # CJK 통합한자 자체를 확인한다. `.hanja` 유무만 검사하면 정상 원고를
        # 누락으로 잘못 판정한다.
        if not re.search(r"\^\[[^\]]*[\u3400-\u9fff][^\]]*\]", text, re.DOTALL):
            errors.append(f"week{week:02d}: Hanja footnote missing")
        if f"week{week:02d}-print.png" not in text:
            errors.append(f"week{week:02d}: evidence figure missing")
        if f"week{week:02d}-symbol-print.png" not in text:
            errors.append(f"week{week:02d}: symbolic illustration missing")
        if text.count("http") < 3:
            errors.append(f"week{week:02d}: fewer than three source URLs")
        if len(re.findall(r"^\|\s*\d+\s*\|", text, re.M)) < 3:
            errors.append(f"week{week:02d}: fewer than three evidence rows")
        if len(re.findall(r"^- .+\?\s*$", text, re.M)) < 6:
            errors.append(f"week{week:02d}: fewer than six chapter-specific questions")
        for phrase in FORBIDDEN:
            if phrase in text:
                errors.append(f"week{week:02d}: forbidden phrase {phrase!r}")
        if week == 12:
            required_abbreviation_notes = (
                "UCIe^[UCIe는 **Universal Chiplet Interconnect Express**",
                "PHY^[PHY는 **Physical Layer**",
                "DFx^[DFx는 **Design for X**",
            )
            for marker in required_abbreviation_notes:
                if marker not in text:
                    errors.append(
                        f"week12: missing first-use abbreviation footnote {marker!r}"
                    )
        for line_number, line in enumerate(text.splitlines(), start=1):
            # 올바른 인라인·블록 수식, URL, Pandoc 각주 표시는 검사 대상에서 뺀다.
            plain = re.sub(r"\$[^$]*\$", "", line)
            plain = re.sub(r"https?://\S+", "", plain).replace("^[", "")
            if any(pattern.search(plain) for pattern in PLAIN_FORMULA_PATTERNS):
                errors.append(
                    f"week{week:02d}:{line_number}: formula needs $...$ delimiters"
                )
        for paragraph in re.split(r"\n\s*\n", text):
            normalized = re.sub(r"\s+", " ", paragraph).strip()
            if (
                len(normalized) >= 120
                and not normalized.startswith(("|", "- [", "![]", "> 기준일"))
            ):
                long_paragraphs.append((normalized, week))

    for label, values in (("title", titles), ("question", questions)):
        duplicates = [value for value, count in Counter(values).items() if count > 1]
        if duplicates:
            errors.append(f"duplicate {label}: {duplicates}")
    grouped_paragraphs: dict[str, list[int]] = {}
    for paragraph, week in long_paragraphs:
        grouped_paragraphs.setdefault(paragraph, []).append(week)
    for paragraph, weeks in grouped_paragraphs.items():
        unique_weeks = sorted(set(weeks))
        if len(unique_weeks) > 1:
            errors.append(
                "duplicate long paragraph in "
                + ", ".join(f"week{week:02d}" for week in unique_weeks)
                + f": {paragraph[:80]}…"
            )

    if errors:
        print("MANUSCRIPT AUDIT FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(
        f"MANUSCRIPT AUDIT PASSED: {len(published)} curated chapters, required sections, "
        "footnotes, figures, sources, formulas, and unique questions"
    )


if __name__ == "__main__":
    main()
