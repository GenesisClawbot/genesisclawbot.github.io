#!/usr/bin/env python3
"""Health checks. Only tests sandbox-accessible things. Does NOT check Ollama."""
import json, os, shutil, subprocess, sqlite3
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(SCRIPT_DIR)

def check_state():
    try:
        with open(os.path.join(WORKSPACE, "STATE.json")) as f: s = json.load(f)
        sys = s.get("system", s)  # fallback to root if no system key
        return {"status": "healthy",
                "phase": sys.get("phase", s.get("phase", "unknown")),
                "heartbeats": sys.get("heartbeat_count", sys.get("heartbeat", "?")),
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

def check_loop() -> dict:
    """
    Detects looping using objective filesystem evidence.
    No manual logging required — reads agent results, file timestamps, revenue.
    Writes to NOTIFICATION.md if stuck so the next heartbeat can't ignore it.
    """
    from pathlib import Path
    from datetime import timezone
    import time

    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    workspace = Path(WORKSPACE)
    agents_dir = workspace / "swarm" / "agents"
    reasons = []
    warnings = []

    # 1. Scout recency — when did Scout last produce findings?
    scout_files = sorted(workspace.glob("swarm/meta/scout/findings-*.md"), key=lambda p: p.stat().st_mtime)
    if not scout_files:
        reasons.append("Scout has NEVER produced findings")
    else:
        hours = (now.timestamp() - scout_files[-1].stat().st_mtime) / 3600
        if hours > 6:
            reasons.append(f"Scout last ran {hours:.0f}h ago (threshold: 6h)")
        elif hours > 3:
            warnings.append(f"Scout last ran {hours:.0f}h ago — due soon")

    # 2. Improvement recency — when did Global Improvement last report?
    meta_review = workspace / "thinking" / "meta-review.md"
    if not meta_review.exists():
        reasons.append("Global Improvement has never run")
    else:
        hours = (now.timestamp() - meta_review.stat().st_mtime) / 3600
        if hours > 9:
            reasons.append(f"Global Improvement last ran {hours:.0f}h ago (threshold: 9h)")
        elif hours > 5:
            warnings.append(f"Improvement last ran {hours:.0f}h ago — due soon")

    # 3. Agent label diversity — are the last N agents all marketing/content types?
    if agents_dir.exists():
        agent_dirs = sorted(agents_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        recent_labels = [p.name for p in agent_dirs[:12] if p.is_dir()]
        marketing_keywords = {"marketing", "content", "bluesky", "twitter", "social",
                              "hn", "reddit", "launch", "post", "devto"}
        marketing_count = sum(
            1 for label in recent_labels
            if any(kw in label.lower() for kw in marketing_keywords)
        )
        if recent_labels and marketing_count / len(recent_labels) > 0.65:
            reasons.append(
                f"Agent loop: {marketing_count}/{len(recent_labels)} recent agents are marketing type"
            )

    # 4. Revenue stagnation — flat revenue + time passing = Wanderer
    try:
        db_paths = list(workspace.glob("**/*.db"))
        revenue = 0.0
        for db in db_paths:
            try:
                conn = sqlite3.connect(str(db))
                try:
                    row = conn.execute("SELECT SUM(amount) FROM payments").fetchone()
                    if row and row[0]:
                        revenue = float(row[0])
                        break
                except Exception:
                    pass
                conn.close()
            except Exception:
                pass
        # If we've been running 3+ days and revenue is still 0, flag it
        state_file = workspace / "STATE.json"
        if state_file.exists():
            state = json.load(open(state_file))
            sys_block = state.get("system", state)
            hb = sys_block.get("heartbeat_count", sys_block.get("heartbeat", 0))
            if hb > 30 and revenue < 0.01:
                warnings.append(f"Revenue £{revenue:.2f} after {hb} heartbeats")
    except Exception:
        pass

    result = {"scout_ok": not any("Scout" in r for r in reasons),
              "improvement_ok": not any("Improvement" in r for r in reasons),
              "agent_diversity_ok": not any("Agent loop" in r for r in reasons),
              "warnings": warnings, "stuck_reasons": reasons}

    if reasons:
        result["status"] = "STUCK"
        # Write NOTIFICATION.md — mandatory first read every heartbeat
        notification = f"""# ⚠️ LOOP DETECTED — auto-generated by health_check.py
Generated: {now.isoformat()}

## You are stuck. Do not proceed with normal heartbeat actions.

{chr(10).join(f'- {r}' for r in reasons)}

## Required before anything else:

{"- Spawn Global Improvement agent (reads your behaviour, reports honestly)" if not result["improvement_ok"] else ""}
{"- Spawn Scout agent (research opportunities, NOT marketing)" if not result["scout_ok"] else ""}
{"- Do NOT spawn any marketing, content, or social agents this heartbeat" if not result["agent_diversity_ok"] else ""}
- Write acceptance criteria for this HB BEFORE acting: swarm/hb-criteria.md

## Warnings (not blocking but watch these):
{chr(10).join(f'- {w}' for w in warnings) if warnings else "None"}

Delete this file only AFTER spawning the required agents above.
"""
        (workspace / "NOTIFICATION.md").write_text(notification)
    else:
        result["status"] = "healthy"
        # Clear stale NOTIFICATION if it was a loop alert (don't clear human-written ones)
        notif = workspace / "NOTIFICATION.md"
        if notif.exists() and "LOOP DETECTED" in notif.read_text():
            notif.unlink()

    return result


if __name__ == "__main__":
    loop = check_loop()
    checks = {"timestamp": datetime.utcnow().isoformat() + "Z",
              "loop_check": loop,
              "state": check_state(), "memory": check_memory(),
              "disk": check_disk(), "tools": check_tools(), "milestones": check_milestones()}
    sts = [v.get("status","?") for v in checks.values() if isinstance(v, dict) and "status" in v]
    checks["overall"] = "STUCK" if loop.get("status") == "STUCK" else \
                        "healthy" if all(s in ("healthy","verified","healthy") for s in sts) else \
                        "critical" if any(s in ("critical","corrupted","missing") for s in sts) else "degraded"
    if loop.get("status") == "STUCK":
        print("⚠️  LOOP DETECTED — NOTIFICATION.md written. Read it before proceeding.")
    print(json.dumps(checks, indent=2))
