import os

with open('.env', 'r') as f:
    lines = f.readlines()

print("--- ENV FILE PREVIEW (Values Hidden) ---")
for i, line in enumerate(lines):
    line_clean = line.strip()
    if '=' in line_clean:
        key = line_clean.split('=')[0].strip()
        print(f"Line {i+1}: {key}=***")
    else:
        print(f"Line {i+1}: {repr(line_clean)}")
print("----------------------------------------")
