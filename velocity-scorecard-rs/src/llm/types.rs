use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PrScore {
    pub pr_number: u64,
    pub title: String,
    pub technical_difficulty: f64,
    pub business_value: f64,
    pub code_quality: f64,
    pub is_srau: bool,
    #[serde(default)]
    pub srau_reasoning: String,
    #[serde(default)]
    pub summary: String,
}

/// What the SCORING prompt returns. Metadata (`pr_number`, `title`) is attached
/// after parsing.
#[derive(Debug, Clone, Deserialize)]
pub(super) struct RawScore {
    pub technical_difficulty: f64,
    pub business_value: f64,
    pub code_quality: f64,
    pub is_srau: bool,
    #[serde(default)]
    pub srau_reasoning: String,
    #[serde(default)]
    pub summary: String,
}
