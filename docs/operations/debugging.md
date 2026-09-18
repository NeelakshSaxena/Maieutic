# Debugging the AI Agents

When the frontend behaves unexpectedly (e.g., returning bizarre hints, skipping checkpoints, or throwing 500 errors), the issue is almost always in the interaction between the Orchestrator, the Pydantic schemas, and the Ollama LLM.

## Reading the Logs

To debug an AI interaction, you need to watch the API logs:
```bash
docker compose logs -f api
```

Look for the following log patterns:
1. **Pydantic ValidationErrors:** This indicates the LLM returned JSON that didn't match the schema. The Orchestrator will automatically retry and pass the error back to the LLM.
2. **"Failed to parse JSON":** The LLM returned raw text (like ````json ... ````) that the client couldn't strip, or it just returned conversational text.
3. **Unexpected State Transitions:** If the Orchestrator goes from `AWAITING_RESPONSE` to `CHECKPOINT_COMPLETED` without a `VERIFYING` step, check the router logic in `apps/api/app/api/routers.py`.

## Prompt Engineering & Agent Tuning

If an agent is consistently failing to follow instructions, you don't need to retrain the model immediately.
1. Open the agent file (e.g., `apps/api/app/agents/verifier.py`).
2. Tweak the system prompt instructions.
3. Add explicit negative constraints (e.g., "DO NOT output conversational filler").
4. The API container supports live-reloading (if run locally) or you can rebuild via Docker.
