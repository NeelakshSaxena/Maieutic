import os
import json
import time
import random

def main():
    monitor_dir = os.path.join(os.path.dirname(__file__), "../outputs/monitor")
    os.makedirs(monitor_dir, exist_ok=True)
    metrics_file = os.path.join(monitor_dir, "metrics.jsonl")
    
    print(f"Generating mock data to {metrics_file}...")
    print("Press Ctrl+C to stop.")
    
    step = 0
    loss = 2.5
    lr = 2e-5
    
    try:
        while True:
            step += 10
            loss = max(0.5, loss - random.uniform(0.01, 0.05))
            epoch = step / 1000.0
            
            status = "TRAINING"
            if step % 50 == 0:
                status = "CHECKPOINTING"
                
            record = {
                "step": step,
                "loss": loss,
                "learning_rate": lr,
                "epoch": epoch,
                "tokens_per_second": random.uniform(1500, 2000),
                "samples_per_second": random.uniform(4.0, 6.0),
                "status": status,
                "is_mock": True,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            
            with open(metrics_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
                
            print(f"Mock step {step} written.")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nMock stopped.")
        
if __name__ == "__main__":
    main()
