"""Build a Letuin review PDF with the preface, contents, and two sample chapters."""

from __future__ import annotations

import io
import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from book_config import display_number, selected_chapters


ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
SOURCE = BOOK / "output" / "pdf" / "반도체-면접-왕의-질문에-답하라-본문-A5.pdf"
OUTPUT = BOOK / "output" / "pdf" / "렛유인-검토용-서문-목차.pdf"
SAMPLE_CHAPTERS = (7, 9)

FONT_DIR = Path(r"C:\Windows\Fonts")
REGULAR_FONT = FONT_DIR / "KoPubDotumMedium.ttf"
SEMIBOLD_FONT = FONT_DIR / "KoPubDotumBold.ttf"

NAVY = HexColor("#10283F")
ACCENT = HexColor("#A94E32")
CREAM = HexColor("#F6F1E7")
INK = HexColor("#18212B")
MUTED = HexColor("#607080")


def normalized(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def first_page_with(reader: PdfReader, needle: str, start: int = 0) -> int:
    target = normalized(needle)
    for index in range(start, len(reader.pages)):
        if target in normalized(reader.pages[index].extract_text() or ""):
            return index
    raise RuntimeError(f"Could not locate section in source PDF: {needle}")


def qmd_title(chapter: int) -> str:
    text = (BOOK / "chapters" / f"week{chapter:02d}.qmd").read_text(encoding="utf-8")
    match = re.search(r'^title:\s*["\'](.+?)["\']\s*$', text, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not read chapter title: week{chapter:02d}.qmd")
    return match.group(1)


def chapter_ranges(reader: PdfReader, start: int) -> dict[int, tuple[int, int]]:
    published = selected_chapters()
    starts: dict[int, int] = {}
    cursor = start
    for chapter in published:
        starts[chapter] = first_page_with(reader, qmd_title(chapter), cursor)
        cursor = starts[chapter] + 1

    epilogue_start = first_page_with(reader, "에필로그 — 데이터가 문장이 되는 순간", cursor)
    return {
        chapter: (
            starts[chapter],
            starts[published[index + 1]] - 1
            if index + 1 < len(published)
            else epilogue_start - 1,
        )
        for index, chapter in enumerate(published)
    }


def toc_start_page(reader: PdfReader, preface_start: int) -> int:
    for index in range(preface_start):
        text = normalized(reader.pages[index].extract_text() or "")
        if "차례" in text or "목차" in text:
            return index

    chapter_markers = ("전쟁은인류를진보", "미국의수출통제", "두생산거점")
    for index in range(preface_start):
        text = normalized(reader.pages[index].extract_text() or "")
        if sum(marker in text for marker in chapter_markers) >= 2:
            return index
    raise RuntimeError("Could not locate the table of contents in source PDF")


def cover_page() -> PdfReader:
    buffer = io.BytesIO()
    page = canvas.Canvas(buffer, pagesize=A5)
    width, height = A5

    page.setFillColor(CREAM)
    page.rect(0, 0, width, height, stroke=0, fill=1)
    page.setFillColor(NAVY)
    page.rect(0, height - 43 * mm, width, 43 * mm, stroke=0, fill=1)
    page.setFillColor(ACCENT)
    page.rect(18 * mm, height - 43 * mm, 31 * mm, 2.2 * mm, stroke=0, fill=1)

    page.setFillColor(CREAM)
    page.setFont("Review-Semibold", 10)
    page.drawString(18 * mm, height - 18 * mm, "렛유인 검토용 자료")
    page.setFont("Review-Regular", 7.6)
    page.drawRightString(width - 18 * mm, height - 18 * mm, "PREFACE · CONTENTS · 2 CHAPTERS")

    y = height - 67 * mm
    page.setFillColor(NAVY)
    page.setFont("Review-Semibold", 20)
    page.drawString(18 * mm, y, "반도체 면접,")
    y -= 12 * mm
    page.drawString(18 * mm, y, "왕의 질문에 답하라")

    y -= 15 * mm
    page.setFillColor(MUTED)
    page.setFont("Review-Regular", 9.2)
    page.drawString(18 * mm, y, "조선의 책문으로 훈련하는")
    y -= 6 * mm
    page.drawString(18 * mm, y, "AI·공정·설계·공급망 데이터 토론")

    box_y = 40 * mm
    box_h = 52 * mm
    page.setFillColor(HexColor("#FBF8F2"))
    page.setStrokeColor(HexColor("#D7CCBC"))
    page.roundRect(16 * mm, box_y, width - 32 * mm, box_h, 2.5 * mm, stroke=1, fill=1)
    page.setFillColor(NAVY)
    page.setFont("Review-Semibold", 10)
    page.drawString(21 * mm, box_y + 40 * mm, "수록 내용")
    page.setFillColor(INK)
    page.setFont("Review-Regular", 9.2)
    page.drawString(21 * mm, box_y + 30 * mm, "01  서문")
    page.drawString(21 * mm, box_y + 22 * mm, "02  목차")
    page.setFont("Review-Regular", 8.4)
    page.drawString(21 * mm, box_y + 14 * mm, "03  제1장  AI 호황의 이익은 누구의 몫인가")
    page.drawString(21 * mm, box_y + 6 * mm, "04  제6장  예지보전 경고에 장비를 세울 것인가")

    page.setFillColor(MUTED)
    page.setFont("Review-Regular", 7.6)
    page.drawString(18 * mm, 23 * mm, "내용 검토 및 협업 논의를 위한 제한 배포본입니다.")
    page.drawString(18 * mm, 18 * mm, "저자명과 작성일은 검토용 표지에서 생략했습니다.")

    page.showPage()
    page.save()
    buffer.seek(0)
    return PdfReader(buffer)


def add_nonblank_range(writer: PdfWriter, reader: PdfReader, start: int, end: int) -> None:
    for index in range(start, end + 1):
        if normalized(reader.pages[index].extract_text() or ""):
            writer.add_page(reader.pages[index])


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    if not REGULAR_FONT.exists() or not SEMIBOLD_FONT.exists():
        raise FileNotFoundError("KoPubDotum fonts are required")

    pdfmetrics.registerFont(TTFont("Review-Regular", str(REGULAR_FONT)))
    pdfmetrics.registerFont(TTFont("Review-Semibold", str(SEMIBOLD_FONT)))

    reader = PdfReader(SOURCE)
    # The preface title also appears in the TOC, so anchor on its opening sentence.
    preface_start = first_page_with(
        reader, "조선의 과거시험에는 낯선 이름의 문제가 있었습니다"
    )
    copyright_start = first_page_with(reader, "판권", preface_start + 1)
    toc_start = toc_start_page(reader, preface_start)
    toc_end = preface_start - 1
    ranges = chapter_ranges(reader, copyright_start + 1)

    writer = PdfWriter()
    writer.add_page(cover_page().pages[0])
    add_nonblank_range(writer, reader, preface_start, copyright_start - 1)
    add_nonblank_range(writer, reader, toc_start, toc_end)
    for chapter in SAMPLE_CHAPTERS:
        add_nonblank_range(writer, reader, *ranges[chapter])
    writer.add_metadata(
        {
            "/Title": "렛유인 검토용 - 반도체 면접, 왕의 질문에 답하라",
            "/Subject": "서문·목차·대표 장 2편 검토용 발췌본",
            "/Creator": "스칼라브릿지",
        }
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("wb") as stream:
        writer.write(stream)

    print(
        f"created={OUTPUT.name.encode('unicode_escape').decode()} "
        f"pages={len(writer.pages)} preface={preface_start}:{copyright_start - 1} "
        f"toc={toc_start}:{toc_end} "
        f"samples={[(display_number(chapter), ranges[chapter]) for chapter in SAMPLE_CHAPTERS]}"
    )


if __name__ == "__main__":
    main()
