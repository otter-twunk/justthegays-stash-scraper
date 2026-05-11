# TODO — gayhardfuck-com scraper

## Must Do (Codex)

- [ ] Implement `scrape_scene()` in `GayHardFuck.py`
  - [ ] Parse title from og:title or `<title>` (strip ' - GayHardFuck.com')
  - [ ] Parse relative date and convert to approximate ISO 8601
  - [ ] Parse og:description for details
  - [ ] Parse og:image for cover image
  - [ ] Parse /models/ links for performers (handle absent gracefully)
  - [ ] Parse /tags/ links for tags
  - [ ] Hardcode studio as "GayHardFuck"
- [ ] Implement `search_scenes()` in `GayHardFuck.py`
  - [ ] Parse video card results from /search/?q={query}
  - [ ] Skip tag-suggestion section at top of results page
  - [ ] Return list of {title, url} dicts
- [ ] Wire up sceneByFragment with fuzzy title matching
- [ ] Write `README.md`
- [ ] Run against validation examples in `SCRAPER_SPEC.json`
- [ ] Check against `workflow/NEW_SCRAPER_CHECKLIST.md`

## Not Supported

- `performerByURL` — /models/ index is empty; do not implement

## Nice to Have

- [ ] More robust relative date parsing (years/months/weeks/days ago)
- [ ] Retry logic for transient network errors
- [ ] Logging to stderr for debug output
