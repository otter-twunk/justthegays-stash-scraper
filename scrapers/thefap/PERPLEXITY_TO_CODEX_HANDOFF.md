# Perplexity to Codex Handoff

Target site: `https://thefap.net`

Target folder: `scrapers/thefap/`

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
- `performerByURL`

## Site Notes

- Platform: Custom social/content platform (not KVS)
- Route structure confirmed from homepage HTML inspection in May 2026
- Not a standard KVS or WordPress install — all parsing must be custom
- Publicly accessible routes: `/videos/`, `/explore/`, `/g/<slug>`
- Profile/performer URLs follow `/<username>-<id>/` pattern
- Some content may be login-gated
- Site is an adult content source — keep scraping metadata-only

## Metadata Mapping

- **scene_title**: scene header text or page `<title>`
- **date**: not reliably exposed on tested public scene pages
- **description**: derived from source slug and page title when site description is generic
- **cover_image**: embedded player iframe `i=` query param or listing thumbnail fallback
- **performers**: profile links at `/<username>-<id>/`
- **tags**: group/category links at `/g/<slug>` when present, otherwise URL source slug fallback
- **studio**: Not applicable — community/social platform

## Anti-Bot / Access Notes

- Custom platform; route structure confirmed from homepage HTML.
- Social/login-gated content may limit anonymous access.
- Begin with publicly accessible /videos/ and /explore/ routes.
- Treat as a community site — respect rate limits and session handling.

## Known Limitations

- Not a standard KVS or WordPress install — custom parsing required throughout.
- Some content may require login.
- Public scene pages tested in May 2026 do not expose a reliable publish date.
- Performer profile images appear to be gallery thumbnails rather than dedicated avatars.

## Validation

Discover scene URLs from the listing page during implementation:
- `https://thefap.net/videos/`

- Test `sceneByURL` against a live scene page such as `https://thefap.net/sortadandy-1405406/coomer/i4`
- Test `performerByURL` against a performer page such as `https://thefap.net/sortadandy-1405406/`
- Test fragment matching if practical
