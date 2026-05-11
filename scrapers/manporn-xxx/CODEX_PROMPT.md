# Codex Prompt — ManPorn Scraper

Create a working Stash scraper for https://manporn.xxx/ in this repository.

## Start

All research is already done. Use the files in `scrapers/manporn-xxx/` to build the scraper:

1. Read `SCRAPER_SPEC.json` — this is the implementation contract
2. Read `PERPLEXITY_TO_CODEX_HANDOFF.md` — this has full site notes and field mapping
3. Use `scrapers/justthegays-tv/JustTheGays.py` as the reference implementation pattern
4. Use `scrapers/boyfriendtv-com/BoyFriendTV.py` as the nearest comparable scraper (same Cloudflare + JSON-LD pattern)
5. Create `ManPorn.py` and complete `ManPorn.yml` in `scrapers/manporn-xxx/`
6. Update `TODO.md` as tasks are completed
7. Update the root `README.md` to add `scrapers/manporn-xxx` to the current scrapers list

## Requirements

- Python 3, stdlib only (+ optional certifi for SSL)
- urllib request + curl subprocess fallback (same as justthegays-tv pattern)
- Supported hooks: `sceneByURL` and `performerByURL` only
- `sceneByName`, `sceneByQueryFragment`, `sceneByFragment` — do NOT implement; search is expected to be Cloudflare-blocked
- Parse all scene metadata from JSON-LD `VideoObject` block
- Set age-gate cookie in all HTTP requests (try `age_verified=1`; confirm name on first fetch and adjust)
- Realistic browser User-Agent and Accept headers required
- Handle missing or empty fields gracefully (return empty string, not error)
- One scraper per site — do not modify other scraper folders

## Key Facts

- Scene URL pattern: `https://manporn.xxx/videos/{id}/{slug}/`
- Performer URL pattern: `https://manporn.xxx/models/{slug}/`
- Scene pages expected accessible to headless fetch with correct headers + age-gate cookie
- Performer + search pages expected to trigger Cloudflare JS challenge
- All scene metadata expected in a JSON-LD `VideoObject` block on the scene page
- Fallback for performers: `a[href^="/models/"]` anchors; for tags: `a[href^="/categories/"]` or `a[href^="/tags/"]`
- Studio is always `ManPorn` (constant)
- Validated scene URL: `https://manporn.xxx/videos/3400273/hot-threesome-action-with-indian-pornstars/`
