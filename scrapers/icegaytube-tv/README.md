# IceGayTube Scraper

Stash scraper for [icegaytube.tv](https://www.icegaytube.tv/).

## Supported Modes

| Mode | Supported | Notes |
|---|---|---|
| sceneByURL | ✅ | No Cloudflare detected — scene pages accessible with standard headers |
| sceneByName | ✅ | Search endpoint accessible at `/search/scenes?q={query}` |
| performerByURL | ✅ | Performer pages appear publicly accessible |
| sceneByQueryFragment | ❌ | Not implemented — lower priority |
| sceneByFragment | ❌ | Not implemented — lower priority |

## Installation

1. Copy `IceGayTube.py` and `IceGayTube.yml` into your Stash `scrapers/` directory.
2. Reload scrapers in Stash (Settings → Scrapers → Reload).

## Usage

- **Scene scraping**: Paste a `https://www.icegaytube.tv/movies/{id}/{slug}` URL into a scene's URL field and click the scrape button.
- **Scene by name**: Use the scrape-by-name function in Stash with the scene title.
- **Performer scraping**: Paste a `https://www.icegaytube.tv/pornstars/{slug}` URL into a performer's URL field.

## Metadata Coverage

| Field | Source |
|---|---|
| Title | `og:title` meta tag (strip ' at Ice Gay Tube' suffix) |
| Date | JSON-LD `VideoObject.uploadDate` or `meta[name='date']` |
| Details | `og:description` meta tag |
| Cover image | `og:image` meta tag |
| Performers | `a[href*='/pornstars/']` anchor text on scene page |
| Tags | `a[href*='/category/']` anchor text on scene page |
| Studio | Channel link on scene page; fallback constant: IceGayTube |

## Known Limitations

- JSON-LD `VideoObject` presence was inferred from site type — verify on a live page.
- Date may be a relative string on some scenes; scraper handles this with a fallback.
- Performer list may be empty on amateur/untagged clips.
- Studio/channel may be absent on some scenes.

## Implementation Notes

- No Cloudflare challenge detected during research. Standard urllib/curl fetch with a realistic User-Agent and `age_verified=1` cookie should be sufficient.
- Primary metadata source is `og:*` meta tags. JSON-LD is used as a secondary fallback.
- See `SCRAPER_SPEC.json` for the full research record and `PERPLEXITY_TO_CODEX_HANDOFF.md` for implementation notes.


## Command-line execution

Run this scraper through the repository CLI wrapper:

```bash
python scripts/run_scraper.py --site icegaytube-tv --mode <supported-mode> [--url <scene-url>] [--name <scene-name>]
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
