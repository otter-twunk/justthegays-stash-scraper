# Gay Fappy Scraper

Stash Python scraper for [gayfappy.com](https://gayfappy.com/).

Files:

- `GayFappy.yml`
- `GayFappy.py`

Install:

1. Copy both files into your Stash `scrapers` directory.
2. Ensure the Python environment Stash uses has `requests` and `beautifulsoup4` installed.
3. Reload scrapers in Stash or restart the app.

## Supported Hooks

| Hook | Description |
|---|---|
| `sceneByURL` | Scrape a scene from a `gayfappy.com/index.php/{id}/{slug}/` URL |
| `sceneByName` | Search the site and return matching scenes |
| `sceneByQueryFragment` | Search using a title/name/filename-derived fragment |
| `sceneByFragment` | Resolve the best scene match from a fragment and scrape it |

## URL Patterns

- Scene: `https://gayfappy.com/index.php/{id}/{slug}/`
- Search: `https://gayfappy.com/?s={query}`

## Metadata

Extracts title, date, details, cover image, tags, and conservative performer guesses from tag labels.
Studio is hardcoded as `Gay Fappy`.

## Usage Notes

- Search results are biased toward posts in the `Videos` category when mixed results are returned.
- `sceneByFragment` only auto-resolves a result when the top title match is strong enough; otherwise it returns an empty object instead of guessing.
- Performer inference is intentionally conservative and may leave `performers` empty when tags look ambiguous.

## Known Limitations

- Some posts expose only a title-like description, so `details` can be very short.
- Search result cards often omit explicit heading elements; the scraper falls back to image alt text and excerpt text.
- Tag labels mix performer names with generic categories, so some real performers may be missed.
- The site appears to be an aggregator, so the scraper uses the site name as the studio instead of trying to infer an upstream source.

## Files

| File | Purpose |
|---|---|
| `GayFappy.yml` | Stash scraper config |
| `GayFappy.py` | Python scraper implementation |
| `SCRAPER_SPEC.json` | Machine-readable implementation spec |
| `PERPLEXITY_TO_CODEX_HANDOFF.md` | Human-readable research notes |
| `CODEX_PROMPT.md` | Folder-local Codex startup prompt |
| `TODO.md` | Implementation checklist |


## Command-line execution

Run this scraper through the repository CLI wrapper:

```bash
python scripts/run_scraper.py --site gayfappy-com --mode <supported-mode> [--url <scene-url>] [--name <scene-name>]
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
