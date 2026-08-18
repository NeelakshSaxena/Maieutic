# MentorAI — Data Pipeline

## 1. Dataset Categories

### Mathematics

- MathInstruct
- NuminaMath
- GSM8K
- MATH

### Programming

- APPS
- MBPP
- HumanEval
- CodeContests

### Tutoring

- SocraticQA
- OpenTutor
- educational conversation datasets

### Educational Modeling

- ASSISTments
- EdNet
- Riiid

## 2. Important

Before downloading datasets, verify:

- License
- Commercial usage rights
- Redistribution restrictions
- Attribution requirements
- Personal data restrictions

A dataset being publicly downloadable does not automatically mean it is suitable for commercial training.

## 3. Pipeline

Raw

↓

License validation

↓

Parsing

↓

Normalization

↓

Language filtering

↓

Quality filtering

↓

Deduplication

↓

Contamination checks

↓

Concept extraction

↓

Tutoring transformation

↓

Human / model quality evaluation

↓

Final dataset

## 4. Unified Record

{
  "id": "...",
  "domain": "math",
  "question": "...",
  "concepts": [],
  "prerequisites": [],
  "solution": "...",
  "checkpoints": [],
  "student_response": "...",
  "evaluation": "...",
  "misconceptions": [],
  "hints": [],
  "metadata": {}
}

## 5. Synthetic Transformation

Existing Q&A:

Question
+
Answer

should NOT automatically become:

Question
+
Socratic dialogue.

A transformation model should generate:

- Learning objectives
- Checkpoints
- Expected reasoning
- Wrong reasoning
- Misconceptions
- Hints

Then quality filtering is required.

## 6. Data Versioning

Every training dataset receives a version.

Example:

mentorai-sft-v0.1

mentorai-sft-v0.2

Never overwrite training datasets.

## 7. Proprietary Dataset

Future user interactions become:

mentorai-interactions-v1

with appropriate consent and anonymization.