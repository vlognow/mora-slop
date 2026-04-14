pub mod prompts;
mod types;

use std::time::Duration;

use reqwest::header::{CONTENT_TYPE, HeaderMap, HeaderValue};
use serde::Deserialize;
use tokio::time::sleep;

pub use self::types::PrScore;
use self::types::RawScore;
use crate::error::LlmError;
use crate::github::{ChangedFile, PullRequest};

const ANTHROPIC_URL: &str = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION: &str = "2023-06-01";
const MAX_DIFF_CHARS: usize = 120_000;

pub struct LlmScorer {
    http: reqwest::Client,
    model: String,
    max_retries: u32,
}

impl LlmScorer {
    pub fn new(api_key: &str, model: impl Into<String>, max_retries: u32) -> Result<Self, LlmError> {
        let mut headers = HeaderMap::new();
        let mut key_val = HeaderValue::from_str(api_key).map_err(|_| LlmError::NoApiKey)?;
        key_val.set_sensitive(true);
        headers.insert("x-api-key", key_val);
        headers.insert("anthropic-version", HeaderValue::from_static(ANTHROPIC_VERSION));
        headers.insert(CONTENT_TYPE, HeaderValue::from_static("application/json"));

        let http = reqwest::Client::builder()
            .default_headers(headers)
            .timeout(Duration::from_secs(120))
            .build()?;

        Ok(Self {
            http,
            model: model.into(),
            max_retries,
        })
    }

    /// Score a single PR. Builds the user message from PR metadata + diff +
    /// files, calls Claude, parses JSON, attaches metadata.
    pub async fn score_pr(&self, pr: &PullRequest, diff: &str, files: &[ChangedFile]) -> Result<PrScore, LlmError> {
        let user_message = build_scoring_message(pr, diff, files);
        let raw = self.call_api(prompts::SCORING_PROMPT, &user_message, 4096).await?;
        let parsed: RawScore = parse_json(&raw)?;
        Ok(PrScore {
            pr_number: pr.number,
            title: pr.title.clone(),
            technical_difficulty: parsed.technical_difficulty,
            business_value: parsed.business_value,
            code_quality: parsed.code_quality,
            is_srau: parsed.is_srau,
            srau_reasoning: parsed.srau_reasoning,
            summary: parsed.summary,
        })
    }

    /// Calibrate a cohort of scored PRs in one batched call. Falls back to the
    /// uncalibrated scores on parse or API failure.
    pub async fn calibrate(&self, scores: Vec<PrScore>) -> Vec<PrScore> {
        if scores.is_empty() {
            return scores;
        }

        let user_message = match serde_json::to_string_pretty(&scores) {
            Ok(s) => s,
            Err(e) => {
                log::warn!("Calibration: failed to serialize scores ({e}); returning originals");
                return scores;
            }
        };

        let raw = match self.call_api(prompts::CALIBRATION_PROMPT, &user_message, 8192).await {
            Ok(r) => r,
            Err(e) => {
                log::warn!("Calibration failed ({e}); returning uncalibrated scores");
                return scores;
            }
        };

        #[derive(Deserialize)]
        struct CalibratedEntry {
            pr_number: u64,
            #[serde(default)]
            technical_difficulty: Option<f64>,
            #[serde(default)]
            business_value: Option<f64>,
            #[serde(default)]
            code_quality: Option<f64>,
            #[serde(default)]
            is_srau: Option<bool>,
        }

        let calibrated: Vec<CalibratedEntry> = match parse_json(&raw) {
            Ok(c) => c,
            Err(e) => {
                log::warn!("Calibration parse failed ({e}); returning uncalibrated scores");
                return scores;
            }
        };

        let mut scores = scores;
        for cal in calibrated {
            if let Some(existing) = scores.iter_mut().find(|s| s.pr_number == cal.pr_number) {
                if let Some(v) = cal.technical_difficulty {
                    existing.technical_difficulty = v;
                }
                if let Some(v) = cal.business_value {
                    existing.business_value = v;
                }
                if let Some(v) = cal.code_quality {
                    existing.code_quality = v;
                }
                if let Some(v) = cal.is_srau {
                    existing.is_srau = v;
                }
            }
        }
        scores
    }

    // --------------------------------------------------------------
    // Internals
    // --------------------------------------------------------------

    async fn call_api(&self, system: &str, user_message: &str, max_tokens: u32) -> Result<String, LlmError> {
        #[derive(Deserialize)]
        struct ApiResponse {
            content: Vec<ContentBlock>,
        }
        #[derive(Deserialize)]
        struct ContentBlock {
            #[serde(default)]
            text: String,
        }

        let body = serde_json::json!({
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{ "role": "user", "content": user_message }],
        });

        let max_retries = self.max_retries;
        let mut last_err: Option<String> = None;

        for attempt in 1..=max_retries {
            let wait_secs = 1_u64 << attempt; // 2s, 4s, 8s
            let resp = match self.http.post(ANTHROPIC_URL).json(&body).send().await {
                Ok(r) => r,
                Err(e) => {
                    log::warn!("Connection error (attempt {attempt}/{max_retries}): {e}; retrying in {wait_secs}s");
                    last_err = Some(e.to_string());
                    sleep(Duration::from_secs(wait_secs)).await;
                    continue;
                }
            };

            let status = resp.status();
            if status.is_success() {
                let api: ApiResponse = resp.json().await?;
                return Ok(api.content.into_iter().next().map(|c| c.text).unwrap_or_default());
            }

            let code = status.as_u16();
            let body_text = resp.text().await.unwrap_or_default();
            let retryable = code == 429 || code >= 500;

            if !retryable {
                log::error!("Anthropic API client error {code}: {body_text}");
                return Err(LlmError::ApiStatus {
                    status: code,
                    body: body_text,
                });
            }

            log::warn!("Anthropic API {code} (attempt {attempt}/{max_retries}); retrying in {wait_secs}s");
            last_err = Some(format!("status {code}: {body_text}"));
            sleep(Duration::from_secs(wait_secs)).await;
        }

        Err(LlmError::RetriesExhausted {
            attempts: max_retries,
            last: last_err.unwrap_or_else(|| "unknown error".into()),
        })
    }
}

// --------------------------------------------------------------------
// Message construction
// --------------------------------------------------------------------

fn build_scoring_message(pr: &PullRequest, diff: &str, files: &[ChangedFile]) -> String {
    use std::fmt::Write;

    let mut file_summary = String::new();
    for (i, f) in files.iter().enumerate() {
        if i > 0 {
            file_summary.push('\n');
        }
        let _ = write!(file_summary, "  - {} (+{} / -{})", f.filename, f.additions, f.deletions);
    }

    let labels = if pr.labels.is_empty() {
        "(none)".into()
    } else {
        pr.labels.join(", ")
    };

    let (truncated_diff, omitted) = if diff.len() > MAX_DIFF_CHARS {
        let end = char_boundary_floor(diff, MAX_DIFF_CHARS);
        (&diff[..end], diff.len() - end)
    } else {
        (diff, 0)
    };

    let truncation_note = if omitted > 0 {
        format!("\n\n... [diff truncated \u{2014} {omitted} chars omitted]")
    } else {
        String::new()
    };

    let number = pr.number;
    let title = if pr.title.is_empty() {
        "(no title)"
    } else {
        pr.title.as_str()
    };
    let user = &pr.user;
    let created = pr.created_at.as_deref().unwrap_or("?");
    let merged = pr.merged_at.as_deref().unwrap_or("?");
    let additions = pr.additions;
    let deletions = pr.deletions;
    let changed_files = pr.changed_files;
    let review_comments = pr.review_comments;
    let body = if pr.body.is_empty() {
        "(no description)"
    } else {
        pr.body.as_str()
    };
    let files_section = if file_summary.is_empty() {
        "(none)"
    } else {
        file_summary.as_str()
    };

    format!(
        "## Pull Request #{number}

**Title**: {title}
**Author**: {user}
**Created**: {created}
**Merged**: {merged}
**Labels**: {labels}
**Stats**: +{additions} / -{deletions} across {changed_files} files
**Review comments**: {review_comments}

### Description
{body}

### Changed files
{files_section}

### Diff
```
{truncated_diff}{truncation_note}
```
"
    )
}

fn char_boundary_floor(s: &str, mut idx: usize) -> usize {
    while idx > 0 && !s.is_char_boundary(idx) {
        idx -= 1;
    }
    idx
}

// --------------------------------------------------------------------
// JSON parsing with markdown-fence + outermost-brace fallbacks
// --------------------------------------------------------------------

fn parse_json<T: serde::de::DeserializeOwned>(raw: &str) -> Result<T, LlmError> {
    let text = strip_fences(raw.trim());

    if let Ok(v) = serde_json::from_str::<T>(text) {
        return Ok(v);
    }

    // Fallback: extract the outermost JSON structure.
    for (open, close) in [('[', ']'), ('{', '}')] {
        let Some(start) = text.find(open) else { continue };
        let Some(end) = text.rfind(close) else { continue };
        if end > start
            && let Ok(v) = serde_json::from_str::<T>(&text[start..=end])
        {
            return Ok(v);
        }
    }

    let preview: String = raw.chars().take(500).collect();
    log::error!("Failed to parse Claude response as JSON. Raw (first 500 chars): {preview}");
    Err(LlmError::Parse(raw.chars().take(200).collect()))
}

/// Strip surrounding markdown fences without allocating.
fn strip_fences(text: &str) -> &str {
    let body = match text.strip_prefix("```") {
        Some(after) => after.find('\n').map_or(after, |nl| &after[nl + 1..]),
        None => text,
    };
    body.strip_suffix("```").unwrap_or(body).trim()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_json_strips_markdown_fences() {
        let raw = "```json\n{\"technical_difficulty\": 5.0, \"business_value\": 4.0, \"code_quality\": 6.0, \"is_srau\": false, \"srau_reasoning\": \"\", \"summary\": \"\"}\n```";
        let v: RawScore = parse_json(raw).expect("should parse");
        assert_eq!(v.technical_difficulty, 5.0);
    }

    #[test]
    fn parse_json_falls_back_to_outermost_braces() {
        let raw = "here you go:\n{\"technical_difficulty\": 7.0, \"business_value\": 8.0, \"code_quality\": 5.0, \"is_srau\": true}";
        let v: serde_json::Value = parse_json(raw).expect("should parse");
        assert_eq!(v["technical_difficulty"], 7.0);
    }
}
