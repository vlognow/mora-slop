use serde::{Deserialize, Serialize};

/// A merged PR with enrichment (detail + reviews) — the shape downstream
/// modules consume.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PullRequest {
    pub number: u64,
    pub title: String,
    pub body: String,
    pub created_at: Option<String>,
    pub merged_at: Option<String>,
    pub user: String,
    pub labels: Vec<String>,
    pub additions: u64,
    pub deletions: u64,
    pub changed_files: u64,
    pub review_comments: u64,
    pub reviews: Vec<Review>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Review {
    pub state: Option<String>,
    pub submitted_at: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChangedFile {
    pub filename: String,
    pub status: String,
    pub additions: u64,
    pub deletions: u64,
    #[serde(default)]
    pub patch: String,
}

// ---------------------------------------------------------------------------
// Raw API response shapes (deserialize targets)
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
pub(super) struct SearchResponse {
    pub items: Vec<SearchItem>,
}

#[derive(Debug, Deserialize)]
pub(super) struct SearchItem {
    pub number: u64,
}

#[derive(Debug, Deserialize)]
pub(super) struct RawUser {
    #[serde(default)]
    pub login: String,
}

#[derive(Debug, Deserialize)]
pub(super) struct RawLabel {
    #[serde(default)]
    pub name: String,
}

#[derive(Debug, Deserialize)]
pub(super) struct RawPull {
    pub number: u64,
    #[serde(default)]
    pub title: String,
    #[serde(default)]
    pub body: Option<String>,
    pub created_at: Option<String>,
    pub merged_at: Option<String>,
    #[serde(default)]
    pub user: Option<RawUser>,
    #[serde(default)]
    pub labels: Vec<RawLabel>,
    #[serde(default)]
    pub additions: u64,
    #[serde(default)]
    pub deletions: u64,
    #[serde(default)]
    pub changed_files: u64,
    #[serde(default)]
    pub review_comments: u64,
}

#[derive(Debug, Deserialize)]
pub(super) struct RawReview {
    #[serde(default)]
    pub state: Option<String>,
    #[serde(default)]
    pub submitted_at: Option<String>,
}

#[derive(Debug, Deserialize)]
pub(super) struct RawFile {
    #[serde(default)]
    pub filename: String,
    #[serde(default)]
    pub status: String,
    #[serde(default)]
    pub additions: u64,
    #[serde(default)]
    pub deletions: u64,
    #[serde(default)]
    pub patch: Option<String>,
}
