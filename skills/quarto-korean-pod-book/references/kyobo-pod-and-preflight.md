# Kyobo Purple POD and print preflight

## Verify current rules

Before final layout, confirm the current official trim, bleed, binding, paper, cover finish, flap rules, spine formula, PDF requirements, AI declaration, ISBN handling, proof, replacement, and settlement documents.

- Notices: https://store.kyobobook.co.kr/pod/notice
- Introduction: https://store.kyobobook.co.kr/pod/introduce
- Reference template notice: https://store.kyobobook.co.kr/pod/notice/1006675
- Forms: https://store.kyobobook.co.kr/pod/notice/1002349
- Post-sale replacement: https://store.kyobobook.co.kr/pod/notice/1002524
- AI use: https://store.kyobobook.co.kr/pod/notice/1007236
- ISBN/deposit: https://store.kyobobook.co.kr/pod/notice/1001255

The current official template overrides this reference.

## Cover geometry

```text
width  = 2×bleed + 2×flap + 2×trim_width + spine
height = 2×bleed + trim_height
```

Reference only: A5 148×210, bleed 3, flaps 80, spine 16 mm yields 484×216 mm. Recalculate the spine from the current paper/page formula after final pagination.

Keep fold, trim, spine, barcode, and safe-area guides in editable source. Check back/front/spine orientation at 100%.

## Color and fonts

- B&W interior: true grayscale unless explicitly accepted otherwise.
- Color interior/cover: actual CMYK and a documented soft proof.
- If `Japan Color 2001 Coated` is required, use that exact licensed ICC. Never rename generic DeviceCMYK.
- If unavailable, request the profile or printer approval for a documented fallback.
- ICC reference: https://registry.color.org/cmyk-registry/jc200103
- Adobe profiles: https://www.adobe.com/support/downloads/iccprofiles/iccprofiles_win.html

## Preflight

```bash
pdfinfo -box interior.pdf
pdffonts interior.pdf
pdfimages -list interior.pdf
python scripts/preflight_print_pdf.py interior.pdf --expected-width-mm 148 --expected-height-mm 210 --mode grayscale
python scripts/preflight_print_pdf.py cover.pdf --expected-width-mm 484 --expected-height-mm 216 --mode cmyk
```

`pdffonts` should show `emb=yes`. A deliberately outlined/raster cover can have no font objects. `pdfimages` does not inspect every vector color, so combine commands with a preflight application and rendered inspection.

Inspect front matter, every part/chapter opening, image/table-heavy pages, footnotes, last pages, and cover for crop, dull CMYK conversion, transparency artifacts, glyph substitution, and fold-safe spacing.

Archive separate final interior/cover PDFs, checksums, preflight report, current template capture, metadata, ISBN, upload receipt, proof photos, and correction log.
