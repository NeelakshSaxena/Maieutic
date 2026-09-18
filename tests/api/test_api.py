import os
os.environ["LLM_BASE_URL"] = "http://test"
os.environ["LLM_API_KEY"] = "test"
os.environ["LLM_MODEL"] = "test"

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("app.agents.orchestrator.Orchestrator.process_student_input", new_callable=AsyncMock)
def test_chat_endpoint(mock_process):
    mock_process.return_value = {
        "type": "new_plan",
        "next_checkpoint": type("Checkpoint", (), {"model_dump": lambda: {"id": "cp1", "task": "Learn FastAPI"}})
    }
    
    response = client.post("/api/chat", json={
        "user_id": "test_user",
        "session_id": "sess123",
        "message": "I want to learn FastAPI"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "new_plan"
    assert data["next_checkpoint"]["id"] == "cp1"
