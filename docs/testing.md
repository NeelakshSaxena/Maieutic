# Testing

MentorAI relies on robust testing to ensure the Orchestrator, Agents, and Student Brain work flawlessly together.

## Running Tests

All tests for the backend should be run from within the `api` container to ensure they have the correct environment and dependencies.

```bash
# Run all tests
docker compose exec api pytest tests/ -v

# Run specific test file
docker compose exec api pytest tests/api/test_api.py -v

# Run with stdout output (for debugging)
docker compose exec api pytest tests/ -v -s
```

## Test Structure

- `tests/api/`: Tests for the FastAPI endpoints (`/chat`, `/session`, etc.).
- `tests/agents/`: Unit tests for individual AI agents (Planner, Verifier, Hint Generator).
- `tests/brain/`: Unit tests for the StudentBrainService and mastery state calculations.

## Mocking the LLM

During testing, the `LLMClient` is mocked to prevent actual API calls to Ollama, which would make tests slow and non-deterministic.
Tests inject a fake prompt/response mapping or use `pytest.MonkeyPatch` to simulate the LLM returning perfectly formatted JSON schemas.
