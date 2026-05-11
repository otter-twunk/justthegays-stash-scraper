# Gay0Day Scraper

Stash Python script scraper for [gay0day.com](https://gay0day.com/).

Files:

- `Gay0Day.yml`
- `Gay0Day.py`

Install:

1. Copy both files into your Stash `scrapers` directory.
2. Ensure the Python environment Stash uses has `requests` and `beautifulsoup4` installed.
3. In Stash, reload scrapers or restart the app.

## Supported Hooks

| Hook                   | Description                                        |
|------------------------|----------------------------------------------------|
| `sceneByURL`           | Scrape a scene from its `gay0day.com/videos/` URL  |
| `sceneByName`          | Search by title and return scene list              |
| `sceneByQueryFragment` | Search using a query derived from scene metadata   |
| `sceneByFragment`      | Match by title/filename fragment via site search   |
| `performerByURL`       | Scrape a performer from `gay0day.com/models/` URL  |

## URL Patterns

- Scene: `https://gay0day.com/videos/{id}/{slug}/`
- Performer: `https://gay0day.com/models/{slug}/`
- Search: `https://gay0day.com/search/?q={query}`

## Metadata

Extracts: title, date, description, cover image, performers, tags.
Studio is hardcoded as `Gay0Day` (tube aggregator — no per-scene studio field).

## Known Limitations

- Some scene pages expose direct performer profile links, while others only show the generic `PornStars` index link, so performer extraction depends on what the page publishes
- Performer profile fields are often empty on this site
- Search results can be broad for short fragments
- Relative dates are only used as fallback when `VideoObject.uploadDate` is absent

## Notes

- Scene pages currently expose `VideoObject` JSON-LD, so published dates are taken from structured data when available.
- Scene search returns a list of matching result cards from the site's own search page.
- Generic landing links such as `Categories` and `PornStars` are filtered out so only real tag/category/model names are returned.

## Files

| File                             | Purpose                            |
|----------------------------------|------------------------------------|
| `Gay0Day.yml`                    | Stash scraper config               |
| `Gay0Day.py`                     | Python scraper implementation      |
| `SCRAPER_SPEC.json`              | Machine-readable spec for Codex    |
| `PERPLEXITY_TO_CODEX_HANDOFF.md` | Human-readable research notes      |
| `CODEX_PROMPT.md`                | Codex start prompt                 |
| `TODO.md`                        | Implementation checklist           |


## Command-line execution

Run this scraper through the repository CLI wrapper:

```bash
python scripts/run_scraper.py --site gay0day-com --mode <supported-mode> [--url <scene-url>] [--name <scene-name>]
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
