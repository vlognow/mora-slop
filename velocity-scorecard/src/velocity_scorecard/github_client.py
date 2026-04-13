"""GitHub API client for the velocity scorecard.

Fetches merged PRs, diffs, file lists, and review data for a given repo.
Uses requests directly with rate-limit awareness and token fallback.
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.github.com"
DIFF_TRUNCATE_CHARS = 15_000


def _resolve_token() -> str:
    """Return a GitHub PAT from env or ~/.claude.json fallback."""
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token

    claude_cfg = Path.home() / ".claude.json"
    if claude_cfg.exists():
        try:
            data = json.loads(claude_cfg.read_text())
            token = (
                data.get("mcpServers", {})
                .get("github", {})
                .get("env", {})
                .get("GITHUB_PERSONAL_ACCESS_TOKEN")
            )
            if token:
                return token
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("Failed to parse token from ~/.claude.json: %s", exc)

    raise RuntimeError(
        "No GitHub token found. Set GITHUB_TOKEN or configure "
        "mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN in ~/.claude.json"
    )


class GitHubClient:
    """Thin wrapper around the GitHub REST API for velocity scorecard data."""

    def __init__(
        self,
        owner: str,
        repo: str,
        token: str | None = None,
    ) -> None:
        self.owner = owner
        self.repo = repo
        self.token = token or _resolve_token()
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        """Issue a request, respecting rate limits and raising on errors."""
        url = f"{BASE_URL}{path}"
        resp = self._session.request(method, url, params=params, headers=headers)

        # Rate-limit guard
        remaining = resp.headers.get("X-RateLimit-Remaining")
        reset_ts = resp.headers.get("X-RateLimit-Reset")
        if remaining is not None and int(remaining) < 10:
            wait = max(int(reset_ts or 0) - int(time.time()), 1)
            logger.warning(
                "Rate limit nearly exhausted (%s remaining). Sleeping %ds.",
                remaining,
                wait,
            )
            time.sleep(wait)

        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            wait = max(int(reset_ts or 0) - int(time.time()), 60)
            logger.error("Rate-limited. Sleeping %ds before retry.", wait)
            time.sleep(wait)
            return self._request(method, path, params=params, headers=headers)

        resp.raise_for_status()
        return resp

    def _get_json(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        return self._request("GET", path, params=params).json()

    def _paginate(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        max_pages: int = 20,
    ) -> list[Any]:
        """Follow Link-header pagination, collecting all items."""
        params = dict(params or {})
        params.setdefault("per_page", 100)

        items: list[Any] = []
        page = 0
        url = f"{BASE_URL}{path}"

        while url and page < max_pages:
            resp = self._request("GET", url.replace(BASE_URL, ""), params=params if page == 0 else None)
            data = resp.json()
            if isinstance(data, list):
                items.extend(data)
            elif isinstance(data, dict) and "items" in data:
                items.extend(data["items"])
            else:
                items.append(data)

            # Follow next page via Link header
            link = resp.headers.get("Link", "")
            url = None
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.split(";")[0].strip().strip("<>")
                    break
            page += 1

        return items

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def fetch_merged_prs(self, weeks: int = 2) -> list[dict]:
        """Fetch PRs merged in the last *weeks* weeks, enriched with review data.

        Returns a list of dicts, each containing:
            number, title, body, created_at, merged_at, user, labels,
            additions, deletions, changed_files, review_comments, reviews
        """
        since = (datetime.now(timezone.utc) - timedelta(weeks=weeks)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        query = (
            f"repo:{self.owner}/{self.repo} is:pr is:merged merged:>={since}"
        )
        logger.info("Searching merged PRs since %s", since)

        raw = self._paginate(
            "/search/issues",
            params={"q": query, "sort": "updated", "order": "desc"},
        )
        logger.info("Search returned %d PRs", len(raw))

        results: list[dict] = []
        for item in raw:
            pr_number: int = item["number"]
            try:
                pr_detail = self._get_json(
                    f"/repos/{self.owner}/{self.repo}/pulls/{pr_number}"
                )
                reviews = self._paginate(
                    f"/repos/{self.owner}/{self.repo}/pulls/{pr_number}/reviews"
                )
            except requests.HTTPError as exc:
                logger.warning("Failed to fetch details for PR #%d: %s", pr_number, exc)
                continue

            results.append(
                {
                    "number": pr_number,
                    "title": pr_detail.get("title", ""),
                    "body": pr_detail.get("body") or "",
                    "created_at": pr_detail.get("created_at"),
                    "merged_at": pr_detail.get("merged_at"),
                    "user": (pr_detail.get("user") or {}).get("login", "unknown"),
                    "labels": [
                        lbl["name"] for lbl in pr_detail.get("labels", [])
                    ],
                    "additions": pr_detail.get("additions", 0),
                    "deletions": pr_detail.get("deletions", 0),
                    "changed_files": pr_detail.get("changed_files", 0),
                    "review_comments": pr_detail.get("review_comments", 0),
                    "reviews": [
                        {
                            "state": r.get("state"),
                            "submitted_at": r.get("submitted_at"),
                        }
                        for r in reviews
                    ],
                }
            )

        logger.info("Returning %d enriched PRs", len(results))
        return results

    def fetch_pr_diff(self, pr_number: int) -> str:
        """Fetch the raw unified diff for a PR, truncated to fit LLM context."""
        resp = self._request(
            "GET",
            f"/repos/{self.owner}/{self.repo}/pulls/{pr_number}",
            headers={"Accept": "application/vnd.github.v3.diff"},
        )
        diff_text = resp.text
        if len(diff_text) > DIFF_TRUNCATE_CHARS:
            logger.info(
                "PR #%d diff truncated from %d to %d chars",
                pr_number,
                len(diff_text),
                DIFF_TRUNCATE_CHARS,
            )
            diff_text = diff_text[:DIFF_TRUNCATE_CHARS] + "\n\n... [truncated]"
        return diff_text

    def fetch_pr_files(self, pr_number: int) -> list[dict]:
        """Fetch the list of files changed in a PR.

        Returns dicts with: filename, status, additions, deletions, patch.
        """
        raw = self._paginate(
            f"/repos/{self.owner}/{self.repo}/pulls/{pr_number}/files"
        )
        return [
            {
                "filename": f.get("filename", ""),
                "status": f.get("status", ""),
                "additions": f.get("additions", 0),
                "deletions": f.get("deletions", 0),
                "patch": f.get("patch", ""),
            }
            for f in raw
        ]
