# everydayporn.co Stash Scraper

Files:

- `EverydayPornScraper.yml`
- `EverydayPornScraper.py`
- `_vendor/` (bundled Python dependency for Cloudflare-aware fetching)
- `SCRAPER_SPEC.json`
- `PERPLEXITY_TO_CODEX_HANDOFF.md`
- `CODEX_PROMPT.md`
- `TODO.md`

Install:

1. Copy `EverydayPornScraper.yml` and `EverydayPornScraper.py` into your Stash `scrapers` directory.
2. In Stash, reload scrapers or restart the app.

What it supports:

- `sceneByURL`
- `sceneByName`

Platform: KVS-like tube platform

Notes:

- Adult content source: keep scraping metadata-only.
- Scene pages expose `VideoObject` JSON-LD; the scraper prefers that over OG tags.
- The site is currently fronted by a Cloudflare managed challenge for non-browser requests, so the scraper ships a bundled `cloudscraper` dependency in `_vendor/`.
- `sceneByName` uses the live `https://www.everydayporn.co/search/?q=...` search endpoint and returns ranked results from the first results page.

Known limitations:

- Performer/model links not present on sampled scene pages.
- Studio/source links not confirmed — may not be populated for all content.
- Search pagination appears to be AJAX-driven; this scraper currently searches the first HTML page only.
- Platform appears KVS-like but exact CMS unconfirmed — avoid hardcoding KVS-specific assumptions.
