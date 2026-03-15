# German By Verb (GBV)

## Project Overview

This repository contains 191 markdown files, one per German verb stem, each listing the stem verb and all its prefixed variants with English translations. The files were OCR-extracted from a PDF (GBV.pdf) and parsed by prefix-based stem matching.

## File Types

### Original files (`{stem}.md`)
Raw OCR-derived entries. Known issues:
- Adjective-only entries (e.g. ENTLEGEN, GELEGEN) are formatted as verbs with "to" prefixes that don't work grammatically
- Homographs with different stress/part-of-speech (e.g. ÜBERLEGEN verb vs. adjective, VERLEGEN verb vs. adjective, UNTERLEGEN verb vs. adjective) are conflated into one entry
- Duplicate translations within entries
- OCR artifacts: misspellings (e.g. "to highlite"), leaked source annotations (e.g. "(new spell.=zu legen)"), ungrammatical forms ("to fixed", "to situated")
- No indication of separability (sep./insep.)
- No sense grouping — all translations are in a flat semicolon-separated list regardless of how different the senses are

### Edited files (`{stem}_edited.md`)
Cleaned-up versions that fix the issues above. When creating an edited version of an original file:
1. Mark each prefixed verb as **(sep.)** or **(insep.)**
2. Convert adjective-only entries (like ENTLEGEN, GELEGEN) to **(adj.)** format without "to" prefixes
3. Where a verb and adjective share the same headword (VERLEGEN, UNTERLEGEN, ÜBERLEGEN), separate them with an em dash: `verb translations — (adj.) adjective translations`
4. Group translations by sense domain using italicized labels: `*(nautical)* to berth; to dock; to moor`
5. Deduplicate translations
6. Remove OCR artifacts and fix misspellings
7. Strip "to" from adjective/adverb translations
8. Retain the original entry order: stem verb first, then prefixed variants alphabetically

### Guide files (`{stem}_guide.md`)
Interpretive guides for English speakers. For each prefixed verb:
1. State the prefix's general spatial/conceptual meaning (e.g. "ein-" = "in, into, inward")
2. Explain how the prefix combines with the stem to produce the compound verb's meaning
3. Offer a literal English translation as a memorization aid (e.g. *einlegen* = "lay in")
4. Give concrete examples showing the image or metaphor at work
5. Close with a "Patterns Worth Noting" section covering: stem stays physical while prefixes go abstract; separable prefixes are spatial/concrete; inseparable prefixes are transformative/opaque; parallels and divergences with English

Use `legen_edited.md` and `legen_guide.md` as models for all other stems.
