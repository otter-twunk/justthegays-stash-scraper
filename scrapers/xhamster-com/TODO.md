# TODO — xHamster Scraper

Implementation tasks for Codex:

- [ ] Create `XHamster.py` implementing the Stash script scraper
- [ ] Complete `XHamster.yml` with correct Stash YAML structure wired to the Python script
- [ ] Implement `sceneByURL` using `window.initials.videoModel` / `videoEntity` / `videoTagsComponent`
- [ ] Implement `sceneByName` using `/search/{query}` and title similarity ranking
- [ ] Implement `sceneByQueryFragment` / `sceneByFragment` using filename fragments and search
- [ ] Implement `performerByURL` with minimal but robust mapping (slug → name, avatar from HTML, gender from channelInfo)
- [ ] Add a `Test URLs` section to `README.md` with at least 2 validated scene URLs and 2 performer URLs
- [ ] Update the repo root `README.md` to list `scrapers/xhamster-com`
- [ ] Run through `workflow/NEW_SCRAPER_CHECKLIST.md`
