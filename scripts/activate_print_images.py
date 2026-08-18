"""Point chapters at compact grayscale assets used by PDF and EPUB."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "book" / "chapters"


def replace_once(text: str, candidates: tuple[str, ...], new: str, path: Path) -> str:
    if new in text:
        return text
    for old in candidates:
        if old in text:
            return text.replace(old, new, 1)
    raise RuntimeError(f"missing expected image reference in {path}: {candidates}")


def main() -> None:
    changed = 0
    for week in range(1, 31):
        path = CHAPTERS / f"week{week:02d}.qmd"
        text = path.read_text(encoding="utf-8")
        updated = replace_once(
            text,
            (f"week{week:02d}.png",),
            f"week{week:02d}-print.png",
            path,
        )
        updated = replace_once(
            updated,
            (f"week{week:02d}-symbol-v2.png", f"week{week:02d}-symbol.png"),
            f"week{week:02d}-symbol-print.png",
            path,
        )
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    print(f"activated grayscale print assets in {changed} chapters")


if __name__ == "__main__":
    main()
