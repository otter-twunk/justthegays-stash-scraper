# Codex Prompt

Use this prompt to add a new scraper to this repo:

```text
Create a working Stash scraper for SITE_URL in this repository.

Requirements:
- Follow the existing repo structure with one scraper per folder under `scrapers/<site-folder>/`
- Include the scraper `.yml`, backing script, and a short `README.md`
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
```
