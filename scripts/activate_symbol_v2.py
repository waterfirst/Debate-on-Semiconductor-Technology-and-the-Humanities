"""Point every chapter at its individually generated v2 symbolic illustration."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "book" / "chapters"


def main() -> None:
    changed = 0
    for week in range(1, 31):
        path = CHAPTERS / f"week{week:02d}.qmd"
        old = f"week{week:02d}-symbol.png"
        new = f"week{week:02d}-symbol-v2.png"
        text = path.read_text(encoding="utf-8")
        if new in text:
            continue
        if old not in text:
            raise RuntimeError(f"missing expected illustration reference: {path}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        changed += 1
    print(f"activated v2 illustrations in {changed} chapters")


if __name__ == "__main__":
    main()
