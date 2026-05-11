# Codex Prompt

Start from the files in this folder and build the scraper for `https://gayforfans.com/`.

Read `SCRAPER_SPEC.json` first.

Requirements:

- Follow Stash script scraper conventions
- Implement `sceneByURL`, `sceneByName`, `sceneByQueryFragment`, `sceneByFragment`, and `performerByURL`
- Prefer Python for the scraper script
- Keep the scraper scoped to `gayforfans.com`
- Handle missing metadata gracefully
- Avoid unnecessary dependencies
- Preserve other scrapers in the repo

Files in this folder:

- `SCRAPER_SPEC.json`
- `GayForFans.yml`
- `GayForFans.py`
- `README.md`
- `PERPLEXITY_TO_CODEX_HANDOFF.md`
- `TODO.md`

Also:

- Use `SCRAPER_SPEC.json` as the primary structured input
- Keep `PERPLEXITY_TO_CODEX_HANDOFF.md` updated as the implementation guide
- Update the root `README.md` with this scraper folder
- Validate with `workflow/NEW_SCRAPER_CHECKLIST.md`
