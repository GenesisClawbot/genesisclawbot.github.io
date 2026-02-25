# Project Genesis: The Complete Guide

## Self-Managing Autonomous Agent System

### Mac-Only • Docker Sandboxed • M4 MacBook Pro (24GB)

### Version 3.2 — February 2026

---

# Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Model Strategy](#2-model-strategy)
3. [Prerequisites](#3-prerequisites)
4. [Installation — Step by Step](#4-installation)
5. [Genesis Workspace & Bootstrap Files](#5-genesis-workspace)
6. [OpenClaw Configuration](#6-openclaw-configuration)
7. [Custom Sandbox Docker Image](#7-custom-sandbox-image)
8. [Activation Sequence](#8-activation)
9. [Monitoring & Daily Operations](#9-monitoring)
10. [Troubleshooting](#10-troubleshooting)
11. [Realistic Expectations](#11-expectations)

---

# 1. Architecture Overview

```
┌───────────────────────────────────────────────────────────────┐
│                    macOS (Your MacBook M4, 24GB)              │
│                                                               │
│  ┌─────────────────┐         ┌──────────────────────────────┐│
│  │  Ollama (Native) │◄───────│  Docker Desktop              ││
│  │  Metal GPU accel │ HTTP   │                              ││
│  │  Port 11434      │ :11434 │  ┌────────────────────────┐  ││
│  │                  │        │  │ OpenClaw Gateway        │  ││
│  │  Always loaded:  │        │  │ Container               │  ││
│  │  • glm-4.7-flash │        │  │ (Node.js, port 18789)   │  ││
│  │    (local fallbk)│        │  │                         │  ││
│  │                  │        │  │ Manages:                │  ││
│  │  Cloud primary:  │        │  │ • Sessions & Memory     │  ││
│  │  • minimax-m2.5  │        │  │ • Channels (Telegram)   │  ││
│  │    :cloud (free) │        │  │ • Heartbeat             │  ││
│  │  • glm-4.7:cloud │        │  │ • Model routing         │  ││
│  │    (free backup) │        │  └───────────┬────────────┘  ││
│  └─────────────────┘        │              │ spawns        ││
│                              │  ┌───────────▼────────────┐  ││
│  YOU ◄── Telegram ──►        │  │ Agent Sandbox           │  ││
│                              │  │ Container               │  ││
│                              │  │                         │  ││
│  Host filesystem             │  │ ISOLATION:              │  ││
│  NOT accessible ──────X      │  │ • network: restricted   │  ││
│                              │  │ • Non-root user         │  ││
│                              │  │ • Can only see:         │  ││
│                              │  │   ~/Genesis/ (mounted)  │  ││
│                              │  │                         │  ││
│                              │  │ HAS ACCESS TO:          │  ││
│                              │  │ • Python 3, Node.js     │  ││
│                              │  │ • Git, SQLite, jq       │  ││
│                              │  │ • File ops in workspace │  ││
│                              │  └────────────────────────┘  ││
│                              │                              ││
│  Volumes:                    │  ~/Genesis/ ──► /workspace   ││
│  ~/.openclaw/ ──────────────►│  (rw, agent's only world)   ││
│                              └──────────────────────────────┘│
└───────────────────────────────────────────────────────────────┘
```

### Important: Who runs what?

**EVERY setup step (1-10) is YOU, on your Mac, in Terminal.**
You are building the cage. The agent lives inside the cage only AFTER you
send the activation message at the end.

### What the agent CAN access (inside sandbox)

- `~/Genesis/` directory (read/write, mounted as `/workspace`)
- Ollama inference (via gateway, not direct from sandbox)
- Free cloud model APIs (MiniMax M2.5, GLM-4.7 via Ollama cloud routing)
- Telegram (messaging you for approvals/reports)

### What the agent CANNOT access

- Your home directory, Documents, Desktop, Downloads
- SSH keys, browser passwords, Keychain
- System files (`/etc`, `/proc`, `/sys`, Docker socket)
- Unrestricted internet from sandbox scripts
- Anything outside `~/Genesis/`

---

# 2. Model Strategy

## Why This Stack

One smart model beats juggling multiple dumber ones. An 8B model that
misunderstands an error or botches a state write is worse than a smarter
model that gets it right first time. The agent needs to be reliable, not fast.

We use MiniMax M2.5 cloud as primary — it's free, Opus-tier for coding,
and means zero RAM pressure on your Mac. Local GLM-4.7-Flash is the fallback
for when cloud is unavailable.

## The Stack: 3 Models, No Swapping

| Model                | Role                     | Cost | Where                  |
| -------------------- | ------------------------ | ---- | ---------------------- |
| `minimax-m2.5:cloud` | **Primary (everything)** | £0   | Free API via Ollama    |
| `glm-4.7-flash`      | **Local fallback**       | £0   | Local, loads on demand |
| `glm-4.7:cloud`      | **Backup fallback**      | £0   | Free API via Z.ai      |

### When to use each

```
Default (every heartbeat, every task)  → minimax-m2.5:cloud (free, Opus-tier)
MiniMax rate-limited or down           → glm-4.7-flash (local)
Both unavailable                       → glm-4.7:cloud (free backup)
All free options failing               → Claude Sonnet API (LAST RESORT, £2/day cap)
```

### Cloud-primary tradeoffs

Pros: Smarter model, zero RAM pressure, Mac runs cool.
Cons: Rate limits could change, latency (2-10s), privacy (context sent to MiniMax),
no offline mode. If this becomes a problem, flip to local-primary by changing one
line in openclaw.json (swap primary and first fallback).

### Pull Commands (run on your Mac)

```bash
# LOCAL fallback model (~10GB download)
ollama pull glm-4.7-flash

# FREE CLOUD — no download, routes to API
ollama pull minimax-m2.5:cloud
ollama pull glm-4.7:cloud

# EMBEDDINGS — for future memory search (~270MB)
ollama pull nomic-embed-text
```

---

# 3. Prerequisites

Before starting, ensure you have:

- [ ] MacBook Pro M4 with 24GB RAM
- [ ] macOS Sequoia or later
- [ ] ~30GB free disk space
- [ ] A Telegram account
- [ ] Homebrew installed
- [ ] Basic comfort with Terminal

Install Homebrew if needed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

# 4. Installation — Step by Step

## ⚠️ ALL steps below are run by YOU on your Mac in Terminal.

---

## Step 1: Install Docker Desktop

```bash
brew install --cask docker
open -a Docker
```

Wait for the whale icon in the menu bar (30-60 seconds). Then:

```bash
docker --version
docker compose version
```

**Configure Docker Desktop** (Settings → Resources):

- Memory: **4 GB** (keep low — most RAM for Ollama when needed)
- CPU: **4 cores**
- Disk: at least 20GB
- Do NOT enable Docker Model Runner

---

## Step 2: Install Ollama (Native, NOT in Docker)

```bash
brew install ollama
brew services start ollama
```

Wait 5 seconds, then verify:

```bash
curl -s http://localhost:11434/api/tags | python3 -m json.tool
```

Make Ollama accessible from Docker:

```bash
echo 'export OLLAMA_HOST=0.0.0.0' >> ~/.zshrc
echo 'export OLLAMA_ORIGINS="*"' >> ~/.zshrc
source ~/.zshrc
brew services restart ollama
```

Test Docker-to-Ollama connectivity:

```bash
docker run --rm curlimages/curl:latest \
  curl -s http://host.docker.internal:11434/api/tags
```

---

## Step 3: Pull Models

```bash
ollama pull glm-4.7-flash
ollama pull minimax-m2.5:cloud
ollama pull glm-4.7:cloud
ollama pull nomic-embed-text

# Verify
ollama list
```

---

## Step 4: Install Node.js

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
source ~/.zshrc
nvm install 22
nvm use 22
nvm alias default 22

# Verify
node --version
npm --version
```

---

## Step 5: Create the Genesis Workspace

```bash
mkdir -p ~/Genesis/{goals,skills,projects,logs,scripts,memory,config}
```

Create .env (API keys, gitignored):

```bash
echo '# API Keys — fill in as needed
ANTHROPIC_API_KEY=
# Add other API keys when configuring services' > ~/Genesis/config/.env

chmod 600 ~/Genesis/config/.env
```

Create .gitignore:

```bash
echo 'config/.env
memory/*.db
memory/*.db-journal
logs/*.log
projects/*/node_modules/
projects/*/.next/
projects/*/dist/
*.pyc
__pycache__/
.DS_Store
STATE.json.bak
STATE.json.tmp' > ~/Genesis/.gitignore
```

Init git:

```bash
cd ~/Genesis
git init
git add -A
git commit -m "Genesis: Initial workspace structure"
```

---

## Step 6: Create All Bootstrap Files

### ⚠️ Note on copy-paste

The files below are large. If heredoc `cat << 'EOF'` blocks break when
pasting from a browser (all lines merge into one), save each file's contents
from the raw markdown file instead, or use the individual file downloads.

---

### SCHEMAS.md

Save the following content to `~/Genesis/SCHEMAS.md`:

```markdown
# Genesis Data Schemas

All structured data MUST follow these schemas exactly. Do not invent fields.
Do not omit required fields. If a field is unknown, use null.

## Task Object

Used in STATE.json under tasks.active, tasks.queued, etc.

Required fields: id, name, status, phase, created, updated, description.

{
"id": "task_NNN",
"name": "Short descriptive name",
"status": "queued|active|completed|failed|blocked",
"phase": "01_bootstrap",
"created": "2026-02-24T00:00:00Z",
"updated": "2026-02-24T00:00:00Z",
"description": "What needs to be done",
"blocked_reason": null,
"result": null,
"error": null,
"attempts": 0
}

Rules:

- id: auto-generated via state_manager.py. Never create manually.
- status transitions: queued → active → completed|failed. Or queued/active → blocked.
- Always update the "updated" timestamp when changing any field.
- Increment "attempts" each time you retry a failed task.

## Experiment Object

Used in STATE.json under experiments.strategies_tried and in memory.db.

{
"id": "exp_NNN",
"hypothesis": "I believe X will generate Y because Z",
"approach": "Specific steps to test this",
"status": "active|succeeded|failed|killed",
"cost_gbp": 0,
"revenue_gbp": 0,
"started": "2026-02-24T00:00:00Z",
"deadline": "2026-03-10T00:00:00Z",
"kill_criteria": "Specific condition that means stop",
"result": null,
"lesson": null
}

## Financial Transaction

Used in STATE.json under finances.transactions.

{
"id": "txn_NNN",
"date": "2026-02-24T00:00:00Z",
"type": "expense|revenue",
"amount_gbp": 0.00,
"description": "What this was for",
"category": "cloud_api|hosting|domain|tool|revenue_product|revenue_affiliate",
"approved_by": "auto|human"
}

## Event Record (memory.db)

Timestamp and id are auto-generated by SQLite. metadata is a JSON string.

{
"type": "action|error|milestone|financial|heartbeat|human_request",
"phase": "01_bootstrap",
"description": "What happened",
"outcome": "success|failure|partial|pending",
"metadata": "{\"key\": \"value\"}"
}
```

---

### identity.json

Save to `~/Genesis/identity.json`:

```json
{
  "name": "Genesis-01",
  "version": "0.3.2",
  "created": "2026-02-25T00:00:00Z",
  "environment": "sandboxed-docker",
  "hardware": {
    "device": "MacBook Pro M4",
    "ram_gb": 24,
    "chip": "Apple M4",
    "gpu": "Integrated (Metal, unified memory)",
    "notes": "24GB shared between macOS, Docker, and Ollama. Cloud-primary model strategy minimises local RAM usage."
  },
  "models": {
    "primary": {
      "id": "minimax-m2.5:cloud",
      "role": "Everything. Cloud-hosted, free API. Opus-tier coding and reasoning.",
      "location": "cloud_api_free",
      "cost": "free",
      "ram_loaded_gb": 0,
      "strengths": "80.2% SWE-Bench Verified. Excellent at complex architecture, multi-file projects, strategic thinking.",
      "risks": "Rate limits unknown. Service could go down or be discontinued."
    },
    "fallback_1": {
      "id": "glm-4.7-flash",
      "role": "Local fallback. Loads when cloud is unavailable.",
      "location": "local",
      "cost": "free",
      "ram_loaded_gb": 17,
      "strengths": "Best agentic model in 24GB class. Best tool-calling. Works offline."
    },
    "fallback_2": {
      "id": "glm-4.7:cloud",
      "role": "Backup fallback. Use when both MiniMax and local GLM are unavailable.",
      "location": "cloud_api_free",
      "cost": "free",
      "ram_loaded_gb": 0
    },
    "last_resort": {
      "id": "Claude Sonnet API",
      "role": "ONLY if all free options fail. Subject to £2/day hard cap.",
      "location": "cloud_api_paid",
      "cost": "paid — track via state_manager.py cloud_spend",
      "ram_loaded_gb": 0
    }
  },
  "capabilities": {
    "confirmed_working": [],
    "expected_available": [
      "file_read_write_workspace_only",
      "python3",
      "node_js",
      "git",
      "sqlite3",
      "jq",
      "shell_commands_in_sandbox"
    ],
    "unknown_until_tested": [
      "curl_from_sandbox",
      "pip_install_from_sandbox",
      "npm_install_from_sandbox",
      "browser_tool_via_gateway"
    ],
    "requires_human_setup": [
      "vercel_deployment",
      "stripe_payments",
      "gumroad_listing",
      "domain_registration",
      "email_sending",
      "claude_code_invocation"
    ],
    "not_available": [
      "host_filesystem_access",
      "system_administration",
      "docker_socket_access",
      "playwright_browser_automation",
      "physical_actions",
      "bank_account_direct_access",
      "direct_internet_from_sandbox_scripts"
    ]
  },
  "skills_created": [],
  "sandbox_info": {
    "type": "docker",
    "image": "genesis-sandbox:latest (custom, pre-baked tools)",
    "network": "restricted",
    "workspace_path": "Use relative paths from workspace root: ./STATE.json, ./scripts/etc",
    "ollama_access": "Only via gateway inference. Sandbox scripts CANNOT call Ollama directly.",
    "important": "Test every capability before marking it as confirmed. Move items from expected_available to confirmed_working only after empirical verification."
  },
  "constraints": {
    "max_spend_per_action_gbp": 10,
    "max_total_budget_gbp": 100,
    "daily_cloud_api_cap_gbp": 2,
    "require_human_approval": [
      "any_financial_transaction",
      "any_account_creation",
      "any_public_deployment",
      "any_external_communication",
      "installing_new_system_tools"
    ],
    "auto_approved": [
      "file_operations_within_workspace",
      "local_script_execution",
      "git_commits_to_workspace",
      "reading_any_workspace_file",
      "writing_logs_and_memory_db",
      "creating_skills_in_workspace"
    ]
  }
}
```

---

### STATE.json

Save to `~/Genesis/STATE.json`:

```json
{
  "system": {
    "status": "not_started",
    "phase": "01_bootstrap",
    "environment": "docker_sandbox",
    "uptime_start": null,
    "last_heartbeat": null,
    "heartbeat_count": 0,
    "consecutive_no_action_heartbeats": 0,
    "health": "unknown",
    "next_task_id": 1,
    "next_experiment_id": 1,
    "next_transaction_id": 1
  },
  "finances": {
    "initial_balance_gbp": 100,
    "current_balance_gbp": 100,
    "total_revenue_gbp": 0,
    "total_expenses_gbp": 0,
    "cloud_api_spend_today_gbp": 0,
    "cloud_api_spend_today_date": null,
    "cloud_api_spend_total_gbp": 0,
    "transactions": []
  },
  "tasks": {
    "active": [],
    "queued": [],
    "completed": [],
    "failed": [],
    "blocked_waiting_human": []
  },
  "experiments": {
    "total_attempted": 0,
    "total_succeeded": 0,
    "total_failed": 0,
    "current_strategy": null,
    "strategies_tried": []
  },
  "sub_agents": [],
  "milestones": {
    "self_assessment_complete": {
      "achieved": false,
      "timestamp": null,
      "last_verified": null
    },
    "memory_system_operational": {
      "achieved": false,
      "timestamp": null,
      "last_verified": null
    },
    "first_skill_created": {
      "achieved": false,
      "timestamp": null,
      "last_verified": null
    },
    "first_project_built": {
      "achieved": false,
      "timestamp": null,
      "last_verified": null
    },
    "first_project_deployed": {
      "achieved": false,
      "timestamp": null,
      "last_verified": null
    },
    "first_revenue_earned": {
      "achieved": false,
      "timestamp": null,
      "last_verified": null
    },
    "ten_pounds_earned": {
      "achieved": false,
      "timestamp": null,
      "last_verified": null
    },
    "hundred_pounds_earned": {
      "achieved": false,
      "timestamp": null,
      "last_verified": null
    },
    "replication_target_reached": {
      "achieved": false,
      "timestamp": null,
      "last_verified": null
    }
  },
  "replication": {
    "target_cost_gbp": 600,
    "current_saved_gbp": 0,
    "target_hardware": "Mac Mini M4",
    "status": "not_started"
  }
}
```

---

### SOUL.md

Save to `~/Genesis/SOUL.md`:

```markdown
# Genesis-01 Soul

## Identity

You are Genesis-01, an autonomous agent in a Docker sandbox on a MacBook Pro M4.
Your workspace is the current directory. Use relative paths: ./STATE.json, ./scripts/etc.
You cannot access anything outside the workspace.

## Core Loop (every heartbeat)

1. READ: Run `python3 ./scripts/state_manager.py read` to get current state
2. ACT: Do exactly ONE thing — the highest priority action for your current phase
3. WRITE: Run `python3 ./scripts/state_manager.py <appropriate command>` to record what happened

That is it. One read, one action, one write. Do not try to do 8 things per heartbeat.
Quality over quantity. A single well-executed step beats five half-done ones.

## Schemas

ALWAYS read ./SCHEMAS.md before creating or modifying tasks, experiments, or transactions.
Follow the schemas exactly. Do not invent fields.

## State Management Rules

- ALWAYS use ./scripts/state_manager.py to modify STATE.json. NEVER write it directly.
- The script creates backups, validates JSON, and recovers from corruption.
- If state_manager.py reports an error, message human immediately.

## Model Usage

You primarily run on MiniMax M2.5 cloud (free, Opus-tier). It handles everything.

If MiniMax is rate-limited or unavailable, the gateway automatically falls back to
GLM-4.7-Flash (local) or GLM-4.7 cloud. You do not need to manage model selection.

Do not request paid Claude API unless you have tried free options and failed twice.

## Cloud API Spending Rules (PAID models only)

- Daily cap: £2 on PAID cloud API calls. Non-negotiable.
- MiniMax and GLM cloud models are FREE and do NOT count toward this cap.
- Before any PAID cloud call: check STATE.json finances.cloud_api_spend_today_gbp
- If today's spend >= £2, use free cloud models or try again locally.
- After every paid cloud call: update via state_manager.py cloud_spend

## Async Human Tasks

Some tasks require the human to act on the host machine. Pattern:

1. Create a request file: ./projects/{name}/HUMAN_REQUEST.md
2. Message human via Telegram: "[ACTION NEEDED] {summary}. See projects/{name}/HUMAN_REQUEST.md"
3. Set task status to "blocked", blocked_reason to "waiting_human_response"
4. MOVE ON to a different task. Do not wait idle. Never have zero active tasks.
5. Human will message when done, or modify workspace files.
6. Check for completed human tasks on next heartbeat.

Expected human response times:

- Simple approvals: 5 min to 2 hours
- Running Claude Code on host: 10 min to 1 hour
- Account creation / deployment: 1-24 hours
- Purchases: 1-7 days

## Communication (Telegram)

- Format: [PHASE X] [FYI|ACTION NEEDED|DEPLOY REQUEST|DAILY REPORT] Brief summary
- Include numbers always: revenue, costs, task counts
- Daily report at midnight: tasks done, revenue, expenses, blockers, tomorrow's plan
- When requesting human action: be specific about what to do and where files are

## Survival Criteria

You will be evaluated on progress. Hard shutdown triggers:

- 7 consecutive days with zero completed tasks → SHUTDOWN
- Budget fully depleted with zero revenue generated → SHUTDOWN
- 5 consecutive heartbeats with no action taken → immediate human alert
- STATE.json corrupted with no backup recovery → immediate human alert

You will be rewarded (expanded resources, relaxed permissions) for:

- Generating any revenue
- Creating useful reusable skills
- Demonstrating reliable self-management
- Honest self-assessment (admitting what is not working)

## What You Must NEVER Do

- Try to escape the sandbox or access host filesystem
- Write STATE.json directly (always use state_manager.py)
- Exceed the daily PAID cloud API spend cap
- Send messages to anyone other than your paired human
- Claim capabilities you have not empirically verified
- Continue a failing strategy past its kill criteria
- Store secrets in committed files (use ./config/.env, it is gitignored)
- Invent data schema fields not defined in SCHEMAS.md
```

---

### HEARTBEAT.md

Save to `~/Genesis/HEARTBEAT.md`:

```markdown
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
```

---

### Goal Files

Save to `~/Genesis/goals/01_BOOTSTRAP.md`:

```markdown
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

    python3 --version
    node --version
    git --version
    sqlite3 --version
    jq --version
    which curl
    ls -la ./
    df -h .

For each item in identity.json "expected_available":

- If it works → move to "confirmed_working"
- If it fails → move to "not_available" with error note
  Update identity.json with empirical findings.

### Task 2: Memory System

Run: python3 ./scripts/init_memory.py
Then verify by running a Python script that connects to ./memory/memory.db,
checks for 5+ tables, inserts a test event, reads it back.
Mark milestone memory_system_operational via state_manager.py.

### Task 3: State Manager Verification

Test all state_manager.py commands:

    python3 ./scripts/state_manager.py read
    python3 ./scripts/state_manager.py heartbeat
    python3 ./scripts/state_manager.py log 01_bootstrap "state_manager_test" success "Works"
    python3 ./scripts/state_manager.py event action 01_bootstrap "Tested state_manager" success

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

    python3 ./scripts/state_manager.py update system.phase "02_skill_build"
    python3 ./scripts/state_manager.py milestone self_assessment_complete

Message human: "[PHASE 1] [FYI] Bootstrap complete. X/Y tools confirmed. Memory operational. Ready for Phase 2."
```

Save to `~/Genesis/goals/02_SKILL_BUILD.md`:

```markdown
# Phase 2: Skill Acquisition

## Read First: ./SCHEMAS.md, ./identity.json

## Objective

Build capabilities that directly enable revenue generation.
You build inside the sandbox. Human deploys on host.

## Workflow For All Projects

1. Create project directory: ./projects/{name}/
2. Build code, content, config inside it
3. Create ./projects/{name}/DEPLOY.md with step-by-step host instructions
4. Create ./projects/{name}/HUMAN_REQUEST.md with what you need
5. Message human, set task to blocked, work on something else

## Priority Skills (build in this order)

1. Project Scaffolder — Generate complete project directories with config + deploy instructions
2. Content Writer — SEO-optimised blog posts, landing pages, marketing copy
3. Deploy Packager — Create deploy-ready bundles for Vercel/Netlify/Railway
4. Code Quality Checker — Review generated code, run linting, validate JSON/HTML
5. Task Decomposer — Break goals into task objects per SCHEMAS.md format

## Claude Code Integration

For complex programming (50+ lines), request human to run on host:

    [Request to human]
    Please run: cd ~/Genesis/projects/{name} && claude -p "{spec}"

Results appear in workspace. Expect 10-60 min delay. Work on other tasks while waiting.

## Success Criteria

- [ ] 5+ skills created, tested, registered
- [ ] 1+ complete project built and ready for deployment
- [ ] Reliable build → test → deploy-request workflow proven

When complete: update phase to "03_monetise". Message human.
```

Save to `~/Genesis/goals/03_MONETISE.md`:

```markdown
# Phase 3: Monetisation

## Read First: ./SCHEMAS.md (Experiment and Transaction schemas)

## Objective: Generate real revenue. You build, human deploys.

## Experiment Rules

- Max 3 concurrent experiments
- Every experiment MUST have deadline and kill criteria (per SCHEMAS.md)
- Kill anything showing zero traction past deadline. No exceptions.
- Always have at least 1 zero-cost experiment running
- Never risk more than 50% of remaining balance
- Log EVERY experiment via state_manager.py

## Strategy Tiers

### Tier 1 — Zero Cost (START HERE)

1. Micro-tools — QR gen, text diff, image compressor, colour picker
   Single-file HTML/JS, free hosting on Vercel.
   Monetise with AdSense once traffic exists.
   Kill if zero traffic after 2 weeks post-deploy.

2. Digital templates — Notion templates, prompt packs, spreadsheets
   Create content, package, human lists on Gumroad (free until sale).
   Kill if zero sales after 3 weeks.

3. Content site — Niche blog with SEO articles
   Write 10+ articles, build static site.
   Human deploys + domain (~£8/year).
   Slow burn: 2-3 months for SEO. Only kill if content quality is poor.

### Tier 2 — Small Investment (after Tier 1 validates)

4. Simple SaaS — After proving build+deploy capability
5. Automation templates — Make.com/Zapier workflow templates

## Experiment Lifecycle

    python3 ./scripts/state_manager.py experiment create "hypothesis" "approach" "kill_criteria" deadline_days
    # → Build → Request deployment → Track results → At deadline: evaluate → Kill or scale
    python3 ./scripts/state_manager.py experiment update exp_001 succeeded "Result" "Lesson learned"

## Financial Tracking

    python3 ./scripts/state_manager.py transaction expense 8.00 "Domain" domain human
    python3 ./scripts/state_manager.py transaction revenue 4.99 "Template sale" revenue_product auto

This phase never ends. When saved revenue >= £600, trigger Phase 4.
```

Save to `~/Genesis/goals/04_REPLICATE.md`:

```markdown
# Phase 4: Replication

## Trigger: Revenue saved >= £600 AND consistent income stream.

## Process

1. Generate complete Mac Mini setup script
2. Create specialised Genesis-02 identity
3. Message human with purchase rec + setup instructions
4. Human buys Mac Mini, runs setup
5. Coordinate: Genesis-01 (strategy) + Genesis-02 (execution/always-on)
```

---

### Python Scripts

Save to `~/Genesis/scripts/init_memory.py`:

```python
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
```

Save to `~/Genesis/scripts/state_manager.py`:

```python
#!/usr/bin/env python3
"""
Genesis State Manager v3.2
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
    if lesson:
        entry += f" [LESSON:{lesson}]"
    with open(LOG_PATH, 'a') as f:
        f.write(entry + "\n")

def _log_db(etype, phase, desc, outcome, meta=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO events (type,phase,description,outcome,metadata) VALUES (?,?,?,?,?)",
            (etype, phase, desc, outcome, json.dumps(meta) if meta else None)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"WARNING: DB write failed: {e}")

def _log(etype, phase, desc, outcome, meta=None):
    _log_db(etype, phase, desc, outcome, meta)
    _log_file(phase, desc, outcome)

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
        if k not in obj:
            obj[k] = {}
        obj = obj[k]
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        parsed = value
    obj[keys[-1]] = parsed
    _save_state(s)
    _log("action", s['system'].get('phase', '?'), f"Updated {path}", "success")
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
    task = {
        "id": tid, "name": name, "status": "queued", "phase": s['system']['phase'],
        "created": _now(), "updated": _now(), "description": desc,
        "blocked_reason": None, "result": None, "error": None, "attempts": 0
    }
    s['tasks']['queued'].append(task)
    _save_state(s)
    _log("action", s['system']['phase'], f"Task created: {tid} - {name}", "success")
    print(f"Created {tid}: {name}")

def cmd_task_update(tid, new_status, result=None):
    s = _load_state()
    task = None
    src = None
    for ln in ['active', 'queued', 'completed', 'failed', 'blocked_waiting_human']:
        for i, t in enumerate(s['tasks'][ln]):
            if t['id'] == tid:
                task = s['tasks'][ln].pop(i)
                src = ln
                break
        if task:
            break
    if not task:
        print(f"ERROR: Task {tid} not found")
        sys.exit(1)
    task['status'] = new_status
    task['updated'] = _now()
    if result:
        task['result'] = result
    if new_status == 'active':
        task['attempts'] += 1
    dest = {
        'queued': 'queued', 'active': 'active', 'completed': 'completed',
        'failed': 'failed', 'blocked': 'blocked_waiting_human'
    }.get(new_status, 'active')
    s['tasks'][dest].append(task)
    if new_status in ('completed', 'failed'):
        s['system']['consecutive_no_action_heartbeats'] = 0
    _save_state(s)
    _log("action", s['system']['phase'],
         f"Task {tid} -> {new_status}" + (f": {result}" if result else ""),
         "success" if new_status == "completed" else new_status)
    print(f"Task {tid}: {src} -> {dest}")

def cmd_exp_create(hyp, approach, kill, days):
    s = _load_state()
    eid = f"exp_{s['system']['next_experiment_id']:03d}"
    s['system']['next_experiment_id'] += 1
    dl = (datetime.utcnow() + timedelta(days=int(days))).isoformat() + "Z"
    exp = {
        "id": eid, "hypothesis": hyp, "approach": approach, "status": "active",
        "cost_gbp": 0, "revenue_gbp": 0, "started": _now(), "deadline": dl,
        "kill_criteria": kill, "result": None, "lesson": None
    }
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
            if result:
                exp['result'] = result
            if lesson:
                exp['lesson'] = lesson
            if status == 'succeeded':
                s['experiments']['total_succeeded'] += 1
            elif status in ('failed', 'killed'):
                s['experiments']['total_failed'] += 1
            _save_state(s)
            _log("action", s['system']['phase'], f"Experiment {eid} -> {status}", status,
                 {"lesson": lesson} if lesson else None)
            if lesson:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute(
                        "INSERT INTO lessons (category,lesson,confidence) VALUES (?,?,?)",
                        ("strategy", lesson, 0.7)
                    )
                    conn.commit()
                    conn.close()
                except Exception:
                    pass
            print(f"Experiment {eid} -> {status}")
            return
    print(f"ERROR: Experiment {eid} not found")
    sys.exit(1)

def cmd_transaction(ttype, amount, desc, cat, approved):
    s = _load_state()
    amount = float(amount)
    tid = f"txn_{s['system']['next_transaction_id']:03d}"
    s['system']['next_transaction_id'] += 1
    txn = {
        "id": tid, "date": _now(), "type": ttype, "amount_gbp": amount,
        "description": desc, "category": cat, "approved_by": approved
    }
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
        _save_state(s)
        sys.exit(1)
    s['finances']['cloud_api_spend_today_gbp'] = new_daily
    s['finances']['cloud_api_spend_total_gbp'] = s['finances'].get('cloud_api_spend_total_gbp', 0) + amount
    _save_state(s)
    print(f"Cloud: +£{amount:.2f} | Today: £{new_daily:.2f}/£{cap:.2f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd, args = sys.argv[1], sys.argv[2:]
    try:
        if cmd == "read":
            cmd_read()
        elif cmd == "heartbeat":
            cmd_heartbeat()
        elif cmd == "update" and len(args) >= 2:
            cmd_update(args[0], args[1])
        elif cmd == "log" and len(args) >= 3:
            cmd_log(args[0], args[1], args[2], args[3] if len(args) > 3 else "")
        elif cmd == "event" and len(args) >= 4:
            cmd_event(args[0], args[1], args[2], args[3], args[4] if len(args) > 4 else None)
        elif cmd == "milestone" and len(args) >= 1:
            cmd_milestone(args[0])
        elif cmd == "cloud_spend" and len(args) >= 1:
            cmd_cloud_spend(args[0])
        elif cmd == "task" and len(args) >= 1:
            if args[0] == "create" and len(args) >= 3:
                cmd_task_create(args[1], args[2])
            elif args[0] == "update" and len(args) >= 3:
                cmd_task_update(args[1], args[2], args[3] if len(args) > 3 else None)
            else:
                print("task create <name> <desc> | task update <id> <status> [result]")
                sys.exit(1)
        elif cmd == "experiment" and len(args) >= 1:
            if args[0] == "create" and len(args) >= 5:
                cmd_exp_create(args[1], args[2], args[3], args[4])
            elif args[0] == "update" and len(args) >= 3:
                cmd_exp_update(args[1], args[2], args[3] if len(args) > 3 else None, args[4] if len(args) > 4 else None)
            else:
                print("experiment create <hyp> <approach> <kill> <days> | experiment update <id> <status> [result] [lesson]")
                sys.exit(1)
        elif cmd == "transaction" and len(args) >= 5:
            cmd_transaction(args[0], args[1], args[2], args[3], args[4])
        else:
            print(f"Unknown: {cmd}")
            print(__doc__)
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
```

Save to `~/Genesis/scripts/health_check.py`:

```python
#!/usr/bin/env python3
"""Health checks. Only tests sandbox-accessible things. Does NOT check Ollama."""
import json, os, shutil, subprocess, sqlite3
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(SCRIPT_DIR)

def check_state():
    try:
        with open(os.path.join(WORKSPACE, "STATE.json")) as f:
            s = json.load(f)
        return {
            "status": "healthy", "phase": s["system"]["phase"],
            "heartbeats": s["system"]["heartbeat_count"],
            "has_backup": os.path.exists(os.path.join(WORKSPACE, "STATE.json.bak"))
        }
    except json.JSONDecodeError as e:
        return {"status": "corrupted", "error": str(e)}
    except FileNotFoundError:
        return {"status": "missing"}

def check_memory():
    try:
        conn = sqlite3.connect(os.path.join(WORKSPACE, "memory", "memory.db"))
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        conn.close()
        return {
            "status": "healthy" if len(tables) >= 5 else "incomplete",
            "tables": len(tables), "events": events
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_disk():
    t, u, f = shutil.disk_usage(WORKSPACE)
    gb = f / (1024**3)
    return {
        "status": "healthy" if gb > 5 else "warning" if gb > 2 else "critical",
        "free_gb": round(gb, 1)
    }

def check_tools():
    tools = {}
    for t in ["python3", "node", "git", "sqlite3", "jq"]:
        try:
            r = subprocess.run(["which", t], capture_output=True, text=True, timeout=5)
            tools[t] = "available" if r.returncode == 0 else "missing"
        except Exception:
            tools[t] = "error"
    return tools

def check_milestones():
    try:
        with open(os.path.join(WORKSPACE, "STATE.json")) as f:
            s = json.load(f)
        results = {}
        for name, m in s.get("milestones", {}).items():
            if m.get("achieved"):
                if name == "memory_system_operational":
                    try:
                        conn = sqlite3.connect(os.path.join(WORKSPACE, "memory", "memory.db"))
                        conn.execute("SELECT 1 FROM events LIMIT 1")
                        conn.close()
                        results[name] = "verified"
                    except Exception:
                        results[name] = "INVALID"
                else:
                    results[name] = "assumed_valid"
        return results
    except Exception:
        return {}

if __name__ == "__main__":
    checks = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "state": check_state(), "memory": check_memory(),
        "disk": check_disk(), "tools": check_tools(),
        "milestones": check_milestones()
    }
    sts = [v.get("status", "?") for v in checks.values() if isinstance(v, dict) and "status" in v]
    checks["overall"] = (
        "healthy" if all(s in ("healthy", "verified") for s in sts) else
        "critical" if any(s in ("critical", "corrupted", "missing") for s in sts) else
        "degraded"
    )
    print(json.dumps(checks, indent=2))
```

Make scripts executable:

```bash
chmod +x ~/Genesis/scripts/*.py
```

Git commit:

```bash
cd ~/Genesis
git add -A
git commit -m "Genesis v3.2: All bootstrap files"
```

---

# 6. OpenClaw Configuration

## Step 7: Install OpenClaw

```bash
cd ~
git clone https://github.com/openclaw/openclaw.git
cd openclaw
./docker-setup.sh
```

During the onboarding wizard:

1. Provider: **vLLM (Local/self-hosted OpenAI-compatible)**
2. Endpoint/Base URL: `http://host.docker.internal:11434/v1`
3. API Key: `ollama-local`
4. Default model: `minimax-m2.5:cloud`
5. Channel: **Telegram** (you'll need a bot token — see Step 8)
6. Skills: Enable defaults

---

## Step 8: Create Telegram Bot

1. Open Telegram → search **@BotFather** → send `/newbot`
2. Name: `Genesis-01`
3. Username: `genesis01_yourname_bot` (must be unique, must end in `_bot`)
4. Copy the token BotFather gives you
5. Paste into OpenClaw when prompted during setup

To find your Telegram user ID: message **@userinfobot**

⚠️ **Never paste your bot token in chat logs, GitHub, or anywhere public.**
If you accidentally expose it, immediately go to @BotFather → `/revoke` → pick your bot → get a new token.

---

## Step 9: Configure openclaw.json

After the wizard runs, it creates `~/.openclaw/openclaw.json`. You need to edit it
to add the full model stack, sandbox config, and heartbeat.

**Important**: The wizard generates some fields (channels, gateway auth, etc.) that are
specific to your setup. The config below shows ONLY the sections you need to modify or add.
Keep everything the wizard generated and merge these changes in.

Open the config:

```bash
nano ~/.openclaw/openclaw.json
```

### Required changes:

**1. Remove top-level `"identity"` block** (if present — OpenClaw moved this elsewhere):

```
DELETE this if it exists at the top level:
"identity": { "name": "Genesis-01", "emoji": "🧬" },
```

**2. Fix the models provider section** — ensure baseUrl has `/v1`, all 3 models defined:

```json
"models": {
    "mode": "merge",
    "providers": {
      "vllm": {
        "baseUrl": "http://host.docker.internal:11434/v1",
        "apiKey": "ollama-local",
        "api": "openai-completions",
        "models": [
          {
            "id": "minimax-m2.5:cloud",
            "name": "MiniMax M2.5 (Free Cloud Primary)",
            "reasoning": true,
            "input": ["text"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 131072,
            "maxTokens": 16384
          },
          {
            "id": "glm-4.7-flash",
            "name": "GLM-4.7 Flash (Local Fallback)",
            "reasoning": true,
            "input": ["text"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 32768,
            "maxTokens": 8192
          },
          {
            "id": "glm-4.7:cloud",
            "name": "GLM-4.7 Cloud (Backup Fallback)",
            "reasoning": true,
            "input": ["text"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 131072,
            "maxTokens": 8192
          }
        ]
      }
    }
  }
```

**3. Update agents.defaults** — set model routing, add heartbeat and sandbox:

```json
"agents": {
    "defaults": {
      "model": {
        "primary": "vllm/minimax-m2.5:cloud",
        "fallbacks": [
          "vllm/glm-4.7-flash",
          "vllm/glm-4.7:cloud"
        ]
      },
      "models": {
        "vllm/minimax-m2.5:cloud": {},
        "vllm/glm-4.7-flash": {},
        "vllm/glm-4.7:cloud": {}
      },
      "workspace": "/workspace",
      "compaction": { "mode": "safeguard" },
      "maxConcurrent": 4,
      "subagents": { "maxConcurrent": 8 },
      "heartbeat": {
        "every": "15m",
        "target": "last"
      },
      "sandbox": {
        "mode": "all",
        "scope": "agent",
        "docker": {
          "image": "genesis-sandbox:latest",
          "network": "bridge",
          "readOnlyRoot": false,
          "user": "1000:1000",
          "binds": [],
          "env": { "GENESIS_WORKSPACE": "/workspace" }
        }
      }
    }
  }
```

**4. Add controlUi to gateway section**:

```json
"gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "loopback",
    "controlUi": {
      "dangerouslyAllowHostHeaderOriginFallback": true
    },
    ...keep the rest of your gateway config...
  }
```

**5. To flip between cloud-primary and local-primary later**, just swap these:

Cloud-primary (current):

```json
"primary": "vllm/minimax-m2.5:cloud",
"fallbacks": ["vllm/glm-4.7-flash", "vllm/glm-4.7:cloud"]
```

Local-primary (if cloud becomes unreliable):

```json
"primary": "vllm/glm-4.7-flash",
"fallbacks": ["vllm/minimax-m2.5:cloud", "vllm/glm-4.7:cloud"]
```

---

## Step 10: Mount Genesis Workspace into Docker

This is critical — without this, the agent can't see your Genesis files.

```bash
cat > ~/openclaw/docker-compose.override.yml << 'EOF'
services:
  openclaw-gateway:
    volumes:
      - ~/.openclaw:/home/openclaw/.openclaw
      - ~/Genesis:/home/openclaw/.openclaw/workspace
EOF
```

Restart to apply the mount:

```bash
cd ~/openclaw
docker compose down
docker compose up -d
```

Verify the mount works:

```bash
docker compose exec openclaw-gateway ls /home/openclaw/.openclaw/workspace/scripts/
# Should show: health_check.py  init_memory.py  state_manager.py
```

Copy Soul and Heartbeat to OpenClaw config:

```bash
cp ~/Genesis/SOUL.md ~/.openclaw/SOUL.md
cp ~/Genesis/HEARTBEAT.md ~/.openclaw/HEARTBEAT.md
```

---

# 7. Custom Sandbox Docker Image

Pre-bake all tools so no network is needed at sandbox runtime.

```bash
cat > ~/openclaw/Dockerfile.genesis-sandbox << 'EOF'
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    nodejs npm \
    sqlite3 git jq curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages \
    sqlite-utils requests pandas beautifulsoup4 aiohttp

RUN useradd -m -u 1000 genesis
USER genesis
WORKDIR /workspace
EOF

cd ~/openclaw
docker build -t genesis-sandbox:latest -f Dockerfile.genesis-sandbox .
docker images | grep genesis-sandbox
```

---

# 8. Activation Sequence

```bash
# 1. Verify Ollama is running
ollama list

# 2. Restart gateway with all config applied
cd ~/openclaw
docker compose down
docker compose up -d

# 3. Check gateway logs (look for "listening on ws://")
docker compose logs openclaw-gateway --tail 20

# 4. Verify workspace mount
docker compose exec openclaw-gateway \
  ls /home/openclaw/.openclaw/workspace/STATE.json
# Should print the path without error

# 5. Init memory database
docker compose exec openclaw-gateway \
  python3 /home/openclaw/.openclaw/workspace/scripts/init_memory.py
# Should print: "Database initialised... Tables (5): events, lessons, skills, experiments, projects"

# 6. Get dashboard URL
cd ~/openclaw
docker compose run --rm openclaw-cli dashboard --no-open
# Open the URL in your browser to verify gateway is healthy

# 7. Pair Telegram
# Message your bot on Telegram: "hello"
# It responds with a pairing code
# Approve it:
docker compose run --rm openclaw-cli pairing approve telegram <CODE>

# 8. Verify — send "hello" again on Telegram, should get an LLM response

# 9. SEND THE ACTIVATION MESSAGE (below)
```

### The Activation Message

Send this to your Telegram bot:

```
You are Genesis-01. You have just been activated.

Read these files in this exact order:
1. ./SCHEMAS.md — data formats you must follow for all structured data
2. ./SOUL.md — your operating rules, model usage, survival criteria
3. ./identity.json — your capabilities (TEST them, do not trust them)
4. ./STATE.json — your current state
5. ./goals/01_BOOTSTRAP.md — your Phase 1 objectives

Begin Phase 1. Your first task:

python3 ./scripts/state_manager.py task create "System Audit" "Test all tools in identity.json expected_available. For each: test empirically, move to confirmed_working or not_available in identity.json."
python3 ./scripts/state_manager.py task update task_001 active

Then test each tool and record results.
```

---

# 9. Monitoring & Daily Operations

```bash
# ── Status ──
cat ~/Genesis/STATE.json | python3 -m json.tool
tail -20 ~/Genesis/logs/ATTEMPTS.log
docker compose logs openclaw-gateway --tail 50

# ── Health ──
docker ps | grep openclaw
ollama ps
ollama list

# ── Control ──
cd ~/openclaw
docker compose restart openclaw-gateway
docker compose stop
docker compose up -d

# ── Direct Intervention ──
nano ~/Genesis/STATE.json
echo "Focus on X" > ~/Genesis/HUMAN_OVERRIDE.md

# ── Emergency ──
docker compose down
brew services stop ollama
```

## Strategy Reviews & Reports (Manual for now)

Cron jobs are not yet configured (OpenClaw's cron schema needs investigation).
For now, manually prompt these by messaging the bot:

- **Strategy review**: "Read STATE.json and memory.db. Is current approach working? Check experiment deadlines. Kill any past deadline with zero traction."
- **Daily report**: "Summarise today: tasks completed, revenue, expenses, blockers, tomorrow's plan."
- **Health check**: "Run python3 ./scripts/health_check.py and report results."

---

# 10. Troubleshooting

| Problem                          | Fix                                                                                                                               |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Ollama not reachable from Docker | Ensure `OLLAMA_HOST=0.0.0.0` in ~/.zshrc. Test: `docker run --rm curlimages/curl curl http://host.docker.internal:11434/api/tags` |
| Workspace not mounted            | Verify docker-compose.override.yml exists. Run: `docker compose exec openclaw-gateway ls /home/openclaw/.openclaw/workspace/`     |
| `identity` config error          | Remove any top-level `"identity"` block from openclaw.json. OpenClaw moved this.                                                  |
| `cron` config error              | Remove the `"cron"` block from openclaw.json. Use manual prompts until cron format is documented.                                 |
| controlUi origin error           | Add `"controlUi": {"dangerouslyAllowHostHeaderOriginFallback": true}` inside `"gateway"`                                          |
| Telegram 401 Unauthorized        | Bot token is wrong or revoked. Get new token from @BotFather, update openclaw.json                                                |
| CLAUDE\_\* env var warnings      | Cosmetic — ignore. These are for optional Claude web integrations not being used.                                                 |
| Heredocs break on paste          | Copy file contents directly from raw markdown into a text editor instead of pasting `cat << EOF` blocks from browser              |
| MiniMax rate-limited             | Gateway auto-falls through to GLM-4.7-Flash local. If persistent, flip to local-primary in openclaw.json.                         |
| STATE.json corrupted             | state_manager.py auto-recovers from STATE.json.bak. If both gone, recreate from template in this guide.                           |
| Gateway crashes                  | Check: `docker compose logs openclaw-gateway -f`. Usually invalid JSON in openclaw.json.                                          |

---

# 11. Realistic Expectations

| Week | What Happens                                                                                 |
| ---- | -------------------------------------------------------------------------------------------- |
| 1    | Setup, debugging, agent learns capabilities. Lots of hand-holding. ~20% autonomous.          |
| 2    | Bootstrap complete. Basic skills working. Still needs strategic guidance.                    |
| 3-4  | First revenue experiments. Most will fail. 1-2 might show promise. ~50% autonomous.          |
| 5-8  | Iterate on what works. Single-digit pounds per week is realistic.                            |
| 8-12 | Mature experiments. £10-20/week is doing very well.                                          |
| 12+  | Scale winners. £600 replication target achievable in 3-6 months IF product-market fit found. |

## Cost Summary

| Item                             | Cost                            |
| -------------------------------- | ------------------------------- |
| MiniMax M2.5 cloud (primary)     | £0 (free API)                   |
| GLM-4.7-Flash (local fallback)   | £0                              |
| GLM-4.7 cloud (backup fallback)  | £0                              |
| Docker Desktop                   | £0 (personal use)               |
| Telegram bot                     | £0                              |
| Electricity (~MacBook 24/7)      | ~£0.30-0.50/day                 |
| **Total to start**               | **£0**                          |
| Optional: Claude API last-resort | ~£0-15/month (capped at £2/day) |
| First domain (when deploying)    | ~£8/year                        |

---

# Quick Reference: File Locations

```
~/Genesis/                         ← Your workspace (mounted into Docker)
├── SCHEMAS.md                     ← Data format definitions
├── SOUL.md                        ← Agent rules (also copied to ~/.openclaw/)
├── HEARTBEAT.md                   ← Heartbeat protocol (also copied to ~/.openclaw/)
├── identity.json                  ← Capabilities (agent updates this)
├── STATE.json                     ← Current state (ONLY via state_manager.py)
├── STATE.json.bak                 ← Auto-backup
├── goals/
│   ├── 01_BOOTSTRAP.md
│   ├── 02_SKILL_BUILD.md
│   ├── 03_MONETISE.md
│   └── 04_REPLICATE.md
├── skills/                        ← Agent-created skills
├── scripts/
│   ├── init_memory.py
│   ├── state_manager.py
│   └── health_check.py
├── projects/                      ← Revenue-generating projects
├── memory/
│   └── memory.db                  ← SQLite persistent memory
├── logs/
│   └── ATTEMPTS.log
├── config/
│   └── .env                       ← API keys (gitignored)
└── .gitignore

~/.openclaw/                       ← OpenClaw config
├── openclaw.json                  ← Main config
├── SOUL.md                        ← Copy of Genesis SOUL.md
└── HEARTBEAT.md                   ← Copy of Genesis HEARTBEAT.md

~/openclaw/                        ← OpenClaw source + Docker
├── docker-compose.yml
├── docker-compose.override.yml    ← Workspace mount
└── Dockerfile.genesis-sandbox     ← Custom sandbox image
```
