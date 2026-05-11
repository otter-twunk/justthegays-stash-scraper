#!/usr/bin/env python3

import json
import re
import ssl
import subprocess
import sys
from datetime import datetime, timezone
from difflib import SequenceMatcher
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


BASE_URL = "https://xhamster.com"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) "
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


def fetch(url, referer=""):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.5",
        "Cookie": COOKIES,
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
            "-H",
            f"Cookie: {COOKIES}",
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


def normalize_title(value):
    value = unescape(value or "").lower()
    value = re.sub(r"\.[a-z0-9]{2,5}$", "", value)
    value = re.sub(r"^\d+\s*[-_. ]\s*", "", value)
    value = re.sub(r"[_./-]+", " ", value)
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    return normalize_space(value)


def similarity(a, b):
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def normalize_fragment_text(value):
    value = unescape(value or "")
    value = re.sub(r"\.[a-z0-9]{2,5}$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^\d+\s*[-_. ]\s*", "", value)
    value = re.sub(r"[_./]+", " ", value)
    return normalize_space(value)


def absolute_url(value):
    if isinstance(value, dict):
        value = value.get("url") or value.get("thumbURL") or value.get("src") or ""
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


def strip_xhamster_suffix(title):
    title = clean_text(title)
    title = re.sub(r"\s*[-|]\s*xHamster.*$", "", title, flags=re.IGNORECASE)
    return normalize_space(title)


def slug_to_name(slug):
    return " ".join(part.capitalize() for part in re.split(r"[-_]+", slug or "") if part)


def normalize_scene_url(url):
    url = (url or "").strip()
    if not url:
        return ""
    url = re.sub(r"^https?://(?:www\.)?xhamster\.com", BASE_URL, url, flags=re.IGNORECASE)
    if re.match(r"^https?://", url, flags=re.IGNORECASE):
        return url
    if url.startswith("/"):
        return BASE_URL + url
    return BASE_URL + "/" + url.lstrip("/")


def normalize_performer_url(url):
    url = normalize_scene_url(url)
    if "/pornstars/" not in url:
        return url
    return url.rstrip("/")


def load_initials(html):
    marker = "window.initials="
    pos = html.find(marker)
    if pos == -1:
        return {}
    decoder = json.JSONDecoder()
    try:
        value, _ = decoder.raw_decode(html[pos + len(marker):])
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def parse_unix_date(value):
    try:
        return datetime.fromtimestamp(int(value), timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return ""


def normalize_gender(value):
    value = clean_text(value).lower()
    mapping = {
        "female": "Female",
        "male": "Male",
        "transgender": "Transgender",
        "shemale": "Transgender",
    }
    if not value:
        return ""
    return mapping.get(value, value.title())


def normalize_country(value):
    value = clean_text(value)
    if len(value) == 2 and value.isalpha():
        return value.upper()
    return value


def infer_gender_from_orientation(value):
    value = clean_text(value).lower()
    return {
        "straight": "Female",
        "gay": "Male",
        "shemale": "Transgender",
        "transgender": "Transgender",
    }.get(value, "")


def unique_named_dicts(values):
    seen = set()
    output = []
    for value in values:
        if not isinstance(value, dict):
            continue
        name = clean_text(value.get("name", ""))
        if not name:
            continue
        dedupe = name.casefold()
        if dedupe in seen:
            continue
        seen.add(dedupe)
        item = dict(value)
        item["name"] = name
        output.append({k: v for k, v in item.items() if v not in ("", [], None)})
    return output


def performer_from_model(model):
    slug = model.get("inurl") or model.get("slug") or ""
    alias_value = model.get("alias")
    aliases = []
    if isinstance(alias_value, list):
        aliases = [clean_text(item) for item in alias_value if clean_text(item)]
    elif alias_value:
        aliases = [clean_text(part) for part in re.split(r"\s*,\s*", str(alias_value)) if clean_text(part)]
    performer = {
        "name": clean_text(model.get("name", "")),
        "url": f"{BASE_URL}/pornstars/{slug}" if slug else clean_text(model.get("url", "")),
        "gender": normalize_gender(model.get("gender", "")),
        "country": normalize_country(model.get("country", "")),
        "image": absolute_url(model.get("thumb", "") or model.get("thumbUrl", "")),
        "aliases": aliases,
    }
    return {k: v for k, v in performer.items() if v not in ("", [], None)}


def parse_scene_performers(initials):
    performers = []
    seen = set()
    for model in initials.get("videoEntity", {}).get("pornstarModels", []):
        if not isinstance(model, dict):
            continue
        performer = performer_from_model(model)
        name = performer.get("name", "")
        if not name:
            continue
        seen.add(name.casefold())
        performers.append(performer)
    for tag in initials.get("videoTagsComponent", {}).get("tags", []):
        if not isinstance(tag, dict) or not tag.get("isPornstar"):
            continue
        name = clean_text(tag.get("name", ""))
        if not name or name.casefold() in seen:
            continue
        seen.add(name.casefold())
        performers.append(
            {
                "name": name,
                "url": clean_text(tag.get("url", "")),
                "gender": normalize_gender(tag.get("gender", "")),
                "country": normalize_country(tag.get("country", "")),
                "image": absolute_url(tag.get("thumbUrl", "")),
            }
        )
    return unique_named_dicts(performers)


def parse_scene_tags(initials):
    tags = []
    seen = set()
    for tag in initials.get("videoTagsComponent", {}).get("tags", []):
        if not isinstance(tag, dict):
            continue
        if tag.get("isPornstar"):
            continue
        if not (tag.get("isCategory") or tag.get("isTag")):
            continue
        name = clean_text(tag.get("name", ""))
        if not name or name.casefold() in seen:
            continue
        seen.add(name.casefold())
        tags.append({"name": name})
    return tags


def scene_from_initials(initials, url, html=""):
    video_model = initials.get("videoModel", {})
    video_entity = initials.get("videoEntity", {})
    if not video_model and not video_entity:
        return {}

    image = absolute_url(
        video_model.get("thumbURL", "") or video_entity.get("thumbBig", "")
    )
    if not image:
        thumbs = video_entity.get("thumbs", [])
        if isinstance(thumbs, list) and thumbs:
            first = thumbs[0]
            if isinstance(first, dict):
                image = absolute_url(first.get("url", "") or first.get("thumbURL", ""))
            elif isinstance(first, str):
                image = absolute_url(first)

    scene = {
        "title": strip_xhamster_suffix(
            clean_text(video_model.get("title", ""))
            or clean_text(video_entity.get("title", ""))
            or extract_meta(html, "property", "og:title")
        ),
        "url": normalize_scene_url(
            video_model.get("pageURL") or video_entity.get("pageURL") or url
        ),
        "date": parse_unix_date(video_model.get("created")),
        "details": clean_text(video_model.get("description", ""))
        or clean_text(video_entity.get("description", ""))
        or extract_meta(html, "property", "og:description"),
        "image": image,
        "performers": parse_scene_performers(initials),
        "tags": parse_scene_tags(initials),
    }
    studio_name = clean_text(video_model.get("channelModel", {}).get("channelName", ""))
    if studio_name:
        scene["studio"] = {"name": studio_name}
    return {k: v for k, v in scene.items() if v not in ("", [], None)}


def scrape_scene(url):
    url = normalize_scene_url(url)
    if not url:
        return {}
    html = fetch(url)
    if not html:
        return {}
    return scene_from_initials(load_initials(html), url, html)


def parse_search_results(html):
    items = load_initials(html).get("searchResult", {}).get("videoThumbProps", [])
    results = []
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        url = normalize_scene_url(item.get("pageURL", ""))
        title = clean_text(item.get("title", ""))
        if not url or not title or url.casefold() in seen:
            continue
        seen.add(url.casefold())
        result = {
            "title": title,
            "url": url,
            "date": parse_unix_date(item.get("created")),
            "image": absolute_url(item.get("thumbURL", "") or item.get("imageURL", "")),
        }
        landing_name = clean_text(item.get("landing", {}).get("name", ""))
        if landing_name:
            result["studio"] = {"name": landing_name}
        results.append({k: v for k, v in result.items() if v not in ("", [], None)})
    return results


def search_scenes(query):
    query = normalize_space(query)
    if not query:
        return []
    html = fetch(f"{BASE_URL}/search/{quote_plus(query)}")
    if not html:
        return []
    results = parse_search_results(html)
    results.sort(
        key=lambda item: (
            normalize_title(item.get("title", "")) != normalize_title(query),
            -similarity(item.get("title", ""), query),
            item.get("title", "").casefold(),
        )
    )
    return results


def extract_fragment_query(fragment):
    if isinstance(fragment, dict):
        direct = fragment.get("title") or fragment.get("name") or fragment.get("code")
        if direct:
            return normalize_fragment_text(direct)
        url = fragment.get("url", "")
        if isinstance(url, str) and "/videos/" in url:
            return normalize_scene_url(url)
        for file_info in fragment.get("files", []):
            if not isinstance(file_info, dict):
                continue
            basename = file_info.get("basename") or file_info.get("path") or ""
            if basename:
                return normalize_fragment_text(basename)
    elif isinstance(fragment, str):
        if "/videos/" in fragment:
            return normalize_scene_url(fragment)
        return normalize_fragment_text(fragment)
    return ""


def extract_id_hash_slug(value):
    normalized = normalize_fragment_text(value).lower()
    match = re.search(r"\b(xh[a-z0-9]{4,})\b", normalized)
    if match:
        return match.group(1)
    return ""


def score_fragment_match(result, query):
    url = result.get("url", "").lower()
    query_norm = normalize_fragment_text(query)
    query_lower = query_norm.lower()
    score = similarity(result.get("title", ""), query_norm)
    if query_lower and query_lower in url:
        score = max(score, 0.97)
    elif query_lower and query_lower.replace(" ", "-") in url:
        score = max(score, 0.92)
    tokens = [token for token in re.split(r"[^a-z0-9]+", query_lower) if len(token) >= 6]
    for token in tokens:
        if token in url:
            score = max(score, 0.95)
            break
    return score


def best_scene_match(query):
    results = search_scenes(query)
    if not results:
        return {}
    best = results[0]
    exact = normalize_title(best.get("title", "")) == normalize_title(query)
    if not exact and score_fragment_match(best, query) < 0.72:
        return {}
    return scrape_scene(best.get("url", ""))


def extract_avatar_from_html(html):
    match = re.search(
        r"landing-info__logo-image[^>]+style=\"[^\"]*background-image:\s*url\('([^']+)'",
        html,
        flags=re.IGNORECASE,
    )
    if match:
        return absolute_url(match.group(1))
    return extract_meta(html, "property", "og:image")


def extract_performer_aliases(html):
    match = re.search(
        r'landing-info__metric aliases[^>]*>.*?<p[^>]*>(.*?)</p>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return []
    aliases = strip_html(match.group(1))
    if not aliases:
        return []
    return [clean_text(part) for part in aliases.split(",") if clean_text(part)]


def extract_performer_name(html, url):
    match = re.search(
        r'<h2[^>]*class="[^"]*landing-info__user-title[^"]*"[^>]*>(.*?)</h2>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match:
        return strip_html(match.group(1))
    title = extract_meta(html, "property", "og:title")
    if title:
        return strip_xhamster_suffix(title)
    slug_match = re.search(r"/pornstars/([^/?#]+)", url)
    return slug_to_name(slug_match.group(1)) if slug_match else ""


def scrape_performer(url):
    url = normalize_performer_url(url)
    if not url:
        return {}
    html = fetch(url)
    if not html:
        return {}

    initials = load_initials(html)
    channel_info = initials.get("channelInfo", {})
    aliases = extract_performer_aliases(html)
    details = []
    if aliases:
        details.append("Aliases: " + ", ".join(aliases))

    country_match = re.search(
        r'pornstar-country[^>]+data-tooltip="([^"]+)"',
        html,
        flags=re.IGNORECASE,
    )
    country = clean_text(country_match.group(1)) if country_match else ""
    if country:
        details.append(f"Country: {country}")

    performer = {
        "name": extract_performer_name(html, url),
        "url": url,
        "gender": infer_gender_from_orientation(channel_info.get("orientation", "")),
        "image": extract_avatar_from_html(html),
        "aliases": aliases,
        "country": country,
        "details": " | ".join(details),
    }
    return {k: v for k, v in performer.items() if v not in ("", [], None)}


def handle_scene_by_fragment(fragment):
    query = extract_fragment_query(fragment)
    if not query:
        return {}
    if isinstance(query, str) and "/videos/" in query:
        return scrape_scene(query)
    id_hash_slug = extract_id_hash_slug(query)
    if id_hash_slug:
        direct = scrape_scene(f"{BASE_URL}/videos/{id_hash_slug}")
        if direct:
            return direct
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

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
