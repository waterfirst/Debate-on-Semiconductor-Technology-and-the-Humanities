"""Shared helpers for the curated chapter list in ``book/_quarto.yml``."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"


def selected_chapters() -> tuple[int, ...]:
    """Return source chapter IDs in their published order."""
    config = (BOOK / "_quarto.yml").read_text(encoding="utf-8")
    chapters = tuple(
        int(match)
        for match in re.findall(r"chapters/week(\d{2})\.qmd", config)
    )
    if not chapters or len(chapters) != len(set(chapters)):
        raise ValueError("book/_quarto.yml has an empty or duplicated chapter list")
    return chapters


def display_number(source_chapter: int) -> int:
    """Return the sequential printed chapter number for a source chapter ID."""
    return selected_chapters().index(source_chapter) + 1
