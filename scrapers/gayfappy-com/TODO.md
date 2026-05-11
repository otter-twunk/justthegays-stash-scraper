# TODO — gayfappy-com scraper

## Must Do (Codex)

- [ ] Implement `scrape_scene()` in `GayFappy.py`
  - [ ] Parse title from `h1.entry-title` or page title fallback
  - [ ] Parse absolute date from `.entry-meta time` or byline text
  - [ ] Parse readable details from `.entry-content`
  - [ ] Parse `og:image` with fallback to first post image or poster
  - [ ] Parse tags from WordPress tag links
  - [ ] Infer performers conservatively from tag labels
  - [ ] Hardcode studio as `"Gay Fappy"`
- [ ] Implement `search_scenes()` in `GayFappy.py`
  - [ ] Query `/?s={query}`
  - [ ] Parse search result cards/articles
  - [ ] Keep likely scene URLs only
  - [ ] Rank results by title similarity
- [ ] Wire `sceneByFragment` to search and best-match resolution
- [ ] Write `README.md`
- [ ] Run against validation examples in `SCRAPER_SPEC.json`
- [ ] Check against `workflow/NEW_SCRAPER_CHECKLIST.md`

## Nice to Have

- [ ] Category-aware filtering to prefer `videos` posts over photos/gifs in search results
- [ ] Better heuristics for separating performer tags from generic tags
- [ ] Retry logic for transient network issues
- [ ] Debug logging to stderr
- [ ] Optional future investigation into whether any reliable performer page pattern exists
