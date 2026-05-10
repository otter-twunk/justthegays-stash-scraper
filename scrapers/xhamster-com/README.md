# xHamster Stash Scraper

This folder contains the implementation scaffold and research notes for a Stash script scraper targeting **xHamster** (https://xhamster.com/).

## Supported hooks

| Hook | Status |
|---|---|
| `sceneByURL` | To be implemented |
| `sceneByName` | To be implemented |
| `sceneByQueryFragment` | To be implemented |
| `sceneByFragment` | To be implemented |
| `performerByURL` | To be implemented |

## Files

- `SCRAPER_SPEC.json` — machine-friendly contract: supported modes, URL patterns, metadata mappings
- `PERPLEXITY_TO_CODEX_HANDOFF.md` — detailed research notes and implementation guidance for Codex
- `CODEX_PROMPT.md` — concise Codex starting prompt focused on this folder
- `XHamster.py` — Python script scraper implementation *(to be created by Codex)*
- `XHamster.yml` — Stash scraper definition file *(stub, to be completed by Codex)*
- `TODO.md` — implementation checklist

## Platform notes

- Custom tube site, no WordPress, no Cloudflare challenge observed
- All metadata embedded in `window.initials` JSON on each page — no JSON-LD, no extra API calls
- Scene URLs: `https://xhamster.com/videos/{slug}-{idHashSlug}`
- Performer URLs: `https://xhamster.com/pornstars/{slug}`
- Search: `https://xhamster.com/search/{query}`

## Known limitations

- Performer bio details (height, measurements, etc.) are not available in `window.initials`; only minimal info (name, slug, avatar) is reliably accessible
- Some scenes have no pornstar metadata; performers fall back to `isPornstar` tags only
- Non-Latin or very long scene titles may reduce fragment/search match quality

## Codex start

```
Use the files in scrapers/xhamster-com/ and build the scraper.
```
