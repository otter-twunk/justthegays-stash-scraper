#!/usr/bin/env python3

import base64
import json
import re
import ssl
import subprocess
import sys
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen


BASE_URL = "https://thefap.net"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) "
    "Gecko/20100101 Firefox/115.0"
)
GENERIC_DESCRIPTION = (
    "The best social network with a lot of leaked girls from Onlyfans, Patreon "
    "and other nude content platforms with high quality and free"
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
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=30, context=SSL_CONTEXT) as response:
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
    value = clean_text(value)
    if not value:
        return ""
    return urljoin(BASE_URL + "/", value)


def extract_html_title(html):
    match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    return strip_html(match.group(1)) if match else ""


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


def extract_canonical(html):
    match = re.search(
        r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)',
        html,
        flags=re.IGNORECASE,
    )
    return absolute_url(match.group(1)) if match else ""


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


def strip_title_suffix(value):
    return re.sub(r"\s*-\s*TheFap\s*$", "", clean_text(value), flags=re.IGNORECASE)


def title_case_slug(value):
    parts = [part for part in re.split(r"[-_]+", value or "") if part]
    return " ".join(part.capitalize() for part in parts)


def performer_name_from_slug(slug):
    slug = re.sub(r"-\d+$", "", slug or "")
    return title_case_slug(slug)


def performer_username_from_slug(slug):
    return clean_text(re.sub(r"-\d+$", "", slug or ""))


def normalize_scene_url(url):
    url = clean_text(url)
    if not url:
        return ""
    if not re.match(r"^https?://", url, flags=re.IGNORECASE):
        url = absolute_url(url)
    url = re.sub(r"^https?://(?:www\.)?thefap\.net", BASE_URL, url, flags=re.IGNORECASE)
    parts = urlsplit(url)
    path = re.sub(r"/+", "/", parts.path or "/")
    path = path.rstrip("/")
    return urlunsplit(("https", "thefap.net", path, "", ""))


def normalize_performer_url(url):
    url = clean_text(url)
    if not url:
        return ""
    if not re.match(r"^https?://", url, flags=re.IGNORECASE):
        url = absolute_url(url)
    url = re.sub(r"^https?://(?:www\.)?thefap\.net", BASE_URL, url, flags=re.IGNORECASE)
    parts = urlsplit(url)
    path = re.sub(r"/+", "/", parts.path or "/").rstrip("/")
    if not path:
        return ""
    return urlunsplit(("https", "thefap.net", path + "/", "", ""))


def parse_scene_path(url):
    parts = [part for part in urlsplit(url).path.split("/") if part]
    if len(parts) < 3:
        return "", "", ""
    return parts[0], parts[1], parts[2]


def parse_performer_path(url):
    parts = [part for part in urlsplit(url).path.split("/") if part]
    return parts[0] if parts else ""


def is_performer_slug(value):
    return bool(re.fullmatch(r"[a-z0-9][a-z0-9_-]*-\d+", value or "", flags=re.IGNORECASE))


def is_scene_id(value):
    return bool(re.fullmatch(r"i\d+", value or "", flags=re.IGNORECASE))


def extract_scene_title(html, performer_slug, scene_code):
    match = re.search(
        r'<a[^>]+href=["\']/[^"\']+-\d+/["\'][^>]*class=["\'][^"\']*font-semibold[^"\']*["\'][^>]*>(.*?)</a>\s*'
        r'<span[^>]*>\s*(Video\s*#.*?|Post\s*#.*?)\s*</span>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match:
        performer_name = strip_html(match.group(1))
        suffix = strip_html(match.group(2))
        if performer_name and suffix:
            return f"{performer_name} {suffix}"

    title = strip_title_suffix(extract_html_title(html))
    if title:
        return title

    performer_name = performer_name_from_slug(performer_slug)
    if performer_name and scene_code:
        return f"{performer_name} Video #{scene_code}"
    return performer_name


def extract_iframe_src(html):
    match = re.search(
        r'<iframe[^>]+id=["\']sv-iframe["\'][^>]+src=["\']([^"\']+)',
        html,
        flags=re.IGNORECASE,
    )
    return absolute_url(match.group(1)) if match else ""


def maybe_decode_base64(value):
    value = clean_text(value)
    if not value:
        return ""
    try:
        padding = (-len(value)) % 4
        decoded = base64.b64decode(value + ("=" * padding)).decode("utf-8", errors="replace")
    except Exception:
        return ""
    return clean_text(decoded)


def extract_scene_image(html):
    iframe_src = extract_iframe_src(html)
    if iframe_src:
        query = parse_qs(urlsplit(iframe_src).query)
        for key in ("i", "img", "image"):
            values = query.get(key, [])
            if values:
                return absolute_url(unquote(values[0]))

    match = re.search(
        r'data-src=["\'](https?://img\.[^"\']+/\S+?\.(?:jpg|jpeg|png|webp))',
        html,
        flags=re.IGNORECASE,
    )
    if match:
        return clean_text(match.group(1))
    return ""


def is_generic_description(value):
    return clean_text(value).casefold() == GENERIC_DESCRIPTION.casefold()


def extract_scene_details(html, source_slug, scene_code):
    pieces = []

    source_label = title_case_slug(source_slug)
    if source_label:
        pieces.append(f"Source: {source_label}")

    code = clean_text(scene_code)
    if code:
        pieces.append(f"Code: {code}")

    title = strip_title_suffix(extract_html_title(html))
    if title:
        title = re.sub(r"\s*/\s*", " / ", title)
        title = normalize_space(title)
        if title:
            pieces.append(title)

    details = " | ".join(piece for piece in pieces if piece)
    return details[:1000]


def extract_scene_tags(html, source_slug):
    tags = []
    for href, text in re.findall(
        r'<a[^>]+href=["\'](/g/[^"\']+)["\'][^>]*>(.*?)</a>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        _ = href
        name = strip_html(text)
        if name:
            tags.append(name)

    if source_slug:
        tags.append(title_case_slug(source_slug))

    return unique_named_items(tags)


def extract_scene_performers(html, performer_slug):
    values = []
    for href, text in re.findall(
        r'<a[^>]+href=["\'](/[^"\']+-\d+/)["\'][^>]*>(.*?)</a>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        slug = parse_performer_path(href)
        name = strip_html(text)
        if slug and name:
            values.append(name)

    if not values and performer_slug:
        values.append(performer_name_from_slug(performer_slug))

    return unique_named_items(values)


def extract_scene_code(scene_path_code):
    if not scene_path_code:
        return ""
    return clean_text(scene_path_code)


def scrape_scene(url):
    url = normalize_scene_url(url)
    performer_slug, source_slug, scene_id = parse_scene_path(url)
    if (
        not performer_slug
        or not source_slug
        or not scene_id
        or not is_performer_slug(performer_slug)
        or not is_scene_id(scene_id)
    ):
        return {}

    html = fetch(url)
    if not html:
        return {}

    code = extract_scene_code(f"{source_slug}{scene_id}")
    details = extract_scene_details(html, source_slug, code)

    scene = {
        "title": extract_scene_title(html, performer_slug, code),
        "url": extract_canonical(html) or url,
        "details": details,
        "image": extract_scene_image(html),
        "performers": extract_scene_performers(html, performer_slug),
        "tags": extract_scene_tags(html, source_slug),
        "code": code,
    }

    return {key: value for key, value in scene.items() if value not in ("", [], None)}


def extract_profile_header(html):
    match = re.search(
        r'<div[^>]+class=["\'][^"\']*justify-between[^"\']*["\'][^>]*>\s*'
        r'<div[^>]*>\s*<h1[^>]*>(.*?)</h1>\s*<div[^>]*>(.*?)</div>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return "", ""
    return strip_html(match.group(1)), strip_html(match.group(2))


def extract_profile_counts(html):
    match = re.search(
        r'(Videos\s*\(\d+\).*?Album\s*\(\d+\).*?\d+\s+Media.*?\d+\s+Like)',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return normalize_space(strip_html(match.group(1))) if match else ""


def extract_profile_thumbnail(html):
    matches = re.findall(
        r'data-src=["\'](https?://img\.[^"\']+/\S+?\.(?:jpg|jpeg|png|webp))',
        html,
        flags=re.IGNORECASE,
    )
    for match in matches:
        image = clean_text(match)
        if image:
            return image
    return ""


def scrape_performer(url):
    url = normalize_performer_url(url)
    slug = parse_performer_path(url)
    if not slug or not is_performer_slug(slug):
        return {}

    html = fetch(url)
    if not html:
        return {
            "name": performer_name_from_slug(slug),
            "url": url,
        }

    display_name, profile_meta = extract_profile_header(html)
    if not display_name:
        display_name = performer_name_from_slug(slug)

    details_bits = []
    username = performer_username_from_slug(slug)
    if username:
        details_bits.append(f"Username: {username}")
    if profile_meta and not is_generic_description(profile_meta):
        details_bits.append(profile_meta)
    counts = extract_profile_counts(html)
    if counts:
        details_bits.append(counts)

    performer = {
        "name": display_name,
        "url": extract_canonical(html) or url,
        "image": extract_profile_thumbnail(html),
        "details": " | ".join(details_bits),
    }
    return {key: value for key, value in performer.items() if value not in ("", [], None)}


def get_url_from_request(request):
    args = request.get("args", {})
    input_data = request.get("input", {})
    return request.get("url") or args.get("url") or input_data.get("url", "")


def main():
    request = read_request()
    mode = request.get("mode")
    url = get_url_from_request(request)

    if mode == "sceneByURL":
        result = scrape_scene(url)
        emit({"results": [result]} if result else {"results": []})
        return

    if mode == "performerByURL":
        result = scrape_performer(url)
        emit({"results": [result]} if result else {"results": []})
        return

    emit({"results": []})


if __name__ == "__main__":
    main()
