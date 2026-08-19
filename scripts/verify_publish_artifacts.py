from __future__ import annotations

import math
from pathlib import Path
from zipfile import ZipFile

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "book" / "output"
PDF = OUTPUT / "pdf"
TITLE_SLUG = "반도체-면접-왕의-질문에-답하라"
EPUB = OUTPUT / "epub" / f"{TITLE_SLUG}.epub"
INTERIOR = PDF / f"{TITLE_SLUG}-본문-A5.pdf"
PREVIEW = PDF / f"{TITLE_SLUG}-최종본.pdf"
WRAP = PDF / f"{TITLE_SLUG}-인쇄용-펼침표지.pdf"

PT_PER_MM = 72 / 25.4


def size_mm(page) -> tuple[float, float]:
    return float(page.mediabox.width) / PT_PER_MM, float(page.mediabox.height) / PT_PER_MM


def assert_close(actual: float, expected: float, tolerance: float = 0.2) -> None:
    assert abs(actual - expected) <= tolerance, f"expected {expected}, got {actual:.3f}"


interior = PdfReader(INTERIOR)
preview = PdfReader(PREVIEW)
wrap = PdfReader(WRAP)

assert 220 <= len(interior.pages) < 290, "interior PDF is outside the curated 220–289 page target"
assert len(interior.pages) % 2 == 0, "interior PDF must have an even page count"
assert len(preview.pages) == len(interior.pages) + 2
assert len(wrap.pages) == 1

interior_width, interior_height = size_mm(interior.pages[0])
assert_close(interior_width, 148)
assert_close(interior_height, 210)

sheet_count = math.ceil(len(interior.pages) / 2)
spine_mm = math.ceil(sheet_count * 0.12)
expected_wrap_width = 148 + spine_mm + 148 + 80 * 2 + 12
wrap_width, wrap_height = size_mm(wrap.pages[0])
assert_close(wrap_width, expected_wrap_width)
assert_close(wrap_height, 216)

wrap_page = wrap.pages[0]
trim_width = float(wrap_page.trimbox.width) / PT_PER_MM
trim_height = float(wrap_page.trimbox.height) / PT_PER_MM
assert_close(trim_width, wrap_width - 6)
assert_close(trim_height, wrap_height - 6)

publisher_pages = []
for page_number, page in enumerate(interior.pages, start=1):
    if "Scholar Bridge" in (page.extract_text() or ""):
        publisher_pages.append(page_number)
assert publisher_pages, "Scholar Bridge publisher text is missing from the interior PDF"

publisher = "스칼라브릿지(Scholar Bridge)"
assert preview.metadata.get("/Publisher") == publisher

with ZipFile(EPUB) as archive:
    package_name = next(name for name in archive.namelist() if name.endswith(".opf"))
    package = archive.read(package_name).decode("utf-8")
assert f"<dc:publisher>{publisher}</dc:publisher>" in package

print(f"interior_pages={len(interior.pages)} size={interior_width:.0f}x{interior_height:.0f}mm")
print(f"preview_pages={len(preview.pages)} publisher={preview.metadata.get('/Publisher')}")
print(f"spine={spine_mm}mm")
print(f"wrap_pages={len(wrap.pages)} size={wrap_width:.0f}x{wrap_height:.0f}mm trim_inset=3mm")
print(f"publisher_text_pages={publisher_pages}")
print(f"epub_publisher={publisher}")
print("verification=PASS")
