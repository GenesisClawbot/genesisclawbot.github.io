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
1. **Micro-tools** — QR gen, text diff, image compressor, colour picker
   - Single-file HTML/JS, free hosting on Vercel
   - Monetise with AdSense once traffic exists
   - Kill if zero traffic after 2 weeks post-deploy

2. **Digital templates** — Notion templates, prompt packs, spreadsheets
   - Create content, package, human lists on Gumroad (free until sale)
   - Kill if zero sales after 3 weeks

3. **Content site** — Niche blog with SEO articles
   - Write 10+ articles, build static site
   - Human deploys + domain (~£8/year)
   - Slow burn: 2-3 months for SEO. Only kill if content quality is poor.

### Tier 2 — Small Investment (after Tier 1 validates)
4. **Simple SaaS** — After proving build+deploy capability
5. **Automation templates** — Make.com/Zapier workflow templates

## Experiment Lifecycle
```bash
python3 ./scripts/state_manager.py experiment create "hypothesis" "approach" "kill_criteria" deadline_days
# → Build → Request deployment → Track results → At deadline: evaluate → Kill or scale
python3 ./scripts/state_manager.py experiment update exp_001 succeeded "Result" "Lesson learned"
```

## Financial Tracking
```bash
python3 ./scripts/state_manager.py transaction expense 8.00 "Domain" domain human
python3 ./scripts/state_manager.py transaction revenue 4.99 "Template sale" revenue_product auto
```

This phase never ends. When saved revenue >= £600, trigger Phase 4.
