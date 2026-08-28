"""Build the publication EPUB3, legacy EPUB2, and upload cover.

The curated 19-chapter reading order and metadata come from ``book/_quarto.yml``.
Quarto renders EPUB3 with its ``epub`` target and EPUB2 with ``epub2``.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
BOOK_OUT = BOOK / "_book"
OUTPUT = BOOK / "output" / "epub"
SLUG = "반도체-면접-왕의-질문에-답하라"
EPUB3 = OUTPUT / f"{SLUG}-EPUB3.epub"
EPUB2 = OUTPUT / f"{SLUG}-EPUB2.epub"
CANONICAL = OUTPUT / f"{SLUG}.epub"
COVER_PNG = BOOK / "cover" / "front-cover-final.png"
COVER_JPG = OUTPUT / f"{SLUG}-전자책-표지.jpg"


def find_quarto() -> Path:
    executable = shutil.which("quarto") or shutil.which("quarto.exe")
    if executable:
        return Path(executable)

    windows_fallback = (
        Path.home()
        / "AppData"
        / "Local"
        / "Programs"
        / "Quarto"
        / "bin"
        / "quarto.exe"
    )
    if windows_fallback.exists():
        return windows_fallback
    raise SystemExit("Quarto is required: https://quarto.org/docs/get-started/")


def render(quarto: Path, output_format: str) -> Path:
    subprocess.run(
        [str(quarto), "render", ".", "--to", output_format],
        cwd=BOOK,
        check=True,
    )
    candidates = list(BOOK_OUT.glob("*.epub"))
    if not candidates:
        raise SystemExit(f"Quarto produced no EPUB for {output_format}")
    return max(candidates, key=lambda path: path.stat().st_mtime_ns)


def export_cover() -> None:
    with Image.open(COVER_PNG) as source:
        source.convert("RGB").save(
            COVER_JPG,
            "JPEG",
            quality=95,
            optimize=True,
            dpi=(300, 300),
        )


def main() -> None:
    quarto = find_quarto()
    OUTPUT.mkdir(parents=True, exist_ok=True)

    epub3_source = render(quarto, "epub")
    shutil.copy2(epub3_source, EPUB3)
    shutil.copy2(epub3_source, CANONICAL)

    epub2_source = render(quarto, "epub2")
    shutil.copy2(epub2_source, EPUB2)
    export_cover()

    for path in (EPUB3, EPUB2, CANONICAL, COVER_JPG):
        print(path)


if __name__ == "__main__":
    main()
