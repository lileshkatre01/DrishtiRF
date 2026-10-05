from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["project"] == "DrishtiRF"
    assert "version" in data

def test_root_endpoint():
    # When frontend/dist is built, / serves SPA HTML and /api serves API JSON info
    response_api = client.get("/api")
    if response_api.status_code == 200:
        data = response_api.json()
        assert "Welcome" in data["message"]
    
    response_root = client.get("/")
    assert response_root.status_code == 200
