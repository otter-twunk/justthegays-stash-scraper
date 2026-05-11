# Codex Prompt

Use the files in `scrapers/gayhardfuck-com/` and build the scraper.

Start with:

- `SCRAPER_SPEC.json`
- `PERPLEXITY_TO_CODEX_HANDOFF.md`
- `GayHardFuck.yml`
- `GayHardFuck.py` (stub — implement the handler functions)

Requirements:

- Implement all four hook modes: `sceneByURL`, `sceneByName`, `sceneByQueryFragment`,
  `sceneByFragment`
- Do NOT implement `performerByURL` — performer pages do not exist on this site
- Use `requests` + `BeautifulSoup` for HTML parsing
- Target URL: `https://www.gayhardfuck.com/`
- Scene pages: `https://www.gayhardfuck.com/videos/{id}/{slug}/`
- Search: `https://www.gayhardfuck.com/search/?q={query}`
- Extract title (from og:title or <title>, strip site suffix), date (convert relative to ISO),
  details (og:description), cover image (og:image), performers (from /models/ links if present),
  tags (from /tags/ links), studio (constant "GayHardFuck")
- Search results have two sections — parse only the video card results, not the tag-suggestion links
- Use a browser-like User-Agent header on all requests
- Always use https://www.gayhardfuck.com/ prefix
- Output must be valid Stash JSON (scene fragment as appropriate)
- Update `README.md` with supported hooks and usage notes
- Validate against `workflow/NEW_SCRAPER_CHECKLIST.md`
