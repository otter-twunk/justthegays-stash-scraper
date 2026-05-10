# My Scrapers

This repo groups Stash scrapers by site, with one folder per scraper.

## Layout

Each scraper lives in:

- `scrapers/<site-folder>/`

Each scraper folder should contain:

- the Stash scraper `.yml`
- the backing Python script
- a short `README.md`

Current scrapers:

- `scrapers/justthegays-tv`
- `scrapers/justthegays-com`

## Add a New Scraper

1. Copy `templates/site-template/`.
2. Rename the folder to `scrapers/<site-folder>/`.
3. Rename the template files for the target site.
4. Implement the scraper logic.
5. Test against live scene and performer pages when possible.
6. Update this README with the new scraper folder.

## Stash Install

For any scraper in this repo:

1. Copy that scraper's `.yml` and script file into your Stash `scrapers` directory.
2. Reload scrapers in Stash or restart the app.

## Conventions

- One site per scraper.
- Prefer Python-backed script scrapers.
- Keep folder names short and URL-safe.
- Document supported scrape modes in each scraper README.
- Preserve existing scraper behavior when adding new ones.

## Codex Workflow

Use the reusable prompt in `workflow/CODEX_PROMPT.md` when creating the next scraper.
