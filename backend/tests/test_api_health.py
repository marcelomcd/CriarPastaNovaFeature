"""Testes do endpoint de health da API FastAPI."""
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_returns_200():
    """GET /health retorna 200 e status ok."""
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"


def test_health_has_required_keys():
    """Resposta do health contém campos esperados."""
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
