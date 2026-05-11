# Codex Prompt

Use the files in `scrapers/gayporn/` and build the scraper.

Start with:

- `SCRAPER_SPEC.json`
- `PERPLEXITY_TO_CODEX_HANDOFF.md`
- `GayPorn.yml`
- `GayPorn.py`

Requirements:

- Implement `sceneByURL`, `sceneByName`, `sceneByQueryFragment`, `sceneByFragment`, and `performerByURL`
- Use Python
- Target URL: `https://gayporn.com/`
- Scene pages: `https://gayporn.com/video/{slug}`
- Performer pages: `https://gayporn.com/pornstars/{slug}`
- Search: `https://gayporn.com/search?query={query}`
- Prefer structured data on scene and performer pages over brittle visual selectors
- Keep the scraper self-contained inside `scrapers/gayporn/`
- Test against live pages if possible
- Update the local docs/spec files and root `README.md`
- Document known limitations clearly, especially missing scene performer data
