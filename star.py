"""
Update star counts in markdown files.
Author: xiejiahe
@example python3 star.py README_zh-CN.md
"""
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from urllib.parse import urlparse

GITHUB_URL_HOSTS = {"github.com", "www.github.com"}
LINK_REGEX = re.compile(r'\[.+?\]\(([^)]+)\)', re.IGNORECASE)
STAR_REGEX = re.compile(r'★\s*([\d,]+)')
REPO_PATH_REGEX = re.compile(r'^/([^/]+)/([^/]+)(?:/.*)?$')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update GitHub star counts in a markdown file.")
    parser.add_argument("path", nargs="?", default="README.md", help="Markdown file to update.")
    parser.add_argument("--token", "-t", default=os.getenv("GITHUB_ACCESS_TOKEN"), help="GitHub access token.")
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes to disk.")
    return parser.parse_args()


def get_github_repo_path(url: str) -> Optional[str]:
    parsed = urlparse(url.strip())
    if parsed.hostname not in GITHUB_URL_HOSTS:
        return None
    match = REPO_PATH_REGEX.match(parsed.path)
    if not match:
        return None
    owner, repo = match.groups()
    return f"/{owner}/{repo.rstrip('/')}"


def get_star_count(session: requests.Session, repo_path: str, token: Optional[str] = None) -> Optional[int]:
    api_url = f"https://api.github.com/repos{repo_path}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    print(f"Fetching {api_url}")
    resp = session.get(api_url, headers=headers, timeout=10)
    if resp.status_code == 200:
        return resp.json().get("stargazers_count")

    print(f"Failed to fetch {api_url}: {resp.status_code} {resp.reason}")
    return None


def update_star_text(line: str, star_count: int) -> str:
    if STAR_REGEX.search(line):
        return STAR_REGEX.sub(f"★ {star_count}", line)
    return line


def sort_secondary_list_lines(lines: List[str]) -> List[str]:
    sorted_lines: List[str] = []
    current_group: List[Tuple[int, str]] = []

    for line in lines:
        if line.startswith("  - "):
            star = 0
            match = STAR_REGEX.search(line)
            if match:
                try:
                    star = int(match.group(1).replace(",", ""))
                except ValueError:
                    star = 0
            current_group.append((star, line))
            continue

        if current_group:
            current_group.sort(key=lambda item: item[0], reverse=True)
            sorted_lines.extend(item[1] for item in current_group)
            current_group = []

        sorted_lines.append(line)

    if current_group:
        current_group.sort(key=lambda item: item[0], reverse=True)
        sorted_lines.extend(item[1] for item in current_group)

    return sorted_lines


def process_file(path: Path, token: Optional[str], dry_run: bool = False) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    updated_lines: List[str] = []
    star_cache: Dict[str, Optional[int]] = {}

    with requests.Session() as session:
        for line in lines:
            link_match = LINK_REGEX.search(line)
            if not link_match:
                updated_lines.append(line)
                continue

            github_url = link_match.group(1)
            repo_path = get_github_repo_path(github_url)
            if not repo_path:
                updated_lines.append(line)
                continue

            if repo_path not in star_cache:
                star_cache[repo_path] = get_star_count(session, repo_path, token=token)

            star_count = star_cache[repo_path]
            if star_count is not None:
                line = update_star_text(line, star_count)

            updated_lines.append(line)

    sorted_lines = sort_secondary_list_lines(updated_lines)

    if dry_run:
        print("Dry run complete. No file changes were written.")
        return

    path.write_text("".join(sorted_lines), encoding="utf-8")
    print(f"\nFinished updating {path}")


def main() -> None:
    args = parse_args()
    path = Path(args.path)
    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {path}")
    process_file(path, token=args.token, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
