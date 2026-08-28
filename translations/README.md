# English and Japanese editions

This directory contains the publication sources and prepublication build artifacts for the English and Japanese editions of the Korean manuscript. The artifacts become upload-ready only after the issued ISBNs, translated-edition publication dates, and confirmed legal publisher name are applied and validation is rerun.

| Language | Title | Build outputs |
|---|---|---|
| English (`en-US`) | *Semiconductor Interviews: Answer the King’s Question* | `en/output/epub/`, `en/output/pdf/`, `en/output/cover/` |
| Japanese (`ja-JP`) | 『半導体面接――王の問いに答えよ』 | `ja/output/epub/`, `ja/output/pdf/`, `ja/output/cover/` |

The editions retain the original 19-chapter publication structure, source URLs, tables, footnotes, data cutoff, and debate scenarios. Prose, headings, captions, figures, cover copy, metadata, author biography, and reader instructions are localized for each market. Classical Chinese source passages and official English technical names remain where their source identity matters.

## Build

Run from the repository root:

```powershell
python -m pip install -r requirements-book.txt
npm install
python scripts/build_translation_books.py
python scripts/validate_translation_books.py
```

Build requirements are Quarto, XeLaTeX, Node.js with Sharp, Python with Pillow and pypdf, and the Windows CJK fonts declared in each locale’s `print-style.tex`. Use `--locale en` or `--locale ja` to build or validate one edition. The build locates tools from `PATH`; `QUARTO_BIN`, `NODE_BIN`, `TEX_BIN`, and `SHARP_NODE_MODULES` can override local paths.

The build creates a reflowable EPUB with an embedded cover, an A5 portrait PDF with an image-only first-page cover and bookmarks, and a standalone 1748×2480 cover PNG. The validation script checks manuscript structure, local resources, EPUB packaging and metadata, image dimensions, PDF page size, bookmarks, language metadata, encryption, and embedded fonts.

EPUB files should also be checked with the current production release of [W3C EPUBCheck](https://github.com/w3c/epubcheck/releases) before upload. Pass `--java <java executable> --epubcheck-jar <epubcheck.jar>` to the validation script, or set `JAVA_BIN` and `EPUBCHECK_JAR`, to include that check in the same validation run.

The default validation command is for prepublication technical review. Before any EPUB store upload, run it again with `--publication-ready`, `--release-metadata <json>`, `--java <java executable>`, and `--epubcheck-jar <epubcheck.jar>`. The JSON must contain both `en` and `ja` objects with exact `title`, `subtitle`, `author`, `language`, EPUB `isbn`, `publication_date`, and legal `publisher` values. The final gate rejects duplicate or Korean-print ISBNs, compares the issued catalog values with `_quarto.yml`, the OPF, and the copyright page, and requires EPUBCheck to pass. Google PDF ISBNs remain a separate publication check.

## Google Play Books handoff

Create one Book Catalog entry per language. Use the reflowable EPUB 3.0 file as the primary reading format and upload the complete PDF to the same language entry so readers can also use the original-page view. The standalone cover PNG may be supplied separately if the Partner Center requests a cover file. Do not upload the `-interior-a5.pdf` intermediate.

Google accepts both EPUB and PDF, recommends supplying both, and requires a complete, unencrypted PDF. EPUB must contain its front cover. Covers must be at least 640 pixels and no more than 7200 pixels on either dimension; embedded EPUB images must not exceed 3200 pixels. See Google’s [EPUB guidance](https://support.google.com/books/partner/answer/3316879?hl=en), [file guidelines](https://support.google.com/books/partner/answer/3424254?hl=en), and [PDF configuration guidance](https://support.google.com/books/partner/answer/107073?hl=en).

The publication plan uses formal ISBNs rather than Google-only GGKEYs. Because the English and Japanese editions are different language editions, and EPUB and PDF are different publicly distributed electronic formats, request four ISBNs: English EPUB, English PDF, Japanese EPUB, and Japanese PDF. In each Google entry, use the EPUB ISBN as the primary identifier and connect the PDF ISBN as a related identifier. See the [ISBN application packet](ISBN_APPLICATION.md).

No translated-edition ISBN or release date has been invented. Add issued identifiers to the sources and rebuild all deliverables before publication; do not reuse the Korean print ISBN for either translated edition.

## Kyobo Book Centre handoff

For Kyobo, register the English and Japanese EPUB editions as two separate ebook products. Use the EPUB 3.0 reflowable file and the standalone RGB JPEG cover for each language; keep the PDFs for Google Play and internal review unless a separate Kyobo PDF product is explicitly approved. Kyobo uses the same two EPUB ISBNs included in the four-ISBN plan above; it does not require two additional ISBNs for these same EPUB editions.

Direct ebook registration requires a Korean corporate or sole-proprietor business partner account. Mark both editions as generative-AI-assisted because AI supported research, translation, editing, and image generation. See the [Kyobo submission guide](KYOBO_EBOOK_SUBMISSION.md) and [Kyobo listing copy](kyobo-listing.md).
