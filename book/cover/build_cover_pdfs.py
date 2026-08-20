from __future__ import annotations

import argparse
import math
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


BOOK = Path(__file__).resolve().parents[1]
COVER = BOOK / "cover"
OUTPUT = BOOK / "output" / "pdf"
TMP = BOOK / "tmp" / "pdfs"
TITLE_SLUG = "반도체-면접-왕의-질문에-답하라"

FRONT = COVER / "front-cover-final.png"
BACK = COVER / "back-cover-final.png"
WRAP = COVER / "full-wrap-cover-final.png"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="A5 본문·날개 표지 PDF를 조립합니다.")
    parser.add_argument(
        "--spine-mm",
        type=float,
        help="인쇄소가 확정한 책등 폭. 생략하면 백색모조 100g 0.12mm/장으로 계산합니다.",
    )
    parser.add_argument("--wing-mm", type=float, default=80.0, help="한쪽 날개 폭")
    parser.add_argument(
        "--cmyk-profile",
        type=Path,
        help="JapanColor2001Coated.icc 경로. 생략하면 환경변수와 표준 설치 위치를 확인합니다.",
    )
    return parser.parse_args()


def image_pdf(image: Path, output: Path, size: tuple[float, float]) -> None:
    page = canvas.Canvas(str(output), pagesize=size)
    page.drawImage(str(image), 0, 0, width=size[0], height=size[1], mask="auto")
    page.showPage()
    page.save()


def print_ready_wrap(input_pdf: Path, output_pdf: Path, size: tuple[float, float]) -> None:
    """바깥쪽 3mm 재단 여유와 최종 펼침면 TrimBox를 명시합니다."""
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



def resolve_cmyk_profile(explicit: Path | None) -> tuple[Path, bool]:
    candidates = [
        explicit,
        Path(os.environ["JAPAN_COLOR_2001_COATED_ICC"])
        if os.environ.get("JAPAN_COLOR_2001_COATED_ICC")
        else None,
        Path(r"C:\\Windows\\System32\\spool\\drivers\\color\\JapanColor2001Coated.icc"),
        Path("/usr/share/color/icc/JapanColor2001Coated.icc"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate, True

    generic = Path("/usr/share/color/icc/ghostscript/default_cmyk.icc")
    if generic.is_file():
        return generic, False
    raise FileNotFoundError(
        "CMYK ICC 프로필이 없습니다. --cmyk-profile 또는 "
        "JAPAN_COLOR_2001_COATED_ICC로 JapanColor2001Coated.icc를 지정하십시오."
    )


def convert_cover_to_cmyk(input_pdf: Path, output_pdf: Path, profile: Path) -> None:
    ghostscript = shutil.which("gswin64c") or shutil.which("gs")
    if not ghostscript:
        raise FileNotFoundError("Ghostscript(gswin64c 또는 gs)가 필요합니다.")
    temp_dir = TMP / "ghostscript"
    temp_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["TMPDIR"] = str(temp_dir)
    subprocess.run(
        [
            ghostscript,
            "-q",
            "-dSAFER",
            "-dBATCH",
            "-dNOPAUSE",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.6",
            "-dPDFSETTINGS=/prepress",
            "-sColorConversionStrategy=CMYK",
            "-sProcessColorModel=DeviceCMYK",
            "-dOverrideICC",
            f"-sOutputICCProfile={profile}",
            f"-sOutputFile={output_pdf}",
            str(input_pdf),
        ],
        check=True,
        env=env,
    )

def main() -> None:
    args = parse_args()
    output_candidates = sorted((BOOK / "_book").glob("*.pdf"))
    if not output_candidates:
        raise FileNotFoundError("먼저 Quarto PDF를 렌더링하십시오: book/_book/*.pdf")
    interior_source = output_candidates[0]

    OUTPUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)

    interior_reader = PdfReader(interior_source)
    interior_pages = len(interior_reader.pages)
    sheet_count = math.ceil(interior_pages / 2)
    calculated_spine = math.ceil(sheet_count * 0.12)  # 백색모조 100g의 제작용 보수 추정치
    spine_mm = args.spine_mm if args.spine_mm is not None else calculated_spine
    wing_mm = args.wing_mm

    front_pdf = TMP / "front-final.pdf"
    back_pdf = TMP / "back-final.pdf"
    image_pdf(FRONT, front_pdf, A5)
    image_pdf(BACK, back_pdf, A5)

    preview_path = OUTPUT / f"{TITLE_SLUG}-최종본.pdf"
    writer = PdfWriter()
    writer.add_page(PdfReader(front_pdf).pages[0])
    for page in interior_reader.pages:
        writer.add_page(page)
    writer.add_page(PdfReader(back_pdf).pages[0])
    writer.add_metadata(
        {
            "/Title": "반도체 면접, 왕의 질문에 답하라",
            "/Author": "최낙초",
            "/Publisher": "스칼라브릿지(Scholar Bridge)",
        }
    )
    with preview_path.open("wb") as stream:
        writer.write(stream)

    interior_path = OUTPUT / f"{TITLE_SLUG}-본문-A5.pdf"
    shutil.copy2(interior_source, interior_path)

    wrap_path = OUTPUT / f"{TITLE_SLUG}-인쇄용-펼침표지.pdf"
    # 바깥 3mm + 80mm 날개 + 3mm 접지 안전폭 + 뒤표지 + 책등 +
    # 앞표지 + 3mm 접지 안전폭 + 80mm 날개 + 바깥 3mm
    wrap_width_mm = 148 + spine_mm + 148 + (wing_mm * 2) + 12
    wrap_size = (wrap_width_mm * mm, 216 * mm)
    with Image.open(WRAP) as wrap_image:
        actual_ratio = wrap_image.width / wrap_image.height
    expected_ratio = wrap_width_mm / 216
    if abs(actual_ratio - expected_ratio) > 0.002:
        raise ValueError(
            "펼침표지 PNG와 현재 본문 쪽수의 비율이 다릅니다. "
            "책등 폭에 맞춰 full-wrap-layout-final.svg를 다시 렌더링하십시오."
        )
    wrap_raw = TMP / "full-wrap-final-raw.pdf"
    wrap_print_rgb = TMP / "full-wrap-final-print-rgb.pdf"
    image_pdf(WRAP, wrap_raw, wrap_size)
    print_ready_wrap(wrap_raw, wrap_print_rgb, wrap_size)
    cmyk_profile, exact_japan_profile = resolve_cmyk_profile(args.cmyk_profile)
    convert_cover_to_cmyk(wrap_print_rgb, wrap_path, cmyk_profile)

    print(f"interior={interior_path}")
    print(f"preview={preview_path}")
    print(f"wrap={wrap_path}")
    print(f"interior_pages={interior_pages}")
    print(f"preview_pages={len(PdfReader(preview_path).pages)}")
    print(f"spine_mm={spine_mm:g}")
    print(f"wrap_mm={wrap_width_mm:g}x216")
    print(f"cmyk_profile={cmyk_profile}")
    print(f"japan_color_2001_coated={exact_japan_profile}")


if __name__ == "__main__":
    main()
