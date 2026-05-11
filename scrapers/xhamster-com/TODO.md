# TODO — xHamster Scraper

Implementation tasks for Codex:

- [x] Create `XHamster.py` implementing the Stash script scraper
- [x] Complete `XHamster.yml` with correct Stash YAML structure wired to the Python script
- [x] Implement `sceneByURL` using `window.initials.videoModel` / `videoEntity` / `videoTagsComponent`
- [x] Implement `sceneByName` using `/search/{query}` and title similarity ranking
- [x] Implement `sceneByQueryFragment` / `sceneByFragment` using filename fragments and search
- [x] Implement `performerByURL` with minimal but robust mapping (slug → name, avatar from HTML, gender from channelInfo)
- [x] Add a `Test URLs` section to `README.md` with at least 2 validated scene URLs and 2 performer URLs
- [x] Update the repo root `README.md` to list `scrapers/xhamster-com`
- [x] Run through `workflow/NEW_SCRAPER_CHECKLIST.md`
