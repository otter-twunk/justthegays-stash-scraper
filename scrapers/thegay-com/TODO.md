# TODO — TheGay.com scraper

## Blocked on (Codex must do first)

- [x] **Confirm internal API endpoint** — confirmed from the shipped frontend bundle:
  `/api/json/video/86400/{million_bucket}/{thousand_bucket}/{video_id}.json`

## Implementation

- [x] Implement `scrape_scene()` in `TheGay.py` using confirmed API endpoint
- [x] Map all JSON fields per `SCRAPER_SPEC.json` metadata_mapping section
- [x] Handle missing/null fields gracefully
- [x] Verify `age_verified=1` cookie is sent on all requests
- [x] Handle API response wrapper keys (`data`, `video`, or direct root object)

## Validation

- [x] Test `sceneByURL` against `https://www.thegay.com/video/748987/bareback-gay-sex-with-jerk/`
- [ ] Confirm title, date, image, performers, tags are populated
- [x] Confirm graceful empty result when URL does not match a real video

## Docs

- [x] Write `README.md` with install instructions and known limitations
- [x] Root `README.md` already includes `scrapers/thegay-com/`; no shared update needed

## Out of scope (until further research)

- sceneByName — SPA search, no server-rendered results
- sceneByQueryFragment / sceneByFragment — same blocker
- performerByURL — SPA performer pages, no server-rendered data
