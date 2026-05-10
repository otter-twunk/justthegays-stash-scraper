# Codex Prompt

Use the files in `scrapers/gay0day-com/` and build the scraper.

Start with:

- `SCRAPER_SPEC.json`
- `PERPLEXITY_TO_CODEX_HANDOFF.md`
- `Gay0Day.yml`
- `Gay0Day.py` (stub — implement the handler functions)

Requirements:

- Implement all five hook modes: `sceneByURL`, `sceneByName`, `sceneByQueryFragment`,
  `sceneByFragment`, `performerByURL`
- Use `requests` + `BeautifulSoup` for HTML parsing
- Target URL: `https://gay0day.com/`
- Scene pages: `https://gay0day.com/videos/{id}/{slug}/`
- Performer pages: `https://gay0day.com/models/{slug}/`
- Search: `https://gay0day.com/search/?q={query}`
- Extract title, date (convert relative to ISO), details, cover image (og:image),
  performers (from /models/ links), tags (from /tags/ links), studio (constant "Gay0Day")
- Handle N/A and missing performer fields gracefully
- Use a browser-like User-Agent header on all requests
- Output must be valid Stash JSON (scene fragment or performer fragment as appropriate)
- Update `README.md` with supported hooks and usage notes
- Validate against `workflow/NEW_SCRAPER_CHECKLIST.md`
