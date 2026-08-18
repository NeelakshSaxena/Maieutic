# MentorAI — AI Architecture

## 1. AI Components

MentorAI consists of specialized reasoning components.

### Planner

Determines:

- What the question requires
- Prerequisites
- Concepts
- Dependencies
- Learning objectives
- Difficulty

### Checkpoint Generator

Transforms concepts into student tasks.

### Verifier

Evaluates student responses.

Output:

CORRECT
PARTIAL
INCORRECT
UNCLEAR

### Misconception Detector

Identifies the conceptual reason behind incorrect reasoning.

### Hint Generator

Produces progressively stronger hints.

### Mastery Engine

Converts evidence into a mastery estimate.

## 2. Important Design Decision

Do not initially implement these as separate LLMs.

They should be logical agents using the same model gateway.

This reduces cost and complexity.

## 3. Model

Initial target:

12–14B instruction model.

Use LoRA/QLoRA rather than full parameter training for MVP.

## 4. Model Responsibilities

The model should become especially good at:

- Decomposition
- Socratic questioning
- Student-response evaluation
- Misconception recognition
- Hint generation
- Educational adaptation

It should not be optimized primarily for:

- Long-form answer generation
- Creative writing
- Generic chat

## 5. Structured Output

Every agent must produce structured output.

Example:

{
  "status": "partial",
  "reason": "...",
  "misconception": "...",
  "mastery_delta": -0.03,
  "next_action": "hint"
}

Never rely on free-form parsing.

## 6. Model Routing

Future architecture:

Small model:
classification
simple verification

14B model:
tutoring
planning
misconceptions

Large teacher:
dataset generation
offline evaluation
difficult cases

## 7. Teacher-Student Architecture

A larger model may eventually generate high-quality tutoring traces.

These traces are filtered and used to train the smaller production model.

Teacher
    |
    v
Synthetic tutoring traces
    |
    v
Quality filter
    |
    v
Human / evaluator validation
    |
    v
SFT / DPO
    |
    v
MentorAI model