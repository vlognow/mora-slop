"""Terminal output rendering for the velocity scorecard."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def render_scorecard(
    repo: str,
    period_weeks: int,
    dimensions: dict[str, float],
    rvi: float,
    rvi_trend: float | None,
    top_signal: str,
    srau_count: int,
    srau_ratio: float,
    quantitative: dict,
    llm_scores: list[dict],
    console: Console | None = None,
) -> None:
    """Render the velocity scorecard to the terminal."""
    if console is None:
        console = Console()

    # Build the bar chart lines
    lines = []
    lines.append(f"  VELOCITY SCORECARD — {repo}")
    lines.append(f"  Period: last {period_weeks} weeks")
    lines.append("")

    dim_labels = {
        "throughput": ("Throughput", _throughput_detail(quantitative)),
        "cycle_time": ("Cycle Time", _cycle_time_detail(quantitative)),
        "quality": ("Quality", _quality_detail(quantitative)),
        "complexity": ("Complexity", _complexity_detail(llm_scores)),
        "impact": ("Impact", _impact_detail(llm_scores)),
        "collaboration": ("Collaboration", _collab_detail(quantitative)),
        "health": ("Health", ""),
    }

    for key, score in dimensions.items():
        label, detail = dim_labels.get(key, (key, ""))
        bar = _bar(score)
        lines.append(f"  {label:<15} {bar}  {score:.1f}  {detail}")

    lines.append("")

    # Show directional arrow if we have a prior RVI to compare against
    trend_str = ""
    if rvi_trend is not None:
        arrow = "\u2191" if rvi_trend > 0 else "\u2193" if rvi_trend < 0 else "\u2192"
        trend_str = f"  ({arrow} {abs(rvi_trend):.0f})"
    lines.append(f"  RVI: {rvi:.0f} / 100{trend_str}")

    lines.append(f"  SRAUs: {srau_count} of {len(llm_scores)} PRs ({srau_ratio:.0%})")
    lines.append("")
    lines.append(f"  Top Signal: {top_signal}")

    content = "\n".join(lines)
    panel = Panel(
        content,
        border_style="green",
        padding=(1, 2),
    )
    console.print(panel)


def render_pr_table(llm_scores: list[dict], console: Console | None = None) -> None:
    """Render a table of individual PR scores."""
    if console is None:
        console = Console()

    table = Table(title="PR Scores", show_lines=False)
    table.add_column("#", style="dim", width=6)
    table.add_column("Title", max_width=50)
    table.add_column("Diff", justify="right", width=6)
    table.add_column("Cmplx", justify="right", width=5)
    table.add_column("Value", justify="right", width=5)
    table.add_column("Qlty", justify="right", width=5)
    table.add_column("SRAU", width=4)

    for s in sorted(llm_scores, key=lambda x: x.get("technical_difficulty", 0), reverse=True):
        srau = "\u2713" if s.get("is_srau") else ""
        table.add_row(
            str(s.get("pr_number", "?")),
            _truncate(s.get("summary", s.get("title", "")), 50),
            f"{s.get('difficulty_color', '')}{s.get('technical_difficulty', 0):.1f}",
            f"{s.get('technical_difficulty', 0):.1f}",
            f"{s.get('business_value', 0):.1f}",
            f"{s.get('code_quality', 0):.1f}",
            srau,
        )

    console.print(table)


def _bar(score: float, width: int = 10) -> str:
    """Generate a bar chart string for a score 1-10."""
    filled = int(round(score))
    filled = max(0, min(width, filled))
    return "\u2588" * filled + "\u2591" * (width - filled)


def _truncate(s: str, length: int) -> str:
    """Truncate string with an ellipsis if it exceeds length."""
    return s[:length - 1] + "\u2026" if len(s) > length else s


def _throughput_detail(q: dict) -> str:
    t = q.get("throughput", {})
    return f"{t.get('prs_merged', 0)} PRs merged"


def _cycle_time_detail(q: dict) -> str:
    ct = q.get("cycle_time", {})
    median = ct.get("median_hours", 0)
    p90 = ct.get("p90_hours", 0)
    return f"p50: {_fmt_hours(median)}, p90: {_fmt_hours(p90)}"


def _quality_detail(q: dict) -> str:
    qual = q.get("quality", {})
    rework = qual.get("rework_rate", 0)
    return f"{rework:.1%} rework"


def _complexity_detail(scores: list[dict]) -> str:
    if not scores:
        return ""
    avg = sum(s.get("technical_difficulty", 0) for s in scores) / len(scores)
    return f"avg {avg:.1f}"


def _impact_detail(scores: list[dict]) -> str:
    if not scores:
        return ""
    avg = sum(s.get("business_value", 0) for s in scores) / len(scores)
    return f"avg {avg:.1f}"


def _collab_detail(q: dict) -> str:
    c = q.get("collaboration", {})
    ratio = c.get("ai_pr_ratio", 0)
    count = c.get("ai_pr_count", 0)
    return f"{count} AI PRs ({ratio:.0%})"


def _fmt_hours(h: float) -> str:
    """Format hours as minutes, hours, or days for display."""
    if h < 1:
        return f"{h * 60:.0f}m"
    if h < 48:
        return f"{h:.0f}h"
    return f"{h / 24:.1f}d"
