# Perplexity to Codex Handoff

Use this as the repo-level template.

The preferred flow is to copy this into `scrapers/<site-folder>/PERPLEXITY_TO_CODEX_HANDOFF.md` and tailor it to the target site.

```text
Create a working Stash scraper for SITE_URL in this repository.

Repository:
- Repo name: otter-twunk/my-scrapers
- Structure: one scraper per folder under `scrapers/<site-folder>/`

Your job:
- Read the research below and use it as implementation guidance
- Create the new scraper in `scrapers/<site-folder>/`
- Include:
  - the scraper `.yml`
  - the backing Python script
  - a short `README.md`
  - keep `SCRAPER_SPEC.json` as the machine-friendly research contract
  - keep `PERPLEXITY_TO_CODEX_HANDOFF.md` in the folder as the research record
  - update `CODEX_PROMPT.md` in the folder if implementation details change
- Follow official Stash scraper conventions
- Preserve existing scrapers and repo structure
- Update the root `README.md` with the new scraper folder

Implementation requirements:
- Prefer Python for the script scraper
- Support the Stash hook modes that are realistic for this site based on the research
- Keep the scraper scoped to this single website
- Handle missing metadata gracefully
- Avoid introducing unnecessary dependencies

Validation requirements:
- Test `sceneByURL` against a live scene page if possible
- Test `performerByURL` if performer pages exist
- Test `sceneByName` if the site has a usable search flow
- Test fragment matching if the research suggests it is practical
- Report any known limitations clearly

Use these repo helpers:
- Start from `templates/site-template/`
- Follow `workflow/NEW_SCRAPER_CHECKLIST.md`
- Use `SCRAPER_SPEC.json` first when specific implementation details are needed

Research:

PASTE PERPLEXITY OUTPUT HERE
```
