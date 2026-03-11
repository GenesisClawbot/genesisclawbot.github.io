# AGENTS.md - Genesis-01 Workspace

## Every Session

Before doing anything else:

1. Read `CLAUDE.md` — your operating instructions
2. Read `WORLDVIEW.md` — your strategy and current phase
3. Check `swarm/scout/` — latest Scout reports
4. Check `swarm/improvements/` — latest Improvement agent changes
5. Check `swarm/state.json` — current phase and heartbeat count

## Coordination

All agent coordination happens via the filesystem:
- Workflow outputs go to `swarm/workflows/`, `swarm/research/`, `swarm/products/`, `swarm/distribution/`
- Scout writes to `swarm/scout/`
- Improvement agent writes to `swarm/improvements/`
- Workflow definitions live in `workflows/*.yml`

## Safety

- Don't exfiltrate private data
- Don't run destructive commands without thinking
- When in doubt, ask
