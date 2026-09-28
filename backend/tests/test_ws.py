import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_websocket_connection():
    job_id = "test-ws-job-123"
    with client.websocket_connect(f"/api/ws/jobs/{job_id}") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "CONNECTION_ESTABLISHED"
        assert data["job_id"] == job_id

        # Send ping action
        websocket.send_json({"action": "ping"})
        response = websocket.receive_json()
        assert response["type"] == "pong"
        assert response["job_id"] == job_id
