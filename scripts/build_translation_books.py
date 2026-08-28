from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject


ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS = ROOT / "translations"

BOOKS = {
    "en": {
        "title": "Semiconductor Interviews: Answer the King’s Question",
        "author": "Nakcho Choi",
        "publisher": "Scholar Bridge",
        "lang": "en-US",
        "subject": "Data-driven semiconductor interview and decision-making practice",
        "keywords": "semiconductors, interview, AI, manufacturing, design, supply chain, chaekmun",
        "slug": "semiconductor-interviews-answer-the-kings-question-en",
    },
    "ja": {
        "title": "半導体面接――王の問いに答えよ",
        "author": "チェ・ナクチョ（Nakcho Choi）",
        "publisher": "スカラーブリッジ（Scholar Bridge）",
        "lang": "ja-JP",
        "subject": "半導体産業の面接・意思決定を鍛えるデータ討論",
        "keywords": "半導体, 面接, AI, 製造工程, 設計, サプライチェーン, 策問",
        "slug": "semiconductor-interviews-answer-the-kings-question-ja",
    },
}


def executable(candidates: list[Path], fallback: str) -> Path:
    located = shutil.which(fallback)
    if located:
        return Path(located)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Required executable not found: {fallback}")


def runtime() -> tuple[Path, Path, dict[str, str]]:
    user_profile = Path(os.environ.get("USERPROFILE", Path.home()))
    quarto_override = os.environ.get("QUARTO_BIN")
    node_override = os.environ.get("NODE_BIN")
    quarto = executable(
        [candidate for candidate in [
            Path(quarto_override) if quarto_override else None,
            user_profile / "AppData/Local/Programs/Quarto/bin/quarto.cmd",
            user_profile / "AppData/Local/Programs/Quarto/bin/quarto.exe",
        ] if candidate is not None],
        "quarto",
    )
    node = executable(
        [candidate for candidate in [
            Path(node_override) if node_override else None,
            user_profile / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe",
        ] if candidate is not None],
        "node",
    )
    env = os.environ.copy()
    tex_bin = Path(os.environ.get("TEX_BIN", user_profile / "AppData/Roaming/TinyTeX/bin/windows"))
    search_paths = [str(quarto.parent)]
    if tex_bin.exists():
        search_paths.append(str(tex_bin))
    search_paths.append(env.get("PATH", ""))
    env["PATH"] = os.pathsep.join(search_paths)
    return quarto, node, env


def newest(path: Path, suffix: str) -> Path:
    candidates = sorted(path.glob(f"*{suffix}"), key=lambda item: item.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No {suffix} artifact found in {path}")
    return candidates[0]


def cover_page(cover_png: Path, output_pdf: Path) -> None:
    with Image.open(cover_png) as image:
        image.convert("RGB").save(output_pdf, "PDF", resolution=300.0)


def package_pdf(locale: str, interior: Path, cover_png: Path, final_pdf: Path) -> None:
    metadata = BOOKS[locale]
    with tempfile.TemporaryDirectory(prefix=f"translation-{locale}-", dir=final_pdf.parent) as temp_dir:
        cover_pdf = Path(temp_dir) / "cover.pdf"
        cover_page(cover_png, cover_pdf)
        writer = PdfWriter(clone_from=PdfReader(interior))
        cover = PdfReader(cover_pdf).pages[0]
        writer.insert_page(cover, index=0)
        writer.add_metadata(
            {
                "/Title": metadata["title"],
                "/Author": metadata["author"],
                "/Publisher": metadata["publisher"],
                "/Subject": metadata["subject"],
                "/Keywords": metadata["keywords"],
            }
        )
        writer.root_object[NameObject("/Lang")] = TextStringObject(metadata["lang"])
        with final_pdf.open("wb") as stream:
            writer.write(stream)

    reopened = PdfReader(final_pdf)
    if len(reopened.pages) < 4:
        raise RuntimeError(f"Packaged PDF is unexpectedly short: {final_pdf}")


def build_locale(locale: str, quarto: Path, env: dict[str, str]) -> None:
    metadata = BOOKS[locale]
    project = TRANSLATIONS / locale
    output_epub = project / "output" / "epub"
    output_pdf = project / "output" / "pdf"
    output_cover = project / "output" / "cover"
    for directory in (output_epub, output_pdf, output_cover):
        directory.mkdir(parents=True, exist_ok=True)

    subprocess.run([str(quarto), "render", ".", "--to", "epub"], cwd=project, env=env, check=True)
    rendered_epub = newest(project / "_book", ".epub")
    final_epub = output_epub / f"{metadata['slug']}.epub"
    shutil.copy2(rendered_epub, final_epub)

    subprocess.run([str(quarto), "render", ".", "--to", "pdf"], cwd=project, env=env, check=True)
    rendered_pdf = newest(project / "_book", ".pdf")
    interior_pdf = output_pdf / f"{metadata['slug']}-interior-a5.pdf"
    shutil.copy2(rendered_pdf, interior_pdf)

    cover_png = project / "cover" / f"front-cover-{locale}.png"
    final_cover = output_cover / f"{metadata['slug']}-cover.png"
    shutil.copy2(cover_png, final_cover)
    final_pdf = output_pdf / f"{metadata['slug']}.pdf"
    package_pdf(locale, interior_pdf, cover_png, final_pdf)

    print(f"{locale}_epub={final_epub}")
    print(f"{locale}_pdf={final_pdf}")
    print(f"{locale}_cover={final_cover}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build localized EPUB and A5 PDF editions.")
    parser.add_argument(
        "--locale",
        action="append",
        choices=sorted(BOOKS),
        help="Build one locale. Repeat to build more than one; default builds all locales.",
    )
    args = parser.parse_args()
    quarto, node, env = runtime()
    subprocess.run([str(node), str(ROOT / "scripts/render_translation_assets.mjs")], cwd=ROOT, env=env, check=True)
    for locale in args.locale or BOOKS:
        build_locale(locale, quarto, env)


if __name__ == "__main__":
    main()
