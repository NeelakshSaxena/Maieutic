# MentorAI — Architecture Decision Records

## ADR-001 — Modular Monolith for MVP

Decision:

Use a modular monolith rather than microservices.

Reason:

The MVP needs fast iteration and low operational complexity.

Future:

Split services when scaling requirements justify it.

---

## ADR-002 — 12–14B Production Model

Decision:

Start with a 12–14B open-weight model.

Reason:

Balance reasoning quality, latency, and inference cost.

---

## ADR-003 — LoRA/QLoRA

Decision:

Use parameter-efficient fine-tuning initially.

Reason:

Lower GPU cost and faster experimentation.

---

## ADR-004 — Backend Controls Progression

Decision:

LLM recommends checkpoint state but backend owns state transitions.

Reason:

Prevents hallucinated progression.

---

## ADR-005 — Student Brain Is Structured

Decision:

Do not treat chat history as the Student Brain.

Reason:

Conversation history is not an accurate representation of mastery.

---

## ADR-006 — PostgreSQL First

Decision:

Use PostgreSQL as the source of truth for knowledge relationships.

Qdrant is used for semantic retrieval.

Reason:

Structured mastery data requires deterministic querying.

---

## ADR-007 — No Live Model Training

Decision:

User interactions never directly update model weights.

Reason:

Safety, reproducibility, privacy, and quality control.

Interactions become candidate training data only after filtering and evaluation.