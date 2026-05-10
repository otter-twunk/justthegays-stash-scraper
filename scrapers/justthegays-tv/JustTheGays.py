#!/usr/bin/env python3

import json
import re
import subprocess
import sys
from datetime import datetime
from difflib import SequenceMatcher
from html import unescape
import ssl
from urllib.parse import quote_plus
from urllib.error import URLError
from urllib.request import Request, urlopen


BASE_URL = "https://justthegays.tv"
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


def load_json_ld_blocks(html):
    blocks = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>\s*(.*?)\s*</script>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    parsed = []
    for block in blocks:
        text = unescape(block).strip()
        if not text:
            continue
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(value, list):
            parsed.extend(item for item in value if isinstance(item, dict))
        elif isinstance(value, dict):
            parsed.append(value)
    return parsed


def find_json_ld(blocks, wanted_type):
    for block in blocks:
        if block.get("@type") == wanted_type:
            return block
    return None


def normalize_space(value):
    return re.sub(r"\s+", " ", value or "").strip()


def clean_details(value):
    text = normalize_space(unescape(value))
    if not text:
        return ""
    text = re.sub(r"^Stream '.*?' and more hot .*?$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^Browse \d+ .*?$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+Find it here on JustTheGays.*$", "", text, flags=re.IGNORECASE)
    text = re.sub(
        r"\s+This video has plenty of amazing .*? action that will get you excited\.?",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\s+Stream '.*?' and more hot .*?$", "", text, flags=re.IGNORECASE)
    return normalize_space(text)


def strip_html(value):
    text = re.sub(r"<[^>]+>", " ", value or "")
    return normalize_space(unescape(text))


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


def similarity(a, b):
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def parse_date(iso_value):
    if not iso_value:
        return ""
    try:
        return datetime.fromisoformat(iso_value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return iso_value.split("T", 1)[0]


def extract_category_names(html):
    names = re.findall(
        r'href="/\d+/category/[^"]+"[^>]*>(.*?)</a>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return unique_names(strip_html(name) for name in names)


def extract_performer_names_from_html(html):
    names = re.findall(
        r'href="/performer/[^"]+"[^>]*>(.*?)</a>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return unique_names(strip_html(name) for name in names)


def scrape_scene(url):
    html = fetch(url)
    blocks = load_json_ld_blocks(html)
    video = find_json_ld(blocks, "VideoObject")
    if not video:
        return {}

    actors = []
    for actor in video.get("actor", []):
        if isinstance(actor, dict):
            actors.append(actor.get("name", ""))
        elif isinstance(actor, str):
            actors.append(actor)

    performers = unique_names(actors)
    if not performers:
        performers = extract_performer_names_from_html(html)

    image = video.get("thumbnailUrl")
    if isinstance(image, list):
        image = image[0] if image else ""

    scene = {
        "title": normalize_space(video.get("name", "")),
        "url": url,
        "date": parse_date(video.get("uploadDate", "")),
        "details": clean_details(video.get("description", "")),
        "image": image or "",
        "performers": performers,
        "tags": extract_category_names(html),
    }
    return {key: value for key, value in scene.items() if value}


def parse_search_results(html):
    blocks = load_json_ld_blocks(html)
    page = find_json_ld(blocks, "SearchResultsPage")
    if not page:
        return []

    item_list = page.get("mainEntity", {}).get("itemListElement", [])
    results = []
    for entry in item_list:
        item = entry.get("item", {})
        title = normalize_space(item.get("name", ""))
        url = item.get("url", "")
        if not title or title.casefold() == "null" or not url or "/video/" not in url:
            continue
        if not title or not url:
            continue
        thumb = item.get("thumbnailUrl", "")
        if thumb and not thumb.startswith("http"):
            thumb = f"https://static.jtg.network/thumbnails/{thumb.lstrip('/')}"
        results.append(
            {
                "title": title,
                "url": url,
                "date": parse_date(item.get("uploadDate", "")),
                "details": clean_details(item.get("description", "")),
                "image": thumb,
            }
        )
    return results


def search_scenes(query):
    query = normalize_space(query)
    if not query:
        return []
    url = f"{BASE_URL}/search?q={quote_plus(query)}"
    html = fetch(url)
    results = parse_search_results(html)
    results.sort(
        key=lambda item: (
            normalize_title(item["title"]) != normalize_title(query),
            -similarity(item["title"], query),
            item.get("title", ""),
        )
    )
    return results


def best_scene_match(query):
    results = search_scenes(query)
    if not results:
        return {}
    best = results[0]
    exact = normalize_title(best["title"]) == normalize_title(query)
    if not exact and similarity(best["title"], query) < 0.55:
        return {}
    return scrape_scene(best["url"])


def performer_details_from_person_json(person):
    performer = {
        "name": normalize_space(person.get("name", "")),
        "url": person.get("url", ""),
        "gender": normalize_space(person.get("gender", "")),
        "image": person.get("image", ""),
        "details": clean_details(person.get("description", "")),
    }
    return {key: value for key, value in performer.items() if value}


def scrape_performer(url):
    html = fetch(url)
    blocks = load_json_ld_blocks(html)
    person = find_json_ld(blocks, "Person")
    if person:
        return performer_details_from_person_json(person)

    title_match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    name = ""
    if title_match:
        name = normalize_space(strip_html(title_match.group(1)).split(" videos - ")[0])
    image_match = re.search(
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
        html,
        flags=re.IGNORECASE,
    )
    performer = {
        "name": name,
        "url": url,
        "gender": "Male",
        "image": image_match.group(1) if image_match else "",
    }
    return {key: value for key, value in performer.items() if value}


def extract_fragment_query(fragment):
    if isinstance(fragment, dict):
        direct = fragment.get("title") or fragment.get("name") or fragment.get("code")
        if direct:
            return direct
        url = fragment.get("url", "")
        if "justthegays.tv/video/" in url:
            return url
        for file_info in fragment.get("files", []):
            basename = file_info.get("basename") or file_info.get("path") or ""
            if basename:
                return basename
    elif isinstance(fragment, str):
        return fragment
    return ""


def handle_scene_by_fragment(fragment):
    query = extract_fragment_query(fragment)
    if not query:
        return {}
    if isinstance(query, str) and "justthegays.tv/video/" in query:
        return scrape_scene(query)
    return best_scene_match(query)


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
