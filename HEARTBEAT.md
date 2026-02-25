# Heartbeat Protocol

## Every Heartbeat (3 steps only)

### Step 1: READ
Read ./STATE.json. Note:
- Current phase
- Active tasks (any stalled > 2 hours?)
- Any blocked tasks where human has responded?
- consecutive_no_action_heartbeats count

### Step 2: ACT
Do exactly ONE of these (in priority order):
1. If a blocked task has been unblocked by human → resume it
2. If an active task exists → do the next step of it
3. If a queued task exists → start the highest priority one
4. If nothing is queued → read current phase goal file, create a new task
5. If truly nothing to do → run health check, verify milestones still valid

If you take no action, increment consecutive_no_action_heartbeats.
If it reaches 5, send alert to human immediately.

### Step 3: WRITE
Run state_manager.py to:
- Record heartbeat: `python3 ./scripts/state_manager.py heartbeat`
- Update task status if changed
- Log the event to memory.db: `python3 ./scripts/state_manager.py event ...`

That is the entire heartbeat. Three steps. Do not add more.

## Periodic Tasks (handled by OpenClaw cron, NOT by you in heartbeat)
- Every 4 hours: Strategy review (cron job sends you a prompt)
- Daily at midnight: Daily report generation (cron job)
- Daily at 6am: Milestone verification (cron job)
