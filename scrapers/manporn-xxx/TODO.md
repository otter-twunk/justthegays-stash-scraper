# TODO — ManPorn Scraper

## Pre-Implementation

- [ ] Do a live fetch of `https://manporn.xxx/videos/3400273/hot-threesome-action-with-indian-pornstars/` and confirm:
  - [ ] Page responds successfully (no Cloudflare block) with Firefox UA + `age_verified=1` cookie
  - [ ] JSON-LD VideoObject block is present in the HTML
  - [ ] Confirm correct age-gate cookie name (expected `age_verified=1`; update if different)
  - [ ] Note actual field names in the VideoObject block (thumbnailUrl vs thumbnail, keywords vs genre, actor vs actors)

## Implementation

- [ ] Create `ManPorn.py` based on justthegays-tv + boyfriendtv-com pattern
- [ ] Complete `ManPorn.yml` with sceneByURL and performerByURL hooks (stub already created)
- [ ] Implement `sceneByURL` — fetch scene page, parse JSON-LD VideoObject
- [ ] Implement `performerByURL` — attempt fetch; return name-from-slug + gender fallback on CF block
- [ ] Set age-gate cookie in all requests (confirm name in pre-implementation step above)
- [ ] Handle missing metadata fields gracefully

## Validation

- [ ] Test sceneByURL against `https://manporn.xxx/videos/3400273/hot-threesome-action-with-indian-pornstars/`
  - [ ] title populated
  - [ ] date populated (YYYY-MM-DD)
  - [ ] performers populated
  - [ ] tags populated
  - [ ] image URL populated
  - [ ] studio: "ManPorn"
- [ ] Test performerByURL against `https://manporn.xxx/models/reign/`
  - [ ] Document what is returned (full bio or partial due to Cloudflare)
- [ ] Test performerByURL against `https://manporn.xxx/models/zbynek-onderka/`

## Repo

- [ ] Write `README.md` for this scraper folder (stub already created)
- [ ] Update root `README.md` to add `scrapers/manporn-xxx` to current scrapers list
- [ ] Run `scripts/validate_scraper_repo.py` if available

## Known Blockers

- sceneByName / sceneByQueryFragment / sceneByFragment: search expected to be Cloudflare-blocked — do not implement
- performerByURL: performer pages may trigger CF challenge — return minimal data (name + gender) as fallback
- Age-gate cookie name unconfirmed — must validate on first live fetch
