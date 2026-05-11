# TheGay.com Scraper

Stash scraper for [TheGay.com](https://www.thegay.com/).

## Supported modes

| Mode | Supported |
|---|---|
| `sceneByURL` | ✅ |
| `sceneByName` | ❌ |
| `sceneByQueryFragment` | ❌ |
| `sceneByFragment` | ❌ |
| `performerByURL` | ❌ |

## Why limited support?

TheGay.com is part of the **TXXX network** and runs as a pure Vue SPA. The server returns
an empty HTML shell for every route — no `<title>`, no og: tags, no JSON-LD. All metadata
is loaded by JavaScript from an internal JSON API. Scene pages can be scraped by extracting
the video ID from the URL and querying the bucketed API route directly. Search and performer
routes have no server-rendered data and cannot be scraped without a JS-capable headless browser.

## Install

1. Copy `TheGay.yml` and `TheGay.py` into your Stash scrapers directory.
2. Reload scrapers in Stash.

## Usage

- Paste a TheGay.com scene URL into the Stash scrape URL field:
  `https://www.thegay.com/video/{id}/{slug}/`
- Click **Scrape**.

## Requirements

- Python 3.7+
- No external Python packages required (`certifi` is used if available for SSL but is optional)

## Implementation notes

- The scraper uses the live endpoint pattern confirmed from the shipped frontend bundle:
  `/api/json/video/86400/{million_bucket}/{thousand_bucket}/{video_id}.json`
- It automatically sends `age_verified=1` plus the scene URL as the `Referer`.
- Tags come from the payload's `categories` object when present.

## Known limitations

- Description may be a comma-separated tag list rather than a prose synopsis on
  user-uploaded clips.
- Studio is always hard-coded to `TheGay.com` — no per-scene channel field in the API.
- Many scenes do not expose performer names in the API. When `models`, `pornstars`,
  and `models_suggested` are empty, the scraper returns the rest of the scene data
  without performers.
- Performer and search modes are not supported (SPA-only routes).

## Notes

- An `age_verified=1` cookie is sent automatically by the scraper.
- Live validation on `https://www.thegay.com/video/748987/bareback-gay-sex-with-jerk/`
  currently returns title, date, image, and tags successfully.


## Command-line execution

Run this scraper through the repository CLI wrapper:

```bash
python scripts/run_scraper.py --site thegay-com --mode <supported-mode> [--url <scene-url>] [--name <scene-name>]
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
