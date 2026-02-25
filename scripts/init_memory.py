#!/usr/bin/env python3
"""Initialize the Genesis memory database."""
import sqlite3, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(WORKSPACE, "memory", "memory.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL DEFAULT (datetime('now')),
        type TEXT NOT NULL CHECK(type IN ('action','error','milestone','financial','heartbeat','human_request')),
        phase TEXT,
        description TEXT NOT NULL,
        outcome TEXT CHECK(outcome IN ('success','failure','partial','pending') OR outcome IS NULL),
        metadata TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL DEFAULT (datetime('now')),
        category TEXT NOT NULL CHECK(category IN ('technical','strategy','market','tool','model','sandbox')),
        lesson TEXT NOT NULL,
        source_event_id INTEGER,
        confidence REAL DEFAULT 0.5 CHECK(confidence >= 0 AND confidence <= 1),
        times_validated INTEGER DEFAULT 0,
        FOREIGN KEY (source_event_id) REFERENCES events(id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS skills (
        name TEXT PRIMARY KEY,
        description TEXT,
        file_path TEXT,
        created TEXT NOT NULL DEFAULT (datetime('now')),
        last_used TEXT,
        times_used INTEGER DEFAULT 0,
        success_count INTEGER DEFAULT 0,
        failure_count INTEGER DEFAULT 0
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS experiments (
        id TEXT PRIMARY KEY,
        hypothesis TEXT NOT NULL,
        approach TEXT NOT NULL,
        status TEXT DEFAULT 'active' CHECK(status IN ('active','succeeded','failed','killed')),
        cost_gbp REAL DEFAULT 0,
        revenue_gbp REAL DEFAULT 0,
        started TEXT NOT NULL DEFAULT (datetime('now')),
        deadline TEXT,
        ended TEXT,
        result TEXT,
        lesson TEXT,
        kill_criteria TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        experiment_id TEXT,
        status TEXT DEFAULT 'planning' CHECK(status IN ('planning','building','testing','deployed','earning','killed')),
        directory TEXT,
        url TEXT,
        created TEXT NOT NULL DEFAULT (datetime('now')),
        deployed TEXT,
        monthly_revenue_gbp REAL DEFAULT 0,
        FOREIGN KEY (experiment_id) REFERENCES experiments(id)
    )""")

    c.execute("CREATE INDEX IF NOT EXISTS idx_events_phase ON events(phase)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(type)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON events(timestamp)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_lessons_cat ON lessons(category)")

    conn.commit()
    tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"Database initialised at {DB_PATH}")
    print(f"Tables ({len(tables)}): {', '.join(tables)}")
    conn.close()

if __name__ == "__main__":
    init_db()
