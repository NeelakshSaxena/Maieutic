# MentorAI - API

Source of truth: [`apps/api/app/api/routers.py`](../apps/api/app/api/routers.py), [`apps/api/app/main.py`](../apps/api/app/main.py) and [`apps/api/app/schemas/api_schemas.py`](../apps/api/app/schemas/api_schemas.py).

Application routes are mounted under `/api`; health routes are at the root. In the local stack the same paths are reachable through the frontend (`http://localhost:4000/api/...`, `http://localhost:4000/health/llm`), where Next.js forwards them to the API.

## Endpoints

| Method and path | Purpose |
|---|---|
| `GET /health` | Liveness: returns `{"status": "ok"}`. Does not touch the database or the LLM. |
| `GET /health/llm` | Calls the configured endpoint's model list (`TRANSFORM_*`) and checks the model exists. 200 with `available_models`, or 503 with a message if the endpoint is unreachable or the model is missing. Does **not** run inference. |
| `POST /api/chat` | Main tutoring endpoint (below). |
| `GET /api/session/{session_id}` | Session goal, status, current checkpoint id and the stored learning plan. 404 if unknown. |
| `GET /api/brain/{user_id}` | Per-concept mastery (`historical_mastery`, `attempts`, `misconceptions_observed`). Creates an empty profile if needed. |
| `GET /api/revision/{user_id}` | Spaced-repetition schedule per concept (`next_review_date`, `interval_days`, `ease_factor`). |

## POST /api/chat

Request:
```json
{ "user_id": "string", "session_id": "string", "message": "string" }
```
If `session_id` does not exist yet, `message` is treated as the learning goal and a plan is generated (`type: "new_plan"`). Otherwise `message` is treated as the answer to the session's current checkpoint.

Response (`ChatResponse`):
```json
{
  "type": "new_plan | correct | incorrect | incomplete | off_topic | completed | error",
  "message": "text shown to the student, or null",
  "next_checkpoint": { "id": "...", "concept_id": "...", "task": "...", "success_criteria": "..." },
  "hint": { "level_used": "1", "hint_text": "...", "target": "...", "rationale": "...", "was_answer_revealed": false },
  "verification": { "is_correct": false, "status": "incorrect", "criteria_evaluation": [], "misconceptions": [], "mastery_score": 0.0, "explanation": "..." }
}
```
Fields not relevant to a given `type` are `null`.

Errors: 422 for a malformed body; 503 when the LLM endpoint is unreachable or the model is missing (the message names the endpoint/model); 500 for other failures (for example a plan that fails validation after retries).

A single request can take one to several minutes with a local 9B model: a new plan is one LLM call; a wrong answer is two (verifier, then hint).

## Design rule
The backend, not the LLM, decides session progression: the verifier proposes a status, and the orchestrator advances the checkpoint only on `correct`.

Authentication is not implemented.
