#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
SCRAPERS_DIR = ROOT / "scrapers"
REQUIRED_FILES = {
    "README.md",
    "SCRAPER_SPEC.json",
    "PERPLEXITY_TO_CODEX_HANDOFF.md",
    "CODEX_PROMPT.md",
}
REQUIRED_SPEC_KEYS = {
    "site_name",
    "site_url",
    "folder_name",
    "supported_hooks",
    "url_patterns",
    "metadata_mapping",
    "selectors_or_parsing_notes",
    "known_limitations",
    "validation_examples",
    "sources",
}


def main() -> int:
    if not SCRAPERS_DIR.exists():
        print("No scrapers directory found.")
        return 1

    errors: list[str] = []
    scraper_dirs = sorted(path for path in SCRAPERS_DIR.iterdir() if path.is_dir())
    if not scraper_dirs:
        errors.append("No scraper folders found under scrapers/.")

    for scraper_dir in scraper_dirs:
        names = {path.name for path in scraper_dir.iterdir() if path.is_file()}
        missing = sorted(REQUIRED_FILES - names)
        for name in missing:
            errors.append(f"{scraper_dir.name}: missing required file {name}")

        if not any(path.suffix == ".yml" for path in scraper_dir.iterdir() if path.is_file()):
            errors.append(f"{scraper_dir.name}: missing scraper .yml file")
        if not any(path.suffix == ".py" for path in scraper_dir.iterdir() if path.is_file()):
            errors.append(f"{scraper_dir.name}: missing scraper .py file")

        spec_path = scraper_dir / "SCRAPER_SPEC.json"
        if spec_path.exists():
            try:
                spec = json.loads(spec_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{scraper_dir.name}: invalid JSON in SCRAPER_SPEC.json: {exc}")
            else:
                missing_keys = sorted(REQUIRED_SPEC_KEYS - set(spec.keys()))
                for key in missing_keys:
                    errors.append(f"{scraper_dir.name}: SCRAPER_SPEC.json missing key {key}")

                folder_name = spec.get("folder_name")
                if folder_name and folder_name != scraper_dir.name:
                    errors.append(
                        f"{scraper_dir.name}: SCRAPER_SPEC.json folder_name "
                        f"does not match directory name"
                    )

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validation passed.")
    for scraper_dir in scraper_dirs:
        print(f"- {scraper_dir.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
