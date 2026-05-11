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


BASE_URL = "https://gayforfans.com"
SEARCH_URL = BASE_URL + "/?s={query}"
STUDIO = "GayForFans"
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
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": BASE_URL + "/",
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
                "-H",
                "Accept: text/html,application/xhtml+xml",
                "-H",
                "Accept-Language: en-US,en;q=0.9",
                "-H",
                f"Referer: {BASE_URL}/",
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


def parse_date(value):
    if not value:
        return ""
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return str(value).split("T", 1)[0]


def extract_meta_content(html, key):
    match = re.search(
        rf'<meta[^>]+(?:property|name)=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)',
        html,
        flags=re.IGNORECASE,
    )
    return html_unescape(match.group(1)) if match else ""


def extract_html_title(html):
    match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    return strip_html(match.group(1)) if match else ""


def load_json_ld_blocks(html):
    blocks = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>\s*(.*?)\s*</script>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    parsed = []
    for block in blocks:
        # Keep the raw JSON string intact; HTML-unescaping first can corrupt quoted
        # strings embedded inside JSON values such as `&quot;...&quot;`.
        text = block.strip()
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
        graph = block.get("@graph", [])
        if isinstance(graph, list):
            for item in graph:
                if isinstance(item, dict) and item.get("@type") == wanted_type:
                    return item
    return None


def split_keywords(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [part.strip() for part in value.split(",")]
    return []


def normalize_title(value):
    value = unescape(value or "")
    value = value.lower()
    value = re.sub(r"\.[a-z0-9]{2,5}$", "", value)
    value = re.sub(r"-\d{8,}$", "", value)
    value = re.sub(r"\b(2160p|1080p|720p|480p|x264|x265|hevc|h264|h265)\b", " ", value)
    value = re.sub(r"[_./-]+", " ", value)
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    return normalize_space(value)


def similarity(a, b):
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def clean_scene_description(value):
    text = html_unescape(value)
    if not text:
        return ""
    text = re.sub(r"\s+on GayForFans\.com$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+only on GayForFans.*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+Your new favorite video is just a click away\.\s*$", "", text, flags=re.IGNORECASE)
    return normalize_space(text)


def clean_performer_description(value):
    text = html_unescape(value)
    if not text:
        return ""
    text = re.sub(r"\s+on GayForFans\..*$", "", text, flags=re.IGNORECASE)
    return normalize_space(text)


def extract_category_tags(html):
    names = re.findall(
        r'<a[^>]+href=["\']https://gayforfans\.com/categories/[^"\']+["\'][^>]*rel=["\']tag["\'][^>]*>(.*?)</a>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return [strip_html(name) for name in names]


def extract_performer_links(html):
    names = re.findall(
        r'<a[^>]+href=["\']https://gayforfans\.com/performer/[^"\']+["\'][^>]*>(.*?)</a>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return [strip_html(name) for name in names]


def scrape_scene(url):
    if not url:
        return {}

    try:
        html = fetch(url)
    except Exception:
        return {}

    blocks = load_json_ld_blocks(html)
    video = find_json_ld(blocks, "VideoObject")
    if not video:
        return {}

    actors = video.get("actor", [])
    if isinstance(actors, dict):
        actors = [actors]
    performer_names = []
    for actor in actors:
        if isinstance(actor, dict):
            performer_names.append(html_unescape(actor.get("name", "")))
        elif isinstance(actor, str):
            performer_names.append(html_unescape(actor))
    performers = unique_names(performer_names) or unique_names(extract_performer_links(html))

    keywords = [html_unescape(item) for item in split_keywords(video.get("keywords", []))]
    tags = unique_names(item for item in keywords if item.casefold() != "video")
    if not tags:
        tags = unique_names(item for item in extract_category_tags(html) if item.casefold() != "video")

    image = video.get("thumbnailUrl", "")
    if isinstance(image, list):
        image = image[0] if image else ""

    title = html_unescape(video.get("name", ""))
    if not title:
        title = extract_meta_content(html, "og:title")
    if not title:
        title = re.sub(
            r"\s*-\s*Watch gay porn for free on GayForFans\.com$",
            "",
            extract_html_title(html),
            flags=re.IGNORECASE,
        )

    description = clean_scene_description(video.get("description", ""))
    if not description:
        description = extract_meta_content(html, "description")

    scene = {
        "title": title,
        "url": url,
        "date": parse_date(video.get("uploadDate", "")),
        "details": description,
        "image": image or "",
        "studio": {"name": STUDIO},
        "performers": performers,
        "tags": tags,
    }
    return {key: value for key, value in scene.items() if value}


def parse_search_results(html):
    pattern = re.compile(
        r'<article class="([^"]*?\bvideo\b[^"]*)".*?'
        r'<a href="(https://gayforfans\.com/video/[^"]+)">\s*'
        r'<img[^>]+src="([^"]+)".*?'
        r'<h3 class="post-title[^"]*"><a href="[^"]+">(.*?)</a></h3>.*?'
        r'<div class="meta"><span class="date">(.*?)</span>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    results = []
    seen = set()
    for article_classes, url, image, title_html, relative_date in pattern.findall(html):
        if url in seen:
            continue
        seen.add(url)
        category_slugs = re.findall(
            r"\bcategories-([a-z0-9_-]+)\b",
            article_classes,
            flags=re.IGNORECASE,
        )
        performer_slugs = re.findall(
            r"\bvideo_tag-([a-z0-9_-]+)\b",
            article_classes,
            flags=re.IGNORECASE,
        )
        results.append(
            {
                "title": strip_html(title_html),
                "url": url,
                "image": image,
                "date_hint": strip_html(relative_date),
                "category_slugs": category_slugs,
                "performer_slugs": performer_slugs,
            }
        )
    return results


def search_scenes(query):
    query = normalize_space(query)
    if not query:
        return []

    try:
        html = fetch(SEARCH_URL.format(query=quote_plus(query)))
    except Exception:
        return []

    results = parse_search_results(html)
    results.sort(
        key=lambda item: (
            normalize_title(item["title"]) != normalize_title(query),
            -similarity(item["title"], query),
            item["title"],
        )
    )
    return [{"title": item["title"], "url": item["url"]} for item in results]


def extract_fragment_query(data):
    if isinstance(data, str):
        return normalize_space(data)
    if not isinstance(data, dict):
        return ""

    direct = (
        data.get("title")
        or data.get("name")
        or data.get("query")
        or data.get("filename")
        or data.get("basename")
        or data.get("code")
    )
    if direct:
        return normalize_space(direct)

    url = data.get("url", "")
    if "/video/" in url:
        return url

    for file_info in data.get("files", []):
        basename = file_info.get("basename") or file_info.get("path") or ""
        if basename:
            return normalize_space(basename)
    return ""


def candidate_queries(query):
    normalized = normalize_space(query)
    if not normalized:
        return []
    candidates = [normalized]
    cleaned = normalize_title(normalized)
    if cleaned and cleaned != normalized:
        candidates.append(cleaned)
    slugless = re.sub(r"\b\d{8,}\b", " ", cleaned)
    slugless = normalize_space(slugless)
    if slugless and slugless not in candidates:
        candidates.append(slugless)
    seen = set()
    ordered = []
    for item in candidates:
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(item)
    return ordered


def best_scene_match(query):
    if not query:
        return {}
    if "/video/" in query:
        return scrape_scene(query)

    for candidate in candidate_queries(query):
        results = search_scenes(candidate)
        if not results:
            continue
        best = results[0]
        score = similarity(best["title"], candidate)
        exact = normalize_title(best["title"]) == normalize_title(candidate)
        if exact or score >= 0.55:
            return scrape_scene(best["url"])
    return {}


def scrape_performer(url):
    if not url:
        return {}

    try:
        html = fetch(url)
    except Exception:
        return {}

    blocks = load_json_ld_blocks(html)
    person = find_json_ld(blocks, "Person")

    name = ""
    description = ""
    image = ""
    if person:
        name = html_unescape(person.get("name", ""))
        description = clean_performer_description(person.get("description", ""))
        image = person.get("image", "") or ""

    if not name:
        heading = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.IGNORECASE | re.DOTALL)
        name = strip_html(heading.group(1)) if heading else ""
    if not name:
        name = re.sub(r"\s+Porn\s+-\s+GayForFans.*$", "", extract_html_title(html), flags=re.IGNORECASE)

    if not description:
        description = extract_meta_content(html, "description")
    if not image:
        image = extract_meta_content(html, "og:image")
    if not image:
        img_match = re.search(
            r'<img[^>]+src=["\'](https://images\.mstatic\.co/[^"\']+)["\']',
            html,
            flags=re.IGNORECASE,
        )
        image = img_match.group(1) if img_match else ""

    performer = {
        "name": name,
        "url": url,
        "gender": "Male",
        "image": image,
        "details": description,
    }
    return {key: value for key, value in performer.items() if value}


def handle_scene_by_fragment(fragment):
    query = extract_fragment_query(fragment)
    if not query:
        return {}
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
