import os
import time
import re
import sys

LOG_PATH = "/root/.gemini/antigravity-ide/brain/45e0c85a-38c5-46d7-92c8-944f7d9a5e4e/.system_generated/tasks/task-1018.log"

# Colors
C_RESET = "\033[0m"
C_CYAN = "\033[96m"
C_PURPLE = "\033[95m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_GRAY = "\033[90m"
C_RED = "\033[91m"
C_BOLD = "\033[1m"

def get_status():
    status = {
        "current_phase": "Initializing...",
        "active_model": "None",
        "progress_percent": 0,
        "detail": "",
        "lines": []
    }
    
    if not os.path.exists(LOG_PATH):
        return status
        
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    status["lines"] = [line.strip() for line in lines[-20:]]
        
    for line in reversed(lines):
        line = line.strip()
        if "[PHASE 3] JUDGING MODEL:" in line:
            status["active_model"] = line.split("MODEL:")[-1].strip()
            break
        elif "[PHASE 2] GENERATING FOR MODEL:" in line:
            status["active_model"] = line.split("MODEL:")[-1].split("from")[0].strip()
            break
            
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
            
    return status

def draw_progress_bar(percent, length=50):
    filled = int(length * percent // 100)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{C_PURPLE}{bar}{C_RESET}] {C_CYAN}{percent}%{C_RESET}"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    try:
        while True:
            status = get_status()
            clear_screen()
            
            print(f"\n{C_BOLD}{C_CYAN}=== MENTORAI TERMINAL DASHBOARD ==={C_RESET}\n")
            
            print(f"{C_BOLD}Phase:{C_RESET} {C_YELLOW}{status['current_phase']}{C_RESET}")
            print(f"{C_BOLD}Model:{C_RESET} {C_GREEN}{status['active_model']}{C_RESET}")
            if status["detail"]:
                print(f"{C_BOLD}Detail:{C_RESET} {status['detail']}")
            
            print("\n" + draw_progress_bar(status['progress_percent']))
            print(f"\n{C_BOLD}{C_GRAY}--- Live Logs (Last 20 lines) ---{C_RESET}")
            
            for line in status["lines"]:
                if "[PHASE" in line:
                    print(f"{C_PURPLE}{C_BOLD}{line}{C_RESET}")
                elif "Generating" in line or "Judging" in line:
                    print(f"{C_CYAN}{line}{C_RESET}")
                elif "Error" in line or "Exception" in line:
                    print(f"{C_RED}{line}{C_RESET}")
                else:
                    print(f"{C_GRAY}{line}{C_RESET}")
                    
            print(f"\n{C_GRAY}(Press Ctrl+C to exit){C_RESET}")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nExiting dashboard.")

if __name__ == "__main__":
    main()
