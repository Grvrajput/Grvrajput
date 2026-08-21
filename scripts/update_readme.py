#!/usr/bin/env python3
"""Update AUTO-marked blocks in the profile README.

Fills:
  - AUTO:DATE  -> "Profile last updated: <DD Mon YYYY>"
  - AUTO:STATS -> public repo count + follower count

Reads GH_TOKEN from the environment (the GitHub Actions built-in token is fine).
No third-party dependencies; uses only the standard library.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

USER = "Grvrajput"
README = "README.md"
API = f"https://api.github.com/users/{USER}"


def fetch_user() -> dict:
    req = urllib.request.Request(API, headers={"Accept": "application/vnd.github+json", "User-Agent": USER})
    token = os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def replace_block(text: str, name: str, body: str) -> str:
    start, end = f"<!-- AUTO:{name}:START -->", f"<!-- AUTO:{name}:END -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    replacement = f"{start}\n{body}\n{end}"
    if not pattern.search(text):
        print(f"warning: markers for {name} not found; skipping", file=sys.stderr)
        return text
    return pattern.sub(replacement, text)


def main() -> int:
    with open(README, "r", encoding="utf-8") as fh:
        text = fh.read()

    today = datetime.now(timezone.utc).strftime("%d %b %Y")
    date_body = f"_Profile last updated: {today}_"
    text = replace_block(text, "DATE", date_body)

    try:
        data = fetch_user()
        repos = data.get("public_repos", 0)
        followers = data.get("followers", 0)
        stats_body = f"<sub>{repos} public repositories · {followers} followers</sub>"
        text = replace_block(text, "STATS", stats_body)
    except Exception as exc:  # noqa: BLE001 - best effort, never fail the run
        print(f"warning: could not fetch stats: {exc}", file=sys.stderr)

    with open(README, "w", encoding="utf-8") as fh:
        fh.write(text)

    print(f"README updated ({today})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
