# GayHardFuck Scraper

Stash Python script scraper for [gayhardfuck.com](https://www.gayhardfuck.com/).

## Supported Hooks

| Hook                   | Description                                              |
|------------------------|----------------------------------------------------------|
| `sceneByURL`           | Scrape a scene from its `gayhardfuck.com/videos/` URL    |
| `sceneByName`          | Search by title and return scene list                    |
| `sceneByQueryFragment` | Search using a query derived from scene metadata         |
| `sceneByFragment`      | Match by title/filename fragment via site search         |

> `performerByURL` is not supported — performer profile pages are not available on this site.

## URL Patterns

- Scene: `https://www.gayhardfuck.com/videos/{id}/{slug}/`
- Search: `https://www.gayhardfuck.com/search/?q={query}`

## Metadata

Extracts: title, approximate date, description, cover image, performers, tags.
Studio is hardcoded as `GayHardFuck` (tube aggregator — no per-scene studio field).

Live pages currently do not expose reliable `/models/` or `/tags/` links on the tested scenes, so the scraper falls back to parsing performer names and keyword-style tags from the scene description when that text is structured enough.

## Usage Notes

- `sceneByURL` returns full scene metadata for `https://www.gayhardfuck.com/videos/...` pages
- `sceneByName` returns search results from `https://www.gayhardfuck.com/search/?q=...`
- `sceneByQueryFragment` uses the same search flow and also accepts a direct scene URL
- `sceneByFragment` is conservative: it returns `{}` when the best site-search match does not contain enough of the requested title tokens
- The YAML keeps the repo's existing `python` command convention; validation in this workspace was run with `python3`

## Known Limitations

- Date is a relative string (e.g. "3 years ago") — converted to approximate ISO date
- Performer profile pages do not exist on this site; `/models/` index is empty
- No API or structured data — relies on HTML parsing
- Site search can miss exact titles, so `sceneByFragment` may return `{}` instead of risking a wrong scene
- Tags may be sparse or absent on some scene pages and may depend on description parsing

## Files

| File                             | Purpose                            |
|----------------------------------|------------------------------------|
| `GayHardFuck.yml`                | Stash scraper config               |
| `GayHardFuck.py`                 | Python scraper implementation      |
| `SCRAPER_SPEC.json`              | Machine-readable spec for Codex    |
| `PERPLEXITY_TO_CODEX_HANDOFF.md` | Human-readable research notes      |
| `CODEX_PROMPT.md`                | Codex start prompt                 |
| `TODO.md`                        | Implementation checklist           |


## Command-line execution

Run this scraper through the repository CLI wrapper:

```bash
python scripts/run_scraper.py --site gayhardfuck-com --mode <supported-mode> [--url <scene-url>] [--name <scene-name>]
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
