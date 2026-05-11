#!/usr/bin/env python3

import json
import re
import subprocess
import sys
from datetime import datetime
from difflib import SequenceMatcher
from html import unescape
from urllib.parse import quote_plus, urljoin


BASE_URL = "https://gayporn.com"
SEARCH_URL = f"{BASE_URL}/search?query={{query}}"
STUDIO = "GayPorn.com"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) "
    "Gecko/20100101 Firefox/115.0"
)
SCENE_URL_RE = re.compile(r"^https?://(?:www\.)?gayporn\.com/video/[^/?#]+/?$", re.IGNORECASE)
PERFORMER_URL_RE = re.compile(r"^https?://(?:www\.)?gayporn\.com/pornstars/[^/?#]+/?$", re.IGNORECASE)
TITLE_SUFFIX_RE = re.compile(r"\s*\|\s*GayPorn\.com\s*$", re.IGNORECASE)
ARTICLE_RE = re.compile(r"<article\b.*?</article>", re.IGNORECASE | re.DOTALL)


def read_stdin():
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    return json.loads(raw)


def fetch(url):
    result = subprocess.run(
        [
            "curl",
            "-L",
            "--silent",
            "--show-error",
            "--fail",
            "-A",
            USER_AGENT,
            "-H",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "-H",
            "Accept-Language: en-US,en;q=0.5",
            url,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def normalize_space(value):
    return re.sub(r"\s+", " ", value or "").strip()


def clean_text(value):
    return normalize_space(unescape(value or ""))


def strip_html(value):
    value = re.sub(r"<!--.*?-->", " ", value or "", flags=re.DOTALL)
    value = re.sub(r"<[^>]+>", " ", value)
    return clean_text(value)


def normalize_url(url):
    if not url:
        return ""
    normalized = urljoin(f"{BASE_URL}/", url)
    return normalized.replace("http://", "https://", 1).replace("https://www.gayporn.com", BASE_URL, 1)


def strip_site_suffix(title):
    return TITLE_SUFFIX_RE.sub("", clean_text(title))


def normalize_title(value):
    value = strip_site_suffix(value).lower()
    value = re.sub(r"\.[a-z0-9]{2,5}$", "", value)
    value = re.sub(r"^\d+\s*[-_. ]\s*", "", value)
    value = re.sub(r"[_./-]+", " ", value)
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    return normalize_space(value)


def similarity(a, b):
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def unique_strings(values):
    seen = set()
    output = []
    for value in values:
        cleaned = clean_text(value)
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key in seen:
            continue
        seen.add(key)
        output.append(cleaned)
    return output


def unique_names(values):
    return [{"name": value} for value in unique_strings(values)]


def extract_meta(html, attr, key):
    pattern = rf'<meta[^>]+{attr}=(["\']){re.escape(key)}\1[^>]+content=(["\'])(.*?)\2'
    match = re.search(pattern, html, flags=re.IGNORECASE)
    return clean_text(match.group(3)) if match else ""


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
            graph = value.get("@graph")
            if isinstance(graph, list):
                parsed.extend(item for item in graph if isinstance(item, dict))
            parsed.append(value)
    return parsed


def find_json_ld(blocks, wanted_type):
    for block in blocks:
        block_type = block.get("@type")
        if block_type == wanted_type:
            return block
        if isinstance(block_type, list) and wanted_type in block_type:
            return block
    return {}


def parse_date(value):
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return value.split("T", 1)[0]


def find_title(html):
    og_title = extract_meta(html, "property", "og:title")
    if og_title:
        return strip_site_suffix(og_title)

    match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return strip_site_suffix(match.group(1))

    match = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.IGNORECASE | re.DOTALL)
    return strip_html(match.group(1)) if match else ""


def split_keywords(value):
    return unique_strings(re.split(r"\s*,\s*", value or ""))


def scene_from_video_object(video_object, url):
    title = clean_text(video_object.get("name"))
    author = video_object.get("author")
    if isinstance(author, dict):
        studio_name = clean_text(author.get("name"))
    else:
        studio_name = clean_text(author)
    studio_name = studio_name or STUDIO

    tag_values = []
    genre = video_object.get("genre")
    if isinstance(genre, list):
        tag_values.extend(genre)
    elif isinstance(genre, str):
        tag_values.extend(split_keywords(genre))
    tag_values.extend(split_keywords(video_object.get("keywords", "")))
    tag_values = [tag for tag in unique_strings(tag_values) if tag.casefold() != studio_name.casefold()]

    scene = {
        "title": title,
        "date": parse_date(video_object.get("uploadDate", "")),
        "details": clean_text(video_object.get("description", "")),
        "image": clean_text(video_object.get("thumbnailUrl", "")),
        "url": url,
        "tags": unique_names(tag_values),
        "studio": {"name": studio_name},
    }
    return {key: value for key, value in scene.items() if value not in ("", [], None)}


def scrape_scene(url):
    url = normalize_url(url)
    if not SCENE_URL_RE.match(url):
        return {}

    try:
        html = fetch(url)
    except Exception:
        return {}

    blocks = load_json_ld_blocks(html)
    video_object = find_json_ld(blocks, "VideoObject")
    scene = scene_from_video_object(video_object, url) if video_object else {"url": url}

    if "title" not in scene:
        title = find_title(html)
        if title:
            scene["title"] = title
    if "details" not in scene:
        details = extract_meta(html, "name", "description")
        if details:
            scene["details"] = details
    if "image" not in scene:
        image = extract_meta(html, "property", "og:image")
        if image:
            scene["image"] = image
    if "studio" not in scene:
        scene["studio"] = {"name": STUDIO}
    return scene


def parse_search_results(html):
    results = []
    seen = set()

    for article in ARTICLE_RE.findall(html):
        title_match = re.search(r"<h2[^>]*>(.*?)</h2>", article, flags=re.IGNORECASE | re.DOTALL)
        href_match = re.search(r'href=["\'](/video/[^"\']+)["\']', article, flags=re.IGNORECASE)
        if not title_match or not href_match:
            continue

        title = strip_html(title_match.group(1))
        url = normalize_url(href_match.group(1))
        image_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\'][^>]+alt=["\']([^"\']+)["\']', article, flags=re.IGNORECASE)
        if not image_match:
            image_match = re.search(r'<img[^>]+alt=["\']([^"\']+)["\'][^>]+src=["\']([^"\']+)["\']', article, flags=re.IGNORECASE)
            image = clean_text(image_match.group(2)) if image_match else ""
        else:
            image = clean_text(image_match.group(1))

        if not title or url in seen:
            continue
        seen.add(url)

        item = {"title": title, "url": url}
        if image:
            item["image"] = image
        results.append(item)

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
    results.sort(key=lambda item: similarity(item.get("title", ""), query), reverse=True)
    return results


def simplify_search_query(value):
    value = clean_text(value)
    value = value.rsplit("/", 1)[-1]
    value = re.sub(r"\.[a-z0-9]{2,5}$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"[_./-]+", " ", value)
    return normalize_space(value)


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
        or data.get("code")
    )
    if direct:
        return simplify_search_query(direct)

    url = data.get("url", "")
    if "/video/" in url:
        return normalize_url(url)

    for file_info in data.get("files", []):
        basename = file_info.get("basename") or file_info.get("path") or ""
        if basename:
            return simplify_search_query(basename)
    return ""


def best_scene_match(query):
    if "/video/" in query:
        return scrape_scene(query)

    results = search_scenes(query)
    if not results:
        return {}

    best = results[0]
    exact = normalize_title(best["title"]) == normalize_title(query)
    if not exact and similarity(best["title"], query) < 0.55:
        return {}
    return scrape_scene(best["url"])


def extract_performer_name(html, url):
    blocks = load_json_ld_blocks(html)
    profile_page = find_json_ld(blocks, "ProfilePage")
    main_entity = profile_page.get("mainEntity", {}) if isinstance(profile_page, dict) else {}
    about = profile_page.get("about", {}) if isinstance(profile_page, dict) else {}

    for candidate in (main_entity.get("name"), about.get("name")):
        cleaned = clean_text(candidate)
        if cleaned:
            return cleaned

    match = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.IGNORECASE | re.DOTALL)
    if match:
        name = strip_html(match.group(1))
        name = re.sub(r"\s+Gay Pornstar Videos\s*$", "", name, flags=re.IGNORECASE)
        if name:
            return name

    slug = url.rstrip("/").rsplit("/", 1)[-1]
    return clean_text(slug.replace("-", " ").title())


def extract_avatar(html, name):
    escaped = re.escape(name)
    patterns = [
        rf'<img[^>]+alt=["\']{escaped} avatar["\'][^>]+src=["\']([^"\']+)["\']',
        rf'<img[^>]+src=["\']([^"\']+)["\'][^>]+alt=["\']{escaped} avatar["\']',
        rf'<img[^>]+alt=["\']{escaped}["\'][^>]+src=["\']([^"\']+)["\']',
        rf'<img[^>]+src=["\']([^"\']+)["\'][^>]+alt=["\']{escaped}["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.IGNORECASE)
        if match:
            return clean_text(match.group(1))

    og_image = extract_meta(html, "property", "og:image")
    if og_image.startswith("http"):
        return og_image
    return ""


def scrape_performer(url):
    url = normalize_url(url)
    if not PERFORMER_URL_RE.match(url):
        return {}

    try:
        html = fetch(url)
    except Exception:
        return {}

    name = extract_performer_name(html, url)
    details = extract_meta(html, "name", "description")
    performer = {
        "name": name,
        "url": url,
        "image": extract_avatar(html, name),
        "details": details,
    }
    return {key: value for key, value in performer.items() if value not in ("", [], None)}


def scene_by_url():
    inp = read_stdin()
    print(json.dumps(scrape_scene(inp.get("url", "")), ensure_ascii=False))


def scene_by_name():
    inp = read_stdin()
    print(json.dumps(search_scenes(inp.get("name", "")), ensure_ascii=False))


def scene_by_query_fragment():
    inp = read_stdin()
    query = extract_fragment_query(inp)
    if "/video/" in query:
        scene = scrape_scene(query)
        print(json.dumps([scene] if scene else [], ensure_ascii=False))
        return
    print(json.dumps(search_scenes(query), ensure_ascii=False))


def scene_by_fragment():
    inp = read_stdin()
    query = extract_fragment_query(inp)
    if not query:
        print(json.dumps({}, ensure_ascii=False))
        return
    print(json.dumps(best_scene_match(query), ensure_ascii=False))


def performer_by_url():
    inp = read_stdin()
    print(json.dumps(scrape_performer(inp.get("url", "")), ensure_ascii=False))


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
