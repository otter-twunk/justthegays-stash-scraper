#!/usr/bin/env python3

import json
import sys


def emit(payload):
    json.dump(payload, sys.stdout, ensure_ascii=False)


def main():
    request = json.load(sys.stdin)
    mode = request.get("mode")
    # args = request.get("args", {})

    # Replace this stub with site-specific scraping logic.
    # Refer to SCRAPER_SPEC.json and PERPLEXITY_TO_CODEX_HANDOFF.md.
    if mode == "sceneByURL":
        emit({"results": []})
        return

    emit({"results": []})


if __name__ == "__main__":
    main()
