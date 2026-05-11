# Perplexity to Codex Handoff

Target site: `https://gayforfans.com/`

Target folder: `scrapers/gayforfans/`

Use this file as the site-specific Codex handoff.

## What Codex Should Do

- Build a working Stash script scraper for this site in this folder.
- Keep the implementation self-contained and lightweight.
- Preserve existing scrapers elsewhere in the repo.
- Update the root `README.md` with the new scraper folder.

## Supported Hook Modes

- `sceneByURL`
- `sceneByName`
- `sceneByQueryFragment`
- `sceneByFragment`
- `performerByURL`

## Site Notes

- `gayforfans.com` is a server-rendered WordPress-style site.
- Scene pages live under `/video/<slug>/`.
- Performer pages live under `/performer/<slug>/`.
- Search works without JavaScript at `/?s={query}` and the pretty `/search/<query>` route.
- Scene pages include server-rendered `VideoObject` JSON-LD with title, description, upload date, thumbnail, keywords, and actors.
- Performer pages include server-rendered `Person` JSON-LD with name, description, URL, and image.

## Metadata Mapping

- Scene title: `VideoObject.name`
- Scene date: `VideoObject.uploadDate`
- Scene description: `VideoObject.description`
- Scene image: `VideoObject.thumbnailUrl`
- Performers: `VideoObject.actor[]`
- Tags: `VideoObject.keywords`, with `/categories/` links as fallback
- Studio: hard-code `GayForFans`
- Performer name: `Person.name`
- Performer image: `Person.image`
- Performer details: `Person.description`

## Known Limitations

- Description text is generic site-generated copy, not always a scene-specific synopsis.
- Search results can be crowded for popular performers, so fragment ranking must be conservative.
- Performer pages expose minimal structured metadata beyond name, image, and description.

## Validation

- Test `sceneByURL` against a live scene page.
- Test `performerByURL` against a live performer page.
- Test `sceneByName` on a performer-based query with many results.
- Test fragment matching with a filename-like query that needs normalization.
