#!/usr/bin/env python3
import json
import re
import sys
from datetime import UTC, datetime, timedelta
from difflib import SequenceMatcher
from html import unescape
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.gayhardfuck.com"
SEARCH_URL = "https://www.gayhardfuck.com/search/?q={query}"
STUDIO = "GayHardFuck"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36"
}


def read_stdin() -> dict:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    return json.loads(raw)


def fetch(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def clean_text(value: str) -> str:
    return normalize_space(unescape(value or ""))


def normalize_url(url: str) -> str:
    if not url:
        return ""
    normalized = urljoin(f"{BASE_URL}/", url)
    return normalized.replace("http://", "https://", 1).replace("https://gayhardfuck.com", BASE_URL, 1)


def normalize_title(value: str) -> str:
    value = clean_text(value).lower()
    value = re.sub(r"\.[a-z0-9]{2,5}$", "", value)
    value = re.sub(r"^\d+\s*[-_. ]\s*", "", value)
    value = re.sub(r"[_./-]+", " ", value)
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    return normalize_space(value)


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def unique_names(values) -> list:
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


def meta_content(soup: BeautifulSoup, *, name: str = "", prop: str = "") -> str:
    attrs = {}
    if name:
        attrs["name"] = name
    if prop:
        attrs["property"] = prop
    tag = soup.find("meta", attrs=attrs)
    if not tag:
        return ""
    return clean_text(tag.get("content", ""))


def strip_site_suffix(title: str) -> str:
    title = clean_text(title)
    return re.sub(r"\s*-\s*GayHardFuck(?:\.com)?\s*$", "", title, flags=re.IGNORECASE)


def parse_relative_date(text: str) -> str:
    text = clean_text(text).lower()
    if not text:
        return ""
    now = datetime.now(UTC)

    if text in {"today", "just now"}:
        return now.date().isoformat()
    if text == "yesterday":
        return (now.date() - timedelta(days=1)).isoformat()

    match = re.search(r"(\d+)\s+(year|month|week|day|hour|minute)s?\s+ago", text)
    if not match:
        return ""

    amount = int(match.group(1))
    unit = match.group(2)
    if unit == "year":
        delta = timedelta(days=amount * 365)
    elif unit == "month":
        delta = timedelta(days=amount * 30)
    elif unit == "week":
        delta = timedelta(weeks=amount)
    elif unit == "day":
        delta = timedelta(days=amount)
    elif unit == "hour":
        delta = timedelta(hours=amount)
    else:
        delta = timedelta(minutes=amount)
    return (now - delta).date().isoformat()


def extract_info_text(soup: BeautifulSoup) -> str:
    info = soup.select_one("#tab_video_info .info") or soup.select_one(".video-info .info")
    if not info:
        return ""
    return clean_text(info.get_text(" ", strip=True))


def extract_description(soup: BeautifulSoup) -> str:
    candidates = [
        meta_content(soup, prop="og:description"),
        meta_content(soup, name="description"),
    ]

    info = soup.select_one("#tab_video_info .info")
    if info:
        detail_item = None
        for item in info.select(".item"):
            text = clean_text(item.get_text(" ", strip=True))
            if text.lower().startswith("description:"):
                detail_item = text
                break
        if detail_item:
            candidates.append(re.sub(r"^Description:\s*", "", detail_item, flags=re.IGNORECASE))

    for candidate in candidates:
        candidate = clean_text(candidate)
        if candidate:
            return candidate
    return ""


def split_description_parts(description: str) -> tuple[str, str]:
    parts = re.split(r"/{3,}", description or "", maxsplit=1)
    tags_part = clean_text(parts[0]) if parts else ""
    trailing = clean_text(parts[1]) if len(parts) > 1 else ""
    return tags_part, trailing


def extract_performer_names(description: str) -> list:
    trailing = clean_text(split_description_parts(description)[1])
    candidates = []

    if trailing:
        model_match = re.search(r"\bModels?\s+(.+?)(?:\.\s|$)", trailing, flags=re.IGNORECASE)
        if model_match:
            candidates.extend(re.split(r",|/|&|\band\b", model_match.group(1)))
        elif trailing.startswith("(") and ")" in trailing:
            inside = trailing[1:trailing.find(")")]
            candidates.extend(re.split(r",|/|&|\band\b", inside))

    performers = []
    for name in candidates:
        cleaned = clean_text(name)
        cleaned = re.sub(r"^(models?|director|studios?)\s+", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"[.()]$", "", cleaned)
        if not cleaned:
            continue
        if len(cleaned) < 3:
            continue
        if cleaned.lower().startswith("studio "):
            continue
        performers.append(cleaned)
    return performers


def extract_tag_names(description: str) -> list:
    tag_text = split_description_parts(description)[0]
    if not tag_text:
        return []
    if any(mark in tag_text for mark in ['"', "“", "”"]):
        return []
    if tag_text.count(",") < 2:
        return []
    if re.search(r"[.!?]\s+[A-Z]", tag_text):
        return []

    tags = []
    for part in tag_text.split(","):
        cleaned = clean_text(part)
        cleaned = re.sub(r"^.+?:\s*", "", cleaned)
        cleaned = re.sub(r"^\d{4}\s+", "", cleaned)
        cleaned = re.sub(r"^.*\b(\d{4})\b\s+", "", cleaned)
        cleaned = re.sub(r"\.$", "", cleaned)
        if not cleaned:
            continue
        if len(cleaned) > 32:
            continue
        tags.append(cleaned)
    return tags


def scene_from_search_item(item) -> dict:
    link = item.select_one("a[href*='/videos/']")
    if not link:
        return {}

    url = normalize_url(link.get("href", ""))
    title = clean_text(link.get("title", ""))
    title_node = item.select_one("strong.title")
    if not title and title_node:
        title = clean_text(title_node.get_text(" ", strip=True))

    image = ""
    img = item.select_one("img")
    if img:
        image = img.get("data-original") or img.get("src") or ""
        image = normalize_url(image.strip()) if image else ""
        if image.startswith("data:image"):
            image = ""

    if not title or not url:
        return {}

    return {"title": title, "url": url, "image": image}


def extract_fragment_query(data) -> str:
    if isinstance(data, str):
        return normalize_space(data)
    if not isinstance(data, dict):
        return ""

    direct = data.get("title") or data.get("name") or data.get("filename") or data.get("code")
    if direct:
        return normalize_space(direct)

    url = data.get("url", "")
    if "/videos/" in url:
        return normalize_url(url)

    for file_info in data.get("files", []):
        basename = file_info.get("basename") or file_info.get("path") or ""
        if basename:
            return normalize_space(basename)
    return ""


def scrape_scene(url: str) -> dict:
    url = normalize_url(url)
    if not url:
        return {}

    soup = fetch(url)

    title = strip_site_suffix(meta_content(soup, prop="og:title"))
    if not title and soup.title:
        title = strip_site_suffix(soup.title.get_text(" ", strip=True))
    if not title:
        headline = soup.select_one("h1")
        if headline:
            title = clean_text(headline.get_text(" ", strip=True))

    details = extract_description(soup)

    info_text = extract_info_text(soup)
    date_match = re.search(r"Submitted:\s*([A-Za-z0-9 ]+?ago|today|yesterday|just now)\b", info_text, flags=re.IGNORECASE)
    date = parse_relative_date(date_match.group(1)) if date_match else ""

    image = meta_content(soup, prop="og:image")

    performer_links = [a.get_text(" ", strip=True) for a in soup.select("a[href*='/models/']")]
    tag_links = [a.get_text(" ", strip=True) for a in soup.select("a[href*='/tags/']")]

    performers = unique_names(performer_links or extract_performer_names(details))
    tags = unique_names(tag_links or extract_tag_names(details))

    scene = {
        "title": title,
        "url": url,
        "date": date,
        "details": details,
        "image": image,
        "performers": performers,
        "tags": tags,
        "studio": {"name": STUDIO},
    }
    return {key: value for key, value in scene.items() if value}


def search_scenes(query: str) -> list:
    query = normalize_space(query)
    if not query:
        return []

    soup = fetch(SEARCH_URL.format(query=quote_plus(query)))
    results = []
    seen = set()
    for item in soup.select("div.item"):
        result = scene_from_search_item(item)
        if not result:
            continue
        if "/videos/" not in result["url"]:
            continue
        if result["url"] in seen:
            continue
        seen.add(result["url"])
        results.append(result)

    results.sort(
        key=lambda item: (
            normalize_title(item["title"]) != normalize_title(query),
            -similarity(item["title"], query),
            item["title"],
        )
    )
    return results


def best_scene_match(query: str) -> dict:
    if "/videos/" in query:
        return scrape_scene(query)

    results = search_scenes(query)
    if not results:
        return {}

    best = results[0]
    exact = normalize_title(best["title"]) == normalize_title(query)
    score = similarity(best["title"], query)
    if not exact and score < 0.55:
        return {}

    query_tokens = {token for token in normalize_title(query).split() if len(token) >= 3}
    title_tokens = set(normalize_title(best["title"]).split())
    if query_tokens:
        overlap = len(query_tokens & title_tokens) / len(query_tokens)
        if len(query_tokens) <= 4 and overlap < 1.0:
            return {}
        if len(query_tokens) > 4 and overlap < 0.7:
            return {}
    return scrape_scene(best["url"])


def scene_by_url():
    inp = read_stdin()
    url = inp.get("url", "")
    result = scrape_scene(url)
    print(json.dumps(result))


def scene_by_name():
    inp = read_stdin()
    query = inp.get("name", "")
    results = search_scenes(query)
    print(json.dumps(results))


def scene_by_query_fragment():
    inp = read_stdin()
    query = extract_fragment_query(inp)
    if "/videos/" in query:
        scene = scrape_scene(query)
        print(json.dumps([scene] if scene else []))
        return
    results = search_scenes(query)
    print(json.dumps(results))


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
