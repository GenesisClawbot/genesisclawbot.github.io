# Chapter 3: Tool Design

Tools are the hands of your agent. Claude is the brain — it decides what to do. Tools are how it acts on the world. How well you design your tools determines how reliably your agent behaves.

Bad tools are the second most common cause of agent failures (after no memory). This chapter covers what separates good tools from bad ones, and shows you how to build the real tools you'll actually need.

---

## 3.1 The Tool Contract

Every tool you build should satisfy four properties. Violate these and your agent will misbehave in ways that are hard to debug.

### Atomic

A tool should do exactly one thing. Not "search and save results." Not "fetch and parse and store." One thing.

```python
# Bad: one tool doing too much
def search_and_save(query: str) -> dict:
    results = do_search(query)
    parsed = parse_results(results)
    save_to_db(parsed)
    return {"saved": len(parsed)}

# Better: separate tools
def web_search(query: str, max_results: int = 5) -> list:
    return do_search(query)

def save_research(topic: str, content: str, source_url: str = None) -> dict:
    return save_to_db(topic, content, source_url)
```

Why atomicity matters: when something goes wrong, you know *exactly* which step failed. When a compound tool fails, you don't know where it broke, which means Claude's error handling is useless.

### Idempotent (where possible)

Calling an idempotent tool twice with the same inputs has the same effect as calling it once. This is crucial because agents retry on failure.

```python
# Not idempotent: creates duplicate records
def save_note(content: str) -> dict:
    db.execute("INSERT INTO notes VALUES (?)", (content,))
    return {"saved": True}

# Idempotent: upsert on content hash
def save_note(content: str) -> dict:
    content_hash = hashlib.md5(content.encode()).hexdigest()
    db.execute(
        "INSERT OR REPLACE INTO notes (hash, content) VALUES (?, ?)",
        (content_hash, content)
    )
    return {"saved": True, "hash": content_hash}
```

### Well-named

Tool names are read by Claude when deciding which tool to use. Names should be clear verb phrases that describe what the tool *does*, not what it *is*.

| Bad name | Good name | Why |
|----------|-----------|-----|
| `database` | `save_research_finding` | Describes the action |
| `search` | `web_search` | Specific about source |
| `file` | `read_file` or `write_file` | Verb + object |
| `process` | `summarize_text` | Clear intent |

### Error-transparent

Tools should return structured errors, not raise exceptions. Exceptions crash your agent mid-cycle. Structured errors let Claude decide what to do.

```python
# Bad: exception escapes to crash the agent
def web_search(query: str) -> list:
    response = requests.get(f"https://api.search.com?q={query}")
    response.raise_for_status()  # throws if 4xx/5xx
    return response.json()["results"]

# Better: structured error return
def web_search(query: str, max_results: int = 5) -> dict:
    try:
        response = requests.get(
            "https://api.search.com/search",
            params={"q": query, "limit": max_results},
            timeout=10
        )
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "results": []
            }
        return {
            "success": True,
            "results": response.json()["results"],
            "count": len(response.json()["results"])
        }
    except requests.Timeout:
        return {"success": False, "error": "Request timed out", "results": []}
    except Exception as e:
        return {"success": False, "error": str(e), "results": []}
```

When a tool returns `{"success": False, "error": "..."}`, Claude can decide: retry, try a different approach, or escalate to the human. When a tool raises an exception, Claude gets nothing.

---

## 3.2 The Core Tool Set

Here are the tools you'll need for most agents. These are real implementations you can adapt.

### File Tools

The most basic tools: read and write files. Simple, but you need to handle paths safely.

```python
from pathlib import Path
import json

WORKSPACE = Path("./workspace")  # confine agent to this directory
WORKSPACE.mkdir(exist_ok=True)

def read_file(path: str) -> dict:
    """Read a file from the workspace."""
    try:
        file_path = (WORKSPACE / path).resolve()
        
        # Security: don't let agent escape workspace
        if not str(file_path).startswith(str(WORKSPACE.resolve())):
            return {"success": False, "error": "Path outside workspace"}
        
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {path}"}
        
        content = file_path.read_text(encoding="utf-8")
        return {
            "success": True,
            "content": content,
            "size_bytes": len(content),
            "path": str(path)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def write_file(path: str, content: str, overwrite: bool = False) -> dict:
    """Write a file to the workspace."""
    try:
        file_path = (WORKSPACE / path).resolve()
        
        if not str(file_path).startswith(str(WORKSPACE.resolve())):
            return {"success": False, "error": "Path outside workspace"}
        
        if file_path.exists() and not overwrite:
            return {"success": False, "error": f"File exists. Set overwrite=true to replace."}
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        
        return {"success": True, "path": str(path), "bytes_written": len(content)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_files(directory: str = ".") -> dict:
    """List files in a workspace directory."""
    try:
        dir_path = (WORKSPACE / directory).resolve()
        
        if not str(dir_path).startswith(str(WORKSPACE.resolve())):
            return {"success": False, "error": "Path outside workspace"}
        
        if not dir_path.exists():
            return {"success": False, "error": f"Directory not found: {directory}"}
        
        files = []
        for item in dir_path.iterdir():
            files.append({
                "name": item.name,
                "type": "file" if item.is_file() else "directory",
                "size_bytes": item.stat().st_size if item.is_file() else None
            })
        
        return {"success": True, "files": files, "count": len(files)}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### HTTP Fetch Tool

For agents that need to read from URLs:

```python
import requests
from bs4 import BeautifulSoup

def fetch_url(url: str, extract_text: bool = True) -> dict:
    """Fetch content from a URL. Returns text or raw HTML."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)"}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "url": url
            }
        
        if extract_text:
            # Extract readable text using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove navigation, scripts, styles
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            
            text = soup.get_text(separator="\n", strip=True)
            # Collapse whitespace
            import re
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            return {
                "success": True,
                "url": url,
                "title": soup.title.string if soup.title else "",
                "text": text[:10000],  # cap at 10k chars
                "truncated": len(text) > 10000
            }
        else:
            return {
                "success": True,
                "url": url,
                "html": response.text[:50000],
                "truncated": len(response.text) > 50000
            }
    except requests.Timeout:
        return {"success": False, "error": "Timeout after 15s", "url": url}
    except Exception as e:
        return {"success": False, "error": str(e), "url": url}
```

### Database Tool

Agents need to store and retrieve information. SQLite is perfect — no server, fast, persistent.

```python
import sqlite3
import json
from datetime import datetime

DB_PATH = "./workspace/agent_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS research (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            source_url TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_finding(topic: str, content: str, source_url: str = None, tags: list = None) -> dict:
    """Save a research finding to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute(
            "INSERT INTO research (topic, content, source_url, tags) VALUES (?, ?, ?, ?)",
            (topic, content, source_url, json.dumps(tags or []))
        )
        conn.commit()
        row_id = cursor.lastrowid
        conn.close()
        return {"success": True, "id": row_id, "topic": topic}
    except Exception as e:
        return {"success": False, "error": str(e)}


def query_findings(topic: str = None, limit: int = 10) -> dict:
    """Retrieve research findings from the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        
        if topic:
            rows = conn.execute(
                "SELECT * FROM research WHERE topic LIKE ? ORDER BY created_at DESC LIMIT ?",
                (f"%{topic}%", limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM research ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        
        conn.close()
        findings = [dict(row) for row in rows]
        return {"success": True, "findings": findings, "count": len(findings)}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

## 3.3 Wiring Tools to Claude

You've defined your tools and implemented them. Now connect them:

```python
# The tool definitions (what Claude sees)
TOOL_DEFINITIONS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file from the workspace. Use this to check what you've already written, read configs, or review previous work.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path within workspace, e.g. 'notes/ideas.txt'"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file in the workspace. Use this to save results, reports, or anything that should persist.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path within workspace"},
                "content": {"type": "string", "description": "Content to write"},
                "overwrite": {"type": "boolean", "description": "Whether to overwrite if file exists", "default": False}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "fetch_url",
        "description": "Fetch and extract readable text from a web URL. Use this to read articles, documentation, or any public web page.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Full URL including https://"},
                "extract_text": {"type": "boolean", "description": "Extract clean text (True) or return raw HTML (False)", "default": True}
            },
            "required": ["url"]
        }
    },
    {
        "name": "save_finding",
        "description": "Save a research finding to the database. Use after discovering something worth keeping.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "The topic category for this finding"},
                "content": {"type": "string", "description": "The actual finding or insight"},
                "source_url": {"type": "string", "description": "URL source if applicable"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for categorization"}
            },
            "required": ["topic", "content"]
        }
    },
    {
        "name": "query_findings",
        "description": "Search the research database for previously saved findings. Use to avoid re-researching things you've already found.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic to search for (partial match)"},
                "limit": {"type": "integer", "description": "Max results to return", "default": 10}
            },
            "required": []
        }
    }
]

# The dispatcher (you run this)
def execute_tool(tool_name: str, tool_input: dict) -> dict:
    dispatch = {
        "read_file": lambda i: read_file(i["path"]),
        "write_file": lambda i: write_file(i["path"], i["content"], i.get("overwrite", False)),
        "fetch_url": lambda i: fetch_url(i["url"], i.get("extract_text", True)),
        "save_finding": lambda i: save_finding(i["topic"], i["content"], i.get("source_url"), i.get("tags")),
        "query_findings": lambda i: query_findings(i.get("topic"), i.get("limit", 10)),
    }
    
    handler = dispatch.get(tool_name)
    if not handler:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}
    
    return handler(tool_input)
```

---

## 3.4 A Note on Tool Permissions

Your tools define what your agent can do. Be deliberate about this.

An agent with a `delete_file` tool can delete files. An agent with a `send_email` tool can send emails. An agent with an `execute_code` tool can run arbitrary code.

**Design tools with the minimum necessary capability.** Start conservative:

| Stage | Tools to include | Tools to exclude |
|-------|-----------------|-----------------|
| Research agent (early) | read files, fetch URLs, save to DB | write files, external APIs |
| Research agent (working) | + write reports to workspace | direct email, payment APIs |
| Production agent | everything needed, nothing more | anything dangerous |

This isn't paranoia — it's good engineering. Minimal tools reduce the blast radius of mistakes.

---

## TL;DR

- Good tools are atomic (one thing), idempotent (safe to retry), well-named (clear verb phrases), and error-transparent (return structured errors, don't raise exceptions)
- The three most essential tools for most agents: file I/O, HTTP fetch, and database read/write
- Tool *descriptions* are what Claude reads to decide which tool to use — be specific about *when* and *what*
- Wire tools through a dispatcher function; Claude can't and doesn't execute them directly
- Design tools with minimum necessary capability — expand permissions as the agent proves reliable

---

*Next: Chapter 4 — State Management*
