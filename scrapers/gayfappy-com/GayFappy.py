#!/usr/bin/env python3
"""
GayFappy.com Stash scraper.
Supported: sceneByURL, sceneByName, sceneByQueryFragment, sceneByFragment
"""

import json
import re
import sys
from datetime import datetime
from difflib import SequenceMatcher
from html import unescape
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://gayfappy.com"
SEARCH_URL = "https://gayfappy.com/?s={query}"
STUDIO = "Gay Fappy"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

GENERIC_PERFORMER_TAGS = {
    "adult",
    "amateur",
    "anal",
    "bareback",
    "bathroom",
    "bedroom",
    "big dick",
    "blowjob",
    "bottom",
    "category",
    "college",
    "cumshot",
    "cute",
    "daddy",
    "free onlyfans videos",
    "gay",
    "guys",
    "latin",
    "leak",
    "men",
    "muscle",
    "onlyfans leaks",
    "onlyfans videos",
    "outdoor",
    "raw",
    "shower",
    "solo",
    "straight",
    "threesome",
    "twink",
    "young",
    "young twink",
    "videos",
}


def read_stdin() -> dict:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    return json.loads(raw)


def fetch(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def clean_text(text: str) -> str:
    return normalize_text(unescape(text or ""))


def absolute_url(url: str) -> str:
    url = clean_text(url)
    if not url:
        return ""
    return urljoin(BASE_URL, url)


def unique_named_dicts(values) -> list:
    seen = set()
    output = []
    for value in values:
        name = clean_text(value)
        if not name:
            continue
        key = name.casefold()
        if key in seen:
            continue
        seen.add(key)
        output.append({"name": name})
    return output


def normalize_title(value: str) -> str:
    value = unescape(value or "").lower()
    value = re.sub(r"\.[a-z0-9]{2,5}$", "", value)
    value = re.sub(r"^\d+\s*[-_. ]\s*", "", value)
    value = value.replace("&", " and ")
    value = re.sub(r"[_./-]+", " ", value)
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    return normalize_text(value)


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def parse_date(soup: BeautifulSoup) -> str:
    time_tag = soup.select_one("time.post-date, time.entry-date, .entry-meta time")
    if time_tag:
        raw_value = clean_text(time_tag.get("datetime") or time_tag.get_text(" ", strip=True))
        if raw_value:
            raw_value = raw_value.split("T", 1)[0]
            try:
                return datetime.fromisoformat(raw_value).date().isoformat()
            except ValueError:
                pass
            for fmt in ("%B %d, %Y", "%b %d, %Y"):
                try:
                    return datetime.strptime(raw_value, fmt).date().isoformat()
                except ValueError:
                    continue

    text = clean_text(soup.get_text(" ", strip=True))
    match = re.search(r"\b([A-Z][a-z]+ \d{1,2}, \d{4})\b", text)
    if not match:
        return ""
    try:
        return datetime.strptime(match.group(1), "%B %d, %Y").date().isoformat()
    except ValueError:
        return ""


def extract_details(soup: BeautifulSoup) -> str:
    container = soup.select_one("article .entry-content .entry-content") or soup.select_one("article .entry-content")
    if not container:
        return ""

    lines = []
    seen = set()
    for node in container.select("p, li"):
        text = clean_text(node.get_text(" ", strip=True))
        if not text or text.lower() == "more":
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        lines.append(text)

    details = " ".join(lines)
    details = re.sub(r"\bLeave a Reply\b.*$", "", details, flags=re.IGNORECASE)
    return normalize_text(details)


def extract_tags(soup: BeautifulSoup) -> list:
    tags = []
    for link in soup.select(".post-tag a, .tags-links a, a[rel='tag'], a[href*='/index.php/tag/']"):
        href = link.get("href", "")
        if "/tag/" not in href:
            continue
        tags.append(link.get_text(" ", strip=True))
    return unique_named_dicts(tags)


def looks_like_performer_tag(name: str) -> bool:
    raw_name = clean_text(name)
    normalized = normalize_title(name)
    if not normalized:
        return False
    if not re.fullmatch(r"[A-Za-z ]+", raw_name):
        return False
    if normalized in GENERIC_PERFORMER_TAGS:
        return False
    if any(char.isdigit() for char in normalized):
        return False
    if len(normalized) < 5 or len(normalized) > 32:
        return False
    words = normalized.split()
    if len(words) < 2 or len(words) > 3:
        return False
    if any(len(word) < 2 for word in words):
        return False
    return True


def extract_performer_candidates(tag_names) -> list:
    performers = []
    for tag_name in tag_names:
        if looks_like_performer_tag(tag_name):
            performers.append(tag_name)
    return unique_named_dicts(performers)


def extract_image(soup: BeautifulSoup) -> str:
    for tag in (
        soup.find("meta", attrs={"property": "og:image"}),
        soup.find("meta", attrs={"name": "og:image"}),
    ):
        if tag and tag.get("content"):
            return absolute_url(tag.get("content"))

    for img in soup.select("figure.post-image img, .entry-content img, img.wp-post-image"):
        src = img.get("src") or img.get("data-lazy-src") or ""
        if src and not src.startswith("data:image"):
            return absolute_url(src)
    return ""


def scrape_scene(url: str) -> dict:
    if not url:
        return {}

    soup = fetch(url)

    title = ""
    title_node = soup.select_one("h1.entry-title, h1.post-title")
    if title_node:
        title = clean_text(title_node.get_text(" ", strip=True))
    if not title and soup.title:
        title = clean_text(re.sub(r"\s*[-|]\s*Gay Fappy.*$", "", soup.title.get_text(), flags=re.IGNORECASE))

    tags = extract_tags(soup)
    tag_names = [tag["name"] for tag in tags]

    scene = {
        "title": title,
        "url": url,
        "date": parse_date(soup),
        "details": extract_details(soup),
        "image": extract_image(soup),
        "studio": {"name": STUDIO},
        "performers": extract_performer_candidates(tag_names),
        "tags": tags,
    }
    return {key: value for key, value in scene.items() if value}


def parse_search_result(article: BeautifulSoup) -> dict:
    link = article.select_one("figure.post-image a[href*='/index.php/'], a.more-link[href*='/index.php/'], h1 a[href*='/index.php/'], h2 a[href*='/index.php/']")
    if not link:
        return {}

    url = absolute_url(link.get("href", ""))
    if not re.search(r"/index\.php/\d+/.+/?$", url):
        return {}

    title = ""
    img = article.select_one("img")
    if img:
        title = clean_text(img.get("alt") or img.get("title") or "")
    if not title:
        desc = article.select_one(".post_desc")
        if desc:
            title = clean_text(desc.get_text(" ", strip=True))
    if not title:
        heading = article.select_one(".entry-title, .post-title")
        if heading:
            title = clean_text(heading.get_text(" ", strip=True))

    if not title:
        return {}

    is_video = "category-videos" in (article.get("class") or [])
    image = ""
    if img:
        image = absolute_url(img.get("src") or img.get("data-lazy-src") or "")

    return {
        "title": title,
        "url": url,
        "image": image,
        "_is_video": is_video,
    }


def search_scenes(query: str) -> list:
    query = normalize_text(query)
    if not query:
        return []

    soup = fetch(SEARCH_URL.format(query=quote_plus(query)))
    results = []
    seen = set()
    for article in soup.select("article.post"):
        result = parse_search_result(article)
        if not result:
            continue
        key = result["url"]
        if key in seen:
            continue
        seen.add(key)
        results.append(result)

    results.sort(
        key=lambda item: (
            normalize_title(item["title"]) != normalize_title(query),
            not item.get("_is_video", False),
            -similarity(item["title"], query),
            item["title"],
        )
    )

    cleaned = []
    for item in results:
        cleaned.append({key: value for key, value in item.items() if value and not key.startswith("_")})
    return cleaned


def extract_fragment_query(data) -> str:
    if isinstance(data, str):
        return normalize_text(data)
    if not isinstance(data, dict):
        return ""

    direct = data.get("title") or data.get("name") or data.get("filename") or data.get("code")
    if direct:
        return normalize_text(direct)

    url = data.get("url", "")
    if "/index.php/" in url:
        return url

    for file_info in data.get("files", []):
        basename = file_info.get("basename") or file_info.get("path") or ""
        if basename:
            return normalize_text(basename)
    return ""


def best_scene_match(query: str) -> dict:
    if "/index.php/" in query:
        return scrape_scene(query)

    results = search_scenes(query)
    if not results:
        return {}

    best = results[0]
    score = similarity(best["title"], query)
    exact = normalize_title(best["title"]) == normalize_title(query)
    if not exact and score < 0.55:
        return {}
    return scrape_scene(best["url"])


def scene_by_url():
    inp = read_stdin()
    print(json.dumps(scrape_scene(inp.get("url", ""))))


def scene_by_name():
    inp = read_stdin()
    print(json.dumps(search_scenes(inp.get("name", ""))))


def scene_by_query_fragment():
    inp = read_stdin()
    query = extract_fragment_query(inp)
    if "/index.php/" in query:
        scene = scrape_scene(query)
        print(json.dumps([scene] if scene else []))
        return
    print(json.dumps(search_scenes(query)))


def scene_by_fragment():
    inp = read_stdin()
    query = extract_fragment_query(inp)
    if not query:
        print(json.dumps({}))
        return
    print(json.dumps(best_scene_match(query)))


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
