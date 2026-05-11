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

- Adult content source: keep scraping metadata-only.
- Scene URLs are slug-based and should look like `https://thisvid.com/videos/<slug>/`.
- The scraper returns verified public metadata from the scene page: title, canonical URL, description, cover image, tags/categories, and the internal ThisVid video ID as `code`.
- Public scene pages expose the uploader, but not a trustworthy performer list; this scraper does not invent performers from uploader/member data.

Known limitations:

- `sceneByName`, fragment matching, and performer scraping are not implemented.
- Many public scene pages do not expose a reliable publish date in anonymous HTML; `date` is returned only when the page includes a parseable `Added:` value.
- ThisVid appears to expose uploader/member links more consistently than performer/model links, so performer metadata is intentionally left blank for now.


## Command-line execution

Run this scraper through the repository CLI wrapper:

```bash
python scripts/run_scraper.py --site thisvid --mode <supported-mode> [--url <scene-url>] [--name <scene-name>]
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
