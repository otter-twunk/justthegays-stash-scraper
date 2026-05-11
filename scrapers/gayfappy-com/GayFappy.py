#!/usr/bin/env python3
"""
GayFappy.com Stash scraper stub.
See SCRAPER_SPEC.json and PERPLEXITY_TO_CODEX_HANDOFF.md for full implementation spec.
Codex: implement each handler function below.
"""

import sys
import json
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus

BASE_URL = "https://gayfappy.com"
SEARCH_URL = "https://gayfappy.com/?s={query}"
STUDIO = "Gay Fappy"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36"
}


def fetch(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def normalize_text(text: str) -> str:
    """Collapse repeated whitespace. TODO: refine during implementation."""
    return re.sub(r"\s+", " ", (text or "")).strip()


def extract_performer_candidates(tag_names):
    """
    Infer performer-like tags conservatively.
    TODO: implement heuristic filtering (e.g. two-word title-case labels).
    """
    raise NotImplementedError


def scrape_scene(url: str) -> dict:
    """
    Scrape a GayFappy post page and return a Stash-compatible scene dict.
    Fields: title, date, details, image, performers, tags, studio, url.
    TODO: implement this.
    """
    raise NotImplementedError


def search_scenes(query: str) -> list:
    """
    Search gayfappy.com and return a list of scene result dicts [{title, url}, ...].
    URL: https://gayfappy.com/?s={query}
    TODO: implement this.
    """
    raise NotImplementedError


def scene_by_url():
    inp = json.loads(sys.stdin.read())
    url = inp.get("url", "")
    result = scrape_scene(url)
    print(json.dumps(result))


def scene_by_name():
    inp = json.loads(sys.stdin.read())
    query = inp.get("name", "")
    results = search_scenes(query)
    print(json.dumps(results))


def scene_by_query_fragment():
    inp = json.loads(sys.stdin.read())
    query = inp.get("title", "") or inp.get("name", "")
    results = search_scenes(query)
    print(json.dumps(results))


def scene_by_fragment():
    inp = json.loads(sys.stdin.read())
    query = inp.get("title", "") or inp.get("filename", "")
    if not query:
        print(json.dumps({}))
        return
    results = search_scenes(query)
    if results:
        top = scrape_scene(results[0]["url"])
        print(json.dumps(top))
    else:
        print(json.dumps({}))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    dispatch = {
        "sceneByURL": scene_by_url,
        "sceneByName": scene_by_name,
        "sceneByQueryFragment": scene_by_query_fragment,
        "sceneByFragment": scene_by_fragment,
    }
    fn = dispatch.get(mode)
    if fn:
        fn()
    else:
        print(json.dumps({"error": f"Unknown mode: {mode}"}), file=sys.stderr)
        sys.exit(1)
