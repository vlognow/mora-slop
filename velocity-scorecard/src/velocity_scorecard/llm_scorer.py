"""LLM-based PR scoring for the velocity scorecard.

Uses Claude to evaluate pull requests on technical difficulty, business value,
code quality, and whether the PR qualifies as a Significant Repo Advancement Unit (SRAU).
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

import anthropic
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

SCORING_PROMPT = """\
You are an expert engineering manager scoring a pull request for a velocity scorecard.

Evaluate the PR on four axes and classify whether it qualifies as a Significant Repo Advancement Unit (SRAU).

## Scoring axes (each 1–10, floats allowed)

### technical_difficulty
Based on:
- Algorithmic complexity (novel algorithms, non-trivial data structures)
- Cross-module / cross-service impact (how many boundaries does this change cross?)
- Concurrency, distributed-systems, or correctness concerns
- Domain-specific difficulty (crypto, compilers, ML pipelines, healthcare data, etc.)
- Size alone is NOT difficulty — a 2000-line migration can be a 3; a 40-line lock-free queue can be a 9.

### business_value
Based on:
- PR title, description, and any linked issues or context
- Is this a user-facing feature, a critical bugfix, a refactor that unblocks future work, or pure maintenance?
- Features and critical bugfixes score higher. Dependency bumps and formatting score lower.
- Consider second-order value: does this unblock other high-value work?

### code_quality
Based on the diff itself:
- Is the code clean, well-structured, and idiomatic for the language?
- Are there tests? Do the tests cover meaningful cases (not just happy path)?
- Are edge cases handled? Is error handling thoughtful?
- Is the change well-scoped — does it do one thing well, or is it a grab-bag?

### SRAU classification
A Significant Repo Advancement Unit is a change that **compounds** — the repo is meaningfully better for having it, and the benefit grows over time. Examples:
- Cross-cutting refactor that simplifies future development
- End-to-end feature that delivers real user value
- Architectural guardrail (linting rule, type safety, schema validation) that prevents future bugs
- New abstraction that collapses repeated patterns

NOT an SRAU:
- Typo fix, README tweak, config change
- Dependency bump (unless it unblocks something significant)
- One-off script, throwaway experiment
- Pure formatting / style changes

## Calibration guidance
Be honest. Most PRs land in the 4–6 range. That is fine and expected.
- 1–3: Trivial — config tweak, typo, dependency bump, small one-liner fix
- 4–6: Solid, competent work — the bread and butter of engineering
- 7–8: Impressive — meaningful complexity, high impact, or exceptionally clean code
- 9–10: Exceptional — reserve for genuinely outstanding work that you'd highlight in a team review

## Output format
Return ONLY valid JSON (no markdown fences, no commentary). Schema:

{
  "technical_difficulty": <float 1-10>,
  "business_value": <float 1-10>,
  "code_quality": <float 1-10>,
  "is_srau": <bool>,
  "srau_reasoning": "<one sentence explaining why or why not>",
  "summary": "<one sentence summary of what this PR does>"
}
"""

CALIBRATION_PROMPT = """\
You are an expert engineering manager reviewing a batch of PR scores for a velocity scorecard.

Below is a JSON array of scored PRs from the same time period. Each entry has:
- pr_number, title, summary
- technical_difficulty, business_value, code_quality (each 1–10)
- is_srau, srau_reasoning

Your job is to **calibrate** these scores as a cohort:

1. **Relative consistency**: If PR #42 (a config tweak) scored higher on technical_difficulty than PR #87 (a distributed consensus change), fix it.
2. **Distribution shape**: Most PRs should be 4–6. If everything is 7+, deflate. If everything is 2–3, inflate. The cohort should look like a real team's output.
3. **SRAU sanity check**: A typical team produces 2–5 SRAUs per sprint. If you see 15 out of 20 PRs marked SRAU, recalibrate.
4. **Preserve ordering**: Your main job is adjusting magnitudes and fixing outliers, not reranking. If the relative order was correct, keep it.

Return ONLY a valid JSON array with the same structure as the input, with adjusted scores. Every entry must include all original fields plus any adjusted score fields. Do not add commentary outside the JSON.
"""


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------


class LLMScorer:
    """Scores pull requests using Claude."""

    def __init__(
        self,
        client: anthropic.Anthropic | None = None,
        model: str = "claude-sonnet-4-20250514",
        max_retries: int = 3,
    ):
        self.client = client or anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )
        self.model = model
        self.max_retries = max_retries

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def score_pr(
        self,
        pr: dict[str, Any],
        diff: str,
        files: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Score a single PR. Returns the scoring dict."""

        user_message = self._build_scoring_message(pr, diff, files)
        raw = self._call_api(
            system=SCORING_PROMPT,
            user_message=user_message,
        )
        scores = self._parse_json(raw)
        # Attach PR metadata for downstream use
        scores["pr_number"] = pr.get("number")
        scores["title"] = pr.get("title")
        return scores

    def calibrate(self, scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Calibration pass across a cohort of scored PRs.

        Sends all scores to Claude to adjust outliers and normalize the
        distribution. Returns the adjusted list.
        """
        if not scores:
            return scores

        # Strip large fields to keep calibration payload manageable
        slim_scores = [
            {k: v for k, v in s.items() if k not in ("diff", "files", "body")}
            for s in scores
        ]
        user_message = json.dumps(slim_scores, indent=2)
        try:
            raw = self._call_api(
                system=CALIBRATION_PROMPT,
                user_message=user_message,
                max_tokens=8192,
            )
            calibrated = self._parse_json(raw)
            if not isinstance(calibrated, list):
                log.warning("Calibration returned non-list; returning original scores")
                return scores
            # Merge calibrated values back onto originals (preserve metadata)
            by_pr = {s.get("pr_number"): s for s in scores}
            for cal in calibrated:
                pr_num = cal.get("pr_number")
                if pr_num in by_pr:
                    for key in ("technical_difficulty", "business_value", "code_quality", "is_srau"):
                        if key in cal:
                            by_pr[pr_num][key] = cal[key]
            return list(by_pr.values())
        except (ValueError, RuntimeError) as e:
            log.warning("Calibration failed (%s); returning uncalibrated scores", e)
            return scores

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _build_scoring_message(
        self,
        pr: dict[str, Any],
        diff: str,
        files: list[dict[str, Any]],
    ) -> str:
        """Assemble the user message with PR metadata, file list, and diff."""

        file_summary = "\n".join(
            f"  - {f.get('filename', '?')} (+{f.get('additions', 0)} / -{f.get('deletions', 0)})"
            for f in files
        )

        labels = ", ".join(
            (l.get("name", l) if isinstance(l, dict) else str(l))
            for l in (pr.get("labels") or [])
        )

        # Truncate diff to ~120k chars to stay well within context window.
        # Most PRs are far smaller; this is a safety valve.
        max_diff_chars = 120_000
        truncated_diff = diff[:max_diff_chars]
        if len(diff) > max_diff_chars:
            truncated_diff += f"\n\n... [diff truncated — {len(diff) - max_diff_chars} chars omitted]"

        return f"""\
## Pull Request #{pr.get('number')}

**Title**: {pr.get('title', '(no title)')}
**Author**: {pr.get('user', {}).get('login', 'unknown') if isinstance(pr.get('user'), dict) else pr.get('user', 'unknown')}
**Created**: {pr.get('created_at', '?')}
**Merged**: {pr.get('merged_at', '?')}
**Labels**: {labels or '(none)'}
**Stats**: +{pr.get('additions', 0)} / -{pr.get('deletions', 0)} across {pr.get('changed_files', 0)} files
**Review comments**: {pr.get('review_comments', 0)}

### Description
{pr.get('body') or '(no description)'}

### Changed files
{file_summary or '(none)'}

### Diff
```
{truncated_diff}
```
"""

    def _call_api(self, system: str, user_message: str, max_tokens: int = 4096) -> str:
        """Call Claude with retries and exponential backoff."""

        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": user_message}],
                )
                # Extract text from the response
                text = response.content[0].text
                return text

            except anthropic.RateLimitError as e:
                last_error = e
                wait = 2 ** attempt  # 2, 4, 8 seconds
                log.warning(
                    "Rate limited (attempt %d/%d), retrying in %ds",
                    attempt, self.max_retries, wait,
                )
                time.sleep(wait)

            except anthropic.APIStatusError as e:
                last_error = e
                if e.status_code >= 500:
                    # Server error — worth retrying
                    wait = 2 ** attempt
                    log.warning(
                        "API server error %d (attempt %d/%d), retrying in %ds",
                        e.status_code, attempt, self.max_retries, wait,
                    )
                    time.sleep(wait)
                else:
                    # Client error (400, 401, 403, etc.) — don't retry
                    log.error("API client error: %s", e)
                    raise

            except anthropic.APIConnectionError as e:
                last_error = e
                wait = 2 ** attempt
                log.warning(
                    "Connection error (attempt %d/%d), retrying in %ds",
                    attempt, self.max_retries, wait,
                )
                time.sleep(wait)

        raise RuntimeError(
            f"Claude API call failed after {self.max_retries} attempts"
        ) from last_error

    @staticmethod
    def _parse_json(raw: str) -> Any:
        """Parse JSON from Claude's response, stripping markdown fences if present."""

        text = raw.strip()

        # Strip markdown code fences if Claude wraps the response
        if text.startswith("```"):
            # Remove opening fence (with optional language tag)
            first_newline = text.index("\n")
            text = text[first_newline + 1 :]
        if text.endswith("```"):
            text = text[: -3]

        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON array or object from the response
        import re
        # Find the first [ or { and match to closing bracket
        for start_char, end_char in [("[", "]"), ("{", "}")]:
            start = text.find(start_char)
            if start == -1:
                continue
            end = text.rfind(end_char)
            if end > start:
                try:
                    return json.loads(text[start:end + 1])
                except json.JSONDecodeError:
                    continue

        log.error("Failed to parse Claude response as JSON.\nRaw: %s", raw[:500])
        raise ValueError(f"Claude returned unparseable response: {raw[:200]}")
