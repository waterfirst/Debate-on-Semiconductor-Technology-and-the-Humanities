"""Build the Kyobo POD grayscale interior with the full colophon on page 2.

The registered 258-page grayscale interior has a blank page 2.  The earlier
Kyobo resubmission artifact contains a complete colophon as its final page.
This script replaces only the blank page, preserving the side, pagination,
trim position, and total page count of every later page.
"""

from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject


ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "book" / "output" / "pdf"
BASE = PDF_DIR / "반도체-면접-왕의-질문에-답하라-본문-A5-흑백.pdf"
DONOR = PDF_DIR / "반도체-면접-왕의-질문에-답하라-본문-A5-교보재제출.pdf"
OUTPUT = PDF_DIR / "반도체-면접-왕의-질문에-답하라-교보재등록용-흑백-판권앞배치.pdf"
ISBN = "979-11-220895-8-5"


def cleaned_colophon(reader: PdfReader):
    page = reader.pages[-1]
    text = page.extract_text() or ""
    required = ["반도체 면접, 왕의 질문에 답하라", "ISBN", ISBN, "스칼라브릿지"]
    missing = [item for item in required if item not in text]
    if missing:
        raise SystemExit(f"donor colophon missing: {missing}")

    # ReportLab put an empty Helvetica selection in this page.  It draws no
    # glyph but makes preflight tools report a non-embedded font.  Remove both
    # the empty command and its unused resource.
    content = page.get_contents().get_data()
    empty_helvetica = b"1 0 0 1 0 0 cm  BT /F1 12 Tf 14.4 TL ET\n"
    content = content.replace(empty_helvetica, b"1 0 0 1 0 0 cm\n")
    cleaned = DecodedStreamObject()
    cleaned.set_data(content)
    page[NameObject("/Contents")] = cleaned
    fonts = page["/Resources"]["/Font"]
    if "/F1" in fonts:
        del fonts["/F1"]
    return page


def main() -> None:
    base = PdfReader(str(BASE))
    donor = PdfReader(str(DONOR))
    if len(base.pages) != 258:
        raise SystemExit(f"expected 258 base pages, found {len(base.pages)}")
    if (base.pages[1].extract_text() or "").strip():
        raise SystemExit("base page 2 is not blank; refusing replacement")

    writer = PdfWriter()
    writer.add_page(base.pages[0])
    writer.add_page(cleaned_colophon(donor))
    for page in base.pages[2:]:
        writer.add_page(page)
    writer.add_metadata(
        {
            "/Title": "반도체 면접, 왕의 질문에 답하라",
            "/Author": "최낙초",
            "/Subject": "교보문고 POD 재등록용 흑백 내지 — 판권 2쪽 앞배치",
        }
    )
    with OUTPUT.open("wb") as handle:
        writer.write(handle)
    print(OUTPUT)


if __name__ == "__main__":
    main()
