use std::io::Write;
use std::sync::Arc;

use anyhow::{Context, anyhow};
use clap::Parser;
use clap::builder::Styles;
use clap::builder::styling::AnsiColor;
use futures::StreamExt;
use futures::stream::FuturesUnordered;
use owo_colors::OwoColorize;
use serde_json::json;
use tokio::sync::Semaphore;

mod config;
mod display;
mod error;
mod github;
mod llm;
mod metrics;
mod scorecard;

use crate::github::{GithubClient, PullRequest};
use crate::llm::{LlmScorer, PrScore};

const MODEL: &str = "claude-sonnet-4-20250514";

/// LLM-scored repo velocity scorecard.
#[derive(Parser)]
#[command(name = "velocity-score", styles = v3_styles(), version)]
#[command(about = "LLM-scored repo velocity measurement")]
#[command(max_term_width = 100)]
struct Cli {
    /// GitHub repo in owner/repo format.
    repo: String,

    /// Analysis window in weeks.
    #[arg(long, default_value_t = 4)]
    weeks: u32,

    /// Display the individual PR scores table after the scorecard.
    #[arg(long)]
    show_prs: bool,

    /// Emit JSON instead of rendering to the terminal.
    #[arg(long)]
    json_output: bool,

    /// Skip LLM scoring (quantitative metrics only).
    #[arg(long)]
    skip_llm: bool,

    /// Max concurrent Anthropic API calls during PR scoring.
    #[arg(long, default_value_t = 5)]
    concurrency: usize,

    /// Enable debug logging.
    #[arg(short, long)]
    verbose: bool,
}

fn v3_styles() -> Styles {
    Styles::styled()
        .header(AnsiColor::Yellow.on_default())
        .usage(AnsiColor::Yellow.on_default())
        .literal(AnsiColor::Green.on_default())
        .placeholder(AnsiColor::Green.on_default())
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    dotenvy::dotenv().ok();
    let cli = Cli::parse();

    let level = if cli.verbose {
        log::LevelFilter::Debug
    } else {
        log::LevelFilter::Info
    };
    env_logger::Builder::new()
        .format(|buf, record| writeln!(buf, "{}", record.args()))
        .filter_level(level)
        .init();

    let (owner, repo_name) = cli
        .repo
        .split_once('/')
        .ok_or_else(|| anyhow!("repo must be in owner/repo format, got '{}'", cli.repo))?;
    if owner.is_empty() || repo_name.is_empty() {
        return Err(anyhow!("repo must be in owner/repo format, got '{}'", cli.repo));
    }

    let token = config::resolve_github_token().context("resolving GitHub token")?;
    let gh = Arc::new(GithubClient::new(owner.to_string(), repo_name.to_string(), &token)?);

    log::info!(
        "{}",
        format!("Fetching merged PRs for {} (last {} weeks)...", cli.repo, cli.weeks).dimmed()
    );
    let prs = gh.fetch_merged_prs(cli.weeks).await.context("fetching merged PRs")?;

    if prs.is_empty() {
        log::warn!("No merged PRs found in this period.");
        return Ok(());
    }
    log::info!("{}", format!("Found {} merged PRs.", prs.len()).dimmed());

    let quantitative = metrics::compute(&prs);

    let llm_scores: Vec<PrScore> = if cli.skip_llm {
        log::info!("{}", "Skipping LLM scoring (--skip-llm).".dimmed());
        Vec::new()
    } else {
        let api_key = config::resolve_anthropic_key()
            .ok_or_else(|| anyhow!("ANTHROPIC_API_KEY not set (required unless --skip-llm)"))?;
        let scorer = Arc::new(LlmScorer::new(&api_key, MODEL, 3)?);
        let scores = score_prs_parallel(gh.clone(), scorer.clone(), &prs, cli.concurrency).await;
        if scores.len() > 1 {
            log::info!("{}", "Running calibration pass...".dimmed());
            scorer.calibrate(scores).await
        } else {
            scores
        }
    };

    let result = scorecard::compute(&quantitative, &llm_scores);

    if cli.json_output {
        let payload = json!({
            "repo": cli.repo,
            "weeks": cli.weeks,
            "prs_analyzed": prs.len(),
            "dimensions": result.dimensions,
            "rvi": result.rvi,
            "top_signal": result.top_signal,
            "srau_count": result.srau_count,
            "srau_ratio": result.srau_ratio,
            "quantitative": quantitative,
            "pr_scores": llm_scores,
        });
        println!("{}", serde_json::to_string_pretty(&payload)?);
    } else {
        display::render_scorecard(&cli.repo, cli.weeks, &result, &quantitative, &llm_scores)?;
        if cli.show_prs && !llm_scores.is_empty() {
            display::render_pr_table(&llm_scores)?;
        }
    }

    Ok(())
}

/// Score PRs in parallel, bounded by a semaphore. Failed PRs are skipped with a
/// log warning.
async fn score_prs_parallel(
    gh: Arc<GithubClient>,
    scorer: Arc<LlmScorer>,
    prs: &[PullRequest],
    concurrency: usize,
) -> Vec<PrScore> {
    let concurrency = concurrency.max(1);
    let sem = Arc::new(Semaphore::new(concurrency));
    let total = prs.len();
    log::info!(
        "{}",
        format!("Scoring {total} PRs with Claude ({concurrency} concurrent)...").dimmed()
    );

    let mut tasks = FuturesUnordered::new();
    for (idx, pr) in prs.iter().enumerate() {
        let gh = gh.clone();
        let scorer = scorer.clone();
        let sem = sem.clone();
        let pr = pr.clone();
        let position = idx + 1;
        tasks.push(tokio::spawn(async move {
            let _permit = sem.acquire_owned().await.ok()?;
            log::debug!("({position}/{total}) PR #{}: {}", pr.number, pr.title);

            let diff = match gh.fetch_pr_diff(pr.number).await {
                Ok(d) => d,
                Err(e) => {
                    log::warn!("PR #{}: diff fetch failed: {e}", pr.number);
                    return None;
                }
            };
            let files = match gh.fetch_pr_files(pr.number).await {
                Ok(f) => f,
                Err(e) => {
                    log::warn!("PR #{}: files fetch failed: {e}", pr.number);
                    return None;
                }
            };
            match scorer.score_pr(&pr, &diff, &files).await {
                Ok(s) => Some(s),
                Err(e) => {
                    log::warn!("PR #{}: LLM scoring failed: {e}", pr.number);
                    None
                }
            }
        }));
    }

    let mut scores = Vec::with_capacity(total);
    while let Some(joined) = tasks.next().await {
        match joined {
            Ok(Some(s)) => scores.push(s),
            Ok(None) => {} // Skipped (error already logged)
            Err(e) => log::warn!("Scoring task panicked: {e}"),
        }
    }
    scores
}
