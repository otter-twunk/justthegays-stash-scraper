# JustTheGays.tv Stash Scraper

Files:

- `JustTheGays.yml`
- `JustTheGays.py`

Install:

1. Copy both files into your Stash `scrapers` directory.
2. In Stash, reload scrapers or restart the app.

What it supports:

- `sceneByURL`
- `sceneByName`
- `sceneByQueryFragment`
- `sceneByFragment`
- `performerByURL`

Notes:

- This scraper uses Python only and does not require extra packages.
- `sceneByName` returns search matches from JustTheGays.
- `sceneByQueryFragment` and `sceneByFragment` try to find the closest JustTheGays match from the scene title or filename.


## Command-line execution

Run this scraper through the repository CLI wrapper:

```bash
python scripts/run_scraper.py --site justthegays-tv --mode <supported-mode> [--url <scene-url>] [--name <scene-name>]
```

Standardized output format:

```json
{"results": [{"title": "Example", "url": "https://example.com/video"}]}
```

Configuration:

- Runtime dependencies are installed from the repository root `requirements.txt`.
- No site credentials are required for default metadata scraping.

Testing:

```bash
pytest -q
```

The test suite includes a CLI smoke test for this scraper (`unsupportedMode` path) to verify executable entrypoint and valid JSON output.
