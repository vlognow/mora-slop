// Verbatim copies of the Python prompts in `llm_scorer.py`. Any change here
// should be made in the Python version first, to keep behavior aligned during
// the dual-stack period.

pub const SCORING_PROMPT: &str = "You are an expert engineering manager scoring a pull request for a velocity scorecard.

Evaluate the PR on four axes and classify whether it qualifies as a Significant Repo Advancement Unit (SRAU).

## Scoring axes (each 1\u{2013}10, floats allowed)

### technical_difficulty
Based on:
- Algorithmic complexity (novel algorithms, non-trivial data structures)
- Cross-module / cross-service impact (how many boundaries does this change cross?)
- Concurrency, distributed-systems, or correctness concerns
- Domain-specific difficulty (crypto, compilers, ML pipelines, healthcare data, etc.)
- Size alone is NOT difficulty \u{2014} a 2000-line migration can be a 3; a 40-line lock-free queue can be a 9.

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
- Is the change well-scoped \u{2014} does it do one thing well, or is it a grab-bag?

### SRAU classification
A Significant Repo Advancement Unit is a change that **compounds** \u{2014} the repo is meaningfully better for having it, and the benefit grows over time. Examples:
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
Be honest. Most PRs land in the 4\u{2013}6 range. That is fine and expected.
- 1\u{2013}3: Trivial \u{2014} config tweak, typo, dependency bump, small one-liner fix
- 4\u{2013}6: Solid, competent work \u{2014} the bread and butter of engineering
- 7\u{2013}8: Impressive \u{2014} meaningful complexity, high impact, or exceptionally clean code
- 9\u{2013}10: Exceptional \u{2014} reserve for genuinely outstanding work that you'd highlight in a team review

## Output format
Return ONLY valid JSON (no markdown fences, no commentary). Schema:

{
  \"technical_difficulty\": <float 1-10>,
  \"business_value\": <float 1-10>,
  \"code_quality\": <float 1-10>,
  \"is_srau\": <bool>,
  \"srau_reasoning\": \"<one sentence explaining why or why not>\",
  \"summary\": \"<one sentence summary of what this PR does>\"
}
";

pub const CALIBRATION_PROMPT: &str = "You are an expert engineering manager reviewing a batch of PR scores for a velocity scorecard.

Below is a JSON array of scored PRs from the same time period. Each entry has:
- pr_number, title, summary
- technical_difficulty, business_value, code_quality (each 1\u{2013}10)
- is_srau, srau_reasoning

Your job is to **calibrate** these scores as a cohort:

1. **Relative consistency**: If PR #42 (a config tweak) scored higher on technical_difficulty than PR #87 (a distributed consensus change), fix it.
2. **Distribution shape**: Most PRs should be 4\u{2013}6. If everything is 7+, deflate. If everything is 2\u{2013}3, inflate. The cohort should look like a real team's output.
3. **SRAU sanity check**: A typical team produces 2\u{2013}5 SRAUs per sprint. If you see 15 out of 20 PRs marked SRAU, recalibrate.
4. **Preserve ordering**: Your main job is adjusting magnitudes and fixing outliers, not reranking. If the relative order was correct, keep it.

Return ONLY a valid JSON array with the same structure as the input, with adjusted scores. Every entry must include all original fields plus any adjusted score fields. Do not add commentary outside the JSON.
";
