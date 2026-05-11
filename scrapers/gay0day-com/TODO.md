# TODO — gay0day-com scraper

## Must Do (Codex)

- [x] Implement `scrape_scene()` in `Gay0Day.py`
  - [x] Parse title from h1 / og:title
  - [x] Parse relative date and convert to approximate ISO 8601
  - [x] Parse og:description for details
  - [x] Parse og:image for cover
  - [x] Parse /models/ links for performers
  - [x] Parse /tags/ links for tags
  - [x] Hardcode studio as "Gay0Day"
- [x] Implement `scrape_performer()` in `Gay0Day.py`
  - [x] Parse name, country, height, weight, image from /models/{slug}/
  - [x] Handle N/A and 0-value fields gracefully
- [x] Implement `search_scenes()` in `Gay0Day.py`
  - [x] Parse search result cards from /search/?q={query}
  - [x] Return list of {title, url} dicts
- [x] Wire up sceneByFragment with fuzzy title matching
- [x] Write `README.md`
- [x] Run against validation examples in `SCRAPER_SPEC.json`
- [x] Check against `workflow/NEW_SCRAPER_CHECKLIST.md`
- [x] Filter generic landing links such as `PornStars` / `Categories`

## Nice to Have

- [x] More robust relative date parsing (years/months/weeks/days ago)
- [ ] Retry logic for transient network errors
- [ ] Logging to stderr for debug output
