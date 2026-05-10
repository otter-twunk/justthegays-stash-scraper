# Perplexity to Codex Handoff

Target site: `https://justthegays.tv/`

Target folder: `scrapers/justthegays-tv/`

Use `SCRAPER_SPEC.json` first, then this file for human-readable context.

## What Codex Should Do

- Maintain and improve the JustTheGays.tv scraper in this folder
- Create or update:
  - `SCRAPER_SPEC.json`
  - `JustTheGays.yml`
  - `JustTheGays.py`
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

- This scraper targets the `.tv` site and already supports scene, search, fragment, and performer URL flows.
- Search-based hooks are an important part of this scraper's behavior.

## Metadata Mapping

- Follow `SCRAPER_SPEC.json` and the current `JustTheGays.py` implementation.

## Known Limitations

- Keep behavior stable unless a site change requires a parser update.

## Validation

- Test `sceneByURL` against a live scene page if possible
- Test `performerByURL` if performer pages exist
- Test `sceneByName`
- Test fragment matching
