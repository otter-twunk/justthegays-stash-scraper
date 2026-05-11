# TODO — gayhardfuck-com scraper

## Must Do (Codex)

- [x] Implement `scrape_scene()` in `GayHardFuck.py`
  - [x] Parse title from og:title or `<title>` (strip ' - GayHardFuck.com')
  - [x] Parse relative date and convert to approximate ISO 8601
  - [x] Parse og:description for details
  - [x] Parse og:image for cover image
  - [x] Parse /models/ links for performers (handle absent gracefully)
  - [x] Parse /tags/ links for tags
  - [x] Hardcode studio as "GayHardFuck"
- [x] Implement `search_scenes()` in `GayHardFuck.py`
  - [x] Parse video card results from /search/?q={query}
  - [x] Skip tag-suggestion section at top of results page
  - [x] Return list of {title, url} dicts
- [x] Wire up sceneByFragment with fuzzy title matching
- [x] Write `README.md`
- [x] Run against validation examples in `SCRAPER_SPEC.json`
- [x] Check against `workflow/NEW_SCRAPER_CHECKLIST.md`

## Not Supported

- `performerByURL` — /models/ index is empty; do not implement

## Nice to Have

- [x] More robust relative date parsing (years/months/weeks/days ago)
- [ ] Retry logic for transient network errors
- [ ] Logging to stderr for debug output
