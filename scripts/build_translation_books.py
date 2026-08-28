from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject
import yaml


ROOT = Path(__file__).resolve().parents[1]
TRANSLATIONS = ROOT / "translations"
DC_NS = "http://purl.org/dc/elements/1.1/"
SLUGS = {
    "en": "semiconductor-interviews-answer-the-kings-question-en",
    "ja": "semiconductor-interviews-answer-the-kings-question-ja",
}
METADATA_FIELDS = ("title", "subtitle", "author", "publisher", "lang", "description", "subject", "keywords", "rights")


def load_book_metadata(locale: str) -> dict[str, object]:
    source = TRANSLATIONS / locale / "_quarto.yml"
    loaded = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise RuntimeError(f"Invalid Quarto metadata file: {source}")
    metadata = {field: loaded.get(field) for field in METADATA_FIELDS}
    missing = [field for field, value in metadata.items() if value in (None, "", [])]
    if missing:
        raise RuntimeError(f"Missing metadata in {source}: {', '.join(missing)}")
    if not isinstance(metadata["keywords"], list) or not all(isinstance(value, str) for value in metadata["keywords"]):
        raise RuntimeError(f"keywords must be a list of strings in {source}")

    book = loaded.get("book")
    if not isinstance(book, dict):
        raise RuntimeError(f"Missing book metadata in {source}")
    for field in ("title", "subtitle", "author"):
        if book.get(field) != metadata[field]:
            raise RuntimeError(f"Top-level and book.{field} differ in {source}")
    metadata["slug"] = SLUGS[locale]
    return metadata


BOOKS = {locale: load_book_metadata(locale) for locale in SLUGS}


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


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def replace_with_retry(source: Path, target: Path) -> None:
    for attempt in range(20):
        try:
            os.replace(source, target)
            return
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(0.5)


def normalize_epub_metadata(epub: Path, metadata: dict[str, object]) -> None:
    temporary = epub.with_name(f"{epub.stem}.{os.getpid()}.metadata.epub")
    with zipfile.ZipFile(epub) as source:
        container = ET.fromstring(source.read("META-INF/container.xml"))
        rootfiles = [node for node in container.iter() if local_name(node.tag) == "rootfile"]
        if not rootfiles:
            raise RuntimeError(f"EPUB container has no rootfile: {epub}")
        opf_path = rootfiles[0].attrib["full-path"]
        package = ET.fromstring(source.read(opf_path))
        metadata_nodes = [node for node in package.iter() if local_name(node.tag) == "metadata"]
        if not metadata_nodes:
            raise RuntimeError(f"EPUB package has no metadata element: {epub}")
        package_metadata = metadata_nodes[0]
        for child in list(package_metadata):
            if local_name(child.tag) in {"description", "subject"}:
                package_metadata.remove(child)

        title_nodes = [child for child in package_metadata if local_name(child.tag) == "title"]
        for child in title_nodes:
            if "".join(child.itertext()).strip() == str(metadata["subtitle"]) or child.attrib.get("id") == "subtitle":
                package_metadata.remove(child)
        title_nodes = [child for child in package_metadata if local_name(child.tag) == "title"]
        main_title = next(
            (child for child in title_nodes if "".join(child.itertext()).strip() == str(metadata["title"])),
            None,
        )
        if main_title is None:
            main_title = ET.SubElement(package_metadata, f"{{{DC_NS}}}title")
            main_title.text = str(metadata["title"])

        package_version = package.attrib.get("version", "")
        if package_version.startswith("3"):
            package_namespace = package.tag.partition("}")[0].lstrip("{")
            for child in list(package_metadata):
                if (
                    local_name(child.tag) == "meta"
                    and child.attrib.get("refines") in {"#main-title", "#subtitle"}
                    and child.attrib.get("property") in {"title-type", "display-seq"}
                ):
                    package_metadata.remove(child)
            main_title.set("id", "main-title")
            subtitle = ET.SubElement(package_metadata, f"{{{DC_NS}}}title", {"id": "subtitle"})
            subtitle.text = str(metadata["subtitle"])
            for target, title_type, sequence in (
                ("#main-title", "main", "1"),
                ("#subtitle", "subtitle", "2"),
            ):
                ET.SubElement(
                    package_metadata,
                    f"{{{package_namespace}}}meta",
                    {"refines": target, "property": "title-type"},
                ).text = title_type
                ET.SubElement(
                    package_metadata,
                    f"{{{package_namespace}}}meta",
                    {"refines": target, "property": "display-seq"},
                ).text = sequence
        else:
            ET.SubElement(package_metadata, f"{{{DC_NS}}}title").text = str(metadata["subtitle"])

        ET.SubElement(package_metadata, f"{{{DC_NS}}}description").text = str(metadata["description"])
        subjects = [str(metadata["subject"]), *(str(keyword) for keyword in metadata["keywords"])]
        for subject in dict.fromkeys(subjects):
            ET.SubElement(package_metadata, f"{{{DC_NS}}}subject").text = subject
        normalized_opf = ET.tostring(package, encoding="utf-8", xml_declaration=True)

        with zipfile.ZipFile(temporary, "w") as target:
            for info in source.infolist():
                payload = normalized_opf if info.filename == opf_path else source.read(info.filename)
                target.writestr(info, payload)
    replace_with_retry(temporary, epub)


def cover_page(cover_png: Path, output_pdf: Path) -> None:
    with Image.open(cover_png) as image:
        image.convert("RGB").save(output_pdf, "PDF", resolution=300.0)


def export_ebook_cover(cover_png: Path, cover_jpg: Path) -> None:
    with Image.open(cover_png) as image:
        image.convert("RGB").save(
            cover_jpg,
            "JPEG",
            quality=95,
            optimize=True,
            dpi=(300, 300),
        )


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
                "/Keywords": ", ".join(metadata["keywords"]),
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
    rendered_epub3 = newest(project / "_book", ".epub")
    final_epub = output_epub / f"{metadata['slug']}.epub"
    final_epub3 = output_epub / f"{metadata['slug']}-EPUB3.epub"
    shutil.copy2(rendered_epub3, final_epub3)
    normalize_epub_metadata(final_epub3, metadata)
    shutil.copy2(final_epub3, final_epub)

    subprocess.run([str(quarto), "render", ".", "--to", "epub2"], cwd=project, env=env, check=True)
    rendered_epub2 = newest(project / "_book", ".epub")
    final_epub2 = output_epub / f"{metadata['slug']}-EPUB2.epub"
    shutil.copy2(rendered_epub2, final_epub2)
    normalize_epub_metadata(final_epub2, metadata)

    subprocess.run([str(quarto), "render", ".", "--to", "pdf"], cwd=project, env=env, check=True)
    rendered_pdf = newest(project / "_book", ".pdf")
    interior_pdf = output_pdf / f"{metadata['slug']}-interior-a5.pdf"
    shutil.copy2(rendered_pdf, interior_pdf)

    cover_png = project / "cover" / f"front-cover-{locale}.png"
    final_cover = output_cover / f"{metadata['slug']}-cover.png"
    shutil.copy2(cover_png, final_cover)
    final_cover_jpg = output_cover / f"{metadata['slug']}-cover.jpg"
    export_ebook_cover(final_cover, final_cover_jpg)
    final_pdf = output_pdf / f"{metadata['slug']}.pdf"
    package_pdf(locale, interior_pdf, cover_png, final_pdf)

    print(f"{locale}_epub={final_epub}")
    print(f"{locale}_epub3={final_epub3}")
    print(f"{locale}_epub2={final_epub2}")
    print(f"{locale}_pdf={final_pdf}")
    print(f"{locale}_cover={final_cover}")
    print(f"{locale}_cover_jpg={final_cover_jpg}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build localized EPUB3, EPUB2, cover, and A5 PDF editions.")
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
