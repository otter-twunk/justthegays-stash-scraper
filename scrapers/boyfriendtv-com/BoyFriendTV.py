#!/usr/bin/env python3
# BoyFriendTV Stash scraper
# Supported: sceneByURL, performerByURL
# NOT supported: sceneByName, sceneByQueryFragment, sceneByFragment
#   -- search pages are Cloudflare-protected and not accessible to headless requests

import json
import re
import subprocess
import sys
from datetime import datetime
from html import unescape
import ssl
from urllib.error import URLError
from urllib.request import Request, urlopen

BASE_URL = "https://www.boyfriendtv.com"
STUDIO = "BoyFriendTV"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) "
    "Gecko/20100101 Firefox/115.0"
)
COOKIES = "age_verified=1"

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
            "Accept-Language": "en-US,en;q=0.5",
            "Cookie": COOKIES,
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
                "-A", USER_AGENT,
                "-H", "Accept: text/html,application/xhtml+xml",
                "-H", "Accept-Language: en-US,en;q=0.5",
                "-H", f"Cookie: {COOKIES}",
                url,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout


def is_cloudflare_challenge(html):
    return "cf_chl" in html or "Just a moment" in html[:500]


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
        graph = block.get("@graph", [])
        if isinstance(graph, list):
            for item in graph:
                if isinstance(item, dict) and item.get("@type") == wanted_type:
                    return item
    return None


def normalize_space(value):
    return re.sub(r"\s+", " ", value or "").strip()


def strip_html(value):
    text = re.sub(r"<[^>]+>", " ", value or "")
    return normalize_space(unescape(text))


def parse_date(iso_value):
    if not iso_value:
        return ""
    try:
        return datetime.fromisoformat(iso_value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return iso_value.split("T", 1)[0]


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


def extract_meta_content(html, prop_name):
    match = re.search(
        rf'<meta[^>]+(?:property|name)=["\']{re.escape(prop_name)}["\'][^>]+content=["\']([^"\']+)',
        html,
        flags=re.IGNORECASE,
    )
    return normalize_space(unescape(match.group(1))) if match else ""


def extract_html_title(html):
    match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    return strip_html(match.group(1)) if match else ""


def clean_performer_name(value):
    name = normalize_space(value)
    name = re.sub(r"\s+Gay Pornstar\s+-\s+BoyFriendTV\.com$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s+\|\s+BoyFriendTV$", "", name, flags=re.IGNORECASE)
    return normalize_space(name)


def split_keywords(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [part.strip() for part in value.split(",")]
    return []


def extract_performers_from_html(html):
    names = re.findall(
        r'href="/pornstars/[^"]+/videos/"[^>]*>([^<]+)</a>',
        html,
        flags=re.IGNORECASE,
    )
    return unique_names(normalize_space(unescape(n)) for n in names)


def extract_tags_from_html(html):
    names = re.findall(
        r'href="/tags/[^"]+"[^>]*>([^<]+)</a>',
        html,
        flags=re.IGNORECASE,
    )
    return unique_names(normalize_space(unescape(n)) for n in names)


def scrape_scene(url):
    try:
        html = fetch(url)
    except Exception:
        return {}

    if is_cloudflare_challenge(html):
        return {}

    blocks = load_json_ld_blocks(html)
    video = find_json_ld(blocks, "VideoObject")
    if not video:
        return {}

    # Performers from JSON-LD actor list
    actors = []
    for actor in video.get("actor", []):
        if isinstance(actor, dict):
            actors.append(actor.get("name", ""))
        elif isinstance(actor, str):
            actors.append(actor)
    performers = unique_names(actors) or extract_performers_from_html(html)

    # Tags from JSON-LD keywords list
    kw = split_keywords(video.get("keywords", []))
    tags = unique_names(kw) if kw else extract_tags_from_html(html)

    # Cover image: prefer first full-size thumbnailUrl
    image = video.get("thumbnailUrl", "")
    if isinstance(image, list):
        image = image[0] if image else ""

    title = normalize_space(video.get("name", ""))
    if not title:
        title = extract_meta_content(html, "og:title")
    if not title:
        title = re.sub(r"\s+\|\s+BoyFriendTV$", "", extract_html_title(html), flags=re.IGNORECASE)

    scene = {
        "title": title,
        "url": url,
        "date": parse_date(video.get("uploadDate", "")),
        "details": normalize_space(unescape(video.get("description", ""))),
        "image": image or "",
        "performers": performers,
        "tags": tags,
        "studio": {"name": STUDIO},
    }
    return {key: value for key, value in scene.items() if value}


def slug_to_name(slug):
    """Convert a URL slug like 'scott-demarco-2077' to 'Scott Demarco'."""
    slug = re.sub(r"-\d+$", "", slug or "")
    return " ".join(part.capitalize() for part in slug.split("-") if part)


def scrape_performer(url):
    # Attempt live fetch; performer pages often trigger CF challenge
    try:
        html = fetch(url)
    except Exception:
        html = ""

    if html and not is_cloudflare_challenge(html):
        blocks = load_json_ld_blocks(html)
        person = find_json_ld(blocks, "Person")
        if person:
            performer = {
                "name": normalize_space(person.get("name", "")),
                "url": url,
                "gender": "Male",
                "image": person.get("image", ""),
                "details": normalize_space(unescape(person.get("description", ""))),
            }
            return {key: value for key, value in performer.items() if value}

        # Fallback: og:title and og:image
        name = extract_meta_content(html, "og:title")
        if not name:
            name = extract_html_title(html)
        performer = {
            "name": clean_performer_name(name),
            "url": url,
            "gender": "Male",
            "image": extract_meta_content(html, "og:image"),
        }
        return {key: value for key, value in performer.items() if value}

    # CF blocked — return minimal data from URL slug
    slug_match = re.search(r'/pornstars/([^/]+)/?$', url)
    name = slug_to_name(slug_match.group(1)) if slug_match else ""
    performer = {
        "name": name,
        "url": url,
        "gender": "Male",
    }
    return {key: value for key, value in performer.items() if value}


def main():
    if len(sys.argv) < 2:
        print("{}")
        return

    mode = sys.argv[1]
    data = read_stdin()

    if mode == "sceneByURL":
        result = scrape_scene(data.get("url", ""))
    elif mode == "performerByURL":
        result = scrape_performer(data.get("url", ""))
    else:
        result = {}

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
