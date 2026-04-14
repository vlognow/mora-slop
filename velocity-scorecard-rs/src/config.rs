use std::{env, fs};

use crate::error::GithubError;

/// Resolve a GitHub token from the environment, falling back to
/// `~/.claude.json`.
///
/// Fallback path mirrors the Python implementation:
/// `mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN`.
pub fn resolve_github_token() -> Result<String, GithubError> {
    if let Ok(tok) = env::var("GITHUB_TOKEN")
        && !tok.is_empty()
    {
        return Ok(tok);
    }

    let Some(home) = dirs_next::home_dir() else {
        return Err(GithubError::NoToken);
    };
    let path = home.join(".claude.json");
    if !path.exists() {
        return Err(GithubError::NoToken);
    }

    let content = fs::read_to_string(&path)?;
    let data: serde_json::Value = serde_json::from_str(&content)?;
    let token = data
        .get("mcpServers")
        .and_then(|v| v.get("github"))
        .and_then(|v| v.get("env"))
        .and_then(|v| v.get("GITHUB_PERSONAL_ACCESS_TOKEN"))
        .and_then(|v| v.as_str());

    match token {
        Some(t) if !t.is_empty() => Ok(t.to_string()),
        _ => Err(GithubError::NoToken),
    }
}

pub fn resolve_anthropic_key() -> Option<String> {
    env::var("ANTHROPIC_API_KEY").ok().filter(|s| !s.is_empty())
}
