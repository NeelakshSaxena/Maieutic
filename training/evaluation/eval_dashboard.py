import os
import re
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Hardcoded path to the background task log file
LOG_PATH = "/root/.gemini/antigravity-ide/brain/45e0c85a-38c5-46d7-92c8-944f7d9a5e4e/.system_generated/tasks/task-1018.log"

@app.route("/")
def index():
    return render_template("eval_dashboard.html")

@app.route("/api/logs")
def api_logs():
    if not os.path.exists(LOG_PATH):
        return jsonify({"lines": ["Log file not found yet..."]})
        
    try:
        # Read the last 200 lines
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Reverse lines so latest is at the bottom, or just keep order and UI scrolls
            # Return last 200 lines
            return jsonify({"lines": [line.rstrip() for line in lines[-200:]]})
    except Exception as e:
        return jsonify({"lines": [f"Error reading log: {str(e)}"]})

@app.route("/api/progress")
def api_progress():
    status = {
        "current_phase": "Initializing...",
        "active_model": "None",
        "progress_percent": 0,
        "detail": ""
    }
    
    if not os.path.exists(LOG_PATH):
        return jsonify(status)
        
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        # First pass: find the active model
        for line in reversed(lines):
            line = line.strip()
            if "[PHASE 3] JUDGING MODEL:" in line:
                status["active_model"] = line.split("MODEL:")[-1].strip()
                break
            elif "[PHASE 2] GENERATING FOR MODEL:" in line:
                status["active_model"] = line.split("MODEL:")[-1].split("from")[0].strip()
                break
                
        # Second pass: find the progress state
        for line in reversed(lines):
            line = line.strip()
            
            if "EVALUATION COMPLETE" in line or "[PHASE 7]" in line:
                status["current_phase"] = "Phase 7: Final Report"
                status["progress_percent"] = 100
                status["detail"] = "Evaluation complete."
                break
                
            elif "[PHASE 6]" in line:
                status["current_phase"] = "Phase 6: Capability Benchmarks"
                status["progress_percent"] = 90
                status["detail"] = "Running GSM8K / MMLU"
                break
                
            elif "[PHASE 5]" in line or "[PHASE 4]" in line:
                status["current_phase"] = "Phase 4/5: Aggregation"
                status["progress_percent"] = 85
                status["detail"] = "Processing qualitative results"
                break
                
            elif "Judging" in line and "/" in line:
                match = re.search(r"Judging (\d+)/(\d+)", line)
                if match:
                    curr = int(match.group(1))
                    tot = int(match.group(2))
                    status["current_phase"] = "Phase 3: LLM Judging"
                    
                    model_idx = 0
                    if status["active_model"] == "Experiment #1": model_idx = 1
                    elif status["active_model"] == "Experiment #2": model_idx = 2
                    
                    status["progress_percent"] = 40 + int((model_idx/3.0)*40) + int((curr/tot) * (40/3.0))
                    status["detail"] = f"{curr} / {tot}"
                    break
                    
            elif "[PHASE 3] JUDGING MODEL" in line:
                status["current_phase"] = "Phase 3: LLM Judging"
                status["progress_percent"] = 40
                break
                
            elif "Generating" in line and "/" in line:
                match = re.search(r"Generating (\d+)/(\d+)", line)
                if match:
                    curr = int(match.group(1))
                    tot = int(match.group(2))
                    status["current_phase"] = "Phase 2: Generation"
                    
                    model_idx = 0
                    if status["active_model"] == "Experiment #1": model_idx = 1
                    elif status["active_model"] == "Experiment #2": model_idx = 2
                    
                    status["progress_percent"] = int((model_idx/3.0)*40) + int((curr/tot) * (40/3.0))
                    status["detail"] = f"{curr} / {tot}"
                    break
                    
            elif "[PHASE 2] GENERATING" in line:
                status["current_phase"] = "Phase 2: Generation"
                status["progress_percent"] = 5
                break

        return jsonify(status)
    except Exception as e:
        status["detail"] = str(e)
        return jsonify(status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
