# TODO — BoyFriendTV Scraper

## Implementation

- [ ] Create `BoyFriendTV.py` based on justthegays-tv pattern
- [ ] Create `BoyFriendTV.yml` with sceneByURL and performerByURL hooks
- [ ] Implement `sceneByURL` — fetch scene page, parse JSON-LD VideoObject
- [ ] Implement `performerByURL` — attempt fetch, return name-from-slug + gender fallback on CF block
- [ ] Set `age_verified=1` cookie in all requests
- [ ] Handle missing metadata fields gracefully

## Validation

- [ ] Test sceneByURL against `https://www.boyfriendtv.com/videos/1426460/selector/`
  - [ ] title: "selector"
  - [ ] date: "2025-06-07"
  - [ ] performers: Scott Demarco, Brody Meyer, Simon Thies
  - [ ] tags: Anal, Big Cock, Tattoo, Bareback, Facial, Cum In Mouth, Muscle, Hairy, etc.
  - [ ] image URL populated
  - [ ] studio: "BoyFriendTV"
- [ ] Test performerByURL against `https://www.boyfriendtv.com/pornstars/scott-demarco-2077/`
  - [ ] Document what is returned (full bio or partial due to Cloudflare)

## Repo

- [ ] Write `README.md` for this scraper folder
- [ ] Update root `README.md` to add `scrapers/boyfriendtv-com` to current scrapers list
- [ ] Run `scripts/validate_scraper_repo.py` if available

## Known Blockers

- sceneByName / sceneByQueryFragment / sceneByFragment: search is Cloudflare-blocked — do not implement
- performerByURL: performer pages trigger CF challenge — return minimal data (name + gender) as fallback
