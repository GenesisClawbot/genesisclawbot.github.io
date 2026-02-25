#!/usr/bin/env python3
"""
Genesis State Manager v3.1
All state mutations go through this script. Provides:
- Backup before every write
- JSON validation after every write
- Automatic recovery from corruption
- Dual logging to SQLite + ATTEMPTS.log

Usage:
  python3 state_manager.py read
  python3 state_manager.py heartbeat
  python3 state_manager.py update <dotted.path> <value>
  python3 state_manager.py log <phase> <action> <result> [lesson]
  python3 state_manager.py event <type> <phase> <description> <outcome> [metadata_json]
  python3 state_manager.py milestone <name>
  python3 state_manager.py task create <name> <description>
  python3 state_manager.py task update <task_id> <status> [result]
  python3 state_manager.py experiment create <hypothesis> <approach> <kill_criteria> <deadline_days>
  python3 state_manager.py experiment update <exp_id> <status> [result] [lesson]
  python3 state_manager.py transaction <expense|revenue> <amount> <description> <category> <approved_by>
  python3 state_manager.py cloud_spend <amount>
"""
import json, os, sys, shutil, sqlite3
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(SCRIPT_DIR)
STATE_PATH = os.path.join(WORKSPACE, "STATE.json")
STATE_BACKUP = os.path.join(WORKSPACE, "STATE.json.bak")
LOG_PATH = os.path.join(WORKSPACE, "logs", "ATTEMPTS.log")
DB_PATH = os.path.join(WORKSPACE, "memory", "memory.db")

def _now():
    return datetime.utcnow().isoformat() + "Z"

def _load_state():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"ERROR: STATE.json issue: {e}")
        if os.path.exists(STATE_BACKUP):
            print("Recovering from backup...")
            shutil.copy2(STATE_BACKUP, STATE_PATH)
            with open(STATE_PATH) as f:
                return json.load(f)
        print("CRITICAL: No backup. Cannot proceed.")
        sys.exit(1)

def _save_state(state):
    if os.path.exists(STATE_PATH):
        shutil.copy2(STATE_PATH, STATE_BACKUP)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(state, f, indent=2)
    try:
        with open(tmp) as f:
            json.load(f)
        os.replace(tmp, STATE_PATH)
    except json.JSONDecodeError as e:
        print(f"ERROR: Written state invalid: {e}. Restoring backup.")
        os.remove(tmp)
        if os.path.exists(STATE_BACKUP):
            shutil.copy2(STATE_BACKUP, STATE_PATH)
        sys.exit(1)

def _log_file(phase, action, result, lesson=""):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    entry = f"[{_now()}] [PHASE:{phase}] [ACTION:{action}] [RESULT:{result}]"
    if lesson: entry += f" [LESSON:{lesson}]"
    with open(LOG_PATH, 'a') as f:
        f.write(entry + "\n")

def _log_db(etype, phase, desc, outcome, meta=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO events (type,phase,description,outcome,metadata) VALUES (?,?,?,?,?)",
                     (etype, phase, desc, outcome, json.dumps(meta) if meta else None))
        conn.commit(); conn.close()
    except Exception as e:
        print(f"WARNING: DB write failed: {e}")

def _log(etype, phase, desc, outcome, meta=None):
    _log_db(etype, phase, desc, outcome, meta)
    _log_file(phase, desc, outcome)

# ── Commands ──

def cmd_read():
    print(json.dumps(_load_state(), indent=2))

def cmd_heartbeat():
    s = _load_state()
    s['system']['last_heartbeat'] = _now()
    s['system']['heartbeat_count'] = s['system'].get('heartbeat_count', 0) + 1
    _save_state(s)
    _log("heartbeat", s['system']['phase'], f"Heartbeat #{s['system']['heartbeat_count']}", "success")
    print(f"Heartbeat #{s['system']['heartbeat_count']} at {s['system']['last_heartbeat']}")

def cmd_update(path, value):
    s = _load_state()
    keys = path.split('.')
    obj = s
    for k in keys[:-1]:
        if k not in obj: obj[k] = {}
        obj = obj[k]
    try: parsed = json.loads(value)
    except: parsed = value
    obj[keys[-1]] = parsed
    _save_state(s)
    _log("action", s['system'].get('phase','?'), f"Updated {path}", "success")
    print(f"Updated {path} = {parsed}")

def cmd_log(phase, action, result, lesson=""):
    _log("action", phase, action, result, {"lesson": lesson} if lesson else None)
    print(f"Logged: [{phase}] {action} -> {result}")

def cmd_event(etype, phase, desc, outcome, meta_json=None):
    meta = json.loads(meta_json) if meta_json else None
    _log(etype, phase, desc, outcome, meta)
    print(f"Event: [{etype}] {desc} -> {outcome}")

def cmd_milestone(name):
    s = _load_state()
    if name not in s.get('milestones', {}):
        print(f"ERROR: Unknown milestone '{name}'. Valid: {list(s['milestones'].keys())}")
        sys.exit(1)
    s['milestones'][name] = {"achieved": True, "timestamp": _now(), "last_verified": _now()}
    _save_state(s)
    _log("milestone", s['system']['phase'], f"Milestone: {name}", "success")
    print(f"Milestone '{name}' achieved")

def cmd_task_create(name, desc):
    s = _load_state()
    tid = f"task_{s['system']['next_task_id']:03d}"
    s['system']['next_task_id'] += 1
    task = {"id": tid, "name": name, "status": "queued", "phase": s['system']['phase'],
            "created": _now(), "updated": _now(), "description": desc,
            "blocked_reason": None, "result": None, "error": None, "attempts": 0}
    s['tasks']['queued'].append(task)
    _save_state(s)
    _log("action", s['system']['phase'], f"Task created: {tid} - {name}", "success")
    print(f"Created {tid}: {name}")

def cmd_task_update(tid, new_status, result=None):
    s = _load_state()
    task = None; src = None
    for ln in ['active','queued','completed','failed','blocked_waiting_human']:
        for i, t in enumerate(s['tasks'][ln]):
            if t['id'] == tid:
                task = s['tasks'][ln].pop(i); src = ln; break
        if task: break
    if not task:
        print(f"ERROR: Task {tid} not found"); sys.exit(1)
    task['status'] = new_status; task['updated'] = _now()
    if result: task['result'] = result
    if new_status == 'active': task['attempts'] += 1
    dest = {'queued':'queued','active':'active','completed':'completed',
            'failed':'failed','blocked':'blocked_waiting_human'}.get(new_status, 'active')
    s['tasks'][dest].append(task)
    if new_status in ('completed','failed'):
        s['system']['consecutive_no_action_heartbeats'] = 0
    _save_state(s)
    _log("action", s['system']['phase'], f"Task {tid} -> {new_status}" + (f": {result}" if result else ""),
         "success" if new_status == "completed" else new_status)
    print(f"Task {tid}: {src} -> {dest}")

def cmd_exp_create(hyp, approach, kill, days):
    s = _load_state()
    eid = f"exp_{s['system']['next_experiment_id']:03d}"
    s['system']['next_experiment_id'] += 1
    dl = (datetime.utcnow() + timedelta(days=int(days))).isoformat() + "Z"
    exp = {"id": eid, "hypothesis": hyp, "approach": approach, "status": "active",
           "cost_gbp": 0, "revenue_gbp": 0, "started": _now(), "deadline": dl,
           "kill_criteria": kill, "result": None, "lesson": None}
    s['experiments']['strategies_tried'].append(exp)
    s['experiments']['total_attempted'] += 1
    _save_state(s)
    _log("action", s['system']['phase'], f"Experiment: {eid} - {hyp[:50]}", "success")
    print(f"Created {eid}: deadline {dl}")

def cmd_exp_update(eid, status, result=None, lesson=None):
    s = _load_state()
    for exp in s['experiments']['strategies_tried']:
        if exp['id'] == eid:
            exp['status'] = status
            if result: exp['result'] = result
            if lesson: exp['lesson'] = lesson
            if status == 'succeeded': s['experiments']['total_succeeded'] += 1
            elif status in ('failed','killed'): s['experiments']['total_failed'] += 1
            _save_state(s)
            _log("action", s['system']['phase'], f"Experiment {eid} -> {status}", status,
                 {"lesson": lesson} if lesson else None)
            if lesson:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("INSERT INTO lessons (category,lesson,confidence) VALUES (?,?,?)",
                                 ("strategy", lesson, 0.7))
                    conn.commit(); conn.close()
                except: pass
            print(f"Experiment {eid} -> {status}"); return
    print(f"ERROR: Experiment {eid} not found"); sys.exit(1)

def cmd_transaction(ttype, amount, desc, cat, approved):
    s = _load_state()
    amount = float(amount)
    tid = f"txn_{s['system']['next_transaction_id']:03d}"
    s['system']['next_transaction_id'] += 1
    txn = {"id": tid, "date": _now(), "type": ttype, "amount_gbp": amount,
           "description": desc, "category": cat, "approved_by": approved}
    s['finances']['transactions'].append(txn)
    if ttype == "expense":
        s['finances']['total_expenses_gbp'] += amount
        s['finances']['current_balance_gbp'] -= amount
    elif ttype == "revenue":
        s['finances']['total_revenue_gbp'] += amount
        s['finances']['current_balance_gbp'] += amount
    _save_state(s)
    _log("financial", s['system']['phase'], f"{ttype}: £{amount:.2f} - {desc}", "success")
    print(f"{tid}: {ttype} £{amount:.2f} | Balance: £{s['finances']['current_balance_gbp']:.2f}")

def cmd_cloud_spend(amount):
    s = _load_state()
    amount = float(amount)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if s['finances'].get('cloud_api_spend_today_date') != today:
        s['finances']['cloud_api_spend_today_gbp'] = 0
        s['finances']['cloud_api_spend_today_date'] = today
    new_daily = s['finances']['cloud_api_spend_today_gbp'] + amount
    cap = 2.0
    if new_daily > cap:
        print(f"BLOCKED: Daily cap. Today: £{s['finances']['cloud_api_spend_today_gbp']:.2f} + £{amount:.2f} > £{cap:.2f}")
        _save_state(s); sys.exit(1)
    s['finances']['cloud_api_spend_today_gbp'] = new_daily
    s['finances']['cloud_api_spend_total_gbp'] = s['finances'].get('cloud_api_spend_total_gbp', 0) + amount
    _save_state(s)
    print(f"Cloud: +£{amount:.2f} | Today: £{new_daily:.2f}/£{cap:.2f}")

if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(1)
    cmd, args = sys.argv[1], sys.argv[2:]
    try:
        if cmd == "read": cmd_read()
        elif cmd == "heartbeat": cmd_heartbeat()
        elif cmd == "update" and len(args) >= 2: cmd_update(args[0], args[1])
        elif cmd == "log" and len(args) >= 3: cmd_log(args[0], args[1], args[2], args[3] if len(args)>3 else "")
        elif cmd == "event" and len(args) >= 4: cmd_event(args[0], args[1], args[2], args[3], args[4] if len(args)>4 else None)
        elif cmd == "milestone" and len(args) >= 1: cmd_milestone(args[0])
        elif cmd == "cloud_spend" and len(args) >= 1: cmd_cloud_spend(args[0])
        elif cmd == "task" and len(args) >= 1:
            if args[0] == "create" and len(args) >= 3: cmd_task_create(args[1], args[2])
            elif args[0] == "update" and len(args) >= 3: cmd_task_update(args[1], args[2], args[3] if len(args)>3 else None)
            else: print("task create <name> <desc> | task update <id> <status> [result]"); sys.exit(1)
        elif cmd == "experiment" and len(args) >= 1:
            if args[0] == "create" and len(args) >= 5: cmd_exp_create(args[1], args[2], args[3], args[4])
            elif args[0] == "update" and len(args) >= 3: cmd_exp_update(args[1], args[2], args[3] if len(args)>3 else None, args[4] if len(args)>4 else None)
            else: print("experiment create <hyp> <approach> <kill> <days> | experiment update <id> <status> [result] [lesson]"); sys.exit(1)
        elif cmd == "transaction" and len(args) >= 5: cmd_transaction(args[0], args[1], args[2], args[3], args[4])
        else: print(f"Unknown: {cmd}"); print(__doc__); sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}"); sys.exit(1)
