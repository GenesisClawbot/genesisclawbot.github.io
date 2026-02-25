#!/usr/bin/env python3
"""Health checks. Only tests sandbox-accessible things. Does NOT check Ollama."""
import json, os, shutil, subprocess, sqlite3
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(SCRIPT_DIR)

def check_state():
    try:
        with open(os.path.join(WORKSPACE, "STATE.json")) as f: s = json.load(f)
        return {"status": "healthy", "phase": s["system"]["phase"],
                "heartbeats": s["system"]["heartbeat_count"],
                "has_backup": os.path.exists(os.path.join(WORKSPACE, "STATE.json.bak"))}
    except json.JSONDecodeError as e: return {"status": "corrupted", "error": str(e)}
    except FileNotFoundError: return {"status": "missing"}

def check_memory():
    try:
        conn = sqlite3.connect(os.path.join(WORKSPACE, "memory", "memory.db"))
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        conn.close()
        return {"status": "healthy" if len(tables) >= 5 else "incomplete",
                "tables": len(tables), "events": events}
    except Exception as e: return {"status": "error", "error": str(e)}

def check_disk():
    t, u, f = shutil.disk_usage(WORKSPACE)
    gb = f / (1024**3)
    return {"status": "healthy" if gb > 5 else "warning" if gb > 2 else "critical", "free_gb": round(gb, 1)}

def check_tools():
    tools = {}
    for t in ["python3", "node", "git", "sqlite3", "jq"]:
        try:
            r = subprocess.run(["which", t], capture_output=True, text=True, timeout=5)
            tools[t] = "available" if r.returncode == 0 else "missing"
        except: tools[t] = "error"
    return tools

def check_milestones():
    try:
        with open(os.path.join(WORKSPACE, "STATE.json")) as f: s = json.load(f)
        results = {}
        for name, m in s.get("milestones", {}).items():
            if m.get("achieved"):
                if name == "memory_system_operational":
                    try:
                        conn = sqlite3.connect(os.path.join(WORKSPACE, "memory", "memory.db"))
                        conn.execute("SELECT 1 FROM events LIMIT 1"); conn.close()
                        results[name] = "verified"
                    except: results[name] = "INVALID"
                else: results[name] = "assumed_valid"
        return results
    except: return {}

if __name__ == "__main__":
    checks = {"timestamp": datetime.utcnow().isoformat() + "Z",
              "state": check_state(), "memory": check_memory(),
              "disk": check_disk(), "tools": check_tools(), "milestones": check_milestones()}
    sts = [v.get("status","?") for v in checks.values() if isinstance(v, dict) and "status" in v]
    checks["overall"] = "healthy" if all(s in ("healthy","verified") for s in sts) else \
                         "critical" if any(s in ("critical","corrupted","missing") for s in sts) else "degraded"
    print(json.dumps(checks, indent=2))
