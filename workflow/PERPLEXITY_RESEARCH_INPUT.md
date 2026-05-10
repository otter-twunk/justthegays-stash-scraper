# Perplexity Research Input

Use this prompt before asking Codex to build a new scraper.

This version is designed to increase handoff automation by having Perplexity draft the folder-local workflow files that Codex can start from.

```text
Research how to build a Stash scraper for SITE_URL.

I want practical implementation research, not a generic overview.

Please do all of the following:

1. Review the official Stash scraper documentation and summarize only the parts relevant to building a script scraper for this site.
2. Inspect SITE_URL and determine:
   - whether the site is custom, WordPress, or another known platform
   - the structure of scene pages
   - the structure of performer pages
   - whether the site has search that can support title lookup
   - whether filename or fragment matching is likely to work
3. Identify how the following metadata appears on the site:
   - scene title
   - date
   - description
   - cover image
   - performers
   - tags or categories
   - studio or site name
4. Provide likely selectors, page patterns, or parsing strategies for extracting that metadata.
5. Note any blockers, anti-bot issues, missing metadata, inconsistent page layouts, or weak areas where scrape quality may be limited.
6. Recommend which Stash hook modes are realistic for this site:
   - sceneByURL
   - sceneByName
   - sceneByQueryFragment
   - sceneByFragment
   - performerByURL
7. Suggest a short URL-safe folder name for adding this scraper to the repo `otter-twunk/my-scrapers` under `scrapers/<folder-name>/`.
8. Draft the full contents for `scrapers/<folder-name>/SCRAPER_SPEC.json` using a machine-friendly structure.
9. Draft the full contents for these two files inside that folder:
   - `scrapers/<folder-name>/PERPLEXITY_TO_CODEX_HANDOFF.md`
   - `scrapers/<folder-name>/CODEX_PROMPT.md`

Output format:
- Short implementation summary
- Recommended supported hook modes
- Metadata field mapping
- Suggested selectors or parsing approach
- Known limitations
- Suggested folder name
- Full content for `SCRAPER_SPEC.json`
- Full content for `PERPLEXITY_TO_CODEX_HANDOFF.md`
- Full content for `CODEX_PROMPT.md`
- Source links
```
