from pathlib import Path
import math
import shutil

from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


BOOK = Path(__file__).resolve().parents[1]
COVER = BOOK / "cover"
OUTPUT = BOOK / "output" / "pdf"
TMP = BOOK / "tmp" / "pdfs"

FRONT = COVER / "front-cover-final.png"
BACK = COVER / "back-cover-final.png"
WRAP = COVER / "full-wrap-cover-final.png"
INTERIOR = next((BOOK / "_book").glob("*.pdf"))

OUTPUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)


def image_pdf(image: Path, output: Path, size: tuple[float, float]) -> None:
    page = canvas.Canvas(str(output), pagesize=size)
    page.drawImage(str(image), 0, 0, width=size[0], height=size[1], mask="auto")
    page.showPage()
    page.save()


def print_ready_wrap(input_pdf: Path, output_pdf: Path, size: tuple[float, float]) -> None:
    """Set 3 mm bleed and the centered A5-spread trim area explicitly."""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    writer.add_page(reader.pages[0])
    page = writer.pages[0]
    media = RectangleObject((0, 0, size[0], size[1]))
    trim = RectangleObject((3 * mm, 3 * mm, size[0] - 3 * mm, size[1] - 3 * mm))
    page.mediabox = media
    page.cropbox = media
    page.bleedbox = media
    page.trimbox = trim
    with output_pdf.open("wb") as stream:
        writer.write(stream)


interior_reader = PdfReader(INTERIOR)
interior_pages = len(interior_reader.pages)
sheet_count = math.ceil(interior_pages / 2)
paper_caliper_mm = 0.12  # white woodfree 100 gsm
spine_mm = math.ceil(sheet_count * paper_caliper_mm)
wing_mm = 80

front_pdf = TMP / "front-final.pdf"
back_pdf = TMP / "back-final.pdf"
image_pdf(FRONT, front_pdf, A5)
image_pdf(BACK, back_pdf, A5)

preview_path = OUTPUT / "반도체-면접-왕의-질문에-답하라-최종본.pdf"
writer = PdfWriter()
writer.add_page(PdfReader(front_pdf).pages[0])
for page in interior_reader.pages:
    writer.add_page(page)
writer.add_page(PdfReader(back_pdf).pages[0])
writer.add_metadata(
    {
        "/Title": "반도체 면접, 왕의 질문에 답하라",
        "/Author": "최낙초",
        "/Publisher": "스칼라브릿지",
    }
)
with preview_path.open("wb") as stream:
    writer.write(stream)

interior_path = OUTPUT / "반도체-면접-왕의-질문에-답하라-본문-A5.pdf"
shutil.copy2(INTERIOR, interior_path)

wrap_path = OUTPUT / "반도체-면접-왕의-질문에-답하라-인쇄용-펼침표지.pdf"
# Kyobo wing cover: outer 3 mm + wing + inner 3 mm on both sides.
wrap_size = ((148 + spine_mm + 148 + (wing_mm * 2) + 12) * mm, (210 + 6) * mm)
wrap_raw = TMP / "full-wrap-final-raw.pdf"
image_pdf(WRAP, wrap_raw, wrap_size)
print_ready_wrap(wrap_raw, wrap_path, wrap_size)

print(f"interior={interior_path}")
print(f"preview={preview_path}")
print(f"wrap={wrap_path}")
print(f"interior_pages={interior_pages}")
print(f"preview_pages={len(PdfReader(preview_path).pages)}")
print(f"spine_mm={spine_mm}")
