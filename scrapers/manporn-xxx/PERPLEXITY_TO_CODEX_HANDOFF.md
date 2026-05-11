# Perplexity to Codex Handoff — ManPorn

Create a working Stash scraper for https://manporn.xxx/ in this repository.

## Repository

- Repo name: `otter-twunk/my-scrapers`
- Structure: one scraper per folder under `scrapers/<site-folder>/`
- This scraper lives in: `scrapers/manporn-xxx/`

## Your Job

- Read the research in `SCRAPER_SPEC.json` and use it as the implementation contract
- Create `ManPorn.py` and `ManPorn.yml` inside this folder
- Keep `SCRAPER_SPEC.json`, `PERPLEXITY_TO_CODEX_HANDOFF.md`, and `CODEX_PROMPT.md` as-is
- Update `TODO.md` as you complete tasks
- Follow official Stash scraper conventions
- Preserve all other scrapers in the repo
- Update the root `README.md` to add `scrapers/manporn-xxx` to the current scrapers list

## Implementation Requirements

- Use Python 3 for the script scraper
- Use the same pattern as `scrapers/justthegays-tv/JustTheGays.py` (stdlib-only, urllib + curl subprocess fallback, JSON-LD parsing)
- Support **sceneByURL** and **performerByURL** — these are the only reliable hooks (see Cloudflare notes below)
- Handle missing metadata gracefully — return empty string, not an error
- No third-party dependencies beyond Python stdlib and optional `certifi`

## Site Research Summary

### Platform

Custom gay tube site at manporn.xxx. Not WordPress. Cloudflare protection active. Site branding: "ManPorn" / "MANPORN.XXX".

### URL Patterns

- Scene pages: `https://manporn.xxx/videos/{id}/{slug}/`
- Performer pages: `https://manporn.xxx/models/{slug}/`
- Search pages: `https://manporn.xxx/search/?q={query}` — **expected to be blocked by Cloudflare for headless requests**

### Cloudflare Notes — Critical

- **Scene pages** are expected to work with a realistic Firefox/Linux UA, `Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8`, `Accept-Language: en-US,en;q=0.5`, `Referer: https://manporn.xxx/`, and an age-gate cookie. Python urllib and curl subprocess both expected to work.
- **Performer pages** (`/models/{slug}/`) and **search pages** (`/search/?q=`) are expected to trigger the Cloudflare JS challenge. Do not implement `sceneByName`, `sceneByQueryFragment`, `sceneByFragment`, or `performerByURL` with live fetches without a JS-capable workaround.
- For `performerByURL`: return minimal data (name parsed from URL slug, gender hardcoded to `'Male'`) without a live fetch, or attempt the fetch and gracefully return partial data on Cloudflare block.
- **Age-gate cookie**: try `age_verified=1` first (same pattern as boyfriendtv-com). If the page still redirects to an age gate, inspect `Set-Cookie` headers on the first response and adjust the cookie name accordingly. Document the correct name in `TODO.md`.

### Metadata — Scene Page

All key scene metadata expected in a `application/ld+json` block of type `VideoObject`:

| Stash field | Source |
|---|---|
| title | `VideoObject.name` |
| date | `VideoObject.uploadDate` (ISO-8601, strip to YYYY-MM-DD) |
| details | `VideoObject.description` (may be tag list, not narrative) |
| image | `VideoObject.thumbnailUrl[0]` (CDN URL) |
| performers | `VideoObject.actor[].name` |
| tags | `VideoObject.keywords[]` |
| studio | Constant: `ManPorn` |

Fallbacks:
- title: `og:title` meta → `<title>` strip suffix
- image: `og:image` meta
- performers: `a[href^="/models/"]` anchors in HTML body
- tags: `a[href^="/categories/"]` or `a[href^="/tags/"]` anchor text

### Metadata — Performer Page

Performer pages may return a Cloudflare challenge for script requests. If the page is fetchable, look for:
- `og:title` or `<h1>` for name
- `og:image` for photo
- Inline HTML bio fields for country, birthdate, etc. (exact selectors TBD — document in TODO.md after first successful fetch)
- Hardcode `gender: 'Male'`

### Validated Example URLs

- Scene: `https://manporn.xxx/videos/3400273/hot-threesome-action-with-indian-pornstars/`
  - title: `Hot threesome action with indian pornstars`
  - date: `2024-05-01` (approximate — confirm from JSON-LD uploadDate)
  - studio: `ManPorn`
- Performers: `https://manporn.xxx/models/reign/`, `https://manporn.xxx/models/zbynek-onderka/`

## Known Limitations

1. `sceneByName`, `sceneByQueryFragment`, and `sceneByFragment` are **not supported** — search is expected to be Cloudflare-gated.
2. `performerByURL` is **partially blocked** — performer pages expected to trigger CF challenge. Return name-from-slug + `gender: Male` as fallback.
3. Scene `description` is often a comma-separated tag list, not a narrative synopsis.
4. No per-scene studio/channel field; always return `ManPorn`.
5. Age-gate cookie name must be confirmed on first live fetch — expected `age_verified=1` but may differ.

## Validation Requirements

- Test `sceneByURL` against: `https://manporn.xxx/videos/3400273/hot-threesome-action-with-indian-pornstars/`
- Confirm JSON-LD is parsed correctly and all fields are populated
- Test `performerByURL` against: `https://manporn.xxx/models/reign/` — document result (may be partial due to CF)
- Confirm correct age-gate cookie name and document in `TODO.md`

## Repo Helpers

- Reference implementation: `scrapers/justthegays-tv/JustTheGays.py` (same stdlib pattern)
- Nearest comparable scraper: `scrapers/boyfriendtv-com/BoyFriendTV.py` (same Cloudflare + JSON-LD pattern)
- Template: `templates/site-template/SiteScraper.py` and `SiteScraper.yml`
- Checklist: `workflow/NEW_SCRAPER_CHECKLIST.md`
