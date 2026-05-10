#!/usr/bin/env python3

import json
import re
import ssl
import subprocess
import sys
from datetime import datetime
from difflib import SequenceMatcher
from html import unescape
from urllib.error import URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


BASE_URL = "https://justthegays.com"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/136.0.0.0 Safari/537.36"
)

SSL_CONTEXT = None
try:
    import certifi

    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CONTEXT = ssl.create_default_context()


PERFORMER_CACHE = {}


def read_stdin():
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    return json.loads(raw)


def fetch(url):
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
            return response.read().decode("utf-8", errors="replace")
    except URLError:
        result = subprocess.run(
            [
                "curl",
                "-L",
                "--silent",
                "--fail",
                "-A",
                USER_AGENT,
                url,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout


def normalize_space(value):
    return re.sub(r"\s+", " ", value or "").strip()


def html_unescape(value):
    return normalize_space(unescape(value or ""))


def strip_html(value):
    return html_unescape(re.sub(r"<[^>]+>", " ", value or ""))


def clean_details(value):
    text = html_unescape(value)
    if not text:
        return ""
    text = re.sub(r"^JustTheGays\s*-\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(
        r"\s*-\s*Stream the hottest gay .*?$",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"\|\s*Just The Gays\s*-\s*Hot free gay videos.*$",
        "",
        text,
        flags=re.IGNORECASE,
    )
    return normalize_space(text)


def parse_date(value):
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return value.split("T", 1)[0]


def unique_names(values):
    seen = set()
    output = []
    for value in values:
        name = normalize_space(value)
        if not name:
            continue
        key = name.casefold()
        if key in seen:
            continue
        seen.add(key)
        output.append({"name": name})
    return output


def normalize_title(value):
    value = unescape(value or "")
    value = value.lower()
    value = re.sub(r"\.[a-z0-9]{2,5}$", "", value)
    value = re.sub(r"[_./-]+", " ", value)
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    return normalize_space(value)


def normalize_fragment_text(value):
    value = unescape(value or "")
    value = re.sub(r"\.[a-z0-9]{2,5}$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^\d+\s*[-_. ]\s*", "", value)
    value = re.sub(r"[_./-]+", " ", value)
    return normalize_space(value)


def similarity(a, b):
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def extract_meta(html, attr, key):
    if attr == "property":
        pattern = rf'<meta[^>]+property=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)'
    else:
        pattern = rf'<meta[^>]+name=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)'
    match = re.search(pattern, html, flags=re.IGNORECASE)
    return html_unescape(match.group(1)) if match else ""


def extract_title_from_page(html):
    match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    title = strip_html(match.group(1))
    title = re.sub(r"\s*-\s*JustTheGays\.com\s*\|\s*Just The Gays\s*$", "", title)
    return normalize_space(title)


def slug_to_name(slug):
    slug = re.sub(r"-052611$", "", slug)
    slug = slug.replace("_", " ")
    slug = re.sub(r"\s+", " ", slug.replace("-", " ")).strip()
    return slug.title()


def performer_name_from_slug(slug):
    slug = re.sub(r"-052611$", "", slug)
    if slug in PERFORMER_CACHE:
        return PERFORMER_CACHE[slug]

    url = f"{BASE_URL}/performers/{slug}-052611/"
    try:
        html = fetch(url)
        name = extract_title_from_page(html)
        if name:
            PERFORMER_CACHE[slug] = name
            return name
    except Exception:
        pass

    fallback = slug_to_name(slug)
    PERFORMER_CACHE[slug] = fallback
    return fallback


def parse_article_classes(article_open_tag):
    categories = re.findall(r"\bcategories-([a-z0-9_-]+-052611)\b", article_open_tag, flags=re.IGNORECASE)
    performers = re.findall(r"\bvideo_tag-([a-z0-9_-]+-052611)\b", article_open_tag, flags=re.IGNORECASE)
    return categories, performers


def parse_search_results(html):
    pattern = re.compile(
        r'<article class="([^"]*?\bvideo\b[^"]*)".*?<a href="(https://justthegays\.com/video/[^"]+)".*?'
        r'<img[^>]+src="([^"]+)".*?<h3 class="post-title"><a href="[^"]+">(.*?)</a></h3>.*?'
        r'<div class="meta"><span class="date">(.*?)</span>',
        flags=re.IGNORECASE | re.DOTALL,
    )

    results = []
    for article_classes, url, image, title_html, relative_date in pattern.findall(html):
        category_slugs, performer_slugs = parse_article_classes(article_classes)
        results.append(
            {
                "title": strip_html(title_html),
                "url": url,
                "image": image,
                "details": "",
                "date": "",
                "relative_date": strip_html(relative_date),
                "category_slugs": category_slugs,
                "performer_slugs": performer_slugs,
            }
        )
    return results


def search_scenes(query):
    query = normalize_space(query)
    if not query:
        return []
    html = fetch(f"{BASE_URL}/?s={quote_plus(query)}")
    results = parse_search_results(html)
    results.sort(
        key=lambda item: (
            normalize_title(item["title"]) != normalize_title(query),
            -similarity(item["title"], query),
            item["title"],
        )
    )
    return [
        {
            "title": item["title"],
            "url": item["url"],
            "image": item["image"],
            "details": item["details"],
            "date": item["date"],
        }
        for item in results
    ]


def find_scene_match_by_title(title):
    html = fetch(f"{BASE_URL}/?s={quote_plus(title)}")
    results = parse_search_results(html)
    exact_title = normalize_title(title)
    for item in results:
        if normalize_title(item["title"]) == exact_title:
            return item
    if results:
        best = max(results, key=lambda item: similarity(item["title"], title))
        if similarity(best["title"], title) >= 0.75:
            return best
    return None


def scrape_scene(url):
    html = fetch(url)
    title = extract_title_from_page(html)
    image = extract_meta(html, "property", "og:image")
    details = clean_details(extract_meta(html, "name", "description") or extract_meta(html, "property", "og:description"))
    date = parse_date(extract_meta(html, "property", "article:published_time") or extract_meta(html, "property", "og:updated_time"))

    scene = {
        "title": title,
        "url": url,
        "image": image,
        "details": details,
        "date": date,
    }

    match = find_scene_match_by_title(title)
    if match and match["url"] == url:
        if not scene["image"]:
            scene["image"] = match["image"]
        scene["tags"] = unique_names(slug_to_name(slug) for slug in match["category_slugs"])
        scene["performers"] = unique_names(
            performer_name_from_slug(slug) for slug in match["performer_slugs"]
        )

    return {key: value for key, value in scene.items() if value}


def best_scene_match(query):
    results = search_scenes(query)
    if not results:
        return {}
    best = results[0]
    exact = normalize_title(best["title"]) == normalize_title(query)
    if not exact and similarity(best["title"], query) < 0.55:
        return {}
    return scrape_scene(best["url"])


def extract_fragment_query(fragment):
    if isinstance(fragment, dict):
        direct = fragment.get("title") or fragment.get("name") or fragment.get("code")
        if direct:
            return normalize_fragment_text(direct)
        url = fragment.get("url", "")
        if "justthegays.com/video/" in url:
            return url
        for file_info in fragment.get("files", []):
            basename = file_info.get("basename") or file_info.get("path") or ""
            if basename:
                return normalize_fragment_text(basename)
    elif isinstance(fragment, str):
        return normalize_fragment_text(fragment)
    return ""


def handle_scene_by_fragment(fragment):
    query = extract_fragment_query(fragment)
    if not query:
        return {}
    if isinstance(query, str) and "justthegays.com/video/" in query:
        return scrape_scene(query)
    return best_scene_match(query)


def scrape_performer(url):
    html = fetch(url)
    name = extract_title_from_page(html)
    details = clean_details(extract_meta(html, "name", "description") or extract_meta(html, "property", "og:description"))
    image = extract_meta(html, "property", "og:image")

    performer = {
        "name": name,
        "url": url,
        "gender": "Male",
        "image": image,
        "details": details,
    }
    return {key: value for key, value in performer.items() if value}


def main():
    if len(sys.argv) < 2:
        print("{}")
        return

    mode = sys.argv[1]
    data = read_stdin()

    if mode == "sceneByURL":
        result = scrape_scene(data.get("url", ""))
    elif mode == "sceneByName":
        result = search_scenes(data.get("name", ""))
    elif mode in {"sceneByQueryFragment", "sceneByFragment"}:
        result = handle_scene_by_fragment(data)
    elif mode == "performerByURL":
        result = scrape_performer(data.get("url", ""))
    else:
        result = {}

    print(json.dumps(result))


if __name__ == "__main__":
    main()
