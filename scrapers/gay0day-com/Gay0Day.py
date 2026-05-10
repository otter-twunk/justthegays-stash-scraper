#!/usr/bin/env python3
import json
import re
import sys
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from html import unescape
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://gay0day.com"
SEARCH_URL = "https://gay0day.com/search/?q={query}"
STUDIO = "Gay0Day"
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


def strip_html(value: str) -> str:
    return clean_text(re.sub(r"<[^>]+>", " ", value or ""))


def normalize_title(value: str) -> str:
    value = unescape(value or "").lower()
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


def clean_scene_details(value: str) -> str:
    text = clean_text(value)
    if not text:
        return ""
    return normalize_space(text)


def clean_performer_details(value: str) -> str:
    text = clean_text(value)
    if not text:
        return ""
    text = re.sub(r"\s+Watch only the best gay porn videos.*$", "", text, flags=re.IGNORECASE)
    return normalize_space(text)


def parse_iso_date(value: str) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return value.split("T", 1)[0]


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


def load_json_ld(soup: BeautifulSoup) -> list:
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


def find_json_ld(blocks: list, wanted_type: str) -> dict:
    for block in blocks:
        if block.get("@type") == wanted_type:
            return block
    return {}


def parse_relative_date(text: str) -> str:
    text = clean_text(text).lower()
    if not text:
        return ""

    if text in {"today", "just now"}:
        return datetime.utcnow().date().isoformat()
    if text == "yesterday":
        return (datetime.utcnow().date() - timedelta(days=1)).isoformat()

    match = re.search(r"(\d+)\s+(year|month|week|day|hour|minute)s?\s+ago", text)
    if not match:
        return ""

    amount = int(match.group(1))
    unit = match.group(2)
    now = datetime.utcnow()

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


def extract_scene_info_block(soup: BeautifulSoup) -> BeautifulSoup:
    return soup.select_one("#tab_video_info .block-details .info") or soup


def extract_scene_date(soup: BeautifulSoup, video_json: dict) -> str:
    date = parse_iso_date(video_json.get("uploadDate", ""))
    if date:
        return date

    info_block = extract_scene_info_block(soup)
    text = clean_text(info_block.get_text(" ", strip=True))
    match = re.search(r"Submitted:\s*([A-Za-z0-9 ]+?ago|today|yesterday)\b", text, flags=re.IGNORECASE)
    if match:
        return parse_relative_date(match.group(1))
    return ""


def extract_scene_details(soup: BeautifulSoup, video_json: dict) -> str:
    candidates = [
        video_json.get("description", ""),
        meta_content(soup, name="description"),
        meta_content(soup, prop="og:description"),
    ]
    info_block = extract_scene_info_block(soup)
    detail_row = info_block.select_one(".item em")
    if detail_row:
        candidates.append(detail_row.get_text(" ", strip=True))

    for candidate in candidates:
        cleaned = clean_scene_details(candidate)
        if cleaned:
            return cleaned
    return ""


def scene_from_search_item(item) -> dict:
    link = item.select_one("a[href*='/videos/']")
    if not link:
        return {}

    url = link.get("href", "").strip()
    title = clean_text(link.get("title") or "")
    title_node = item.select_one("strong.title")
    if not title and title_node:
        title = clean_text(title_node.get_text(" ", strip=True))

    img = item.select_one("img")
    image = ""
    if img:
        image = img.get("data-original") or img.get("src") or ""
        image = image.strip()
        if image.startswith("data:image"):
            image = ""

    if not title or not url:
        return {}

    return {
        "title": title,
        "url": url,
        "image": image,
    }


def scrape_scene(url: str) -> dict:
    if not url:
        return {}

    soup = fetch(url)
    video_json = find_json_ld(load_json_ld(soup), "VideoObject")

    title = ""
    title = clean_text(video_json.get("name", ""))
    if not title and soup.find("h1"):
        title = clean_text(soup.find("h1").get_text(" ", strip=True))
    if not title:
        title = clean_text(soup.title.get_text()) if soup.title else ""

    image = clean_text(video_json.get("thumbnailUrl", "")) or meta_content(soup, prop="og:image")
    if not image:
        preview = soup.find("link", attrs={"rel": "preload", "as": "image"})
        if preview:
            image = clean_text(preview.get("href", ""))

    performer_links = [a.get_text(" ", strip=True) for a in soup.select("#tab_video_info a[href*='/models/']")]
    tag_links = [a.get_text(" ", strip=True) for a in soup.select("#tab_video_info a[href*='/tags/']")]
    category_links = [a.get_text(" ", strip=True) for a in soup.select("#tab_video_info a[href*='/categories/']")]

    scene = {
        "title": title,
        "url": url,
        "date": extract_scene_date(soup, video_json),
        "details": extract_scene_details(soup, video_json),
        "image": image,
        "studio": {"name": STUDIO},
        "performers": unique_names(performer_links),
        "tags": unique_names(tag_links + category_links),
    }
    return {key: value for key, value in scene.items() if value}


def scrape_performer(url: str) -> dict:
    if not url:
        return {}

    soup = fetch(url)

    name = ""
    headline = soup.select_one(".headline h2")
    if headline:
        name = clean_text(headline.get_text(" ", strip=True))
        name = re.sub(r"^Gay actors?\s+", "", name, flags=re.IGNORECASE)
    if not name and soup.title:
        name = clean_text(soup.title.get_text())
        name = re.sub(r"'s Gay porn model$", "", name, flags=re.IGNORECASE)

    image = ""
    img = soup.select_one(".block-model img.thumb")
    if img:
        image = clean_text(img.get("src", ""))
    if not image:
        image = meta_content(soup, prop="og:image")

    stats = {}
    for item in soup.select(".model-list li"):
        text = clean_text(item.get_text(" ", strip=True))
        if ":" not in text:
            continue
        key, value = text.split(":", 1)
        value = clean_text(value)
        if value in {"N/A", "0", ""}:
            continue
        stats[key.strip().lower()] = value

    details = ""
    desc = soup.select_one(".block-model .desc")
    if desc:
        details = clean_performer_details(desc.get_text(" ", strip=True))

    performer = {
        "name": name,
        "url": url,
        "gender": "Male",
        "image": image,
        "details": details,
        "country": stats.get("country", ""),
        "height": stats.get("height", ""),
        "weight": stats.get("weight", ""),
        "birthdate": "",
        "ethnicity": "",
        "hair_color": "",
        "eye_color": "",
        "career_length": "",
    }
    return {key: value for key, value in performer.items() if value}


def search_scenes(query: str) -> list:
    query = normalize_space(query)
    if not query:
        return []

    soup = fetch(SEARCH_URL.format(query=quote_plus(query)))
    results = []
    seen = set()
    for item in soup.select(".list-videos .item"):
        result = scene_from_search_item(item)
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
            -similarity(item["title"], query),
            item["title"],
        )
    )
    return results


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
        return url

    for file_info in data.get("files", []):
        basename = file_info.get("basename") or file_info.get("path") or ""
        if basename:
            return normalize_space(basename)
    return ""


def best_scene_match(query: str) -> dict:
    if "/videos/" in query:
        return scrape_scene(query)

    results = search_scenes(query)
    if not results:
        return {}

    best = results[0]
    exact = normalize_title(best["title"]) == normalize_title(query)
    if not exact and similarity(best["title"], query) < 0.55:
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


def performer_by_url():
    inp = read_stdin()
    url = inp.get("url", "")
    result = scrape_performer(url)
    print(json.dumps(result))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    dispatch = {
        "sceneByURL": scene_by_url,
        "sceneByName": scene_by_name,
        "sceneByQueryFragment": scene_by_query_fragment,
        "sceneByFragment": scene_by_fragment,
        "performerByURL": performer_by_url,
    }
    fn = dispatch.get(mode)
    if fn:
        fn()
    else:
        print(json.dumps({"error": f"Unknown mode: {mode}"}), file=sys.stderr)
        sys.exit(1)
