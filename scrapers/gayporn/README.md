# GayPorn Scraper

Stash Python script scraper for [gayporn.com](https://gayporn.com/).

Files:

- `GayPorn.yml`
- `GayPorn.py`

Install:

1. Copy both files into your Stash `scrapers` directory.
2. Ensure the host running Stash has `python` and `curl` available.
3. In Stash, reload scrapers or restart the app.

## Supported Hooks

| Hook                   | Description                                          |
|------------------------|------------------------------------------------------|
| `sceneByURL`           | Scrape a scene from its `gayporn.com/video/` URL     |
| `sceneByName`          | Search by title and return scene candidates          |
| `sceneByQueryFragment` | Search using a query derived from scene metadata     |
| `sceneByFragment`      | Match a single scene from a fragment or direct URL   |
| `performerByURL`       | Scrape a performer from `gayporn.com/pornstars/` URL |

## URL Patterns

- Scene: `https://gayporn.com/video/{slug}`
- Performer: `https://gayporn.com/pornstars/{slug}`
- Search: `https://gayporn.com/search?query={query}`

## Metadata

Scene extraction uses the page's `VideoObject` JSON-LD where available:

- title
- date
- description/details
- cover image
- tags
- studio/channel

Performer extraction uses the performer `ProfilePage` JSON-LD and page avatar where available:

- name
- profile URL
- avatar image
- description/details

## Known Limitations

- Live testing in May 2026 showed `curl` succeeds more reliably than `requests` against this site, so the scraper shells out to `curl` for fetching.
- Scene pages expose strong structured metadata, but they do not publish a reliable performer list for the specific scene; scene performer output is therefore omitted instead of guessed.
- Performer pages appear to expose only sparse profile metadata beyond name, image, and description.
- Site search can return broad matches for short fragments, so `sceneByFragment` uses fuzzy matching before resolving a single result.

## Files

| File                             | Purpose                            |
|----------------------------------|------------------------------------|
| `GayPorn.yml`                    | Stash scraper config               |
| `GayPorn.py`                     | Python scraper implementation      |
| `SCRAPER_SPEC.json`              | Machine-readable spec for Codex    |
| `PERPLEXITY_TO_CODEX_HANDOFF.md` | Human-readable research notes      |
| `CODEX_PROMPT.md`                | Codex start prompt                 |
| `TODO.md`                        | Implementation checklist           |


## Command-line execution

Run this scraper through the repository CLI wrapper:

```bash
python scripts/run_scraper.py --site gayporn --mode <supported-mode> [--url <scene-url>] [--name <scene-name>]
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
