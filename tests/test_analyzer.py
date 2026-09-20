"""Unit-тесты анализатора: без сети, на фикстурах."""

from app.services.analyzer import analyze, health_score, top2_share
from app.services.digest_builder import build_digest
from app.services.github_client import MOCK_SNAPSHOT


def test_top2_share() -> None:
    assert top2_share([10, 5, 2, 1]) == 0.83
    assert top2_share([]) == 0.0


def test_health_score_deterministic() -> None:
    assert health_score(MOCK_SNAPSHOT, stale_days=30) == 56


def test_analyze_and_digest() -> None:
    health = analyze(MOCK_SNAPSHOT, stale_days=30)
    assert health.full_name == "octocat/Hello-World"
    assert health.health_score == 56
    assert len(health.stale) == 2
    digest = build_digest(health)
    assert "health 56/100" in digest
    assert "#12" in digest
