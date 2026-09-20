"""Эндпоинты анализа репозиториев."""

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.services.analyzer import RepoHealth, analyze
from app.services.digest_builder import build_digest
from app.services.github_client import GitHubClient

router = APIRouter()


def get_client(settings: Settings = Depends(get_settings)) -> GitHubClient:
    return GitHubClient(
        api_url=settings.github_api_url,
        token=settings.github_token,
        mock_mode=settings.mock_mode,
    )


@router.get("/repos/{owner}/{repo}")
async def repo_metrics(
    owner: str,
    repo: str,
    live: bool = False,
    settings: Settings = Depends(get_settings),
    client: GitHubClient = Depends(get_client),
) -> dict:
    snapshot = await client.fetch_snapshot(owner, repo, live=live)
    health = analyze(snapshot, stale_days=settings.stale_days)
    return health.model_dump()


@router.get("/repos/{owner}/{repo}/digest")
async def repo_digest(
    owner: str,
    repo: str,
    live: bool = False,
    settings: Settings = Depends(get_settings),
    client: GitHubClient = Depends(get_client),
) -> dict:
    snapshot = await client.fetch_snapshot(owner, repo, live=live)
    health: RepoHealth = analyze(snapshot, stale_days=settings.stale_days)
    payload = health.model_dump()
    payload["digest_md"] = build_digest(health)
    return payload
