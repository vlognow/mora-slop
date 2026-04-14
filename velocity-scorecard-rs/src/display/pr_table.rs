use std::io::{self, Write};

use owo_colors::OwoColorize;
use tabwriter::TabWriter;

use super::bar::truncate;
use crate::llm::PrScore;

pub fn render_pr_table(scores: &[PrScore]) -> io::Result<()> {
    let mut sorted: Vec<&PrScore> = scores.iter().collect();
    sorted.sort_by(|a, b| {
        b.technical_difficulty
            .partial_cmp(&a.technical_difficulty)
            .unwrap_or(std::cmp::Ordering::Equal)
    });

    let mut wtr = TabWriter::new(io::stdout()).ansi(true);
    writeln!(
        wtr,
        "{}\t{}\t{}\t{}\t{}\t{}",
        "#".bold().yellow(),
        "Title".bold().yellow(),
        "Cmplx".bold().yellow(),
        "Value".bold().yellow(),
        "Qlty".bold().yellow(),
        "SRAU".bold().yellow(),
    )?;
    writeln!(wtr, "----\t-----\t-----\t-----\t----\t----")?;
    for s in sorted {
        let title = if s.summary.is_empty() { &s.title } else { &s.summary };
        let srau = if s.is_srau {
            "\u{2713}".green().to_string()
        } else {
            String::new()
        };
        writeln!(
            wtr,
            "{}\t{}\t{:.1}\t{:.1}\t{:.1}\t{}",
            s.pr_number,
            truncate(title, 60),
            s.technical_difficulty,
            s.business_value,
            s.code_quality,
            srau,
        )?;
    }
    wtr.flush()?;
    Ok(())
}
