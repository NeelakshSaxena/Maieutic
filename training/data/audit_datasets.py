import os
import json
from datasets import load_dataset

def audit_socrateach():
    print("Auditing SocraTeach (Single and Multi)...")
    try:
        # Load single-turn dataset
        ds_single = load_dataset("ulises-c/SocraTeach_Single", split="train", streaming=True)
        single_count = 0
        for _ in ds_single:
            single_count += 1
        print(f"[SocraTeach_Single] Estimated examples: {single_count}")
        
        # Load multi-turn dataset
        ds_multi = load_dataset("ulises-c/SocraTeach_Multi", split="train", streaming=True)
        multi_count = 0
        for _ in ds_multi:
            multi_count += 1
        print(f"[SocraTeach_Multi] Estimated examples: {multi_count}")
    except Exception as e:
        print(f"Error auditing SocraTeach: {e}")

def audit_mathdial():
    print("\nAuditing MathDial...")
    try:
        ds = load_dataset("eth-nlped/mathdial", split="train", streaming=True)
        count = 0
        for _ in ds:
            count += 1
        print(f"[MathDial] Estimated examples: {count}")
    except Exception as e:
        print(f"Error auditing MathDial: {e}")

def audit_eedi():
    print("\nAuditing Eedi Question-Anchored Tutoring Dialogues...")
    try:
        ds = load_dataset("Eedi/Question-Anchored-Tutoring-Dialogues-2k", split="train", streaming=True)
        count = 0
        for _ in ds:
            count += 1
        print(f"[Eedi] Estimated examples: {count}")
    except Exception as e:
        print(f"Error auditing Eedi: {e}")

def audit_cima():
    print("\nAuditing CIMA (Requires manual download from GitHub: kstats/CIMA)...")
    print("Please download from https://github.com/kstats/CIMA")
    
if __name__ == "__main__":
    print("Starting dataset audit pipeline...\n")
    audit_socrateach()
    audit_mathdial()
    audit_eedi()
    audit_cima()
    print("\nAudit pipeline complete.")
