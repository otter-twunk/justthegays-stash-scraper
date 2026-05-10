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
