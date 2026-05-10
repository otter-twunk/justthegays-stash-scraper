# New Scraper Checklist

Use this before publishing a new scraper to the repo.

## Research

- Confirm the target site URL and preferred folder name.
- Confirm whether the site is custom, WordPress, or another common platform.
- Identify scene page URLs and performer page URLs.
- Identify where title, date, image, description, tags, studio, and performers appear.
- Note whether the site exposes search that can support `sceneByName` or fragment matching.

## Repo Setup

- Copy `templates/site-template/` into `scrapers/<site-folder>/`.
- Rename the template files for the target scraper.
- Fill in `SCRAPER_SPEC.json`.
- Add or update `PERPLEXITY_TO_CODEX_HANDOFF.md` in the scraper folder.
- Add or update `CODEX_PROMPT.md` in the scraper folder.
- Update `TODO.md` during implementation.
- Update the scraper README with site-specific notes.
- Add the new scraper folder to the root `README.md`.

## Scraper Implementation

- Set the scraper `name`, `description`, and script path in the `.yml`.
- Implement the supported Stash hook modes.
- Keep the scraper scoped to a single website.
- Preserve the structure and behavior of existing scrapers.

## Validation

- Test `sceneByURL` against a live scene page.
- Test `performerByURL` if performer pages exist.
- Test `sceneByName` if the site has a usable search flow.
- Test fragment matching if filenames or scene titles make that practical.
- Verify the scraper returns sensible empty results when data is missing.

## Publish

- Confirm the folder contains only the scraper files and README.
- Check for accidental temp files, caches, or local machine artifacts.
- Run `python3 scripts/validate_scraper_repo.py`.
- Commit with a short site-specific message.
- Push to `main`.
- Verify the repo renders the new files correctly on GitHub.

## Install Notes

- Confirm the README tells the user which `.yml` and script file to copy into Stash.
- Note any dependencies or known limitations clearly.
