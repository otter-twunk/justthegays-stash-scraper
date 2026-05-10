# Perplexity to Codex Handoff

Target site: `https://gay0day.com/`

Target folder: `scrapers/gay0day-com/`

Use `SCRAPER_SPEC.json` first, then this file for human-readable context.

## What Codex Should Do

- Implement the Gay0Day.com scraper from the stub in `Gay0Day.py`
- Create or update:
  - `SCRAPER_SPEC.json`
  - `Gay0Day.yml`
  - `Gay0Day.py`
  - `README.md`
- Preserve all other scrapers elsewhere in the repo
- Validate against `workflow/NEW_SCRAPER_CHECKLIST.md`

## Suggested Hook Modes

- `sceneByURL`
- `sceneByName`
- `sceneByQueryFragment`
- `sceneByFragment`
- `performerByURL`

## Site Notes

- gay0day.com is a custom free gay tube aggregator (no WordPress, no known CMS)
- Scene URL pattern: `https://gay0day.com/videos/{id}/{slug}/`
- Performer URL pattern: `https://gay0day.com/models/{slug}/`
- Search URL: `https://gay0day.com/search/?q={query}`
- No API, no JSON-LD structured data detected
- No Cloudflare/captcha as of May 2026 — standard requests + BeautifulSoup should work
- Use a browser-like User-Agent header on all requests

## Metadata Mapping

See `SCRAPER_SPEC.json` for full selector/parsing notes. Summary:

| Field       | Source                                                          |
|-------------|-----------------------------------------------------------------|
| title       | `h1` or `meta[property='og:title']`                             |
| date        | Relative string near player ("6 years ago") — convert to ISO   |
| details     | `meta[property='og:description']` or inline paragraph           |
| image       | `meta[property='og:image']`                                     |
| performers  | `a[href*='/models/']` links on scene page                       |
| tags        | `a[href*='/tags/']` links on scene page                         |
| studio      | Hardcode `"Gay0Day"` (tube aggregator — no per-scene studio)    |

## Known Limitations

- Date is relative (e.g. "6 years ago"), not absolute — must be converted
- Performer metadata fields are frequently empty or N/A on model pages
- No per-scene studio — constant value only
- Fragment/name matching uses text search; fuzzy match recommended for top result selection

## Validation

- Test `sceneByURL`: `https://gay0day.com/videos/4391/what-str8-jocks-do-behind-the-scenes-at-the-guy-site/`
- Test `performerByURL`: `https://gay0day.com/models/devin-franco/`
- Test `sceneByName` with query: `"devin franco"`
- Test `sceneByFragment` with a title fragment
