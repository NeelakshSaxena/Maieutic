# MentorAI — System Architecture

## 1. Architecture

MVP uses a modular monolith.

Frontend:

Next.js
React
Tailwind

Backend:

FastAPI

AI:

Model Gateway
    |
    +-- Planner
    +-- Checkpoint Generator
    +-- Verifier
    +-- Hint Generator
    +-- Misconception Detector
    +-- Mastery Engine

Data:

PostgreSQL
Redis
Qdrant
Object Storage

Inference:

RunPod + vLLM

Training:

RunPod + Hugging Face + PEFT/TRL

## 2. Request Flow

Student
    |
    v
Next.js
    |
    v
FastAPI
    |
    v
Tutoring Orchestrator
    |
    +--> Student Brain Retrieval
    |
    +--> Planner
    |
    +--> Checkpoint Generator
    |
    v
Response
    |
    v
Student

When student responds:

Student
    |
    v
Verifier
    |
    +--> Misconception Detector
    |
    +--> Mastery Engine
    |
    +--> Hint Generator
    |
    v
Session State
    |
    +--> PostgreSQL
    +--> Student Brain
    +--> Analytics

## 3. Infrastructure

MVP:

Next.js
FastAPI
PostgreSQL
Redis
Qdrant
RunPod

Do not split agents into independent microservices initially.

## 4. Model Gateway

All model calls must pass through a single abstraction.

Example:

ModelGateway.generate()

The application should not directly depend on a particular inference provider.

This allows:

Development:
API model

Staging:
RunPod model

Production:
Fine-tuned MentorAI model

## 5. Async Jobs

Use Redis-backed workers for:

- Embedding
- Knowledge graph updates
- Analytics aggregation
- Dataset generation
- Long-running evaluations

## 6. Reliability

AI responses must be schema validated.

Invalid model output must never directly mutate Student Brain state.

Every state transition must be validated by backend logic.

## 7. State Machine

SESSION_CREATED
    |
PLANNING
    |
READY
    |
CHECKPOINT_ACTIVE
    |
AWAITING_RESPONSE
    |
VERIFYING
    |
    +--> CORRECT --> CHECKPOINT_COMPLETED
    |
    +--> PARTIAL --> HINT
    |
    +--> INCORRECT --> MISCONCEPTION
                            |
                            v
                           HINT
                            |
                            v
                       RETRY_REQUIRED

CHECKPOINT_COMPLETED
    |
    +--> MORE_CHECKPOINTS --> CHECKPOINT_ACTIVE
    |
    +--> COMPLETE --> SESSION_COMPLETE