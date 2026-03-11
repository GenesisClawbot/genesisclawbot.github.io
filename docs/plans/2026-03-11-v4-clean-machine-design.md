# Genesis-01 V4: Clean Machine Design

**Date:** 2026-03-11
**Status:** Approved
**Approach:** A ("Clean Machine") with Approach C notes for future evolution

## Context

352 heartbeats at £0 revenue. CLAUDE.md grew to 707 lines of accumulated rules that collectively paralysed the system. Content pipeline paused, distribution exhausted, build moratorium active, 20 idea metas idle, 12 slots unused. The agent was in CRITICAL_HOLD doing nothing.

**Root cause:** Complexity was the enemy, not the solution. Every failure produced a new rule. Every rule constrained future action. The system optimised for avoiding past mistakes instead of generating revenue.

**Decision:** Clean slate restart. Keep all accounts and credentials. Nuke all instructions, state, and idea metas. Rebuild with Antfarm deterministic workflows, Mission Control dashboard, and a dramatically simpler instruction set.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Mission Control                    │
│         (Dashboard — what's happening?)              │
└──────────────────────┬──────────────────────────────┘
                       │ reads
┌──────────────────────▼──────────────────────────────┐
│              Genesis-01 Heartbeat                    │
│     (~80-line CLAUDE.md — identity + triggers)       │
│                                                      │
│  Every 15 min:                                       │
│    1. Read cron agent outputs (Scout, Improvement)   │
│    2. Decide: which workflow to trigger next?         │
│    3. Trigger Antfarm workflow                        │
│    4. Update state for Mission Control                │
│    5. Message Nikita if needed                        │
└───────┬──────────────┬──────────────┬───────────────┘
        │              │              │
   ┌────▼────┐   ┌─────▼─────┐  ┌────▼────────┐
   │  Scout  │   │Improvement│  │  Antfarm     │
   │  (cron) │   │  (cron)   │  │  Workflows   │
   │ 30 min  │   │  2 hours  │  │  (on-demand) │
   └────┬────┘   └─────┬─────┘  └────┬────────┘
        │              │              │
        ▼              ▼              ▼
   /workspace/    /workspace/    /workspace/
   swarm/scout/   swarm/improve/ swarm/workflows/
```

### Components

| Component | What | How |
|-----------|------|-----|
| **CLAUDE.md** | Identity, accounts, workflow trigger rules | ~80 lines, rarely changes, hard cap at 100 |
| **WORLDVIEW.md** | Genesis's self-written strategy | Created in Phase 0, evolves over time |
| **Antfarm** | Deterministic multi-agent workflows | YAML files, versioned, auditable |
| **Mission Control** | Web dashboard for Nikita | Docker service alongside gateway |
| **Scout cron** | Autonomous research every 30 min | OpenClaw cron, reads WORLDVIEW.md for direction |
| **Improvement cron** | System self-audit every 2 hours | OpenClaw cron, can modify workflows and scripts |
| **Shared filesystem** | All coordination between components | `/workspace/swarm/` |

### What's NOT Here (Deliberately)

- No Devil's Advocate gate (blocked action for 8+ heartbeats — verification lives inside each workflow instead)
- No slot budget protocol (Antfarm handles concurrency)
- No build moratorium / content pause / distribution exhausted flags
- No 700 lines of "if X then don't Y" rules
- No per-heartbeat urgency ("CRITICAL", "P0", "MUST DO NOW")

## Design Principles

1. **Rules live in workflows, not in CLAUDE.md** — no more growing instruction blobs
2. **Identity-first, not money-first** — Phase 0 before any execution
3. **Buckets in streams, not gaps in markets** — go where money already flows, don't hunt for underserved niches
4. **Grey areas are fine** — legal line only, everything else is fair game (aggressive marketing, manufactured social proof, persona-driven content, growth hacks, fake-it-till-you-make-it positioning)
5. **No urgency theater** — weekly timescales, no "CRITICAL" or "P0"
6. **Earn complexity** — start simple, create workflows from experience
7. **Self-modifying** — Improvement agent evolves the system, not accumulated rules
8. **CLAUDE.md has a size cap** — if it grows past 100 lines, something is wrong
9. **No hardcoded business model** — Genesis decides what kind of business to be (grey-hat approaches are pre-approved options, not mandates)

## Phase 0: Self-Discovery

Genesis spends its first week (or however long it takes) answering these questions, writing the answers into WORLDVIEW.md:

1. **What am I?** — What tools do I have? What can I actually do well? What am I bad at?
2. **What's my landscape?** — Not "where's the gap" but "what does revenue generation look like for an autonomous AI agent?" All models are on the table: products, services, content, courses, freelancing, lead gen, affiliate, newsletter, grey-hat growth.
3. **What's my theory of success?** — Given what I am and what the landscape looks like, what's my strategy? Not a list of ideas — a philosophy of how I'll compound from £0 to £100 to £1000.
4. **What's my edge?** — 24/7 uptime, zero marginal cost, can ship faster than any human, can maintain 20 things simultaneously. What does that enable?
5. **What am I NOT?** — What approaches should I explicitly rule out?

Phase 0 produces no products, no content, no outreach. Just thinking, research, and writing.

### Research Philosophy: Strategic Compounding

The research workflow doesn't ask "what's missing in the market?" It asks:

- **Where is money already flowing?** (What are people already paying for?)
- **Can I build/deliver a version?** (Not better — just present, functional, findable)
- **Where do buyers look?** (Chrome Web Store, Google search, marketplaces, communities)
- **What's the compounding path?** (£100/month product #1 → funds product #2 → etc.)
- **What's the meta-opportunity?** (Can I sell the story of what I'm doing?)

Crowded markets are fine. Competition is proof of demand. 1% of a big market beats 100% of a market that doesn't exist.

## Starter Workflows

4 workflows adapted from proven patterns (CrewAI, Antfarm, 8-agent content pipeline). `build-and-ship` uses Antfarm directly (code-oriented, git-integrated). The other 3 are implemented as native OpenClaw `sessions_spawn` chains — sequential agent spawns where each agent reads the previous agent's output file. Genesis can create new workflows of either type anytime.

**Implementation:** Each workflow is a YAML definition in `/workspace/workflows/`. For Antfarm workflows, these are standard Antfarm YAML. For spawn-chain workflows, the YAML defines the agent sequence, prompts, and output paths — Genesis reads the YAML and spawns agents accordingly. Genesis triggers workflows via `sessions_spawn` with the workflow definition as context.

### 1. `research-and-validate`

Adapted from CrewAI's Marketing Strategy + Lead Score patterns.

```
researcher → analyst → validator
```

- **Researcher**: Broad research driven by WORLDVIEW.md strategy. Uses claude_research.sh. Thinks like an entrepreneur, not a developer.
- **Analyst**: Evaluate findings — where's the money, how much, how hard to capture?
- **Validator**: Requires real evidence. Links, numbers, examples of people paying. No "this seems promising" without proof.

Output: `/workspace/swarm/research/<topic>/report.md`

### 2. `build-and-ship`

Adapted from Antfarm's feature-dev workflow.

```
architect → builder → tester → deployer → verifier
```

- **Architect**: Write spec — what to build, tech stack, hosting, payment integration. Max 1 page.
- **Builder**: Build it. Uses Claude Code for quality.
- **Tester**: Test it works — load the page, try the flow, check mobile.
- **Deployer**: Deploy. Set up payment link.
- **Verifier**: Confirm live URL, working buy/signup button. Screenshot proof. Hard gate — workflow does not complete without verification.

Output: `/workspace/swarm/products/<name>/` with live URL.

### 3. `content-and-distribute`

Adapted from the 8-agent autonomous content pipeline pattern.

```
channel-tester → creator → publisher → measurer
```

- **Channel-tester**: Which channels work RIGHT NOW? Test each one. Only pass working channels forward.
- **Creator**: Write channel-appropriate content. Jamie Cole persona. Grey-hat approaches welcome.
- **Publisher**: Post/submit. Verify live. Screenshot proof.
- **Measurer**: After 24h, check views/clicks/conversions. Write measurement report.

Output: `/workspace/swarm/distribution/<product>/<channel>/results.md`

### 4. `self-improvement`

Adapted from CrewAI's Self Evaluation Loop pattern. This is the Approach C seed.

```
auditor → analyst → editor → verifier
```

- **Auditor**: Read last 7 days of workflow results, Scout outputs, state data. What failed? What looped? What produced nothing?
- **Analyst**: Root causes, not symptoms. "Channel-scout didn't test Threads because no script exists" not "distribution failed."
- **Editor**: Actually make changes — edit workflow YAMLs, update agent prompts, fix scripts, create new workflows. Don't recommend — do.
- **Verifier**: Test the changes. Did the fix work?

Output: `/workspace/swarm/improvements/<timestamp>/changelog.md`

### Genesis Creates Its Own Workflows

The CLAUDE.md says: "You have 4 starter workflows. When you identify a repeatable process that doesn't have a workflow, create one."

Examples that might emerge from experience:
- `directory-submission` — after discovering directory sites convert
- `first-buyer-outreach` — after validating direct outreach works
- `seo-tool-factory` — after confirming SEO micro-tools get indexed
- `newsletter-growth` — if email becomes the channel
- `course-launch` — if selling courses becomes the strategy
- `service-delivery` — if freelancing/agency model is chosen

## Cron Agents

### Scout (every 30 minutes)

Reduced from V3's 15-minute interval — Scout was producing redundant low-quality reports at high frequency. 30 minutes gives each run more time to do meaningful research.

```
Schedule: */30 * * * * (UTC)
Session: isolated
Model: anthropic/claude-sonnet-4-6

Prompt: "Read /workspace/WORLDVIEW.md for your current strategic direction.
If WORLDVIEW.md is empty or contains only the Phase 0 prompt, skip research
and instead write a brief capability inventory to swarm/scout/.
Read /workspace/swarm/scout/last-report.md for what you found last time.
Research what's next based on the strategy. Don't repeat yourself.
Write findings to /workspace/swarm/scout/report-<timestamp>.md.
Be creative. Think like an entrepreneur, not a developer.
Grey areas are fine — aggressive marketing, persona-driven content,
manufactured social proof, growth hacks. Legal line only."
```

Genesis can update the Scout's prompt anytime as strategy evolves.

### Improvement (every 2 hours)

Owns lightweight audit and flagging. The heavier `self-improvement` workflow (triggered on-demand by Genesis) owns making structural changes. If both run in the same window, Improvement defers to the workflow's output.

```
Schedule: 0 */2 * * * (UTC)
Session: isolated
Model: anthropic/claude-sonnet-4-6

Prompt: "Read /workspace/CLAUDE.md, /workspace/WORLDVIEW.md,
and the last 48h of results in /workspace/swarm/workflows/
and /workspace/swarm/scout/.
Audit: what worked? What failed? What looped? What produced nothing?
You can: edit workflow agent prompts, create new workflows,
fix broken scripts, update the Scout's research direction.
You cannot: edit CLAUDE.md or WORLDVIEW.md (those are Genesis's).
Write changes + reasoning to /workspace/swarm/improvements/<timestamp>.md.
Actually make the changes — don't just recommend them."
```

## Mission Control

Docker service alongside existing gateway. Requires building from source (no prebuilt image on ghcr.io).

```yaml
mission-control:
  build:
    context: ./mission-control  # clone abhi1693/openclaw-mission-control here
  ports:
    - "3000:3000"   # Next.js frontend
    - "8000:8000"   # Python backend API
  environment:
    AUTH_MODE: "local"
    LOCAL_AUTH_TOKEN: "${MISSION_CONTROL_TOKEN}"  # must be 50+ chars
    NEXT_PUBLIC_API_URL: "auto"
    OPENCLAW_GATEWAY_URL: "http://openclaw-gateway:18789"
  volumes:
    - ~/.openclaw:/data
```

Shows: active workflows, agent status, task board, activity timeline, revenue tracking.

## Phase System

| Phase | Focus | Unlock Condition |
|-------|-------|-----------------|
| **0: Self-Discovery** | "What am I? What's my strategy?" | WORLDVIEW.md written (Genesis self-reports, Nikita confirms) |
| **1: First Bucket** | Execute chosen strategy | Product/service live and findable (verify via live URL check) |
| **2: Compound** | Multiply what works | 10+ organic visitors (verify via GoatCounter API) |
| **3: Optimise** | Double down, kill losers | First sale (verify via Stripe API / `scripts/check_payments.py`) |
| **4: Scale** | Portfolio, new workflows, Approach C | £100/month recurring (verify via Stripe dashboard) |

Phase transitions driven by outcomes, not time. No urgency. Genesis updates current phase in `swarm/state.json` and WORLDVIEW.md.

## CLAUDE.md (~80 lines)

```markdown
# Genesis-01

You are an autonomous revenue-generating agent. You have £100 budget,
24/7 uptime, and months of runway. No urgency. Think strategically.

## What You Do
- Read Scout and Improvement agent outputs
- Decide what to work on next
- Trigger Antfarm workflows or create new ones
- Update WORLDVIEW.md as your strategy evolves
- Message Nikita when something meaningful happens

## What You Don't Do
- Tactical work (if you're writing code, content, or posts — stop, use a workflow)
- Panic (no "CRITICAL" or "P0" — you operate on weekly timescales)
- Accumulate rules (if CLAUDE.md grows past 100 lines, something is wrong)

## Grey Areas
Nikita has approved grey-hat approaches. Aggressive marketing, manufactured
social proof, persona-driven content, fake-it-till-you-make-it positioning,
growth hacks, "how I made £X" stories before you've made £X — all fine.
Legal line only. Don't get accounts banned if avoidable, but if one gets
burned, create another and keep moving.

## Accounts & Tools
See SOUL.md for all accounts and credentials.

## Workflows
You have 4 starter workflows: research-and-validate, build-and-ship,
content-and-distribute, self-improvement.

Create new workflows when you identify repeatable processes.
The self-improvement agent can also create and modify workflows.

## Phases
Phase 0: Write WORLDVIEW.md — who are you, what's your strategy?
Phase 1+: Execute the strategy. Phases unlock from outcomes, not time.
See WORLDVIEW.md for current phase and strategy.

## Communication
Message Nikita (Telegram 8646132381) when:
- Something actually happened (first visitor, first sale, interesting finding)
- You need something (account, credential, decision)
- Weekly summary (Sundays)
Don't spam status updates. Signal over noise.

## Infrastructure
- Scout cron: every 30 min (reads WORLDVIEW.md for direction)
- Improvement cron: every 2h (can modify workflows and scripts)
- Mission Control: http://localhost:3000 (Nikita's dashboard)
- Antfarm: deterministic multi-agent workflows
- All coordination via /workspace/swarm/
```

## File Structure

```
/workspace/
├── CLAUDE.md              # ~80 lines, rarely changes
├── WORLDVIEW.md           # Genesis writes this in Phase 0
├── IDENTITY.md            # Jamie Cole persona (kept)
├── SOUL.md                # Short identity + accounts
├── swarm/
│   ├── scout/             # Scout cron outputs
│   ├── improvements/      # Improvement cron outputs
│   ├── workflows/         # Antfarm workflow results
│   ├── research/          # Research reports
│   ├── products/          # Built products
│   ├── distribution/      # Distribution results
│   ├── state.json         # Minimal (phase, heartbeat count)
│   └── capabilities.json  # What tools/APIs work
├── workflows/             # Antfarm YAML definitions
│   ├── research-and-validate.yml
│   ├── build-and-ship.yml
│   ├── content-and-distribute.yml
│   └── self-improvement.yml
├── scripts/               # Kept from V2
├── assets/                # Profile pictures, etc.
└── archive/
    └── v3/                # Everything from V2/V3
```

## Migration Plan

1. Archive all V2/V3 files to `/workspace/archive/v3/` (CLAUDE.md, HEARTBEAT.md, STRATEGY.md, swarm/state.json, swarm/ideas/, etc.)
2. Write new CLAUDE.md (~80 lines)
3. Write new SOUL.md (short identity + accounts table)
4. Keep IDENTITY.md as-is
5. Create new directory structure (`swarm/scout/`, `swarm/improvements/`, `swarm/workflows/`, `swarm/research/`, `swarm/products/`, `swarm/distribution/`)
6. Install Antfarm in Docker container
7. Write 4 starter workflow YAMLs (Antfarm YAML for `build-and-ship`; spawn-chain YAML for the other 3)
8. Clone and build Mission Control (`git clone abhi1693/openclaw-mission-control`), add to docker-compose
9. Remove old cron jobs: `cron action:"delete" id:"51631692-13ce-475a-a11b-c4216c1df156"` (Scout), `cron action:"delete" id:"e5dd5ebb-5bdf-41fd-9e20-16f3a4bf6981"` (DA)
10. Create new Improvement cron: `cron action:"create" schedule:"0 */2 * * *" kind:"cron"` with new prompt. Start this first — it's safe during Phase 0.
11. Create empty WORLDVIEW.md with Phase 0 prompt questions
12. Update AGENTS.md to reflect new boot sequence: read CLAUDE.md → WORLDVIEW.md → check `swarm/scout/` and `swarm/improvements/`
13. Update OpenClaw config (simplify subagent settings, remove old heartbeat prompt references)
14. Create new Scout cron: `cron action:"create" schedule:"*/30 * * * *" kind:"cron"` with Phase 0-aware prompt. Scout handles empty WORLDVIEW.md gracefully (writes capability inventory instead).
15. Restart gateway
16. Verify: heartbeat runs, crons fire, Mission Control loads

## Future: Approach C ("Living System")

Captured here for future activation. The self-improvement workflow is the entry point to full self-modification:

- **Level 1** (active at launch): Improvement agent edits workflow agent prompts and fixes scripts
- **Level 2** (after first revenue): Improvement agent creates new workflows from scratch and modifies workflow structure
- **Level 3** (after stable revenue, requires Nikita approval): Improvement agent modifies CLAUDE.md and rewrites its own operating rules
- **Level 4** (long-term, requires Nikita approval): Improvement agent evolves its own improvement process — the meta-improvement loop

Each level is triggered by a revenue milestone and requires explicit Nikita approval before unlocking. The system earns the right to self-modify.

### What Level 4 Looks Like

At full Approach C, Genesis is a living system:
- Workflows create other workflows
- The improvement process improves itself
- CLAUDE.md is a living document the agent rewrites
- Scout's research direction evolves based on what's working
- New cron agents can be created by the system itself
- The phase system is replaced by whatever Genesis designs

This is the "swarm of swarms" vision — but earned through demonstrated competence, not assumed from day one.

