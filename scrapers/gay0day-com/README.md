# Gay0Day Scraper

Stash Python script scraper for [gay0day.com](https://gay0day.com/).

## Supported Hooks

| Hook                   | Description                                        |
|------------------------|----------------------------------------------------|
| `sceneByURL`           | Scrape a scene from its `gay0day.com/videos/` URL  |
| `sceneByName`          | Search by title and return scene list              |
| `sceneByQueryFragment` | Search using a query derived from scene metadata   |
| `sceneByFragment`      | Match by title/filename fragment via site search   |
| `performerByURL`       | Scrape a performer from `gay0day.com/models/` URL  |

## URL Patterns

- Scene: `https://gay0day.com/videos/{id}/{slug}/`
- Performer: `https://gay0day.com/models/{slug}/`
- Search: `https://gay0day.com/search/?q={query}`

## Metadata

Extracts: title, approximate date, description, cover image, performers, tags.
Studio is hardcoded as `Gay0Day` (tube aggregator — no per-scene studio field).

## Known Limitations

- Date is a relative string (e.g. "6 years ago") — converted to approximate ISO date
- Performer profile fields are often empty on this site
- No API or structured data — relies on HTML parsing

## Files

| File                             | Purpose                            |
|----------------------------------|------------------------------------|
| `Gay0Day.yml`                    | Stash scraper config               |
| `Gay0Day.py`                     | Python scraper implementation      |
| `SCRAPER_SPEC.json`              | Machine-readable spec for Codex    |
| `PERPLEXITY_TO_CODEX_HANDOFF.md` | Human-readable research notes      |
| `CODEX_PROMPT.md`                | Codex start prompt                 |
| `TODO.md`                        | Implementation checklist           |
