# xHamster Stash Scraper

Stash scraper for [xhamster.com](https://xhamster.com/).

## Supported hooks

| Hook | Status |
|---|---|
| `sceneByURL` | Supported |
| `sceneByName` | Supported |
| `sceneByQueryFragment` | Supported |
| `sceneByFragment` | Supported |
| `performerByURL` | Supported |

## Install

1. Copy `XHamster.py` and `XHamster.yml` into your Stash `scrapers/` directory.
2. Reload scrapers in Stash or restart the app.

## Files

- `SCRAPER_SPEC.json` — machine-friendly contract: supported modes, URL patterns, metadata mappings
- `PERPLEXITY_TO_CODEX_HANDOFF.md` — detailed research notes and implementation guidance for Codex
- `CODEX_PROMPT.md` — concise Codex starting prompt focused on this folder
- `XHamster.py` — Python script scraper implementation
- `XHamster.yml` — Stash scraper definition file
- `TODO.md` — implementation checklist

## Platform notes

- Custom tube site using a large `window.initials` JSON blob on scene, search, and performer pages
- No JSON-LD required for the main scrape flow
- Scene URLs: `https://xhamster.com/videos/{slug}-{idHashSlug}`
- Performer URLs: `https://xhamster.com/pornstars/{slug}`
- Search: `https://xhamster.com/search/{query}`

## Known limitations

- Performer bio details (height, measurements, social links, etc.) are not exposed cleanly in `window.initials`; performer scraping is intentionally minimal
- Some scenes have no pornstar metadata; performers fall back to `isPornstar` tags only
- Search-based title and fragment matching is conservative; long or non-Latin titles may return no match instead of a weak guess
- In Australia, xHamster currently injects an age-verification banner into page HTML. The scraper ignores it and reads the embedded metadata instead.

## Test URLs

- Scenes:
  - `https://xhamster.com/videos/day-1-seven-slave-intake-xhk23el`
  - `https://xhamster.com/videos/the-training-of-number-seven-day-one-xhu06Uo`
- Performers:
  - `https://xhamster.com/pornstars/coffee-brown`
  - `https://xhamster.com/pornstars/emma-haize`

## Codex start

```
Use the files in scrapers/xhamster-com/ and build the scraper.
```


## Command-line execution

Run this scraper through the repository CLI wrapper:

```bash
python scripts/run_scraper.py --site xhamster-com --mode <supported-mode> [--url <scene-url>] [--name <scene-name>]
```

Standardized output format:

```json
{"results": [{"title": "Example", "url": "https://example.com/video"}]}
```

Configuration:

- Runtime dependencies are installed from the repository root `requirements.txt`.
- No site credentials are required for default metadata scraping.

Testing:

```bash
pytest -q
```

The test suite includes a CLI smoke test for this scraper (`unsupportedMode` path) to verify executable entrypoint and valid JSON output.
