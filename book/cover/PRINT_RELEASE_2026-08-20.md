# Print cover release — 2026-08-20

## Artifact

- File: `반도체-면접-왕의-질문에-답하라-인쇄용-펼침표지-한글상표추가-2026-08-20.pdf`
- SHA-256: `01a0b22d5e7a2fc7d6e01e809e896cdff8393f3b5266ae6aa288bc3b0684894f`
- Page count: 1
- Media size: 484 × 216 mm
- Trim: 3 mm bleed/TrimBox preserved
- Raster resolution: 300 dpi
- Image color spaces: CMYK and Gray
- RGB images: none
- Font objects: none; cover text/marks are intentionally rasterized or outlined in the generated PDF

## Branding

- Back cover keeps the English `SB | Scholar Bridge` logo.
- Korean word mark `스칼라브릿지` appears on a separate line with balanced top/bottom white-box spacing.
- Spine publisher mark is Korean `스칼라브릿지`.
- No `®`, `등록상표`, or registration-complete claim is used.

## Color-profile status

The release PDF is actual CMYK. It was converted with Ghostscript's installed default CMYK ICC because an exact licensed `Japan Color 2001 Coated` profile was not available in the build environment. Do not call this file an exact Japan Color 2001 Coated conversion.

For a printer-required exact conversion, provide the licensed profile to:

```bash
python book/cover/build_cover_pdfs.py --cmyk-profile /path/to/JapanColor2001Coated.icc
```

Then rerun `pdfinfo -box`, `pdffonts`, and `pdfimages -list`, generate a new checksum, and replace this release record.

## Source

The Korean marks and CMYK build path were introduced in commit `3c8d8896f1df236935d7f14c54d14813e3f94c84`.
