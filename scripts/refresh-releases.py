#!/usr/bin/env python3
"""Refresh the latest-release table in README.md."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
OWNER = "benyamin-git"
PROJECTS = [
    ("ClyTrade", "ClyTrade"),
    ("Kumiho", "Kumiho"),
    ("poker.pot", "poker.pot"),
    ("ORBYN", "ORBYN"),
]
START = "<!-- releases:start -->"
END = "<!-- releases:end -->"


def api(url: str) -> list[dict]:
    request = urllib.request.Request(url)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("User-Agent", "benyamin-git-profile-readme")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def latest_release(repo: str) -> dict | None:
    releases = api(f"https://api.github.com/repos/{OWNER}/{repo}/releases?per_page=10")
    for release in releases:
        if not release.get("draft"):
            return release
    return None


def row(name: str, repo: str, release: dict | None) -> str:
    url = f"https://github.com/{OWNER}/{repo}"
    if release is None:
        return f"| [{name}]({url}) | no release yet | — |"
    tag = release["tag_name"]
    link = release["html_url"]
    date = (release.get("published_at") or release.get("created_at") or "")[:10]
    return f"| [{name}]({url}) | [{tag}]({link}) | {date} |"


def main() -> int:
    rows = ["| Project | Latest release | Published |", "| --- | --- | --- |"]
    for name, repo in PROJECTS:
        rows.append(row(name, repo, latest_release(repo)))

    table = "\n".join(rows)
    text = README.read_text()
    pattern = re.compile(
        rf"({re.escape(START)}\n).*?(\n{re.escape(END)})",
        re.DOTALL,
    )
    if not pattern.search(text):
        print(f"missing {START} / {END} markers in {README}", file=sys.stderr)
        return 1

    updated = pattern.sub(lambda match: f"{match.group(1)}{table}{match.group(2)}", text)
    if updated == text:
        print("release table already current")
        return 0

    README.write_text(updated)
    print("updated release table")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
