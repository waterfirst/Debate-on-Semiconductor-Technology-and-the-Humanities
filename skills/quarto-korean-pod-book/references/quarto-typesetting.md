# R/Quarto Korean book production

## Layout

```text
book/
  _quarto.yml
  index.qmd
  chapters/01.qmd
  references.bib
  styles/custom.scss
  tex/preamble.tex
  images/
  cover/
scripts/
output/
```

Use UTF-8, stable filenames, one chapter per QMD, and version control. Keep generated caches and temporary TeX files out of source unless archiving a release.

## Environment and rendering

```r
install.packages("quarto")
quarto::quarto_check()
quarto::quarto_render("book", output_format = "pdf")
```

```bash
quarto check
quarto render book --to pdf
quarto render book --to epub
```

Pin executable R dependencies with `renv`. Record R, Quarto, TeX, Pandoc, and font versions.

## Reference A5 setup

The semiconductor-book project used A5 148×210 mm, XeLaTeX, Pretendard with KoPub/Noto fallbacks, 10.5 pt body, about 1.36 leading, and margins inner 20, outer 15, top 18, bottom 20 mm.

```yaml
project:
  type: book
book:
  title: "책 제목"
  author: "저자"
  chapters:
    - index.qmd
    - part: "제1부"
      chapters:
        - chapters/01.qmd
format:
  pdf:
    pdf-engine: xelatex
    documentclass: scrbook
    papersize: a5
    fontsize: 10.5pt
    geometry:
      - inner=20mm
      - outer=15mm
      - top=18mm
      - bottom=20mm
    mainfont: "Pretendard"
    keep-tex: true
  epub: default
bibliography: references.bib
```

Font names/options vary by OS. Inspect installed fonts, render a Korean glyph sheet, and check `pdffonts`.

## Authoring rules

- Use headings for structure, not font hacks.
- Use Quarto cross-references (`@fig-`, `@tbl-`, `@sec-`) and citekeys.
- Keep caption and source adjacent to each asset.
- Redesign wide tables instead of shrinking them below readability.
- Use explicit page breaks sparingly and recheck after pagination changes.
- Separate print-only and EPUB-only material with profiles/conditional content.

## Debug and release

Read the first real TeX/log error. Then check YAML indentation/paths, Korean fonts/glyphs, raw LaTeX, tables, SVGs, and filters. Reproduce with one minimal chapter before a full render.

Render releases from a clean checkout. Save command, versions, checksum, page count, and source commit. Correct QMD/YAML/TeX/SVG source, never the generated PDF.
