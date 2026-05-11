# Perplexity to Codex Handoff

Target site: `https://www.everydayporn.co`

Target folder: `scrapers/everydayporn/`

Use this file as the site-specific Codex handoff.

## What Codex Should Do

- Build a working Stash scraper for this site in this folder
- Create or update:
  - `SCRAPER_SPEC.json`
  - the scraper `.yml`
  - the backing Python script
  - `README.md`
- Preserve existing scrapers elsewhere in the repo
- Update the root `README.md` with this scraper folder

## Suggested Hook Modes

- `sceneByURL`
- `sceneByName`

## Site Notes

- Platform: KVS-like tube platform (exact CMS unconfirmed — avoid hardcoding KVS assumptions)
- Scene pages expose `VideoObject` JSON-LD, OG tags, duration, upload date, and embed URLs
- `/search/?q=...` returns HTML results and is the most practical `sceneByName` entry point
- `/latest-updates/` remains a useful listing page, but search pagination appears to be AJAX-driven
- As of May 11, 2026, direct non-browser traffic receives a Cloudflare managed challenge
- Perplexity live-inspected this site in May 2026; validation URLs below are confirmed working
- Site is an adult content source — keep scraping metadata-only

## Metadata Mapping

- **scene_title**: `JSON-LD VideoObject.name` or `og:title`
- **date**: `JSON-LD VideoObject.uploadDate` or `meta[property='ya:ovs:upload_date']`
- **description**: `JSON-LD VideoObject.description` or `og:description`
- **cover_image**: `JSON-LD VideoObject.thumbnailUrl` or `og:image`
- **performers**: `a[href*='/models/']` — not present on sampled scene pages
- **tags**: `a[href*='/categories/']`
- **studio**: `a[href*='/sites/']` — not confirmed on sampled pages

## Anti-Bot / Access Notes

- A Cloudflare-aware fetch layer is required for reliable non-browser scraping.
- Use conservative request delays between search calls.

## Known Limitations

- Performer/model links not present on sampled scene pages.
- Studio/source links not confirmed — may not be populated for all content.
- Search pagination beyond the first HTML page is not confirmed.
- Platform appears KVS-like but exact CMS unconfirmed — avoid hardcoding KVS-specific assumptions.

## Validation

Test against these live scene URLs:
- `https://www.everydayporn.co/video/340577/teddy-torres-fucks-bbutcherboy-fan-club2/`
- `https://www.everydayporn.co/video/326655/onlyfans-mr-slimkat-trufreak2k-aka-notapout-free-gay-porn2/`

- Test `sceneByURL` against a live scene page
- Test `sceneByName` via `/search/?q=...`
- Test fragment matching if practical
