import os
import json
import subprocess
from flask import Flask, render_template, jsonify

app = Flask(__name__)

def get_gpu_stats():
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu', '--format=csv,noheader,nounits'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if lines:
                parts = lines[0].split(', ')
                if len(parts) >= 4:
                    return {
                        "utilization": parts[0],
                        "memory_used": parts[1],
                        "memory_total": parts[2],
                        "temperature": parts[3]
                    }
    except Exception as e:
        pass
    
    return {
        "utilization": "N/A",
        "memory_used": "N/A",
        "memory_total": "N/A",
        "temperature": "N/A"
    }

def get_latest_metrics():
    metrics_file = os.path.join(os.path.dirname(__file__), "../outputs/monitor/metrics.jsonl")
    
    metrics = {
        "status": "NOT_STARTED",
        "step": 0,
        "loss": 0.0,
        "learning_rate": 0.0,
        "epoch": 0.0,
        "is_mock": False,
        "recent_logs": []
    }
    
    if os.path.exists(metrics_file):
        try:
            with open(metrics_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                valid_lines = []
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        valid_lines.append(data)
                    except json.JSONDecodeError:
                        continue
                        
                if valid_lines:
                    # latest valid line
                    latest = valid_lines[-1]
                    metrics.update(latest)
                    # get last 5 events
                    metrics["recent_logs"] = [v for v in valid_lines[-5:]]
        except Exception as e:
            metrics["status"] = "ERROR_READING_METRICS"
            
    return metrics

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/metrics")
def api_metrics():
    data = get_latest_metrics()
    gpu = get_gpu_stats()
    data["gpu"] = gpu
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
