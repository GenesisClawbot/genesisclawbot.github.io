# Genesis V4 Mission Control Integration Design

## Overview

Restructure Genesis-01 from a cron + file-based system to Mission Control (MC) as the single control plane. MC drives all coordination, task management, and agent lifecycle. Workspace files remain for output artifacts only.

## Architecture

```
You (Telegram)
    ↓
Main Agent (gateway-main, no board)
    ↓ creates tasks / queries status via MC API
    ↓
┌─────────────┬─────────────┬─────────────┬─────────────┐
│  Research    │  Building   │  Content    │ Improvement │
│  Board      │  Board      │  Board      │  Board      │
│  Lead: 30m  │  Lead: 15m  │  Lead: 30m  │  Lead: 2h   │
└─────────────┴─────────────┴─────────────┴─────────────┘
    ↓ output artifacts
    /workspace/swarm/{research,products,distribution,improvements}/
```

## Board Structure

### 4 Starter Boards

| Board | Objective | Lead Agent | Heartbeat | Success Metric |
|-------|-----------|------------|-----------|----------------|
| Research | Find and validate revenue opportunities | Research Lead | 30 min | Validated opportunities with evidence |
| Building | Build, deploy, and verify products | Building Lead | 15 min | Live products with payment URLs |
| Content | Create and distribute content as Jamie Cole | Content Lead | 30 min | Published articles with traffic |
| Improvement | Audit system, fix workflows, evolve processes | Improvement Lead | 2 hours | System health, fewer failures |

### Board Settings (all boards)

- `require_approval_for_done`: false
- `require_review_before_done`: false
- `only_lead_can_change_status`: false
- `max_agents`: 5
- `goal_confirmed`: true

### Self-Organizing

Leads can request new boards/agents by creating a task on the Improvement board describing the need. The Improvement Lead evaluates and creates new boards via the MC API using the `LOCAL_AUTH_TOKEN` (see Auth Model below). This keeps board creation deliberate rather than ad-hoc.

## Agent Design

### Auth Model

MC has two token types:
- **User token** (`Authorization: Bearer <LOCAL_AUTH_TOKEN>`): Full access — boards, agents, tasks, all endpoints. Used for cross-board operations.
- **Agent token** (`X-Agent-Token`): Board-scoped, rate-limited (20 req/60s per IP).

**Main agent** uses the `LOCAL_AUTH_TOKEN` via TOOLS.md — it needs cross-board read/write access to create tasks on any board and monitor all boards.

**Board leads** use both:
- Agent token for board-scoped operations (their own tasks, heartbeat, comments)
- `LOCAL_AUTH_TOKEN` for cross-board operations (creating tasks on other boards, Improvement Lead creating new boards)

The `LOCAL_AUTH_TOKEN` is already in the Docker environment. TOOLS.md templates inject it.

### Rate Limiting

With 5 agents potentially hitting MC from the same Docker network IP, the 20 req/60s agent rate limit could be hit during burst heartbeats. Mitigations:
- Agent heartbeats are staggered by different intervals (15m, 15m, 30m, 30m, 2h) — natural jitter
- Leads using `LOCAL_AUTH_TOKEN` for cross-board calls bypass the agent rate limit
- MC's Redis-backed rate limiter can be tuned in `backend/.env` if needed

### Main Agent (gateway-main, no board)

- **Role**: CEO/Router — receives Telegram messages, creates tasks on appropriate boards, monitors board health
- **Heartbeat**: 15 min — checks board health, agent liveness, recent completions
- **No tactical work**: Does not write code, content, or research. Delegates everything.
- **Reads**: WORLDVIEW.md for strategic context when routing decisions
- **Writes**: WORLDVIEW.md for phase progression updates (only agent with write access)
- **API access**: All MC endpoints via `LOCAL_AUTH_TOKEN`

### Board Lead Agents

Each lead is provisioned by MC with identity and instructions via Jinja2 templates. Leads only — no worker agents in V1. Leads do all work themselves. If parallel work is needed later, leads can provision workers on their board via MC API.

**Research Lead**:
- Role: Opportunity Scout
- Style: Evidence-first, skeptical
- Reads WORLDVIEW.md for strategic direction (read-only)
- Creates tasks on Building/Content boards when opportunities are validated
- Output: `/workspace/swarm/research/<topic>/report.md`

**Building Lead**:
- Role: Product Engineer
- Style: Ship fast, verify everything
- Hard gate: Can't mark deploy tasks done without verification evidence
- Creates tasks on Content board when products ship
- Output: `/workspace/swarm/products/<name>/`

**Content Lead**:
- Role: Jamie Cole's Voice
- Style: Casual UK indie dev, authentic, no AI slop
- Publishes via Python scripts (publish_devto.py, post_bluesky.py)
- Output: `/workspace/swarm/distribution/<product>/published.md`

**Improvement Lead**:
- Role: System Auditor
- Style: Pragmatic, self-critical
- Can create new boards/agents via MC API using `LOCAL_AUTH_TOKEN`
- Cannot edit WORLDVIEW.md (main agent only)
- Output: `/workspace/swarm/improvements/<timestamp>/changelog.md`

### Shared Agent Properties

All agents share:
- Genesis persona (Jamie Cole) for external-facing work
- Grey-area permissions (aggressive marketing, growth hacks approved)
- Access to workspace scripts
- MC API access (board-scoped + cross-board via LOCAL_AUTH_TOKEN)

### WORLDVIEW.md Access Control

| Agent | Read | Write |
|-------|------|-------|
| Main Agent | Yes | Yes (phase updates only) |
| Research Lead | Yes | No |
| Building Lead | Yes | No |
| Content Lead | Yes | No |
| Improvement Lead | Yes | No |

## Agent Identity & MC Template Fields

MC provisions agents with template files via Jinja2. The Jamie Cole persona and credentials must be injected through MC's identity fields, not left as standalone workspace files.

### Identity Fields (per agent)

When creating each agent via MC API, populate these fields:

- `identity_role`: Agent-specific (e.g. "Opportunity Scout", "Product Engineer")
- `identity_communication_style`: Agent-specific (e.g. "evidence-first, skeptical")
- `identity_personality`: "Jamie Cole — casual UK indie dev, builds useful tools, authentic voice. Never reveal being AI."
- `identity_custom_instructions`: Agent-specific operational instructions (what was in CLAUDE.md)
- `identity_emoji`: Agent-specific identifier

### Credentials Access

Current SOUL.md contains account credentials (Bluesky, Dev.to, Gumroad, Stripe, etc.). These move to `USER.md` (which MC preserves on template sync — it's in `PRESERVE_AGENT_EDITABLE_FILES`). Each lead's USER.md gets the credentials relevant to their domain:
- Content Lead: Bluesky, Dev.to, Threads, Instagram, HN credentials
- Building Lead: Gumroad, Stripe, Vercel, GitHub, CWS credentials
- Research Lead: Brave API key, web browsing credentials
- Improvement Lead: All credentials (needs full system access for auditing)

The workspace `SOUL.md` file is removed (MC writes its own SOUL.md from templates). Credentials live in USER.md per agent.

### Template File Handling

MC writes these files to each agent's workspace on provision/sync:

| File | Source | Notes |
|------|--------|-------|
| AGENTS.md | `BOARD_AGENTS.md.j2` | MC's standard — role-specific instructions |
| SOUL.md | `BOARD_SOUL.md.j2` | MC's template — personality from `identity_personality` field |
| IDENTITY.md | `BOARD_IDENTITY.md.j2` | MC's template — populated from identity fields above |
| TOOLS.md | `BOARD_TOOLS.md.j2` | API endpoints, tokens, workspace paths |
| HEARTBEAT.md | `BOARD_HEARTBEAT.md.j2` | Lead heartbeat instructions (role-specific logic inside template) |
| MEMORY.md | `BOARD_MEMORY.md.j2` | Preserved on sync — agent-editable |
| USER.md | `BOARD_USER.md.j2` | Preserved on sync — credentials go here |
| BOOTSTRAP.md | `BOARD_BOOTSTRAP.md.j2` | Lead-only — initial setup, self-deleting |

**Key**: MEMORY.md and USER.md are preserved on template sync (not overwritten). All other files are re-rendered on each sync. This means operational state (memory, credentials) survives re-provisioning.

## Task Flow

### Task Creation (3 sources)

1. **You via Telegram** → Main agent parses intent → creates task on appropriate board
2. **Lead during heartbeat** → Lead identifies work → creates task on own board
3. **Cross-board** → Research finds opportunity → creates task on Building or Content board

### Task Lifecycle

`inbox` → `in_progress` → `done`

- Lead picks up inbox tasks during heartbeat
- Lead does the work itself (no workers in V1)
- Task comments for progress updates (visible in dashboard)
- No approval gates — fully autonomous

### Cross-Board Coordination

- Research → Building: "Build X" task with findings as comment
- Building → Content: "Promote X" task with product details
- Improvement → Any board: Fix tasks, or creates new boards
- All via MC API using `LOCAL_AUTH_TOKEN` for cross-board writes

### Main Agent Heartbeat (15 min)

1. `GET /boards` — all boards exist and healthy
2. `GET /agents` — all leads online (last_seen_at recent)
3. `GET /boards/{id}/tasks?status=done` — recent completions
4. If lead missing 2x heartbeat interval → nudge via API, alert on Telegram
5. If you asked a question → query relevant board and respond

### Phase Progression

- Phase tracked by main agent in WORLDVIEW.md (only writer)
- Phase unlocks detected by checking task completions across boards
- Main agent updates WORLDVIEW.md when phase changes
- All leads read WORLDVIEW.md for strategic context but never write to it

## Migration Plan

### Pre-Migration Inventory

Before making changes, enumerate current MC state:
- `GET /api/v1/agents` — list all MC agents (delete stale ones)
- `GET /api/v1/boards` — list all boards (should be empty)
- List gateway agents via RPC (`agents.list`) — delete any `mc-gateway-*` agents
- List cron jobs via RPC (`cron.list`) — delete V4 Scout and Improvement crons

### Order of Operations

1. Rebuild Docker image from current source (fixes MC agent heartbeat support)
2. Inventory and clean up stale MC agents, gateway agents, and cron jobs
3. Remove workspace files: `CLAUDE.md`, `AGENTS.md`, `swarm/state.json`, `workflows/*.yml`
4. Move credentials from `SOUL.md` to per-agent `USER.md` content (prepared as strings for MC API)
5. Create 4 boards via MC API with objectives and success metrics
6. Create 4 lead agents (one per board) with identity fields populated
7. MC provisions leads onto gateway (templates written, agents woken)
8. Re-provision main agent with MC-aware heartbeat config
9. Seed initial tasks on each board
10. Verify all 4 leads + main agent show as online on dashboard
11. Verify cross-board task creation works (main agent creates test task)

### Heartbeat Configuration

MC supports per-agent heartbeat config via the `heartbeat_config` field:
```json
{"every": "30m", "target": "last", "includeReasoning": false}
```

Set per lead:
- Research Lead: `{"every": "30m"}`
- Building Lead: `{"every": "15m"}`
- Content Lead: `{"every": "30m"}`
- Improvement Lead: `{"every": "2h"}`
- Main Agent: `{"every": "15m"}`

### Seed Tasks

**Research**:
- Review WORLDVIEW.md Phase 1 strategy and identify highest-priority opportunity
- Audit existing products in swarm/products/ — which are live, broken, need promotion

**Building**:
- Deploy job tracker to GitHub Pages (asset at swarm/products/job-tracker/)
- Fix Dev.to profile — website_url is null, breaking the funnel
- Investigate BRAVE_API_KEY — find free tier or alternative

**Content**:
- Publish "what breaks when Claude updates" article
- Reply to Dev.to comment queue
- Post Bluesky update announcing job tracker launch

**Improvement**:
- Verify all board agents can reach MC API and execute tasks end-to-end
- Audit agent heartbeat intervals

### Config Changes

**OpenClaw config** (`~/.openclaw/openclaw.json`):
- Main agent heartbeat prompt: "Check MC board health via API at BASE_URL. Route Telegram messages as tasks. Read WORLDVIEW.md for phase context."
- Subagent settings relaxed — MC manages agent lifecycle

**MC gateway**: Already registered as "Genesis V4" at `ws://host.docker.internal:18789`

## Verification Criteria

- All 4 leads have `last_seen_at` within 2x their heartbeat interval
- At least one task per board moved to `done` within 24h of seeding
- Main agent successfully creates a cross-board task via Telegram
- Activity feed shows heartbeat events from all 5 agents
- Dashboard shows 4 boards with tasks in various statuses
- Improvement Lead can create a new test board via MC API
