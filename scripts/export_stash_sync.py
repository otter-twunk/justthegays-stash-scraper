#!/usr/bin/env python3

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
SCRAPERS_DIR = ROOT / "scrapers"
EXPORT_DIR = ROOT / "build" / "stash-sync"
MANIFEST_PATH = EXPORT_DIR / "manifest.json"
VALIDATION_SCRIPT = ROOT / "scripts" / "validate_scraper_repo.py"


def run_validation() -> None:
    completed = subprocess.run([sys.executable, str(VALIDATION_SCRIPT)], cwd=ROOT)
    if completed.returncode != 0:
        raise RuntimeError("Validation failed. Fix errors before exporting stash sync files.")


def git_revision() -> str:
    completed = subprocess.run(
        ["git", "--no-pager", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return "unknown"
    return completed.stdout.strip() or "unknown"


def primary_file(scraper_dir: Path, suffix: str) -> Path:
    matches = sorted(path for path in scraper_dir.iterdir() if path.is_file() and path.suffix == suffix)
    if len(matches) != 1:
        raise RuntimeError(
            f"{scraper_dir.name}: expected exactly one {suffix} file after validation, found {len(matches)}"
        )
    return matches[0]


def export_scrapers() -> list[dict[str, str]]:
    if EXPORT_DIR.exists():
        shutil.rmtree(EXPORT_DIR)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict[str, str]] = []

    for scraper_dir in sorted(path for path in SCRAPERS_DIR.iterdir() if path.is_dir()):
        yml_file = primary_file(scraper_dir, ".yml")
        py_file = primary_file(scraper_dir, ".py")
        target_yml = EXPORT_DIR / yml_file.name
        target_py = EXPORT_DIR / py_file.name

        if target_yml.exists():
            raise RuntimeError(f"Duplicate export filename detected: {target_yml.name}")
        if target_py.exists():
            raise RuntimeError(f"Duplicate export filename detected: {target_py.name}")

        shutil.copy2(yml_file, target_yml)
        shutil.copy2(py_file, target_py)

        manifest_rows.append(
            {
                "site": scraper_dir.name,
                "source_dir": str(scraper_dir.relative_to(ROOT)),
                "yml_file": str(target_yml.relative_to(ROOT)),
                "py_file": str(target_py.relative_to(ROOT)),
            }
        )

    return manifest_rows


def write_manifest(entries: list[dict[str, str]]) -> None:
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "generated_from_revision": git_revision(),
        "export_root": str(EXPORT_DIR.relative_to(ROOT)),
        "scrapers": entries,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    try:
        run_validation()
        manifest_entries = export_scrapers()
        write_manifest(manifest_entries)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Exported {len(manifest_entries)} scraper file pairs to {EXPORT_DIR}")
    print(f"Wrote manifest: {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
