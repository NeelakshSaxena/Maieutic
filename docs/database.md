# MentorAI — Database

## Core Tables

users

students

sessions

session_checkpoints

checkpoint_attempts

concepts

concept_relationships

student_concepts

misconceptions

student_misconceptions

hints

interactions

projects

student_notes

revision_schedule

model_evaluations

## users

id
email
created_at

## sessions

id
student_id
question
domain
status
created_at
completed_at

## checkpoints

id
session_id
concept_id
sequence
objective
question
status

## attempts

id
checkpoint_id
student_id
response
evaluation
correctness
created_at

## concepts

id
canonical_id
name
domain
description

## student_concepts

student_id
concept_id
mastery
confidence
attempts
correct_attempts
hints_used
last_seen
next_review

## misconceptions

id
concept_id
canonical_id
description
severity

## student_misconceptions

student_id
misconception_id
confidence
occurrences
resolved
last_seen

## interactions

id
session_id
student_id
type
input
output
model
prompt_version
created_at

## projects

id
student_id
name
description
created_at

## revision_schedule

student_id
concept_id
scheduled_at
reason
completed

## Important

Do not store every model-generated field blindly.

Persist validated, structured state.

Raw model traces should have separate retention policies.