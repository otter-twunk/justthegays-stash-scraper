# Codex Prompt

Use this as the repo-level direct Codex prompt.

The preferred flow is to copy this into `scrapers/<site-folder>/CODEX_PROMPT.md` and tailor it to the target site so Codex can start from files in that folder.

```text
Create a working Stash scraper for SITE_URL in this repository.

Requirements:
- Follow the existing repo structure with one scraper per folder under `scrapers/<site-folder>/`
- Include the scraper `.yml`, backing script, and a short `README.md`
- Keep folder-local workflow notes in `SCRAPER_SPEC.json`, `PERPLEXITY_TO_CODEX_HANDOFF.md`, and `CODEX_PROMPT.md`
- Follow official Stash scraper conventions
- Support the appropriate scene and performer scrape modes for the site
- Prefer Python for the script scraper
- Test against live pages if possible
- Preserve existing scrapers
- Update the root README with the new scraper folder

Also:
- Start from `templates/site-template/`
- Rename the files appropriately
- Document any known limitations
- Use `SCRAPER_SPEC.json` as the primary machine-friendly implementation guide
```
