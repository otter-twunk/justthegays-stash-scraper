#!/usr/bin/env python3
"""Unified CLI runner for repository scrapers."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRAPERS_ROOT = REPO_ROOT / "scrapers"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a scraper with standardized JSON output")
    parser.add_argument("--site", required=True, help="Scraper folder under scrapers/")
    parser.add_argument("--mode", required=True, help="Scraper mode (sceneByURL, sceneByName, etc.)")
    parser.add_argument("--url", default="", help="URL argument when needed")
    parser.add_argument("--name", default="", help="Name/query argument when needed")
    parser.add_argument("--input-json", default="", help="Raw JSON payload to pass to the scraper")
    parser.add_argument("--raw", action="store_true", help="Print scraper raw output without normalization")
    return parser.parse_args()


def find_scraper_script(site: str) -> Path:
    folder = SCRAPERS_ROOT / site
    if not folder.is_dir():
        raise FileNotFoundError(f"Unknown scraper site: {site}")

    scripts = sorted(
        path
        for path in folder.glob("*.py")
        # Allow optional folder-local helper launchers while keeping the main scraper script.
        if "_vendor" not in path.parts and path.name != "run.py"
    )
    if not scripts:
        raise FileNotFoundError(f"No scraper Python script found for site: {site}")
    return scripts[0]


def scraper_interface_hint(script_path: Path) -> str:
    source = script_path.read_text(encoding="utf-8", errors="replace")
    return "argv" if "sys.argv[1]" in source else "stdin"


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.input_json:
        parsed_input = json.loads(args.input_json)
        if not isinstance(parsed_input, dict):
            raise ValueError("--input-json must decode to a JSON object")
        return parsed_input

    payload: dict[str, Any] = {}
    if args.url:
        payload["url"] = args.url
    if args.name:
        payload["name"] = args.name
    return payload


def normalize_output(parsed: Any) -> dict[str, Any]:
    if isinstance(parsed, dict) and isinstance(parsed.get("results"), list):
        return {"results": parsed["results"]}
    if isinstance(parsed, list):
        return {"results": [item for item in parsed if isinstance(item, dict)]}
    if isinstance(parsed, dict):
        return {"results": [parsed] if parsed else []}
    return {"results": []}


def run_scraper(script_path: Path, interface: str, mode: str, payload: dict[str, Any]) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(script_path)]

    if interface == "argv":
        command.append(mode)
        stdin_payload = payload
    else:
        stdin_payload = {"mode": mode, "args": payload}

    return subprocess.run(
        command,
        input=json.dumps(stdin_payload),
        text=True,
        capture_output=True,
        check=False,
        cwd=str(REPO_ROOT),
    )


def run_with_fallback(script_path: Path, mode: str, payload: dict[str, Any]) -> subprocess.CompletedProcess[str]:
    first = scraper_interface_hint(script_path)
    second = "stdin" if first == "argv" else "argv"

    primary = run_scraper(script_path, first, mode, payload)
    if primary.returncode == 0:
        return primary
    return run_scraper(script_path, second, mode, payload)


def print_error(message: str, *, returncode: int = 1) -> int:
    json.dump({"results": [], "error": message}, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return returncode


def main() -> int:
    args = parse_args()

    try:
        script_path = find_scraper_script(args.site)
        payload = build_payload(args)
    except Exception as exc:
        return print_error(str(exc))

    completed = run_with_fallback(script_path, args.mode, payload)

    if completed.returncode != 0:
        stderr = (completed.stderr or "").strip() or "Scraper process failed"
        return print_error(stderr, returncode=completed.returncode)

    raw_stdout = (completed.stdout or "").strip()
    if not raw_stdout:
        return print_error("Scraper produced no output")

    try:
        parsed = json.loads(raw_stdout)
    except json.JSONDecodeError as exc:
        return print_error(f"Scraper returned invalid JSON: {exc}")

    output = parsed if args.raw else normalize_output(parsed)
    json.dump(output, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
