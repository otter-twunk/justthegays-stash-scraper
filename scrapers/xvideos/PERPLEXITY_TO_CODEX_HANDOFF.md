# Perplexity to Codex Handoff

Target site: `https://www.xvideos.com`

Target folder: `scrapers/xvideos/`

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
- `performerByURL`

## Site Notes

- Platform: Custom/proprietary (XVideos in-house platform)
- Site is an adult content source; keep scraping metadata-only and respect rate limits
- Live validation on 2026-05-11 confirmed public scene, search, and profile pages are accessible with normal browser headers

## Metadata Mapping

- **scene_title**: `window.xv.conf.dyn.video_title` OR `html5player.setVideoTitle(...)` OR JSON-LD `VideoObject.name`
- **date**: JSON-LD `VideoObject.uploadDate`
- **description**: JSON-LD `VideoObject.description` OR `meta[name="description"]`
- **cover_image**: JSON-LD `VideoObject.thumbnailUrl[0]` OR `html5player.setThumbUrl169(...)` OR `og:image`
- **performers**: primary uploader/profile link in the scene metadata block at `/profiles/<name>`; `window.xv.conf.dyn.video_models` may still be empty
- **tags**: `window.xv.conf.dyn.video_tags` OR `/tags/` links
- **studio**: `html5player.setSponsors(...)` when present; commonly `false`
- **performer profile**: `window.xv.conf.data.user` plus `pinfo-*` fields in the profile HTML

## Anti-Bot / Access Notes

- No Cloudflare detected on the validated public pages.
- Standard browser-grade headers (`User-Agent`, `Accept-Language`) were sufficient.
- The scraper can stay dependency-light and use direct HTTP requests.

## Known Limitations

- `video_models` is frequently empty on amateur or uploader-driven pages.
- Performer pages use `/profiles/` rather than a dedicated studio or pornstar route.
- Signed CDN media URLs expire; do not store raw stream URLs.
- Search results provide listing metadata only; full scene details should come from `sceneByURL`.

## Validation

Validated examples on 2026-05-11:

- Scene URL: `https://www.xvideos.com/video57885821/mi_gran_polla`
- Performer URL: `https://www.xvideos.com/profiles/negro-guebo`
- Search query: `gay`

Observed URL behavior:

- Canonical scene URLs currently appear as `https://www.xvideos.com/video.<id_or_hash>/<slug>` on page metadata and search listings, although some older `video<id>/<slug>` links still resolve.
