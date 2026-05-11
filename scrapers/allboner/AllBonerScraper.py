#!/usr/bin/env python3

import json
import re
import ssl
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen


BASE_URL = "https://www.allboner.com"
SEARCH_URL = f"{BASE_URL}/search/{{query}}/"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/136.0.0.0 Safari/537.36"
)
COOKIE = "age_verified=1; kt_tc=1"
SCENE_URL_RE = re.compile(
    r"^https?://(?:www\.)?allboner\.com/videos/\d+/[^/?#]+/?$",
    re.IGNORECASE,
)
CF_CHALLENGE_RE = re.compile(
    r"(?:cf[-_]challenge|__cf_chl_|Just a moment|Enable JavaScript and cookies to continue)",
    re.IGNORECASE,
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


def emit(payload):
    json.dump(payload, sys.stdout, ensure_ascii=False)


def fetch(url):
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Cookie": COOKIE,
        },
    )
    try:
        with urlopen(request, timeout=30, context=SSL_CONTEXT) as response:
            html = response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        if exc.code == 404:
            return ""
        html = ""
    except URLError:
        html = ""

    if not html:
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
                "Accept-Language: en-US,en;q=0.9",
                "-H",
                f"Cookie: {COOKIE}",
                url,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return ""
        html = result.stdout

    if CF_CHALLENGE_RE.search(html):
        return ""
    return html


def normalize_space(value):
    return re.sub(r"\s+", " ", value or "").strip()


def clean_text(value):
    return normalize_space(unescape(value or ""))


def strip_html(value):
    return clean_text(re.sub(r"<[^>]+>", " ", value or ""))


def absolute_url(value):
    value = clean_text(value)
    if not value:
        return ""
    return urljoin(BASE_URL, value)


def normalize_title(value):
    value = unescape(value or "").lower()
    value = re.sub(r"\.[a-z0-9]{2,5}$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^\d+\s*[-_. ]\s*", "", value)
    value = value.replace("&", " and ")
    value = re.sub(r"[_./-]+", " ", value)
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    return normalize_space(value)


def similarity(a, b):
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def title_tokens(value):
    return [token for token in normalize_title(value).split() if token]


def token_overlap_score(title, query):
    query_parts = set(title_tokens(query))
    if not query_parts:
        return 0.0
    title_parts = set(title_tokens(title))
    return len(query_parts & title_parts) / len(query_parts)


def slugify_query(value):
    value = normalize_title(value)
    return value.replace(" ", "-")


def unique_names(values):
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


def absolute_result_url(url):
    url = absolute_url(url)
    if not SCENE_URL_RE.match(url):
        return ""
    return url


def extract_meta(html, attr, key):
    patterns = [
        rf'<meta[^>]+{attr}=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+{attr}=["\']{re.escape(key)}["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.IGNORECASE)
        if match:
            return clean_text(match.group(1))
    return ""


def load_json_ld(html):
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
        block_type = block.get("@type")
        if block_type == wanted_type:
            return block
        if isinstance(block_type, list) and wanted_type in block_type:
            return block
    return {}


def parse_date_value(value):
    value = clean_text(value)
    if not value:
        return ""

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        pass

    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue

    lowered = value.casefold()
    relative_match = re.search(
        r"(\d+)\s+(minute|minutes|hour|hours|day|days|week|weeks|month|months)\b",
        lowered,
    )
    if relative_match:
        amount = int(relative_match.group(1))
        unit = relative_match.group(2)
        delta = timedelta()
        if "minute" in unit:
            delta = timedelta(minutes=amount)
        elif "hour" in unit:
            delta = timedelta(hours=amount)
        elif "day" in unit:
            delta = timedelta(days=amount)
        elif "week" in unit:
            delta = timedelta(weeks=amount)
        elif "month" in unit:
            delta = timedelta(days=30 * amount)
        return (datetime.now(timezone.utc) - delta).date().isoformat()

    if lowered in {"today", "just now"}:
        return datetime.now(timezone.utc).date().isoformat()
    if lowered == "yesterday":
        return (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat()
    return ""


def extract_h1_title(html):
    match = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.IGNORECASE | re.DOTALL)
    return strip_html(match.group(1)) if match else ""


def extract_description(html, video_json):
    candidates = [
        video_json.get("description", "") if video_json else "",
        extract_meta(html, "property", "og:description"),
        extract_meta(html, "name", "description"),
    ]
    for candidate in candidates:
        text = clean_text(candidate)
        if text:
            return text
    return ""


def extract_image(html, video_json):
    thumbnail = video_json.get("thumbnailUrl", "") if video_json else ""
    if isinstance(thumbnail, list) and thumbnail:
        return absolute_url(thumbnail[0])
    if isinstance(thumbnail, str) and thumbnail:
        return absolute_url(thumbnail)
    return absolute_url(extract_meta(html, "property", "og:image"))


def extract_performers(html):
    names = []
    for href, text in re.findall(
        r'<a[^>]+href=["\']([^"\']*/models/[^"\']*)["\'][^>]*>(.*?)</a>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        if "/models/" not in href.lower():
            continue
        name = strip_html(text)
        if not name or name.casefold() == "pornstar":
            continue
        names.append(name)
    return unique_names(names)


def extract_studio(html):
    match = re.search(
        r'<a[^>]+href=["\']([^"\']*/sites/[^"\']*)["\'][^>]*>(.*?)</a>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return {}
    name = strip_html(match.group(2))
    return {"name": name} if name else {}


def extract_tag_section(html):
    match = re.search(
        r'<div[^>]+class=["\'][^"\']*\brow\b[^"\']*["\'][^>]*>\s*<span>\s*Tags:\s*</span>(.*?)</ul>\s*</div>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match:
        return match.group(1)
    return html


def extract_tags(html):
    section = extract_tag_section(html)
    tags = []
    for href, text in re.findall(
        r'<a[^>]+href=["\']([^"\']*/search/[^"\']*)["\'][^>]*>(.*?)</a>',
        section,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        href_lower = href.lower()
        if "/search/" not in href_lower:
            continue
        if re.search(r"/search/(?:latest|top-rated|most-viewed|longest)/?$", href_lower):
            continue
        name = strip_html(text)
        if not name or name.casefold() in {"videos", "search", "ok", "learn more"}:
            continue
        name = name.rstrip(",")
        tags.append(name)
    if tags:
        return unique_names(tags)

    meta_tags = re.findall(
        r'<meta[^>]+property=["\']video:tag["\'][^>]+content=["\']([^"\']+)',
        html,
        flags=re.IGNORECASE,
    )
    return unique_names(meta_tags)


def scrape_scene(url):
    url = absolute_result_url(url)
    if not url:
        return {}

    html = fetch(url)
    if not html:
        return {}

    json_ld = load_json_ld(html)
    video_json = find_json_ld(json_ld, "VideoObject")

    title = clean_text(video_json.get("name", "")) if video_json else ""
    if not title:
        title = extract_meta(html, "property", "og:title")
    if not title:
        title = extract_h1_title(html)
    if title.endswith(" - AllBoner.com"):
        title = title[: -len(" - AllBoner.com")].strip()

    date = parse_date_value(
        extract_meta(html, "property", "ya:ovs:upload_date")
        or extract_meta(html, "property", "video:release_date")
        or (video_json.get("uploadDate", "") if video_json else "")
    )
    if not date:
        added_match = re.search(
            r"Added:\s*([^<]+?)(?:Views:|</)",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if added_match:
            date = parse_date_value(strip_html(added_match.group(1)))

    scene = {
        "title": title,
        "url": url,
        "date": date,
        "details": extract_description(html, video_json),
        "image": extract_image(html, video_json),
        "performers": extract_performers(html),
        "tags": extract_tags(html),
        "studio": extract_studio(html),
    }
    return {key: value for key, value in scene.items() if value not in ("", [], {}, None)}


def parse_search_results(html):
    pattern = re.compile(
        r'<a[^>]+href=["\'](?P<url>https?://(?:www\.)?allboner\.com/videos/\d+/[^"\']+/|/videos/\d+/[^"\']+/?)["\'][^>]*>'
        r'(?:(?P<body>.*?))</a>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    results = []
    seen = set()
    for match in pattern.finditer(html):
        url = absolute_result_url(match.group("url"))
        if not url or url in seen:
            continue

        body = match.group("body") or ""
        full_tag = match.group(0)
        title = ""

        title_attr = re.search(r'title=(["\'])(.*?)\1', full_tag, flags=re.IGNORECASE | re.DOTALL)
        if title_attr:
            title = clean_text(title_attr.group(2))
        if not title:
            alt_attr = re.search(r'alt=(["\'])(.*?)\1', full_tag, flags=re.IGNORECASE | re.DOTALL)
            if alt_attr:
                title = clean_text(alt_attr.group(2))
        if not title:
            body_title = re.search(
                r'<div[^>]+class=["\'][^"\']*\btitle\b[^"\']*["\'][^>]*>(.*?)</div>',
                body,
                flags=re.IGNORECASE | re.DOTALL,
            )
            if body_title:
                title = strip_html(body_title.group(1))
        if not title:
            title = strip_html(body)
        title = re.sub(r"\s+\d{1,2}:\d{2}\s*$", "", title).strip()
        if not title:
            slug = url.rstrip("/").rsplit("/", 1)[-1]
            title = clean_text(slug.replace("-", " "))

        image = ""
        for pattern in (
            r'data-original=(["\'])(.*?)\1',
            r'data-src=(["\'])(.*?)\1',
            r'src=(["\'])(.*?)\1',
        ):
            image_match = re.search(pattern, full_tag, flags=re.IGNORECASE | re.DOTALL)
            if not image_match:
                continue
            candidate = absolute_url(image_match.group(2))
            if not candidate or candidate.startswith("data:image"):
                continue
            image = candidate
            break

        seen.add(url)
        results.append(
            {
                "title": title,
                "url": url,
                "image": image,
            }
        )
    return results


def search_scenes(query):
    query = normalize_space(query)
    if not query:
        return []

    urls = []
    slug = slugify_query(query)
    if slug:
        urls.append(SEARCH_URL.format(query=quote(slug, safe="-")))
    urls.append(SEARCH_URL.format(query=quote(query, safe="")))

    results = []
    seen = set()
    for url in urls:
        html = fetch(url)
        if not html:
            continue
        for item in parse_search_results(html):
            key = item["url"]
            if key in seen:
                continue
            seen.add(key)
            results.append(item)
        if results:
            break

    results.sort(
        key=lambda item: (
            normalize_title(item.get("title", "")) != normalize_title(query),
            -token_overlap_score(item.get("title", ""), query),
            -similarity(item.get("title", ""), query),
            item.get("title", "").casefold(),
        )
    )
    return results


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
    request = read_stdin()
    mode = request.get("mode", "")
    args = request.get("args") or {}

    if mode == "sceneByURL":
        emit(wrap_scene_result(scrape_scene(args.get("url", ""))))
        return

    if mode == "sceneByName":
        emit(wrap_search_results(search_scenes(args.get("name", ""))))
        return

    emit({"results": []})


if __name__ == "__main__":
    main()
