"""CLI entrypoint for velocity-scorecard."""

import json
import logging
import sys

import click
from dotenv import load_dotenv
from rich.console import Console

from velocity_scorecard.github_client import GitHubClient
from velocity_scorecard.llm_scorer import LLMScorer
from velocity_scorecard.metrics import MetricsCalculator
from velocity_scorecard.output import render_pr_table, render_scorecard
from velocity_scorecard.scorecard import Scorecard

load_dotenv()

console = Console()


@click.command()
@click.argument("repo")
@click.option("--weeks", default=4, help="Number of weeks to analyze")
@click.option("--show-prs", is_flag=True, help="Show individual PR scores table")
@click.option("--json-output", is_flag=True, help="Output raw JSON instead of terminal")
@click.option("--skip-llm", is_flag=True, help="Skip LLM scoring (quantitative only)")
@click.option("--verbose", "-v", is_flag=True, help="Verbose logging")
def main(repo: str, weeks: int, show_prs: bool, json_output: bool, skip_llm: bool, verbose: bool):
    """Score a GitHub repo's velocity.

    REPO should be in owner/repo format, e.g. vlognow/olapui
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s %(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=logging.WARNING)

    # Parse repo
    if "/" not in repo:
        console.print(f"[red]Error: repo must be in owner/repo format, got '{repo}'[/red]")
        sys.exit(1)

    owner, repo_name = repo.split("/", 1)

    # Step 1: Fetch PRs
    console.print(f"[dim]Fetching merged PRs for {repo} (last {weeks} weeks)...[/dim]")
    gh = GitHubClient(owner, repo_name)
    prs = gh.fetch_merged_prs(weeks)

    if not prs:
        console.print("[yellow]No merged PRs found in this period.[/yellow]")
        sys.exit(0)

    console.print(f"[dim]Found {len(prs)} merged PRs.[/dim]")

    # Step 2: Compute quantitative metrics
    calculator = MetricsCalculator()
    quantitative = calculator.compute(prs)

    # Step 3: LLM scoring
    llm_scores = []
    if not skip_llm:
        import anthropic

        client = anthropic.Anthropic()
        scorer = LLMScorer(client)

        console.print(f"[dim]Scoring {len(prs)} PRs with Claude...[/dim]")
        for i, pr in enumerate(prs):
            console.print(f"[dim]  ({i+1}/{len(prs)}) PR #{pr['number']}: {pr['title'][:60]}[/dim]")
            diff = gh.fetch_pr_diff(pr["number"])
            files = gh.fetch_pr_files(pr["number"])
            score = scorer.score_pr(pr, diff, files)
            score["pr_number"] = pr["number"]
            score["title"] = pr["title"]
            llm_scores.append(score)

        # Calibration pass
        if len(llm_scores) > 1:
            console.print("[dim]Running calibration pass...[/dim]")
            llm_scores = scorer.calibrate(llm_scores)
    else:
        console.print("[dim]Skipping LLM scoring (--skip-llm).[/dim]")

    # Step 4: Build scorecard
    sc = Scorecard()
    result = sc.compute(quantitative, llm_scores)

    # Step 5: Output
    if json_output:
        output = {
            "repo": repo,
            "weeks": weeks,
            "prs_analyzed": len(prs),
            "dimensions": result["dimensions"],
            "rvi": result["rvi"],
            "top_signal": result["top_signal"],
            "srau_count": result["srau_count"],
            "srau_ratio": result["srau_ratio"],
            "quantitative": quantitative,
            "pr_scores": llm_scores,
        }
        click.echo(json.dumps(output, indent=2, default=str))
    else:
        render_scorecard(
            repo=repo,
            period_weeks=weeks,
            dimensions=result["dimensions"],
            rvi=result["rvi"],
            rvi_trend=result["rvi_trend"],
            top_signal=result["top_signal"],
            srau_count=result["srau_count"],
            srau_ratio=result["srau_ratio"],
            quantitative=quantitative,
            llm_scores=llm_scores,
            console=console,
        )

        if show_prs and llm_scores:
            console.print()
            render_pr_table(llm_scores, console=console)


if __name__ == "__main__":
    main()
