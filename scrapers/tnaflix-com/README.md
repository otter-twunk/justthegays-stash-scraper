# TNAFlix Scraper

Stash scraper for [tnaflix.com](https://www.tnaflix.com/).

## Supported Modes

| Hook | Status |
|---|---|
| `sceneByURL` | ✅ Implemented |
| `sceneByName` | ✅ Implemented |
| `performerByURL` | ✅ Implemented |
| `sceneByQueryFragment` | ❌ Not implemented |
| `sceneByFragment` | ❌ Not implemented |

## Metadata Coverage

| Field | Source |
|---|---|
| title | JSON-LD `VideoObject.name` |
| date | JSON-LD `VideoObject.uploadDate` |
| description | JSON-LD `VideoObject.description` (empty if `"No description provided"`) |
| image | JSON-LD `VideoObject.thumbnailUrl` (plain string) |
| performers | `a.badge-kiss` links in page HTML |
| tags | Category slug from scene URL (title-cased) |
| studio | Hardcoded: `TNAFlix` |

## Known Limitations

- No per-scene tag list; only the URL category slug is available as a tag
- Performer profiles have no bio data (no birthdate, gender, country)
- `description` is often blank for user-uploaded content
- Studio is always `TNAFlix`

## Implementation Notes

- Platform: custom tube; no Cloudflare protection
- Python 3, stdlib only (`urllib` + optional `certifi`)
- Scene URL pattern: `https://www.tnaflix.com/{category}/{slug}/video{id}`
- Performer URL pattern: `https://www.tnaflix.com/profile/{slug}`
- Search endpoint: `https://www.tnaflix.com/search?what={query}`

## Validation Example

```
Scene: https://www.tnaflix.com/amateur-porn/Best-Of-Lolo-Ferrari/video563066
  title:      Best Of Lolo Ferrari
  date:       2013-12-09
  performers: Lolo Ferrari
  tags:       Amateur Porn
  studio:     TNAFlix

Performer: https://www.tnaflix.com/profile/lolo-ferrari
  name:  Lolo Ferrari
  image: https://img.tnaflix.com/q80w210r/pics/alpha/pornstars/3208712.jpg
```
