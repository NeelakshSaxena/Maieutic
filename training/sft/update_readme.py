import os
from dotenv import load_dotenv
from huggingface_hub import HfApi, hf_hub_download

load_dotenv("/workspace/Maieutic/.env")
HF_TOKEN = os.getenv("HF_TOKEN")
HF_REPO = os.getenv("HF_REPO")

api = HfApi(token=HF_TOKEN)

try:
    # Try to download existing README
    readme_path = hf_hub_download(repo_id=HF_REPO, filename="README.md", token=HF_TOKEN)
    with open(readme_path, "r") as f:
        content = f.read()
except Exception as e:
    content = "# MentorAI\n\n"

new_section = """
## Phase 2A (version: `phase2a_qwen3-8b_real-socratic_2026-09-15`)
**STATUS: TRAINED — BEHAVIORAL EVALUATION PENDING**

- **Goal**: Real Socratic tutoring data (Experiment 2)
- **Base Model**: Qwen/Qwen3-8B
- **Training Method**: QLoRA (4-bit, Rank 16, Alpha 32)
- **Date**: 2026-09-15
- **Dataset**: 13,859 training examples
- **Epochs**: 1
- **Note**: The sanity check passed (the adapter loads and generates text), but this does not establish Socratic behavioral improvement. Behavioral evaluation is pending.
"""

if "Phase 2A" not in content:
    content += "\n" + new_section
    
    with open("README_updated.md", "w") as f:
        f.write(content)
        
    api.upload_file(
        path_or_fileobj="README_updated.md",
        path_in_repo="README.md",
        repo_id=HF_REPO,
        repo_type="model"
    )
    print("Successfully updated README.md")
else:
    print("README.md already contains Phase 2A.")
