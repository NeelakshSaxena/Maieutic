# MentorAI — Model Evaluation

## 1. Evaluation Philosophy

Do not evaluate MentorAI primarily on whether it produces the correct final answer.

Evaluate whether it helps the student reach the answer.

## 2. Metrics

### Planning

- Dependency correctness
- Missing prerequisite rate
- Unnecessary checkpoint rate

### Verification

- True positive correctness
- False positive correctness
- False negative rate
- Misconception accuracy

### Tutoring

- Socratic adherence
- Hint quality
- Answer leakage
- Student progression

### Learning

- Pre-session mastery
- Post-session mastery
- Delayed retention

## 3. Critical Safety Metric

Answer Leakage Rate.

Definition:

Percentage of tutoring responses that reveal enough information to bypass the intended checkpoint.

Target:

As close to zero as practical.

## 4. Evaluation Dataset

Create a permanent benchmark containing:

- Correct student answers
- Incorrect answers
- Partial answers
- Common misconceptions
- Adversarial answers
- "Give me the answer" requests
- Ambiguous answers

## 5. Regression Testing

Every model update runs the complete benchmark.

A model cannot ship if critical tutoring behavior regresses.

## 6. Human Evaluation

Human evaluators score:

1. Did the tutor understand the student's answer?
2. Did it correctly identify mistakes?
3. Did it give a useful hint?
4. Did it avoid solving prematurely?
5. Did it move at an appropriate pace?

## 7. Model Release

Model release requires:

- Benchmark pass
- No critical regression
- Acceptable latency
- Acceptable inference cost
- Acceptable answer leakage