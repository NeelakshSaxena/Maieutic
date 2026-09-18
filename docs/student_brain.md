# MentorAI — Student Brain

## 1. Purpose
The Student Brain is a persistent representation of what a learner knows, tracking mastery over time across different concepts using empirical performance data. It is stored across PostgreSQL (relational records) and Qdrant (semantic search).

## 2. Mastery Tracking (EMA)

Mastery is not a simple average. MentorAI uses an **Exponential Moving Average (EMA)** to calculate a student's mastery of a concept.
- **Why EMA?** A student who fails 5 times and then succeeds 5 times has likely learned the concept. A simple average (50%) would not reflect their current understanding. EMA heavily weights the most recent attempts.
- **Calculation:** When the Verifier evaluates an attempt as `correct`, the EMA increases. When it evaluates as `incorrect`, the EMA decreases. `partial` attempts have a smaller positive/neutral weight.

## 3. Spaced Repetition (SuperMemo-2)

The Student Brain includes a simplified implementation of the SuperMemo-2 (SM-2) algorithm.
- Every time a concept is practiced, the `next_review_date` is recalculated based on the EMA mastery and the consecutive correct attempts.
- If the student struggles, the review interval shrinks (e.g., review tomorrow).
- If the student demonstrates mastery, the review interval expands (e.g., review in 7 days).

## 4. Concept Record

**StudentConcept (Mastery State in DB):**
- `student_id`
- `concept_id`
- `mastery_level` (The EMA float value: 0.0 to 1.0)
- `correct_attempts`
- `incorrect_attempts`
- `partial_attempts`
- `last_reviewed_at`
- `next_review_date`

## 5. Memory Retrieval Pipeline

Before the LLM starts tutoring, the `StudentBrainService` executes the retrieval pipeline:

1. Identify relevant concepts (Query Qdrant).
2. Retrieve mastery states (Query PostgreSQL).
3. Retrieve misconceptions (If applicable).
4. **Inject context:** Only the exact concepts and mastery levels relevant to the current session are injected into the Planner Agent's context.

*Rule: Do not dump the entire Student Brain into the model context.*

## 6. Privacy

Student data is private by default. Training on user interactions requires explicit consent and appropriate anonymization.