from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "providers" in data

def test_list_models():
    response = client.get("/models")
    assert response.status_code == 200
    models = response.json()
    assert isinstance(models, list)
    assert len(models) > 0
    assert all("name" in model and "description" in model for model in models)

def test_get_context():
    response = client.post(
        "/context",
        json={
            "query": "Tell me about iPhone 15",
            "model": "mistral"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "context" in data
    assert "metadata" in data
    assert "analysis" in data
    assert "response" in data 