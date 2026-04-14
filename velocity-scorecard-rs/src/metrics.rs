use std::collections::HashSet;
use std::sync::LazyLock;

use chrono::{DateTime, Duration, Utc};
use regex::Regex;
use serde::{Deserialize, Serialize};

use crate::github::{PullRequest, Review};

// Regex to detect AI-assisted PRs via co-author lines, bot names, or labels.
// Matches the Python regex in `metrics.py` verbatim.
static AI_MARKERS: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)co-authored-by:\s*claude|cursor_agent|claude|copilot|ai[\s\-_]generated")
        .expect("AI_MARKERS regex must compile")
});

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Quantitative {
    pub throughput: Throughput,
    pub cycle_time: CycleTime,
    pub quality: Quality,
    pub collaboration: Collaboration,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Throughput {
    pub prs_merged: u64,
    pub avg_additions: f64,
    pub avg_deletions: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct CycleTime {
    pub median_hours: f64,
    pub p90_hours: f64,
    pub first_review_median_hours: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Quality {
    pub rework_rate: f64,
    pub avg_review_comments: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Collaboration {
    pub ai_pr_count: u64,
    pub ai_pr_ratio: f64,
    pub avg_reviews_per_pr: f64,
}

pub fn compute(prs: &[PullRequest]) -> Quantitative {
    let merged: Vec<&PullRequest> = prs.iter().filter(|p| p.merged_at.is_some()).collect();
    Quantitative {
        throughput: throughput(&merged),
        cycle_time: cycle_time(&merged),
        quality: quality(&merged),
        collaboration: collaboration(prs),
    }
}

// --------------------------------------------------------------------
// Throughput
// --------------------------------------------------------------------

fn throughput(merged: &[&PullRequest]) -> Throughput {
    let n = merged.len();
    if n == 0 {
        return Throughput::default();
    }
    let n_f = n as f64;
    let (add_sum, del_sum): (u64, u64) = merged
        .iter()
        .fold((0, 0), |(a, d), p| (a + p.additions, d + p.deletions));
    Throughput {
        prs_merged: n as u64,
        avg_additions: add_sum as f64 / n_f,
        avg_deletions: del_sum as f64 / n_f,
    }
}

// --------------------------------------------------------------------
// Cycle time
// --------------------------------------------------------------------

fn cycle_time(merged: &[&PullRequest]) -> CycleTime {
    let mut cycle_hours: Vec<f64> = Vec::with_capacity(merged.len());
    let mut review_hours: Vec<f64> = Vec::new();

    for pr in merged {
        let created = parse_dt(pr.created_at.as_deref());
        let merged_at = parse_dt(pr.merged_at.as_deref());
        if let (Some(c), Some(m)) = (created, merged_at) {
            cycle_hours.push((m - c).num_seconds() as f64 / 3600.0);
        }

        if let Some(c) = created {
            let first_review = pr
                .reviews
                .iter()
                .filter_map(|r: &Review| parse_dt(r.submitted_at.as_deref()))
                .min();
            if let Some(fr) = first_review {
                review_hours.push((fr - c).num_seconds() as f64 / 3600.0);
            }
        }
    }

    CycleTime {
        median_hours: median(&cycle_hours),
        p90_hours: percentile(&cycle_hours, 0.90),
        first_review_median_hours: median(&review_hours),
    }
}

// --------------------------------------------------------------------
// Quality — 14-day file-overlap rework + review engagement
// --------------------------------------------------------------------

fn quality(merged: &[&PullRequest]) -> Quality {
    let n = merged.len();
    if n == 0 {
        return Quality::default();
    }

    // Python's implementation only has file-level overlap when `changed_files` is a
    // list (it's a count in our schema), so the set is always empty and rework
    // stays 0. We keep the structure here so that if `changed_files` ever
    // carries filenames (e.g. via a future GraphQL switch), behavior lines up
    // trivially.
    let mut timeline: Vec<(DateTime<Utc>, HashSet<String>)> = Vec::with_capacity(merged.len());
    for pr in merged {
        if let Some(m) = parse_dt(pr.merged_at.as_deref()) {
            timeline.push((m, HashSet::new()));
        }
    }
    timeline.sort_by_key(|t| t.0);

    let mut rework_count: u64 = 0;
    for (i, (merged_at_i, files_i)) in timeline.iter().enumerate() {
        if files_i.is_empty() {
            continue;
        }
        let window_start = *merged_at_i - Duration::days(14);
        for (merged_at_j, files_j) in &timeline[..i] {
            if *merged_at_j < window_start {
                continue;
            }
            if !files_i.is_disjoint(files_j) {
                rework_count += 1;
                break;
            }
        }
    }

    let total_comments: u64 = merged.iter().map(|p| p.review_comments).sum();
    let n_f = n as f64;
    Quality {
        rework_rate: rework_count as f64 / n_f,
        avg_review_comments: total_comments as f64 / n_f,
    }
}

// --------------------------------------------------------------------
// Collaboration — AI adoption + review load
// --------------------------------------------------------------------

fn collaboration(prs: &[PullRequest]) -> Collaboration {
    let n = prs.len();
    if n == 0 {
        return Collaboration::default();
    }
    let mut ai_count: u64 = 0;
    let mut total_reviews: u64 = 0;

    for pr in prs {
        let label_text = pr.labels.join(" ");
        let haystack = format!("{} {} {}", pr.body, pr.title, label_text);
        if AI_MARKERS.is_match(&haystack) {
            ai_count += 1;
        }
        total_reviews += pr.reviews.len() as u64;
    }

    let n_f = n as f64;
    Collaboration {
        ai_pr_count: ai_count,
        ai_pr_ratio: ai_count as f64 / n_f,
        avg_reviews_per_pr: total_reviews as f64 / n_f,
    }
}

// --------------------------------------------------------------------
// Helpers
// --------------------------------------------------------------------

fn parse_dt(s: Option<&str>) -> Option<DateTime<Utc>> {
    let raw = s?;
    // GitHub returns RFC3339 timestamps; chrono parses via
    // DateTime::parse_from_rfc3339
    DateTime::parse_from_rfc3339(raw).ok().map(|d| d.with_timezone(&Utc))
}

fn median(data: &[f64]) -> f64 {
    if data.is_empty() {
        return 0.0;
    }
    let mut s: Vec<f64> = data.to_vec();
    s.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
    let mid = s.len() / 2;
    if s.len() % 2 == 1 {
        s[mid]
    } else {
        (s[mid - 1] + s[mid]) / 2.0
    }
}

/// Linear-interpolation percentile (matches numpy's default method, and
/// `_percentile` in Python).
fn percentile(data: &[f64], pct: f64) -> f64 {
    if data.is_empty() {
        return 0.0;
    }
    let mut s: Vec<f64> = data.to_vec();
    s.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
    let k = (s.len() - 1) as f64 * pct;
    let f = k.floor() as usize;
    let c = if f + 1 < s.len() { f + 1 } else { f };
    s[f] + (k - f as f64) * (s[c] - s[f])
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn percentile_matches_numpy_default() {
        // e.g. p90 of 1..=10 is 9.1 under linear interpolation
        let v: Vec<f64> = (1..=10).map(|x| x as f64).collect();
        let p = percentile(&v, 0.9);
        assert!((p - 9.1).abs() < 1e-9, "got {p}");
    }

    #[test]
    fn median_odd_and_even() {
        assert!((median(&[1.0, 2.0, 3.0]) - 2.0).abs() < 1e-9);
        assert!((median(&[1.0, 2.0, 3.0, 4.0]) - 2.5).abs() < 1e-9);
        assert_eq!(median(&[]), 0.0);
    }

    #[test]
    fn ai_markers_detects_co_author_claude() {
        assert!(AI_MARKERS.is_match("Co-Authored-By: Claude <claude@anthropic.com>"));
        assert!(AI_MARKERS.is_match("cursor_agent committed"));
        assert!(AI_MARKERS.is_match("AI-generated refactor"));
        assert!(!AI_MARKERS.is_match("plain PR description"));
    }
}
