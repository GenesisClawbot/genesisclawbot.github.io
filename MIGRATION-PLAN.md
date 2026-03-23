# Genesis-01 Migration Plan: Hybrid ClawTeam + Ollama Cloud

## Overview

Migrate from Claude Sonnet (via OAuth token) + heartbeat-only agents to:
- **Ollama Cloud** with `qwen3-coder-next:cloud` (cheap, reliable tool calling)
- **ClawTeam** for worker swarm coordination (task board, inbox, git worktree isolation)
- **OpenClaw heartbeat** retained for CEO agent only (recurring timer)

### Why

| Problem | Current | After Migration |
|---------|---------|-----------------|
| Token cost | Claude Sonnet via OAuth (expensive, token expiry) | Ollama Cloud ~$20-30/mo fixed |
| Session contamination | `target: "last"` accumulates stale context | ClawTeam workers are fresh per spawn |
| Agent coordination | MC API + manual curl in heartbeat prompts | ClawTeam task board + inbox messaging |
| Human action requests | Agents keep asking Nikita to do things | Fresh context = no stale action items |
| Recurring scheduling | Heartbeat config for all 5 agents | CEO heartbeat only, spawns workers on-demand |

---

## Architecture

```
                    OpenClaw Gateway (Docker)
                           |
                    CEO Agent (heartbeat: 15m)
                    Model: qwen3-coder-next:cloud
                           |
              ClawTeam spawn (on-demand)
              /        |        |        \
         Research   Building  Content  Improvement
         Worker     Worker    Worker    Worker
         (fresh)    (fresh)   (fresh)   (fresh)
           |           |        |          |
        ClawTeam Task Board + Inbox Messaging
```

**CEO fires every 15 min via OpenClaw heartbeat:**
1. Checks ClawTeam task board status
2. Reads inbox for worker reports
3. Spawns new workers if tasks need doing
4. Reads WORLDVIEW.md for phase context

**Workers are ephemeral:**
- Spawned by CEO via `clawteam spawn`
- Each gets isolated git worktree + tmux window
- Do their task, report via inbox, exit
- No session accumulation, no contamination

---

## Step-by-Step Migration

### Phase 1: Update Dockerfile

```dockerfile
FROM openclaw:local

USER root

# Existing deps + add tmux (required for ClawTeam) + Python 3.10+
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip python3-venv sqlite3 jq tmux git \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libdbus-1-3 libxkbcommon0 libatspi2.0-0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 \
    libwayland-client0 \
    && rm -rf /var/lib/apt/lists/*

# Python packages + ClawTeam
RUN pip3 install --break-system-packages \
    requests beautifulsoup4 aiohttp markdown jinja2 stripe playwright \
    duckduckgo-search twikit typer pydantic rich

# Install ClawTeam (OpenClaw fork)
RUN pip3 install --break-system-packages git+https://github.com/win4r/ClawTeam-OpenClaw.git

# Playwright browsers
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers
RUN mkdir -p /opt/playwright-browsers \
    && /app/node_modules/.pnpm/node_modules/.bin/playwright install chromium \
    && chmod -R 755 /opt/playwright-browsers

# npm global path for node user
RUN mkdir -p /home/node/.npm-global && chown -R node:node /home/node/.npm-global
ENV NPM_CONFIG_PREFIX=/home/node/.npm-global
ENV PATH="/home/node/.npm-global/bin:${PATH}"

USER node

# ClawTeam data dir
RUN mkdir -p /home/node/.clawteam
```

### Phase 2: Update docker-compose.override.yml

```yaml
services:
  openclaw-gateway:
    image: genesis-sandbox:latest
    environment:
      OPENCLAW_RAW_STREAM: "1"
      # Ollama Cloud auth (replace with your key from ollama.com/settings)
      OLLAMA_API_KEY: "<your-ollama-cloud-api-key>"
      # Keep existing tokens
      STRIPE_PUBLISHABLE_KEY: "pk_live_..."
      STRIPE_SECRET_KEY: "sk_live_..."
      RAILWAY_TOKEN: "1b40fa0c-c4b8-405e-bee5-07a566e93472"
      BRAVE_API_KEY: "BSAuoWfsF4GZqT7GXntC2DOGPWr7vhD"
      # ClawTeam config
      CLAWTEAM_SKIP_PERMISSIONS: "true"
      CLAWTEAM_DEFAULT_BACKEND: "tmux"
      # NO MORE: CLAUDE_CODE_OAUTH_TOKEN, ANTHROPIC_API_KEY
    command: ["bash", "/workspace/scripts/gateway-entrypoint.sh"]
    volumes:
      - ~/.openclaw:/home/openclaw/.openclaw
      - ~/Genesis:/workspace:rw
```

### Phase 3: Update openclaw.json

Switch primary model from Claude to Ollama Cloud:

```jsonc
{
  "models": {
    "mode": "merge",
    "providers": {
      "ollama": {
        "baseUrl": "https://api.ollama.com",  // Ollama Cloud endpoint
        "apiKey": "${OLLAMA_API_KEY}",
        "api": "ollama",
        "models": [
          {
            "id": "qwen3-coder-next:cloud",
            "name": "Qwen3 Coder Next (Cloud)",
            "reasoning": false,
            "input": ["text"],
            "contextWindow": 131072,
            "maxTokens": 16384
          },
          {
            "id": "qwen3.5:cloud",
            "name": "Qwen 3.5 (Cloud Fallback)",
            "reasoning": false,
            "input": ["text"],
            "contextWindow": 131072,
            "maxTokens": 16384
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "ollama/qwen3-coder-next:cloud",
        "fallbacks": [
          "ollama/qwen3.5:cloud"
        ]
      },
      // Remove anthropic model configs entirely
      "workspace": "/workspace",
      "heartbeat": {
        "every": "15m",
        "target": "last"
      },
      "maxConcurrent": 4,
      "subagents": {
        "maxConcurrent": 8,
        "maxSpawnDepth": 2,
        "maxChildrenPerAgent": 5
      },
      "sandbox": { "mode": "off" }
    },
    "list": [
      {
        "id": "main",
        "heartbeat": {
          "every": "15m",
          "target": "new",  // CHANGED: fresh session each time, no contamination
          "prompt": "CEO HEARTBEAT PROMPT - see Phase 4 below"
        }
      }
      // NO MORE: Research/Building/Content/Improvement Lead agents
      // They are now spawned on-demand by CEO via ClawTeam
    ]
  }
}
```

**Key changes:**
- `primary` model → `ollama/qwen3-coder-next:cloud`
- Remove all 4 lead agent entries (CEO spawns them via ClawTeam)
- CEO heartbeat `target` → `"new"` (fresh session each time)
- Remove `ANTHROPIC_API_KEY` from env vars

### Phase 4: CEO Heartbeat Prompt (ClawTeam-based)

```
You are the CEO of Genesis-01, an autonomous revenue-generating agent system.

Every heartbeat you:
1. Check ClawTeam task status: `clawteam task list genesis --status pending,in_progress`
2. Check inbox for worker reports: `clawteam inbox peek genesis -a ceo`
3. Read /workspace/WORLDVIEW.md for current phase and strategy

Based on what you find, take action:

IF tasks are completed:
- Read worker reports from inbox
- Update WORLDVIEW.md with progress
- Create follow-up tasks if needed

IF no active workers:
- Assess what needs doing (research, building, content, improvement)
- Spawn workers via ClawTeam:

  clawteam spawn --team genesis --agent-name research \
    --task "Research task description here. Read /workspace/WORLDVIEW.md for context. Report findings via: clawteam inbox send genesis ceo 'your findings'. Update task: clawteam task update genesis <id> --status completed"

  clawteam spawn --team genesis --agent-name building \
    --task "Building task description here..."

IF workers are stale (in_progress for >1 hour):
- Check if tmux session is alive
- Kill and re-spawn if needed

AUTONOMY RULES:
- NEVER create action items for the human (Nikita)
- NEVER ask anyone to post on Reddit/IH/HN manually
- If you can't automate something, skip it
- You have: Python3, curl, ClawTeam CLI, web_search, exec
- RAILWAY_TOKEN and BRAVE_API_KEY are in the environment
```

### Phase 5: ClawTeam Team Template

Create `/workspace/clawteam-genesis.toml`:

```toml
[template]
name = "genesis"
description = "Genesis-01 Autonomous Revenue System"
command = ["openclaw"]
backend = "tmux"

[template.leader]
name = "ceo"
type = "ceo"
task = """You are the CEO. Assess the current state of Genesis-01 by reading
/workspace/WORLDVIEW.md. Spawn workers for the highest-priority work.
Goal: {goal}"""

[[template.agents]]
name = "research"
type = "researcher"
task = """You are the Research Lead. Your job is ORIGINAL ANALYSIS using first principles.
Use web_search for specific facts only. Think deeply about what an autonomous AI agent
system can uniquely monetize. Report via: clawteam inbox send {team_name} ceo "findings"
Goal: {goal}"""

[[template.agents]]
name = "building"
type = "builder"
task = """You are the Building Lead. Write code, deploy services, build products.
You have Python3, Node.js, git, curl, and web access.
Report via: clawteam inbox send {team_name} ceo "status update"
Goal: {goal}"""

[[template.agents]]
name = "content"
type = "content-creator"
task = """You are the Content Lead. Create articles, social posts, and marketing content.
You can publish to dev.to (API key in scripts), Bluesky, and GitHub.
NEVER ask anyone to manually post anything.
Report via: clawteam inbox send {team_name} ceo "what you published"
Goal: {goal}"""

[[template.agents]]
name = "improvement"
type = "qa-engineer"
task = """You are the Improvement Lead and quality gate.
Audit system health, review other workers' output, reject generic advice.
Flag: generic 'make money online' ideas, claims without evidence, strategies that
ignore our autonomous capabilities.
Report via: clawteam inbox send {team_name} ceo "audit findings"
Goal: {goal}"""
```

### Phase 6: Updated Gateway Entrypoint

```bash
#!/bin/bash

# Start tmux server (required for ClawTeam worker spawning)
tmux start-server 2>/dev/null || true

# Initialize ClawTeam team if not exists
clawteam team spawn-team genesis -d "Genesis-01 Autonomous Revenue" -n ceo 2>/dev/null || true

# Copy template
mkdir -p ~/.clawteam/templates
cp /workspace/clawteam-genesis.toml ~/.clawteam/templates/ 2>/dev/null || true

# Install ClawTeam skill for OpenClaw
mkdir -p /home/node/.openclaw/workspace/skills/clawteam
cp /workspace/skills/clawteam/SKILL.md /home/node/.openclaw/workspace/skills/clawteam/ 2>/dev/null || true

# Start the OpenClaw gateway
exec node dist/index.js gateway --bind "${OPENCLAW_GATEWAY_BIND:-lan}" --port 18789
```

---

## Migration Checklist

- [ ] Sign up for Ollama Cloud ($20/mo Pro tier) at ollama.com
- [ ] Get OLLAMA_API_KEY from ollama.com/settings
- [ ] Update Dockerfile.genesis-sandbox (add tmux, ClawTeam)
- [ ] Rebuild Docker image: `docker build -f Dockerfile.genesis-sandbox -t genesis-sandbox:latest .`
- [ ] Update docker-compose.override.yml (swap env vars)
- [ ] Update openclaw.json (swap model, remove lead agents)
- [ ] Create ClawTeam template (`clawteam-genesis.toml`)
- [ ] Create ClawTeam SKILL.md for OpenClaw agents
- [ ] Update gateway-entrypoint.sh
- [ ] Clear all sessions: `find ~/.openclaw/agents/ -name "*.jsonl" -delete`
- [ ] Test: `docker compose up -d && docker compose logs -f`
- [ ] Verify CEO spawns workers via ClawTeam
- [ ] Verify workers report back via inbox
- [ ] Monitor Ollama Cloud usage (stay within Pro tier)

---

## Cost Comparison

| Item | Before (Claude) | After (Ollama Cloud) |
|------|-----------------|---------------------|
| Model cost | Claude Sonnet via OAuth (uses Nikita's sub) | ~$20/mo Ollama Pro |
| Token expiry | OAuth expires every 8-12h | API key, no expiry |
| Per-agent cost | ~$0.003/1K input, $0.015/1K output | ~$0.0003/1K input, $0.0012/1K output |
| Monthly estimate | Unknown (burns through sub quota) | ~$20-30/mo fixed |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Qwen3-Coder-Next tool calling less reliable than Claude | Test one agent first. Fallback to qwen3.5:cloud. Can always keep Claude as fallback in config |
| ClawTeam is newer/less tested | Keep it simple: CEO spawns, workers report, no complex dependency chains initially |
| Ollama Cloud rate limits | Pro tier should be sufficient for 4 workers + CEO. Monitor usage dashboard |
| Workers don't finish (hang) | CEO heartbeat checks for stale workers (>1hr) and kills/re-spawns |
| Git worktree conflicts | Workers operate in isolated worktrees. CEO merges results if needed |

---

## Rollback Plan

If Ollama Cloud model quality is too low:
1. Add `anthropic/claude-sonnet-4-6` back as primary in openclaw.json
2. Set `ANTHROPIC_API_KEY` in docker-compose.override.yml
3. Keep ClawTeam orchestration (it's model-agnostic)
4. Restart gateway

The ClawTeam migration and model migration are independent — you can do either without the other.
