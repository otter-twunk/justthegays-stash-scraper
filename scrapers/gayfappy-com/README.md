# Gay Fappy scraper

This folder contains the research handoff and implementation stub for a Stash scraper targeting [Gay Fappy](https://gayfappy.com/).

## Status

Research and Codex handoff files are present.

Implementation of the Python scraper logic is still pending.

## Recommended hooks

- `sceneByURL`
- `sceneByName`
- `sceneByQueryFragment`
- `sceneByFragment`

## Not currently recommended

- `performerByURL`, because no dedicated performer page pattern was identified during research.

## Site characteristics

- WordPress-style site structure
- Post URLs use `/index.php/{id}/{slug}/`
- Search uses `/?s={query}`
- Content mix includes videos, photos, and gifs, so search filtering matters
- Metadata is available in server-rendered HTML and should be accessible with `requests` + `BeautifulSoup`

## Files

- `SCRAPER_SPEC.json` — machine-friendly implementation spec
- `PERPLEXITY_TO_CODEX_HANDOFF.md` — human-readable handoff for Codex
- `CODEX_PROMPT.md` — minimal startup prompt
- `TODO.md` — implementation checklist
- `GayFappy.yml` — Stash scraper config stub
- `GayFappy.py` — Python implementation stub
