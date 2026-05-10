# Perplexity → Codex Handoff — xHamster Scraper

Create a working Stash scraper for https://xhamster.com/ in this repository.

Repository:
- Repo name: otter-twunk/my-scrapers
- Structure: one scraper per folder under `scrapers/<site-folder>/`

Your job:
- Read the research below and use it as implementation guidance
- Create the new scraper in `scrapers/xhamster-com/`
- Include:
  - the scraper `.yml`
  - the backing Python script
  - a short `README.md`
  - keep `SCRAPER_SPEC.json` as the machine-friendly research contract
  - keep `PERPLEXITY_TO_CODEX_HANDOFF.md` in the folder as the research record
  - update `CODEX_PROMPT.md` in the folder if implementation details change
- Follow official Stash scraper conventions
- Preserve existing scrapers and repo structure
- Update the root `README.md` with the new scraper folder

Implementation requirements:
- Prefer Python for the script scraper (mirror the style from `scrapers/boyfriendtv-com/` and `scrapers/justthegays-tv/`)
- Support the following hook modes based on the research:
  - `sceneByURL`
  - `sceneByName`
  - `sceneByQueryFragment`
  - `sceneByFragment`
  - `performerByURL`
- Keep the scraper scoped to xHamster only
- Handle missing metadata gracefully (empty strings/arrays instead of errors)
- Avoid introducing unnecessary third-party dependencies; standard library + requests is acceptable if needed

Validation requirements:
- Test `sceneByURL` against several live scenes
- Test `sceneByName` on realistic titles and ensure the best result is chosen from `/search/{query}`
- Test `sceneByFragment` with filename-style fragments (e.g. partial slug, idHashSlug) and verify the correct scene is selected
- Test `performerByURL` on at least a couple of `/pornstars/{slug}` pages
- Report any known limitations clearly in `README.md`

Use these repo helpers:
- Start from `templates/site-template/` (same pattern as existing scrapers)
- Follow `workflow/NEW_SCRAPER_CHECKLIST.md`
- Use `SCRAPER_SPEC.json` as the first reference when specific implementation details are needed

---

## Research Notes (for Codex)

### 1. Platform / structure

- xHamster is a custom tube platform, not WordPress.
- Scene pages render a large `window.initials` JSON object in a `<script>` tag in the HTML response.
- There is **no JSON-LD VideoObject block**; all useful metadata lives under `window.initials`.
- Search pages (`/search/{query}`) and performer pages (`/pornstars/{slug}`) respond with full HTML and the same `window.initials` pattern; **no Cloudflare challenge was observed**.

### 2. Scene pages

Validated example: `https://xhamster.com/videos/day-1-seven-slave-intake-xhk23el`

Key structures in `window.initials`:

**`videoModel`** (core video metadata)
- `id`: numeric internal ID (e.g. `28952176`)
- `idHashSlug`: short alphanumeric ID appearing in the URL (e.g. `xhk23el`)
- `title` / `titleLocalized`: main scene title
- `pageURL`: canonical scene URL
- `thumbURL`: large 16:9 thumbnail (primary cover image)
- `previewThumbURL`, `spriteURL`: smaller/sprite thumbnails
- `duration`: seconds (integer)
- `created`: **UNIX timestamp in seconds** — convert to `%Y-%m-%d` for the Stash `date` field
- `description`: full text synopsis
- `channelModel.channelName`: paysite / channel name (e.g. `The Training of O by Kink`)
- `channelModel.channelURL`: full channel URL
- `resolution`, `views`, `rating`, `orientation`, etc.

**`videoEntity`** (overlapping metadata, used for performer list)
- `id`, `duration`, `title`, `description`, `views`, `dateAgo`
- `thumbBig`, `thumbs`: alternate thumbnail sources
- `pornstarModels`: **array of performer objects** with:
  - `id`, `name`, `country`, `bdate`, `gender`, `alias`, `inurl`, `thumb`

**`videoTagsComponent`** (tags and categories)
- `tags`: mixed array of performers, categories, and general tags
- Each tag object has:
  - `name`: display text
  - `url`: xHamster URL
  - `isPornstar` (bool): performer
  - `isCategory` (bool): content category
  - `isTag` (bool): general tag
  - `isChannel` (bool): channel/studio

**Parsing approach for scenes:**

```python
import json, re

POS = html.find('window.initials=')
json_str = html[POS + len('window.initials='):]
obj, _ = json.JSONDecoder().raw_decode(json_str)

vm = obj.get('videoModel', {})
ve = obj.get('videoEntity', {})
tags_comp = obj.get('videoTagsComponent', {})

title       = vm.get('title') or ve.get('title', '')
date        = datetime.utcfromtimestamp(vm['created']).strftime('%Y-%m-%d')  # if created present
description = vm.get('description') or ve.get('description', '')
image       = vm.get('thumbURL') or ve.get('thumbBig', '')
studio      = (vm.get('channelModel') or {}).get('channelName', '')

performers  = [
    {'name': p['name'],
     'url': f"https://xhamster.com/pornstars/{p['inurl']}",
     'gender': p.get('gender', '')}
    for p in ve.get('pornstarModels', [])
]

tags = [
    t['name']
    for t in tags_comp.get('tags', [])
    if t.get('isCategory') or t.get('isTag')
]
```

### 3. Performer pages

- Performer URLs: `https://xhamster.com/pornstars/{slug}` (e.g. `coffee-brown`)
- `window.initials.channelInfo` on performer pages contains only: `id`, `type`, `orientation`, `slug`, `personType`
- Full bio fields (height, measurements, etc.) are **not** in `window.initials`; they render in the HTML `landing-info` section
- Avatar URL appears in a `background-image` CSS inline style inside the `landing-info__logo-image` element

Recommended minimal `performerByURL` approach:
- Parse slug from URL for `name` (title-case the slug, e.g. `coffee-brown` → `Coffee Brown`)
- Return `url` as the canonical performer page URL
- Where possible, extract gender from `channelInfo.orientation` (0 = straight female, etc.) or from scene-level `pornstarModels` data
- Attempt to extract avatar from the HTML `background-image` in `.landing-info__logo-image`

### 4. Search and fragment matching

- Search URL: `https://xhamster.com/search/{url-encoded-query}`
- Returns full HTML with scene link `href` values matching `/videos/{slug}-{idHashSlug}`
- **No Cloudflare challenge on search pages**

Suggested strategy for `sceneByName` / `sceneByQueryFragment` / `sceneByFragment`:

1. URL-encode the title or fragment and fetch `/search/{query}` with standard headers
2. Extract all `/videos/...` hrefs from the results page
3. For title matching: compare requested title to each candidate title (fetch scene page or parse thumbnail title attribute); pick highest similarity
4. For fragment matching: if the fragment contains an `idHashSlug` substring (alphanumeric ~7 chars), prefer URL substring match over title similarity
5. Return `None` / empty if no candidate meets a minimum confidence threshold

### 5. Known limitations / edge cases

- Some scenes have no `pornstarModels`; performer list will be empty unless tags supply `isPornstar` entries
- Performer bio details (height, measurements, city) are not available in structured JSON from performer pages
- Non-Latin or very long titles degrade search-based matching quality; implement conservative thresholds
- The `created` UNIX timestamp on xHamster is the upload date, not the original filming date

Use this document alongside `SCRAPER_SPEC.json` when implementing the scraper.
