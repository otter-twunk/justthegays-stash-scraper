# TODO — gayfappy-com scraper

## Must Do (Codex)

- [x] Implement `scrape_scene()` in `GayFappy.py`
  - [x] Parse title from `h1.entry-title` or page title fallback
  - [x] Parse absolute date from `time.post-date` or page text fallback
  - [x] Parse readable details from `.entry-content`
  - [x] Parse `og:image` with fallback to post images
  - [x] Parse tags from WordPress tag links
  - [x] Infer performers conservatively from tag labels
  - [x] Hardcode studio as `"Gay Fappy"`
- [x] Implement `search_scenes()` in `GayFappy.py`
  - [x] Query `/?s={query}`
  - [x] Parse search result cards/articles
  - [x] Keep likely scene URLs only
  - [x] Rank results by title similarity and bias video posts
- [x] Wire `sceneByFragment` to search and best-match resolution
- [x] Write `README.md`
- [x] Run against validation examples in `SCRAPER_SPEC.json`
- [x] Check against `workflow/NEW_SCRAPER_CHECKLIST.md`

## Nice to Have

- [x] Category-aware filtering to prefer `videos` posts over photos/gifs in search results
- [ ] Better heuristics for separating performer tags from generic tags
- [ ] Retry logic for transient network issues
- [ ] Debug logging to stderr
- [ ] Optional future investigation into whether any reliable performer page pattern exists
