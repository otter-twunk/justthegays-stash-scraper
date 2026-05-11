# GayHardFuck Scraper

Stash Python script scraper for [gayhardfuck.com](https://www.gayhardfuck.com/).

## Supported Hooks

| Hook                   | Description                                              |
|------------------------|----------------------------------------------------------|
| `sceneByURL`           | Scrape a scene from its `gayhardfuck.com/videos/` URL    |
| `sceneByName`          | Search by title and return scene list                    |
| `sceneByQueryFragment` | Search using a query derived from scene metadata         |
| `sceneByFragment`      | Match by title/filename fragment via site search         |

> `performerByURL` is not supported — performer profile pages are not available on this site.

## URL Patterns

- Scene: `https://www.gayhardfuck.com/videos/{id}/{slug}/`
- Search: `https://www.gayhardfuck.com/search/?q={query}`

## Metadata

Extracts: title, approximate date, description, cover image, performers (if linked), tags.
Studio is hardcoded as `GayHardFuck` (tube aggregator — no per-scene studio field).

## Known Limitations

- Date is a relative string (e.g. "3 years ago") — converted to approximate ISO date
- Performer profile pages do not exist on this site; `/models/` index is empty
- No API or structured data — relies on HTML parsing
- Tags may be sparse or absent on some scene pages

## Files

| File                             | Purpose                            |
|----------------------------------|------------------------------------|n| `GayHardFuck.yml`                | Stash scraper config               |
| `GayHardFuck.py`                 | Python scraper implementation      |
| `SCRAPER_SPEC.json`              | Machine-readable spec for Codex    |
| `PERPLEXITY_TO_CODEX_HANDOFF.md` | Human-readable research notes      |
| `CODEX_PROMPT.md`                | Codex start prompt                 |
| `TODO.md`                        | Implementation checklist           |
