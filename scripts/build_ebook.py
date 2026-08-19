"""Build a review EPUB3 with Pandoc when Quarto is unavailable.

This is a fast preflight builder. The canonical publication path remains
`quarto render book --to epub`.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"
DIST = ROOT / "dist"
OUTPUT = DIST / "semiconductor-chaekmun-review.epub"


def split_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, flags=re.DOTALL)
    if not match:
        return {}, text
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    return meta, match.group(2).strip()


def source_files() -> list[Path]:
    return [
        BOOK / "index.qmd",
        *sorted((BOOK / "chapters").glob("week*.qmd")),
        BOOK / "publishing-guide.qmd",
        BOOK / "references.qmd",
    ]


def main() -> None:
    if shutil.which("pandoc") is None:
        raise SystemExit("pandoc is required; use `quarto render book --to epub` instead")

    chunks = []
    for path in source_files():
        meta, body = split_front_matter(path.read_text(encoding="utf-8"))
        title = meta.get("title", path.stem)
        body = body.replace("../figures/", f"{(BOOK / 'figures').as_posix()}/")
        body = re.sub(
            r"```\{mermaid\}.*?```",
            "> **의사결정 흐름**: 문제 정의 → 영향받는 사람 → 측정 지표 → 중단·수정 조건",
            body,
            flags=re.DOTALL,
        )
        chunks.append(f"# {title}\n\n{body}\n")

    DIST.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="chaekmun-epub-", dir=DIST) as tmp:
        manuscript = Path(tmp) / "manuscript.md"
        manuscript.write_text("\n\n".join(chunks), encoding="utf-8")
        subprocess.run(
            [
                "pandoc",
                str(manuscript),
                "--from=markdown+fenced_divs",
                "--to=epub3",
                "--toc",
                "--toc-depth=1",
                "--split-level=1",
                "--metadata=title:반도체 면접, 왕의 질문에 답하라",
                "--metadata=subtitle:조선의 책문으로 훈련하는 AI·공정·설계·공급망 데이터 토론",
                "--metadata=author:waterfirst",
                "--metadata=lang:ko-KR",
                f"--css={BOOK / 'styles.css'}",
                f"--output={OUTPUT}",
            ],
            check=True,
        )
    print(OUTPUT)


if __name__ == "__main__":
    main()
