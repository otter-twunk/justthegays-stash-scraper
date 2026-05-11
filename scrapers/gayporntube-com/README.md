# GayPornTube Scraper

Stash scraper for [gayporntube.com](https://www.gayporntube.com/).

## Supported Modes

| Mode | Supported | Notes |
|---|---|---|
| sceneByURL | ✅ | Reliable — JSON-LD VideoObject on every scene page |
| sceneByName | ✅ | Search endpoint is accessible with no bot protection |
| sceneByQueryFragment | ✅ | Best-effort via search |
| sceneByFragment | ✅ | Best-effort via search |
| performerByURL | ❌ | Site has no performer/model pages |

## Installation

1. Copy `GayPornTube.py` and `GayPornTube.yml` into your Stash `scrapers/` directory.
2. Reload scrapers in Stash (Settings → Scrapers → Reload).

## Usage

- **Scene scraping**: Paste a `https://www.gayporntube.com/video/{id}/{slug}` URL into a scene's URL field and click the scrape button.
- **Scene by name**: Use the scene title in Stash's search-by-name scrape flow.

## Metadata Coverage

| Field | Source |
|---|---|
| Title | JSON-LD VideoObject.name |
| Date | JSON-LD VideoObject.uploadDate |
| Details | JSON-LD VideoObject.description (sanitised — often empty) |
| Cover image | JSON-LD VideoObject.thumbnailUrl |
| Performers | Not available |
| Tags | div.video-info-tags + div.video-info-categories anchor text |
| Studio | Constant: GayPornTube |

## Known Limitations

- No performer metadata — site does not have model/performer profile pages.
- Scene descriptions are often star-rating emoji only (`⭐⭐⭐⭐⭐`) and will be returned as empty.
- Tags are sparse; typically 0–2 per scene.
- Category links (`/channels/`) are merged into the tags list for richer coverage.
- Title matching for fragment modes is best-effort; results depend on filename quality.

## Verified URLs

- `https://www.gayporntube.com/video/2041527/ass-addiction`
- `https://www.gayporntube.com/video/2041520/help-cumming-00`
- `https://www.gayporntube.com/search/videos/?q=bareback`

## Implementation Notes

- No Cloudflare protection — standard Firefox UA with `age_verified=1` cookie is sufficient.
- All scene metadata is extracted from the `application/ld+json` VideoObject block.
- See `SCRAPER_SPEC.json` for the full research record and selectors.
- See `PERPLEXITY_TO_CODEX_HANDOFF.md` for full implementation guidance.


## Command-line execution

Run this scraper through the repository CLI wrapper:

```bash
python scripts/run_scraper.py --site gayporntube-com --mode <supported-mode> [--url <scene-url>] [--name <scene-name>]
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
