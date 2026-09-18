# Database Operations

This document covers common administrative tasks for the PostgreSQL database in MentorAI.

## Accessing the Database

**Launch `psql` inside the container:**
```bash
docker compose exec db psql -U postgres -d postgres
```

## Common Queries

**View all users/students:**
```sql
SELECT * FROM student_profiles;
```

**View mastery state for a concept:**
```sql
SELECT * FROM concept_mastery_states WHERE concept_id = 'variables';
```

**Check recent session activity:**
```sql
SELECT * FROM learning_sessions ORDER BY created_at DESC LIMIT 5;
```

## Migrations (Alembic)

The backend uses SQLAlchemy and Alembic. Migrations live in `apps/api/alembic/versions`.

- **Upgrade to latest:** `docker compose exec api alembic upgrade head`
- **Generate new migration:** `docker compose exec api alembic revision --autogenerate -m "message"`
- **Rollback one version:** `docker compose exec api alembic downgrade -1`
