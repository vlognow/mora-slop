"""Quantitative metrics computed from GitHub PR data."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from statistics import median


def _parse_dt(s: str | None) -> datetime | None:
    """Parse an ISO-8601 datetime string, returning timezone-aware UTC."""
    if not s:
        return None
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


# Regex to detect AI-assisted PRs via co-author lines, bot names, or labels
_AI_MARKERS = re.compile(
    r"co-authored-by:\s*claude|cursor_agent|claude|copilot|ai[\s\-_]generated",
    re.IGNORECASE,
)


class MetricsCalculator:
    """Computes throughput, cycle time, quality, and collaboration metrics."""

    def compute(self, prs: list[dict]) -> dict:
        """Return throughput, cycle time, quality, and collaboration metrics for a set of PRs."""
        merged = [p for p in prs if p.get("merged_at")]
        return {
            "throughput": self._throughput(merged),
            "cycle_time": self._cycle_time(merged),
            "quality": self._quality(merged),
            "collaboration": self._collaboration(prs),
        }

    # ------------------------------------------------------------------
    # Throughput
    # ------------------------------------------------------------------

    @staticmethod
    def _throughput(merged: list[dict]) -> dict:
        """Count merged PRs and average line churn."""
        n = len(merged)
        additions = [p.get("additions", 0) for p in merged]
        deletions = [p.get("deletions", 0) for p in merged]
        return {
            "prs_merged": n,
            "avg_additions": sum(additions) / n if n else 0.0,
            "avg_deletions": sum(deletions) / n if n else 0.0,
        }

    # ------------------------------------------------------------------
    # Cycle time
    # ------------------------------------------------------------------

    @staticmethod
    def _cycle_time(merged: list[dict]) -> dict:
        """Compute median/p90 cycle time and first-review latency in hours."""
        cycle_hours: list[float] = []
        review_hours: list[float] = []

        for pr in merged:
            created = _parse_dt(pr.get("created_at"))
            merged_at = _parse_dt(pr.get("merged_at"))
            if created and merged_at:
                cycle_hours.append((merged_at - created).total_seconds() / 3600)

            # First review latency — find earliest submitted_at among reviews
            reviews = pr.get("reviews") or []
            submitted_times = [
                _parse_dt(r.get("submitted_at"))
                for r in reviews
                if _parse_dt(r.get("submitted_at"))
            ]
            if created and submitted_times:
                first_review = min(submitted_times)
                review_hours.append((first_review - created).total_seconds() / 3600)

        def _percentile(data: list[float], pct: float) -> float:
            """Linear interpolation percentile (matches numpy's default method)."""
            if not data:
                return 0.0
            s = sorted(data)
            k = (len(s) - 1) * pct
            f = int(k)
            c = f + 1 if f + 1 < len(s) else f
            return s[f] + (k - f) * (s[c] - s[f])

        return {
            "median_hours": median(cycle_hours) if cycle_hours else 0.0,
            "p90_hours": _percentile(cycle_hours, 0.90),
            "first_review_median_hours": median(review_hours) if review_hours else 0.0,
        }

    # ------------------------------------------------------------------
    # Quality — rework rate approximated by file overlap within 14 days
    # ------------------------------------------------------------------

    @staticmethod
    def _quality(merged: list[dict]) -> dict:
        """Estimate rework rate via file-overlap within 14 days, plus review comment density."""
        n = len(merged)
        if n == 0:
            return {"rework_rate": 0.0, "avg_review_comments": 0.0}

        # Build a timeline of (merged_at, changed_files) for overlap detection.
        # changed_files can be an int (count) or a list of filenames.
        # We need filenames for overlap; fall back to labels/title heuristic if absent.
        timeline: list[tuple[datetime, set[str]]] = []
        for pr in merged:
            merged_at = _parse_dt(pr.get("merged_at"))
            files = pr.get("changed_files")
            if isinstance(files, list):
                file_set = set(files)
            elif isinstance(files, dict):
                # Some API shapes return {filename: ...}
                file_set = set(files.keys())
            else:
                # Numeric or absent — no file-level overlap possible
                file_set = set()
            if merged_at:
                timeline.append((merged_at, file_set))

        # Sort by merge time
        timeline.sort(key=lambda t: t[0])

        # Count PRs that touch the same files as another PR merged within 14 days.
        # This is a proxy for rework — re-touching recently changed code.
        rework_count = 0
        for i, (merged_at_i, files_i) in enumerate(timeline):
            if not files_i:
                continue
            window_start = merged_at_i - timedelta(days=14)
            for j in range(i):
                merged_at_j, files_j = timeline[j]
                if merged_at_j < window_start:
                    continue
                if files_i & files_j:
                    rework_count += 1
                    break  # Only count this PR once

        total_comments = sum(pr.get("review_comments", 0) for pr in merged)

        return {
            "rework_rate": rework_count / n if n else 0.0,
            "avg_review_comments": total_comments / n if n else 0.0,
        }

    # ------------------------------------------------------------------
    # Collaboration — AI adoption + review load
    # ------------------------------------------------------------------

    @staticmethod
    def _collaboration(prs: list[dict]) -> dict:
        """Detect AI-authored PRs and compute average review count per PR."""
        n = len(prs)
        ai_count = 0
        total_reviews = 0

        for pr in prs:
            # Check body, title, and labels for AI markers
            body = pr.get("body") or ""
            title = pr.get("title") or ""
            labels = pr.get("labels") or []
            label_text = " ".join(
                (l.get("name", "") if isinstance(l, dict) else str(l)) for l in labels
            )
            search_text = f"{body} {title} {label_text}"
            if _AI_MARKERS.search(search_text):
                ai_count += 1

            reviews = pr.get("reviews") or []
            total_reviews += len(reviews)

        return {
            "ai_pr_count": ai_count,
            "ai_pr_ratio": ai_count / n if n else 0.0,
            "avg_reviews_per_pr": total_reviews / n if n else 0.0,
        }
