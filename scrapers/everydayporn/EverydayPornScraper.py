#!/usr/bin/env python3

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from html import unescape
from urllib.parse import quote_plus, urljoin, urlparse

VENDOR_DIR = os.path.join(os.path.dirname(__file__), "_vendor")
if os.path.isdir(VENDOR_DIR) and VENDOR_DIR not in sys.path:
    sys.path.insert(0, VENDOR_DIR)

try:
    import cloudscraper
except Exception:  # pragma: no cover
    cloudscraper = None

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.everydayporn.co"
SEARCH_URL = BASE_URL + "/search/?q={query}"
SITE_STUDIO = "EveryDayPorn.co"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/136.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": BASE_URL + "/",
}
GENERIC_TAG_NAMES = {"categories", "all categories", "search", "home", "latest"}


def emit(payload):
    json.dump(payload, sys.stdout, ensure_ascii=False)


def read_request():
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    return json.loads(raw)


def normalize_space(value):
    return re.sub(r"\s+", " ", value or "").strip()


def clean_text(value):
    return normalize_space(unescape(value or ""))


def absolute_url(value):
    value = clean_text(value)
    if not value:
        return ""
    return urljoin(BASE_URL, value)


def strip_html(value):
    return clean_text(re.sub(r"<[^>]+>", " ", value or ""))


def normalize_title(value):
    value = unescape(value or "").lower()
    value = re.sub(r"\.[a-z0-9]{2,5}$", "", value)
    value = re.sub(r"^\d+\s*[-_. ]\s*", "", value)
    value = re.sub(r"[_./-]+", " ", value)
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    return normalize_space(value)


def similarity(a, b):
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def token_overlap_score(a, b):
    tokens_a = set(normalize_title(a).split())
    tokens_b = set(normalize_title(b).split())
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_b)


def unique_named_items(values):
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


def parse_iso_date(value):
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return value.split("T", 1)[0]


def parse_relative_date(text):
    text = clean_text(text).lower()
    if not text:
        return ""

    now = datetime.now(timezone.utc)
    if text in {"today", "just now"}:
        return now.date().isoformat()
    if text == "yesterday":
        return (now - timedelta(days=1)).date().isoformat()

    match = re.search(r"(\d+)\s+(minute|hour|day|week|month|year)s?\s+ago", text)
    if not match:
        return ""

    amount = int(match.group(1))
    unit = match.group(2)
    if unit == "minute":
        delta = timedelta(minutes=amount)
    elif unit == "hour":
        delta = timedelta(hours=amount)
    elif unit == "day":
        delta = timedelta(days=amount)
    elif unit == "week":
        delta = timedelta(weeks=amount)
    elif unit == "month":
        delta = timedelta(days=amount * 30)
    else:
        delta = timedelta(days=amount * 365)

    return (now - delta).date().isoformat()


def create_session():
    if cloudscraper:
        return cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )

    session = requests.Session()
    session.headers.update(HEADERS)
    return session


SESSION = create_session()


def fetch_html(url):
    if not url:
        return ""

    response = SESSION.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def fetch_soup(url):
    return BeautifulSoup(fetch_html(url), "html.parser")


def meta_content(soup, *, name="", prop=""):
    attrs = {}
    if name:
        attrs["name"] = name
    if prop:
        attrs["property"] = prop
    tag = soup.find("meta", attrs=attrs)
    if not tag:
        return ""
    return clean_text(tag.get("content", ""))


def load_json_ld(soup):
    blocks = []
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = tag.string or tag.get_text()
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, list):
            blocks.extend(item for item in parsed if isinstance(item, dict))
        elif isinstance(parsed, dict):
            blocks.append(parsed)
    return blocks


def find_json_ld(blocks, wanted_type):
    for block in blocks:
        if block.get("@type") == wanted_type:
            return block
    return {}


def collect_link_names(soup, pattern):
    values = []
    seen = set()
    for link in soup.select(f"a[href*='{pattern}']"):
        href = absolute_url(link.get("href", ""))
        text = clean_text(link.get_text(" ", strip=True))
        if not href or not text:
            continue
        if text.casefold() in GENERIC_TAG_NAMES:
            continue
        key = (href.casefold(), text.casefold())
        if key in seen:
            continue
        seen.add(key)
        values.append(text)
    return values


def extract_scene_info(soup):
    info = soup.select_one(".info")
    if not info:
        return ""
    return clean_text(info.get_text(" ", strip=True))


def extract_scene_date(soup, video_json):
    date = parse_iso_date(video_json.get("uploadDate", ""))
    if date:
        return date

    date = parse_iso_date(meta_content(soup, prop="ya:ovs:upload_date"))
    if date:
        return date

    match = re.search(r"Submitted:\s*([^|]+)$", extract_scene_info(soup), flags=re.IGNORECASE)
    if not match:
        return ""
    return parse_relative_date(match.group(1))


def scene_from_search_item(item):
    link = item.select_one("a[href*='/video/']")
    if not link:
        return {}

    url = absolute_url(link.get("href", ""))
    title = clean_text(link.get("title", ""))
    title_node = item.select_one("strong.title")
    if not title and title_node:
        title = clean_text(title_node.get_text(" ", strip=True))

    image = ""
    image_node = item.select_one("img")
    if image_node:
        image = image_node.get("data-original") or image_node.get("src") or ""
        image = absolute_url(image)
        if image.startswith("data:image"):
            image = ""

    date = ""
    added = item.select_one(".added em")
    if added:
        date = parse_relative_date(added.get_text(" ", strip=True))

    if not title or not url:
        return {}

    scene = {
        "title": title,
        "url": url,
        "image": image,
        "date": date,
    }
    return {key: value for key, value in scene.items() if value}


def scrape_scene(url):
    url = absolute_url(url)
    if not url:
        return {}

    soup = fetch_soup(url)
    video_json = find_json_ld(load_json_ld(soup), "VideoObject")

    title = clean_text(video_json.get("name", ""))
    if not title and soup.find("h1"):
        title = clean_text(soup.find("h1").get_text(" ", strip=True))
    if not title and soup.title:
        title = clean_text(soup.title.get_text(" ", strip=True))

    details = clean_text(video_json.get("description", ""))
    if not details:
        details = meta_content(soup, prop="og:description") or meta_content(
            soup, name="description"
        )

    image = absolute_url(video_json.get("thumbnailUrl", ""))
    if not image:
        image = absolute_url(meta_content(soup, prop="og:image"))

    categories = collect_link_names(soup, "/categories/")
    tags = collect_link_names(soup, "/tags/")
    performers = collect_link_names(soup, "/models/")
    studios = collect_link_names(soup, "/sites/")
    studio_name = studios[0] if studios else SITE_STUDIO

    scene = {
        "title": title,
        "url": url,
        "date": extract_scene_date(soup, video_json),
        "details": details,
        "image": image,
        "studio": {"name": studio_name},
        "performers": unique_named_items(performers),
        "tags": unique_named_items(categories + tags),
        "code": clean_text(video_json.get("embedUrl", "").rstrip("/").split("/")[-1]),
    }
    return {key: value for key, value in scene.items() if value not in ("", [], {}, None)}


def search_scenes(query):
    query = normalize_space(query)
    if not query:
        return []

    soup = fetch_soup(SEARCH_URL.format(query=quote_plus(query)))
    results = []
    seen = set()
    for item in soup.select(".list-videos .item"):
        result = scene_from_search_item(item)
        if not result:
            continue
        key = result["url"].casefold()
        if key in seen:
            continue
        seen.add(key)
        results.append(result)

    results.sort(
        key=lambda item: (
            normalize_title(item.get("title", "")) != normalize_title(query),
            -token_overlap_score(item.get("title", ""), query),
            -similarity(item.get("title", ""), query),
            item.get("title", "").casefold(),
        )
    )
    return results


def get_args(request):
    return request.get("args") or {}


def get_request_value(request, key):
    args = get_args(request)
    if key in request and request.get(key) not in (None, ""):
        return request.get(key)
    if key in args and args.get(key) not in (None, ""):
        return args.get(key)
    return request.get("input", {}).get(key, "")


def wrap_scene_result(scene):
    return {"results": [scene]} if scene else {"results": []}


def wrap_search_results(results):
    payload = []
    for result in results:
        cleaned = {key: value for key, value in result.items() if value not in ("", [], {}, None)}
        if cleaned:
            payload.append(cleaned)
    return {"results": payload}


def main():
    request = read_request()
    mode = request.get("mode", "")

    if mode == "sceneByURL":
        emit(wrap_scene_result(scrape_scene(get_request_value(request, "url"))))
        return

    if mode == "sceneByName":
        emit(wrap_search_results(search_scenes(get_request_value(request, "name"))))
        return

    emit({"results": []})


if __name__ == "__main__":
    main()
