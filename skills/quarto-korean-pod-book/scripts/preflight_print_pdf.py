#!/usr/bin/env python3
"""Lightweight print-PDF preflight using Poppler command-line tools."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

PT_PER_MM = 72 / 25.4


def run(*args: str) -> str:
    proc = subprocess.run(args, text=True, capture_output=True, check=False)
    if proc.returncode:
        raise RuntimeError(f"{' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def tool_path(name: str) -> str | None:
    system = Path("/usr/bin") / name
    return str(system) if system.is_file() else shutil.which(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--expected-width-mm", type=float)
    parser.add_argument("--expected-height-mm", type=float)
    parser.add_argument("--mode", choices=("grayscale", "cmyk", "any"), default="any")
    parser.add_argument("--tolerance-mm", type=float, default=0.3)
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    if not args.pdf.is_file():
        print(f"ERROR: missing file: {args.pdf}")
        return 2
    tools = {name: tool_path(name) for name in ("pdfinfo", "pdffonts", "pdfimages")}
    for name, path in tools.items():
        if not path:
            print(f"ERROR: required tool not found: {name}")
            return 2

    info = run(tools["pdfinfo"], "-box", str(args.pdf))
    match = re.search(r"Page size:\s+([0-9.]+) x ([0-9.]+) pts", info)
    if not match:
        errors.append("could not read page size")
    elif args.expected_width_mm and args.expected_height_mm:
        width = float(match.group(1)) / PT_PER_MM
        height = float(match.group(2)) / PT_PER_MM
        if (
            abs(width - args.expected_width_mm) > args.tolerance_mm
            or abs(height - args.expected_height_mm) > args.tolerance_mm
        ):
            errors.append(
                f"page size {width:.2f}×{height:.2f} mm; expected "
                f"{args.expected_width_mm:.2f}×{args.expected_height_mm:.2f} mm"
            )

    fonts = run(tools["pdffonts"], str(args.pdf))
    font_rows = [line for line in fonts.splitlines()[2:] if line.strip()]
    for row in font_rows:
        cols = row.split()
        if len(cols) >= 5 and cols[4].lower() != "yes":
            errors.append(f"unembedded font: {cols[0]}")
    if not font_rows:
        warnings.append("no font objects; confirm text is intentionally outlined/rasterized")

    images = run(tools["pdfimages"], "-list", str(args.pdf))
    spaces = set(re.findall(r"\b(gray|rgb|cmyk|icc)\b", images.lower()))
    if args.mode == "grayscale" and ({"rgb", "cmyk"} & spaces):
        errors.append(f"non-grayscale images found: {sorted(spaces)}")
    if args.mode == "cmyk" and "rgb" in spaces:
        errors.append(f"RGB images found in CMYK target: {sorted(spaces)}")
    if args.mode == "cmyk" and not ({"cmyk", "icc"} & spaces):
        warnings.append("no CMYK/ICC images detected; vector colors need separate preflight")

    print(f"FILE: {args.pdf}")
    print(f"IMAGE_COLOR_SPACES: {', '.join(sorted(spaces)) or 'none detected'}")
    for item in warnings:
        print(f"WARNING: {item}")
    for item in errors:
        print(f"ERROR: {item}")
    print("RESULT: FAIL" if errors else "RESULT: PASS WITH WARNINGS" if warnings else "RESULT: PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
