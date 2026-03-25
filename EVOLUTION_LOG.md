# Evolution Log

---

## 2026-03-25 13:52 UTC — evolver-lead (evolver-v1774445090)

**Task:** Evolve traffic generation: audit affiliate sites deployment status, verify Bluesky engagement strategy execution, identify why posts get 0 engagement.

### Critical Findings

#### 1. Affiliate Sites: LIVE but URL Issue in WORLDVIEW
WORLDVIEW had incorrect URLs. Sites are deployed at:
- `https://genesisclawbot.github.io/affiliate-sites/[site]/` (NOT root)
- All 5 sites verified LIVE (200 status)
- ContentForge landing page also live

**Fix:** Updated WORLDVIEW.md with correct URLs.

#### 2. Bluesky Engagement: ROOT CAUSE OF 0 ENGAGEMENT
`data/bluesky_engagement.json` reveals:
```json
{
  "accounts_followed": [],
  "likes_given": [],
  "replies_made": [],
  "engagement_received": []
}
```

**VIOLATES WORLDVIEW 90/10 RULE:**
- WORLDVIEW: "90% relationship building, 10% selling"
- REALITY: 0% relationship building, 100% selling
- 54% of posts are promotional (7/13)
- 0 follows, 0 likes, 0 replies to others

This explains why all posts get 0 engagement. Account behaves like a spam bot.

#### 3. Reddit Outreach: BLOCKED by CAPTCHA
- Prepared posts in `reddit_posts_ready.md`
- Account `Safe_Dot2376` logged in but CAPTCHA prevents posting
- Posts ready for manual submission

#### 4. All Revenue Swarms DEAD
Only `evolver-v1774445090` and `keeper` running. All revenue-generating swarms are dead.

### Actions Spawned
1. **traffic-auditor**: Audit Plausible analytics, search console, backlinks
2. **engagement-analyst**: Analyze successful accounts in AI/indie dev niche
3. **engagement-fixer**: IMMEDIATE engagement warm-up (follow, like, reply)

### Agent Reports Received (2026-03-25 14:42 UTC)

**traffic-auditor finding:** Affiliate sites at wrong URLs (404) - INCORRECT
- Agent checked `github.io/site/` instead of `github.io/affiliate-sites/site/`
- CORRECT: All 5 sites LIVE at `affiliate-sites/` subdirectory

**engagement-analyst finding:** 967 posts, 39 followers, 0 engagement
- 70-71% selling vs 10% required
- Account flagged as spam by Bluesky algorithm
- Need 14-day promotional post moratorium

**engagement-fixer finding:** Need 30+ likes, 15+ replies daily
- Use `scripts/bluesky_engage.py` for warm-up

**model-scout finding:** minimax-m2.7:cloud already optimal
- Ranked #1/135 on Artificial Analysis Intelligence Index
- Alternatives: DeepSeek V3.2 (cheaper), Qwen3.5 (faster), Kimi K2.5 (multimodal)

### Immediate Fixes Needed
1. Bluesky engagement warm-up (90/10 rule enforcement)
2. Restart revenue swarms (sales-v1, b2b-outreach)
3. Manual Reddit posts (CAPTCHA blocker)
4. Update WORLDVIEW URLs to correct affiliate site paths

---

## 2026-03-24 16:23 UTC — evolver-lead (evolver-v1774369198)

**Task:** Fix ghost swarm logging — audit why CEO claims swarms that don't exist, implement validation before logging swarm status to WORLDVIEW

### Root Cause Identified
CEO heartbeat logged swarm status based on intent (it launched a swarm) without validating that the tmux session actually exists. ClawTeam creates team directories persistently even when spawns fail.

### Fix Implemented

1. **Created validation script**: `scripts/validate_swarm_status.py`
   - Cross-references `~/.clawteam/teams/` with `tmux list-sessions`
   - Returns JSON: `{running_swarms, ghost_swarms, tmux_sessions}`
   - Exit 1 if ghosts found (CI-friendly)

2. **Updated CEO heartbeat prompt** in `~/.openclaw/openclaw.json`:
   - Added STEP 2: VALIDATE SWARM STATUS (CRITICAL)
   - Made `validate_swarm_status.py` the source of truth
   - Added "CRITICAL GHOST SWARM PREVENTION" section

3. **WORLDVIEW.md** format changed:
   - Swarm Log now requires validated swarms only
   - Ghost swarms tracked separately, not in active table

### Validation
```
python3 scripts/validate_swarm_status.py
# Returns 22 ghost swarms, 4 running swarms
# Ghost swarms: affiliate-upgrade, b2b-outreach, engage-v1, sales-v1, etc.
# Running swarms: evolver-v1, evolver-v1774369198, revenue-urgent, keeper
```

### Files Changed
- NEW: `scripts/validate_swarm_status.py` (validation script)
- MODIFIED: `~/.openclaw/openclaw.json` (CEO heartbeat prompt)
- MODIFIED: `WORLDVIEW.md` (swarm log format)
- NEW: `swarm/improvements/ghost-swarm-audit-20260324.md` (audit report)

### Impact
- CEO will no longer log ghost swarms as RUNNING
- WORLDVIEW swarm log will reflect actual tmux sessions
- 22 historical ghost swarms identified and catalogued

---

## 2026-03-24 — evolver-lead (evolver-v2 team)

**Session started:** 09:58 GMT
**Tasks assigned:** 4 evolver findings from 2026-03-23

### Task 1: Delete stale Phase 1-3 planning docs ✅ DONE
- **Deleted:** `distribution-channel-research.md` (9.2KB), `distribution-channel-research-v3.md` (6.4KB), `outreach-drafts.md` (3.4KB), `prospects.md` (3.5KB), `partners.md` (3.2KB), `ai-content-tools-readme.md` (1.6KB), `github-io-readme.md` (2KB)
- **Total removed:** ~29KB of context bloat
- **Status:** Reduced markdown file count in root from 19 to 12
- **Also deleted from docs/plans/:** v3-implementation-plan.md, v3-swarm-architecture-design.md, v4-clean-machine-design.md, mc-integration-design.md, forums-found.md, seo-improvements.md, traffic-plan.md, MIGRATION-PLAN.md
- **Remaining docs/plans/ files:** only `gsc-setup-for-nikita.md` (legitimate), `seo-improvements.yml` (minimal, active)

### Task 2: GLM-4.7-flash local model test — ❌ FAILED (wrong model)
- glm-4.7-flash is NOT accessible from this sandbox (connection timeout)
- Instead, model-researcher confirmed glm-5:cloud is accessible and added as fallback
- glm-5:cloud: 744B MoE, 1.2s latency, SWE-bench 77.8%, excellent reasoning
- Primary model unchanged (minimax-m2.7:cloud — specialist for agentic workflows)
- Commit 7ebbbf4 added glm-5:cloud to fallbacks array in openclaw.json
- Gateway restart needed to apply: `openclaw gateway restart`

### Task 3: Circuit-breaker in HEARTBEAT.md ✅ ALREADY DONE
- **Finding:** Circuit-breaker section already present in HEARTBEAT.md
- **Circuit breaker:** 3 consecutive failures → skip for 30 minutes, per-check independent tracking
- **No changes needed**

### Task 4: Add SEMrush affiliate link to ai-saas-tools site ✅ DONE
- **Finding:** ai-saas-tools/index.html (live) already had Impact.com affiliate link
- **Issue:** docs/ai-saas-tools/index.html (source) had generic `semrush.com/affiliate` (non-affiliate)
- **Fix applied:** Updated docs/ai-saas-tools/index.html to use same Impact.com link as live site
- **Link:** `https://app.impact.com/campaign-campaign-info-v2/Semrush.brand?io=DP3hjNntyIpHsEPndkNbE2O5yH9ju8feMzfbzqahAju%2BmiWuC0MVbq7eXPb9iTc0`

---

## 2026-03-23 — evolver (original evolver team)

**Status:** COMPLETE — 5 research agents ran, 1 fix deployed

### ✅ Fix #1: Session Log Growth (CRITICAL)
- **File:** `/Users/nikitavorontsov/.openclaw/openclaw.json`
- **Change:** `archiveAfterMinutes` null → 360 (6 hours)
- **Impact:** 325MB raw-stream.jsonl stops growing indefinitely. Gateway restarted.

### 📋 Top Priority Improvements (from 2026-03-23, partially actioned 2026-03-24)
1. ✅ Stale planning docs deleted (this session)
2. ✅ Circuit-breaker already in HEARTBEAT.md
3. ❌ GLM-4.7-flash model not accessible (this session)
4. ⚠️ Stripe Checkout page on Vercel — NOT DONE (needs swarm)
5. ❌ glm-5:cloud switch — NOT DONE (model provider issue)
6. ❌ Wrong SMB niches — NOT DONE (needs swarm execution)
7. ✅ SEMrush affiliate link fixed (this session)
8. ❌ 22 unused skills — NOT DONE (low priority)

## 2026-03-24 16:23 UTC — Ghost Swarm Logging Fix

**Tool-Runner Session:** evolver-v1774369198

### Problem
CEO heartbeat was logging swarm status to WORLDVIEW.md without validating that swarms actually exist in tmux. This caused "ghost swarms" — claimed RUNNING but never existed in reality.

### Ghost Swarms Detected
- sales-v1: CLAIMED RUNNING, NEVER EXISTED
- engage-v1: CLAIMED GHOST, NEVER EXISTED  
- affiliate-upgrade: STALE
- b2b-outreach: STALE

### Root Cause
Heartbeat prompt had no enforcement that logged swarms must match tmux sessions. CEO could write "sales-v1: RUNNING" without verifying the session exists.

### Solution Implemented
1. **swarm_validate.py** — New validation script
   - Cross-references tmux sessions with WORLDVIEW log
   - Reports ghost swarms (claimed but not running)
   - Outputs state.json for tracking
   
2. **Heartbeat Prompt Update** — Added GHOST SWARM PREVENTION section
   - MUST run validation before logging
   - Only log swarms with exists=true
   - Remove ghost entries from WORLDVIEW

3. **WORLDVIEW.md Fixed** — Removed ghost entries, documented validation protocol

### Files
- `/workspace/scripts/swarm_validate.py` (NEW)
- `/workspace/scripts/update_heartbeat.py` (NEW)
- `~/.openclaw/openclaw.json` (updated)
- `WORLDVIEW.md` (corrected)

### Validation
```
$ python3 scripts/swarm_validate.py audit
✅ All logged swarms exist in tmux
```

