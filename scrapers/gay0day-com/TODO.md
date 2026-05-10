# TODO — gay0day-com scraper

## Must Do (Codex)

- [ ] Implement `scrape_scene()` in `Gay0Day.py`
  - [ ] Parse title from h1 / og:title
  - [ ] Parse relative date and convert to approximate ISO 8601
  - [ ] Parse og:description for details
  - [ ] Parse og:image for cover
  - [ ] Parse /models/ links for performers
  - [ ] Parse /tags/ links for tags
  - [ ] Hardcode studio as "Gay0Day"
- [ ] Implement `scrape_performer()` in `Gay0Day.py`
  - [ ] Parse name, country, height, weight, image from /models/{slug}/
  - [ ] Handle N/A and 0-value fields gracefully
- [ ] Implement `search_scenes()` in `Gay0Day.py`
  - [ ] Parse search result cards from /search/?q={query}
  - [ ] Return list of {title, url} dicts
- [ ] Wire up sceneByFragment with fuzzy title matching
- [ ] Write `README.md`
- [ ] Run against validation examples in `SCRAPER_SPEC.json`
- [ ] Check against `workflow/NEW_SCRAPER_CHECKLIST.md`

## Nice to Have

- [ ] More robust relative date parsing (years/months/weeks/days ago)
- [ ] Retry logic for transient network errors
- [ ] Logging to stderr for debug output
