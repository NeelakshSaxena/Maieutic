MVP PRD — Socratic AI Tutor
 
Working Name: MentorAI (placeholder)
 
 
---
 
Vision
 
Build an AI tutor that does not solve problems immediately.
 
Instead, it teaches using the Socratic method by breaking problems into checkpoints, verifying understanding, giving hints, and only unlocking the next step when the learner demonstrates mastery.
 
The objective is understanding, not answer generation.
 
 
---
 
Core Principles
 
Never reveal the complete answer unless explicitly requested.
 
Guide, don't solve.
 
One checkpoint at a time.
 
Verify every response.
 
Detect misconceptions.
 
Adapt to the learner.
 
Build long-term knowledge graphs.
 
Continuously improve from user interactions.
 
 
 
---
 
MVP Scope
 
Supported Domains
 
Mathematics
 
Data Structures & Algorithms
 
Programming
 
Computer Science fundamentals
 
 
 
---
 
User Flow
 
User asks question
 
↓
 
Planner breaks it into concepts
 
↓
 
Checklist generated
 
□ Prerequisite
□ Concept 1
□ Concept 2
□ Edge Cases
□ Final Understanding
 
↓
 
Checkpoint 1
 
↓
 
Student answers
 
↓
 
Verifier
 
↓
 
Correct?
      │
 ┌────┴─────┐
 │          │
Yes        No
 │          │
Unlock    Generate Hint
Next Step Retry
 
 
---
 
AI Pipeline
 
1. Planner
 
Creates a dependency graph.
 
Input
 
Question
 
Output
 
Learning Objectives
 
Prerequisites
 
Checklist
 
Difficulty
 
Estimated Time
 
Concept Dependencies
 
 
---
 
2. Checkpoint Generator
 
Creates questions.
 
Example
 
Instead of
 
> Explain Binary Search
 
 
 
Generates
 
Checkpoint 1
 
Can Binary Search work on any array?
 
Checkpoint 2
 
Why?
 
Checkpoint 3
 
How do we reduce the search space?
 
 
---
 
3. Verifier
 
Evaluates responses.
 
Outputs
 
Correct
 
Partially Correct
 
Incorrect
 
Misconception
 
Missing Concept
 
Never reveals the answer.
 
 
---
 
4. Hint Generator
 
Hints are progressive.
 
Level 1
 
Tiny nudge
 
Level 2
 
Concept reminder
 
Level 3
 
Example
 
Level 4
 
Near-complete guidance
 
Only after repeated failures.
 
 
---
 
5. Mastery Tracker
 
Stores
 
Concept
 
Confidence
 
Attempts
 
Time
 
Hints Used
 
Mistakes
 
Mastery Score
 
 
---
 
Tech Stack
 
Frontend
 
React
 
Next.js
 
 
Backend
 
FastAPI
 
 
Database
 
PostgreSQL
 
 
Cache
 
Redis
 
 
Vector DB
 
Qdrant
 
 
Storage
 
S3 / MinIO
 
 
Monitoring
 
Langfuse
 
OpenTelemetry
 
 
 
---
 
Base Model
 
Recommendation
 
12–14B parameter open-weight model
 
Reason
 
Strong reasoning
 
Affordable inference
 
Fast enough for production
 
Good instruction following
 
Easier deployment than 20–30B models
 
 
Examples include modern instruction-tuned models in the 12–14B class (or an equivalent if a newer, stronger model is available at launch).
 
 
---
 
Training Strategy
 
Stage 1
 
Instruction Fine-tuning
 
↓
 
Stage 2
 
Tutor Fine-tuning
 
↓
 
Stage 3
 
Preference Optimization (DPO/ORPO/KTO)
 
↓
 
Stage 4
 
Online Learning from User Data (periodic retraining, not live weight updates)
 
 
---
 
Dataset Pipeline
 
Mathematics
 
MathInstruct
 
NuminaMath
 
OpenThoughts (reasoning traces)
 
GSM8K (basic reasoning)
 
MATH
 
 
 
---
 
Programming
 
APPS
 
CodeContests
 
HumanEval
 
MBPP
 
 
 
---
 
Tutoring
 
OpenTutor
 
SocraticQA
 
LMSYS Chat-1M (filtered)
 
WildChat (filtered for educational dialogs)
 
 
 
---
 
Educational / Knowledge Tracing
 
ASSISTments
 
EdNet
 
Riiid! Answer Correctness Prediction
 
 
 
---
 
Alignment
 
UltraFeedback
 
Helpful-Harmless preference datasets
 
 
 
---
 
Data Normalization
 
Convert every dataset into a unified schema:
 
{
  "question": "...",
  "learning_objectives": [],
  "prerequisites": [],
  "checkpoints": [],
  "student_response": "...",
  "evaluation": "...",
  "hint": "...",
  "misconception": "...",
  "next_step": "..."
}
 
 
---
 
Internal Knowledge Graph
 
Every concept becomes a node.
 
Example
 
Arrays
   │
Sorting
   │
Binary Search
   │
Lower Bound
 
Mastery unlocks dependent concepts.
 
 
---
 
Student Memory
 
Store:
 
User ID
 
Concept
 
Attempts
 
Correct %
 
Average Time
 
Hints Used
 
Last Practiced
 
Mastery
 
Weak Areas
 
Strong Areas
 
 
---
 
Misconception Database
 
One of the product's key assets.
 
Example
 
Concept
 
Common Wrong Answer
 
Correct Concept
 
Hint Sequence
 
Difficulty
 
Frequency
 
Recovery Success Rate
 
Example
 
Binary Search
 
Wrong
 
Works on any array
 
Correct
 
Requires sorted data
 
Hint
 
"Think about what allows us to discard half the array."
 
 
---
 
Analytics
 
Track:
 
Average attempts per concept
 
Hint usage
 
Success rate
 
Time to mastery
 
Drop-off points
 
Most common misconceptions
 
Most difficult checkpoints
 
 
 
---
 
AI Memory
 
Store every interaction.
 
Question
 
↓
 
Planner Output
 
↓
 
Student Response
 
↓
 
Verifier Output
 
↓
 
Hint
 
↓
 
Retry Count
 
↓
 
Final Mastery
 
These become future training data.
 
 
---
 
Future Training Dataset
 
Every completed session becomes:
 
Question
 
↓
 
Task Graph
 
↓
 
Student Journey
 
↓
 
Mistakes
 
↓
 
Hints
 
↓
 
Correct Answer
 
↓
 
Mastery Outcome
 
This proprietary dataset is likely to become your biggest competitive advantage.
 
 
---
 
Future Features
 
Voice tutoring
 
Whiteboard mode
 
Handwritten math support
 
Code execution sandbox
 
Compiler integration
 
LeetCode/HackerRank practice mode
 
Personalized revision plans
 
Interview preparation mode
 
Classroom/teacher dashboard
 
Parent progress reports
 
Multi-agent tutoring (Planner, Verifier, Hint Generator, Motivator)
 
Adaptive curriculum based on mastery graphs
 
 
 
---
 
MVP Deliverables
 
AI
 
Planner
 
Checkpoint Generator
 
Verifier
 
Hint Generator
 
Mastery Tracker
 
 
Backend
 
User authentication
 
Session management
 
Progress storage
 
Misconception database
 
Analytics API
 
 
Frontend
 
Chat interface
 
Checklist view
 
Progress tracker
 
Concept graph
 
Hint panel
 
Mastery dashboard
 
 
Initial Fine-tuned Model
 
12–14B instruction-tuned open model
 
Trained on curated tutoring and reasoning datasets
 
Optimized to teach using Socratic dialogue rather than immediately providing answers
 
 
This MVP is sufficient to validate the core product: whether students learn more effectively through guided reasoning, while simultaneously building a proprietary dataset of misconceptions, hint effectiveness, and mastery progression that can continuously improve future model versions.