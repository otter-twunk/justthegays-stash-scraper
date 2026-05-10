# Codex Prompt — BoyFriendTV Scraper

Create a working Stash scraper for https://www.boyfriendtv.com/ in this repository.

## Start

All research is already done. Use the files in `scrapers/boyfriendtv-com/` to build the scraper:

1. Read `SCRAPER_SPEC.json` — this is the implementation contract
2. Read `PERPLEXITY_TO_CODEX_HANDOFF.md` — this has full site notes and field mapping
3. Use `scrapers/justthegays-tv/JustTheGays.py` as the reference implementation pattern
4. Create `BoyFriendTV.py` and `BoyFriendTV.yml` in `scrapers/boyfriendtv-com/`
5. Update `TODO.md` as tasks are completed
6. Update the root `README.md` to add `scrapers/boyfriendtv-com` to the current scrapers list

## Requirements

- Python 3, stdlib only (+ optional certifi for SSL)
- urllib request + curl subprocess fallback (same as justthegays-tv pattern)
- Supported hooks: `sceneByURL` and `performerByURL` only
- `sceneByName`, `sceneByQueryFragment`, `sceneByFragment` — do NOT implement; search is Cloudflare-blocked
- Parse all scene metadata from JSON-LD `VideoObject` block
- Set `age_verified=1` cookie in all HTTP requests
- Realistic browser User-Agent and Accept headers required
- Handle missing or empty fields gracefully (return empty string, not error)
- One scraper per site — do not modify other scraper folders

## Key Facts

- Scene URL pattern: `https://www.boyfriendtv.com/videos/{id}/{slug}/`
- Performer URL pattern: `https://www.boyfriendtv.com/pornstars/{slug}/`
- Scene pages are accessible to headless fetch; performer + search pages trigger Cloudflare JS challenge
- All scene metadata is in a JSON-LD `VideoObject` block on the scene page
- Studio is always `BoyFriendTV` (constant)
- Validated scene: `https://www.boyfriendtv.com/videos/1426460/selector/`
