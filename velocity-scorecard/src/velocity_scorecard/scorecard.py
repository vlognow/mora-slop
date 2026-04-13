"""Velocity Scorecard — aggregates quantitative metrics and LLM scores into a composite score."""

from __future__ import annotations


# Dimension weights for RVI calculation
_WEIGHTS: dict[str, float] = {
    "quality": 0.20,
    "throughput": 0.15,
    "cycle_time": 0.15,
    "complexity": 0.10,
    "impact": 0.15,
    "collaboration": 0.15,
    "health": 0.10,
}


def _clamp(v: float, lo: float = 1.0, hi: float = 10.0) -> float:
    return max(lo, min(hi, v))


class Scorecard:
    """Produces a scored velocity scorecard from quantitative metrics + LLM scores."""

    def compute(self, quantitative: dict, llm_scores: list[dict]) -> dict:
        dimensions = self._score_dimensions(quantitative, llm_scores)
        rvi = self._compute_rvi(dimensions)
        top_signal = self.generate_top_signal(dimensions, quantitative, llm_scores)

        srau_count = sum(1 for s in llm_scores if s.get("is_srau"))
        total = len(llm_scores) if llm_scores else 0

        return {
            "dimensions": dimensions,
            "rvi": round(rvi, 1),
            "rvi_trend": None,
            "top_signal": top_signal,
            "srau_count": srau_count,
            "srau_ratio": round(srau_count / total, 3) if total else 0.0,
        }

    # ------------------------------------------------------------------
    # Dimension scoring
    # ------------------------------------------------------------------

    def _score_dimensions(
        self, quantitative: dict, llm_scores: list[dict]
    ) -> dict[str, float]:
        return {
            "throughput": self._score_throughput(quantitative),
            "cycle_time": self._score_cycle_time(quantitative),
            "quality": self._score_quality(quantitative),
            "complexity": self._score_complexity(llm_scores),
            "impact": self._score_impact(llm_scores),
            "collaboration": self._score_collaboration(quantitative),
            "health": 5.0,  # placeholder — agent readiness requires repo analysis
        }

    # ------------------------------------------------------------------
    # Throughput: PRs merged per week, adjusted by durable-lines proxy
    # ------------------------------------------------------------------

    @staticmethod
    def _score_throughput(q: dict) -> float:
        tp = q.get("throughput", {})
        merged = tp.get("prs_merged", 0)

        # Base score from volume
        if merged >= 30:
            base = 9.0
        elif merged >= 15:
            base = 7.0 + 2.0 * (merged - 15) / 15
        elif merged >= 5:
            base = 5.0 + 2.0 * (merged - 5) / 10
        elif merged >= 1:
            base = 3.0 + 2.0 * (merged - 1) / 4
        else:
            base = 1.0

        # Durable-lines proxy: net additions (additions - deletions).
        # Large net positive with many PRs nudges up; churn-heavy nudges down.
        avg_add = tp.get("avg_additions", 0)
        avg_del = tp.get("avg_deletions", 0)
        net = avg_add - avg_del
        if merged > 0 and net > 100:
            base += 0.5
        elif merged > 0 and net < -50:
            base -= 0.5

        return round(_clamp(base), 1)

    # ------------------------------------------------------------------
    # Cycle time: median hours to merge
    # ------------------------------------------------------------------

    @staticmethod
    def _score_cycle_time(q: dict) -> float:
        ct = q.get("cycle_time", {})
        med = ct.get("median_hours", 48)

        if med <= 4:
            score = 9.0
        elif med <= 12:
            score = 7.0 + 2.0 * (12 - med) / 8
        elif med <= 48:
            score = 5.0 + 2.0 * (48 - med) / 36
        else:
            score = max(1.0, 3.0 - (med - 48) / 48)

        return round(_clamp(score), 1)

    # ------------------------------------------------------------------
    # Quality: low rework + engaged reviews = high
    # ------------------------------------------------------------------

    @staticmethod
    def _score_quality(q: dict) -> float:
        qual = q.get("quality", {})
        rework = qual.get("rework_rate", 0.0)
        avg_comments = qual.get("avg_review_comments", 0.0)

        # Rework component: 0% = 10, 50%+ = 2
        rework_score = 10.0 - 16.0 * rework  # linear, clamped below
        rework_score = _clamp(rework_score, 2.0, 10.0)

        # Review engagement component: 0 comments = 3, 1-3 = 6, 3-8 = 8, 8+ = 6 (diminishing)
        if avg_comments < 0.5:
            engagement = 3.0
        elif avg_comments <= 3:
            engagement = 3.0 + 3.0 * (avg_comments - 0.5) / 2.5
        elif avg_comments <= 8:
            engagement = 6.0 + 2.0 * (avg_comments - 3) / 5
        else:
            engagement = max(5.0, 8.0 - (avg_comments - 8) / 10)

        score = 0.6 * rework_score + 0.4 * engagement
        return round(_clamp(score), 1)

    # ------------------------------------------------------------------
    # Complexity: average of LLM technical_difficulty scores
    # ------------------------------------------------------------------

    @staticmethod
    def _score_complexity(llm_scores: list[dict]) -> float:
        vals = [s.get("technical_difficulty", 5) for s in (llm_scores or [])]
        if not vals:
            return 5.0
        return round(_clamp(sum(vals) / len(vals)), 1)

    # ------------------------------------------------------------------
    # Impact: average of LLM business_value scores
    # ------------------------------------------------------------------

    @staticmethod
    def _score_impact(llm_scores: list[dict]) -> float:
        vals = [s.get("business_value", 5) for s in (llm_scores or [])]
        if not vals:
            return 5.0
        return round(_clamp(sum(vals) / len(vals)), 1)

    # ------------------------------------------------------------------
    # Collaboration: AI adoption + review burden
    # ------------------------------------------------------------------

    @staticmethod
    def _score_collaboration(q: dict) -> float:
        collab = q.get("collaboration", {})
        ai_ratio = collab.get("ai_pr_ratio", 0.0)
        avg_reviews = collab.get("avg_reviews_per_pr", 0.0)

        # AI adoption: 0% = 3, 10-40% = 7, 40-70% = 9, 70%+ = 8 (over-reliance drag)
        if ai_ratio < 0.10:
            ai_score = 3.0 + 40.0 * ai_ratio  # 0->3, 0.1->7
        elif ai_ratio <= 0.40:
            ai_score = 7.0 + 2.0 * (ai_ratio - 0.10) / 0.30
        elif ai_ratio <= 0.70:
            ai_score = 9.0
        else:
            ai_score = max(6.0, 9.0 - 3.0 * (ai_ratio - 0.70) / 0.30)

        # Review burden: 0 = 2, 1-2 = 7, 2-4 = 9, 4+ = 7 (overloaded)
        if avg_reviews < 0.5:
            review_score = 2.0
        elif avg_reviews <= 2:
            review_score = 2.0 + 5.0 * (avg_reviews - 0.5) / 1.5
        elif avg_reviews <= 4:
            review_score = 7.0 + 2.0 * (avg_reviews - 2) / 2
        else:
            review_score = max(5.0, 9.0 - 2.0 * (avg_reviews - 4) / 4)

        score = 0.5 * ai_score + 0.5 * review_score
        return round(_clamp(score), 1)

    # ------------------------------------------------------------------
    # RVI — weighted composite 0-100
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_rvi(dimensions: dict[str, float]) -> float:
        weighted_sum = sum(
            dimensions.get(dim, 5.0) * weight for dim, weight in _WEIGHTS.items()
        )
        # Dimensions are 1-10; normalize to 0-100
        return round(weighted_sum * 10, 1)

    # ------------------------------------------------------------------
    # Top signal — one-sentence actionable finding
    # ------------------------------------------------------------------

    def generate_top_signal(
        self,
        dimensions: dict[str, float],
        quantitative: dict,
        llm_scores: list[dict],
    ) -> str:
        if not dimensions:
            return "Insufficient data to identify a top signal."

        # Find the dimension with the largest gap from a "healthy" baseline of 7
        baseline = 7.0
        gaps: list[tuple[str, float]] = []
        for dim, score in dimensions.items():
            gaps.append((dim, baseline - score))

        # Sort by absolute gap descending
        gaps.sort(key=lambda t: abs(t[1]), reverse=True)
        top_dim, top_gap = gaps[0]

        # Build contextual message
        if top_gap > 0:
            # Below baseline — the problem area
            return self._signal_for_weakness(
                top_dim, dimensions[top_dim], top_gap, quantitative, llm_scores
            )
        else:
            # Above baseline — call out the strength
            return self._signal_for_strength(
                top_dim, dimensions[top_dim], quantitative, llm_scores
            )

    @staticmethod
    def _signal_for_weakness(
        dim: str,
        score: float,
        gap: float,
        quantitative: dict,
        llm_scores: list[dict],
    ) -> str:
        messages = {
            "throughput": lambda: (
                f"Throughput is the biggest gap at {score}/10 "
                f"({quantitative.get('throughput', {}).get('prs_merged', 0)} PRs merged) "
                f"— consider whether work is stuck in review or scope is too large per PR."
            ),
            "cycle_time": lambda: (
                f"Cycle time scored {score}/10 "
                f"(median {quantitative.get('cycle_time', {}).get('median_hours', 0):.1f}h) "
                f"— look for bottlenecks in review latency or CI."
            ),
            "quality": lambda: (
                f"Quality scored {score}/10 "
                f"(rework rate {quantitative.get('quality', {}).get('rework_rate', 0):.0%}) "
                f"— frequent file re-touches suggest specs or decomposition need attention."
            ),
            "complexity": lambda: (
                f"Average complexity is low at {score}/10 "
                f"— the team may be under-investing in hard problems vs. routine changes."
            ),
            "impact": lambda: (
                f"Business impact scored only {score}/10 "
                f"— many PRs are low-value; consider reprioritizing toward higher-leverage work."
            ),
            "collaboration": lambda: (
                f"Collaboration scored {score}/10 "
                f"— review coverage or AI adoption may need a boost."
            ),
            "health": lambda: (
                f"Repo health is at the placeholder score of {score}/10 "
                f"— full assessment requires repo-level analysis (coming soon)."
            ),
        }
        return messages.get(dim, lambda: f"{dim} scored {score}/10, below the healthy baseline.")()

    @staticmethod
    def _signal_for_strength(
        dim: str,
        score: float,
        quantitative: dict,
        llm_scores: list[dict],
    ) -> str:
        messages = {
            "throughput": lambda: (
                f"Throughput is a standout at {score}/10 "
                f"({quantitative.get('throughput', {}).get('prs_merged', 0)} PRs merged) "
                f"— shipping velocity is strong."
            ),
            "cycle_time": lambda: (
                f"Cycle time is excellent at {score}/10 "
                f"(median {quantitative.get('cycle_time', {}).get('median_hours', 0):.1f}h) "
                f"— PRs move through review fast."
            ),
            "quality": lambda: (
                f"Quality is the top dimension at {score}/10 "
                f"— low rework and engaged reviews signal healthy engineering discipline."
            ),
            "complexity": lambda: (
                f"The team is tackling genuinely hard problems (complexity {score}/10) "
                f"— this is a sign of healthy ambition."
            ),
            "impact": lambda: (
                f"Business impact is strong at {score}/10 "
                f"— PRs are well-aligned with what matters."
            ),
            "collaboration": lambda: (
                f"Collaboration is a strength at {score}/10 "
                f"— healthy AI adoption and good review discipline."
            ),
            "health": lambda: (
                f"Repo health placeholder at {score}/10 — no signal yet."
            ),
        }
        return messages.get(dim, lambda: f"{dim} scored {score}/10, above the healthy baseline.")()
