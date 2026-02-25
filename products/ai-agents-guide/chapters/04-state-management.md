# Chapter 4: State Management

Here's the uncomfortable truth about agent state: most developers don't think about it until something breaks. Then they spend hours debugging why their agent forgot what it was doing, re-ran a task that already completed, or corrupted its own data.

State management isn't glamorous. But it's the difference between an agent that reliably runs for weeks and one that works fine for ten minutes and then dies mysteriously.

---

## 4.1 Why Agents Die Without Proper State

Consider this: your agent runs successfully for three cycles. On the fourth cycle, the API call times out. Python raises an exception. The process crashes.

If all your state was in Python variables, it's gone. The next time the agent starts, it has no idea what happened. Did it complete the research? Did it save anything? Which tasks are done?

Without persistence, every agent restart is a fresh start. With persistence, a restart picks up where you left off.

There are three categories of state every agent needs:

**Operational state** — what is the agent doing right now?
- Current phase/task
- What's in progress vs complete
- Any errors or blockers

**Short-term memory** — what happened recently?
- Last few actions and their results
- Current working context
- Temporary data for the current task

**Long-term memory** — what does the agent know across sessions?
- Learned information
- Historical decisions and outcomes
- Accumulated research or data

Different state types need different storage. We'll cover all three.

---

## 4.2 JSON State Files: Simple and Reliable

For operational state, a JSON file is often the right choice. It's:
- Human-readable (you can inspect it when debugging)
- Easy to edit manually (useful for course corrections)
- Versioned by git (full history of state changes)
- Requires zero infrastructure

Here's a real state schema:

```python
# state.json — the agent's operational state
{
    "system": {
        "phase": "research",          # current phase: init|research|writing|done
        "heartbeat_count": 14,        # how many cycles completed
        "last_heartbeat": "2026-02-25T14:30:00Z",
        "consecutive_idle": 0,        # cycles with no meaningful action
        "health": "ok"                # ok|degraded|stuck
    },
    "tasks": {
        "active": [
            {
                "id": "task_001",
                "name": "Research competitor pricing",
                "status": "in_progress",
                "started": "2026-02-25T14:00:00Z",
                "attempts": 1
            }
        ],
        "completed": ["task_000"],
        "failed": []
    },
    "context": {
        "current_topic": "competitor analysis",
        "urls_checked": ["https://example.com/pricing"],
        "findings_count": 7
    }
}
```

### Safe State Management

Never write directly to the state file. Always: read → modify → validate → backup → write.

```python
import json
import shutil
from pathlib import Path
from datetime import datetime

STATE_PATH = Path("state.json")
BACKUP_PATH = Path("state.json.bak")

def load_state() -> dict:
    """Load state with fallback to backup."""
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except json.JSONDecodeError:
            print("WARNING: state.json corrupted, trying backup...")
            if BACKUP_PATH.exists():
                return json.loads(BACKUP_PATH.read_text())
            raise RuntimeError("Both state.json and backup are corrupted")
    
    # Fresh start
    return {
        "system": {
            "phase": "init",
            "heartbeat_count": 0,
            "last_heartbeat": None,
            "consecutive_idle": 0,
            "health": "ok"
        },
        "tasks": {"active": [], "completed": [], "failed": []},
        "context": {}
    }


def save_state(state: dict) -> None:
    """Save state with backup. Never corrupts the file."""
    # Validate before writing
    required_keys = ["system", "tasks", "context"]
    for key in required_keys:
        if key not in state:
            raise ValueError(f"State missing required key: {key}")
    
    # Backup current good state
    if STATE_PATH.exists():
        shutil.copy(STATE_PATH, BACKUP_PATH)
    
    # Write new state atomically (write to temp, then rename)
    temp_path = STATE_PATH.with_suffix(".tmp")
    temp_path.write_text(json.dumps(state, indent=2, default=str))
    temp_path.rename(STATE_PATH)  # atomic on most filesystems


def update_state(key_path: str, value) -> None:
    """Update a single key in state using dot notation."""
    state = load_state()
    
    # Navigate to the right key
    keys = key_path.split(".")
    target = state
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = value
    
    save_state(state)

# Usage:
# update_state("system.phase", "research")
# update_state("system.heartbeat_count", 5)
```

The `temp_path.rename()` trick is important — it's atomic on POSIX filesystems. If the process crashes mid-write, you either have the old file or the new file, never a partial write.

---

## 4.3 State Machine Patterns

Agents benefit from explicit state machines — defined phases with defined transitions. Without them, the agent can wander into inconsistent states.

Here's a simple state machine for a research agent:

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class Phase(Enum):
    INIT = "init"
    PLANNING = "planning"
    RESEARCHING = "researching"
    WRITING = "writing"
    REVIEWING = "reviewing"
    DONE = "done"
    STUCK = "stuck"
    ERROR = "error"

# Valid transitions: which phases can move to which
VALID_TRANSITIONS = {
    Phase.INIT: [Phase.PLANNING],
    Phase.PLANNING: [Phase.RESEARCHING, Phase.STUCK],
    Phase.RESEARCHING: [Phase.WRITING, Phase.PLANNING, Phase.STUCK],
    Phase.WRITING: [Phase.REVIEWING, Phase.RESEARCHING, Phase.STUCK],
    Phase.REVIEWING: [Phase.DONE, Phase.WRITING],
    Phase.DONE: [],
    Phase.STUCK: [Phase.PLANNING],
    Phase.ERROR: [Phase.PLANNING, Phase.STUCK],
}

def transition_phase(current: str, new_phase: Phase) -> bool:
    """Attempt to transition to a new phase. Returns True if successful."""
    try:
        current_phase = Phase(current)
    except ValueError:
        print(f"WARNING: Unknown current phase '{current}', allowing transition")
        current_phase = Phase.ERROR
    
    if new_phase not in VALID_TRANSITIONS.get(current_phase, []):
        print(f"INVALID TRANSITION: {current_phase.value} → {new_phase.value}")
        return False
    
    update_state("system.phase", new_phase.value)
    print(f"Phase transition: {current_phase.value} → {new_phase.value}")
    return True

# Usage in agent loop:
def agent_cycle(state: dict) -> dict:
    phase = state["system"]["phase"]
    
    if phase == Phase.INIT.value:
        # Initialize and transition to planning
        state["tasks"]["active"] = get_initial_tasks()
        transition_phase(phase, Phase.PLANNING)
    
    elif phase == Phase.PLANNING.value:
        # Plan next research actions
        next_task = pick_next_task(state["tasks"])
        if next_task:
            transition_phase(phase, Phase.RESEARCHING)
        else:
            transition_phase(phase, Phase.WRITING)
    
    elif phase == Phase.RESEARCHING.value:
        # Do research
        result = do_research(state["tasks"]["active"][0])
        if result["success"]:
            mark_task_complete(state["tasks"]["active"][0])
            transition_phase(phase, Phase.PLANNING)
        else:
            increment_failures(state)
            if state["tasks"]["active"][0]["attempts"] >= 3:
                transition_phase(phase, Phase.STUCK)
    
    # ... etc
    return load_state()  # return fresh state after transitions
```

Explicit state machines prevent the agent from being simultaneously "in research" and "in writing" — a common source of bugs.

---

## 4.4 SQLite for Structured Data

JSON is great for operational state, but it's poor for large amounts of structured data. If your agent is saving research findings, tracking experiments, or building a knowledge base, use SQLite.

SQLite is part of Python's standard library. It stores data in a single file. It supports full SQL. It handles concurrent reads fine, and is fast enough for any single-agent workload.

```python
import sqlite3
from contextlib import contextmanager
from pathlib import Path
import json

DB_PATH = Path("./memory/agent.db")
DB_PATH.parent.mkdir(exist_ok=True)

@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    conn.execute("PRAGMA journal_mode=WAL")  # better concurrent access
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                type TEXT NOT NULL,
                description TEXT NOT NULL,
                outcome TEXT,
                metadata TEXT  -- JSON
            );
            
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                topic TEXT NOT NULL,
                content TEXT NOT NULL,
                source_url TEXT,
                tags TEXT,  -- JSON array
                confidence REAL DEFAULT 1.0
            );
            
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                made_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                decision TEXT NOT NULL,
                reasoning TEXT,
                outcome TEXT,
                lesson TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_findings_topic ON findings(topic);
            CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);
        """)


def log_event(type: str, description: str, outcome: str = None, metadata: dict = None):
    """Log an event to the database."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO events (type, description, outcome, metadata) VALUES (?, ?, ?, ?)",
            (type, description, outcome, json.dumps(metadata) if metadata else None)
        )


def save_finding(topic: str, content: str, source_url: str = None, 
                 tags: list = None, confidence: float = 1.0) -> int:
    """Save a research finding. Returns the new row ID."""
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO findings (topic, content, source_url, tags, confidence) 
               VALUES (?, ?, ?, ?, ?)""",
            (topic, content, source_url, json.dumps(tags or []), confidence)
        )
        return cursor.lastrowid


def get_findings(topic: str = None, limit: int = 20) -> list:
    """Retrieve findings, optionally filtered by topic."""
    with get_db() as conn:
        if topic:
            rows = conn.execute(
                """SELECT * FROM findings WHERE topic LIKE ? 
                   ORDER BY created_at DESC LIMIT ?""",
                (f"%{topic}%", limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM findings ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        
        return [dict(row) for row in rows]


def record_decision(decision: str, reasoning: str) -> int:
    """Record a decision for later review."""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO decisions (decision, reasoning) VALUES (?, ?)",
            (decision, reasoning)
        )
        return cursor.lastrowid


def update_decision_outcome(decision_id: int, outcome: str, lesson: str = None):
    """Update a decision with its outcome and lesson learned."""
    with get_db() as conn:
        conn.execute(
            "UPDATE decisions SET outcome = ?, lesson = ? WHERE id = ?",
            (outcome, lesson, decision_id)
        )
```

---

## 4.5 Putting It Together: A Complete State Layer

Here's how operational state (JSON) and memory (SQLite) work together in a single agent:

```python
class AgentState:
    """Unified interface for all agent state."""
    
    def __init__(self):
        init_db()
        self._state = load_state()
    
    # --- Operational state ---
    
    @property
    def phase(self) -> str:
        return self._state["system"]["phase"]
    
    @property
    def heartbeat_count(self) -> int:
        return self._state["system"]["heartbeat_count"]
    
    def increment_heartbeat(self):
        self._state["system"]["heartbeat_count"] += 1
        self._state["system"]["last_heartbeat"] = datetime.utcnow().isoformat()
        save_state(self._state)
    
    def set_phase(self, new_phase: Phase):
        if transition_phase(self.phase, new_phase):
            self._state = load_state()  # reload after transition
    
    def get_active_tasks(self) -> list:
        return self._state["tasks"]["active"]
    
    def complete_task(self, task_id: str):
        tasks = self._state["tasks"]
        task = next((t for t in tasks["active"] if t["id"] == task_id), None)
        if task:
            tasks["active"].remove(task)
            tasks["completed"].append(task_id)
            save_state(self._state)
    
    # --- Memory ---
    
    def remember(self, topic: str, content: str, source: str = None):
        finding_id = save_finding(topic, content, source)
        log_event("memory", f"Saved finding: {topic}", "success", {"id": finding_id})
        return finding_id
    
    def recall(self, topic: str, limit: int = 5) -> list:
        return get_findings(topic, limit)
    
    def log(self, description: str, outcome: str = "ok", metadata: dict = None):
        log_event("action", description, outcome, metadata)
```

This class gives you a clean interface so your main loop doesn't have to think about *how* state is stored — just *what* it wants to know.

```python
# Main loop using the state layer
def main():
    state = AgentState()
    
    while True:
        state.increment_heartbeat()
        
        # Check what phase we're in
        if state.phase == "init":
            state.set_phase(Phase.PLANNING)
        
        elif state.phase == "researching":
            tasks = state.get_active_tasks()
            if not tasks:
                state.set_phase(Phase.WRITING)
                continue
            
            task = tasks[0]
            result = do_research(task)
            
            if result["success"]:
                state.remember(task["name"], result["content"], result.get("url"))
                state.complete_task(task["id"])
                state.log(f"Completed research: {task['name']}", "success")
            else:
                state.log(f"Research failed: {task['name']}", "failure", result)
        
        time.sleep(900)
```

---

## TL;DR

- State has three types: operational (what's happening now), short-term (recent context), long-term (accumulated knowledge)
- Use JSON files for operational state; write atomically with backup to prevent corruption
- Use explicit state machines (defined phases and valid transitions) to prevent the agent from wandering into impossible states
- Use SQLite for structured memory: events, findings, decisions — anything you'll need to query later
- Build a unified state interface so your main loop doesn't think about storage mechanics, only semantics

---

*Next: Chapter 5 — Memory That Actually Works*
