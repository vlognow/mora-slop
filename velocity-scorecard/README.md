# velocity-scorecard

LLM-scored repo velocity measurement. Point it at a GitHub repo, get a seven-dimension scorecard with a 0-100 composite index.

## What it does

Pulls merged PRs for a given period, computes quantitative metrics (throughput, cycle time, quality) from the GitHub API, then sends each PR diff to Claude for the dimensions that require judgment (complexity, impact, business value, SRAU classification). Seven scores roll up into a 0-100 composite Repo Velocity Index (RVI).

## Quick start

```bash
cd velocity-scorecard
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# Configure
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY and GITHUB_TOKEN

# Run
velocity-score vlognow/olapui --weeks 1
```

## Usage

```bash
# Full scorecard with LLM scoring
velocity-score vlognow/olapui --weeks 4

# Show individual PR scores table
velocity-score vlognow/olapui --weeks 1 --show-prs

# Quantitative only (no LLM, no API cost)
velocity-score vlognow/olapui --weeks 4 --skip-llm

# JSON output
velocity-score vlognow/olapui --weeks 2 --json-output

# Verbose logging
velocity-score vlognow/olapui --weeks 1 -v
```

## Architecture

```
src/velocity_scorecard/
├── cli.py              # Click CLI — wires everything together
├── github_client.py    # GitHub API — fetches PRs, diffs, reviews
├── metrics.py          # Quantitative metrics — throughput, cycle time, quality, collaboration
├── llm_scorer.py       # Claude API — scores each PR for complexity, impact, quality, SRAU
├── scorecard.py        # Aggregation — 7 dimension scores (1-10) → weighted RVI (0-100)
└── output.py           # Rich terminal rendering — the scorecard visual
```

### How scoring works

1. **Fetch** — Pull all merged PRs for the period via GitHub search API. Enrich each with PR detail + reviews.
2. **Quantitative metrics** — Compute throughput, cycle time (p50/p90), quality (rework rate), collaboration (AI PR detection from commit markers).
3. **LLM scoring** — For each PR, send the diff + metadata to Claude with an explicit rubric. Get back: technical difficulty (1-10), business value (1-10), code quality (1-10), SRAU classification (yes/no + reasoning).
4. **Calibration** — Send all scores to Claude in one pass to normalize across the cohort. Adjusts outliers.
5. **Aggregate** — Map quantitative + LLM scores into 7 dimensions (1-10 each). Compute weighted RVI (0-100). Generate Top Signal narrative.
6. **Render** — Terminal scorecard with Rich, or JSON for piping.

### Seven dimensions

| Dimension | Source | What it measures |
|-----------|--------|-----------------|
| Throughput | GitHub API | PRs merged, deploy frequency, durable lines |
| Cycle Time | GitHub API | PR open→merge p50/p90, review latency |
| Quality | GitHub API | Change failure rate, rework rate, 30-day line survival |
| Complexity | **LLM** | Algorithmic difficulty, cross-module impact, domain complexity |
| Impact | **LLM** | Business value — feature vs. maintenance vs. tech debt |
| Collaboration | GitHub API | AI PR ratio, review rounds, load distribution |
| Health | Placeholder | Agent readiness, test coverage trend, tech debt (v2) |

Dimensions counterbalance — gaming one hurts another.

### RVI weighting

Quality 20%, Throughput 15%, Cycle Time 15%, Impact 15%, Collaboration 15%, Complexity 10%, Health 10%. Tunable per org.

### SRAU — Significant Repo Advancement Unit

The LLM classifies each PR: does this change compound? Cross-cutting refactor = SRAU. Version bump = not. The SRAU ratio tells you what fraction of throughput is real codebase advancement vs. operational noise.

## Cost

~$0.15 per repo with Claude Sonnet. Weekly scorecard for 10 repos: ~$6/month.

## Auth

Reads from environment variables or `.env` file (via python-dotenv):

- `ANTHROPIC_API_KEY` — Claude API
- `GITHUB_TOKEN` — GitHub API (falls back to `~/.claude.json` PAT if not set)

## Status

First pass experiment. Built in ~12 hours. Validated against 4 vlognow repos (170 PRs). The goal was to test whether LLM scoring adds signal that quantitative metrics miss. It does — see the [Notion proposal](https://www.notion.so/3415356b39718157a26bd926ccb34c54) for full results.
