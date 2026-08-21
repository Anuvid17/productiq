import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()

    assert data.get("status") == "ok"
    assert data.get("service") == "ProductIQ"
    assert "database" in data
    assert "connected" in data["database"]
    assert "ollama" in data
    assert "available" in data["ollama"]
    assert data["ollama"].get("model") == "llama3.1"
