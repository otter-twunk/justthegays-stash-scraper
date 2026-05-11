# Perplexity to Codex Handoff

Target site: `https://www.gayhardfuck.com/`

Target folder: `scrapers/gayhardfuck-com/`

Use `SCRAPER_SPEC.json` first, then this file for human-readable context.

## What Codex Should Do

- Implement the GayHardFuck.com scraper from the stub in `GayHardFuck.py`
- Create or update:
  - `SCRAPER_SPEC.json`
  - `GayHardFuck.yml`
  - `GayHardFuck.py`
  - `README.md`
- Preserve all other scrapers elsewhere in the repo
- Validate against `workflow/NEW_SCRAPER_CHECKLIST.md`

## Supported Hook Modes

- `sceneByURL`
- `sceneByName`
- `sceneByQueryFragment`
- `sceneByFragment`

> `performerByURL` is NOT supported — the `/models/` index is empty and performer profile pages do not exist on this site as of May 2026.

## Site Notes

- gayhardfuck.com is a custom free gay tube aggregator (no WordPress, no known CMS)
- Scene URL pattern: `https://www.gayhardfuck.com/videos/{id}/{slug}/`
- Search URL: `https://www.gayhardfuck.com/search/?q={query}`
- No API, no JSON-LD structured data detected
- No Cloudflare/captcha as of May 2026 — standard requests + BeautifulSoup should work
- Always use `https://www.` prefix — the site redirects bare http:// and non-www
- Use a browser-like User-Agent header on all requests
- Search results page has two sections: (1) suggested tag links at top, (2) video cards below — parse only video cards

## Metadata Mapping

See `SCRAPER_SPEC.json` for full selector/parsing notes. Summary:

| Field      | Source                                                              |
|------------|---------------------------------------------------------------------|
| title      | `meta[property='og:title']` or `<title>` (strip ' - GayHardFuck.com') |
| date       | Relative string near player ("3 years ago") — convert to ISO       |
| details    | `meta[property='og:description']` or inline paragraph              |
| image      | `meta[property='og:image']`                                         |
| performers | `a[href*='/models/']` links on scene page (may be absent)           |
| tags       | `a[href*='/tags/']` links on scene page                             |
| studio     | Hardcode `"GayHardFuck"` (tube aggregator — no per-scene studio)    |

## Known Limitations

- Date is relative (e.g. "3 years ago"), not absolute — must be converted to approximate ISO
- No performer scraping — `/models/` index is empty, performer profile pages are not available
- No per-scene studio — constant value only
- Tags may be sparse or absent on some scene pages
- Fragment/name matching uses text search; fuzzy match recommended for top result selection

## Validation

- Test `sceneByURL`: `https://www.gayhardfuck.com/videos/6019/pavel-jeremy-screen-test-raw-full-contact/`
- Test `sceneByName` with query: `"bareback"`
- Test `sceneByFragment` with a title fragment
- Search test: `https://www.gayhardfuck.com/search/?q=bareback`
