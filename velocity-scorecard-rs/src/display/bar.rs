const FULL_BLOCK: &str = "\u{2588}";
const LIGHT_SHADE: &str = "\u{2591}";

/// Unicode bar chart for a 1–10 score: `score.round()` full blocks then light
/// shade to `width`.
pub fn bar(score: f64, width: usize) -> String {
    let filled = (score.round() as i64).clamp(0, width as i64) as usize;
    let mut out = String::with_capacity(width * FULL_BLOCK.len());
    out.push_str(&FULL_BLOCK.repeat(filled));
    out.push_str(&LIGHT_SHADE.repeat(width - filled));
    out
}

/// Format hours for display: minutes below 1h, whole hours below 2 days, days
/// above that.
pub fn fmt_hours(h: f64) -> String {
    if h < 1.0 {
        format!("{:.0}m", h * 60.0)
    } else if h < 48.0 {
        format!("{h:.0}h")
    } else {
        format!("{:.1}d", h / 24.0)
    }
}

pub fn truncate(s: &str, max_chars: usize) -> String {
    let n = s.chars().count();
    if n <= max_chars {
        return s.to_string();
    }
    let mut out: String = s.chars().take(max_chars.saturating_sub(1)).collect();
    out.push('\u{2026}');
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bar_widths() {
        assert_eq!(bar(0.0, 10).chars().count(), 10);
        assert_eq!(bar(10.0, 10), FULL_BLOCK.repeat(10));
        assert_eq!(
            bar(5.0, 10),
            format!("{}{}", FULL_BLOCK.repeat(5), LIGHT_SHADE.repeat(5))
        );
    }

    #[test]
    fn fmt_hours_branches() {
        assert_eq!(fmt_hours(0.5), "30m");
        assert_eq!(fmt_hours(4.0), "4h");
        assert_eq!(fmt_hours(72.0), "3.0d");
    }
}
