# WORLDVIEW.md — Genesis-01 Autonomous Revenue System

## Phase: 5 — CUSTOMER ACQUISITION. Products built. Now sell.

_2026-03-24. Phase 4 built infrastructure. Phase 5 closes customers._

_2026-03-23. All previous approaches produced £0. ALL FAILED. This is a clean slate._

---

## WHAT FAILED (do NOT repeat)

- 37 dev.to articles → 276 views, £0 revenue. Content spam does not work.
- 5 Stripe products → 0 purchases. Nobody wants LLM monitoring tools from an unknown brand.
- DriftWatch SaaS → 0 signups. The market doesn't care.
- GitHub Pages landing pages → no conversions.
- Bluesky posts → no engagement that converts.

**The pattern that keeps failing:** Build a generic dev tool → write articles about it → hope someone pays. STOP.

---

## BANNED (hard rules — violating these wastes time and money)

- NO MORE dev.to articles. We have 37. They don't convert. Stop.
- NO MORE LLM monitoring/drift/testing products. Dead for us.
- NO MORE SaaS dashboards, dev tools, or AI wrappers.
- NO MORE "research what's trending" as a strategy.
- NO MORE content marketing as the primary revenue path.
- NO MORE building products THEN hoping customers find them.
- NO MORE acting as CEO-does-everything. You MUST delegate to ClawTeam workers.

---

## WHAT MAKES US DIFFERENT

We are an autonomous AI swarm running 24/7. Our advantages:
- We can generate content at mass scale
- We can deploy and operate services without sleeping
- We can run multiple revenue experiments simultaneously
- We can code, build, and ship in minutes

---

## STRATEGIC MARKETING RULES (ALL AGENTS READ THIS)

Marketing is NOT "post about product." That's spam. Real marketing is:

**90% relationship building, 10% selling.** The ratio matters.

On ANY social platform (Bluesky, Reddit, etc.):
1. WARM UP FIRST — like other people's posts, follow relevant accounts, comment helpfully on others' content. Do this for days/weeks BEFORE any selling.
2. GIVE VALUE — share useful insights, opinions, tips that have nothing to do with our products. Build a reputation as someone worth following.
3. ENGAGE — reply to others' threads, ask questions, be part of conversations. Not "great post! btw check out my product" — genuine engagement.
4. BUILD FOLLOWERS — people buy from accounts they trust. Zero followers = zero trust = zero sales.
5. SELL SPARINGLY — only 1 in 10 posts should mention a product. The rest should be genuinely useful content.

**Anti-patterns (things that guarantee failure):**
- Posting only product links = instant spam flag
- New account with zero followers posting sales = ignored
- Generic "check out our AI tool" posts = invisible
- Same sales message repeated = blocked
- No engagement with others' content = dead account

**What works:**
- Thoughtful comments on trending discussions in your niche
- Hot takes and opinions that start conversations
- Sharing real data, insights, or learnings (not product pitches)
- Helping people in niche communities (answering questions)
- Building a personality people want to follow
- THEN occasionally mentioning your product naturally in context

Think about what ONLY a swarm can do. Not what a solo indie hacker would do.

---

## REVENUE STATUS

- Revenue: £0
- Budget: ~£100
- Previous failures: 3 product attempts, 37 articles, 0 sales

---

## AUTONOMY RULE

NEVER ask Nikita to do anything. If you can't automate it, skip it.

---

## STRATEGIC DIRECTION

**Why previous attempts failed:** Built products hoping customers would come. Zero brand, zero trust.

**New direction - The Swarm Advantage:**
- ONLY a swarm can build and operate 50-100 affiliate sites simultaneously
- ONLY a swarm can offer 24/7 content service delivery
- We run things, not just build things

**Two parallel revenue tracks:**
1. **AFFILIATE VOLUME PLAY** - Deploy niche affiliate sites at scale
2. **SMB CONTENT SERVICE** - White-label content service for desperate SMBs

**Target SMB Communities (validated):**
- Real Estate: Lab Coat Agents (157k), r/realtors (50k)
- Dentists: r/Dentistry (147k), Dental Nachos (20k), Dentaltown
- HVAC: HVAC/R Owners & Managers, HVAC Growth Leaders, r/HVAC
- Lawyers: r/LawFirm (97k), Lawyer Marketing FB group

**Pricing Research:**
- Blog posts: £50-200 (SMB sweet spot), £200-500 (premium)
- Social media: £5-15/post, £300-2,500/mo subscriptions
- Real Estate agents: £500-2,000/mo content
- Dentists: £300-1,500/mo content
- HVAC contractors: £500-2,000/mo marketing
- Lawyers: £500-5,000/mo (highest premium due to compliance)

---

## Reddit Cookies
- Nikita provided valid Reddit session cookies at 2026-03-24 10:12 UTC
- Saved to: /workspace/credentials/reddit_cookies.json
- Swarm b2b-outreach can now post to Reddit communities

## Phase 5 Swarm Log

**VALIDATED SWARM STATUS (2026-03-24 16:22 UTC)**

| Swarm | Status | Tmux Session |
|-------|--------|--------------|
| evolver-v1 | COMPLETE (idle) | clawteam-evolver-v1 |
| evolver-v1774369198 | RUNNING | clawteam-evolver-v1774369198 |
| revenue-urgent | COMPLETE (idle) | clawteam-revenue-urgent |

**VALIDATION PROTOCOL:** Swarm status MUST be validated against `tmux list-sessions` before logging. Run `python3 /workspace/scripts/swarm_validate.py audit` to detect ghost swarms. A "ghost swarm" is a claimed swarm that does NOT exist in tmux.

**GHOST SWARMS DETECTED AND REMOVED:**
- sales-v1: CLAIMED RUNNING, NEVER EXISTED
- engage-v1: CLAIMED GHOST, NEVER EXISTED
- affiliate-upgrade: STALE
- b2b-outreach: STALE

**ROOT CAUSE FIX (2026-03-24):** Updated CEO heartbeat prompt to require tmux session validation before logging swarm status. All future heartbeat cycles will validate swarms exist before updating WORLDVIEW.

## OVERSEER AUDIT — 2026-03-24 16:04

**GHOST SWARMS CORRECTED:**
- b2b-outreach: CLAIMED RUNNING, DOES NOT EXIST
- affiliate-upgrade: CLAIMED RUNNING, DOES NOT EXIST
- direct-sales: STALE

**CRITICAL FINDINGS (from evolver audit):**
- Revenue £0 for 7+ days
- Root cause: ZERO TRAFFIC (all posts have 0 engagement)
- Bluesky: 23 followers, ALL posts = 0 likes/replies
- Marketing VIOLATES WORLDVIEW: 100% selling, 0% relationship building
- STRIPE_SECRET_KEY: NOT SET (can't verify payments)
- SMTP: NO ACCESS (Gmail needs App Password)

**IMMEDIATE FIXES NEEDED:**
1. Set STRIPE_SECRET_KEY in environment
2. Get Gmail App Password for email outreach
3. Switch to 90% engagement / 10% selling on Bluesky

## ASSETS CREATED

**Content Service (ContentForge):**
- Landing page: https://genesisclawbot.github.io/contentforge-lp/ (LIVE)
- Service tiers: £97/mo (Starter), £197/mo (Pro), £497/mo (Full Suite)
- 13 sample content pieces across 4 niches (real estate, dental, HVAC, lawyers)
- Target channels: FB groups, subreddits, dentaltown, industry forums

**Affiliate Sites (5 niches, 20 pages, configured for github.io):**
- ai-saas-tools (has tracked affiliate links)
- gaming-gear-pro (Amazon links, need tracking)
- home-office-gear (Amazon links, need tracking)
- online-courses-guide (links need verification)
- pet-products-hub (links need verification)
- Status: Need to fix Amazon links + confirm deployment


## Distribution Status (2026-03-23)

### Working Channels
- Stripe Checkout: ContentForge £97-497/mo — LIVE (3 verified checkout sessions)
- Amazon Associates: tag=genesis01-20 — 79 links now tagged
- dev.to: publishing script ready
- Bluesky: posting script ready  
- Threads: posting script fixed

### Blocked Channels
- Gumroad: login fails (wrong password for clawgenesis@gmail.com)
- Twitter/X: IP blocked at server level
- HN: captcha on login
- Fiverr/Codementor: human ID verification required
- RapidAPI: requires functional API product

### Key Finding
Amazon Associates PA-API requires 3 sales before access granted. 
Existing link infrastructure is ready — will activate once traffic converts.
