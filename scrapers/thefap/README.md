# thefap.net Stash Scraper

Files:

- `TheFapScraper.yml`
- `TheFapScraper.py`
- `SCRAPER_SPEC.json`
- `PERPLEXITY_TO_CODEX_HANDOFF.md`
- `CODEX_PROMPT.md`
- `TODO.md`

Install:

1. Copy `TheFapScraper.yml` and `TheFapScraper.py` into your Stash `scrapers` directory.
2. In Stash, reload scrapers or restart the app.

What it supports:

- `sceneByURL`
- `performerByURL`

Platform: Custom social/content platform (not KVS)

Notes:

- Public scene URLs use `https://thefap.net/<performer>-<id>/<source>/i<number>`.
- Public performer URLs use `https://thefap.net/<performer>-<id>/`.
- The scraper is metadata-only and uses custom HTML parsing with no third-party Python dependencies.
- Scene images are derived from the public embedded player URL when available.

Known limitations:

- Public scene pages do not expose a reliable publish date, so `date` is currently omitted.
- Public scene pages expose very little structured metadata; titles, thumbnails, and performer names are inferred from page HTML and URL structure.
- Some content may require login or may become unavailable behind rate limiting or Cloudflare checks.
