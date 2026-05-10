# JustTheGays.com Stash Scraper

Files:

- `JustTheGaysCom.yml`
- `JustTheGaysCom.py`

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

- This scraper targets `https://justthegays.com`.
- It uses Python only and does not require extra packages.
- It can enrich scene URL scrapes with categories and performers by matching the scene against the site's own search results.
