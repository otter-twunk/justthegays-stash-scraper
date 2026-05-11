#!/usr/bin/env python3

import json
import re
import ssl
import subprocess
import sys
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen


BASE_URL = "https://thisvid.com"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) "
    "Gecko/20100101 Firefox/115.0"
)

SSL_CONTEXT = None
try:
    import certifi

    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CONTEXT = ssl.create_default_context()


def emit(payload):
    json.dump(payload, sys.stdout, ensure_ascii=False)


def read_request():
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    return json.loads(raw)


def fetch(url):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.5",
    }
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
            return response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        if exc.code == 404:
            return ""
        raise
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
                "Accept-Language: en-US,en;q=0.5",
                url,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return ""
        return result.stdout


def normalize_space(value):
    return re.sub(r"\s+", " ", value or "").strip()


def clean_text(value):
    return normalize_space(unescape(value or ""))


def strip_html(value):
    return clean_text(re.sub(r"<[^>]+>", " ", value or ""))


def absolute_url(value):
    value = (value or "").strip()
    if not value:
        return ""
    if value.startswith("//"):
        return "https:" + value
    if value.startswith("/"):
        return BASE_URL + value
    return value


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


def strip_title_suffix(value):
    value = clean_text(value)
    return re.sub(r"\s*-\s*ThisVid\.com\s*$", "", value, flags=re.IGNORECASE)


def normalize_scene_url(url):
    url = (url or "").strip()
    if not url:
        return ""
    if not re.match(r"^https?://", url, flags=re.IGNORECASE):
        url = BASE_URL.rstrip("/") + "/" + url.lstrip("/")
    url = re.sub(r"^https?://(?:www\.)?thisvid\.com", BASE_URL, url, flags=re.IGNORECASE)
    parts = urlsplit(url)
    path = re.sub(r"/+", "/", parts.path or "/")
    if not path.endswith("/"):
        path += "/"
    normalized = urlunsplit((parts.scheme or "https", parts.netloc or "thisvid.com", path, "", ""))
    return normalized


def extract_title(html):
    title = strip_title_suffix(extract_meta(html, "property", "og:title"))
    if title:
        return title

    match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return strip_title_suffix(strip_html(match.group(1)))
    return ""


def extract_description(html):
    match = re.search(
        r'<ul[^>]+class=["\'][^"\']*\bdescription\b[^"\']*["\'][^>]*>.*?<li>\s*<p>(.*?)</p>\s*</li>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match:
        value = strip_html(match.group(1))
        if value:
            return value

    description = extract_meta(html, "property", "og:description")
    if description:
        return description

    return extract_meta(html, "name", "description")


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


def parse_link_list(html, label):
    pattern = re.compile(
        rf'<li>\s*<span>\s*{re.escape(label)}\s*</span>(.*?)</li>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(html)
    if not match:
        return []

    values = []
    for href, text in re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', match.group(1), flags=re.IGNORECASE | re.DOTALL):
        _ = href
        name = strip_html(text)
        if name:
            values.append(name)
    return unique_named_items(values)


def extract_date(html):
    match = re.search(
        r'<span>\s*Added:\s*</span>\s*([^<]+)',
        html,
        flags=re.IGNORECASE,
    )
    if not match:
        return ""

    value = clean_text(match.group(1))
    date_match = re.search(r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})", value)
    if not date_match:
        return ""

    parts = clean_text(date_match.group(1)).split()
    if len(parts) != 3:
        return ""

    day, month_name, year = parts
    months = {
        "january": "01",
        "february": "02",
        "march": "03",
        "april": "04",
        "may": "05",
        "june": "06",
        "july": "07",
        "august": "08",
        "september": "09",
        "october": "10",
        "november": "11",
        "december": "12",
    }
    month = months.get(month_name.casefold())
    if not month:
        return ""
    return f"{year}-{month}-{int(day):02d}"


def extract_video_id(html):
    match = re.search(r'data-video-id=["\'](\d+)["\']', html, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"videoId:\s*['\"]?(\d+)", html, flags=re.IGNORECASE)
    return match.group(1) if match else ""


def scrape_scene(url):
    url = normalize_scene_url(url)
    if not url or "/videos/" not in url:
        return {}

    html = fetch(url)
    if not html:
        return {}

    categories = parse_link_list(html, "Categories:")
    tags = parse_link_list(html, "Tags:")
    merged_tags = unique_named_items([item["name"] for item in categories + tags])
    scene = {
        "title": extract_title(html),
        "url": absolute_url(extract_meta(html, "property", "og:url")) or url,
        "date": extract_date(html),
        "details": extract_description(html),
        "image": absolute_url(extract_meta(html, "property", "og:image")),
        "tags": merged_tags,
        # ThisVid exposes the uploader publicly, but not reliable performer metadata.
        "code": extract_video_id(html),
    }

    return {key: value for key, value in scene.items() if value not in ("", [], None)}


def get_url_from_request(request):
    args = request.get("args", {})
    return (
        request.get("url")
        or args.get("url")
        or request.get("input", {}).get("url", "")
    )


def main():
    request = read_request()
    mode = request.get("mode")

    if mode == "sceneByURL":
        result = scrape_scene(get_url_from_request(request))
        emit({"results": [result]} if result else {"results": []})
        return

    emit({"results": []})


if __name__ == "__main__":
    main()
