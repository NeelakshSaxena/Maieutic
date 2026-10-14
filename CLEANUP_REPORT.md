# Cleanup Report

Scope: remove proven residue, fix ignore files and stale docs, keep the verified local setup (Compose + existing `ollama` container, `qwen3.5-aggressive:latest`, UI on :4000) working. No Docker objects, volumes, models, datasets or Git history were touched.

## 1. Removed
| Item | Reason |
|---|---|
| `load_lora.py` (untracked) | One-off RunPod debug script with a **hardcoded live RunPod API key**; not referenced anywhere. **Rotate that key** - it was in plaintext on disk. |
| `payload.json`, `test_inference.py`, `test_llm.py`, `test_llm.ps1` (untracked) | Debug artifacts from the recent local/RunPod debugging; unreferenced; replaced by the documented commands in `DEPLOYMENT.md`. |
| 38 `__pycache__/` dirs, `.pytest_cache/`, `apps/frontend/tsconfig.tsbuildinfo`, `apps/frontend/.next/` (~830 MB) | Regenerable caches/build output (all already git-ignored). |
| 42 empty untracked directories (`ai/`, `infrastructure/`, `packages/`, `student-data/`, `tests/e2e` etc. leaves) | Git cannot track empty dirs; no content. Skipped `training/`, `.hf_cache/`, `.cache/`. |
| BOMs added to `routers.py`, `docker-compose.yml`, `.env.example`, `DEPLOYMENT.md` | Introduced by my earlier PowerShell rewrites; stripped. |

Already deleted in the working tree before this task (not by this cleanup; still unstaged): `Dockerfile`, `Dockerfile.runpod`, `Makefile`, `apps/api/Dockerfile`, `apps/web/package.json`, `docker-entrypoint.sh`, `supervisord.conf`. I checked for live references; the only ones were `.github/workflows/docker-publish.yml` and docs, both fixed below.

## 2. Retained despite being candidates
- `envvv` (ignored): scratch file containing real tokens/keys. User's local config; not touched or printed. Consider merging into `.env` and deleting it.
- `runpodctl.exe` (untracked, 14 MB): not on PATH, so this may be your only copy. Now git-ignored and docker-ignored.
- `maieutic.db`, `apps/api/maieutic.db` (**tracked** SQLite files): local data; kept. Untracking them (`git rm --cached`) is your call.
- `PROJECT_REPORT.md`, `Socratic_Training_Report.md`, `behavioral_audit.md`, `mathdial_consecutive_investigation.md`, `RESTORE.md` (referenced by `docs/phases/phase_2.md`), `README_updated.md` (output of `training/sft/update_readme.py`), `local_gpu_handoff.md`, `archive_phase2.py`, `requirements.txt` (training deps), `skills-lock.json`, `training/`, `venv/`, `node_modules/`, `.agents/`, `.claude/`, `.hf_cache/`.
- `scripts/runpod_entrypoint.sh`, `scripts/model_bootstrap.sh`: belong to the removed unified RunPod image, but hold vLLM/LoRA bootstrap logic; kept as reference (see legacy doc).
- Tracked zero-byte scaffolding stubs (`apps/api/app/{api,models,services}/*.py`, `scripts/*.sh`, `ai/configs/*.yaml`, `packages/**`, `student-data/**`, `LICENSE`, 4 workflow files): planned project layout in `docs/folder-structure.md`; not removed.
- `training/datasets/socratic/live_generation.log` (ignored): training-run output; kept.

## 3. Ignore-file changes
- `.gitignore`: fixed corrupted line (`.envmaieutic.db` = `.env` + `maieutic.db` fused); regrouped; added `.env.*` with `!.env.example`, `node_modules/`, `.next/`, `*.tsbuildinfo`, `.pytest_cache/`, `runpodctl.exe`. All previous entries kept.
- `apps/frontend/.gitignore`: added `!.env.example` (the template was being ignored by `.env*`; it is now trackable).
- `.dockerignore`: added `.pytest_cache`, `*.tsbuildinfo`, `envvv`, `.cache`, `.hf_cache`, `.agents`, `.claude`, `*.exe`; regrouped. Both images rebuilt successfully with it.

## 4. Documentation
- `DEPLOYMENT.md` Mode 3: added Docker Desktop start, connectivity checks (frontend, API, DB, API-to-Ollama, loaded model), volume-preservation notes; overview table now shows :4000.
- `README.md`: the second half described the superseded single-image RunPod design (`Dockerfile.runpod`, supervisord, :3000, SQLite). It is now a short pointer to `DEPLOYMENT.md`, keeping the model-architecture section. The removed text is preserved verbatim, with a "superseded" banner, in `docs/legacy-runpod-unified-image.md` (the README edits were uncommitted).
- Corrected stale `qwen2`/`LLM_MODEL`/port 3000/Makefile/`ollama pull` references in `docs/{configuration,ollama,getting-started,PROJECT_STATUS,system_architecture,troubleshooting,folder-structure,operations/commands}.md`. `docs/verification/phase-6-8-verification.md` still shows `qwen2` as a historical record.
- **Required fix:** `.github/workflows/docker-publish.yml` built `./Dockerfile.runpod` (deleted); now `./Dockerfile.api`. Not run in CI from here, but `Dockerfile.api` builds locally.

## 5. Validation (actual results)
- `docker compose config --quiet`: rc 0
- Backend: `PYTHONPATH=apps/api pytest tests` -> 30 passed
- Frontend: `npm run lint` rc 0; `npx tsc --noEmit` rc 0; `npm run build` rc 0 (routes `/`, `/api/chat`, `/health/llm`)
- `docker compose build` + `up -d`: both images built, api/postgres healthy
- `GET :4000/health/llm` -> ok, model `qwen3.5-aggressive:latest`; API container -> `host.docker.internal:11434/v1/models` HTTP 200; `pg_isready` accepting connections
- Not re-run: a full LLM chat (unchanged code path, verified earlier; no model pull or Ollama rebuild).
- Git audit: no lockfile/migration changes, no secrets in changed/new text files, no new tracked deletions.

## 6. Unresolved
- Rotate the RunPod API key that was in `load_lora.py`; decide on `envvv`.
- Empty workflow files (`build.yml`, `deploy.yml`, `lint.yml`, `test.yml`): no CI for tests/lint exists.
- Tracked SQLite DBs and zero-byte stubs (above); obsolete RunPod entrypoint/bootstrap scripts.
- `apps/api` has no `poetry.lock`, so `Dockerfile.api` builds are not reproducible.
- `README_updated.md` and other docs under `docs/` still describe planned (not built) modules.
