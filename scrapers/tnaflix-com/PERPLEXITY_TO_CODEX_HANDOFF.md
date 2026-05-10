# Perplexity to Codex Handoff — TNAFlix

Create a working Stash scraper for https://www.tnaflix.com/ in this repository.

## Repository

- Repo name: `otter-twunk/my-scrapers`
- Structure: one scraper per folder under `scrapers/<site-folder>/`
- This scraper lives in: `scrapers/tnaflix-com/`

## Your Job

- Read the research in `SCRAPER_SPEC.json` and use it as the implementation contract
- Create `TNAFlix.py` and `TNAFlix.yml` inside this folder
- Keep `SCRAPER_SPEC.json`, `PERPLEXITY_TO_CODEX_HANDOFF.md`, and `CODEX_PROMPT.md` as-is
- Update `TODO.md` as you complete tasks
- Follow official Stash scraper conventions
- Preserve all other scrapers in the repo
- Update the root `README.md` to add `scrapers/tnaflix-com` to the current scrapers list

## Implementation Requirements

- Use Python 3 for the script scraper
- Use the same pattern as `scrapers/justthegays-tv/JustTheGays.py` (stdlib-only, urllib + curl subprocess fallback, JSON-LD parsing)
- Support **sceneByURL**, **sceneByName**, and **performerByURL**
- Do NOT implement `sceneByQueryFragment` or `sceneByFragment`
- Handle missing metadata gracefully — return empty string, not an error
- No third-party dependencies beyond Python stdlib and optional `certifi`

## Site Research Summary

### Platform

Custom tube site. Not WordPress. **No Cloudflare or aggressive anti-bot protection.** Standard Firefox UA is sufficient for all routes. Python urllib works directly without issues.

### URL Patterns

- Scene pages: `https://www.tnaflix.com/{category-slug}/{Title-Slug}/video{id}`
  - Example: `https://www.tnaflix.com/amateur-porn/Best-Of-Lolo-Ferrari/video563066`
- Performer profiles: `https://www.tnaflix.com/profile/{performer-slug}`
  - Example: `https://www.tnaflix.com/profile/lolo-ferrari`
- Search: `https://www.tnaflix.com/search?what={query}` — GET, no blocking

### Metadata — Scene Page

Key metadata is in a `application/ld+json` block of type `VideoObject`:

| Stash field | Source |
|---|---|
| title | `VideoObject.name` |
| date | `VideoObject.uploadDate` (strip to YYYY-MM-DD) |
| details | `VideoObject.description` (empty if `"No description provided"`) |
| image | `VideoObject.thumbnailUrl` (**plain string**, not array) |
| performers | HTML `a.badge-kiss[href^="/profile/"]` anchor text |
| tags | Category slug from URL first path segment, title-cased |
| studio | Constant: `TNAFlix` |

**Critical:** `thumbnailUrl` is a plain string — do not use `[0]`.

**Performers:** Find `<a>` tags whose `class` contains `badge-kiss` and `href` starts with `/profile/`. Exclude `badge-unverified` links (those are uploader accounts, not performers).

**Tags:** No explicit tag list on scene pages. Parse the first path segment of the scene URL (e.g. `amateur-porn`), replace hyphens with spaces, title-case it.

### Metadata — Performer Profile Page

| Stash field | Source |
|---|---|
| name | `<h1>` text content |
| image | `div.ph-avatar img[src]` |

No bio fields (birthdate, gender, country) are present in the HTML — do not attempt to scrape them.

### Search (sceneByName)

- Endpoint: `https://www.tnaflix.com/search?what={query}` (GET)
- Returns HTML with video card links matching `href="https://www.tnaflix.com/{category}/{slug}/video{id}"`
- Extract all result URLs, then fetch the best title match using `SequenceMatcher` (same as justthegays-tv)

### Validated Examples

**Scene:** `https://www.tnaflix.com/amateur-porn/Best-Of-Lolo-Ferrari/video563066`
- title: `Best Of Lolo Ferrari`
- date: `2013-12-09`
- description: `` (empty)
- image: `https://img.tnaflix.com/a16:9q80w920/thumbs/f2/12_563066l.jpg`
- performers: `["Lolo Ferrari"]`
- tags: `["Amateur Porn"]`
- studio: `TNAFlix`

**Performer:** `https://www.tnaflix.com/profile/lolo-ferrari`
- name: `Lolo Ferrari`
- image: `https://img.tnaflix.com/q80w210r/pics/alpha/pornstars/3208712.jpg`

**Search:** `https://www.tnaflix.com/search?what=lolo+ferrari` → returns video cards including `video563066`

## Known Limitations

- No per-scene tag list; only URL category slug used as a tag
- `description` is often blank for user-uploaded content
- Performer profiles: name and photo only — no bio fields
- `sceneByQueryFragment` and `sceneByFragment` not implemented
- Studio always hardcoded to `TNAFlix`
