from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import posixpath
import re
import subprocess
import sys
import unicodedata
import zipfile
from datetime import date
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
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)
A5_POINTS = (419.53, 595.28)
KOREAN_PRINT_ISBN = "9791122089585"
AI_DISCLOSURE_SENTENCES = {
    "en": (
        "Generative AI technologies supported research, translation from the Korean manuscript, editing, and image generation for this book.",
        "The author reviewed the localized edition and is responsible for the final selection, arrangement, revision, and publication of all text and visual material.",
    ),
    "ja": (
        "本書では、資料調査、韓国語原稿からの翻訳、編集、画像生成の過程で生成AI技術を補助的に利用しました。",
        "著者がローカライズ版を確認し、最終的な文章と視覚資料の選定、構成、修正、刊行に責任を負います。",
    ),
}


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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_valid_isbn13(value: str) -> bool:
    digits = re.sub(r"[^0-9]", "", value)
    if len(digits) != 13 or not digits.startswith(("978", "979")):
        return False
    total = sum(int(digit) * (1 if index % 2 == 0 else 3) for index, digit in enumerate(digits[:12]))
    return int(digits[-1]) == (10 - total % 10) % 10


def normalized_catalog_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    normalized = normalized.translate(str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'}))
    return " ".join(normalized.split())


def resolved_member(base: PurePosixPath, reference: str) -> str | None:
    target = reference.split("#", 1)[0].split("?", 1)[0].strip()
    if not target or target.startswith(("data:", "http://", "https://", "mailto:", "tel:", "//")):
        return None
    return posixpath.normpath(posixpath.join(str(base), target))


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
        text_without_publisher = text.replace(str(BOOKS[locale]["publisher"]), "")
        checks.require(not HANGUL.search(text_without_publisher), f"{locale}: Hangul remains in {path.relative_to(ROOT)}")
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


def validate_epub_edition(
    locale: str,
    checks: Checks,
    epub: Path,
    major_version: str,
    require_isbn: bool,
    publication_ready: bool,
    release_metadata: dict[str, str] | None,
) -> None:
    metadata = BOOKS[locale]
    label = f"{locale} EPUB{major_version}"
    checks.require(epub.exists(), f"{label}: file is missing: {epub}")
    if not epub.exists():
        return
    checks.require(epub.stat().st_size < 2 * 1024**3, f"{label}: EPUB exceeds 2 GB")

    try:
        archive = zipfile.ZipFile(epub)
    except zipfile.BadZipFile as exc:
        checks.errors.append(f"{label}: invalid ZIP package: {exc}")
        return

    with archive:
        names = archive.namelist()
        name_set = set(names)
        lower_names = {name.lower() for name in names}
        checks.require(archive.testzip() is None, f"{label}: EPUB ZIP CRC check failed")
        checks.require(bool(names) and names[0] == "mimetype", f"{label}: mimetype must be the first EPUB entry")
        if "mimetype" in name_set:
            info = archive.getinfo("mimetype")
            checks.require(info.compress_type == zipfile.ZIP_STORED, f"{label}: EPUB mimetype must be uncompressed")
            checks.require(archive.read("mimetype") == b"application/epub+zip", f"{label}: invalid EPUB mimetype")
        checks.require("meta-inf/encryption.xml" not in lower_names, f"{label}: encryption.xml/DRM is not allowed")
        checks.require("meta-inf/rights.xml" not in lower_names, f"{label}: rights.xml/DRM is not allowed")

        if "META-INF/container.xml" not in name_set:
            checks.errors.append(f"{label}: EPUB container.xml is missing")
            return
        try:
            container = ET.fromstring(archive.read("META-INF/container.xml"))
        except ET.ParseError as exc:
            checks.errors.append(f"{label}: invalid container.xml: {exc}")
            return
        rootfiles = [node for node in container.iter() if local_name(node.tag) == "rootfile"]
        checks.require(bool(rootfiles), f"{label}: EPUB container has no rootfile")
        if not rootfiles:
            return
        opf_path = rootfiles[0].attrib.get("full-path", "")
        checks.require(opf_path in name_set, f"{label}: OPF package is missing: {opf_path}")
        if opf_path not in name_set:
            return
        try:
            opf_root = ET.fromstring(archive.read(opf_path))
        except ET.ParseError as exc:
            checks.errors.append(f"{label}: invalid OPF XML: {exc}")
            return
        opf_dir = PurePosixPath(opf_path).parent
        package_version = opf_root.attrib.get("version", "")
        checks.require(
            package_version.startswith(major_version),
            f"{label}: expected package version {major_version}, found {package_version}",
        )

        titles = xml_text(opf_root, "title")
        creators = xml_text(opf_root, "creator")
        languages = xml_text(opf_root, "language")
        publishers = xml_text(opf_root, "publisher")
        identifiers = xml_text(opf_root, "identifier")
        dates = xml_text(opf_root, "date")
        descriptions = xml_text(opf_root, "description")
        subjects = xml_text(opf_root, "subject")
        rights = xml_text(opf_root, "rights")
        expected_subjects = list(dict.fromkeys([str(metadata["subject"]), *(str(value) for value in metadata["keywords"])]))
        checks.require(titles == [metadata["title"], metadata["subtitle"]], f"{label}: title metadata mismatch: {titles}")
        checks.require(creators == [metadata["author"]], f"{label}: author metadata mismatch: {creators}")
        checks.require(languages == [metadata["lang"]], f"{label}: language metadata mismatch: {languages}")
        checks.require(publishers == [metadata["publisher"]], f"{label}: publisher metadata mismatch: {publishers}")
        checks.require(descriptions == [metadata["description"]], f"{label}: description metadata mismatch: {descriptions}")
        checks.require(subjects == expected_subjects, f"{label}: subject or keyword metadata mismatch: {subjects}")
        checks.require(rights == [metadata["rights"]], f"{label}: rights metadata mismatch: {rights}")
        if require_isbn:
            checks.require(
                any(is_valid_isbn13(identifier) for identifier in identifiers),
                f"{label}: no valid ISBN-13 identifier found: {identifiers}",
            )
        if publication_ready:
            expected = release_metadata or {}
            expected_isbn = str(expected.get("isbn", "")).strip()
            expected_date = str(expected.get("publication_date", "")).strip()
            expected_publisher = str(expected.get("publisher", "")).strip()
            expected_title = str(expected.get("title", "")).strip()
            expected_subtitle = str(expected.get("subtitle", "")).strip()
            expected_author = str(expected.get("author", "")).strip()
            expected_language = str(expected.get("language", "")).strip()
            checks.require(is_valid_isbn13(expected_isbn), f"{label}: release metadata is missing a valid issued ISBN-13")
            try:
                expected_date_valid = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", expected_date)) and date.fromisoformat(expected_date) is not None
            except ValueError:
                expected_date_valid = False
            checks.require(expected_date_valid, f"{label}: release metadata is missing a valid YYYY-MM-DD publication date")
            checks.require(bool(expected_publisher), f"{label}: release metadata is missing the confirmed legal publisher name")
            for field, expected_value in (
                ("title", expected_title),
                ("subtitle", expected_subtitle),
                ("author", expected_author),
                ("lang", expected_language),
            ):
                checks.require(bool(expected_value), f"{label}: release metadata is missing {field}")
                checks.require(
                    bool(expected_value) and expected_value == str(metadata[field]),
                    f"{label}: release {field} does not match _quarto.yml",
                )

            identifier_nodes = [node for node in opf_root.iter() if local_name(node.tag) == "identifier"]
            identifier_by_id = {node.attrib.get("id", ""): "".join(node.itertext()).strip() for node in identifier_nodes}
            unique_identifier = identifier_by_id.get(opf_root.attrib.get("unique-identifier", ""), "")
            checks.require(
                is_valid_isbn13(unique_identifier) and re.sub(r"\D", "", unique_identifier) == re.sub(r"\D", "", expected_isbn),
                f"{label}: OPF unique identifier must match the issued ISBN-13, found: {unique_identifier or '(missing)'}",
            )
            checks.require(
                len(identifiers) == 1 and re.sub(r"\D", "", identifiers[0]) == re.sub(r"\D", "", expected_isbn),
                f"{label}: OPF must contain exactly one dc:identifier matching the issued ISBN-13, found: {identifiers}",
            )
            checks.require(
                expected_date_valid and dates == [expected_date],
                f"{label}: dc:date must match the confirmed publication date {expected_date or '(missing)'}, found: {dates}",
            )
            checks.require(
                bool(expected_publisher) and publishers == [expected_publisher],
                f"{label}: dc:publisher must match the confirmed legal publisher name {expected_publisher or '(missing)'}, found: {publishers}",
            )
            checks.require(
                titles == [expected_title, expected_subtitle],
                f"{label}: dc:title values conflict with release metadata: {titles}",
            )
            checks.require(creators == [expected_author], f"{label}: dc:creator conflicts with release metadata: {creators}")
            checks.require(languages == [expected_language], f"{label}: dc:language conflicts with release metadata: {languages}")

            copyright_heading = "Copyright" if locale == "en" else "奥付"
            copyright_pages: list[tuple[str, str]] = []
            for member in archive.namelist():
                if PurePosixPath(member).suffix.lower() not in {".html", ".xhtml"}:
                    continue
                page_text = " ".join(ET.fromstring(archive.read(member)).itertext())
                if copyright_heading in page_text:
                    copyright_pages.append((member, page_text))
            copyright_text = copyright_pages[0][1] if len(copyright_pages) == 1 else ""
            checks.require(len(copyright_pages) == 1, f"{label}: EPUB must contain exactly one copyright page, found: {len(copyright_pages)}")
            checks.require(
                bool(expected_isbn) and re.sub(r"\D", "", expected_isbn) in re.sub(r"\D", "", copyright_text),
                f"{label}: copyright page does not contain the issued ISBN-13",
            )
            checks.require(
                bool(expected_date) and normalized_catalog_text(expected_date) in normalized_catalog_text(copyright_text),
                f"{label}: copyright page does not contain the confirmed publication date {expected_date or '(missing)'}",
            )
            checks.require(
                bool(expected_publisher) and normalized_catalog_text(expected_publisher) in normalized_catalog_text(copyright_text),
                f"{label}: copyright page does not contain the confirmed legal publisher name {expected_publisher or '(missing)'}",
            )
            for field, expected_value in (
                ("title", expected_title),
                ("subtitle", expected_subtitle),
                ("author", expected_author),
            ):
                checks.require(
                    bool(expected_value) and normalized_catalog_text(expected_value) in normalized_catalog_text(copyright_text),
                    f"{label}: copyright page does not contain the confirmed {field}",
                )
            normalized_copyright = normalized_catalog_text(copyright_text)
            for sentence in AI_DISCLOSURE_SENTENCES[locale]:
                checks.require(
                    normalized_catalog_text(sentence) in normalized_copyright,
                    f"{label}: copyright page is missing required AI-use scope or author-responsibility text",
                )

        manifest = [node for node in opf_root.iter() if local_name(node.tag) == "item"]
        manifest_by_id = {item.attrib.get("id", ""): item for item in manifest}
        spine_nodes = [node for node in opf_root.iter() if local_name(node.tag) == "spine"]
        checks.require(bool(manifest), f"{label}: manifest is missing or empty")
        checks.require(bool(spine_nodes), f"{label}: spine is missing")
        if not spine_nodes:
            return
        spine = spine_nodes[0]
        spine_refs = [node.attrib.get("idref", "") for node in spine if local_name(node.tag) == "itemref"]
        checks.require(len(spine_refs) >= 24, f"{label}: EPUB spine is unexpectedly short ({len(spine_refs)})")
        checks.require(all(reference in manifest_by_id for reference in spine_refs), f"{label}: spine references missing items")

        cover_items: list[ET.Element] = []
        if major_version == "3":
            main_title_nodes = [
                node
                for node in opf_root.iter()
                if local_name(node.tag) == "title"
                and "".join(node.itertext()).strip() == metadata["title"]
            ]
            subtitle_nodes = [
                node
                for node in opf_root.iter()
                if local_name(node.tag) == "title"
                and "".join(node.itertext()).strip() == metadata["subtitle"]
            ]
            main_title_ids = {node.attrib.get("id", "") for node in main_title_nodes}
            subtitle_ids = {node.attrib.get("id", "") for node in subtitle_nodes}
            refinement_values: dict[tuple[str, str], list[str]] = {}
            for node in opf_root.iter():
                if local_name(node.tag) != "meta" or not node.attrib.get("refines", "").startswith("#"):
                    continue
                key = (node.attrib["refines"].removeprefix("#"), node.attrib.get("property", ""))
                refinement_values.setdefault(key, []).append("".join(node.itertext()).strip())
            checks.require(len(main_title_nodes) == 1 and bool(next(iter(main_title_ids), "")), f"{label}: main title id is missing or duplicated")
            checks.require(len(subtitle_nodes) == 1 and bool(next(iter(subtitle_ids), "")), f"{label}: subtitle id is missing or duplicated")
            for title_ids, title_type, sequence in (
                (main_title_ids, "main", "1"),
                (subtitle_ids, "subtitle", "2"),
            ):
                title_id = next(iter(title_ids), "")
                checks.require(
                    refinement_values.get((title_id, "title-type")) == [title_type],
                    f"{label}: {title_type} title-type refinement is missing or invalid",
                )
                checks.require(
                    refinement_values.get((title_id, "display-seq")) == [sequence],
                    f"{label}: {title_type} display-seq refinement is missing or invalid",
                )
            nav_items = [item for item in manifest if "nav" in item.attrib.get("properties", "").split()]
            checks.require(bool(nav_items), f"{label}: EPUB3 navigation document is missing")
            cover_items = [item for item in manifest if "cover-image" in item.attrib.get("properties", "").split()]
            checks.require(bool(cover_items), f"{label}: EPUB3 cover-image manifest property is missing")
            for nav_item in nav_items:
                nav_member = resolved_member(opf_dir, nav_item.attrib.get("href", ""))
                if nav_member and nav_member in name_set:
                    try:
                        nav_document = ET.fromstring(archive.read(nav_member))
                        toc_nodes = [
                            node for node in nav_document.iter()
                            if local_name(node.tag) == "nav"
                            and any(local_name(key) == "type" and "toc" in value.split() for key, value in node.attrib.items())
                        ]
                        checks.require(bool(toc_nodes), f"{label}: navigation document has no EPUB TOC")
                    except ET.ParseError as exc:
                        checks.errors.append(f"{label}: invalid navigation document {nav_member}: {exc}")
        else:
            metadata_nodes = [node for node in opf_root.iter() if local_name(node.tag) == "metadata"]
            cover_meta = next(
                (
                    node for metadata_node in metadata_nodes for node in metadata_node
                    if local_name(node.tag) == "meta" and node.attrib.get("name") == "cover"
                ),
                None,
            )
            checks.require(cover_meta is not None, f"{label}: EPUB2 cover metadata is missing")
            if cover_meta is not None:
                cover_id = cover_meta.attrib.get("content", "")
                checks.require(cover_id in manifest_by_id, f"{label}: EPUB2 cover metadata points to a missing item")
                if cover_id in manifest_by_id:
                    cover_items = [manifest_by_id[cover_id]]
            ncx_items = [item for item in manifest if item.attrib.get("media-type") == "application/x-dtbncx+xml"]
            checks.require(bool(ncx_items), f"{label}: EPUB2 NCX manifest item is missing")
            toc_id = spine.attrib.get("toc", "")
            checks.require(bool(toc_id) and toc_id in manifest_by_id, f"{label}: EPUB2 spine does not reference an NCX")
            if toc_id in manifest_by_id:
                checks.require(
                    manifest_by_id[toc_id].attrib.get("media-type") == "application/x-dtbncx+xml",
                    f"{label}: EPUB2 spine toc does not point to the NCX item",
                )
                ncx_member = resolved_member(opf_dir, manifest_by_id[toc_id].attrib.get("href", ""))
                if ncx_member and ncx_member in name_set:
                    try:
                        ncx_document = ET.fromstring(archive.read(ncx_member))
                        nav_points = [node for node in ncx_document.iter() if local_name(node.tag) == "navPoint"]
                        checks.require(bool(nav_points), f"{label}: NCX contains no navPoint entries")
                    except ET.ParseError as exc:
                        checks.errors.append(f"{label}: invalid NCX {ncx_member}: {exc}")

        checks.require(len(cover_items) == 1, f"{label}: expected one cover image, found {len(cover_items)}")

        for item in manifest:
            href = item.attrib.get("href", "")
            member = resolved_member(opf_dir, href)
            if not member:
                checks.errors.append(f"{label}: manifest item has no usable href: {item.attrib}")
                continue
            checks.require(member in name_set, f"{label}: manifest resource is missing: {member}")
            media_type = item.attrib.get("media-type", "")
            checks.require(
                "javascript" not in media_type.lower() and not member.lower().endswith((".js", ".mjs")),
                f"{label}: JavaScript is not allowed: {member}",
            )
            if media_type.startswith("image/") and member in name_set:
                try:
                    with Image.open(io.BytesIO(archive.read(member))) as image:
                        width, height = image.size
                    checks.require(max(width, height) <= 3200, f"{label}: image exceeds 3200 px: {member} ({width}x{height})")
                except Exception as exc:
                    checks.errors.append(f"{label}: unreadable EPUB image {member}: {exc}")
            if media_type == "text/css" and member in name_set:
                css_base = PurePosixPath(member).parent
                css = archive.read(member).decode("utf-8", errors="replace")
                for _, reference in CSS_URL.findall(css):
                    target = resolved_member(css_base, reference)
                    if target:
                        checks.require(target in name_set, f"{label}: missing CSS resource {reference} in {member}")

        for name in names:
            if not name.lower().endswith((".xhtml", ".html", ".htm")):
                continue
            raw = archive.read(name)
            text = raw.decode("utf-8", errors="replace")
            checks.require("<script" not in text.lower(), f"{label}: script element found in {name}")
            try:
                document = ET.fromstring(raw)
            except ET.ParseError as exc:
                checks.errors.append(f"{label}: invalid XHTML in {name}: {exc}")
                continue
            visible_text = " ".join(document.itertext()).replace(str(metadata["publisher"]), "")
            checks.require(not HANGUL.search(visible_text), f"{label}: Hangul remains in EPUB content {name}")
            images = [node for node in document.iter() if local_name(node.tag) == "img"]
            checks.require(all("alt" in node.attrib for node in images), f"{label}: image without alt attribute in {name}")
            xhtml_base = PurePosixPath(name).parent
            for node in document.iter():
                checks.require(local_name(node.tag) != "script", f"{label}: script element found in {name}")
                checks.require(
                    not any(local_name(attribute).lower().startswith("on") for attribute in node.attrib),
                    f"{label}: inline JavaScript event handler found in {name}",
                )
                for attribute, reference in node.attrib.items():
                    if local_name(attribute) not in {"src", "href"}:
                        continue
                    target = resolved_member(xhtml_base, reference)
                    if target:
                        checks.require(target in name_set, f"{label}: broken resource {reference} in {name}")

        if cover_items:
            cover_member = resolved_member(opf_dir, cover_items[0].attrib.get("href", ""))
            checks.require(bool(cover_member) and cover_member in name_set, f"{label}: embedded cover is missing")
            if cover_member and cover_member in name_set:
                try:
                    with Image.open(io.BytesIO(archive.read(cover_member))) as image:
                        width, height = image.size
                    checks.require(width >= 640 and height >= 640, f"{label}: embedded cover is below 640 px")
                    checks.require(max(width, height) <= 7200, f"{label}: embedded cover exceeds 7200 px")
                except Exception as exc:
                    checks.errors.append(f"{label}: unreadable embedded cover {cover_member}: {exc}")

    checks.note(f"{label}: {epub.stat().st_size / 1024**2:.1f} MB, {len(spine_refs)} spine items")


def validate_epubs(
    locale: str,
    checks: Checks,
    require_isbn: bool,
    publication_ready: bool,
    release_metadata: dict[str, str] | None,
) -> tuple[Path, Path]:
    metadata = BOOKS[locale]
    output = TRANSLATIONS / locale / "output" / "epub"
    canonical = output / f"{metadata['slug']}.epub"
    epub3 = output / f"{metadata['slug']}-EPUB3.epub"
    epub2 = output / f"{metadata['slug']}-EPUB2.epub"
    validate_epub_edition(locale, checks, epub3, "3", require_isbn, publication_ready, release_metadata)
    validate_epub_edition(locale, checks, epub2, "2", require_isbn, publication_ready, release_metadata)
    checks.require(canonical.exists(), f"{locale}: canonical EPUB is missing: {canonical}")
    if canonical.exists() and epub3.exists():
        identical = digest(canonical) == digest(epub3)
        checks.require(identical, f"{locale}: canonical EPUB differs from EPUB3")
        if identical:
            checks.note(f"{locale}: canonical EPUB is byte-identical to EPUB3")
    return epub3, epub2


def validate_output_covers(locale: str, checks: Checks) -> None:
    metadata = BOOKS[locale]
    output = TRANSLATIONS / locale / "output" / "cover"
    cover_png = output / f"{metadata['slug']}-cover.png"
    cover_jpg = output / f"{metadata['slug']}-cover.jpg"
    checks.require(cover_png.exists(), f"{locale}: final PNG cover is missing")
    if cover_png.exists():
        with Image.open(cover_png) as image:
            checks.require(image.size == (1748, 2480), f"{locale}: PNG cover must be 1748x2480, found {image.size}")
            checks.require(image.format == "PNG", f"{locale}: existing cover is not a PNG")
    checks.require(cover_jpg.exists(), f"{locale}: RGB JPEG cover is missing")
    if cover_jpg.exists():
        with Image.open(cover_jpg) as image:
            checks.require(image.size == (1748, 2480), f"{locale}: JPEG cover must be 1748x2480, found {image.size}")
            checks.require(image.mode == "RGB", f"{locale}: JPEG cover must be RGB, found {image.mode}")
            checks.require(image.format == "JPEG", f"{locale}: cover has .jpg extension but is not JPEG")
        checks.note(f"{locale}: standalone cover is a 1748x2480 RGB JPEG")


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
    for key in ("title", "author", "publisher", "subject"):
        checks.require(str(actual.get(f"/{key.title()}", "")) == metadata[key], f"{locale}: PDF {key} metadata mismatch")
    expected_keywords = ", ".join(metadata["keywords"])
    checks.require(str(actual.get("/Keywords", "")) == expected_keywords, f"{locale}: PDF keywords metadata mismatch")
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


def validate_with_epubcheck(
    locale: str,
    version: str,
    epub: Path,
    checks: Checks,
    java: Path,
    epubcheck_jar: Path,
) -> None:
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
    label = f"{locale} EPUB{version}"
    checks.require(result.returncode == 0, f"{label}: EPUBCheck failed:\n{output}")
    clean = "No errors or warnings detected." in output
    checks.require(clean, f"{label}: EPUBCheck reported a warning or error:\n{output}")
    if result.returncode == 0 and clean:
        checks.note(f"{label}: EPUBCheck passed with zero errors and warnings")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate localized EPUB3, EPUB2, cover, and PDF artifacts.")
    parser.add_argument("--locale", action="append", choices=sorted(BOOKS), help="Validate one locale; repeat as needed.")
    parser.add_argument("--java", default=os.environ.get("JAVA_BIN"), help="Java executable for optional W3C EPUBCheck validation.")
    parser.add_argument("--epubcheck-jar", default=os.environ.get("EPUBCHECK_JAR"), help="Path to epubcheck.jar for optional official validation.")
    parser.add_argument(
        "--require-isbn",
        action="store_true",
        help="Require a checksum-valid 13-digit ISBN in each EPUB package; leave off until ISBNs are assigned.",
    )
    parser.add_argument(
        "--publication-ready",
        action="store_true",
        help="Final gate: compare package and copyright metadata with --release-metadata and require EPUBCheck.",
    )
    parser.add_argument(
        "--release-metadata",
        type=Path,
        help="JSON file keyed by locale with exact title, subtitle, author, language, isbn, publication_date, and publisher values.",
    )
    args = parser.parse_args()
    locales = args.locale or list(BOOKS)
    checks = Checks()
    release_metadata: dict[str, dict[str, str]] = {}
    if args.release_metadata:
        try:
            loaded_release_metadata = json.loads(args.release_metadata.read_text(encoding="utf-8"))
            if isinstance(loaded_release_metadata, dict):
                release_metadata = loaded_release_metadata
            else:
                checks.errors.append("Release metadata must be a JSON object keyed by locale.")
        except (OSError, json.JSONDecodeError) as exc:
            checks.errors.append(f"Unable to read release metadata: {exc}")
    if args.publication_ready and not args.release_metadata:
        checks.errors.append("--publication-ready requires --release-metadata with exact issued values.")
    if args.publication_ready:
        missing_locales = sorted(set(BOOKS) - set(release_metadata))
        if missing_locales:
            checks.errors.append(f"Release metadata must include every language edition: {', '.join(missing_locales)}")
        isbn_owners: dict[str, str] = {}
        for locale, values in release_metadata.items():
            if not isinstance(values, dict):
                checks.errors.append(f"Release metadata entry must be an object: {locale}")
                continue
            isbn = re.sub(r"\D", "", str(values.get("isbn", "")))
            if not is_valid_isbn13(isbn):
                continue
            if isbn == KOREAN_PRINT_ISBN:
                checks.errors.append(f"{locale}: translated EPUB must not reuse the Korean print ISBN")
            previous_owner = isbn_owners.get(isbn)
            if previous_owner and previous_owner != locale:
                checks.errors.append(f"EPUB ISBN is duplicated across {previous_owner} and {locale}")
            isbn_owners[isbn] = locale
    java = Path(args.java) if args.java else None
    epubcheck_jar = Path(args.epubcheck_jar) if args.epubcheck_jar else None
    if bool(java) != bool(epubcheck_jar):
        checks.errors.append("Provide both --java and --epubcheck-jar, or neither.")
    if args.publication_ready and (not java or not epubcheck_jar):
        checks.errors.append("--publication-ready requires both --java and --epubcheck-jar.")
    if java:
        checks.require(java.exists(), f"Java executable does not exist: {java}")
    if epubcheck_jar:
        checks.require(epubcheck_jar.exists(), f"EPUBCheck JAR does not exist: {epubcheck_jar}")
    for locale in locales:
        validate_sources(locale, checks)
        locale_release_metadata = release_metadata.get(locale)
        if args.publication_ready and not isinstance(locale_release_metadata, dict):
            checks.errors.append(f"Release metadata is missing the {locale} object.")
            locale_release_metadata = None
        epub3, epub2 = validate_epubs(
            locale,
            checks,
            args.require_isbn or args.publication_ready,
            args.publication_ready,
            locale_release_metadata,
        )
        validate_output_covers(locale, checks)
        validate_pdf(locale, checks)
        if java and epubcheck_jar and java.exists() and epubcheck_jar.exists():
            validate_with_epubcheck(locale, "3", epub3, checks, java, epubcheck_jar)
            validate_with_epubcheck(locale, "2", epub2, checks, java, epubcheck_jar)

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
