# MentorAI — Product Requirements Document

## 1. Product

MentorAI is a Socratic AI learning system designed to help students derive answers rather than receive them.

The system decomposes a question into a sequence of prerequisite concepts and checkpoints.

The student must demonstrate sufficient understanding of the current checkpoint before the system unlocks the next one.

## 2. Vision

Build a persistent AI learning companion that remembers what a student knows, what they misunderstand, how they learn, and how their knowledge connects.

MentorAI is not primarily an answer engine.

It is a guided reasoning engine.

## 3. Core Loop

Student asks a question.

1. Understand the question.
2. Generate learning objectives.
3. Identify prerequisites.
4. Build a dependency graph.
5. Generate checkpoints.
6. Present exactly one checkpoint.
7. Student responds.
8. Verify the response.
9. Detect misconceptions.
10. Give feedback or hint.
11. Retry if necessary.
12. Unlock the next checkpoint after mastery.
13. Update Student Brain.
14. Update mastery.
15. Schedule future revision.

## 4. MVP Domains

Initial domains:

- Mathematics
- Programming
- Data Structures
- Algorithms
- Computer Science

## 5. Core Product Principles

### Principle 1 — Guide, don't solve

The default behavior must be to guide the learner.

### Principle 2 — One active checkpoint

Only one checkpoint should normally be active.

### Principle 3 — Verification before progression

A student should not progress merely because they submitted an answer.

### Principle 4 — Misconceptions matter

Wrong answers are useful learning signals.

### Principle 5 — Memory should represent understanding

The Student Brain should represent demonstrated mastery, not merely chat history.

### Principle 6 — Student agency

The student can explicitly request a solution, but normal tutoring mode remains Socratic.

## 6. MVP Screens

- Landing page
- Dashboard
- New learning session
- Tutor interface
- Checkpoint checklist
- Student Brain
- Concept page
- Progress dashboard
- Session history

## 7. MVP Success Metrics

### Learning

- Checkpoint completion rate
- First-attempt correctness
- Mastery improvement
- Retention after revision
- Hint dependency

### Product

- Sessions per student
- Session completion
- Return rate
- Average session duration
- Concepts mastered

### AI

- Verification accuracy
- Hallucination rate
- Answer leakage rate
- Hint quality
- Misconception detection accuracy
- Planning accuracy

## 8. Non-goals

MVP does not require:

- Voice
- Mobile application
- Classroom management
- Parent dashboards
- Full autonomous curriculum generation
- Real-time model training
- Multi-agent distributed infrastructure

## 9. Long-term Vision

MentorAI becomes a personal Learning OS.

Every interaction contributes to:

- Student knowledge
- Concept graph
- Mastery model
- Misconception model
- Personalized curriculum
- Proprietary tutoring dataset