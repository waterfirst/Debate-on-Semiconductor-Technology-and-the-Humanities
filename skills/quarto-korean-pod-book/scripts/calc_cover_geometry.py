"""Calculate POD spine and full-wrap dimensions from finished interior pages."""

from __future__ import annotations

import argparse
import json
import math


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, required=True)
    parser.add_argument("--paper-thickness-mm", type=float, default=0.12)
    parser.add_argument("--trim-width-mm", type=float, default=148.0)
    parser.add_argument("--trim-height-mm", type=float, default=210.0)
    parser.add_argument("--wing-mm", type=float, default=80.0)
    parser.add_argument("--bleed-mm", type=float, default=3.0)
    parser.add_argument("--fold-allowance-mm", type=float, default=3.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.pages < 1:
        raise SystemExit("--pages must be positive")
    sheets = math.ceil(args.pages / 2)
    spine = math.ceil(sheets * args.paper_thickness_mm)
    width = (
        2 * args.trim_width_mm
        + spine
        + 2 * args.wing_mm
        + 2 * args.bleed_mm
        + 2 * args.fold_allowance_mm
    )
    height = args.trim_height_mm + 2 * args.bleed_mm
    result = {
        "pages": args.pages,
        "sheets": sheets,
        "paper_thickness_mm": args.paper_thickness_mm,
        "spine_mm": spine,
        "full_wrap_width_mm": width,
        "full_wrap_height_mm": height,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
