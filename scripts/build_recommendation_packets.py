"""Build personalized recommendation-review excerpts from the print-ready A5 PDF."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
BODY = BOOK / "output" / "pdf" / "반도체-면접-왕의-질문에-답하라-본문-A5.pdf"
OUTPUT = BOOK / "output" / "pdf" / "recommendation"
TMP = BOOK / "tmp" / "pdfs" / "recommendation"

FONT_DIR = Path(r"C:\Windows\Fonts")
REGULAR_FONT = FONT_DIR / "KoPubDotumMedium.ttf"
SEMIBOLD_FONT = FONT_DIR / "KoPubDotumBold.ttf"

NAVY = HexColor("#10283F")
ACCENT = HexColor("#A94E32")
CREAM = HexColor("#F6F1E7")
INK = HexColor("#18212B")
MUTED = HexColor("#607080")


@dataclass(frozen=True)
class Packet:
    recipient: str
    affiliation: str
    chapters: tuple[int, int]
    filename: str


PACKETS = (
    Packet(
        recipient="김영철 교수님",
        affiliation="서강대학교 경제학부",
        chapters=(5, 10),
        filename="김영철-교수님-추천사-검토용.pdf",
    ),
    Packet(
        recipient="홍성규 교수님",
        affiliation="동국대학교 화공생물공학과",
        chapters=(4, 22),
        filename="홍성규-교수님-추천사-검토용.pdf",
    ),
    Packet(
        recipient="이승우 교수님",
        affiliation="경희대학교 정보디스플레이학과",
        chapters=(14, 20),
        filename="이승우-교수님-추천사-검토용.pdf",
    ),
    Packet(
        recipient="홍문표 교수님",
        affiliation="고려대학교 반도체물리학부",
        chapters=(13, 15),
        filename="홍문표-교수님-추천사-검토용.pdf",
    ),
)


def normalized(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def qmd_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r'^title:\s*["\'](.+?)["\']\s*$', text, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"No title found in {path}")
    return match.group(1)


def first_page_with(reader: PdfReader, title: str, start: int) -> int:
    needle = normalized(title)
    for page_index in range(start, len(reader.pages)):
        if needle in normalized(reader.pages[page_index].extract_text() or ""):
            return page_index
    raise RuntimeError(f"Could not locate title in PDF: {title!r}")


def locate_sections(reader: PdfReader) -> tuple[dict[int, tuple[int, int]], tuple[int, int], tuple[int, int]]:
    preface_title = qmd_title(BOOK / "index.qmd")
    preface_start = first_page_with(reader, preface_title, 8)

    starts: dict[int, int] = {}
    cursor = preface_start + 1
    for chapter in range(1, 31):
        title = qmd_title(BOOK / "chapters" / f"week{chapter:02d}.qmd")
        starts[chapter] = first_page_with(reader, title, cursor)
        cursor = starts[chapter] + 1

    epilogue_title = qmd_title(BOOK / "epilogue.qmd")
    epilogue_start = first_page_with(reader, epilogue_title, starts[30] + 1)
    checklist_title = qmd_title(BOOK / "interview-checklist.qmd")
    checklist_start = first_page_with(reader, checklist_title, epilogue_start + 1)

    ranges: dict[int, tuple[int, int]] = {}
    for chapter in range(1, 31):
        next_start = starts[chapter + 1] if chapter < 30 else epilogue_start
        ranges[chapter] = (starts[chapter], next_start - 1)

    preface_range = (preface_start, starts[1] - 1)
    epilogue_range = (epilogue_start, checklist_start - 1)
    return ranges, preface_range, epilogue_range


def wrap_lines(text: str, font_name: str, font_size: float, max_width: float) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        if current and pdfmetrics.stringWidth(candidate, font_name, font_size) > max_width:
            lines.append(current.rstrip())
            current = char.lstrip()
        else:
            current = candidate
    if current:
        lines.append(current.rstrip())
    return lines


def draw_paragraph(
    page: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    font_name: str,
    font_size: float,
    leading: float,
    color=INK,
) -> float:
    page.setFillColor(color)
    page.setFont(font_name, font_size)
    for line in wrap_lines(text, font_name, font_size, width):
        page.drawString(x, y, line)
        y -= leading
    return y


def request_cover(packet: Packet, chapter_titles: dict[int, str]) -> PdfReader:
    buffer = io.BytesIO()
    page = canvas.Canvas(buffer, pagesize=A5)
    width, height = A5

    page.setFillColor(CREAM)
    page.rect(0, 0, width, height, stroke=0, fill=1)
    page.setFillColor(NAVY)
    page.rect(0, height - 37 * mm, width, 37 * mm, stroke=0, fill=1)
    page.setFillColor(ACCENT)
    page.rect(18 * mm, height - 37 * mm, 30 * mm, 2.2 * mm, stroke=0, fill=1)

    page.setFillColor(CREAM)
    page.setFont("Pretendard-SemiBold", 10)
    page.drawString(18 * mm, height - 17 * mm, "추천사 검토용 발췌본")
    page.setFont("Pretendard-Regular", 7.8)
    page.drawRightString(width - 18 * mm, height - 17 * mm, "REVIEW COPY")

    y = height - 53 * mm
    page.setFillColor(NAVY)
    page.setFont("Pretendard-Regular", 9.3)
    page.drawString(18 * mm, y, packet.affiliation)
    y -= 9 * mm
    page.setFont("Pretendard-SemiBold", 19)
    page.drawString(18 * mm, y, f"{packet.recipient}께")

    y -= 15 * mm
    page.setFillColor(ACCENT)
    page.setFont("Pretendard-SemiBold", 8.5)
    page.drawString(18 * mm, y, "BOOK TITLE")
    y -= 8 * mm
    page.setFillColor(INK)
    page.setFont("Pretendard-SemiBold", 17)
    page.drawString(18 * mm, y, "반도체 면접, 왕의 질문에 답하라")
    y -= 8.5 * mm
    y = draw_paragraph(
        page,
        "조선의 책문으로 훈련하는 AI·전쟁·환율·공급망 데이터 토론 30",
        18 * mm,
        y,
        width - 36 * mm,
        "Pretendard-Regular",
        9.3,
        13,
        MUTED,
    )

    y -= 7 * mm
    page.setStrokeColor(HexColor("#D7CCBC"))
    page.setFillColor(HexColor("#FBF8F2"))
    box_y = 38 * mm
    box_h = y - box_y + 3 * mm
    page.roundRect(15 * mm, box_y, width - 30 * mm, box_h, 2.5 * mm, stroke=1, fill=1)

    y -= 7 * mm
    page.setFillColor(NAVY)
    page.setFont("Pretendard-SemiBold", 9.4)
    page.drawString(20 * mm, y, "검토 부탁드리는 부분")
    y -= 7 * mm
    items = (
        "서문",
        f"제{packet.chapters[0]}장  {chapter_titles[packet.chapters[0]]}",
        f"제{packet.chapters[1]}장  {chapter_titles[packet.chapters[1]]}",
        "에필로그",
    )
    page.setFont("Pretendard-Regular", 9.1)
    page.setFillColor(INK)
    for item in items:
        page.setFillColor(ACCENT)
        page.circle(21.5 * mm, y + 2.4, 1.1, stroke=0, fill=1)
        page.setFillColor(INK)
        page.drawString(25 * mm, y, item)
        y -= 6.2 * mm

    y -= 2.5 * mm
    request = (
        "교수님의 전문적 견해를 바탕으로, 이 책이 취업을 준비하는 독자에게 주는 가치와 "
        "읽을 만한 이유에 관한 짧은 추천 말씀을 부탁드립니다."
    )
    y = draw_paragraph(
        page,
        request,
        20 * mm,
        y,
        width - 40 * mm,
        "Pretendard-Regular",
        8.8,
        13.5,
        INK,
    )
    y -= 3 * mm
    y = draw_paragraph(
        page,
        "권장 분량 250~500자 · 성명·소속·직함 표기와 책·홍보물 인용 문안은 게재 전 다시 확인드리겠습니다.",
        20 * mm,
        y,
        width - 40 * mm,
        "Pretendard-Regular",
        7.8,
        11.5,
        MUTED,
    )

    page.setFillColor(NAVY)
    page.setFont("Pretendard-SemiBold", 8.8)
    page.drawString(18 * mm, 24 * mm, "최낙초 드림")
    page.setFont("Pretendard-Regular", 7.8)
    page.setFillColor(MUTED)
    page.drawString(18 * mm, 19.5 * mm, "스칼라브릿지 · 검토용 / 외부 배포 금지")

    page.showPage()
    page.save()
    buffer.seek(0)
    return PdfReader(buffer)


def add_range(writer: PdfWriter, reader: PdfReader, page_range: tuple[int, int]) -> None:
    start, end = page_range
    for page_index in range(start, end + 1):
        writer.add_page(reader.pages[page_index])


def main() -> None:
    if not BODY.exists():
        raise FileNotFoundError(BODY)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)

    pdfmetrics.registerFont(TTFont("Pretendard-Regular", str(REGULAR_FONT)))
    pdfmetrics.registerFont(TTFont("Pretendard-SemiBold", str(SEMIBOLD_FONT)))

    reader = PdfReader(BODY)
    chapter_ranges, preface_range, epilogue_range = locate_sections(reader)
    chapter_titles = {
        chapter: qmd_title(BOOK / "chapters" / f"week{chapter:02d}.qmd")
        for chapter in range(1, 31)
    }

    for packet in PACKETS:
        writer = PdfWriter()
        writer.add_page(request_cover(packet, chapter_titles).pages[0])
        add_range(writer, reader, preface_range)
        for chapter in packet.chapters:
            add_range(writer, reader, chapter_ranges[chapter])
        add_range(writer, reader, epilogue_range)

        writer.add_metadata(
            {
                "/Title": f"{packet.recipient} 추천사 검토용 발췌본",
                "/Author": "최낙초",
                "/Subject": "서문, 관련 장 2개, 에필로그",
                "/Creator": "스칼라브릿지",
            }
        )
        target = OUTPUT / packet.filename
        with target.open("wb") as stream:
            writer.write(stream)
        print(
            f"created={target.name.encode('unicode_escape').decode()} "
            f"pages={len(writer.pages)} chapters={packet.chapters}"
        )

    print(f"preface={preface_range} epilogue={epilogue_range}")
    for chapter in sorted({chapter for packet in PACKETS for chapter in packet.chapters}):
        print(f"chapter_{chapter}={chapter_ranges[chapter]}")


if __name__ == "__main__":
    main()
