#!/usr/bin/env python3

import json
import re
import ssl
import subprocess
import sys
from datetime import datetime
from difflib import SequenceMatcher
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


BASE_URL = "https://www.xvideos.com"
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


def read_stdin():
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    return json.loads(raw)


def fetch(url, referer=""):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.5",
    }
    if referer:
        headers["Referer"] = referer

    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
            return response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        if exc.code == 404:
            return ""
        raise
    except URLError:
        args = [
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
        ]
        if referer:
            args.extend(["-e", referer])
        args.append(url)
        result = subprocess.run(args, capture_output=True, text=True, check=False)
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
    if value.startswith("//"):
        return "https:" + value
    if value.startswith("/"):
        return BASE_URL + value
    return value


def normalize_scene_url(url):
    url = clean_text(url)
    if not url:
        return ""
    if url.startswith("/"):
        return BASE_URL + url
    return url


def normalize_performer_url(url):
    url = clean_text(url)
    if not url:
        return ""
    if url.startswith("/"):
        return BASE_URL + url
    return url.rstrip("/")


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


def extract_title_tag(html):
    match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    title = clean_text(match.group(1))
    return re.sub(r"\s*-\s*XVIDEOS\.COM.*$", "", title, flags=re.IGNORECASE)


def extract_json_ld(html):
    for match in re.finditer(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        raw = match.group(1)
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and value.get("@type") == "VideoObject":
            return value
    return {}


def extract_xv_conf(html):
    marker = "window.xv.conf="
    pos = html.find(marker)
    if pos == -1:
        return {}
    try:
        value, _ = json.JSONDecoder().raw_decode(html[pos + len(marker):])
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def parse_date(value):
    value = clean_text(value)
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except ValueError:
        return value[:10] if re.match(r"\d{4}-\d{2}-\d{2}", value) else ""


def normalize_gender(value):
    value = clean_text(value)
    if not value:
        return ""
    mapping = {
        "man": "Male",
        "male": "Male",
        "woman": "Female",
        "female": "Female",
        "trans": "Transgender",
        "transgender": "Transgender",
    }
    return mapping.get(value.lower(), value)


def unique_named_dicts(values):
    seen = set()
    output = []
    for value in values:
        if not isinstance(value, dict):
            continue
        name = clean_text(value.get("name", ""))
        if not name:
            continue
        dedupe = (name.casefold(), clean_text(value.get("url", "")).casefold())
        if dedupe in seen:
            continue
        seen.add(dedupe)
        item = dict(value)
        item["name"] = name
        output.append({k: v for k, v in item.items() if v not in ("", [], None)})
    return output


def unique_tag_dicts(values):
    seen = set()
    output = []
    for value in values:
        if not isinstance(value, dict):
            continue
        name = clean_text(value.get("name", ""))
        if not name or name.casefold() in seen:
            continue
        seen.add(name.casefold())
        output.append({"name": name})
    return output


def extract_js_call_value(html, function_name):
    pattern = rf"{re.escape(function_name)}\((.*?)\);"
    match = re.search(pattern, html, flags=re.DOTALL)
    if not match:
        return None
    raw = match.group(1).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        if raw in {"false", "true", "null"}:
            return {"false": False, "true": True, "null": None}[raw]
        return clean_text(raw.strip("'\""))


def parse_scene_performers(html):
    performers = []
    for match in re.finditer(
        r'<li class="main-uploader".*?<a href="(/profiles/[^"]+)"[^>]*>.*?<span class="name">(.*?)</span>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        performers.append(
            {
                "name": strip_html(match.group(2)),
                "url": normalize_performer_url(match.group(1)),
            }
        )
    return unique_named_dicts(performers)


def parse_scene_tags(html, dyn):
    tags = []
    for tag in dyn.get("video_tags", []):
        name = clean_text(tag)
        if name:
            tags.append({"name": name})
    if tags:
        return unique_tag_dicts(tags)

    for match in re.finditer(r'href="/tags/[^"]+"[^>]*>(.*?)</a>', html, re.IGNORECASE):
        name = strip_html(match.group(1))
        if name:
            tags.append({"name": name})
    return unique_tag_dicts(tags)


def scene_from_html(html, url):
    if not html:
        return {}

    conf = extract_xv_conf(html)
    dyn = conf.get("dyn", {})
    json_ld = extract_json_ld(html)

    title = (
        clean_text(dyn.get("video_title", ""))
        or clean_text(json_ld.get("name", ""))
        or extract_meta(html, "property", "og:title")
        or extract_title_tag(html)
    )

    image = ""
    thumbs = json_ld.get("thumbnailUrl")
    if isinstance(thumbs, list) and thumbs:
        image = absolute_url(thumbs[0])
    elif isinstance(thumbs, str):
        image = absolute_url(thumbs)
    if not image:
        image = absolute_url(extract_js_call_value(html, "html5player.setThumbUrl169") or "")
    if not image:
        image = absolute_url(extract_meta(html, "property", "og:image"))

    details = clean_text(json_ld.get("description", "")) or extract_meta(
        html, "name", "description"
    )
    generic_details = f"XVIDEOS {title} free"
    if details == generic_details:
        details = title

    scene = {
        "title": title,
        "url": normalize_scene_url(extract_meta(html, "property", "og:url") or url),
        "date": parse_date(json_ld.get("uploadDate", "")),
        "details": details,
        "image": image,
        "performers": parse_scene_performers(html),
        "tags": parse_scene_tags(html, dyn),
    }

    sponsor = extract_js_call_value(html, "html5player.setSponsors")
    if isinstance(sponsor, str):
        sponsor = clean_text(sponsor)
        if sponsor and sponsor.lower() != "false":
            scene["studio"] = {"name": sponsor}

    return {k: v for k, v in scene.items() if v not in ("", [], None)}


def extract_profile_field(html, field_id):
    match = re.search(
        rf'<p id="{re.escape(field_id)}"[^>]*>.*?<span>(.*?)</span>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return ""
    return strip_html(match.group(1))


def performer_from_html(html, url):
    if not html:
        return {}

    conf = extract_xv_conf(html)
    data = conf.get("data", {})
    user = data.get("user", {})

    display = clean_text(user.get("display", ""))
    username = clean_text(user.get("username", ""))
    name = display or username
    if not name:
        match = re.search(
            r"<h2[^>]*>.*?<strong[^>]*>(.*?)</strong>",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if match:
            name = strip_html(match.group(1))

    aliases = []
    if username and display and username.casefold() != display.casefold():
        aliases.append(username)

    age = extract_profile_field(html, "pinfo-age")
    country = extract_profile_field(html, "pinfo-country")
    region = extract_profile_field(html, "pinfo-region")
    sexual_preference = extract_profile_field(html, "pinfo-sexualpreference")
    body_type = extract_profile_field(html, "pinfo-body")

    detail_parts = []
    for label, value in (
        ("Age", age),
        ("Country", country),
        ("Region", region),
        ("Preference", sexual_preference),
        ("Body", body_type),
    ):
        if value:
            detail_parts.append(f"{label}: {value}")

    performer = {
        "name": name,
        "url": normalize_performer_url(user.get("url", "") or url),
        "gender": normalize_gender(
            user.get("sex", "") or extract_profile_field(html, "pinfo-gender")
        ),
        "country": country,
        "image": absolute_url(
            user.get("profile_picture", "") or user.get("profile_picture_small", "")
        ),
        "aliases": aliases,
        "details": " | ".join(detail_parts),
    }
    return {k: v for k, v in performer.items() if v not in ("", [], None)}


def normalize_title(value):
    value = unescape(value or "").lower()
    value = re.sub(r"\.[a-z0-9]{2,5}$", "", value)
    value = re.sub(r"^\d+\s*[-_. ]\s*", "", value)
    value = re.sub(r"[_./-]+", " ", value)
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    return normalize_space(value)


def similarity(a, b):
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def search_scenes(name):
    query = clean_text(name)
    if not query:
        return []
    if query.startswith("http://") or query.startswith("https://"):
        scene = scrape_scene(query)
        return [scene] if scene else []

    url = f"{BASE_URL}/?k={quote_plus(query)}"
    html = fetch(url)
    if not html:
        return []

    results = []
    seen = set()
    pattern = re.compile(
        r'<div id="video_[^"]+"[^>]*data-id="(?P<id>\d+)"[^>]*>'
        r'(?P<body>.*?)<script>xv\.thumbs\.prepareVideo\(\d+\);</script></div>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(html):
        block = match.group("body")
        link_match = re.search(
            r'<p class="title"><a href="(?P<url>/video[^"]+)" title="(?P<title>[^"]+)"',
            block,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not link_match:
            continue
        scene_url = normalize_scene_url(link_match.group("url"))
        if scene_url in seen:
            continue
        seen.add(scene_url)

        thumb_match = re.search(r'data-src="([^"]+)"', block, re.IGNORECASE)
        performer_match = re.search(
            r'<a href="(/profiles/[^"]+)"><span class="name">(.*?)</span></a>',
            block,
            flags=re.IGNORECASE | re.DOTALL,
        )
        result = {
            "title": clean_text(link_match.group("title")),
            "url": scene_url,
            "image": absolute_url(thumb_match.group(1) if thumb_match else ""),
        }
        if performer_match:
            result["performers"] = [
                {
                    "name": strip_html(performer_match.group(2)),
                    "url": normalize_performer_url(performer_match.group(1)),
                }
            ]
        results.append(result)

    results.sort(key=lambda item: similarity(query, item.get("title", "")), reverse=True)
    return results[:20]


def scrape_scene(url):
    url = normalize_scene_url(url)
    if not url:
        return {}
    html = fetch(url)
    return scene_from_html(html, url)


def scrape_performer(url):
    url = normalize_performer_url(url)
    if not url:
        return {}
    html = fetch(url)
    return performer_from_html(html, url)


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
    elif mode == "performerByURL":
        result = scrape_performer(data.get("url", ""))
    else:
        result = {}

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
