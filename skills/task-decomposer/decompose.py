#!/usr/bin/env python3
"""Break a goal into task objects per SCHEMAS.md format"""
import json, subprocess, sys
from datetime import datetime

def get_next_id():
    r = subprocess.run(["python3","./scripts/state_manager.py","read"], capture_output=True, text=True)
    if r.returncode == 0:
        return json.loads(r.stdout)["system"]["next_task_id"]
    return 1

def decompose(goal):
    g = goal.lower()
    if any(w in g for w in ["build","create","make"]):
        return ["Plan and design", "Implement core", "Test and verify", "Document and finish"]
    if "deploy" in g:
        return ["Prepare package", "Run deployment", "Verify live"]
    if "research" in g or "investigate" in g:
        return ["Gather information", "Analyse findings", "Document results"]
    return ["Understand goal", "Plan approach", "Execute", "Review and complete"]

def main():
    if len(sys.argv) < 2: print("Usage: python3 decompose.py <goal> [phase] [--create]"); sys.exit(1)
    goal = sys.argv[1]
    phase = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "03_monetise"
    create = "--create" in sys.argv
    steps = decompose(goal)
    start = get_next_id()
    print(f"=== {goal} ===\n")
    for i, step in enumerate(steps):
        tid = f"task_{start+i:03d}"
        print(f"{tid}: {step}")
        if create:
            subprocess.run(["python3","./scripts/state_manager.py","task","create", step, f"Part of: {goal}"])
    print(f"\n{len(steps)} tasks")

if __name__ == '__main__': main()
