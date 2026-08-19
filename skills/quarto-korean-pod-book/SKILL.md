---
name: quarto-korean-pod-book
description: Transform a Korean Quarto manuscript into a publication-ready A5 POD interior, EPUB, full-wrap wing cover, review packet, and reproducible GitHub handoff. Use for book-scale writing, editing, evidence verification, data charts, chapter illustrations, Korean typography, PDF/EPUB rendering, ISBN/barcode placement, spine calculation, POD preflight, or adapting an existing Quarto repository into a new independently published book.
---

# Quarto Korean POD Book

Treat the repository as the source of truth. Preserve user work, keep source and generated artifacts separate, and never infer ISBN, price, publication date, printer specifications, endorsements, or page count.

## 1. Establish the publication contract

Read the project instructions and inspect `_quarto.yml`, chapter files, styles, filters, build scripts, output folders, cover assets, and Git status. Record:

- trim size, paper, binding, color mode, wings, coating, bleed, and target price;
- title, subtitle, author, publisher, print ISBN, ebook ISBN, and publication date;
- intended reader, training outcome, chapter template, and citation standard;
- final deliverables and whether a review packet is required.

Mark undecided metadata as pending. Do not place placeholder identifiers in final artifacts. Treat print and ebook ISBNs as separate identifiers.

Read [references/publishing-specs.md](references/publishing-specs.md) when calculating print geometry or preparing POD files.

## 2. Edit before illustrating

Freeze the selected table of contents before final layout. Remove weak or overlapping chapters instead of shrinking type to meet a price target. For a debate-training book, make every chapter carry a distinct decision:

1. one concrete question;
2. historical or conceptual framing;
3. attributable evidence with denominator, unit, year, and status;
4. genuinely opposed answers rather than two straw men and one universal compromise;
5. an AI research plan that separates acquisition, verification, judgment, and debate;
6. a role-specific case with clearly labelled hypothetical values;
7. a 90-second answer that makes an actual choice and names reversal conditions;
8. topic-specific follow-up questions and direct sources.

Audit all model answers as a set. Do not teach “always choose the conditional answer.” Allow stop, proceed, reject, and bounded decisions when the evidence supports them.

When the user requests multi-agent work, assign non-overlapping roles: manuscript editor, independent red team, and illustration art director. Keep one lead agent responsible for final integration, rendering, and release.

## 3. Verify evidence

Prefer primary institutional, regulatory, standards, corporate filing, or peer-reviewed sources. For every number, label it as one of:

- observed historical fact;
- estimate;
- forecast;
- scenario or sensitivity;
- interview-only hypothetical value.

Do not mix different periods, accounting concepts, denominators, or valuation types in one total. Replace unstable casualty, combat-performance, breaking-news, or ongoing-conflict numbers with durable historical evidence unless the current date is essential and verified immediately before release.

Do not use the author’s essay as authority for an external fact. Author essays may supply voice and motivation in a preface or epilogue, with the platform and URL identified.

## 4. Build charts and illustrations

Finish a chapter’s text before commissioning its illustration.

For charts:

- use restrained color plus shape, pattern, direct labels, or line style so categories remain distinct in grayscale;
- show actual years at proportionate positions on time axes;
- distinguish actual, estimate, and forecast visually;
- keep labels readable at final A5 size and avoid relying on a legend alone;
- export screen color and print grayscale variants, then inspect both.

For illustrations, use the image-generation capability only after reading its applicable skill. Keep a consistent brief: warm white hanji, monochrome ink and graphite, pale gray wash, bright negative space, two or three symbolic objects, no text, numbers, logos, watermark, decorative border, or photorealism. Compare every result with the final chapter question before accepting it.

## 5. Typeset for Korean A5 reading

Start from a comfortable mobile-reading layout: about 10.5pt body type, 1.3–1.4 line spacing, generous paragraph rhythm, and an A5 text block near 110–115mm. Keep tables and figures inside the text block.

Prevent split footnotes, single-character page starts, stranded final words, and headings at the bottom of a page. Give ordinal table columns minimal width and distribute the remainder by actual sentence length. Use a different but compatible face and a bordered box for the book-question prompt.

Render after structural edits. Do not claim layout quality from source inspection alone.

## 6. Render and preflight

Render PDF and EPUB from the same frozen sources. Then:

1. confirm trim dimensions, page count, even/odd page logic, embedded fonts, metadata, and link behavior;
2. render representative and suspicious PDF pages to PNG and inspect title pages, question boxes, charts, dense tables, footnotes, chapter endings, and page transitions;
3. inspect the EPUB navigation, chapter count, cover, images, and reflow;
4. run source, manuscript, visual, and artifact audits supplied by the repository;
5. rerender every dependent artifact after any source change.

Read [references/red-team-checklist.md](references/red-team-checklist.md) for the independent final pass.

## 7. Calculate the cover last

Calculate the spine only after the interior PDF is final. Run:

```powershell
python scripts/calc_cover_geometry.py --pages 262 --paper-thickness-mm 0.12 --wing-mm 80
```

Use the printer or POD platform’s value when it differs from the estimate. Rebuild the full-wrap cover whenever page count, paper, binding, wing size, or bleed changes. Put the assigned barcode in a quiet white area at least as large as the platform requirement, and place author and publisher legibly on the spine when its width permits.

## 8. Package and hand off

Keep these outputs distinct:

- interior PDF at trim size;
- print full-wrap cover PDF with bleed and TrimBox;
- reader preview PDF;
- EPUB;
- optional reviewer PDF and email text;
- README, project SKILL, publication guide, and reproducibility notes.

If endorsements are absent, do not leave endorsement headings, blank pages, or metadata promises in the publication files.

Before Git publication, inspect the diff, preserve unrelated user files, run all validations, commit intentionally, and push the intended branch. Report exact page count, spine assumption, ISBN status, outputs, tests, and remaining printer-dependent checks.

Use `scripts/audit_quarto_book.py` for a portable structural audit and `scripts/calc_cover_geometry.py` for deterministic cover geometry.
