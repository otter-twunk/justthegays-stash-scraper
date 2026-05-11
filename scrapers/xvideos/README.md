# xvideos.com Stash Scraper

Files:

- `XVideosScraper.yml`
- `XVideosScraper.py`
- `SCRAPER_SPEC.json`
- `PERPLEXITY_TO_CODEX_HANDOFF.md`
- `CODEX_PROMPT.md`
- `TODO.md`

Install:

1. Copy `XVideosScraper.yml` and `XVideosScraper.py` into your Stash `scrapers` directory.
2. In Stash, reload scrapers or restart the app.

What it supports:

- `sceneByURL`
- `sceneByName`
- `performerByURL`

Platform: Custom/proprietary (XVideos in-house platform)

Notes:

- Metadata-only scraper for live XVideos scene pages, search results, and profile pages.
- Uses embedded `window.xv.conf`, JSON-LD, and stable HTML fallbacks.
- No external Python dependencies are required. If `certifi` is installed it will be used automatically.

Known limitations:

- `video_models` is frequently empty on amateur or uploader-driven pages.
- Performer pages use `/profiles/` rather than a dedicated studio or pornstar route.
- Signed CDN media URLs expire; do not store or reuse stream URLs.
- Search results return listing metadata only; full details come from `sceneByURL`.
- Scene performer extraction is usually limited to the main uploader/profile link shown on the page.


## Command-line execution

Run this scraper through the repository CLI wrapper:

```bash
python scripts/run_scraper.py --site xvideos --mode <supported-mode> [--url <scene-url>] [--name <scene-name>]
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
