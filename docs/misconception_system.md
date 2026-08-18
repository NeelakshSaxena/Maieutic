# MentorAI — Misconception System

## 1. Purpose

Turn incorrect answers into structured learning information.

## 2. Misconception Record

Fields:

- id
- concept_id
- canonical_description
- severity
- frequency
- examples
- remediation_strategy
- hint_sequence
- recovery_rate

## 3. Example

Concept:

Binary Search

Misconception:

"Binary search works on unsorted arrays."

Severity:

High

Remediation:

Ask why half of the array can be safely discarded.

## 4. Detection

Student response

↓

Verifier

↓

Misconception Detector

↓

Canonical misconception

## 5. Canonicalization

Different responses may represent the same misconception.

Example:

"Order doesn't matter."

"Can use binary search anywhere."

"Doesn't need sorting."

All map to:

binary_search.requires_sorted_input

## 6. Misconception Confidence

Each detection has confidence.

High confidence:

Update Student Brain.

Low confidence:

Ask clarification.

## 7. Recovery

After misconception detection:

1. Explain nothing directly.
2. Ask targeted question.
3. Give level-1 hint.
4. Retry.
5. Escalate hint if required.
6. Re-evaluate.

## 8. Metrics

Track:

- Detection accuracy
- Frequency
- Recovery rate
- Attempts to recover
- Hint effectiveness
- Recurrence