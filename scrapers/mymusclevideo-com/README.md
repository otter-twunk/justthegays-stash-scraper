# MyMuscleVideo Scraper

Stash scraper for [mymusclevideo.com](https://mymusclevideo.com/) — a custom muscle/bodybuilder video tube site.

## Supported Modes

| Mode | Supported |
|---|---|
| `sceneByURL` | ✅ Yes |
| `sceneByName` | ✅ Yes |
| `performerByURL` | ❌ No (login-gated) |
| `sceneByFragment` | ❌ No |
| `sceneByQueryFragment` | ❌ No |

## Scraped Fields

| Field | Source |
|---|---|
| Title | `og:title` meta tag |
| Date | `og:video:release_date` meta property |
| Description | `og:description` meta property |
| Cover Image | `og:image` (300×226 JPG) |
| Tags | `/video/tag/` anchor links on scene page, with `video:tag` / `keywords` fallback |
| Studio | Constant: `MyMuscleVideo` |
| Performers | ❌ Not available |

## Install

1. Copy `MyMuscleVideo.yml` and `MyMuscleVideo.py` into your Stash `scrapers/` folder.
2. Restart Stash.
3. The scraper will appear as **MyMuscleVideo** in the scraper list.

## Usage

- **Scene by URL**: paste a scene URL such as `https://mymusclevideo.com/107027/sexy-guy-muscle/`
- **Scene by Name**: enter a title string — the scraper queries `/search/video/?s=` and returns matching candidates from the search results page

## Known Limitations

- **No performer data**: scene pages show only the uploader account, not named performers.
- **Low-resolution cover**: `og:image` is 300×226px — no full-res public alternative.
- **Model pages are login-gated**: `performerByURL` is not implemented.
- **Visible date is relative** (`"5 years ago"`): the scraper uses `og:video:release_date` for the real date.
- **Search results can contain near-duplicates**: `sceneByName` deduplicates by video ID and returns search-page metadata, not a fully scraped scene payload.


## Command-line execution

Run this scraper through the repository CLI wrapper:

```bash
python scripts/run_scraper.py --site mymusclevideo-com --mode <supported-mode> [--url <scene-url>] [--name <scene-name>]
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
