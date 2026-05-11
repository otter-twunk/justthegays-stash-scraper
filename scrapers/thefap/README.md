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

Platform: Custom social/content platform (not KVS)

Notes:

- Scraper implementation pending — this folder contains Perplexity research handoff files for Codex.
- Adult content source: keep scraping metadata-only.
- Custom platform — all parsing logic must be written from scratch.
- Some content may require login.

Known limitations:

- Not a standard KVS or WordPress install — custom parsing required throughout.
- Some content may require login.
- Post/video/profile entity distinction needs clarification during implementation.
- Full metadata availability requires live page fetches.
