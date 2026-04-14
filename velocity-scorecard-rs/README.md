# velocity-scorecard (Rust)

LLM-scored repo velocity scorecard. Rust port of the Python `velocity-scorecard`
with parallel PR scoring via `tokio`.

Binary: `velocity-score` (same as the Python version).

## Install

```bash
cargo install --path .
```

## Setup

```bash
cp .env.example .env
# Fill in ANTHROPIC_API_KEY and GITHUB_TOKEN (or rely on ~/.claude.json for GitHub)
```

## Usage

```bash
velocity-score owner/repo --weeks 4
velocity-score owner/repo --weeks 1 --show-prs
velocity-score owner/repo --weeks 4 --skip-llm
velocity-score owner/repo --weeks 2 --json-output
velocity-score owner/repo --weeks 1 --concurrency 10 -v
```

### Flags

| Flag | Default | Description |
|---|---|---|
| `--weeks N` | 4 | Analysis window |
| `--show-prs` | off | Render per-PR score table |
| `--json-output` | off | Emit JSON instead of rendered panels |
| `--skip-llm` | off | Quantitative metrics only |
| `--concurrency N` | 5 | Max parallel Anthropic API calls |
| `-v`, `--verbose` | off | Debug logging |

## What it scores

Seven dimensions, weighted into a composite RVI (0–100):

- **Quality** 20%, **Throughput** 15%, **Cycle Time** 15%, **Impact** 15%,
  **Collaboration** 15%, **Complexity** 10%, **Health** 10%.

LLM pass scores each PR on technical difficulty, business value, code quality,
plus classifies it as a **SRAU** (Significant Repo Advancement Unit).
