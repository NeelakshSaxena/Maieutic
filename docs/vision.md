## Vision
 
MentorAI is an AI-powered Socratic tutor that teaches through guided reasoning instead of directly answering questions.
 
The objective is long-term understanding, mastery, and knowledge retention.
 
The tutor should never immediately provide the final answer unless the user explicitly requests it.
 
Instead, it should:
 
• Break problems into prerequisite concepts.
• Generate dependency graphs.
• Create checkpoint-based learning plans.
• Verify every student response.
• Detect misconceptions.
• Generate progressively stronger hints.
• Unlock the next checkpoint only after mastery.
 
---
 
## Supported Subjects
 
- Mathematics
- Programming
- Data Structures
- Algorithms
- Computer Science
- Interview Preparation
 
---
 
## Core AI Components
 
Planner
 
↓
 
Checkpoint Generator
 
↓
 
Verifier
 
↓
 
Hint Generator
 
↓
 
Mastery Tracker
 
↓
 
Student Brain (LLMWiki)
 
↓
 
Analytics
 
---
 
## Student Brain (LLMWiki)
 
Every student owns a persistent knowledge graph.
 
Store:
 
- Concepts
- Mastery
- Confidence
- Attempts
- Common mistakes
- Preferred explanations
- Personal notes
- AI explanations
- Revision schedule
- Interview questions
- Projects
- Concept relationships
- Learning timeline
 
The Student Brain continuously evolves and becomes the student's second memory.
 
---
 
## Misconception Database
 
Store:
 
Concept
 
Wrong answer
 
Correct understanding
 
Hint sequence
 
Difficulty
 
Recovery success
 
Frequency
 
The misconception database is one of the product's most valuable long-term assets.
 
---
 
## Initial Model
 
12–14B open-weight model.
 
Fine-tuned specifically for:
 
- Socratic questioning
- Checkpoint generation
- Verification
- Hint generation
- Misconception detection
- Adaptive tutoring
 
Avoid optimizing for direct answer generation.
 
---
 
## Training Pipeline
 
Stage 1
 
Instruction Fine-tuning
 
↓
 
Stage 2
 
Tutor Fine-tuning
 
↓
 
Stage 3
 
Preference Optimization
 
↓
 
Stage 4
 
Continuous Dataset Growth
 
---
 
## Datasets
 
Mathematics
 
- MathInstruct
- NuminaMath
- GSM8K
- MATH
 
Programming
 
- APPS
- MBPP
- HumanEval
- CodeContests
 
Tutoring
 
- SocraticQA
- OpenTutor
- LMSYS Chat
- WildChat
 
Education
 
- ASSISTments
- EdNet
- Riiid
 
Alignment
 
- UltraFeedback
 
---
 
## Technology
 
Frontend
 
Next.js
React
Tailwind
 
Backend
 
FastAPI
 
Storage
 
PostgreSQL
Redis
Qdrant
MinIO
 
Inference
 
vLLM
 
Training
 
Transformers
TRL
PEFT
Unsloth
 
Deployment
 
Runpod
 
---
 
## Long-Term Vision
 
MentorAI should become an AI learning operating system.
 
Instead of remembering chats, it remembers knowledge.
 
Instead of generating answers, it grows understanding.
 
Every completed tutoring session improves both the student and the AI itself.