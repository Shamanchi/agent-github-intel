"""Анализ снапшота репозитория в метрики здоровья."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.github_client import RepoSnapshot


class RepoHealth(BaseModel):
    full_name: str
    health_score: int
    activity: dict
    review_load: dict
    bus_factor: dict
    stale: list[dict]


def top2_share(contributor_commits: list[int]) -> float:
    total = sum(contributor_commits)
    if total <= 0:
        return 0.0
    top2 = sum(sorted(contributor_commits, reverse=True)[:2])
    return round(top2 / total, 2)


def health_score(snapshot: RepoSnapshot, stale_days: int = 30) -> int:
    """Эвристика 0..100: активность + ревью + bus factor. Детерминирована для тестов."""
    score = 50
    score += min(snapshot.commits_30d, 20)
    score += min(snapshot.prs_merged_30d * 2, 12)
    score -= min(snapshot.open_prs * 3, 15)
    score -= min(snapshot.oldest_open_pr_days // 7, 10)
    stale_count = sum(1 for item in snapshot.stale_items if item.get("days_open", 0) >= stale_days)
    score -= min(stale_count * 4, 12)
    share = top2_share(snapshot.contributor_commits)
    if share >= 0.9:
        score -= 8
    elif share >= 0.75:
        score -= 4
    return max(0, min(100, score))


def analyze(snapshot: RepoSnapshot, stale_days: int = 30) -> RepoHealth:
    share = top2_share(snapshot.contributor_commits)
    stale = [item for item in snapshot.stale_items if item.get("days_open", 0) >= stale_days]
    return RepoHealth(
        full_name=snapshot.full_name,
        health_score=health_score(snapshot, stale_days),
        activity={
            "stars": snapshot.stars,
            "forks": snapshot.forks,
            "commits_30d": snapshot.commits_30d,
            "prs_merged_30d": snapshot.prs_merged_30d,
        },
        review_load={
            "open_prs": snapshot.open_prs,
            "oldest_open_pr_days": snapshot.oldest_open_pr_days,
        },
        bus_factor={
            "top_contributors": snapshot.contributors[:2],
            "top2_share": share,
        },
        stale=stale,
    )
