"""Normalize a small set of house-style terms in Quarto source files.

This is intentionally conservative: it only performs literal replacements
that the editorial audit can verify without changing sentence structure.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPLACEMENTS = {
    "%p": "%포인트",
    "퍼센트포인트": "%포인트",
    "2026년 8월 19일 현재 국가법령정보센터": "2026년 8월 20일 현재 국가법령정보센터",
}


def main() -> None:
    changed = 0
    for path in (ROOT / "book").rglob("*.qmd"):
        original = path.read_text(encoding="utf-8")
        updated = original
        for before, after in REPLACEMENTS.items():
            updated = updated.replace(before, after)
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    print(f"normalized_files={changed}")


if __name__ == "__main__":
    main()
