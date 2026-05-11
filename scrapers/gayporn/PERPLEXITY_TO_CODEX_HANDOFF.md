# Perplexity to Codex Handoff

Target site: `https://gayporn.com/`

Target folder: `scrapers/gayporn/`

Use `SCRAPER_SPEC.json` first, then this file for human-readable context.

## What Codex Should Do

- Implement the GayPorn scraper in `GayPorn.py`
- Create or update:
  - `SCRAPER_SPEC.json`
  - `GayPorn.yml`
  - `GayPorn.py`
  - `README.md`
- Preserve all other scrapers elsewhere in the repo
- Validate against `workflow/NEW_SCRAPER_CHECKLIST.md`

## Suggested Hook Modes

- `sceneByURL`
- `sceneByName`
- `sceneByQueryFragment`
- `sceneByFragment`
- `performerByURL`

## Site Notes

- gayporn.com is a custom tube site with server-rendered HTML and JSON-LD metadata
- Scene URL pattern: `https://gayporn.com/video/{slug}`
- Performer URL pattern: `https://gayporn.com/pornstars/{slug}`
- Search URL: `https://gayporn.com/search?query={query}`
- Scene pages expose `VideoObject` JSON-LD with title, upload date, thumbnail, description, author, genres, and keywords
- Performer pages expose `ProfilePage` JSON-LD with `Person` name and URL
- Live validation on 2026-05-11 showed `curl` worked reliably while requests-based fetches often received `502 Bad Gateway`

## Metadata Mapping

See `SCRAPER_SPEC.json` for full selector/parsing notes. Summary:

| Field       | Source                                                             |
|-------------|--------------------------------------------------------------------|
| title       | `VideoObject.name` or `og:title`                                   |
| date        | `VideoObject.uploadDate`                                           |
| details     | `VideoObject.description` or `meta[name='description']`            |
| image       | `VideoObject.thumbnailUrl` or `og:image`                           |
| performers  | Not reliably exposed on tested scene pages                         |
| tags        | `VideoObject.genre` + `VideoObject.keywords`                       |
| studio      | `VideoObject.author`                                               |

## Known Limitations

- Scene performers are intentionally omitted unless the site starts publishing a reliable scene-specific list
- Performer pages appear sparse and may only offer name, description, and avatar
- Search result quality depends on title matching for fragment resolution
- The scraper assumes a working `curl` binary on the target host

## Validation

- Test `sceneByURL`: `https://gayporn.com/video/corbin-fisher-blond-adonis-topping`
- Test `performerByURL`: `https://gayporn.com/pornstars/daniel-dean`
- Test `sceneByName` with query: `"blond adonis topping"`
- Test `sceneByFragment` with a title or filename fragment
