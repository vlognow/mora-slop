# velocity-scorecard

LLM-scored repo velocity measurement. Point it at a GitHub repo, get a seven-dimension scorecard.

## What it does

Pulls merged PRs for a given period, computes quantitative metrics (throughput, cycle time, quality) from the GitHub API, then sends each PR diff to Claude for the dimensions that require judgment (complexity, impact, business value, SRAU classification). Seven scores roll up into a 0-100 composite Repo Velocity Index (RVI).

## Quick start

```bash
# Setup
cd velocity-scorecard
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# Configure (copy and fill in your keys)
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY and GITHUB_TOKEN

# Run
velocity-score vlognow/olapui --weeks 4
```

## Usage

```bash
# Full scorecard with LLM scoring
velocity-score vlognow/olapui --weeks 4

# Show individual PR scores table
velocity-score vlognow/olapui --weeks 1 --show-prs

# Quantitative only (skip LLM, no API cost)
velocity-score vlognow/olapui --weeks 4 --skip-llm

# JSON output for piping
velocity-score vlognow/olapui --weeks 2 --json-output

# Verbose logging
velocity-score vlognow/olapui --weeks 1 -v
```

## Seven dimensions

| Dimension | What it measures | Source |
|-----------|-----------------|--------|
| Throughput | How much work flows through | GitHub API |
| Cycle Time | How fast, start to done | GitHub API |
| Quality | Is the work durable | GitHub API |
| Complexity | How hard is the work | LLM (Claude) |
| Impact | Pointed at business value | LLM (Claude) |
| Collaboration | Humans + agents working well | GitHub API + markers |
| Health | Codebase getting easier to work with | Placeholder (v2) |

Dimensions are designed to counterbalance — gaming one hurts another.

## RVI weighting

Quality 20%, Throughput 15%, Cycle Time 15%, Impact 15%, Collaboration 15%, Complexity 10%, Health 10%. Tunable.

## SRAU — Significant Repo Advancement Unit

Not every PR matters equally. The LLM classifies each PR as an SRAU or not. An SRAU is a change that compounds — cross-cutting refactor, end-to-end feature, architectural guardrail. Not a typo fix or version bump. The SRAU ratio tells you what fraction of your throughput is actually advancing the codebase.

## Architecture

```
src/velocity_scorecard/
├── cli.py              # Click entrypoint
├── github_client.py    # GitHub API — PR fetching, diffs, reviews
├── metrics.py          # Quantitative dimension calculations
├── llm_scorer.py       # Claude API — scoring prompts, calibration
├── scorecard.py        # Dimension aggregation, RVI, Top Signal
└── output.py           # Rich terminal rendering
```

## Cost

~$0.15 per repo analysis using Claude Sonnet. A weekly scorecard for 10 repos costs ~$6/month.

## Auth

The tool reads credentials from environment variables (or `.env` file via python-dotenv):

- `ANTHROPIC_API_KEY` — for Claude API scoring
- `GITHUB_TOKEN` — for GitHub API access (falls back to `~/.claude.json` if not set)

## Status

First pass experiment. The goal isn't a product — it's a test: does LLM scoring add signal that quantitative metrics miss?
