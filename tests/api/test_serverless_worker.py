import os
os.environ["LLM_BASE_URL"] = "http://test"
os.environ["LLM_API_KEY"] = "test"
os.environ["LLM_MODEL"] = "test"

import pytest
from unittest.mock import AsyncMock, patch
from app.workers.serverless_worker import async_handler

@pytest.mark.asyncio
async def test_serverless_worker_ping():
    job = {"input": {"ping": True}}
    res = await async_handler(job)
    assert res == {"status": "ok", "service": "mentorai-serverless-worker"}

@pytest.mark.asyncio
async def test_serverless_worker_missing_message():
    job = {"input": {"session_id": "s1", "user_id": "u1"}}
    res = await async_handler(job)
    assert res["status"] == 400
    assert "Missing 'message'" in res["error"]

@pytest.mark.asyncio
@patch("app.agents.orchestrator.Orchestrator.process_student_input", new_callable=AsyncMock)
async def test_serverless_worker_success(mock_process):
    mock_process.return_value = {"type": "checkpoint", "message": "What is binary search?"}
    job = {
        "input": {
            "session_id": "s1",
            "user_id": "u1",
            "message": "Start session"
        }
    }
    res = await async_handler(job)
    assert res["status"] == "success"
    assert res["data"]["message"] == "What is binary search?"
