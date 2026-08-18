# MentorAI — API

## Base

/api/v1

## Sessions

POST /sessions

Create tutoring session.

GET /sessions/{id}

Retrieve session.

POST /sessions/{id}/start

Start session.

## Checkpoints

GET /sessions/{id}/checkpoints

Get checkpoint state.

POST /sessions/{id}/response

Submit student response.

Example:

{
  "checkpoint_id": "...",
  "response": "..."
}

Response:

{
  "status": "partial",
  "feedback": "...",
  "hint_available": true,
  "next_action": "hint"
}

## Hints

POST /sessions/{id}/hint

Request next hint.

## Student Brain

GET /students/{id}/brain

GET /students/{id}/concepts

GET /students/{id}/mastery

GET /students/{id}/misconceptions

## Concepts

GET /concepts/{id}

GET /concepts/{id}/relationships

## Analytics

GET /students/{id}/analytics

## Authentication

Use token-based authentication.

Never expose internal database IDs unnecessarily.

## API Rule

The backend is the authority over session progression.

The LLM cannot directly decide:

"Checkpoint completed."

It can recommend a state.

Backend validates the recommendation against protocol rules.