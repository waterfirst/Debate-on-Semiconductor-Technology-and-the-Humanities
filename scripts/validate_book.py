from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


chapters = sorted((BOOK / "chapters").glob("week*.qmd"))
if len(chapters) != 30:
    fail(f"expected 30 chapters, found {len(chapters)}")

required = [
    "[오늘의 책문]{.book-question-label}",
    "## 데이터 렌즈",
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

figures = sorted((BOOK / "figures").glob("week*-print.png"))
symbols = sorted((BOOK / "figures" / "symbols").glob("week*-symbol-print.png"))
if len(figures) != 30:
    fail(f"expected 30 data charts, found {len(figures)}")
if len(symbols) != 30:
    fail(f"expected 30 symbolic illustrations, found {len(symbols)}")

evidence = ROOT / "data" / "evidence.csv"
if not evidence.exists() or sum(1 for _ in evidence.open(encoding="utf-8-sig")) < 61:
    fail("evidence.csv must contain at least 60 comparison rows")

for needed in [BOOK / "index.qmd", BOOK / "interview-checklist.qmd", ROOT / "PUBLISHING.md", ROOT / "README.md", ROOT / "SKILL.md"]:
    if not needed.exists():
        fail(f"missing {needed.relative_to(ROOT)}")

print(f"OK: 30 chapters, {len(figures)} charts, {len(symbols)} illustrations and evidence data passed validation")
