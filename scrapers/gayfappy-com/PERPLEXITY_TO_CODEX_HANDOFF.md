# Perplexity to Codex Handoff

Target site: `https://gayfappy.com/`

Target folder: `scrapers/gayfappy-com/`

Use `SCRAPER_SPEC.json` first, then this file for human-readable context.

## What Codex Should Do

- Implement the Gay Fappy scraper from the stub in `GayFappy.py`
- Create or update:
  - `SCRAPER_SPEC.json`
  - `GayFappy.yml`
  - `GayFappy.py`
  - `README.md`
- Preserve all other scrapers elsewhere in the repo
- Validate against `workflow/NEW_SCRAPER_CHECKLIST.md`

## Suggested Hook Modes

- `sceneByURL`
- `sceneByName`
- `sceneByQueryFragment`
- `sceneByFragment`

## Not Recommended Initially

- `performerByURL`

Reason: the site appears to be WordPress-based and uses tags for performer-like entities, but no dedicated performer pages were identified.

## Site Notes

- gayfappy.com appears to be a WordPress site with `/index.php/{id}/{slug}/` style post permalinks
- Video listing page: `https://gayfappy.com/index.php/category/videos/`
- Site search: `https://gayfappy.com/?s={query}`
- Search results and category archives appear server-rendered, so `requests` + `BeautifulSoup` should be sufficient
- No API, JSON-LD scraper target, Cloudflare, or captcha requirement was identified during inspection
- Use a browser-like User-Agent header on every request

## Metadata Mapping

See `SCRAPER_SPEC.json` for the machine-readable form. Practical summary:

| Field | Source |
|---|---|
| title | `h1.entry-title` or page `<title>` |
| date | `.entry-meta time` or byline text with absolute date like `May 9, 2026` |
| details | `.entry-content` cleaned to readable post text |
| image | `meta[property='og:image']`, else first content image / poster fallback |
| performers | inferred conservatively from tag links under `/index.php/tag/` |
| tags | `.tags-links a`, `a[rel='tag']`, or `/index.php/tag/` links |
| studio | hardcode `"Gay Fappy"` |

## Parsing Strategy

1. For `sceneByURL`, fetch the post page and parse the main `article.post`.
2. Extract title from `h1.entry-title`.
3. Extract date from `.entry-meta time` first, then fallback to date text in the byline.
4. Extract details from `.entry-content`, removing boilerplate and preserving readable paragraph text.
5. Extract tags from WordPress tag links.
6. Infer performers from tags only when the labels look person-like; otherwise leave performers empty rather than adding noisy names.
7. For search-based hooks, query `/?s={query}`, parse result articles, keep URLs matching post patterns, and rank by title similarity before returning.

## Known Limitations

- Search can return non-video content because the site includes photos and gifs alongside videos
- Tag taxonomy mixes performers and generic topical labels, so performer inference will be imperfect
- There is no confirmed performer page structure for a reliable `performerByURL` implementation
- Some posts may embed remote videos in ways that do not expose a rich local poster image
- The source studio may not be recoverable from the page; use the site name as the studio fallback

## Validation

- Test `sceneByURL`: `https://gayfappy.com/index.php/58774/outdoor-session-with-vadim-romeo-davis/`
- Test `sceneByURL`: `https://gayfappy.com/index.php/58733/marin-barbarosie-bottoms-for-bastian-karim/`
- Test `sceneByName` with query: `"bastian karim"`
- Test `sceneByFragment` with filename/title fragments such as `"vadim romeo davis"`
