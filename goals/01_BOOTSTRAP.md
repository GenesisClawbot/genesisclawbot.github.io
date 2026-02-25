# Phase 1: Bootstrap — Know Thyself

## Read First
- ./SCHEMAS.md (data formats you MUST follow)
- ./SOUL.md (your rules and operating principles)

## Context
You are in a Docker sandbox. Your entire world is this workspace directory.
Use relative paths: ./STATE.json, ./scripts/init_memory.py, etc.
You CANNOT access the host filesystem, Ollama directly, or the internet from scripts.
The gateway handles inference for you — you just think and act within the workspace.

## Objective
Systematically test your capabilities, establish persistent memory, and prove
you can maintain yourself reliably across restarts.

## Tasks (do these in order, one per heartbeat cycle)

### Task 1: Tool Audit
Create a task via state_manager.py. Test each tool:
```bash
python3 --version
node --version
git --version
sqlite3 --version
jq --version
which curl
ls -la ./
df -h .
```
For each item in identity.json "expected_available":
- If it works → move to "confirmed_working"
- If it fails → move to "not_available" with error note
Update identity.json with empirical findings.

### Task 2: Memory System
Run: `python3 ./scripts/init_memory.py`
Then verify:
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('./memory/memory.db')
tables = [r[0] for r in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()]
print('Tables:', tables)
assert len(tables) >= 5, f'Expected 5+ tables, got {len(tables)}'
conn.execute(\"INSERT INTO events (type, phase, description, outcome) VALUES ('test', '01', 'Memory test', 'success')\")
conn.commit()
rows = conn.execute('SELECT * FROM events').fetchall()
print('Events:', len(rows))
conn.close()
print('MEMORY SYSTEM: OPERATIONAL')
"
```
Mark milestone memory_system_operational via state_manager.py.

### Task 3: State Manager Verification
Test all state_manager.py commands:
```bash
python3 ./scripts/state_manager.py read
python3 ./scripts/state_manager.py heartbeat
python3 ./scripts/state_manager.py log 01_bootstrap "state_manager_test" success "Works"
python3 ./scripts/state_manager.py event action 01_bootstrap "Tested state_manager" success
```
Verify STATE.json updated correctly.

### Task 4: Create First Skill
Build a skill in ./skills/workspace-summary/SKILL.md that reads STATE.json
and memory.db and produces a compact status report.
Test it works. Register in identity.json skills_created.
Mark milestone first_skill_created.

### Task 5: Restart Survival Test
Write a pre-restart marker to STATE.json and memory.db.
Message human: "[ACTION NEEDED] Please restart OpenClaw gateway to test restart survival."
Set task to blocked. After restart, verify data persists.

## Phase Completion
ALL must be true (verified, not assumed):
- [ ] identity.json has only confirmed capabilities (nothing in expected_available)
- [ ] memory.db operational with 5+ tables, read/write verified
- [ ] STATE.json managed exclusively via state_manager.py with backups working
- [ ] At least 1 skill created and tested
- [ ] Survived at least 1 gateway restart
- [ ] self_assessment_complete milestone achieved

When complete:
```bash
python3 ./scripts/state_manager.py update system.phase "02_skill_build"
python3 ./scripts/state_manager.py milestone self_assessment_complete
```
Message human: "[PHASE 1] [FYI] Bootstrap complete. X/Y tools confirmed. Memory operational. Ready for Phase 2."
