# Perplexity to Codex Handoff — BoyFriendTV

Create a working Stash scraper for https://www.boyfriendtv.com/ in this repository.

## Repository

- Repo name: `otter-twunk/my-scrapers`
- Structure: one scraper per folder under `scrapers/<site-folder>/`
- This scraper lives in: `scrapers/boyfriendtv-com/`

## Your Job

- Read the research in `SCRAPER_SPEC.json` and use it as the implementation contract
- Create `BoyFriendTV.py` and `BoyFriendTV.yml` inside this folder
- Keep `SCRAPER_SPEC.json`, `PERPLEXITY_TO_CODEX_HANDOFF.md`, and `CODEX_PROMPT.md` as-is
- Update `TODO.md` as you complete tasks
- Follow official Stash scraper conventions
- Preserve all other scrapers in the repo
- Update the root `README.md` to add `scrapers/boyfriendtv-com` to the current scrapers list

## Implementation Requirements

- Use Python 3 for the script scraper
- Use the same pattern as `scrapers/justthegays-tv/JustTheGays.py` (stdlib-only, urllib + curl subprocess fallback, JSON-LD parsing)
- Support **sceneByURL** and **performerByURL** — these are the only reliable hooks (see Cloudflare notes below)
- Handle missing metadata gracefully — return empty string, not an error
- No third-party dependencies beyond Python stdlib and optional `certifi`

## Site Research Summary

### Platform

Custom tube site. Not WordPress. Cloudflare protection is active on most routes.

### URL Patterns

- Scene pages: `https://www.boyfriendtv.com/videos/{id}/{slug}/`
- Performer pages: `https://www.boyfriendtv.com/pornstars/{slug}/`
- Search pages: `https://www.boyfriendtv.com/search/?q={query}` — **blocked by Cloudflare for headless requests**

### Cloudflare Notes — Critical

- **Scene pages work** with a realistic Firefox/Linux UA, `Accept: text/html`, `Accept-Language: en-US,en;q=0.5`, and the cookie `age_verified=1`. Python urllib and curl subprocess both work.
- **Performer pages** and **search pages** consistently trigger the Cloudflare JS challenge. Do not implement sceneByName, sceneByQueryFragment, sceneByFragment, or performerByURL with live fetches without a JS-capable workaround.
- For performerByURL: return minimal data (name parsed from URL slug, gender hardcoded to 'Male') without a live fetch, or attempt the fetch and gracefully return partial data on Cloudflare block.

### Metadata — Scene Page

All key scene metadata is available in a `application/ld+json` block of type `VideoObject`:

| Stash field | Source |
|---|---|
| title | `VideoObject.name` |
| date | `VideoObject.uploadDate` (ISO-8601, strip to YYYY-MM-DD) |
| details | `VideoObject.description` (may be tag list, not narrative) |
| image | `VideoObject.thumbnailUrl[0]` (full CDN URL) |
| performers | `VideoObject.actor[].name` |
| tags | `VideoObject.keywords[]` |
| studio | Constant: `BoyFriendTV` |

Fallback for performers: `a[href^="/pornstars/"][href$="/videos/"]` anchors in HTML.
Fallback for tags: `a[href^="/tags/"]` anchor text in HTML.

### Metadata — Performer Page

Performer pages return a Cloudflare challenge for script requests. If the page is fetchable (e.g. via playwright), look for:
- `og:title` for name
- `og:image` for photo
- HTML bio fields for country, birthdate, etc. (structure TBD)
- Hardcode `gender: 'Male'`

### Validated Example

- Scene URL: `https://www.boyfriendtv.com/videos/1426460/selector/`
  - title: `selector`
  - date: `2025-06-07`
  - performers: Scott Demarco, Brody Meyer, Simon Thies
  - tags: Anal, Big Cock, Tattoo, Bareback, Facial, Cum In Mouth, Muscle, Hairy, Finger Fuck, Big Load, Lick And Suck, Various Positions
  - image: `https://cdn77-t.boyfriendtv.com/b-boyfriendtv/thumbs/bftv-full/2025-06/ae/a84ae26ae2b6d87d65e4f02301379f31e.mp4-full-5.jpg`

## Known Limitations

1. `sceneByName`, `sceneByQueryFragment`, and `sceneByFragment` are **not supported** — search is Cloudflare-gated.
2. `performerByURL` is **partially blocked** — performer pages trigger CF challenge. Return name-from-slug + `gender: Male` as fallback.
3. Scene `description` is often a comma-separated tag list, not a narrative synopsis.
4. No per-scene studio/channel field; always return `BoyFriendTV`.

## Validation Requirements

- Test `sceneByURL` against: `https://www.boyfriendtv.com/videos/1426460/selector/`
- Confirm JSON-LD is parsed correctly and all fields above are populated
- Test `performerByURL` against: `https://www.boyfriendtv.com/pornstars/scott-demarco-2077/` — document result (may be partial due to CF)
- Document any access issues in `TODO.md`

## Repo Helpers

- Reference implementation: `scrapers/justthegays-tv/JustTheGays.py` (same stdlib pattern)
- Template: `templates/site-template/SiteScraper.py` and `SiteScraper.yml`
- Checklist: `workflow/NEW_SCRAPER_CHECKLIST.md`
