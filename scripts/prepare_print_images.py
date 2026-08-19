"""Create print-safe grayscale assets for the black-and-white book interior.

The digital charts use a restrained four-colour palette. A naive RGB-to-gray
conversion collapses those hues into almost the same luminance, which makes
legends and series difficult to distinguish in POD printing. Chart colours are
therefore mapped to four deliberately separated gray levels before conversion.
Illustrations keep their original monochrome tonal range.
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "book" / "figures"
SYMBOLS = FIGURES / "symbols"
SYMBOL_SOURCE_OVERRIDES = {
    5: "week05-symbol-v3.png",
    6: "week06-symbol-v3.png",
    7: "week07-symbol-v3.png",
    9: "week09-symbol-v3.png",
    12: "week12-symbol-v3.png",
    18: "week18-symbol-v3.png",
    19: "week19-symbol-v3.png",
}

# Source chart palette and target print luminance. The 50-point intervals stay
# legible after ordinary laser/POD dot gain while retaining a quiet editorial
# appearance. Dark text and the warm paper background are not remapped.
CHART_GRAY_LEVELS = {
    (169, 78, 50): 50,    # rust
    (31, 90, 117): 100,   # blue
    (77, 124, 111): 150,  # green
    (193, 138, 61): 200,  # ochre
}
PALETTE_MATCH_DISTANCE = 48


def flatten_on_white(image: Image.Image) -> Image.Image:
    """Return an RGB image with transparent pixels composited on white."""
    if "A" in image.getbands() or "transparency" in image.info:
        rgba = image.convert("RGBA")
        paper = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        paper.alpha_composite(rgba)
        return paper.convert("RGB")
    return image.convert("RGB")


def chart_to_print_grayscale(image: Image.Image) -> Image.Image:
    """Convert a chart while preserving categorical palette separation."""
    rgb = flatten_on_white(image)
    rgb_array = np.asarray(rgb, dtype=np.int32)
    gray_array = np.asarray(rgb.convert("L"), dtype=np.uint8).copy()
    max_distance_sq = PALETTE_MATCH_DISTANCE**2
    nearest_distance_sq = np.full(rgb_array.shape[:2], max_distance_sq + 1, dtype=np.int32)
    mapped_levels = np.zeros(rgb_array.shape[:2], dtype=np.uint8)

    for palette_rgb, gray_level in CHART_GRAY_LEVELS.items():
        difference = rgb_array - np.asarray(palette_rgb, dtype=np.int32)
        distance_sq = np.sum(difference * difference, axis=2, dtype=np.int32)
        nearer = distance_sq < nearest_distance_sq
        nearest_distance_sq[nearer] = distance_sq[nearer]
        mapped_levels[nearer] = gray_level

    matched = nearest_distance_sq <= max_distance_sq
    gray_array[matched] = mapped_levels[matched]
    return Image.fromarray(gray_array, mode="L")


def save_grayscale(
    source: Path,
    destination: Path,
    max_size: tuple[int, int] | None,
    *,
    remap_chart_palette: bool = False,
) -> None:
    with Image.open(source) as image:
        if remap_chart_palette:
            rendered = chart_to_print_grayscale(image)
        else:
            rendered = flatten_on_white(image).convert("L")
        if max_size:
            rendered.thumbnail(max_size, Image.Resampling.LANCZOS)
        rendered.save(destination, optimize=True, compress_level=9)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weeks", nargs="*", type=int, help="Only rebuild these weeks")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    weeks = sorted(set(args.weeks or range(1, 31)))
    for week in weeks:
        save_grayscale(
            FIGURES / f"week{week:02d}.png",
            FIGURES / f"week{week:02d}-print.png",
            None,
            remap_chart_palette=True,
        )
        symbol_source = SYMBOLS / SYMBOL_SOURCE_OVERRIDES.get(
            week, f"week{week:02d}-symbol-v2.png"
        )
        save_grayscale(
            symbol_source,
            SYMBOLS / f"week{week:02d}-symbol-print.png",
            (720, 720),
        )
    print(
        f"prepared {len(weeks)} grayscale data figures and "
        f"{len(weeks)} grayscale 720px symbols"
    )


if __name__ == "__main__":
    main()
