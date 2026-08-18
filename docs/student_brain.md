# MentorAI — Student Brain

## 1. Purpose

The Student Brain is a persistent representation of what a learner knows.

It is not simply conversation memory.

## 2. Layers

### Layer 1 — Episodic Memory

What happened.

Examples:

- Session
- Question
- Response
- Hint
- Mistake

### Layer 2 — Semantic Knowledge

What the student knows.

Examples:

- Binary Search
- Recursion
- Derivatives

### Layer 3 — Mastery

How well the student understands a concept.

### Layer 4 — Misconceptions

What the student consistently gets wrong.

### Layer 5 — Relationships

How concepts connect.

### Layer 6 — Personal Knowledge

Student-created:

- Notes
- Analogies
- Explanations
- Examples
- Projects

## 3. Concept Record

Concept:

- id
- name
- domain
- description
- prerequisites

StudentConcept:

- student_id
- concept_id
- mastery
- confidence
- attempts
- correct_attempts
- hints_used
- last_seen
- next_review

## 4. Example

Concept:

Binary Search

Mastery:
0.82

Confidence:
0.76

Attempts:
8

Correct:
6

Misconceptions:

- Forgetting sorted-array prerequisite

Related:

- Arrays
- Sorting
- Divide and Conquer

Personal explanation:

"Cut the search space in half every time."

## 5. Memory Retrieval

Before tutoring:

1. Identify relevant concepts.
2. Retrieve mastery.
3. Retrieve misconceptions.
4. Retrieve relevant prior explanations.
5. Retrieve related projects.
6. Inject only relevant context.

Do not dump the entire Student Brain into the model context.

## 6. Privacy

Student data is private by default.

Training on user interactions requires explicit consent and appropriate anonymization.