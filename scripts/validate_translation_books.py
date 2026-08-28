from __future__ import annotations

import argparse
import io
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET

from PIL import Image
from pypdf import PdfReader

from build_translation_books import BOOKS, ROOT, TRANSLATIONS


EXPECTED_WEEKS = {
    "01", "02", "04", "05", "07", "08", "09", "10", "11", "12",
    "13", "14", "15", "18", "19", "21", "26", "28", "30",
}
HANGUL = re.compile(r"[\u1100-\u11ff\u3130-\u318f\uac00-\ud7a3]")
IMAGE_LINK = re.compile(r"!\[[^]]*]\(([^ )]+)")
URL = re.compile(r"https?://[^\s)\]}>]+")
A5_POINTS = (419.53, 595.28)


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.notes: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def note(self, message: str) -> None:
        self.notes.append(message)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def xml_text(root: ET.Element, name: str) -> list[str]:
    return ["".join(node.itertext()).strip() for node in root.iter() if local_name(node.tag) == name]


def outline_count(items: list[object]) -> int:
    total = 0
    for item in items:
        if isinstance(item, list):
            total += outline_count(item)
        else:
            total += 1
    return total


def font_records(reader: PdfReader) -> dict[tuple[str, str], bool]:
    records: dict[tuple[str, str], bool] = {}
    for page in reader.pages:
        resources = page.get("/Resources")
        resources = resources.get_object() if resources else {}
        fonts = resources.get("/Font", {})
        fonts = fonts.get_object() if hasattr(fonts, "get_object") else fonts
        for key, reference in fonts.items():
            font = reference.get_object()
            base = str(font.get("/BaseFont", key))
            subtype = str(font.get("/Subtype", ""))
            descriptor = font.get("/FontDescriptor")
            descendants = font.get("/DescendantFonts")
            if not descriptor and descendants:
                descriptor = descendants[0].get_object().get("/FontDescriptor")
            descriptor = descriptor.get_object() if descriptor and hasattr(descriptor, "get_object") else descriptor
            embedded = subtype == "/Type3" or bool(
                descriptor and any(name in descriptor for name in ("/FontFile", "/FontFile2", "/FontFile3"))
            )
            records[(base, subtype)] = records.get((base, subtype), True) and embedded
    return records


def validate_sources(locale: str, checks: Checks) -> None:
    project = TRANSLATIONS / locale
    qmd_files = sorted(project.glob("*.qmd")) + sorted((project / "chapters").glob("*.qmd"))
    checks.require(len(qmd_files) == 24, f"{locale}: expected 24 manuscript files, found {len(qmd_files)}")
    chapter_weeks = {path.stem.removeprefix("week") for path in (project / "chapters").glob("week*.qmd")}
    checks.require(chapter_weeks == EXPECTED_WEEKS, f"{locale}: chapter set differs from the 19-title edition")

    for path in qmd_files:
        text = path.read_text(encoding="utf-8")
        match = HANGUL.search(text)
        checks.require(not match, f"{locale}: Hangul remains in {path.relative_to(ROOT)}")
        for target in IMAGE_LINK.findall(text):
            if "://" in target or target.startswith("data:"):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            checks.require(resolved.exists(), f"{locale}: missing image referenced by {path.name}: {target}")

        if path.parent.name == "chapters":
            source = ROOT / "book" / "chapters" / path.name
            checks.require(source.exists(), f"{locale}: original chapter is missing for {path.name}")
            if source.exists():
                original = source.read_text(encoding="utf-8")
                checks.require(len(text.splitlines()) == len(original.splitlines()), f"{locale}: line structure differs in {path.name}")
                checks.require(URL.findall(text) == URL.findall(original), f"{locale}: URL set or order differs in {path.name}")
                checks.require(IMAGE_LINK.findall(text) == IMAGE_LINK.findall(original), f"{locale}: image references differ in {path.name}")
                for marker, label in (("^[", "footnotes"), (":::", "fenced divs"), ("|", "table cells")):
                    checks.require(text.count(marker) == original.count(marker), f"{locale}: {label} differ in {path.name}")
                original_headings = sum(1 for line in original.splitlines() if re.match(r"^#{1,6}\s", line))
                translated_headings = sum(1 for line in text.splitlines() if re.match(r"^#{1,6}\s", line))
                checks.require(translated_headings == original_headings, f"{locale}: heading count differs in {path.name}")

    figures = project / "figures"
    svg_weeks = {path.stem.removeprefix("week") for path in figures.glob("week??.svg")}
    png_weeks = {path.stem.removeprefix("week").removesuffix("-print") for path in figures.glob("week??-print.png")}
    checks.require(svg_weeks == EXPECTED_WEEKS, f"{locale}: localized SVG set is incomplete")
    checks.require(png_weeks == EXPECTED_WEEKS, f"{locale}: print PNG set is incomplete")
    for svg in figures.glob("week??.svg"):
        try:
            ET.parse(svg)
        except ET.ParseError as exc:
            checks.errors.append(f"{locale}: invalid SVG XML in {svg.name}: {exc}")

    cover = project / "cover" / f"front-cover-{locale}.png"
    checks.require(cover.exists(), f"{locale}: source cover PNG is missing")
    if cover.exists():
        with Image.open(cover) as image:
            checks.require(image.size == (1748, 2480), f"{locale}: cover must be 1748x2480, found {image.size}")


def validate_epub(locale: str, checks: Checks) -> None:
    metadata = BOOKS[locale]
    epub = TRANSLATIONS / locale / "output" / "epub" / f"{metadata['slug']}.epub"
    checks.require(epub.exists(), f"{locale}: final EPUB is missing")
    if not epub.exists():
        return
    checks.require(epub.stat().st_size < 2 * 1024**3, f"{locale}: EPUB exceeds 2 GB")

    with zipfile.ZipFile(epub) as archive:
        names = archive.namelist()
        checks.require(archive.testzip() is None, f"{locale}: EPUB ZIP CRC check failed")
        checks.require(bool(names) and names[0] == "mimetype", f"{locale}: mimetype must be the first EPUB entry")
        if "mimetype" in names:
            info = archive.getinfo("mimetype")
            checks.require(info.compress_type == zipfile.ZIP_STORED, f"{locale}: EPUB mimetype must be uncompressed")
            checks.require(archive.read("mimetype") == b"application/epub+zip", f"{locale}: invalid EPUB mimetype")

        container = ET.fromstring(archive.read("META-INF/container.xml"))
        rootfiles = [node for node in container.iter() if local_name(node.tag) == "rootfile"]
        checks.require(bool(rootfiles), f"{locale}: EPUB container has no rootfile")
        if not rootfiles:
            return
        opf_path = rootfiles[0].attrib["full-path"]
        opf_root = ET.fromstring(archive.read(opf_path))
        opf_dir = PurePosixPath(opf_path).parent
        checks.require(opf_root.attrib.get("version", "").startswith("3"), f"{locale}: EPUB package is not version 3")

        titles = xml_text(opf_root, "title")
        creators = xml_text(opf_root, "creator")
        languages = xml_text(opf_root, "language")
        publishers = xml_text(opf_root, "publisher")
        checks.require(metadata["title"] in titles, f"{locale}: EPUB title metadata mismatch")
        checks.require(metadata["author"] in creators, f"{locale}: EPUB author metadata mismatch")
        checks.require(metadata["lang"] in languages, f"{locale}: EPUB language metadata mismatch")
        checks.require(metadata["publisher"] in publishers, f"{locale}: EPUB publisher metadata mismatch")

        manifest = [node for node in opf_root.iter() if local_name(node.tag) == "item"]
        manifest_by_id = {item.attrib.get("id", ""): item for item in manifest}
        nav_items = [item for item in manifest if "nav" in item.attrib.get("properties", "").split()]
        cover_items = [item for item in manifest if "cover-image" in item.attrib.get("properties", "").split()]
        checks.require(bool(nav_items), f"{locale}: EPUB navigation document is missing")
        checks.require(bool(cover_items), f"{locale}: EPUB cover-image manifest property is missing")

        spine_refs = [node.attrib.get("idref", "") for node in opf_root.iter() if local_name(node.tag) == "itemref"]
        checks.require(len(spine_refs) >= 24, f"{locale}: EPUB spine is unexpectedly short ({len(spine_refs)})")
        checks.require(all(reference in manifest_by_id for reference in spine_refs), f"{locale}: EPUB spine references missing items")

        for item in manifest:
            href = item.attrib.get("href")
            if not href:
                continue
            member = str(opf_dir / PurePosixPath(href.split("#", 1)[0]))
            checks.require(member in names, f"{locale}: manifest resource is missing: {member}")
            media_type = item.attrib.get("media-type", "")
            checks.require("javascript" not in media_type and not member.lower().endswith(".js"), f"{locale}: JavaScript is not allowed: {member}")
            if media_type.startswith("image/") and member in names:
                try:
                    with Image.open(io.BytesIO(archive.read(member))) as image:
                        width, height = image.size
                    checks.require(max(width, height) <= 3200, f"{locale}: image exceeds 3200 px: {member} ({width}x{height})")
                except Exception as exc:
                    checks.errors.append(f"{locale}: unreadable EPUB image {member}: {exc}")

        for name in names:
            if name.lower().endswith((".xhtml", ".html", ".htm")):
                raw = archive.read(name)
                text = raw.decode("utf-8", errors="replace")
                checks.require("<script" not in text.lower(), f"{locale}: script element found in {name}")
                checks.require(not HANGUL.search(text), f"{locale}: Hangul remains in EPUB content {name}")
                try:
                    document = ET.fromstring(raw)
                    images = [node for node in document.iter() if local_name(node.tag) == "img"]
                    checks.require(all("alt" in node.attrib for node in images), f"{locale}: image without alt attribute in {name}")
                except ET.ParseError as exc:
                    checks.errors.append(f"{locale}: invalid XHTML in {name}: {exc}")

        if cover_items:
            cover_member = str(opf_dir / PurePosixPath(cover_items[0].attrib["href"]))
            if cover_member in names:
                with Image.open(io.BytesIO(archive.read(cover_member))) as image:
                    width, height = image.size
                checks.require(width >= 640 and height >= 640, f"{locale}: embedded cover is below 640 px")
                checks.require(max(width, height) <= 7200, f"{locale}: embedded cover exceeds 7200 px")

    checks.note(f"{locale}: EPUB {epub.stat().st_size / 1024**2:.1f} MB, {len(spine_refs)} spine items")


def validate_pdf(locale: str, checks: Checks) -> None:
    metadata = BOOKS[locale]
    pdf = TRANSLATIONS / locale / "output" / "pdf" / f"{metadata['slug']}.pdf"
    checks.require(pdf.exists(), f"{locale}: final PDF is missing")
    if not pdf.exists():
        return
    checks.require(pdf.stat().st_size < 2 * 1024**3, f"{locale}: PDF exceeds 2 GB")
    reader = PdfReader(pdf)
    checks.require(not reader.is_encrypted, f"{locale}: PDF must not be encrypted")
    checks.require(len(reader.pages) >= 24, f"{locale}: PDF is unexpectedly short ({len(reader.pages)} pages)")

    for index, page in enumerate(reader.pages, start=1):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        checks.require(width < height, f"{locale}: PDF page {index} is not portrait")
        checks.require(abs(width - A5_POINTS[0]) <= 1 and abs(height - A5_POINTS[1]) <= 1, f"{locale}: PDF page {index} is not A5 ({width:.2f}x{height:.2f} pt)")

    actual = reader.metadata or {}
    for key in ("title", "author", "publisher", "subject", "keywords"):
        checks.require(str(actual.get(f"/{key.title()}", "")) == metadata[key], f"{locale}: PDF {key} metadata mismatch")
    checks.require(str(reader.root_object.get("/Lang", "")) == metadata["lang"], f"{locale}: PDF language metadata mismatch")
    checks.require(outline_count(reader.outline) >= 24, f"{locale}: PDF bookmarks are incomplete")

    first_resources = reader.pages[0].get("/Resources")
    first_resources = first_resources.get_object() if first_resources else {}
    xobjects = first_resources.get("/XObject", {})
    xobjects = xobjects.get_object() if hasattr(xobjects, "get_object") else xobjects
    checks.require(bool(xobjects), f"{locale}: PDF cover page has no embedded image")
    checks.require(not (reader.pages[0].extract_text() or "").strip(), f"{locale}: PDF cover should be image-only")

    fonts = font_records(reader)
    missing_fonts = sorted(f"{name} ({subtype})" for (name, subtype), embedded in fonts.items() if not embedded)
    checks.require(not missing_fonts, f"{locale}: unembedded PDF fonts: {', '.join(missing_fonts)}")
    checks.note(f"{locale}: PDF {pdf.stat().st_size / 1024**2:.1f} MB, {len(reader.pages)} A5 pages, {outline_count(reader.outline)} bookmarks, {len(fonts)} embedded fonts")


def validate_with_epubcheck(locale: str, checks: Checks, java: Path, epubcheck_jar: Path) -> None:
    metadata = BOOKS[locale]
    epub = TRANSLATIONS / locale / "output" / "epub" / f"{metadata['slug']}.epub"
    if not epub.exists():
        return
    result = subprocess.run(
        [str(java), "-Duser.language=en", "-Duser.country=US", "-Dfile.encoding=UTF-8", "-jar", str(epubcheck_jar), str(epub)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    output = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
    checks.require(result.returncode == 0, f"{locale}: EPUBCheck failed:\n{output}")
    clean = "No errors or warnings detected." in output
    checks.require(clean, f"{locale}: EPUBCheck reported a warning or error:\n{output}")
    if result.returncode == 0 and clean:
        checks.note(f"{locale}: EPUBCheck passed with zero errors and warnings")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate localized Google Play Books artifacts.")
    parser.add_argument("--locale", action="append", choices=sorted(BOOKS), help="Validate one locale; repeat as needed.")
    parser.add_argument("--java", default=os.environ.get("JAVA_BIN"), help="Java executable for optional W3C EPUBCheck validation.")
    parser.add_argument("--epubcheck-jar", default=os.environ.get("EPUBCHECK_JAR"), help="Path to epubcheck.jar for optional official validation.")
    args = parser.parse_args()
    locales = args.locale or list(BOOKS)
    checks = Checks()
    java = Path(args.java) if args.java else None
    epubcheck_jar = Path(args.epubcheck_jar) if args.epubcheck_jar else None
    if bool(java) != bool(epubcheck_jar):
        checks.errors.append("Provide both --java and --epubcheck-jar, or neither.")
    if java:
        checks.require(java.exists(), f"Java executable does not exist: {java}")
    if epubcheck_jar:
        checks.require(epubcheck_jar.exists(), f"EPUBCheck JAR does not exist: {epubcheck_jar}")
    for locale in locales:
        validate_sources(locale, checks)
        validate_epub(locale, checks)
        validate_pdf(locale, checks)
        if java and epubcheck_jar and java.exists() and epubcheck_jar.exists():
            validate_with_epubcheck(locale, checks, java, epubcheck_jar)

    for note in checks.notes:
        print(f"PASS: {note}")
    if checks.errors:
        for error in checks.errors:
            print(f"FAIL: {error}", file=sys.stderr)
        print(f"Validation failed with {len(checks.errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Validation passed for: {', '.join(locales)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
