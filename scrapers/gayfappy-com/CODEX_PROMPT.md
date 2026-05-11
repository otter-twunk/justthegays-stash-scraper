# Codex Prompt

Use the files in `scrapers/gayfappy-com/` and build the scraper.

Start with:

- `SCRAPER_SPEC.json`
- `PERPLEXITY_TO_CODEX_HANDOFF.md`
- `GayFappy.yml`
- `GayFappy.py` (stub — implement the handler functions)

Requirements:

- Implement four hook modes: `sceneByURL`, `sceneByName`, `sceneByQueryFragment`, `sceneByFragment`
- Do not implement `performerByURL` unless you discover a real dedicated performer page pattern during coding
- Use `requests` + `BeautifulSoup` for HTML parsing
- Target URL: `https://gayfappy.com/`
- Scene pages: `https://gayfappy.com/index.php/{id}/{slug}/`
- Search: `https://gayfappy.com/?s={query}`
- Prefer posts in the Videos category when search results are mixed
- Extract title, absolute date, details, cover image, tags, conservative performer inference, studio constant `"Gay Fappy"`
- Use a browser-like User-Agent header on all requests
- Output must be valid Stash JSON for scene fragments and search result lists
- Update `README.md` with supported hooks, known limitations, and usage notes
- Validate against `workflow/NEW_SCRAPER_CHECKLIST.md`

Implementation guidance:

- Use a helper to normalize whitespace and collect readable text from `.entry-content`
- Use a helper to normalize titles for fuzzy matching between query/fragment and result title
- Prefer exact or high-similarity title matches when selecting the top result for `sceneByFragment`
- Keep performer inference conservative; empty performers is better than incorrect performers
