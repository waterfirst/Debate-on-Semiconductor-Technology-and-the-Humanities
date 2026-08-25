"""Audit all chapter charts and illustrations and build visual proof sheets."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

from prepare_print_images import (
    CHART_GRAY_LEVELS,
    CHART_MUTED_TEXT_MAX_GRAY,
    CHART_PALETTE_MIN_CHROMA,
    PALETTE_MATCH_DISTANCE,
    flatten_on_white,
)


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "book" / "figures"
SYMBOLS = FIGURES / "symbols"
PROOF = ROOT / "tmp" / "proof" / "visual-assets"


def palette_masks(image: Image.Image) -> list[tuple[int, np.ndarray]]:
    rgb = np.asarray(flatten_on_white(image), dtype=np.int32)
    chroma = np.max(rgb, axis=2) - np.min(rgb, axis=2)
    max_distance_sq = PALETTE_MATCH_DISTANCE**2
    distances: list[np.ndarray] = []
    levels: list[int] = []
    for palette_rgb, gray_level in CHART_GRAY_LEVELS.items():
        difference = rgb - np.asarray(palette_rgb, dtype=np.int32)
        distances.append(np.sum(difference * difference, axis=2, dtype=np.int32))
        levels.append(gray_level)
    distance_stack = np.stack(distances, axis=2)
    nearest = np.argmin(distance_stack, axis=2)
    nearest_distance = np.min(distance_stack, axis=2)
    return [
        (
            level,
            (nearest == index)
            & (nearest_distance <= max_distance_sq)
            & (chroma >= CHART_PALETTE_MIN_CHROMA),
        )
        for index, level in enumerate(levels)
    ]


def edge_dark_ratio(gray: np.ndarray, threshold: int = 235) -> float:
    edge = np.concatenate((gray[0, :], gray[-1, :], gray[:, 0], gray[:, -1]))
    return float(np.mean(edge < threshold))


def audit_chart(index: int) -> str:
    source_path = FIGURES / f"week{index:02d}.png"
    print_path = FIGURES / f"week{index:02d}-print.png"
    with Image.open(source_path) as source, Image.open(print_path) as printed:
        assert source.size == (1840, 880), f"unexpected source size: {source_path}"
        assert printed.size == (1840, 880), f"unexpected print size: {print_path}"
        gray = np.asarray(printed.convert("L"), dtype=np.uint8)
        source_rgb = np.asarray(flatten_on_white(source), dtype=np.uint8)
        source_gray = np.asarray(flatten_on_white(source).convert("L"), dtype=np.uint8)
        levels: list[int] = []
        for expected, mask in palette_masks(source):
            if int(mask.sum()) < 80:
                continue
            median = int(np.median(gray[mask]))
            assert abs(median - expected) <= 3, (
                f"week{index:02d}: expected palette level {expected}, got {median}"
            )
            levels.append(median)
        for left, right in zip(sorted(set(levels)), sorted(set(levels))[1:]):
            assert right - left >= 45, f"week{index:02d}: gray levels too close: {levels}"
        # 작은 단위·주석처럼 채도가 낮은 회색 글씨는 원래 농도를 유지해야
        # 한다. 팔레트 오인으로 더 밝아지면 흑백 POD에서 획이 사라진다.
        source_chroma = np.max(source_rgb, axis=2) - np.min(source_rgb, axis=2)
        gray_text = (
            (source_chroma < CHART_PALETTE_MIN_CHROMA)
            & (source_gray >= 75)
            & (source_gray <= 160)
        )
        assert int(gray_text.sum()) >= 80, f"week{index:02d}: no gray text sample"
        printed_gray_text = gray[gray_text]
        assert int(np.percentile(printed_gray_text, 95)) <= CHART_MUTED_TEXT_MAX_GRAY, (
            f"week{index:02d}: gray text is too light for print"
        )
        border = edge_dark_ratio(gray)
        assert border == 0.0, f"week{index:02d}: dark pixels touch chart edge ({border:.4%})"
        return f"week{index:02d}: levels={sorted(set(levels)) or ['n/a']} edge={border:.1%}"


def audit_symbol(index: int) -> str:
    path = SYMBOLS / f"week{index:02d}-symbol-print.png"
    with Image.open(path) as image:
        assert image.size == (720, 720), f"unexpected symbol size: {path}"
        gray = np.asarray(image.convert("L"), dtype=np.uint8)
        ink = float(np.mean(gray < 220))
        deep_ink = float(np.mean(gray < 50))
        edge = np.concatenate((gray[0, :], gray[-1, :], gray[:, 0], gray[:, -1]))
        edge_median = float(np.median(edge))
        deep_edge = float(np.mean(edge < 120))
        assert ink < 0.58, f"week{index:02d}: symbol has too little open paper ({ink:.1%})"
        assert deep_ink < 0.22, f"week{index:02d}: symbol may plug in print ({deep_ink:.1%})"
        assert edge_median > 210, (
            f"week{index:02d}: symbol edge is too dark ({edge_median:.0f})"
        )
        assert deep_edge < 0.08, (
            f"week{index:02d}: symbol may have an artificial border ({deep_edge:.1%})"
        )
        return (
            f"week{index:02d}: ink={ink:.1%} deep={deep_ink:.1%} "
            f"edge_median={edge_median:.0f} deep_edge={deep_edge:.1%}"
        )


def make_chart_sheets(suffix: str, label: str) -> None:
    tile_width, image_height, label_height = 900, 430, 34
    font = ImageFont.load_default(size=20)
    for start in (1, 11, 21):
        sheet = Image.new("RGB", (tile_width * 2, (image_height + label_height) * 5), "white")
        draw = ImageDraw.Draw(sheet)
        for offset, week in enumerate(range(start, start + 10)):
            path = FIGURES / f"week{week:02d}{suffix}.png"
            with Image.open(path) as source:
                image = ImageOps.contain(
                    source.convert("RGB"),
                    (tile_width, image_height),
                    Image.Resampling.LANCZOS,
                )
            x = (offset % 2) * tile_width
            y = (offset // 2) * (image_height + label_height)
            sheet.paste(image, (x + (tile_width - image.width) // 2, y))
            draw.text((x + 12, y + image_height + 5), f"week{week:02d}", fill="black", font=font)
        sheet.save(PROOF / f"{label}-{start:02d}-{start + 9:02d}.png", optimize=True)


def make_symbol_sheets() -> None:
    tile, label_height = 500, 34
    font = ImageFont.load_default(size=20)
    for start in (1, 11, 21):
        sheet = Image.new("RGB", (tile * 2, (tile + label_height) * 5), "white")
        draw = ImageDraw.Draw(sheet)
        for offset, week in enumerate(range(start, start + 10)):
            path = SYMBOLS / f"week{week:02d}-symbol-print.png"
            with Image.open(path) as source:
                image = ImageOps.contain(
                    source.convert("RGB"),
                    (tile, tile),
                    Image.Resampling.LANCZOS,
                )
            x = (offset % 2) * tile
            y = (offset // 2) * (tile + label_height)
            sheet.paste(image, (x + (tile - image.width) // 2, y))
            draw.text((x + 12, y + tile + 5), f"week{week:02d}", fill="black", font=font)
        sheet.save(PROOF / f"symbols-{start:02d}-{start + 9:02d}.png", optimize=True)


def main() -> None:
    PROOF.mkdir(parents=True, exist_ok=True)
    # Build proof sheets before assertions so a failed audit still leaves a
    # visual diagnostic for the editor.
    make_chart_sheets("", "charts-color")
    make_chart_sheets("-print", "charts-print")
    make_symbol_sheets()
    for week in range(1, 31):
        print(audit_chart(week))
    for week in range(1, 31):
        print(audit_symbol(week))
    print(f"PASS: 30 charts and 30 symbols; proof sheets: {PROOF}")


if __name__ == "__main__":
    main()
