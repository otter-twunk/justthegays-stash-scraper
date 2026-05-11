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

## Site Notes

- Platform: Custom social/content platform (not KVS)
- Route structure confirmed from homepage HTML inspection in May 2026
- Not a standard KVS or WordPress install — all parsing must be custom
- Publicly accessible routes: `/videos/`, `/explore/`, `/g/<slug>`
- Profile/performer URLs follow `/<username>-<id>/` pattern
- Some content may be login-gated
- Site is an adult content source — keep scraping metadata-only

## Metadata Mapping

- **scene_title**: `og:title` or page `<title>`
- **date**: Not confirmed — requires live scene/post page parse during implementation
- **description**: `og:description`
- **cover_image**: `og:image`
- **performers**: Profile links at `/<username>-<id>/` or `/feed/<name-id>`
- **tags**: Group/category links at `/g/<slug>`
- **studio**: Not applicable — community/social platform

## Anti-Bot / Access Notes

- Custom platform; route structure confirmed from homepage HTML.
- Social/login-gated content may limit anonymous access.
- Begin with publicly accessible /videos/ and /explore/ routes.
- Treat as a community site — respect rate limits and session handling.

## Known Limitations

- Not a standard KVS or WordPress install — custom parsing required throughout.
- Some content may require login.
- Post/video/profile entity distinction needs clarification during implementation.
- Full metadata availability requires live page fetches.

## Validation

Discover scene URLs from the listing page during implementation:
- `https://thefap.net/videos/`

- Test `sceneByURL` against a live scene page
- Test `performerByURL` if performer pages exist
- Test fragment matching if practical
