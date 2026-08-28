"""Validate publication structure and content for the Korean EPUB editions."""

from __future__ import annotations

import hashlib
import posixpath
import re
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET
from zipfile import ZIP_STORED, ZipFile

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
OUTPUT = BOOK / "output" / "epub"
SLUG = "반도체-면접-왕의-질문에-답하라"
EPUB3 = OUTPUT / f"{SLUG}-EPUB3.epub"
EPUB2 = OUTPUT / f"{SLUG}-EPUB2.epub"
CANONICAL = OUTPUT / f"{SLUG}.epub"
COVER = OUTPUT / f"{SLUG}-전자책-표지.jpg"

CONTAINER_NS = "urn:oasis:names:tc:opendocument:xmlns:container"
DC_NS = "http://purl.org/dc/elements/1.1/"
EXPECTED_METADATA = {
    "title": "반도체 면접, 왕의 질문에 답하라",
    "creator": "최낙초",
    "language": "ko-KR",
    "publisher": "스칼라브릿지",
    "date": "2026-08-30",
    "identifier": "urn:uuid:1929a370-0363-43dc-8750-b7f44f8bdc2c",
}
EXPECTED_PHRASES = (
    "나눌 수 있는 금액의 계산식",
    "민간용 재난 드론",
    "재현성이 높은 공정 조건 B",
    "안정 생산 조건 범위와 가속모델이 이전과 같다는 점",
    "조건을 나눈 로트 시험을 설계하며",
    "전력 대비 성능 1.48배",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def chapter_titles() -> list[str]:
    config = (BOOK / "_quarto.yml").read_text(encoding="utf-8")
    paths = re.findall(r"- (chapters/week\d+\.qmd)", config)
    assert len(paths) == 19, f"expected 19 selected chapters, got {len(paths)}"
    titles: list[str] = []
    for relative in paths:
        source = (BOOK / relative).read_text(encoding="utf-8")
        match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', source, re.MULTILINE)
        assert match, f"missing title in {relative}"
        titles.append(match.group(1))
    return titles


def package_data(archive: ZipFile) -> tuple[str, ET.Element, str]:
    container = ET.fromstring(archive.read("META-INF/container.xml"))
    rootfile = container.find(f".//{{{CONTAINER_NS}}}rootfile")
    assert rootfile is not None, "container has no rootfile"
    opf_name = rootfile.attrib["full-path"]
    package = ET.fromstring(archive.read(opf_name))
    namespace = package.tag.partition("}")[0].lstrip("{")
    return opf_name, package, namespace


def validate_references(archive: ZipFile, xhtml_names: list[str]) -> None:
    names = set(archive.namelist())
    for member in xhtml_names:
        root = ET.fromstring(archive.read(member))
        for element in root.iter():
            local_name = element.tag.rpartition("}")[2]
            if local_name == "script":
                raise AssertionError(f"unsupported script element in {member}")
            if local_name == "math":
                raise AssertionError(f"unsupported MathML in {member}")
            attribute = "src" if local_name == "img" else "href" if local_name == "a" else None
            if attribute is None or attribute not in element.attrib:
                continue
            if local_name == "img":
                assert "alt" in element.attrib, f"image without alt in {member}"
            reference = element.attrib[attribute]
            if not reference or reference.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target = reference.split("#", 1)[0].split("?", 1)[0]
            resolved = posixpath.normpath(
                str(PurePosixPath(member).parent / PurePosixPath(target))
            )
            assert resolved in names, f"broken reference {reference} in {member}"


def validate_edition(path: Path, major_version: str, titles: list[str]) -> None:
    assert path.exists(), f"missing {path}"
    assert path.stat().st_size < 2 * 1024**3, f"EPUB exceeds 2 GB: {path}"
    with ZipFile(path) as archive:
        assert archive.testzip() is None, f"ZIP CRC failure: {path}"
        entries = archive.infolist()
        assert entries[0].filename == "mimetype", "mimetype is not the first entry"
        assert entries[0].compress_type == ZIP_STORED, "mimetype is compressed"
        assert archive.read("mimetype") == b"application/epub+zip", "invalid mimetype"

        opf_name, package, opf_ns = package_data(archive)
        assert package.attrib["version"].startswith(major_version), (
            f"expected EPUB {major_version}, got {package.attrib['version']}"
        )
        ns = {"opf": opf_ns, "dc": DC_NS}
        metadata = package.find("opf:metadata", ns)
        manifest = package.find("opf:manifest", ns)
        spine = package.find("opf:spine", ns)
        assert metadata is not None and manifest is not None and spine is not None

        for key, expected in EXPECTED_METADATA.items():
            values = [node.text or "" for node in metadata.findall(f"dc:{key}", ns)]
            assert expected in values, f"metadata mismatch for {key}: {values}"

        items = manifest.findall("opf:item", ns)
        by_id = {item.attrib["id"]: item for item in items}
        spine_refs = [item.attrib["idref"] for item in spine.findall("opf:itemref", ns)]
        assert len(spine_refs) >= 24, f"spine unexpectedly short: {len(spine_refs)}"
        assert all(item_id in by_id for item_id in spine_refs), "invalid spine reference"

        if major_version == "3":
            assert any("nav" in item.attrib.get("properties", "").split() for item in items)
            cover_items = [
                item for item in items if "cover-image" in item.attrib.get("properties", "").split()
            ]
        else:
            cover_meta = next(
                (node for node in metadata.findall("opf:meta", ns) if node.attrib.get("name") == "cover"),
                None,
            )
            assert cover_meta is not None, "EPUB2 cover metadata is missing"
            cover_items = [by_id[cover_meta.attrib["content"]]]
            assert spine.attrib.get("toc") in by_id, "EPUB2 NCX is not linked from the spine"

        assert len(cover_items) == 1, f"expected one cover image, got {len(cover_items)}"
        opf_dir = PurePosixPath(opf_name).parent
        cover_name = posixpath.normpath(str(opf_dir / cover_items[0].attrib["href"]))
        assert cover_name in archive.namelist(), "embedded cover is missing"

        xhtml_names = [
            posixpath.normpath(str(opf_dir / item.attrib["href"]))
            for item in items
            if item.attrib.get("media-type") == "application/xhtml+xml"
        ]
        validate_references(archive, xhtml_names)
        raw_xhtml = b"\n".join(archive.read(name) for name in xhtml_names)
        text = " ".join(
            "".join(ET.fromstring(archive.read(name)).itertext()) for name in xhtml_names
        )
        text = re.sub(r"\s+", " ", text)

        assert text.count("데이터로 보기") == 19, "section heading count mismatch"
        assert "데이터 렌즈" not in text, "stale section heading remains"
        assert all(title in text for title in titles), "one or more selected chapter titles are missing"
        assert all(phrase in text for phrase in EXPECTED_PHRASES), "final-PDF wording is missing"
        assert re.search(
            rb"<sup>1/(?:<em>)?n(?:</em>)?</sup>", raw_xhtml
        ), "portable exponent markup is missing"
        assert b"http://www.w3.org/1998/Math/MathML" not in raw_xhtml, "MathML remains"
        assert b"\\text{" not in raw_xhtml and b"\\begin{" not in raw_xhtml, (
            "raw TeX remains"
        )

    print(f"{path.name}: EPUB {major_version}, {len(spine_refs)} spine items, PASS")


def validate_cover() -> None:
    assert COVER.exists(), f"missing {COVER}"
    with Image.open(COVER) as image:
        assert image.mode == "RGB", f"cover mode must be RGB, got {image.mode}"
        assert image.size == (1748, 2480), f"unexpected cover size: {image.size}"
        assert 640 <= min(image.size) and max(image.size) <= 7200
    print(f"{COVER.name}: 1748x2480 RGB JPEG, PASS")


def main() -> None:
    titles = chapter_titles()
    validate_edition(EPUB3, "3", titles)
    validate_edition(EPUB2, "2", titles)
    assert digest(CANONICAL) == digest(EPUB3), "canonical EPUB differs from EPUB3"
    validate_cover()
    print("ebook_validation=PASS")


if __name__ == "__main__":
    main()
