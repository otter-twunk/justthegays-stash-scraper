#!/usr/bin/env python3
# TheGay.com Stash scraper
# Supported: sceneByURL
# NOT supported: sceneByName, sceneByQueryFragment, sceneByFragment, performerByURL
#   -- site is a Vue SPA (TXXX network); all routes return empty HTML shells with no metadata.
#   -- performer and search pages have no server-rendered data.
#
import json
import re
import ssl
import subprocess
import sys
from datetime import datetime
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = "https://www.thegay.com"
STUDIO = "TheGay.com"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) "
    "Gecko/20100101 Firefox/115.0"
)
COOKIES = "age_verified=1"

API_ENDPOINT_PATH = "/api/json/video/{lifetime}/{million_bucket}/{thousand_bucket}/{id}.json"
API_LIFETIME = 86400

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


def fetch(url, extra_headers=None):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/html, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Cookie": COOKIES,
    }
    if extra_headers:
        headers.update(extra_headers)
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
            return response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError):
        curl_args = [
            "curl", "-L", "--silent", "--fail",
            "-A", USER_AGENT,
            "-H", "Accept: application/json, text/html, */*",
            "-H", "Accept-Language: en-US,en;q=0.5",
            "-H", f"Cookie: {COOKIES}",
        ]
        for k, v in (extra_headers or {}).items():
            curl_args += ["-H", f"{k}: {v}"]
        curl_args.append(url)
        try:
            result = subprocess.run(curl_args, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            return ""
        return result.stdout


def extract_id_from_url(url):
    m = re.search(r"/video/(\d+)/", url)
    return m.group(1) if m else None


def parse_date(value):
    if not value:
        return ""
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return str(value).split("T", 1)[0]


def normalize(value):
    return re.sub(r"\s+", " ", unescape(str(value or ""))).strip()


def unique_by_name(items):
    seen = set()
    unique = []
    for item in items:
        name = normalize(item.get("name", ""))
        key = name.lower()
        if not name or key in seen:
            continue
        seen.add(key)
        unique.append({"name": name})
    return unique


def category_items(value):
    if isinstance(value, dict):
        return list(value.values())
    if isinstance(value, list):
        return value
    return []


def build_video_api_url(video_id):
    numeric_id = int(video_id)
    return BASE_URL + API_ENDPOINT_PATH.format(
        lifetime=API_LIFETIME,
        million_bucket=(numeric_id // 1_000_000) * 1_000_000,
        thousand_bucket=(numeric_id // 1_000) * 1_000,
        id=video_id,
    )


def fetch_video_api(video_id, scene_url):
    api_url = build_video_api_url(video_id)
    raw = fetch(api_url, extra_headers={"Referer": scene_url})
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def scrape_scene(url):
    video_id = extract_id_from_url(url)
    if not video_id:
        return {}

    data = fetch_video_api(video_id, url)
    if not data:
        return {}

    # Unwrap if API wraps payload under a key
    if isinstance(data, dict) and "video" in data:
        data = data["video"]
    elif isinstance(data, dict) and "data" in data:
        data = data["data"]
    elif not isinstance(data, dict):
        return {}

    title = normalize(data.get("title") or data.get("name") or "")

    raw_date = data.get("post_date") or data.get("added") or data.get("date") or ""
    date = parse_date(raw_date)

    details = normalize(data.get("description") or data.get("text") or "")

    # Cover image
    image = normalize(
        data.get("thumbsrc")
        or data.get("thumb")
        or data.get("thumb_url")
        or data.get("preview_url")
        or ""
    )
    thumbs = data.get("thumbs") or []
    if not image and thumbs and isinstance(thumbs, list):
        image = thumbs[0].get("src", "") if isinstance(thumbs[0], dict) else str(thumbs[0])

    # Performers
    performers = []
    performer_sources = []
    for field in ("models", "pornstars", "models_suggested"):
        performer_sources.extend(category_items(data.get(field)))
    for model in performer_sources:
        name = ""
        if isinstance(model, dict):
            name = normalize(
                model.get("title")
                or model.get("name")
                or model.get("username")
                or ""
            )
        elif isinstance(model, str):
            name = normalize(model)
        if name:
            performers.append({"name": name})
    performers = unique_by_name(performers)

    # Tags
    tags = []
    tag_sources = []
    for field in ("categories", "tags"):
        tag_sources.extend(category_items(data.get(field)))
    for cat in tag_sources:
        label = ""
        if isinstance(cat, dict):
            label = normalize(cat.get("title") or cat.get("name") or "")
        elif isinstance(cat, str):
            label = normalize(cat)
        if label:
            tags.append({"name": label})
    tags = unique_by_name(tags)

    scene = {
        "title": title,
        "url": url,
        "date": date,
        "details": details,
        "image": image,
        "studio": {"name": STUDIO},
        "performers": performers,
        "tags": tags,
    }
    return {k: v for k, v in scene.items() if v}


def main():
    if len(sys.argv) < 2:
        print("{}")
        return

    mode = sys.argv[1]
    data = read_stdin()

    if mode == "sceneByURL":
        result = scrape_scene(data.get("url", ""))
    else:
        result = {}

    print(json.dumps(result))


if __name__ == "__main__":
    main()
