# Perplexity to Codex Handoff

Target site: `SITE_URL`

Target folder: `scrapers/<site-folder>/`

Use this file as the site-specific Codex handoff.

## What Codex Should Do

- Build a working Stash scraper for this site in this folder
- Create or update:
  - `SCRAPER_SPEC.json`
  - the scraper `.yml`
  - the backing Python script
  - `README.md`
- Preserve existing scrapers elsewhere in the repo
- Update the root `README.md` with this scraper folder

## Suggested Hook Modes

- Replace with the hook modes supported by the research

## Site Notes

- Replace with Perplexity's implementation summary

## Metadata Mapping

- Replace with field mapping and likely selectors or parsing notes
- Mirror the same data in `SCRAPER_SPEC.json`

## Known Limitations

- Replace with blockers, missing metadata, or weak areas

## Validation

- Test `sceneByURL` against a live scene page if possible
- Test `performerByURL` if performer pages exist
- Test `sceneByName` if site search is usable
- Test fragment matching if practical
