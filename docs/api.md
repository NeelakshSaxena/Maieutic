# MentorAI — API

## Base URL
`/api/v1`

## Interactive Chat

`POST /chat`
The main orchestrator endpoint for the conversational interface. It handles both generating the initial learning plan/checkpoints and verifying student responses.

**Request payload (Session Initialization):**
```json
{
  "student_id": "string",
  "concept": "string",
  "message": "string"
}
```

**Request payload (Student Response):**
```json
{
  "student_id": "string",
  "concept": "string",
  "message": "string",
  "checkpoint": { ... },
  "plan": { ... }
}
```

## Session Management

`POST /session`
Initialize a new tutoring session manually (currently wrapped inside `/chat`).

## Student Brain

`GET /brain/{user_id}`
Retrieve the student's overall mastery profile, including the moving average of their correct/incorrect attempts across concepts.

`GET /revision/{user_id}`
Retrieve a list of concepts that are due for spaced repetition review based on the SM-2 scheduler.

## Authentication
Use token-based authentication (to be implemented). 
Never expose internal database IDs unnecessarily.

## API Rule
The backend is the absolute authority over session progression. The LLM cannot directly decide "Checkpoint completed." It can only recommend a state (`correct`, `incorrect`, `partial`). The Backend validates the recommendation against the protocol rules and mutates the Student Brain state accordingly.