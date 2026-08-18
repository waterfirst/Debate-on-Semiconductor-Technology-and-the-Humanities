"""Create compact grayscale assets for the black-and-white book interior."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "book" / "figures"
SYMBOLS = FIGURES / "symbols"


def save_grayscale(source: Path, destination: Path, max_size: tuple[int, int] | None) -> None:
    with Image.open(source) as image:
        rendered = image.convert("L")
        if max_size:
            rendered.thumbnail(max_size, Image.Resampling.LANCZOS)
        rendered.save(destination, optimize=True, compress_level=9)


def main() -> None:
    for week in range(1, 31):
        save_grayscale(
            FIGURES / f"week{week:02d}.png",
            FIGURES / f"week{week:02d}-print.png",
            None,
        )
        save_grayscale(
            SYMBOLS / f"week{week:02d}-symbol-v2.png",
            SYMBOLS / f"week{week:02d}-symbol-print.png",
            (720, 720),
        )
    print("prepared 30 grayscale data figures and 30 grayscale 720px symbols")


if __name__ == "__main__":
    main()
