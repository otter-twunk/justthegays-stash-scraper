# Codex Prompt

Start from the files in this folder and build the scraper for `https://thefap.net`.

Read `SCRAPER_SPEC.json` first.

Requirements:

- Follow Stash script scraper conventions
- Implement the realistic hook modes for this site
- Prefer Python for the scraper script
- Keep the scraper scoped to this single website
- Handle missing metadata gracefully
- Avoid unnecessary dependencies
- Preserve other scrapers in the repo

Files to create or update in this folder:

- `SCRAPER_SPEC.json`
- the scraper `.yml`
- the backing Python script
- `README.md`
- keep this `CODEX_PROMPT.md` and `PERPLEXITY_TO_CODEX_HANDOFF.md` as workflow notes

Also:

- Start from the site template files in this folder
- Use `SCRAPER_SPEC.json` as the primary structured input
- Use `PERPLEXITY_TO_CODEX_HANDOFF.md` as the research and implementation guide
- Update the root `README.md` with this scraper folder
- Validate the result with `workflow/NEW_SCRAPER_CHECKLIST.md`
