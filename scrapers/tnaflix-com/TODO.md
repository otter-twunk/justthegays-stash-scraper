# TODO — TNAFlix Scraper

## Implementation

- [ ] Create `TNAFlix.py` based on justthegays-tv pattern
- [ ] Create `TNAFlix.yml` with sceneByURL, sceneByName, and performerByURL hooks
- [ ] Implement `sceneByURL` — fetch scene page, parse JSON-LD VideoObject
- [ ] Implement `sceneByName` — GET search?what=, extract video URLs, best-match by title
- [ ] Implement `performerByURL` — fetch profile page, extract name + photo
- [ ] Handle `"No description provided"` as empty string
- [ ] Derive tag from URL category slug (title-case, replace hyphens with spaces)
- [ ] Hardcode studio as `"TNAFlix"`
- [ ] `thumbnailUrl` is a plain string — do not subscript with `[0]`

## Validation

- [ ] Test `sceneByURL` against `https://www.tnaflix.com/amateur-porn/Best-Of-Lolo-Ferrari/video563066`
  - [ ] title: `Best Of Lolo Ferrari`
  - [ ] date: `2013-12-09`
  - [ ] performers: `["Lolo Ferrari"]`
  - [ ] tags: `["Amateur Porn"]`
  - [ ] image URL populated
  - [ ] studio: `TNAFlix`
- [ ] Test `performerByURL` against `https://www.tnaflix.com/profile/lolo-ferrari`
  - [ ] name: `Lolo Ferrari`
  - [ ] image URL populated
- [ ] Test `sceneByName` with query `lolo ferrari`
  - [ ] Returns at least one matching scene

## Repo

- [ ] Write `README.md` for this scraper folder
- [ ] Update root `README.md` to add `scrapers/tnaflix-com` to current scrapers list
- [ ] Run `scripts/validate_scraper_repo.py` if available

## Known Non-Issues (Do Not Implement)

- `sceneByQueryFragment` — not implemented, fragment matching unreliable
- `sceneByFragment` — not implemented
- Performer bio fields (birthdate, gender, country) — not available on profile pages
