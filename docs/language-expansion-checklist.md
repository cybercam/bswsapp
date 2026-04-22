# Verse Detail Language Expansion Checklist

Use this checklist when enabling verse-detail crossrefs/interlinear/Strong's for a new language after Telugu.

## 1) Data prerequisites
- Confirm language Bible source exists in `src/data/bible_<lang>.json` or remote source.
- Confirm `crossrefs_mobile.json` key format matches `book_chapter_verse`.
- Confirm Strong's dictionary is available (`dictionary.json`).
- Confirm interlinear availability for target books (via `bookMapping.json` + `<ABBREV>.json`).

## 2) Generator configuration
- Add/verify version entry in `VERSIONS`.
- Confirm `HREFLANG` mapping exists for the language.
- Run generation with `--only <lang>`.
- Validate fallback path: local file should be preferred when remote is unavailable.

## 3) QA on representative verses
- Verse with many crossrefs (e.g., John 1:1 equivalent) renders panel correctly.
- Verse with interlinear tokens renders clickable token chips.
- Token click opens lexical drawer with Strong's fields.
- Verse with missing interlinear data shows graceful empty state.

## 4) UX and accessibility checks
- Mobile touch targets are at least 44px.
- Bottom action bar can auto-hide on scroll down and reappear on scroll up.
- Manual close/minimize for bottom bar works.
- Focus states and keyboard interaction remain visible and usable.

## 5) SEO checks
- Canonical URL includes `/book/chapter/verse/`.
- Title and description include verse reference.
- OG/Twitter tags are present.
- Structured data remains valid for verse pages.

## 6) Disk-safe release flow
- Attempt one-pass language build first.
- If disk pressure appears, build book-wise batches.
- Commit/push each batch, then clean local generated artifacts for completed batches.
- Keep source changes consistent across batches.

