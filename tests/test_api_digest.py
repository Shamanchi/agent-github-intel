"""API-тесты без сети: TestClient + mock-фикстуры."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_health(client: TestClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_repo_digest_mock(client: TestClient) -> None:
    resp = client.get("/api/v1/repos/octocat/Hello-World/digest")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["health_score"] == 56
    assert "digest_md" in payload
    assert "octocat/Hello-World" in payload["digest_md"]


@pytest.mark.integration()
def test_repo_digest_live_shape(client: TestClient) -> None:
    """Интеграционный по маркеру: форма та же, данные mock (без сети по умолчанию)."""
    resp = client.get("/api/v1/repos/octocat/Hello-World/digest?live=false")
    assert resp.status_code == 200
    assert resp.json()["activity"]["commits_30d"] == 18
