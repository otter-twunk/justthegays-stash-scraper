import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "scripts" / "run_scraper.py"
SCRAPERS_DIR = REPO_ROOT / "scrapers"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RUNNER), *args],
        text=True,
        capture_output=True,
        cwd=str(REPO_ROOT),
        check=False,
    )


def first_site_for_interface(interface: str) -> str:
    for folder in sorted(path for path in SCRAPERS_DIR.iterdir() if path.is_dir()):
        scripts = sorted(path for path in folder.glob("*.py") if "_vendor" not in path.parts)
        if not scripts:
            continue
        source = scripts[0].read_text(encoding="utf-8", errors="replace")
        detected = "argv" if "sys.argv[1]" in source else "stdin"
        if detected == interface:
            return folder.name
    raise AssertionError(f"No scraper found for interface: {interface}")


def test_unknown_site_returns_structured_error() -> None:
    result = run_cli("--site", "missing-site", "--mode", "sceneByName")
    assert result.returncode != 0
    payload = json.loads(result.stdout)
    assert payload["results"] == []
    assert payload["error"]


def test_runner_normalizes_argv_scraper_output() -> None:
    site = first_site_for_interface("argv")
    result = run_cli("--site", site, "--mode", "unsupportedMode")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload == {"results": []}


def test_runner_normalizes_stdin_scraper_output() -> None:
    site = first_site_for_interface("stdin")
    result = run_cli("--site", site, "--mode", "unsupportedMode")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload == {"results": []}


def test_all_scrapers_support_cli_smoke() -> None:
    sites = sorted(path.name for path in SCRAPERS_DIR.iterdir() if path.is_dir())
    for site in sites:
        result = run_cli("--site", site, "--mode", "sceneByName")
        assert result.returncode == 0, f"site={site} stderr={result.stderr}"
        payload = json.loads(result.stdout)
        assert "results" in payload and isinstance(payload["results"], list), site
