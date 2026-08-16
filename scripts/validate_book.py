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

required = ["## 오늘의 책문", "## 데이터 렌즈", "## 대립 답안", "## 판정 조건", "## 꼬리 질문", "## 출처"]
for path in chapters:
    text = path.read_text(encoding="utf-8")
    for heading in required:
        if heading not in text:
            fail(f"{path.name}: missing {heading}")
    if len(re.findall(r"https://", text)) < 1:
        fail(f"{path.name}: missing source URL")
    if text.count("?") + text.count("까") < 4:
        fail(f"{path.name}: too few discussion questions")

for needed in [BOOK / "index.qmd", BOOK / "publishing-guide.qmd", ROOT / "PUBLISHING.md"]:
    if not needed.exists():
        fail(f"missing {needed.relative_to(ROOT)}")

print("OK: 30 chapters and publishing files passed structural validation")

