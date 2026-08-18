# MentorAI — Roadmap

## Phase 0 — Foundation

- Repository
- Documentation
- Docker
- Database
- Basic frontend
- Model gateway

Definition of done:

Local environment works.

---

## Phase 1 — Dataset Pipeline

- Dataset ingestion
- Normalization
- Filtering
- Deduplication
- Dataset versioning

Definition of done:

A reproducible training dataset can be generated.

---

## Phase 2 — Baseline Tutor

Implement:

- Planner
- Checkpoint generator
- Verifier
- Hint generator

Initially use an API model.

Definition of done:

Student can complete a full tutoring session.

---

## Phase 3 — Student Brain

Implement:

- Concepts
- Mastery
- Misconceptions
- Relationships
- Session memory

Definition of done:

A student can return later and continue learning with persistent context.

---

## Phase 4 — Evaluation

Build:

- Verification benchmark
- Hint benchmark
- Misconception benchmark
- Answer leakage benchmark

Definition of done:

Every model change can be objectively evaluated.

---

## Phase 5 — Fine-tuning

Train 12–14B model.

SFT

↓

Preference optimization

↓

Evaluation

↓

RunPod deployment

Definition of done:

Fine-tuned model outperforms baseline on MentorAI benchmarks.

---

## Phase 6 — MVP Product

- Authentication
- Dashboard
- Tutor
- Checklist
- Brain
- Progress
- Analytics

Definition of done:

External students can use MentorAI.

---

## Phase 7 — Data Flywheel

Interactions

↓

Consent

↓

Anonymization

↓

Quality filtering

↓

Evaluation

↓

Training data

↓

Model improvement

Definition of done:

New model versions demonstrably improve tutoring.

---

## Phase 8 — Advanced Tutor

- Adaptive difficulty
- Spaced repetition
- Code execution
- Whiteboard
- Voice
- Project context
- Interview mode

---

## Phase 9 — Learning OS

Student Brain becomes the central layer.

Tutor

Projects

Notes

Courses

Practice

Revision

Interviews

All connect to one personal knowledge graph.