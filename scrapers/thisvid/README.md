# thisvid.com Stash Scraper

Files:

- `ThisVidScraper.yml`
- `ThisVidScraper.py`
- `SCRAPER_SPEC.json`
- `PERPLEXITY_TO_CODEX_HANDOFF.md`
- `CODEX_PROMPT.md`
- `TODO.md`

Install:

1. Copy `ThisVidScraper.yml` and `ThisVidScraper.py` into your Stash `scrapers` directory.
2. In Stash, reload scrapers or restart the app.

What it supports:

- `sceneByURL`

Platform: Custom community video site

Notes:

- Scraper implementation pending — this folder contains Perplexity research handoff files for Codex.
- Adult content source: keep scraping metadata-only.
- Scene URLs are slug-based; listing-first discovery is required.

Known limitations:

- Scene URL structure uses slugs, not numeric IDs — listing-first discovery required.
- Performer/member pages not confirmed during research.
- Search support unconfirmed.
- Full metadata availability requires live scene page fetch during implementation.
