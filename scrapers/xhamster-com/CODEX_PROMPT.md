# Codex Prompt — xHamster Scraper

Create a working Stash scraper for https://xhamster.com/ in this repository.

## Start

All research is already done. Use the files in `scrapers/xhamster-com/` to build the scraper:

1. Read `SCRAPER_SPEC.json` — this is the implementation contract
2. Read `PERPLEXITY_TO_CODEX_HANDOFF.md` — this has full site notes and field mapping
3. Use `scrapers/boyfriendtv-com/BoyFriendTV.py` as the reference implementation pattern
4. Create `XHamster.py` and `XHamster.yml` in `scrapers/xhamster-com/`
5. Update `TODO.md` as tasks are completed
6. Update the root `README.md` to add `scrapers/xhamster-com` to the current scrapers list

## Requirements

- Python 3, stdlib only (+ optional requests for convenience)
- urllib request + curl subprocess fallback (same pattern as existing scrapers)
- Supported hooks: `sceneByURL`, `sceneByName`, `sceneByQueryFragment`, `sceneByFragment`, `performerByURL`
- Parse all scene metadata from `window.initials` JSON blob on the scene page
- Set `age_verified=1` cookie in all HTTP requests
- Realistic browser User-Agent and Accept headers required
- Handle missing or empty fields gracefully (return empty string/list, not error)
- One scraper per site — do not modify other scraper folders

## Key Facts

- Scene URL pattern: `https://xhamster.com/videos/{slug}-{idHashSlug}` (e.g. `xhk23el`)
- Performer URL pattern: `https://xhamster.com/pornstars/{slug}`
- Search URL pattern: `https://xhamster.com/search/{query}`
- All three page types respond to headless fetch without Cloudflare challenge
- All scene metadata is in `window.initials.videoModel`, `window.initials.videoEntity`, and `window.initials.videoTagsComponent`
- Parse with `json.JSONDecoder().raw_decode(html[html.find('window.initials=')+16:])`
- Studio = `videoModel.channelModel.channelName`
- Date = `videoModel.created` (UNIX seconds) → UTC date string
- Performers = `videoEntity.pornstarModels` + tags where `isPornstar==true`
- Tags = tags where `isCategory==true` or `isTag==true`
- Validated scene: `https://xhamster.com/videos/day-1-seven-slave-intake-xhk23el`
