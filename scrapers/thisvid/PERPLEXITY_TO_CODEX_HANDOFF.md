# Perplexity to Codex Handoff

Target site: `https://thisvid.com`

Target folder: `scrapers/thisvid/`

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

## Site Notes

- Platform: Custom community video site
- Site is an adult content source — keep scraping metadata-only and respect rate limits
- Perplexity live-inspected this site in May 2026; URL patterns and selectors below are verified
- Scene URLs use human-readable slugs (e.g. `/videos/blonde-anal-fun/`), not numeric IDs
- Some content requires login; start implementation with publicly accessible pages

## Metadata Mapping

- **scene_title**: `og:title` or page `<title>`
- **date**: Likely in page metadata or structured data — confirm during live implementation
- **description**: `og:description`
- **cover_image**: `og:image`
- **performers**: `a[href*='/members/']` links on scene page if present
- **tags**: `a[href*='/categories/']` links on scene page
- **studio**: Not applicable — community upload site

## Anti-Bot / Access Notes

- Site uses slug-based URLs; numeric-ID guessing returned 404.
- Expect anti-bot or session constraints on rapid crawling.
- Start discovery from listing pages rather than guessing video IDs.
- Use browser-grade headers and introduce request delays.

## Known Limitations

- Scene URL structure uses slugs, not numeric IDs — listing-first discovery required.
- Performer/member pages not confirmed during research.
- Search support unconfirmed.
- Full metadata availability requires live scene page fetch during implementation.

## Validation

Test against these live scene URLs:
- `https://thisvid.com/videos/blonde-anal-fun/`

- Test `sceneByURL` against a live scene page
- Test `performerByURL` if performer pages exist
- Test `sceneByName` if site search is usable
- Test fragment matching if practical
