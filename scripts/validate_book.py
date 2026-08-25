from pathlib import Path
import re
import sys

from book_config import selected_chapters

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


published = selected_chapters()
chapters = [BOOK / "chapters" / f"week{week:02d}.qmd" for week in published]
missing_chapters = [path.name for path in chapters if not path.exists()]
if missing_chapters:
    fail(f"missing curated chapters: {missing_chapters}")

required = [
    "[오늘의 책문]{.book-question-label}",
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
]
for path in chapters:
    text = path.read_text(encoding="utf-8")
    for heading in required:
        if heading not in text:
            fail(f"{path.name}: missing {heading}")
    if len(re.findall(r"https://", text)) < 1:
        fail(f"{path.name}: missing source URL")
    if text.count("?") + text.count("까") < 4:
        fail(f"{path.name}: too few discussion questions")
    if len(text) < 3000:
        fail(f"{path.name}: manuscript is too short ({len(text)} chars)")
    if len(re.findall(r"^\|\s*\d+\s*\|", text, re.M)) < 3:
        fail(f"{path.name}: missing evidence table")
    if "../figures/week" not in text:
        fail(f"{path.name}: missing chart or decision-flow figure")
    if "../figures/symbols/week" not in text:
        fail(f"{path.name}: missing symbolic illustration")
    if "`결론 → 데이터 2개 → 강한 반론 → 전환 조건`" in text:
        fail(f"{path.name}: Korean response sequence must not use code font")

figures = [BOOK / "figures" / f"week{week:02d}-print.png" for week in published]
symbols = [
    BOOK / "figures" / "symbols" / f"week{week:02d}-symbol-print.png"
    for week in published
]
for asset in (*figures, *symbols):
    if not asset.exists():
        fail(f"missing curated visual asset: {asset.relative_to(ROOT)}")

evidence = ROOT / "data" / "evidence.csv"
if not evidence.exists() or sum(1 for _ in evidence.open(encoding="utf-8-sig")) < 61:
    fail("evidence.csv must contain at least 60 comparison rows")

for needed in [BOOK / "index.qmd", BOOK / "interview-checklist.qmd", ROOT / "PUBLISHING.md", ROOT / "README.md", ROOT / "SKILL.md"]:
    if not needed.exists():
        fail(f"missing {needed.relative_to(ROOT)}")

print(
    f"OK: {len(chapters)} curated chapters, {len(figures)} charts, "
    f"{len(symbols)} illustrations and evidence data passed validation"
)
