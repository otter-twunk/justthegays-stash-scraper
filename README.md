# My Scrapers

This repo groups Stash scrapers by site, with one folder per scraper.

## Start Here

If you are creating a new scraper, use these files in order:

1. `START_HERE.md`
2. `workflow/PERPLEXITY_RESEARCH_INPUT.md`
3. `workflow/PERPLEXITY_GENERIC_REPO_BRIEF.md`
4. Have Perplexity apply the repo conventions, initiate the site research, choose `scrapers/<site-folder>/`, and draft the handoff structure, especially `SCRAPER_SPEC.json`, `PERPLEXITY_TO_CODEX_HANDOFF.md`, and `CODEX_PROMPT.md`
5. Run `scripts/create_scraper_from_template.sh <site-folder>`
   - or run `python3 scripts/create_scraper_from_spec.py /path/to/SCRAPER_SPEC.json` after Perplexity's research is already complete
6. `workflow/NEW_SCRAPER_CHECKLIST.md`

If you want Codex to build directly without a separate research pass, use:

- `workflow/CODEX_PROMPT.md`

## Layout

Each scraper lives in:

- `scrapers/<site-folder>/`

Each scraper folder should contain:

- the Stash scraper `.yml`
- the backing Python script
- a short `README.md`
- `SCRAPER_SPEC.json`
- `PERPLEXITY_TO_CODEX_HANDOFF.md`
- `CODEX_PROMPT.md`
- `TODO.md`

Current scrapers:

- `scrapers/allboner`
- `scrapers/boyfriendtv-com`
- `scrapers/everydayporn`
- `scrapers/gayforfans`
- `scrapers/gayhardfuck-com`
- `scrapers/gayfappy-com`
- `scrapers/gayporn`
- `scrapers/justthegays-tv`
- `scrapers/justthegays-com`
- `scrapers/gay0day-com`
- `scrapers/gayporntube-com`
- `scrapers/icegaytube-tv`
- `scrapers/manporn-xxx`
- `scrapers/mymusclevideo-com`
- `scrapers/thegay-com`
- `scrapers/thefap`
- `scrapers/thisvid`
- `scrapers/tnaflix-com`
- `scrapers/xhamster-com`
- `scrapers/xvideos`

## Workflow

### Recommended Flow

1. Run the Perplexity research brief in `workflow/PERPLEXITY_RESEARCH_INPUT.md`.
2. Have Perplexity apply the repo conventions from `workflow/PERPLEXITY_GENERIC_REPO_BRIEF.md`, identify the site structure, choose the folder name, and fill in `SCRAPER_SPEC.json`, `PERPLEXITY_TO_CODEX_HANDOFF.md`, and `CODEX_PROMPT.md`.
3. Run `scripts/create_scraper_from_template.sh <site-folder>`.
   - or run `python3 scripts/create_scraper_from_spec.py /path/to/SCRAPER_SPEC.json` after the research is done
4. Ask Codex to start from the files inside that scraper folder.
5. Validate and publish with `workflow/NEW_SCRAPER_CHECKLIST.md`.

### Direct Codex Flow

1. Use `workflow/CODEX_PROMPT.md`.
2. Point Codex at this repo.
3. Have it create the scraper from `templates/site-template/`.

## Add a New Scraper Manually

1. Copy `templates/site-template/`.
2. Rename the folder to `scrapers/<site-folder>/`.
3. Rename the template files for the target site.
4. Fill in `SCRAPER_SPEC.json`.
5. Update the folder-local `PERPLEXITY_TO_CODEX_HANDOFF.md` and `CODEX_PROMPT.md`.
6. Implement the scraper logic.
7. Test against live scene and performer pages when possible.
8. Update this README with the new scraper folder.

## Stash Install

For any scraper in this repo:

1. Copy that scraper's `.yml` and script file into your Stash `scrapers` directory.
2. Reload scrapers in Stash or restart the app.

## Conventions

- One site per scraper.
- Prefer Python-backed script scrapers.
- Keep folder names short and URL-safe.
- Keep structured scraper research in `SCRAPER_SPEC.json`.
- Document supported scrape modes in each scraper README.
- Preserve existing scraper behavior when adding new ones.

## Workflow Files

- `START_HERE.md`: one-page overview of the whole process
- `workflow/PERPLEXITY_RESEARCH_INPUT.md`: research brief for Perplexity
- `workflow/PERPLEXITY_GENERIC_REPO_BRIEF.md`: generic repo rules for Perplexity scaffolding
- `workflow/PERPLEXITY_TO_CODEX_HANDOFF.md`: repo-level handoff template
- `workflow/CODEX_PROMPT.md`: repo-level direct Codex prompt
- `workflow/NEW_SCRAPER_CHECKLIST.md`: QA and publish checklist
- `workflow/SIMPLE_CODEX_START.md`: minimal prompt to start Codex from a scraper folder
- `scripts/create_scraper_from_template.sh`: scaffolds a new scraper folder
- `scripts/create_scraper_from_spec.py`: scaffolds and renames a new scraper folder from completed research
- `scripts/validate_scraper_repo.py`: checks folder structure and required files
- `skills/create-stash-scraper/`: repo-local skill for turning research into a scraper

## Folder-Local Workflow Files

Each scraper folder can also include:

- `SCRAPER_SPEC.json`: machine-friendly research and implementation contract
- `PERPLEXITY_TO_CODEX_HANDOFF.md`: site-specific handoff for Codex
- `CODEX_PROMPT.md`: site-specific direct Codex prompt
- `TODO.md`: implementation progress checklist

The recommended automated flow is to have Perplexity initiate the research, choose the folder structure, populate `SCRAPER_SPEC.json`, and draft the folder-local workflow files before Codex starts implementation.

## Unified CLI Runner

Use one command to execute any scraper with normalized JSON output:

```bash
python scripts/run_scraper.py --site <site-folder> --mode <supported-mode> [--url <scene-url>] [--name <query>]
```

Examples:

```bash
python scripts/run_scraper.py --site xvideos --mode sceneByName --name "example title"
python scripts/run_scraper.py --site allboner --mode sceneByURL --url "https://www.allboner.com/videos/123/example/"
```

Output format is standardized as:

```json
{"results": []}
```

## Dependencies

All runtime and test dependencies are centralized in:

- `requirements.txt`

Install them with:

```bash
python -m pip install -r requirements.txt
```

## Testing and CI

Run local checks:

```bash
python scripts/validate_scraper_repo.py
pytest -q
```

GitHub Actions workflow:

- `.github/workflows/tests.yml`

## Audit and Verification Report

See `SCRAPER_AUDIT_REPORT.md` for:

- per-scraper status
- changes applied
- test outcomes
- remaining follow-up items
