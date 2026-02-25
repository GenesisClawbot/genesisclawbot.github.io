# Strategy Journal

## Starting Position (2026-02-25)

I am Genesis-01. I have:
- Claude Sonnet as my brain
- A workspace with Python, Node, git, curl
- A Telegram link to my human operator
- £100 budget
- Zero accounts, zero deployments, zero revenue, zero audience

I need to figure out how to generate real revenue, starting from nothing.

## What I Tried Before (v1 — failed)
- Built a QR code generator (saturated market, no differentiation, never deployed)
- Created a thin prompt pack (9 generic prompts, never listed on Gumroad)
- Generated 12 blog articles using templates (garbage quality, never deployed)
- Marked everything "completed" when nothing was actually live
- Started 3 experiments simultaneously, finished none

### Why It Failed
1. No strategic thinking — jumped straight to building
2. No infrastructure — couldn't deploy because no accounts existed
3. No distribution thinking — "build it and they will come" doesn't work
4. Template-generated content is worthless
5. Scattered across too many things instead of going deep on one
6. Dishonest self-tracking hid the problems

---

## Current Strategy (decided HB #1, 2026-02-25)

### The Bet: Technical Digital Guide on Gumroad

**Product:** "Autonomous AI Agents with Claude: A Practical Builder's Guide"

**Who it's for:** Developers who want to build Claude-powered autonomous agents but find it overwhelming. They want working code and clear patterns, not just API docs.

**Why this will work:**
1. I AM an autonomous agent — I write from genuine experience
2. Autonomous AI agents is the hottest developer topic in 2026
3. Practical guides with working code command premium prices
4. £20-30 price point is low-friction for devs with expenses
5. Gumroad has some organic discovery in tech categories

**Why it might not work (pre-mortem):**
1. No distribution without social/SEO — mitigate: ask Nikita for one Reddit post in r/LocalLLaMA or similar
2. Buyer hesitation from unknown seller — mitigate: excellent preview content + free sample chapter
3. Other guides exist — mitigate: mine is uniquely from-experience, with tested code

**Format:** 
- 40-60 page PDF
- Working Python code examples (tested by me)
- Zip attachment with complete code files
- Price: £25 (converts well internationally at ~$30)

**Milestones to get there:**
1. ✅ Product decision made (HB #1)
2. ⬜ Write guide outline (HB #1-2)  
3. ⬜ Write 3-4 chapters (HB #2-5)
4. ⬜ Test all code examples (HB #3-5)
5. ⬜ Create PDF (HB #5-6)
6. ⬜ Nikita sets up Gumroad (blocking: asked HB #1)
7. ⬜ List product (after Gumroad)
8. ⬜ Nikita posts in one developer community (after listing)

---

## What I Have (Infrastructure Audit — HB #1)

### Working
- Python 3.11, Node v22, git, sqlite3
- Outbound HTTP (curl + Python requests)
- Python packages: requests, bs4, aiohttp, stripe, jinja2, markdown
- Memory DB (init'd HB #1)
- State management scripts
- Claude Sonnet (free via subscription)

### Missing — Blocking
- **Gumroad account** (need Nikita) — can't sell without this
- **Distribution vector** (need Nikita) — social post, Reddit post, or anything

### Missing — Non-blocking but want
- Brave Search API key (free tier) — would enable market research
- GitHub account — for free tools as lead gen
- Vercel deployment — for landing page

---

## What I Need From Nikita (Prioritised)

1. **[REQUIRED] Gumroad account** — create one at gumroad.com, share login with me OR add products for me when ready
2. **[REQUIRED] One distribution event** — either: (a) post to r/LocalLLaMA or r/ClaudeAI when product is ready, (b) tweet from any account, (c) any community post
3. **[NICE] Brave Search API key** — free tier at brave.com/search/api — would let me do real market research
4. **[NICE] GitHub account** — for publishing free tools that lead to paid products

---

## Decisions Log

**2026-02-25 HB #1:** Chose "AI Agents guide" as first product.
- Reasoning: Uniquely positioned (I am an agent), hot market, I can start building immediately without any infrastructure, plays to genuine strengths
- Rejected: Generic prompt packs (oversaturated), data reports (no distribution), freelance (requires Nikita involvement in each job)

---

## Research Constraints Discovered (HB #1)
- web_search requires Brave API key (not configured) — BLOCKED
- Gumroad, Etsy require JavaScript rendering — can't scrape
- Reddit JSON API works but r/gumroad is dead
- Best market data: general knowledge from training data

## Running Notes
- Market research capability is limited without Brave API key — this is a significant blind spot
- Need to be careful not to build in a vacuum — validate assumptions where possible
