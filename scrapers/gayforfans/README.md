# GayForFans Stash Scraper

Files:

- `GayForFans.yml`
- `GayForFans.py`

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

- This scraper targets [gayforfans.com](https://gayforfans.com/).
- It uses Python only and does not require third-party packages.
- Scene pages expose `VideoObject` JSON-LD with title, upload date, thumbnail, actors, keywords, and a templated description.
- Performer pages expose `Person` JSON-LD and a dedicated `/performer/<slug>/` route.

Known limitations:

- Scene descriptions are site-generated marketing text, not always creator-written synopses.
- Tags come from category-style keywords and intentionally drop the generic `Video` category.
- Search and fragment matching rely on the site search endpoint, so weak filenames may still miss the correct scene.
