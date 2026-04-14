mod types;

use std::time::Duration;

use chrono::{Duration as ChronoDuration, Utc};
use reqwest::header::{ACCEPT, AUTHORIZATION, HeaderMap, HeaderValue, USER_AGENT};
use reqwest::{Request, Response, StatusCode};
use serde::de::DeserializeOwned;
use tokio::time::sleep;

pub use self::types::{ChangedFile, PullRequest, Review};
use self::types::{RawFile, RawPull, RawReview, SearchResponse};
use crate::error::GithubError;

const BASE_URL: &str = "https://api.github.com";
const DIFF_TRUNCATE_CHARS: usize = 15_000;
const MAX_PAGES: u32 = 20;
const TRUNCATION_MARKER: &str = "\n\n... [truncated]";
const USER_AGENT_STR: &str = concat!("velocity-scorecard/", env!("CARGO_PKG_VERSION"));

pub struct GithubClient {
    owner: String,
    repo: String,
    http: reqwest::Client,
}

impl GithubClient {
    pub fn new(owner: impl Into<String>, repo: impl Into<String>, token: &str) -> Result<Self, GithubError> {
        let mut headers = HeaderMap::new();
        let auth = format!("Bearer {token}");
        let mut auth_val = HeaderValue::from_str(&auth).map_err(|_| GithubError::NoToken)?;
        auth_val.set_sensitive(true);
        headers.insert(AUTHORIZATION, auth_val);
        headers.insert(ACCEPT, HeaderValue::from_static("application/vnd.github+json"));
        headers.insert("X-GitHub-Api-Version", HeaderValue::from_static("2022-11-28"));
        headers.insert(USER_AGENT, HeaderValue::from_static(USER_AGENT_STR));

        let http = reqwest::Client::builder()
            .default_headers(headers)
            .timeout(Duration::from_secs(60))
            .build()?;

        Ok(Self {
            owner: owner.into(),
            repo: repo.into(),
            http,
        })
    }

    // --------------------------------------------------------------
    // Public API
    // --------------------------------------------------------------

    /// Fetch PRs merged within the last `weeks` weeks, enriched with review
    /// data.
    pub async fn fetch_merged_prs(&self, weeks: u32) -> Result<Vec<PullRequest>, GithubError> {
        let since = Utc::now() - ChronoDuration::weeks(weeks as i64);
        let since_str = since.format("%Y-%m-%dT%H:%M:%SZ").to_string();
        let query = format!(
            "repo:{}/{} is:pr is:merged merged:>={}",
            self.owner, self.repo, since_str
        );

        log::info!("Searching merged PRs since {since_str}");

        let params = [
            ("q", query.as_str()),
            ("sort", "updated"),
            ("order", "desc"),
            ("per_page", "100"),
        ];
        let raw_items = self.paginate_search("/search/issues", &params).await?;
        log::info!("Search returned {} PRs", raw_items.len());

        let mut results = Vec::with_capacity(raw_items.len());
        for item in raw_items {
            let n = item.number;
            match self.enrich_pr(n).await {
                Ok(pr) => results.push(pr),
                Err(e) => log::warn!("Failed to fetch details for PR #{n}: {e}"),
            }
        }

        log::info!("Returning {} enriched PRs", results.len());
        Ok(results)
    }

    /// Fetch the raw unified diff for a PR, truncated to fit LLM context.
    pub async fn fetch_pr_diff(&self, pr_number: u64) -> Result<String, GithubError> {
        let path = format!("/repos/{}/{}/pulls/{pr_number}", self.owner, self.repo);
        let req = self
            .http
            .get(format!("{BASE_URL}{path}"))
            .header(ACCEPT, HeaderValue::from_static("application/vnd.github.v3.diff"))
            .build()?;
        let resp = self.send_with_rate_limit(req).await?;
        let resp = check_status(resp, &path).await?;
        let text = resp.text().await?;
        if text.len() <= DIFF_TRUNCATE_CHARS {
            return Ok(text);
        }
        log::info!(
            "PR #{pr_number} diff truncated from {} to {DIFF_TRUNCATE_CHARS} chars",
            text.len()
        );
        let cutoff = char_boundary_floor(&text, DIFF_TRUNCATE_CHARS);
        let mut out = String::with_capacity(cutoff + TRUNCATION_MARKER.len());
        out.push_str(&text[..cutoff]);
        out.push_str(TRUNCATION_MARKER);
        Ok(out)
    }

    pub async fn fetch_pr_files(&self, pr_number: u64) -> Result<Vec<ChangedFile>, GithubError> {
        let path = format!("/repos/{}/{}/pulls/{pr_number}/files", self.owner, self.repo);
        let raw: Vec<RawFile> = self.paginate(&path, &[("per_page", "100")]).await?;
        Ok(raw
            .into_iter()
            .map(|f| ChangedFile {
                filename: f.filename,
                status: f.status,
                additions: f.additions,
                deletions: f.deletions,
                patch: f.patch.unwrap_or_default(),
            })
            .collect())
    }

    // --------------------------------------------------------------
    // Internals
    // --------------------------------------------------------------

    async fn enrich_pr(&self, pr_number: u64) -> Result<PullRequest, GithubError> {
        let detail: RawPull = self
            .get_json(&format!("/repos/{}/{}/pulls/{pr_number}", self.owner, self.repo))
            .await?;
        let raw_reviews: Vec<RawReview> = self
            .paginate(
                &format!("/repos/{}/{}/pulls/{pr_number}/reviews", self.owner, self.repo),
                &[("per_page", "100")],
            )
            .await?;

        Ok(PullRequest {
            number: detail.number,
            title: detail.title,
            body: detail.body.unwrap_or_default(),
            created_at: detail.created_at,
            merged_at: detail.merged_at,
            user: detail.user.map(|u| u.login).unwrap_or_else(|| "unknown".into()),
            labels: detail.labels.into_iter().map(|l| l.name).collect(),
            additions: detail.additions,
            deletions: detail.deletions,
            changed_files: detail.changed_files,
            review_comments: detail.review_comments,
            reviews: raw_reviews
                .into_iter()
                .map(|r| Review {
                    state: r.state,
                    submitted_at: r.submitted_at,
                })
                .collect(),
        })
    }

    async fn get_json<T: DeserializeOwned>(&self, path: &str) -> Result<T, GithubError> {
        let req = self.http.get(format!("{BASE_URL}{path}")).build()?;
        let resp = self.send_with_rate_limit(req).await?;
        let resp = check_status(resp, path).await?;
        Ok(resp.json().await?)
    }

    /// Paginate a flat list endpoint via the `Link: ...; rel="next"` header.
    async fn paginate<T: DeserializeOwned>(&self, path: &str, params: &[(&str, &str)]) -> Result<Vec<T>, GithubError> {
        self.paginate_with(path, params, |body| {
            serde_json::from_slice::<Vec<T>>(body).map_err(Into::into)
        })
        .await
    }

    /// Pagination for `/search/issues`, which returns `{ items: [...] }` per
    /// page.
    async fn paginate_search(
        &self,
        path: &str,
        params: &[(&str, &str)],
    ) -> Result<Vec<self::types::SearchItem>, GithubError> {
        self.paginate_with(path, params, |body| {
            let page: SearchResponse = serde_json::from_slice(body)?;
            Ok(page.items)
        })
        .await
    }

    /// Common pagination driver. The `parse` callback extracts each page's
    /// batch so flat lists and `{ items: [...] }` shapes share the same
    /// loop.
    async fn paginate_with<T, F>(&self, path: &str, params: &[(&str, &str)], parse: F) -> Result<Vec<T>, GithubError>
    where
        F: Fn(&[u8]) -> Result<Vec<T>, GithubError>,
    {
        let mut items: Vec<T> = Vec::new();
        let mut next_url: Option<String> = Some(format!("{BASE_URL}{path}"));

        for page in 0..MAX_PAGES {
            let Some(url) = next_url.take() else { break };
            let builder = self.http.get(&url);
            let builder = if page == 0 { builder.query(params) } else { builder };
            let req = builder.build()?;

            let resp = self.send_with_rate_limit(req).await?;
            let resp = check_status(resp, path).await?;
            next_url = parse_next_link(resp.headers().get("link"));
            let bytes = resp.bytes().await?;
            items.extend(parse(&bytes)?);
        }

        Ok(items)
    }

    /// Send one request with rate-limit handling:
    /// - `X-RateLimit-Remaining < 10` → sleep until reset, then proceed with
    ///   this response.
    /// - HTTP 403 with remaining=0 → sleep and retry once with a cloned
    ///   request.
    async fn send_with_rate_limit(&self, req: Request) -> Result<Response, GithubError> {
        let retry = req.try_clone().ok_or(GithubError::UncloneableRequest)?;
        let resp = self.http.execute(req).await?;

        if let Some(remaining) = header_i64(&resp, "x-ratelimit-remaining")
            && remaining < 10
        {
            let wait = wait_until_reset(&resp, 1);
            log::warn!("Rate limit nearly exhausted ({remaining} remaining). Sleeping {wait}s.");
            sleep(Duration::from_secs(wait)).await;
        }

        if resp.status() == StatusCode::FORBIDDEN && header_i64(&resp, "x-ratelimit-remaining") == Some(0) {
            let wait = wait_until_reset(&resp, 60);
            log::error!("Rate-limited (403). Sleeping {wait}s before retry.");
            sleep(Duration::from_secs(wait)).await;
            return Ok(self.http.execute(retry).await?);
        }

        Ok(resp)
    }
}

fn wait_until_reset(resp: &Response, min_secs: i64) -> u64 {
    let reset = header_i64(resp, "x-ratelimit-reset").unwrap_or(0);
    let now = Utc::now().timestamp();
    (reset - now).max(min_secs) as u64
}

fn char_boundary_floor(s: &str, mut idx: usize) -> usize {
    while idx > 0 && !s.is_char_boundary(idx) {
        idx -= 1;
    }
    idx
}

async fn check_status(resp: Response, path: &str) -> Result<Response, GithubError> {
    if resp.status().is_success() {
        return Ok(resp);
    }
    let status = resp.status().as_u16();
    let body = resp.text().await.unwrap_or_default();
    Err(GithubError::Status {
        status,
        path: path.to_string(),
        body,
    })
}

fn header_i64(resp: &Response, name: &str) -> Option<i64> {
    resp.headers().get(name)?.to_str().ok()?.parse::<i64>().ok()
}

/// Parse the `rel="next"` URL out of a GitHub `Link` header.
fn parse_next_link(link: Option<&HeaderValue>) -> Option<String> {
    let s = link?.to_str().ok()?;
    for part in s.split(',') {
        if part.contains(r#"rel="next""#) {
            let url = part.split(';').next()?.trim();
            let url = url.trim_start_matches('<').trim_end_matches('>');
            return Some(url.to_string());
        }
    }
    None
}
