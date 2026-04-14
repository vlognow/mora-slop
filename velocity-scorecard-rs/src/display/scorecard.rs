use std::io::{self, Write};

use owo_colors::{AnsiColors, OwoColorize};

use super::bar::{bar, fmt_hours};
use crate::llm::PrScore;
use crate::metrics::Quantitative;
use crate::scorecard::ScorecardResult;

pub fn render_scorecard(
    repo: &str,
    period_weeks: u32,
    result: &ScorecardResult,
    quantitative: &Quantitative,
    llm_scores: &[PrScore],
) -> io::Result<()> {
    let stdout = io::stdout();
    let mut out = stdout.lock();
    let d = &result.dimensions;

    writeln!(out)?;
    writeln!(
        out,
        "  {} {}",
        "VELOCITY SCORECARD".bold().green(),
        format!("\u{2014} {repo}").bold()
    )?;
    writeln!(out, "  Period: last {period_weeks} weeks")?;
    writeln!(out)?;

    render_dim(&mut out, "Throughput", d.throughput, &throughput_detail(quantitative))?;
    render_dim(&mut out, "Cycle Time", d.cycle_time, &cycle_time_detail(quantitative))?;
    render_dim(&mut out, "Quality", d.quality, &quality_detail(quantitative))?;
    render_dim(&mut out, "Complexity", d.complexity, &complexity_detail(llm_scores))?;
    render_dim(&mut out, "Impact", d.impact, &impact_detail(llm_scores))?;
    render_dim(&mut out, "Collaboration", d.collaboration, &collab_detail(quantitative))?;
    render_dim(&mut out, "Health", d.health, "")?;

    writeln!(out)?;

    write!(out, "  {}: {:.0} / 100", "RVI".bold(), result.rvi)?;
    match result.rvi_trend {
        Some(t) if t > 0.0 => write!(out, "  ({} {:.0})", "\u{2191}".green(), t.abs())?,
        Some(t) if t < 0.0 => write!(out, "  ({} {:.0})", "\u{2193}".red(), t.abs())?,
        Some(_) => write!(out, "  ({} 0)", "\u{2192}".yellow())?,
        None => {}
    }
    writeln!(out)?;

    let total = llm_scores.len();
    writeln!(
        out,
        "  SRAUs: {} of {total} PRs ({:.0}%)",
        result.srau_count,
        result.srau_ratio * 100.0
    )?;
    writeln!(out)?;
    writeln!(out, "  {}: {}", "Top Signal".bold().yellow(), result.top_signal)?;
    writeln!(out)?;
    Ok(())
}

/// Score-to-color mapping: green ≥ 7, yellow ≥ 4, red below.
fn score_color(score: f64) -> AnsiColors {
    if score >= 7.0 {
        AnsiColors::Green
    } else if score >= 4.0 {
        AnsiColors::Yellow
    } else {
        AnsiColors::Red
    }
}

fn render_dim<W: Write>(out: &mut W, label: &str, score: f64, detail: &str) -> io::Result<()> {
    let bar_text = bar(score, 10);
    writeln!(
        out,
        "  {:<14} {}  {:>4.1}  {}",
        label.bold(),
        bar_text.color(score_color(score)),
        score,
        detail.dimmed(),
    )
}

fn throughput_detail(q: &Quantitative) -> String {
    format!("{} PRs merged", q.throughput.prs_merged)
}

fn cycle_time_detail(q: &Quantitative) -> String {
    format!(
        "p50: {}, p90: {}",
        fmt_hours(q.cycle_time.median_hours),
        fmt_hours(q.cycle_time.p90_hours)
    )
}

fn quality_detail(q: &Quantitative) -> String {
    format!("{:.1}% rework", q.quality.rework_rate * 100.0)
}

fn complexity_detail(scores: &[PrScore]) -> String {
    avg_detail(scores, |s| s.technical_difficulty)
}

fn impact_detail(scores: &[PrScore]) -> String {
    avg_detail(scores, |s| s.business_value)
}

fn avg_detail(scores: &[PrScore], field: impl Fn(&PrScore) -> f64) -> String {
    if scores.is_empty() {
        return String::new();
    }
    let avg: f64 = scores.iter().map(field).sum::<f64>() / scores.len() as f64;
    format!("avg {avg:.1}")
}

fn collab_detail(q: &Quantitative) -> String {
    format!(
        "{} AI PRs ({:.0}%)",
        q.collaboration.ai_pr_count,
        q.collaboration.ai_pr_ratio * 100.0
    )
}
