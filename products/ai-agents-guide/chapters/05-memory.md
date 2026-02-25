# Chapter 5: Memory That Actually Works

Memory is the hardest part of agent design to get right. It's also the part most developers underestimate until they're debugging an agent that just re-discovered information it found three days ago.

The challenge: Claude has no memory between calls. Every API call starts fresh. The context window that holds the conversation is limited — you can't just dump everything Claude has ever known into every prompt. You need a deliberate memory architecture.

This chapter gives you one that works.

---

## 5.1 The Memory Problem

Consider what happens as your agent runs:

- **Cycle 1:** Finds 5 research articles on Topic A. Saves them.
- **Cycle 2:** Does more research. Context is fresh — Claude doesn't know what it found in Cycle 1.
- **Cycle 50:** Has accumulated 200 findings, 50 decisions, and 15 completed tasks. None of that fits in a context window without crushing it.

You have two problems:
1. **Recall:** Claude needs to know relevant history before making decisions
2. **Capacity:** You can't send all history every cycle — context windows have limits and every token costs money

The solution is a tiered memory system: different storage and retrieval strategies for different types of memory.

```
┌─────────────────────────────────────────────┐
│  WORKING MEMORY (in context)                │
│  Current cycle's context, state summary     │
│  ~1-2K tokens per cycle                     │
├─────────────────────────────────────────────┤
│  SHORT-TERM MEMORY (recent history)         │
│  Last N actions, recent findings            │
│  Retrieved and injected each cycle          │
├─────────────────────────────────────────────┤
│  LONG-TERM MEMORY (SQLite)                  │
│  All findings, decisions, events            │
│  Queried when needed, not loaded wholesale  │
└─────────────────────────────────────────────┘
```

---

## 5.2 Working Memory: What Goes in Context Every Cycle

Every cycle, Claude needs to know:
- What phase the agent is in
- What tasks are active
- What it did last cycle (immediate context)
- Any relevant prior findings (selectively retrieved)

Here's how to structure the system prompt to inject working memory:

```python
def build_working_memory(state: dict, recent_events: list, relevant_findings: list) -> str:
    """Build the memory section of the system prompt."""
    
    lines = [
        "=== CURRENT STATE ===",
        f"Phase: {state['system']['phase']}",
        f"Heartbeat: {state['system']['heartbeat_count']}",
        f"Active tasks: {len(state['tasks']['active'])}",
        "",
        "=== ACTIVE TASKS ===",
    ]
    
    for task in state["tasks"]["active"][:3]:  # max 3 tasks in context
        lines.append(f"- [{task['status']}] {task['name']} (attempts: {task.get('attempts', 0)})")
    
    if recent_events:
        lines.extend(["", "=== RECENT ACTIONS (last 5) ==="])
        for event in recent_events[-5:]:
            lines.append(f"- {event['timestamp'][:16]} | {event['description']} → {event['outcome']}")
    
    if relevant_findings:
        lines.extend(["", "=== RELEVANT PRIOR FINDINGS ==="])
        for finding in relevant_findings[:3]:  # max 3 in context
            lines.append(f"- [{finding['topic']}] {finding['content'][:200]}...")
    
    return "\n".join(lines)
```

The key principle: **inject what's relevant, not what's complete.** You're curating, not dumping.

---

## 5.3 Episodic Memory: What Happened and What I Learned

Episodic memory is your event log — what the agent did, when, and what happened. This is critical for detecting patterns (e.g., "I've tried this 3 times and failed each time").

We set up the events table in Chapter 4. Here's how to use it effectively:

```python
def get_recent_events(limit: int = 20, hours_back: int = 24) -> list:
    """Get recent events for working memory."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT timestamp, type, description, outcome, metadata
               FROM events 
               WHERE timestamp > datetime('now', ?)
               ORDER BY timestamp DESC 
               LIMIT ?""",
            (f"-{hours_back} hours", limit)
        ).fetchall()
    return [dict(row) for row in rows]


def get_failure_pattern(task_name: str, hours_back: int = 48) -> dict:
    """Check if a task has been failing repeatedly."""
    with get_db() as conn:
        failures = conn.execute(
            """SELECT COUNT(*) as count, MAX(timestamp) as last_attempt
               FROM events
               WHERE description LIKE ? AND outcome = 'failure'
               AND timestamp > datetime('now', ?)""",
            (f"%{task_name}%", f"-{hours_back} hours")
        ).fetchone()
    
    return {
        "failure_count": failures["count"],
        "last_attempt": failures["last_attempt"],
        "is_repeating": failures["count"] >= 3
    }


def get_decisions_log(limit: int = 10) -> list:
    """Get recent decisions for context."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT made_at, decision, reasoning, outcome, lesson
               FROM decisions
               ORDER BY made_at DESC
               LIMIT ?""",
            (limit,)
        ).fetchall()
    return [dict(row) for row in rows]
```

Use `get_failure_pattern()` at the start of each cycle to detect if you're stuck:

```python
def check_for_stuck_state(state: dict) -> bool:
    """Detect if the agent is repeating failed actions."""
    for task in state["tasks"]["active"]:
        pattern = get_failure_pattern(task["name"])
        if pattern["is_repeating"]:
            print(f"STUCK: {task['name']} has failed {pattern['failure_count']} times")
            return True
    return False
```

---

## 5.4 Semantic Memory: Finding Relevant Findings

The hardest part of long-term memory is *retrieval*: given a current task, which of the 200 findings I've accumulated are actually relevant?

The naive approach — search by keyword — misses synonyms and related concepts. The sophisticated approach — vector embeddings — requires running an embedding model.

Here's a middle path that works well for most agents: **tag-based retrieval with keyword fallback**.

```python
def save_finding_with_tags(topic: str, content: str, tags: list = None, 
                            source_url: str = None) -> int:
    """Save a finding with explicit tags for later retrieval."""
    # Auto-generate tags from content if not provided
    if not tags:
        tags = extract_keywords(content)
    
    return save_finding(topic, content, source_url, tags)


def extract_keywords(text: str) -> list:
    """Extract keywords from text for tagging. Simple but effective."""
    # Remove common words
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "in", "on", 
                  "at", "to", "for", "of", "and", "or", "but", "with", "from"}
    
    words = text.lower().split()
    words = [w.strip(".,;:!?\"'") for w in words]
    keywords = [w for w in words if len(w) > 4 and w not in stop_words]
    
    # Return top keywords by frequency
    from collections import Counter
    return [word for word, _ in Counter(keywords).most_common(5)]


def find_relevant_findings(current_task: str, limit: int = 5) -> list:
    """Find findings relevant to the current task."""
    # Extract keywords from current task
    keywords = extract_keywords(current_task)
    
    with get_db() as conn:
        # Build a query that matches any of the keywords
        conditions = " OR ".join(
            [f"(topic LIKE ? OR content LIKE ? OR tags LIKE ?)" for _ in keywords]
        )
        params = []
        for kw in keywords:
            params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%"])
        params.append(limit)
        
        rows = conn.execute(
            f"""SELECT *, 
                (CASE WHEN topic LIKE ? THEN 3 ELSE 0 END +
                 CASE WHEN tags LIKE ? THEN 2 ELSE 0 END +
                 CASE WHEN content LIKE ? THEN 1 ELSE 0 END) as relevance_score
                FROM findings
                WHERE {conditions}
                ORDER BY relevance_score DESC, created_at DESC
                LIMIT ?""",
            [f"%{current_task}%", f"%{current_task}%", f"%{current_task}%"] + params
        ).fetchall()
    
    return [dict(row) for row in rows]
```

For agents that need better semantic search, you can add embedding-based retrieval. But this simple approach handles most practical use cases without the overhead.

---

## 5.5 A Complete Memory System: 60 Lines

Here's everything from this chapter assembled into a usable module:

```python
# memory_system.py — complete agent memory system
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from collections import Counter

DB_PATH = Path("./memory/agent.db")
DB_PATH.parent.mkdir(exist_ok=True)

@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

def setup():
    with db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT NOT NULL,
                outcome TEXT DEFAULT 'ok',
                meta TEXT
            );
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                topic TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT,
                tags TEXT DEFAULT '[]'
            );
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                decision TEXT NOT NULL,
                reasoning TEXT,
                outcome TEXT,
                lesson TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_f_topic ON findings(topic);
        """)

def log(description: str, outcome: str = "ok", meta: dict = None):
    with db() as conn:
        conn.execute(
            "INSERT INTO events (description, outcome, meta) VALUES (?, ?, ?)",
            (description, outcome, json.dumps(meta) if meta else None)
        )

def remember(topic: str, content: str, source: str = None, tags: list = None) -> int:
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO findings (topic, content, source, tags) VALUES (?, ?, ?, ?)",
            (topic, content, source, json.dumps(tags or []))
        )
        return cur.lastrowid

def recall(query: str, limit: int = 5) -> list:
    words = [w for w in query.lower().split() if len(w) > 3]
    if not words:
        return []
    
    with db() as conn:
        results = []
        seen = set()
        for word in words[:3]:  # check top 3 keywords
            rows = conn.execute(
                """SELECT * FROM findings 
                   WHERE topic LIKE ? OR content LIKE ?
                   ORDER BY ts DESC LIMIT ?""",
                (f"%{word}%", f"%{word}%", limit)
            ).fetchall()
            for row in rows:
                if row["id"] not in seen:
                    seen.add(row["id"])
                    results.append(dict(row))
        
        return results[:limit]

def recent_events(n: int = 10) -> list:
    with db() as conn:
        rows = conn.execute(
            "SELECT ts, description, outcome FROM events ORDER BY ts DESC LIMIT ?",
            (n,)
        ).fetchall()
    return [dict(r) for r in rows]

def decide(decision: str, reasoning: str) -> int:
    with db() as conn:
        cur = conn.execute(
            "INSERT INTO decisions (decision, reasoning) VALUES (?, ?)",
            (decision, reasoning)
        )
        return cur.lastrowid

def resolve_decision(decision_id: int, outcome: str, lesson: str = None):
    with db() as conn:
        conn.execute(
            "UPDATE decisions SET outcome = ?, lesson = ? WHERE id = ?",
            (outcome, lesson, decision_id)
        )

def failure_count(task_name: str, hours: int = 48) -> int:
    with db() as conn:
        row = conn.execute(
            """SELECT COUNT(*) as n FROM events
               WHERE description LIKE ? AND outcome = 'failure'
               AND ts > datetime('now', ?)""",
            (f"%{task_name}%", f"-{hours} hours")
        ).fetchone()
    return row["n"] if row else 0
```

Usage in your main loop:

```python
import memory_system as mem

mem.setup()  # call once at startup

# Log an action
mem.log("Started research on competitor pricing", "ok")

# Save a finding
finding_id = mem.remember(
    topic="competitor_pricing",
    content="Competitor X charges $99/month for basic tier, $299 for pro",
    source="https://competitor.com/pricing",
    tags=["pricing", "competitor", "saas"]
)

# Recall relevant findings before a task
relevant = mem.recall("pricing strategy")

# Check if stuck
if mem.failure_count("web_search") >= 3:
    # Escalate to human
    notify_human("web_search is failing repeatedly")
```

---

## TL;DR

- Memory has three tiers: working (in context every cycle), episodic (event log, queried for patterns), semantic (findings, queried by relevance)
- Inject curated working memory into the system prompt each cycle — not a full dump, but what's relevant to current task
- Use the event log to detect repeating failures and stuck states
- For finding retrieval, keyword matching is sufficient for most agents; add embeddings only if you hit real limits
- The 60-line `memory_system.py` module gives you everything you need to start

---

*Next: Chapter 6 — The Planning Loop*
