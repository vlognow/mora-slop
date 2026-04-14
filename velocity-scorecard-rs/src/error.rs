use thiserror::Error;

#[derive(Debug, Error)]
pub enum GithubError {
    #[error("HTTP error: {0}")]
    Http(#[from] reqwest::Error),
    #[error("GitHub returned {status} for {path}: {body}")]
    Status { status: u16, path: String, body: String },
    #[error("request body was not cloneable (reqwest streamed body)")]
    UncloneableRequest,
    #[error(
        "No GitHub token found: set GITHUB_TOKEN or configure mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN in ~/.claude.json"
    )]
    NoToken,
    #[error("JSON parse error: {0}")]
    Json(#[from] serde_json::Error),
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
}

#[derive(Debug, Error)]
pub enum LlmError {
    #[error("HTTP error: {0}")]
    Http(#[from] reqwest::Error),
    #[error("Anthropic API error (status {status}): {body}")]
    ApiStatus { status: u16, body: String },
    #[error("Anthropic API call failed after {attempts} attempts: {last}")]
    RetriesExhausted { attempts: u32, last: String },
    #[error("Failed to parse LLM response as JSON: {0}")]
    Parse(String),
    #[error("Missing ANTHROPIC_API_KEY")]
    NoApiKey,
}
