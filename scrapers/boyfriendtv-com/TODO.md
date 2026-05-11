# TODO — BoyFriendTV Scraper

## Implementation

- [x] Create `BoyFriendTV.py` based on justthegays-tv pattern
- [x] Create `BoyFriendTV.yml` with sceneByURL and performerByURL hooks
- [x] Implement `sceneByURL` — fetch scene page, parse JSON-LD VideoObject
- [x] Implement `performerByURL` — attempt fetch, return name-from-slug + gender fallback on CF block
- [x] Set `age_verified=1` cookie in all requests
- [x] Handle missing metadata fields gracefully

## Validation

- [x] Test sceneByURL against `https://www.boyfriendtv.com/videos/1426460/selector/`
  - [x] title: "selector"
  - [x] date: "2025-06-07"
  - [x] performers: Scott Demarco, Brody Meyer, Simon Thies
  - [x] tags: Anal, Big Cock, Tattoo, Bareback, Facial, Cum In Mouth, Muscle, Hairy, etc.
  - [x] image URL populated
  - [x] studio: "BoyFriendTV"
- [x] Test performerByURL against `https://www.boyfriendtv.com/pornstars/scott-demarco-2077/`
  - [x] Live result currently returns partial data: `name` + `url` + `gender`

## Repo

- [x] Write `README.md` for this scraper folder
- [x] Root `README.md` already includes `scrapers/boyfriendtv-com` in the current scrapers list
- [x] Run `scripts/validate_scraper_repo.py` if available

## Known Blockers

- sceneByName / sceneByQueryFragment / sceneByFragment: search is Cloudflare-blocked — do not implement
- performerByURL: performer pages trigger CF challenge — return minimal data (name + gender) as fallback
