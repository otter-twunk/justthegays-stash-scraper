# Codex Prompt — TNAFlix Scraper

Create a working Stash scraper for https://www.tnaflix.com/ in this repository.

## Start

All research is already done. Use the files in `scrapers/tnaflix-com/` to build the scraper:

1. Read `SCRAPER_SPEC.json` — this is the implementation contract
2. Read `PERPLEXITY_TO_CODEX_HANDOFF.md` — full site notes and field mapping
3. Use `scrapers/justthegays-tv/JustTheGays.py` as the reference implementation pattern
4. Create `TNAFlix.py` and `TNAFlix.yml` in `scrapers/tnaflix-com/`
5. Update `TODO.md` as tasks are completed
6. Update the root `README.md` to add `scrapers/tnaflix-com` to the scrapers list

## Requirements

- Python 3, stdlib only (+ optional certifi for SSL)
- urllib request + curl subprocess fallback (same as justthegays-tv pattern)
- Supported hooks: `sceneByURL`, `sceneByName`, `performerByURL`
- `sceneByQueryFragment`, `sceneByFragment` — do NOT implement
- Parse scene metadata from JSON-LD `VideoObject` block
- `thumbnailUrl` in JSON-LD is a plain string — access directly, do NOT subscript with `[0]`
- Performers: `a[class*="badge-kiss"][href^="/profile/"]` anchor text; exclude `badge-unverified`
- Tags: first path segment of scene URL, replace hyphens with spaces, title-case
- Description: if value is `"No description provided"` (case-insensitive), return empty string
- Studio: hardcoded constant `"TNAFlix"`
- `sceneByName`: GET `https://www.tnaflix.com/search?what={query}`, extract video URLs, fetch best match via `SequenceMatcher`
- `performerByURL`: fetch `/profile/{slug}`, name from `<h1>`, image from `div.ph-avatar img[src]`
- Handle all missing fields gracefully

## Validation Targets

- `sceneByURL`: `https://www.tnaflix.com/amateur-porn/Best-Of-Lolo-Ferrari/video563066`
  - title=`Best Of Lolo Ferrari`, date=`2013-12-09`, performers=[`Lolo Ferrari`], tags=[`Amateur Porn`], studio=`TNAFlix`
- `performerByURL`: `https://www.tnaflix.com/profile/lolo-ferrari`
  - name=`Lolo Ferrari`, image URL populated
- `sceneByName`: query `lolo ferrari` → returns matching results

## Reference Files

- Pattern: `scrapers/justthegays-tv/JustTheGays.py`
- Checklist: `workflow/NEW_SCRAPER_CHECKLIST.md`
- Template: `templates/site-template/` (if present)
