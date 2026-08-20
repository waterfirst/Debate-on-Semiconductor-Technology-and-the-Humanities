---
name: quarto-korean-pod-book
description: Plan, write, typeset, preflight, and publish a Korean book with R/Quarto, including Kyobo Purple POD submission, ISBN and publisher administration, print-ready interior and cover PDFs, proof-copy review, Korean trademark filing, and regional small-business IP support. Use when someone wants to write or self-publish a Korean book, convert manuscripts to Quarto, solve Korean PDF typography, calculate a POD cover, prepare Kyobo files, register a publisher or ISBN, protect a book or publisher brand, or preserve evidence of trademark use.
---

# Korean Quarto POD Publishing

Turn an idea into a reproducible publishing project and print-ready submission. Treat platform specifications, fees, forms, deadlines, and support programs as changeable facts: verify them from official sources at the time of action.

## Route the request

1. Identify the stage: idea, manuscript, edit, Quarto conversion, PDF production, POD submission, ISBN, trademark, support application, or post-publication.
2. Ask only for decisions that materially change the result: target reader, format, color/B&W, page count, owner, business region, and deadline.
3. Read only the references needed:
   - Entire order and gates: `references/end-to-end-workflow.md`
   - R/Quarto manuscript and typesetting: `references/quarto-typesetting.md`
   - Kyobo Purple POD and PDFs: `references/kyobo-pod-and-preflight.md`
   - Trademark and small-business support: `references/trademark-and-support.md`
4. Preserve source files and generate reproducibly. Never hand-edit a generated PDF when the source can be corrected.

## Apply the sequence

1. Define the reader problem and one-sentence promise.
2. Build the table of contents and sample chapter before drafting the whole book.
3. Establish sources, citation rules, AI-use rules, permissions, and an asset ledger.
4. Draft in Markdown/QMD; separate content from layout.
5. Perform structural edit, fact-check, rights review, copyedit, and proofread in that order.
6. Freeze trim, paper, color, binding, flaps, and printer template before final pagination.
7. Render the interior; preflight size, fonts, images, color spaces, links, blanks, and overflows.
8. Calculate the spine from the printer's current formula; build the cover after final page count.
9. Complete publisher, ISBN, POD, and metadata administration.
10. Order and inspect a physical proof. Correct source and regenerate.
11. Approve sale only after proof sign-off.
12. Search and design trademark filings early. Apply for support before self-filing when programs may exclude already-filed applications.

## Work with R and Quarto

- Keep `_quarto.yml`, chapter QMDs, bibliography, CSL, images, fonts, filters, and scripts under version control.
- Use Quarto Book with XeLaTeX for Korean PDF output. Verify the fonts actually used and embedded.
- Use semantic Markdown: headings, figures, tables, citations, cross-references, callouts, and parts.
- Keep print and EPUB/HTML differences in profiles or conditional content.
- Render with `quarto render` or `quarto::quarto_render()`.
- Run source audits before rendering and PDF preflight afterward. Use `scripts/preflight_print_pdf.py` when Poppler is available.
- For the reference A5 setup and commands, read `references/quarto-typesetting.md`.

## Produce print PDFs safely

- B&W interior: require true grayscale unless the current printer specification says otherwise.
- Color interior and cover: require actual CMYK.
- Never describe a generic CMYK conversion as `Japan Color 2001 Coated`.
- If an exact ICC is required but unavailable, request a licensed profile or printer-approved conversion. Record the profile and command.
- Verify with `pdfinfo -box`, `pdffonts`, and `pdfimages -list`; visual rendering alone is insufficient.
- Use bleed and trim/crop boxes exactly as required by the current template.
- Never reuse an old spine width. Recalculate after pagination is frozen.

## Handle Kyobo Purple POD

- Verify the current Kyobo notice, template, PDF version, bleed, paper, binding, finish, AI disclosure, ISBN handling, and replacement policy before final files.
- Submit interior and cover as separate PDFs when required.
- Treat project values—A5 148×210 mm, 3 mm bleed, 80 mm flaps, 258 pages, 16 mm spine, 484×216 mm wrap—as examples, not universal specifications.
- Save upload receipt, order record, proof approval, and product page.

## Handle trademarks and support

- Search Korean, English, spacing, pronunciation, and meaning variants in KIPRIS.
- Choose owner, mark type, Nice classes, and designated goods/services from actual use. Books often raise classes 16, 41, and sometimes 9, but confirm official classification rather than filing automatically.
- Korean word, English word, and composite logo filings protect different subject matter.
- Before registration, never use `®`, `등록상표`, or `상표등록 완료`. Plain use of the mark is acceptable.
- Check the current regional IP center and Bizinfo notice before filing. Eligibility, region, self-payment, VAT, exclusions, quantity, and prior-filing rules vary.
- Preserve dated source/PDFs, POD orders, invoices, product-page captures, and physical-book photos.
- Track application number, deadlines, office actions, publication/opposition, registration payment, and renewal.

## Quality gates

Do not call the book ready until:

- audience, promise, manuscript, and metadata agree;
- every quotation, image, table, and font has a source and permission basis;
- citations resolve and no TODO/placeholder remains;
- size, page count, blanks, links, bookmarks, and image resolution are checked;
- fonts are embedded or intentionally outlined/rasterized;
- barcode/ISBN zone, spine, safe areas, bleed, and folds match the template;
- the physical proof is checked for color, binding, gutter, crop, thin lines, and Korean text;
- trademark/support claims are backed by a current official notice.

## Deliver the handoff

Provide source project, render command, final PDFs and checksums, preflight report, proof correction log, POD metadata/upload checklist, ISBN/publisher records, and a trademark search/class/support/evidence checklist.

State assumptions, exact color profile, unresolved risks, and next blocker. This is operational guidance, not a substitute for a patent attorney, tax professional, or printer approval.
