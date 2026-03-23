"""Overseer Dashboard — monitors the meta-agent watching Genesis."""

import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI(title="Overseer Dashboard")


@app.post("/send")
async def send_message(message: str = Form(...)):
    """Send a message to the Overseer via notification file."""
    notify = Path.home() / "Genesis" / "OVERSEER_NOTIFICATION.md"
    notify.write_text(f"# Message from Nikita\n\n{message}\n\n_Received {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}_\n")
    return RedirectResponse(url="/", status_code=303)

SESSION_DIR = Path.home() / ".openclaw-overseer" / "agents"
CLAWTEAM_DIR = Path.home() / ".clawteam"
OVERSEER_LOG = Path.home() / "Genesis" / "OVERSEER_LOG.md"
WORLDVIEW = Path.home() / "Genesis" / "WORLDVIEW.md"
GATEWAY_LOG = Path("/tmp/openclaw-overseer.log")


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def read_file(p):
    try:
        return p.read_text()
    except Exception:
        return ""


def read_session_events():
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
                                    events.append({"time": ts_short, "agent": agent_id, "type": "think", "detail": txt[:800]})
                            elif bt == "toolCall":
                                name = block.get("name", "?")
                                args = block.get("arguments", {})
                                if name == "exec":
                                    detail = args.get("command", "")[:400]
                                elif name == "read":
                                    detail = args.get("file_path", "")
                                elif name == "write":
                                    detail = f'{args.get("file_path", "")} ({len(args.get("content", ""))} chars)'
                                elif name == "edit":
                                    detail = f'{args.get("path", args.get("file_path", ""))}'
                                elif name == "web_search":
                                    detail = args.get("query", "")
                                else:
                                    detail = json.dumps(args)[:300]
                                events.append({"time": ts_short, "agent": agent_id, "type": f"tool:{name}", "detail": detail})
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
                            events.append({"time": ts_short, "agent": agent_id, "type": f"result:{tool_name}", "detail": txt.strip()[:500]})
                except Exception:
                    pass
        except Exception:
            pass
    events.sort(key=lambda e: e.get("time", ""), reverse=True)
    return events[:100]


def read_gateway_log_tail(n=30):
    lines = []
    if GATEWAY_LOG.exists():
        try:
            all_lines = GATEWAY_LOG.read_text().splitlines()
            for line in all_lines[-n:]:
                lines.append(line)
        except Exception:
            pass
    return lines


def read_clawteam_overseer():
    tasks = []
    tasks_dir = CLAWTEAM_DIR / "tasks" / "overseer"
    if tasks_dir.exists():
        for f in sorted(tasks_dir.glob("task-*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                tasks.append(json.loads(f.read_text()))
            except Exception:
                pass
    msgs = []
    inboxes_dir = CLAWTEAM_DIR / "teams" / "overseer" / "inboxes"
    if inboxes_dir.exists():
        for agent_dir in inboxes_dir.iterdir():
            if agent_dir.is_dir():
                for msg_file in sorted(agent_dir.glob("msg-*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
                    try:
                        msg = json.loads(msg_file.read_text())
                        msgs.append(msg)
                    except Exception:
                        pass
    return tasks[:20], sorted(msgs, key=lambda m: m.get("timestamp", ""), reverse=True)[:20]


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    events = read_session_events()
    overseer_log = read_file(OVERSEER_LOG)
    worldview = read_file(WORLDVIEW)
    tasks, msgs = read_clawteam_overseer()
    gateway_lines = read_gateway_log_tail(20)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    event_html = ""
    for e in events:
        t = e["type"]
        if t == "think":
            cls, label = "ev-think", "THINKING"
        elif t.startswith("tool:"):
            cls, label = "ev-tool", t.replace("tool:", "").upper()
        elif t.startswith("result:"):
            cls, label = "ev-result", "RESULT"
        else:
            cls, label = "", t
        ts = e.get("time", "")[-8:]
        event_html += f'<div class="ev {cls}"><span class="ts">{ts}</span> <span class="ev-label">{label}</span> <span class="ev-detail">{esc(e["detail"])}</span></div>'
    if not event_html:
        event_html = '<div class="ev muted">Waiting for first overseer heartbeat (~12:43 UTC)...</div>'

    log_html = esc(overseer_log) if overseer_log else "_No interventions yet_"

    gw_html = ""
    for line in reversed(gateway_lines):
        # Strip ANSI codes
        import re
        clean = re.sub(r'\x1b\[[0-9;]*m', '', line)
        gw_html += f'<div class="gw-line">{esc(clean[:200])}</div>'

    task_rows = ""
    for t in tasks[:10]:
        status = t.get("status", "?")
        task_rows += f'<tr><td>{esc(status)}</td><td>{esc(t.get("subject", "")[:60])}</td><td>{esc(t.get("owner", ""))}</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="15">
<title>Overseer</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0d0d0d;color:#ccc;font:12px/1.5 'SF Mono','Menlo','Consolas',monospace}}
.top{{background:#1a1210;padding:10px 16px;border-bottom:1px solid #332820;display:flex;justify-content:space-between;align-items:center}}
.top h1{{font-size:13px;font-weight:500;color:#e8a}}
.top .info{{color:#665;font-size:11px}}
.cols{{display:grid;grid-template-columns:1fr 1fr;min-height:0}}
.col{{border-right:1px solid #222;display:flex;flex-direction:column}}
.col:last-child{{border-right:none}}
.section{{border-bottom:1px solid #222}}
.section h2{{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1.5px;color:#665;padding:8px 12px;background:#141210;border-bottom:1px solid #222}}
.section .body{{padding:0;overflow-y:auto;max-height:400px}}
table{{width:100%;border-collapse:collapse}}
th{{text-align:left;font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#444;padding:4px 10px;border-bottom:1px solid #222}}
td{{padding:4px 10px;border-bottom:1px solid #1a1a1a;font-size:11px}}
.ts{{color:#555}}
.muted{{color:#444;padding:16px 10px;font-style:italic}}
.ev{{padding:3px 12px;font-size:11px;line-height:1.6;border-bottom:1px solid #1a1a1a}}
.ev:hover{{background:#1a1a1a}}
.ev-label{{display:inline-block;min-width:70px;font-weight:600;margin-right:6px}}
.ev-detail{{color:#999;word-break:break-all}}
.ev-think{{background:#1a1a16}}
.ev-think .ev-label{{color:#ba4}}
.ev-think .ev-detail{{color:#cca;white-space:pre-wrap}}
.ev-tool .ev-label{{color:#48a}}
.ev-tool .ev-detail{{color:#8ac}}
.ev-result .ev-label{{color:#555}}
.ev-result .ev-detail{{color:#777;font-size:10px}}
.log-content{{padding:12px;white-space:pre-wrap;font-size:11px;line-height:1.6;color:#888;max-height:300px;overflow-y:auto}}
.gw-line{{padding:1px 12px;font-size:10px;color:#666;border-bottom:1px solid #1a1a1a}}
.full{{grid-column:1/-1}}
.msg-bar{{display:flex;gap:0;padding:0;border-bottom:1px solid #222}}
.msg-bar input{{flex:1;background:#151210;border:none;color:#ccc;padding:8px 16px;font:12px/1.5 'SF Mono','Menlo','Consolas',monospace;outline:none}}
.msg-bar input::placeholder{{color:#444}}
.msg-bar button{{background:#221a15;color:#886;border:none;padding:8px 20px;font:12px/1.5 'SF Mono','Menlo',monospace;cursor:pointer}}
.msg-bar button:hover{{background:#332a20;color:#cca}}
</style>
</head>
<body>
<div class="top">
  <h1>overseer</h1>
  <div class="info">{now} / meta-agent monitoring genesis-01 / refresh: 15s</div>
</div>
<form class="msg-bar" action="/send" method="post">
  <input type="text" name="message" placeholder="Message Overseer..." autocomplete="off">
  <button type="submit">Send</button>
</form>
<div class="cols">
  <div class="col">
    <div class="section">
      <h2>Overseer Activity (newest first)</h2>
      <div class="body">{event_html}</div>
    </div>
    <div class="section">
      <h2>Overseer Tasks</h2>
      <div class="body">
        <table><tr><th>Status</th><th>Task</th><th>Owner</th></tr>{task_rows if task_rows else '<tr><td colspan="3" class="muted">No tasks</td></tr>'}</table>
      </div>
    </div>
  </div>
  <div class="col">
    <div class="section">
      <h2>Intervention Log</h2>
      <div class="log-content">{log_html}</div>
    </div>
    <div class="section">
      <h2>Gateway Log (tail)</h2>
      <div class="body">{gw_html if gw_html else '<div class="gw-line muted">No log entries</div>'}</div>
    </div>
  </div>
</div>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8282, reload=True)
