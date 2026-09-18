# MentorAI — Database

MentorAI utilizes a hybrid database approach: PostgreSQL for structured relational data and Qdrant for semantic concept embeddings.

## 1. PostgreSQL (Relational State)

The primary data store is PostgreSQL, managed via SQLAlchemy ORM and Alembic migrations.

### Core Tables

#### `student_profiles`
- `id` (UUID, Primary Key)
- `email` (String, Unique)
- `created_at` (DateTime)

#### `concepts`
- `id` (String, Primary Key) - e.g., 'python_variables'
- `name` (String)
- `domain` (String)
- `description` (Text)

#### `concept_mastery_states`
Tracks the student's mastery of specific concepts using an Exponential Moving Average (EMA).
- `id` (UUID, Primary Key)
- `student_id` (UUID, Foreign Key -> `student_profiles`)
- `concept_id` (String, Foreign Key -> `concepts`)
- `mastery_level` (Float) - The EMA score.
- `correct_attempts` (Integer)
- `partial_attempts` (Integer)
- `incorrect_attempts` (Integer)
- `last_reviewed_at` (DateTime)
- `next_review_date` (DateTime) - Used for spaced repetition (SM-2).

#### `learning_sessions`
- `id` (UUID, Primary Key)
- `student_id` (UUID, Foreign Key -> `student_profiles`)
- `goal_concept_id` (String)
- `created_at` (DateTime)
- `completed_at` (DateTime, Nullable)
- `status` (String) - e.g., 'active', 'completed'
- `history` (JSON) - Serialized checkpoint history.

## 2. Qdrant (Semantic State)

Qdrant is used to store and retrieve concepts based on semantic similarity.

### Collection: `concepts`
- **Vector:** The embedding of the concept's description/name.
- **Payload:**
  - `concept_id`: The ID matching the PostgreSQL `concepts` table.
  - `domain`: The domain of the concept.

When the Orchestrator plans a session, it queries Qdrant to find related prerequisite concepts to inject into the LLM's context window.

## 3. Redis (Transient State)
Redis is currently provisioned for caching and pub/sub. It is not used for persistent storage.

## Important Rule

Do not store every raw model-generated trace in PostgreSQL.
Persist validated, structured state. Raw model traces should have separate retention policies or be pushed to an analytics data warehouse.