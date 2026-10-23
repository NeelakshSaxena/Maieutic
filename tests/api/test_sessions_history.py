import os
os.environ["LLM_BASE_URL"] = "http://test"
os.environ["LLM_API_KEY"] = "test"
os.environ["LLM_MODEL"] = "test"

import uuid
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.db.database import SessionLocal
from app.main import app
from app.schemas.planner_schemas import Checkpoint
from app.services.student_brain import StudentBrainService

client = TestClient(app)

PLAN = {
    "learning_objectives": "Understand variables",
    "concepts": [{"id": "c1", "name": "Variables", "description": "Named values"}],
    "dependencies": [],
    "checkpoints": [
        {"id": "cp1", "concept_id": "c1", "task": "Explain a variable", "success_criteria": "Mentions names and values"},
        {"id": "cp2", "concept_id": "c1", "task": "Reassign one", "success_criteria": "Mentions reassignment"},
    ],
}


def _make_session(user_id: str, session_id: str, status: str = "active", current: str = "cp1"):
    db = SessionLocal()
    try:
        brain = StudentBrainService(db=db)
        s = brain.create_session(user_id=user_id, goal="Learn variables", learning_plan=PLAN,
                                 current_checkpoint_id=current, session_id=session_id)
        if status != "active":
            brain.update_session(s.id, status=status)
    finally:
        db.close()


def test_list_sessions_empty_for_unknown_user():
    r = client.get("/api/sessions", params={"user_id": f"nobody-{uuid.uuid4()}"})
    assert r.status_code == 200
    assert r.json()["sessions"] == []


def test_list_sessions_returns_only_that_users_sessions_with_progress():
    uid, other = f"u-{uuid.uuid4()}", f"u-{uuid.uuid4()}"
    sid, sid2 = f"s-{uuid.uuid4()}", f"s-{uuid.uuid4()}"
    _make_session(uid, sid, current="cp2")
    _make_session(other, sid2)
    sessions = client.get("/api/sessions", params={"user_id": uid}).json()["sessions"]
    assert [s["id"] for s in sessions] == [sid]
    assert sessions[0]["checkpoint_count"] == 2
    assert sessions[0]["completed_checkpoints"] == 1
    assert sessions[0]["goal"] == "Learn variables"


def test_completed_session_reports_all_checkpoints_done():
    uid, sid = f"u-{uuid.uuid4()}", f"s-{uuid.uuid4()}"
    _make_session(uid, sid, status="completed", current=None)
    s = client.get("/api/sessions", params={"user_id": uid}).json()["sessions"][0]
    assert s["completed_checkpoints"] == s["checkpoint_count"] == 2


def test_session_detail_still_has_original_fields_plus_timestamps():
    uid, sid = f"u-{uuid.uuid4()}", f"s-{uuid.uuid4()}"
    _make_session(uid, sid)
    d = client.get(f"/api/session/{sid}").json()
    assert {"id", "goal", "status", "current_checkpoint_id", "learning_plan"} <= d.keys()
    assert "created_at" in d and "updated_at" in d


def test_messages_404_for_unknown_session():
    assert client.get(f"/api/session/missing-{uuid.uuid4()}/messages").status_code == 404


@patch("app.agents.orchestrator.Orchestrator.process_student_input", new_callable=AsyncMock)
def test_chat_turn_is_persisted_and_restorable(mock_process):
    uid, sid = f"u-{uuid.uuid4()}", f"s-{uuid.uuid4()}"
    _make_session(uid, sid)
    mock_process.return_value = {
        "type": "new_plan",
        "checkpoint": Checkpoint(**PLAN["checkpoints"][0]),
    }
    r = client.post("/api/chat", json={"user_id": uid, "session_id": sid, "message": "variables please"})
    assert r.status_code == 200
    msgs = client.get(f"/api/session/{sid}/messages").json()["messages"]
    assert [m["role"] for m in msgs] == ["student", "tutor"]
    assert msgs[0]["content"] == "variables please"
    assert msgs[1]["payload"]["type"] == "new_plan"
    assert msgs[1]["payload"]["next_checkpoint"]["id"] == "cp1"


@patch("app.agents.orchestrator.Orchestrator.process_student_input", new_callable=AsyncMock)
def test_failed_chat_persists_nothing(mock_process):
    uid, sid = f"u-{uuid.uuid4()}", f"s-{uuid.uuid4()}"
    _make_session(uid, sid)
    mock_process.side_effect = RuntimeError("boom")
    assert client.post("/api/chat", json={"user_id": uid, "session_id": sid, "message": "hi"}).status_code == 500
    assert client.get(f"/api/session/{sid}/messages").json()["messages"] == []
