"""
GitHub API helpers for posting and replacing PR comments, and adding labels.
Uses only httpx + the GITHUB_TOKEN provided by GitHub Actions.
"""

from __future__ import annotations

import os
import httpx

GITHUB_API = "https://api.github.com"
_TOKEN = os.environ.get("GITHUB_TOKEN", "")
_HEADERS = {
    "Authorization": f"Bearer {_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def _get(url: str, **kwargs) -> httpx.Response:
    return httpx.get(url, headers=_HEADERS, timeout=30, **kwargs)


def _post(url: str, json: dict) -> httpx.Response:
    return httpx.post(url, headers=_HEADERS, json=json, timeout=30)


def _patch(url: str, json: dict) -> httpx.Response:
    return httpx.patch(url, headers=_HEADERS, json=json, timeout=30)


def get_pr_comments(repo: str, pr_number: int) -> list[dict]:
    """Fetch all issue comments on a PR (not review comments)."""
    comments: list[dict] = []
    page = 1
    while True:
        resp = _get(
            f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/comments",
            params={"per_page": 100, "page": page},
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        comments.extend(batch)
        page += 1
    return comments


def find_comment_with_marker(comments: list[dict], marker: str) -> dict | None:
    """Return the first comment whose body contains the given HTML marker."""
    for c in comments:
        if marker in c.get("body", ""):
            return c
    return None


def post_comment(repo: str, pr_number: int, body: str) -> dict:
    """Create a new issue comment on the PR."""
    resp = _post(
        f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/comments",
        json={"body": body},
    )
    resp.raise_for_status()
    return resp.json()


def update_comment(repo: str, comment_id: int, body: str) -> dict:
    """Edit an existing issue comment."""
    resp = _patch(
        f"{GITHUB_API}/repos/{repo}/issues/comments/{comment_id}",
        json={"body": body},
    )
    resp.raise_for_status()
    return resp.json()


def upsert_comment(repo: str, pr_number: int, marker: str, body: str) -> dict:
    """
    Post or replace a comment identified by an HTML marker.
    Idempotent: replaces the existing comment if found, else creates a new one.
    """
    comments = get_pr_comments(repo, pr_number)
    existing = find_comment_with_marker(comments, marker)
    if existing:
        return update_comment(repo, existing["id"], body)
    return post_comment(repo, pr_number, body)


def add_label(repo: str, pr_number: int, label: str) -> None:
    """Add a label to a PR (silently ignores errors if label doesn't exist)."""
    resp = _post(
        f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/labels",
        json={"labels": [label]},
    )
    # 404 / 422 are tolerated — label may not exist in the repo yet
    if resp.status_code not in (200, 201, 404, 422):
        resp.raise_for_status()


def get_pr_diff(repo: str, base_sha: str, head_sha: str) -> str:
    """Fetch the unified diff for the PR via the compare API."""
    resp = httpx.get(
        f"{GITHUB_API}/repos/{repo}/compare/{base_sha}...{head_sha}",
        headers={**_HEADERS, "Accept": "application/vnd.github.v3.diff"},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.text


def get_changed_files(repo: str, base_sha: str, head_sha: str) -> list[str]:
    """Return list of filenames changed in the PR."""
    resp = _get(
        f"{GITHUB_API}/repos/{repo}/compare/{base_sha}...{head_sha}",
        params={"per_page": 300},
    )
    resp.raise_for_status()
    data = resp.json()
    return [f["filename"] for f in data.get("files", [])]
