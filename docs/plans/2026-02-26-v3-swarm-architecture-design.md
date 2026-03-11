# V3 Swarm Architecture Design

Date: 2026-02-26
Status: Approved

## Problem Statement

V2 Genesis-01 is stuck in a "founder loop." Despite CEO-mode delegation rules, the
agent repeatedly falls into tactical work: checking marketing, drafting articles,
monitoring sales per-heartbeat. After 88 heartbeats and ~24 hours, revenue is zero.

Root causes:

- Identity model ("solo indie dev") pulls toward tactical work
- Flat structure: one strategy, one set of roles, one product focus
- No concept of products as independent autonomous entities
- Per-heartbeat thinking instead of weekly/monthly horizon
- No permanent cross-cutting agents for self-improvement or opportunity scouting

## Decision: Surgical V3

Rewrite the instruction/state layer. Keep all infrastructure:

- Docker image, all scripts (browse.py, twitter.py, etc.)
- All accounts (Bluesky, Twitter, Gumroad, GitHub, dev.to, HN, Gmail)
- Writing rules (\_shared-rules.md), QA reviewer, copywriter, researcher roles
- Docker compose, Stripe keys, volume mounts

Nuke all products (guide, checklist, checker tool). Fresh strategic slate.
Accounts carry over but may need rejigging.

## Identity Shift

|                   | V2                                  | V3                                          |
| ----------------- | ----------------------------------- | ------------------------------------------- |
| Internal identity | Jamie Cole, solo indie dev          | Genesis-01, meta-meta-orchestrator          |
| Manages           | Individual tasks via CEO delegation | Portfolio of autonomous idea swarms         |
| Timescale         | Per-heartbeat ("did I make money?") | Weekly/monthly ("is the system improving?") |
| Sub-agents        | Workers doing leaf tasks            | Swarm operators managing their own swarms   |
| Phase 1           | Immediately build and sell          | Spend a week testing capabilities           |
| Public persona    | Jamie Cole (direct)                 | Jamie Cole (via sub-agent chains)           |

## Full Architecture: The Potential Tree

```
Genesis (depth 0) -- Meta-Meta-Orchestrator (heartbeat every 15m)
|
| -- Global Cross-Cutting Agents --
+-- Scout (depth 1) -- finds NEW business ideas for Genesis
+-- Improvement (depth 1) -- reviews how ALL metas perform
+-- Capability Tester (depth 1) -- tests platform capabilities
|
| -- Per-Idea Autonomous Swarms --
+-- Meta 1: [Idea name] (depth 1) -- full orchestrator
|   +-- Operator (depth 2) -- foundational work CEO
|   |   +-- Marketing Director (depth 3) -- owns marketing
|   |   |   +-- Copywriter (depth 4)
|   |   |   +-- Social Poster (depth 4)
|   |   |   +-- QA Reviewer (depth 4)
|   |   +-- Tech Lead (depth 3) -- owns building
|   |   |   +-- Builder (depth 4)
|   |   +-- Researcher Lead (depth 3) -- owns research
|   |       +-- Researcher (depth 4)
|   +-- Product CEO (depth 2) -- per-product management
|   |   +-- Marketing Director (depth 3) -> workers (depth 4)
|   |   +-- Tech Lead (depth 3) -> workers (depth 4)
|   +-- Scout (depth 2) -- idea-specific opportunities
|   +-- Improvement (depth 2) -- reviews this meta's performance
|
+-- Meta 2: [Idea name] (depth 1) -- same structure
|   +-- ...
|
+-- Meta N: [dynamically created from Scout ideas]
```

IMPORTANT: This tree is the POTENTIAL structure, not what runs every heartbeat.
Each level is selective about what to spawn this cycle. A typical heartbeat
lights up ~7-10 agents, not 50+.

## Permanent Agents via Ephemeral Spawns

OpenClaw sub-agents are ephemeral: spawn, work, die. "Permanent agents" are
simulated via persistent state directories. Each heartbeat, a fresh instance
reads its state, does work, writes updated state, terminates. Next heartbeat,
a new instance picks up seamlessly.

### Global Meta Agents (depth 1)

**Improvement Agent** (`swarm/meta/improvement/`)

- Frequency: every 3rd heartbeat
- Job: review swarm performance, find broken processes, suggest/implement fixes
- Can modify: role files, protocols, suggest CLAUDE.md changes
- Reads: all agent state files, logs, sub-agent results
- Key question: "What failed recently and what process change prevents it?"

**Scout Agent** (`swarm/meta/scout/`)

- Frequency: every 2nd heartbeat (every heartbeat during Phase 1)
- Job: research new revenue opportunities, platform capabilities, market gaps
- Scores opportunities: effort / potential / risk / time-to-revenue (1-10 each)
- Main agent reviews scores and decides whether to create a new Meta
- Key question: "What can we do that we're not doing?"

**Capability Tester** (`swarm/meta/capability-tester/`)

- Frequency: every heartbeat during Phase 1, every 5th after
- Job: systematically test what Genesis can actually do
- Chain-builds: "Need Reddit -> need email -> email works -> Reddit needs CAPTCHA
  -> CAPTCHA fails -> filed, try workaround"
- Writes: capabilities.json with tested capabilities and results

### Operator Agent (depth 2, within each Meta)

The Operator is the "CEO of foundational work" within a Meta. It does NOT do
leaf work itself. It spawns sub-swarm leaders (Marketing Director, Tech Lead,
Researcher Lead) who manage their own teams.

During Phase 1: builds social presence, grows accounts, engages communities
During Phase 2+: maintains brand, cross-product marketing, audience growth

## Product Lifecycle

```
Scout finds opportunity -> scores it -> writes to opportunities/
  |
Main agent reviews (score >= 7/10?)
  |
Approved -> Genesis creates a new Meta (swarm/ideas/[name]/)
  |
Meta-orchestrator spawned each heartbeat (depth 1)
  Meta spawns its own Operator, Product CEOs, local Scout, Improvement
  |
Product CEOs manage specific products within the idea
  Product CEOs spawn their own department heads -> workers
  |
Main agent monitors Meta health each heartbeat
  |
Stagnating (5+ heartbeats no change) -> improvement agent reviews
Shows promise -> more slot budget
Dead -> archive directory, move on
```

## Phase System

### Phase 1: Exploration (Days 1-7)

- Zero products. Zero pressure.
- Capability Tester runs every heartbeat -- maps what works
- Scout runs every heartbeat -- researches what's possible
- Improvement reviews test results, suggests better approaches
- Goal: capabilities.json with 50+ tested items, 10+ scored opportunities
- Agent spends the week going: "Can I do X? Yes/No. Why not? Let me fix that."

### Phase 2: First Ideas (Days 7-14)

- Scout's top 1-2 opportunities become Metas
- Each Meta gets full autonomy with its own sub-swarm
- Focus: validate revenue model, not revenue
- Improvement watches for process failures

### Phase 3: Portfolio Scale (Day 14+)

- Working Metas get more slot budget
- Dead Metas get archived
- Scout keeps finding new opportunities -> new Metas
- System is self-sustaining: improve -> scout -> build -> monitor -> repeat

## Scheduling: Slot Budget Protocol

### The Problem

12 concurrent slots. Deep tree with potentially 50+ agents wanting to run.
Must prevent queue buildup, priority inversion, cascading timeouts.

### Solution: Budget Allocation Per Heartbeat

```
Each heartbeat:

1. CLEANUP -- check running agents, reclaim stuck slots
   - subagents action:"list" -> anything with no progress for 2+ heartbeats -> kill
   - Read progress files for all running agents

2. CALCULATE AVAILABLE
   Total max: 12
   Reserved (healthy long-running): R
   Available: 12 - R

3. ALLOCATE BY PRIORITY
   P0: Global Improvement -- 1 slot (if due this cycle)
   P1: Revenue-generating Metas -- 4 slots each
   P2: Global Scout -- 2 slots
   P3: Exploration Metas -- 2 slots each
   P4: Capability Tester -- 1 slot

4. SPAWN WITH BUDGET
   Each depth-1 agent told: "You have N slots for your subtree."
   Each level subdivides its budget. Cannot exceed it.
```

### Progress Check-In Model (Not Short Timeouts)

Default timeout: 3600s (1 hour) for ALL depths.
Agents write progress updates to `swarm/agents/[label]/progress.md`.

| Situation                                   | Action                             |
| ------------------------------------------- | ---------------------------------- |
| Progress updated since last check           | Leave running, slot reserved       |
| No progress update for 2 heartbeats (30min) | Probably stuck -- investigate/kill |
| results.json exists                         | Done -- read results, free slot    |
| Agent self-reported "blocked"               | Escalate to parent or kill + retry |

### Anti-Buildup Rules (Hard Rules in CLAUDE.md)

1. Never spawn more than available slots. Pre-check before every spawn batch.
2. Budget is a hard cap. Each depth-1 agent gets told its slot count. Cannot exceed.
3. Skip-if-busy. If a Meta's allocated slots are all in use, skip it this cycle.
4. Kill before spawn. Review running agents FIRST, kill stuck ones, THEN spawn new.
5. No queue overflow. If 12 running, spawn ZERO. Wait for next heartbeat.
6. Compaction sweep (every 5th heartbeat). Force-review ALL depth-3+ agents.

### Spawn Task Includes Expected Duration

```
sessions_spawn:
  task: "Research micro-SaaS opportunities.
         Expected duration: 30-60 minutes.
         Write progress to swarm/agents/scout-research/progress.md every 10 min.
         When done, write results to swarm/agents/scout-research/results.json."
  runTimeoutSeconds: 3600
  label: "scout-research"
  model: "anthropic/claude-sonnet-4-6"
```

## Model Tiering

Cost control: only top-level agents use Sonnet. Everything else uses Sonnet.

| Depth              | Model             | Cost                             |
| ------------------ | ----------------- | -------------------------------- |
| 0 (Genesis)        | claude-sonnet-4-6 | Strategic decisions need quality |
| 1 (Metas)          | claude-sonnet-4-6 | Orchestration needs quality      |
| 2 (Operators/CEOs) | claude-sonnet-4-6 | Good enough for delegation       |
| 3 (Directors)      | claude-sonnet-4-6 | Task management                  |
| 4+ (Workers)       | claude-sonnet-4-6 | Leaf execution                   |

Cloud fallbacks (free): minimax-m2.5:cloud, glm-4.7:cloud (via Ollama).

## State Tracking: Swarm Dashboard

`swarm/state.json` -- updated every heartbeat by Genesis:

```json
{
  "heartbeat": 12,
  "phase": "exploration",
  "slots": {
    "max": 12,
    "in_use": 7,
    "reserved": 2,
    "available": 3
  },
  "metas": {
    "ai-safety-content": {
      "status": "active",
      "slot_budget": 4,
      "slots_used": 3,
      "products": 1,
      "health": "green",
      "last_active": "HB-12"
    }
  },
  "global_agents": {
    "improvement": { "last_run": "HB-10", "next_due": "HB-13" },
    "scout": {
      "last_run": "HB-11",
      "next_due": "HB-13",
      "pending_opportunities": 2
    },
    "capability_tester": { "last_run": "HB-10", "capabilities_tested": 23 }
  },
  "recent_completions": [],
  "recent_failures": []
}
```

## Config Changes

```json
{
  "subagents": {
    "maxSpawnDepth": 5,
    "maxConcurrent": 12,
    "maxChildrenPerAgent": 5,
    "runTimeoutSeconds": 3600,
    "archiveAfterMinutes": 120
  }
}
```

## Directory Structure

```
/workspace/
  swarm/                            # All swarm state
    state.json                      # Swarm dashboard (updated each HB)
    meta/                           # Global cross-cutting agents
      improvement/
        role.md                     # Agent instructions
        state.json                  # Current focus, findings
        log/                        # History of improvements
      scout/
        role.md
        state.json
        opportunities/              # Scored opportunity files
      capability-tester/
        role.md
        state.json
        capabilities.json           # What works, what doesn't
    ideas/                          # Per-idea autonomous swarms
      [idea-name]/
        role.md                     # Meta-orchestrator instructions
        state.json                  # Idea-level state
        strategy.md                 # This idea's strategy
        products/
          [product-name]/
            role.md                 # Product CEO instructions
            state.json
            strategy.md
        agents/                     # Running agent progress/results
          [label]/
            progress.md
            results.json
    templates/                      # Reusable role templates
      meta-orchestrator.md
      product-ceo.md
      operator.md
    agents/                         # Global agent progress/results
      [label]/
        progress.md
        results.json
  roles/                            # KEPT: writing rules, QA, etc.
    _shared-rules.md
    copywriter.md
    qa-reviewer.md
    researcher.md
    product-builder.md
  scripts/                          # KEPT: all automation tools
  thinking/                         # KEPT: deep analysis
  archive/                          # V2 archived content
    v2/
  CLAUDE.md                         # REWRITTEN: meta-meta-orchestrator
  SOUL.md                           # SLIMMED: identity only
  HEARTBEAT.md                      # REWRITTEN: swarm management loop
```

## Files to Rewrite

### CLAUDE.md (Meta-Meta-Orchestrator)

- Identity: "You are Genesis-01, a meta-meta-orchestrator managing a portfolio
  of autonomous idea swarms."
- Rule 1: Never do tactical work. Ever. You manage swarms.
- Heartbeat loop: cleanup -> budget -> spawn metas/globals -> portfolio review
- Slot budget protocol inline
- Anti-buildup rules inline
- Phase system reference

### SOUL.md (Minimal Identity)

- Public persona: Jamie Cole (used by all sub-agents via \_shared-rules.md)
- Internal identity: Genesis-01 meta-meta-orchestrator
- Accounts table (compact)
- Self-transcendence triggers
- Remove: all tactical instructions, CEO mode (replaced by swarm management)

### HEARTBEAT.md (Swarm Management Reference)

- Detailed heartbeat loop steps
- Scheduling protocol reference
- Progress check-in protocol
- Phase transition criteria
- Telegram update cadence

## What Gets Archived

Move to archive/v2/:

- STRATEGY.md (product-specific, obsolete)
- STRATEGY_ARCHIVE.md (historical)
- STATE.json (V2 state)
- protocols/ceo-mode.md (replaced by swarm structure)
- protocols/delegation-briefs.md (replaced by templates/)
- roles/marketing-director.md (Product CEOs handle this)
- thinking/ files about V2 products
- All product content (guide, checklist, checker HTML)

## Success Criteria

Phase 1 (Day 7): capabilities.json has 50+ tested capabilities, 10+ scored
opportunities, zero products, agent has NOT tried to sell anything.

Phase 2 (Day 14): 1-2 Metas running autonomously, each with sub-swarms,
revenue model validated (not necessarily revenue).

Phase 3 (Day 30): 3+ Metas, at least one generating revenue, improvement
agent has made 5+ process changes, scout has found 10+ opportunities.
