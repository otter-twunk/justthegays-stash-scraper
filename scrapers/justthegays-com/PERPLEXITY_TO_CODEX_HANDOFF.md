# Perplexity to Codex Handoff

Target site: `https://justthegays.com/`

Target folder: `scrapers/justthegays-com/`

Use `SCRAPER_SPEC.json` first, then this file for human-readable context.

## What Codex Should Do

- Maintain and improve the JustTheGays.com scraper in this folder
- Create or update:
  - `SCRAPER_SPEC.json`
  - `JustTheGaysCom.yml`
  - `JustTheGaysCom.py`
  - `README.md`
- Preserve other scrapers elsewhere in the repo
- Update the root `README.md` if supported hooks or repo guidance change

## Suggested Hook Modes

- `sceneByURL`
- `sceneByName`
- `sceneByQueryFragment`
- `sceneByFragment`
- `performerByURL`

## Site Notes

- This scraper targets the `.com` WordPress-style site.
- Search-based flows help compensate for pages that do not expose complete metadata directly.

## Metadata Mapping

- Follow `SCRAPER_SPEC.json` and the current `JustTheGaysCom.py` implementation.

## Known Limitations

- Some scene pages do not expose performer/category taxonomy cleanly.

## Validation

- Test `sceneByURL` against a live scene page if possible
- Test `performerByURL` if performer pages exist
- Test `sceneByName`
- Test fragment matching
