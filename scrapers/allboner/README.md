# allboner.com Stash Scraper

Files:

- `AllBonerScraper.yml`
- `AllBonerScraper.py`
- `SCRAPER_SPEC.json`
- `PERPLEXITY_TO_CODEX_HANDOFF.md`
- `CODEX_PROMPT.md`
- `TODO.md`

Install:

1. Copy `AllBonerScraper.yml` and `AllBonerScraper.py` into your Stash `scrapers` directory.
2. In Stash, reload scrapers or restart the app.

What it supports:

- `sceneByURL`
- `sceneByName`

Platform: KVS (Kernel Video Sharing)

Notes:

- Adult content source: keep scraping metadata-only.
- The scraper sends age-gate cookies (`age_verified=1; kt_tc=1`) and browser-like headers.
- Search uses the site's `/search/<query>/` route and returns scene URLs, titles, and images when available.

Known limitations:

- `allboner.com` is currently protected by a Cloudflare managed challenge for non-browser clients in this environment on May 11, 2026, so command-line fetches can still return empty results even though the site renders in a browser.
- Scene dates can fall back to a best-effort conversion when only relative text such as `8 minutes` is exposed.
- Generic performer placeholders like `pornstar` are filtered out.
- Adult content — keep scraper metadata-only.


## Command-line execution

Run this scraper through the repository CLI wrapper:

```bash
python scripts/run_scraper.py --site allboner --mode <supported-mode> [--url <scene-url>] [--name <scene-name>]
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
