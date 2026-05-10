#!/bin/sh

set -eu

if [ "$#" -ne 1 ]; then
  echo "Usage: scripts/create_scraper_from_template.sh <site-folder>" >&2
  exit 1
fi

folder_name="$1"
repo_root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
template_dir="$repo_root/templates/site-template"
target_dir="$repo_root/scrapers/$folder_name"

if [ -e "$target_dir" ]; then
  echo "Target already exists: $target_dir" >&2
  exit 1
fi

mkdir -p "$repo_root/scrapers"
cp -R "$template_dir" "$target_dir"

echo "Created $target_dir"
echo "Next steps:"
echo "1. Fill in SCRAPER_SPEC.json"
echo "2. Update PERPLEXITY_TO_CODEX_HANDOFF.md"
echo "3. Update CODEX_PROMPT.md"
echo "4. Rename SiteScraper.py and SiteScraper.yml when implementation starts"
