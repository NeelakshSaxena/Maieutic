# Local GPU Transition Guide

The generation pipeline has been successfully halted and all background timers have been stopped. 

### Generation State
- **Stopping Point:** The pipeline was successfully paused at exactly **13 accepted Socratic samples** and **51 rejections**.
- **State Persisted:** All progress is safely written to the live tracking files:
  - `/workspace/Maieutic/training/datasets/socratic/socratic_pilot.jsonl`
  - `/workspace/Maieutic/training/datasets/socratic/rejections.jsonl`
- **Reproducibility:** The pipeline was designed to be fully persistent. Because it reads these exact output files on startup to populate the `processed_ids` cache, **you will not lose a single generated sample**.

### How to Resume on Local GPU
When you are ready to switch from RunPod to your local idle GPU, follow these steps:

1. **Boot your Local Endpoint:** Spin up vLLM (or your preferred OpenAI-compatible server) on your local GPU. By default, this usually binds to `http://localhost:8000/v1`.
2. **Update Environment:** Open your `.env` file (or export to your terminal session) and update the endpoints:
   ```env
   TRANSFORM_BASE_URL="http://localhost:8000/v1"
   JUDGE_BASE_URL="http://localhost:8000/v1"
   ```
3. **Resume Pipeline:** Simply re-run the exact same orchestrator script:
   ```bash
   PYTHONUNBUFFERED=1 python training/preprocessing/build_pilot_dataset.py
   ```

The script will automatically detect the existing 13 accepted samples, load their IDs to skip them, and seamlessly continue processing the remaining candidates at the speed of your local GPU!
