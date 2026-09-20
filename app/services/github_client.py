"""Клиент GitHub API с mock-режимом без сети."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, Field


class RepoSnapshot(BaseModel):
    full_name: str
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    open_prs: int = 0
    commits_30d: int = 0
    prs_merged_30d: int = 0
    oldest_open_pr_days: int = 0
    contributors: list[str] = Field(default_factory=list)
    contributor_commits: list[int] = Field(default_factory=list)
    stale_items: list[dict] = Field(default_factory=list)


MOCK_SNAPSHOT = RepoSnapshot(
    full_name="octocat/Hello-World",
    stars=120,
    forks=30,
    open_issues=4,
    open_prs=3,
    commits_30d=18,
    prs_merged_30d=6,
    oldest_open_pr_days=21,
    contributors=["alice", "bob", "carol", "dave"],
    contributor_commits=[10, 5, 2, 1],
    stale_items=[
        {"number": 12, "title": "Flaky test on Windows", "days_open": 96, "kind": "issue"},
        {"number": 15, "title": "Docs: outdated quickstart", "days_open": 45, "kind": "issue"},
    ],
)


class GitHubClient:
    """Тонкий клиент: живые данные при токене, иначе фикстуры."""

    def __init__(self, api_url: str, token: str = "", mock_mode: bool = True) -> None:
        self._api_url = api_url.rstrip("/")
        self._token = token
        self._mock_mode = mock_mode

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    async def fetch_snapshot(self, owner: str, repo: str, live: bool = False) -> RepoSnapshot:
        if self._mock_mode or not live or not self._token:
            return MOCK_SNAPSHOT.model_copy(update={"full_name": f"{owner}/{repo}"})
        async with httpx.AsyncClient(base_url=self._api_url, headers=self._headers(), timeout=15.0) as client:
            repo_resp = await client.get(f"/repos/{owner}/{repo}")
            repo_resp.raise_for_status()
            data = repo_resp.json()
            return RepoSnapshot(
                full_name=data.get("full_name", f"{owner}/{repo}"),
                stars=int(data.get("stargazers_count", 0)),
                forks=int(data.get("forks_count", 0)),
                open_issues=int(data.get("open_issues_count", 0)),
            )
