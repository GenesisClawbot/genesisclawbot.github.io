"""Genesis-01 Live Dashboard — functional agent swarm visibility."""

import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI(title="Genesis-01 Dashboard")


@app.post("/send")
async def send_message(message: str = Form(...)):
    """Send a message to the Genesis CEO via the gateway."""
    try:
        result = subprocess.run(
            ["openclaw", "message", "send", "--channel", "webchat", "--target", "main", "-m", message],
            capture_output=True, text=True, timeout=30
        )
        # Fallback: write to a file the agent reads next heartbeat
        notify = Path("/workspace/NOTIFICATION.md")
        notify.write_text(f"# Message from Nikita\n\n{message}\n\n_Received {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}_\n")
    except Exception:
        # Write to notification file as fallback
        notify = Path("/workspace/NOTIFICATION.md")
        notify.write_text(f"# Message from Nikita\n\n{message}\n\n_Received {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}_\n")
    return RedirectResponse(url="/", status_code=303)

CLAWTEAM_DIR = Path.home() / ".clawteam"
WORKSPACE = Path("/workspace")
WORLDVIEW = WORKSPACE / "WORLDVIEW.md"
SESSION_DIR = Path.home() / ".openclaw" / "agents"
LOG_DIR = Path("/tmp/openclaw")


def read_worldview():
    try:
        return WORLDVIEW.read_text()
    except Exception:
        return "_No WORLDVIEW.md found_"


def read_clawteam_tasks():
    tasks_dir = CLAWTEAM_DIR / "tasks" / "genesis"
    tasks = []
    if tasks_dir.exists():
        for f in sorted(tasks_dir.glob("task-*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                tasks.append(json.loads(f.read_text()))
            except Exception:
                pass
    return tasks


def read_clawteam_inboxes():
    inboxes_dir = CLAWTEAM_DIR / "teams" / "genesis" / "inboxes"
    messages = []
    if inboxes_dir.exists():
        for agent_dir in inboxes_dir.iterdir():
            if agent_dir.is_dir():
                for msg_file in sorted(agent_dir.glob("msg-*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
                    try:
                        msg = json.loads(msg_file.read_text())
                        msg["_agent"] = agent_dir.name
                        messages.append(msg)
                    except Exception:
                        pass
    return sorted(messages, key=lambda m: m.get("timestamp", ""), reverse=True)[:30]


def read_session_events():
    """Read actual agent actions from session JSONL files — tool calls, thinking, results."""
    events = []
    if not SESSION_DIR.exists():
        return events
    for agent_dir in SESSION_DIR.iterdir():
        if not agent_dir.is_dir():
            continue
        sessions_dir = agent_dir / "sessions"
        if not sessions_dir.exists():
            continue
        jsonl_files = list(sessions_dir.glob("*.jsonl"))
        if not jsonl_files:
            continue
        newest = max(jsonl_files, key=lambda f: f.stat().st_mtime)
        agent_id = agent_dir.name
        try:
            for line in newest.read_text().splitlines():
                try:
                    obj = json.loads(line)
                    if obj.get("type") != "message":
                        continue
                    msg = obj.get("message", {})
                    role = msg.get("role", "")
                    ts = obj.get("timestamp", "")
                    ts_short = ts[:19].replace("T", " ") if isinstance(ts, str) and len(ts) > 19 else ""
                    content = msg.get("content", "")

                    if role == "assistant" and isinstance(content, list):
                        for block in content:
                            bt = block.get("type", "")
                            if bt == "text":
                                txt = block.get("text", "").strip()
                                if len(txt) > 3:
                                    events.append({
                                        "time": ts_short,
                                        "agent": agent_id,
                                        "type": "think",
                                        "detail": txt[:500]
                                    })
                            elif bt == "toolCall":
                                name = block.get("name", "?")
                                args = block.get("arguments", {})
                                # Extract the interesting part
                                if name == "exec":
                                    detail = args.get("command", "")[:300]
                                elif name == "read":
                                    detail = args.get("file_path", "")
                                elif name == "write":
                                    detail = f'{args.get("file_path", "")} ({len(args.get("content", ""))} chars)'
                                elif name == "edit":
                                    detail = f'{args.get("path", args.get("file_path", ""))}'
                                elif name == "web_search":
                                    detail = args.get("query", "")
                                else:
                                    detail = json.dumps(args)[:200]
                                events.append({
                                    "time": ts_short,
                                    "agent": agent_id,
                                    "type": f"tool:{name}",
                                    "detail": detail
                                })
                    elif role == "toolResult":
                        tool_name = msg.get("toolName", "")
                        result_content = msg.get("content", [])
                        txt = ""
                        if isinstance(result_content, list):
                            for item in result_content:
                                if isinstance(item, dict):
                                    txt += item.get("text", "")
                                else:
                                    txt += str(item)
                        elif isinstance(result_content, str):
                            txt = result_content
                        if txt.strip():
                            events.append({
                                "time": ts_short,
                                "agent": agent_id,
                                "type": f"result:{tool_name}",
                                "detail": txt.strip()[:400]
                            })
                except Exception:
                    pass
        except Exception:
            pass
    events.sort(key=lambda e: e.get("time", ""), reverse=True)
    return events[:80]


def read_session_activity():
    agents = []
    if SESSION_DIR.exists():
        for agent_dir in SESSION_DIR.iterdir():
            if agent_dir.is_dir():
                sessions_dir = agent_dir / "sessions"
                if sessions_dir.exists():
                    jsonl_files = list(sessions_dir.glob("*.jsonl"))
                    if jsonl_files:
                        newest = max(jsonl_files, key=lambda f: f.stat().st_mtime)
                        stat = newest.stat()
                        age_sec = time.time() - stat.st_mtime
                        agents.append({
                            "id": agent_dir.name,
                            "session": newest.name[:8],
                            "size_kb": round(stat.st_size / 1024, 1),
                            "last_active": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%H:%M:%S"),
                            "age_min": round(age_sec / 60, 1),
                            "alive": age_sec < 1800,
                        })
    return sorted(agents, key=lambda a: a["age_min"])


def get_uptime():
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = LOG_DIR / f"openclaw-{today}.log"
        if log_file.exists():
            first_line = log_file.open().readline()
            obj = json.loads(first_line)
            start = obj.get("time", "")
            if start:
                start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                delta = datetime.now(timezone.utc) - start_dt
                hours = int(delta.total_seconds() // 3600)
                mins = int((delta.total_seconds() % 3600) // 60)
                return f"{hours}h {mins}m"
    except Exception:
        pass
    return "?"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    worldview = read_worldview()
    tasks = read_clawteam_tasks()
    messages = read_clawteam_inboxes()
    sessions = read_session_activity()
    events = read_session_events()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    uptime = get_uptime()

    active_count = sum(1 for s in sessions if s["alive"])
    task_active = sum(1 for t in tasks if t.get("status") == "in_progress")
    task_done = sum(1 for t in tasks if t.get("status") == "completed")
    task_pending = sum(1 for t in tasks if t.get("status") == "pending")

    # Task rows
    task_rows = ""
    for t in tasks[:20]:
        status = t.get("status", "?")
        cls = {"pending": "st-pending", "in_progress": "st-active", "completed": "st-done", "blocked": "st-blocked"}.get(status, "")
        task_rows += f'<tr><td class="{cls}">{esc(status)}</td><td>{esc(t.get("subject", "?")[:70])}</td><td>{esc(t.get("owner", "-"))}</td><td class="ts">{esc(t.get("updatedAt", t.get("createdAt", ""))[:19])}</td></tr>'
    if not task_rows:
        task_rows = '<tr><td colspan="4" class="muted">No ClawTeam tasks yet</td></tr>'

    # Message rows
    msg_rows = ""
    for m in messages[:15]:
        content = str(m.get("content", m.get("message", "")))[:120]
        msg_rows += f'<tr><td>{esc(m.get("from", "?"))}</td><td>{esc(m.get("to", m.get("_agent", "?")))}</td><td>{esc(content)}</td><td class="ts">{esc(str(m.get("timestamp", ""))[:19])}</td></tr>'
    if not msg_rows:
        msg_rows = '<tr><td colspan="4" class="muted">No inter-agent messages yet</td></tr>'

    # Agent rows
    agent_rows = ""
    for s in sessions:
        status = "ACTIVE" if s["alive"] else "idle"
        cls = "st-active" if s["alive"] else "st-idle"
        agent_rows += f'<tr><td class="{cls}">{status}</td><td>{esc(s["id"])}</td><td class="ts">{s["last_active"]}</td><td>{s["age_min"]}m</td><td>{s["size_kb"]}KB</td></tr>'
    if not agent_rows:
        agent_rows = '<tr><td colspan="5" class="muted">No sessions yet</td></tr>'

    # Event feed (newest first, already sorted)
    event_html = ""
    for e in events:
        t = e["type"]
        if t == "think":
            cls = "ev-think"
            label = "THINKING"
        elif t.startswith("tool:"):
            cls = "ev-tool"
            label = t.replace("tool:", "").upper()
        elif t.startswith("result:"):
            cls = "ev-result"
            label = f"RESULT"
        else:
            cls = ""
            label = t
        detail = esc(e["detail"])
        agent = esc(e.get("agent", "?")[:12])
        ts = e.get("time", "")[-8:]  # just HH:MM:SS
        event_html += f'<div class="ev {cls}"><span class="ts">{ts}</span> <span class="ev-agent">{agent}</span> <span class="ev-label">{label}</span> <span class="ev-detail">{detail}</span></div>'
    if not event_html:
        event_html = '<div class="ev muted">Waiting for agent activity...</div>'

    wv_html = esc(worldview)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="15">
<title>Genesis-01</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#111;color:#ccc;font:12px/1.5 'SF Mono','Menlo','Consolas',monospace}}
.top{{background:#181818;padding:10px 16px;border-bottom:1px solid #282828;display:flex;justify-content:space-between;align-items:center}}
.top h1{{font-size:13px;font-weight:500;color:#eee;letter-spacing:0.5px}}
.top .info{{color:#666;font-size:11px}}
.counters{{display:flex;gap:24px;padding:8px 16px;background:#151515;border-bottom:1px solid #222;font-size:11px}}
.counters .c{{display:flex;align-items:center;gap:6px}}
.counters .c .n{{font-weight:600;font-size:14px}}
.counters .c.green .n{{color:#4a2}}
.counters .c.blue .n{{color:#48f}}
.counters .c.yellow .n{{color:#da3}}
.counters .c.gray .n{{color:#666}}
.cols{{display:grid;grid-template-columns:1fr 1fr;min-height:0}}
.col{{border-right:1px solid #222;display:flex;flex-direction:column}}
.col:last-child{{border-right:none}}
.section{{border-bottom:1px solid #222;flex:none}}
.section.grow{{flex:1;min-height:0;display:flex;flex-direction:column}}
.section h2{{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1.5px;color:#555;padding:8px 12px;background:#161616;border-bottom:1px solid #222;position:sticky;top:0;z-index:1}}
.section .body{{padding:0;overflow-y:auto;max-height:350px}}
.section.grow .body{{flex:1;overflow-y:auto;max-height:500px}}
table{{width:100%;border-collapse:collapse}}
th{{text-align:left;font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#444;padding:4px 10px;border-bottom:1px solid #222;position:sticky;top:0;background:#131313;z-index:1}}
td{{padding:4px 10px;border-bottom:1px solid #1a1a1a;font-size:11px;overflow:hidden;text-overflow:ellipsis;max-width:400px}}
tr:hover{{background:#1a1a1a}}
.ts{{color:#555}}
.muted{{color:#444;padding:16px 10px;font-style:italic}}
.st-active{{color:#4a2;font-weight:600}}
.st-done{{color:#555}}
.st-pending{{color:#da3}}
.st-blocked{{color:#c44}}
.st-idle{{color:#444}}
.ev{{padding:3px 12px;font-size:11px;line-height:1.6;border-bottom:1px solid #1a1a1a}}
.ev:hover{{background:#1a1a1a}}
.ev-agent{{color:#68a;font-weight:600;margin-right:4px}}
.ev-label{{display:inline-block;min-width:70px;font-weight:600;margin-right:6px}}
.ev-detail{{color:#999;word-break:break-all}}
.ev-think{{background:#1a1a16}}
.ev-think .ev-label{{color:#ba4}}
.ev-think .ev-detail{{color:#cca;white-space:pre-wrap}}
.ev-tool .ev-label{{color:#48a}}
.ev-tool .ev-detail{{color:#8ac}}
.ev-result .ev-label{{color:#555}}
.ev-result .ev-detail{{color:#777;font-size:10px}}
.wv{{padding:12px;white-space:pre-wrap;font-size:11px;line-height:1.6;color:#888;overflow-y:auto;max-height:300px}}
.full{{grid-column:1/-1;border-top:1px solid #222}}
.msg-bar{{display:flex;gap:0;padding:0;border-bottom:1px solid #222}}
.msg-bar input{{flex:1;background:#151515;border:none;color:#ccc;padding:8px 16px;font:12px/1.5 'SF Mono','Menlo','Consolas',monospace;outline:none}}
.msg-bar input::placeholder{{color:#444}}
.msg-bar button{{background:#222;color:#888;border:none;padding:8px 20px;font:12px/1.5 'SF Mono','Menlo',monospace;cursor:pointer}}
.msg-bar button:hover{{background:#333;color:#ccc}}
</style>
</head>
<body>
<div class="top">
  <h1>genesis-01</h1>
  <div class="info">{now} / model: minimax-m2.7 / uptime: {uptime} / refresh: 15s</div>
</div>
<div class="counters">
  <div class="c green"><span class="n">{active_count}</span> agents</div>
  <div class="c blue"><span class="n">{task_active}</span> running</div>
  <div class="c yellow"><span class="n">{task_pending}</span> pending</div>
  <div class="c gray"><span class="n">{task_done}</span> done</div>
  <div class="c gray"><span class="n">{len(messages)}</span> msgs</div>
  <div class="c gray"><span class="n">{len(events)}</span> events</div>
</div>
<form class="msg-bar" action="/send" method="post">
  <input type="text" name="message" placeholder="Message Genesis CEO..." autocomplete="off">
  <button type="submit">Send</button>
</form>
<div class="cols">
  <div class="col">
    <div class="section">
      <h2>Tasks</h2>
      <div class="body"><table><tr><th>Status</th><th>Task</th><th>Owner</th><th>Updated</th></tr>{task_rows}</table></div>
    </div>
    <div class="section">
      <h2>Agents</h2>
      <div class="body"><table><tr><th>Status</th><th>Agent ID</th><th>Last</th><th>Age</th><th>Size</th></tr>{agent_rows}</table></div>
    </div>
    <div class="section">
      <h2>Messages</h2>
      <div class="body"><table><tr><th>From</th><th>To</th><th>Content</th><th>Time</th></tr>{msg_rows}</table></div>
    </div>
  </div>
  <div class="col">
    <div class="section grow">
      <h2>Agent Activity (newest first)</h2>
      <div class="body">{event_html}</div>
    </div>
  </div>
</div>
<div class="full">
  <div class="section">
    <h2>Worldview</h2>
    <div class="wv">{wv_html}</div>
  </div>
</div>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
