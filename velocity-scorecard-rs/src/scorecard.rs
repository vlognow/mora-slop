use serde::{Deserialize, Serialize};

use crate::llm::PrScore;
use crate::metrics::Quantitative;

/// The seven scored dimensions. Serialization is via `snake_case` to match the
/// Python JSON shape. Keeping this an enum (not a bag of `&str` constants)
/// means every call site is exhaustive-checked by the compiler — adding a
/// dimension can't miss a branch.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Dimension {
    Throughput,
    CycleTime,
    Quality,
    Complexity,
    Impact,
    Collaboration,
    Health,
}

impl Dimension {
    /// All dimensions in canonical order. Used for top-signal tie-breaking,
    /// where the first-listed dimension wins on ties (matching Python's
    /// stable `sorted`).
    pub const ALL: [Dimension; 7] = [
        Dimension::Throughput,
        Dimension::CycleTime,
        Dimension::Quality,
        Dimension::Complexity,
        Dimension::Impact,
        Dimension::Collaboration,
        Dimension::Health,
    ];

    /// Weight in the RVI composite. All weights sum to 1.0.
    pub const fn weight(self) -> f64 {
        match self {
            Dimension::Quality => 0.20,
            Dimension::Throughput | Dimension::CycleTime | Dimension::Impact | Dimension::Collaboration => 0.15,
            Dimension::Complexity | Dimension::Health => 0.10,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Dimensions {
    pub throughput: f64,
    pub cycle_time: f64,
    pub quality: f64,
    pub complexity: f64,
    pub impact: f64,
    pub collaboration: f64,
    pub health: f64,
}

impl Dimensions {
    pub fn get(&self, dim: Dimension) -> f64 {
        match dim {
            Dimension::Throughput => self.throughput,
            Dimension::CycleTime => self.cycle_time,
            Dimension::Quality => self.quality,
            Dimension::Complexity => self.complexity,
            Dimension::Impact => self.impact,
            Dimension::Collaboration => self.collaboration,
            Dimension::Health => self.health,
        }
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct ScorecardResult {
    pub dimensions: Dimensions,
    pub rvi: f64,
    pub rvi_trend: Option<f64>,
    pub top_signal: String,
    pub srau_count: u64,
    pub srau_ratio: f64,
}

pub fn compute(quantitative: &Quantitative, llm_scores: &[PrScore]) -> ScorecardResult {
    let dimensions = Dimensions {
        throughput: score_throughput(quantitative),
        cycle_time: score_cycle_time(quantitative),
        quality: score_quality(quantitative),
        complexity: score_complexity(llm_scores),
        impact: score_impact(llm_scores),
        collaboration: score_collaboration(quantitative),
        health: 5.0,
    };
    let rvi = round1(compute_rvi(&dimensions));

    let srau_count = llm_scores.iter().filter(|s| s.is_srau).count() as u64;
    let total = llm_scores.len();
    let srau_ratio = if total > 0 {
        round3(srau_count as f64 / total as f64)
    } else {
        0.0
    };

    let top_signal = generate_top_signal(&dimensions, quantitative);

    ScorecardResult {
        dimensions,
        rvi,
        rvi_trend: None,
        top_signal,
        srau_count,
        srau_ratio,
    }
}

// --------------------------------------------------------------------
// Throughput
// --------------------------------------------------------------------

fn score_throughput(q: &Quantitative) -> f64 {
    let merged = q.throughput.prs_merged as f64;

    let mut base = if merged >= 30.0 {
        9.0
    } else if merged >= 15.0 {
        7.0 + 2.0 * (merged - 15.0) / 15.0
    } else if merged >= 5.0 {
        5.0 + 2.0 * (merged - 5.0) / 10.0
    } else if merged >= 1.0 {
        3.0 + 2.0 * (merged - 1.0) / 4.0
    } else {
        1.0
    };

    let net = q.throughput.avg_additions - q.throughput.avg_deletions;
    if merged > 0.0 && net > 100.0 {
        base += 0.5;
    } else if merged > 0.0 && net < -50.0 {
        base -= 0.5;
    }

    round1(base.clamp(1.0, 10.0))
}

// --------------------------------------------------------------------
// Cycle time
// --------------------------------------------------------------------

fn score_cycle_time(q: &Quantitative) -> f64 {
    let med = q.cycle_time.median_hours;

    let score = if med <= 4.0 {
        9.0
    } else if med <= 12.0 {
        7.0 + 2.0 * (12.0 - med) / 8.0
    } else if med <= 48.0 {
        5.0 + 2.0 * (48.0 - med) / 36.0
    } else {
        (3.0 - (med - 48.0) / 48.0).max(1.0)
    };

    round1(score.clamp(1.0, 10.0))
}

// --------------------------------------------------------------------
// Quality
// --------------------------------------------------------------------

fn score_quality(q: &Quantitative) -> f64 {
    let rework = q.quality.rework_rate;
    let avg = q.quality.avg_review_comments;

    let rework_score = (10.0 - 16.0 * rework).clamp(2.0, 10.0);

    let engagement = if avg < 0.5 {
        3.0
    } else if avg <= 3.0 {
        3.0 + 3.0 * (avg - 0.5) / 2.5
    } else if avg <= 8.0 {
        6.0 + 2.0 * (avg - 3.0) / 5.0
    } else {
        (8.0 - (avg - 8.0) / 10.0).max(5.0)
    };

    round1((0.6 * rework_score + 0.4 * engagement).clamp(1.0, 10.0))
}

// --------------------------------------------------------------------
// Complexity / Impact — averages over LLM scores
// --------------------------------------------------------------------

fn score_complexity(scores: &[PrScore]) -> f64 {
    avg_llm(scores, |s| s.technical_difficulty)
}

fn score_impact(scores: &[PrScore]) -> f64 {
    avg_llm(scores, |s| s.business_value)
}

fn avg_llm(scores: &[PrScore], field: impl Fn(&PrScore) -> f64) -> f64 {
    if scores.is_empty() {
        return 5.0;
    }
    let sum: f64 = scores.iter().map(field).sum();
    round1((sum / scores.len() as f64).clamp(1.0, 10.0))
}

// --------------------------------------------------------------------
// Collaboration
// --------------------------------------------------------------------

fn score_collaboration(q: &Quantitative) -> f64 {
    let ai_ratio = q.collaboration.ai_pr_ratio;
    let avg_reviews = q.collaboration.avg_reviews_per_pr;

    let ai_score = if ai_ratio < 0.10 {
        3.0 + 40.0 * ai_ratio
    } else if ai_ratio <= 0.40 {
        7.0 + 2.0 * (ai_ratio - 0.10) / 0.30
    } else if ai_ratio <= 0.70 {
        9.0
    } else {
        (9.0 - 3.0 * (ai_ratio - 0.70) / 0.30).max(6.0)
    };

    let review_score = if avg_reviews < 0.5 {
        2.0
    } else if avg_reviews <= 2.0 {
        2.0 + 5.0 * (avg_reviews - 0.5) / 1.5
    } else if avg_reviews <= 4.0 {
        7.0 + 2.0 * (avg_reviews - 2.0) / 2.0
    } else {
        (9.0 - 2.0 * (avg_reviews - 4.0) / 4.0).max(5.0)
    };

    round1((0.5 * ai_score + 0.5 * review_score).clamp(1.0, 10.0))
}

// --------------------------------------------------------------------
// RVI
// --------------------------------------------------------------------

fn compute_rvi(d: &Dimensions) -> f64 {
    let weighted: f64 = Dimension::ALL.iter().map(|&dim| d.get(dim) * dim.weight()).sum();
    weighted * 10.0
}

// --------------------------------------------------------------------
// Top-signal selection
// --------------------------------------------------------------------

/// Pick the dimension furthest from the "healthy" baseline of 7.0 and describe
/// it. On ties, the first dimension in [`Dimension::ALL`] wins (matches
/// Python's stable sort).
fn generate_top_signal(d: &Dimensions, q: &Quantitative) -> String {
    const BASELINE: f64 = 7.0;

    // Strict `>` on the absolute gap preserves first-listed-wins tie-breaking
    // (matches Python's stable `sorted(..., reverse=True)`). `max_by` would return
    // the *last* equal element, which would diverge on ties.
    let mut winner = Dimension::Throughput;
    let mut best_abs = -1.0_f64;
    let mut gap = 0.0_f64;
    for &dim in &Dimension::ALL {
        let g = BASELINE - d.get(dim);
        if g.abs() > best_abs {
            best_abs = g.abs();
            gap = g;
            winner = dim;
        }
    }

    let score = d.get(winner);
    if gap > 0.0 {
        signal_weakness(winner, score, q)
    } else {
        signal_strength(winner, score, q)
    }
}

fn signal_weakness(dim: Dimension, score: f64, q: &Quantitative) -> String {
    match dim {
        Dimension::Throughput => format!(
            "Throughput is the biggest gap at {score:.1}/10 ({prs} PRs merged) \u{2014} consider whether work is stuck in review or scope is too large per PR.",
            prs = q.throughput.prs_merged,
        ),
        Dimension::CycleTime => format!(
            "Cycle time scored {score:.1}/10 (median {med:.1}h) \u{2014} look for bottlenecks in review latency or CI.",
            med = q.cycle_time.median_hours,
        ),
        Dimension::Quality => format!(
            "Quality scored {score:.1}/10 (rework rate {pct:.0}%) \u{2014} frequent file re-touches suggest specs or decomposition need attention.",
            pct = q.quality.rework_rate * 100.0,
        ),
        Dimension::Complexity => format!(
            "Average complexity is low at {score:.1}/10 \u{2014} the team may be under-investing in hard problems vs. routine changes."
        ),
        Dimension::Impact => format!(
            "Business impact scored only {score:.1}/10 \u{2014} many PRs are low-value; consider reprioritizing toward higher-leverage work."
        ),
        Dimension::Collaboration => {
            format!("Collaboration scored {score:.1}/10 \u{2014} review coverage or AI adoption may need a boost.")
        }
        Dimension::Health => format!(
            "Repo health is at the placeholder score of {score:.1}/10 \u{2014} full assessment requires repo-level analysis (coming soon)."
        ),
    }
}

fn signal_strength(dim: Dimension, score: f64, q: &Quantitative) -> String {
    match dim {
        Dimension::Throughput => format!(
            "Throughput is a standout at {score:.1}/10 ({prs} PRs merged) \u{2014} shipping velocity is strong.",
            prs = q.throughput.prs_merged,
        ),
        Dimension::CycleTime => format!(
            "Cycle time is excellent at {score:.1}/10 (median {med:.1}h) \u{2014} PRs move through review fast.",
            med = q.cycle_time.median_hours,
        ),
        Dimension::Quality => format!(
            "Quality is the top dimension at {score:.1}/10 \u{2014} low rework and engaged reviews signal healthy engineering discipline."
        ),
        Dimension::Complexity => format!(
            "The team is tackling genuinely hard problems (complexity {score:.1}/10) \u{2014} this is a sign of healthy ambition."
        ),
        Dimension::Impact => {
            format!("Business impact is strong at {score:.1}/10 \u{2014} PRs are well-aligned with what matters.")
        }
        Dimension::Collaboration => format!(
            "Collaboration is a strength at {score:.1}/10 \u{2014} healthy AI adoption and good review discipline."
        ),
        Dimension::Health => format!("Repo health placeholder at {score:.1}/10 \u{2014} no signal yet."),
    }
}

// --------------------------------------------------------------------
// Rounding helpers — kept to match Python's `round(x, N)` at the same points.
// --------------------------------------------------------------------

fn round1(v: f64) -> f64 {
    (v * 10.0).round() / 10.0
}
fn round3(v: f64) -> f64 {
    (v * 1000.0).round() / 1000.0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn weights_sum_to_one() {
        let total: f64 = Dimension::ALL.iter().map(|d| d.weight()).sum();
        assert!((total - 1.0).abs() < 1e-9, "weights sum to {total}");
    }

    #[test]
    fn rvi_of_all_fives_is_fifty() {
        let d = Dimensions {
            throughput: 5.0,
            cycle_time: 5.0,
            quality: 5.0,
            complexity: 5.0,
            impact: 5.0,
            collaboration: 5.0,
            health: 5.0,
        };
        assert!((compute_rvi(&d) - 50.0).abs() < 1e-9);
    }

    #[test]
    fn throughput_zero_is_one() {
        let q = Quantitative::default();
        assert_eq!(score_throughput(&q), 1.0);
    }
}
