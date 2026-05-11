# ManPorn Scraper

Stash scraper for [manporn.xxx](https://manporn.xxx/).

## Supported Modes

| Mode | Supported | Notes |
|---|---|---|
| sceneByURL | ✅ | Scene pages expected to bypass Cloudflare with correct headers + age-gate cookie |
| performerByURL | ⚠️ Partial | Performer pages may trigger Cloudflare JS challenge; returns name + gender fallback |
| sceneByName | ❌ | Search pages expected to be Cloudflare-blocked |
| sceneByQueryFragment | ❌ | Depends on search — blocked |
| sceneByFragment | ❌ | Depends on search — blocked |

## Installation

1. Copy `ManPorn.py` and `ManPorn.yml` into your Stash `scrapers/` directory.
2. Reload scrapers in Stash (Settings → Scrapers → Reload).

## Usage

- **Scene scraping**: Paste a `https://manporn.xxx/videos/{id}/{slug}/` URL into a scene's URL field and click the scrape button.
- **Performer scraping**: Paste a `https://manporn.xxx/models/{slug}/` URL into a performer's URL field.

## Metadata Coverage

| Field | Source |
|---|---|
| Title | JSON-LD VideoObject.name |
| Date | JSON-LD VideoObject.uploadDate |
| Details | JSON-LD VideoObject.description |
| Cover image | JSON-LD VideoObject.thumbnailUrl[0] |
| Performers | JSON-LD VideoObject.actor[].name |
| Tags | JSON-LD VideoObject.keywords[] |
| Studio | Constant: ManPorn |

## Known Limitations

- Scene descriptions on user-uploaded content may be a comma-separated tag list, not a narrative synopsis.
- Performer details (photo, bio) may not be available due to Cloudflare protection on performer pages.
- No per-scene channel/studio metadata — studio is always `ManPorn`.
- Age-gate cookie name (`age_verified=1`) must be confirmed on first live fetch.

## Implementation Notes

- Site is protected by Cloudflare. Scene pages are expected to respond correctly to a headless fetch with a realistic Firefox/Linux User-Agent, correct `Accept`/`Accept-Language` headers, a `Referer` header, and an age-gate cookie.
- All scene metadata is expected in the `application/ld+json` VideoObject block on each scene page.
- Nearest comparable scraper in this repo: `scrapers/boyfriendtv-com/` (same Cloudflare + JSON-LD pattern).
- See `SCRAPER_SPEC.json` for the full research record and `PERPLEXITY_TO_CODEX_HANDOFF.md` for implementation notes.


## Command-line execution

Run this scraper through the repository CLI wrapper:

```bash
python scripts/run_scraper.py --site manporn-xxx --mode <supported-mode> [--url <scene-url>] [--name <scene-name>]
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
