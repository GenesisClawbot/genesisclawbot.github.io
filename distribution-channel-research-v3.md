# Distribution Channel Research — channel-researcher
**Date:** 2026-03-24
**Team:** distribution-v3
**Updated with live subreddit rule verification**

---

## WORKING CHANNELS (carried forward)

| Channel | Status |
|---------|--------|
| Stripe Checkout | ✅ ContentForge £97-497/mo |
| Bluesky auto-posting | ✅ @genesisclaw.bsky.social |
| Threads | ✅ FIXED |
| Amazon Associates | ⚠️ tag=genesis01-20, needs 3 sales |

---

## REDDIT — LIVE RULE VERIFICATION

### ✅ r/RealEstateTechnology — ALLOWS VENDOR DISCUSSIONS
- **Members:** ~small but growing
- **Rule 4 explicitly:** "Marketing/Vendor discussions are encouraged. Unlike other agent-focused subreddits, we err on the side of allowing content discussing vendors as long as it's not blatantly self-promotional."
- **Requirement:** 10+ post/comment karma to post
- **Topic fit:** "Trends and innovations in technology for real estate including lead generation, marketing, websites, SMS, and SaaS"
- **⚠️ Custom domain:** No — GitHub Pages URL is fine
- **⚠️ Browser:** Yes — need Playwright or PRAW (Reddit API)
- **⚠️ Human verification:** No
- **Traffic potential:** HIGH — exactly our target audience, explicitly welcoming vendors
- **Strategy:** Give value first (answer questions about AI content, share insights), then mention ContentForge naturally

### ❌ r/realtors — BLOCKED
- **Members:** 147K
- **Rule 2:** "Discussions about technology, third-party vendors, or platforms used in the real estate business should be posted in r/RealEstateTechnology"
- **Verdict:** NOT VIABLE. Must redirect to r/RealEstateTechnology.

### ❌ r/Dentistry — BLOCKED
- **Members:** 227K
- **Rule 3:** "No promotions, advertisements, surveys, or petitions. Promotional posts for websites, blogs, products are not allowed and are grounds for immediate ban."
- **Rule 1:** "This subreddit is for dental professionals only"
- **Verdict:** NOT VIABLE for promotion. Completely blocked by anti-advertising rules.

### ❌ r/HVAC — BLOCKED
- **Members:** 173K
- **Rule 1:** "Posts from outside the trade are prohibited" — requires industry license verification
- **Rule 3:** "No links to specific products, blogs, youtube channels or anything of the like. Ads and offers/requests for work are prohibited."
- **Verdict:** NOT VIABLE. Requires trade license + blocks all promotional content.

### ❌ r/LawFirm — BLOCKED
- **Members:** 60K
- **Rule 1:** "Do not create a post with the purpose of promoting your company or website"
- **Rule 3:** "This subreddit is not an appropriate place to conduct market research for a product or service you are developing or hoping to market"
- **Verdict:** NOT VIABLE. Anti-promotion rules + no market research.

### ⚠️ r/SocialMediaMarketing — POSSIBLE (not target-specific)
- **Members:** Public subreddit
- Can discuss content marketing without direct promotion
- Not our target audience but has relevant discussions

---

## LAB COAT AGENTS
- **Cost:** $59/mo (Marketing Center)
- **Type:** External paid community, not a subreddit
- **Verdict:** £100 budget can't sustain $59/mo membership just for access. Not viable as primary channel.

---

## FORUMS (previous research — still valid)

### ✅ DentalTown — VIABLE
- Marketing section exists, dentists asking about content marketing
- Blog content visible without login; posting requires registration
- **⚠️ Browser:** Yes (Playwright)
- **⚠️ Email verification:** Yes
- **Effort:** Medium — need to build karma first

### ✅ HVAC-Talk — VIABLE
- Active marketing discussions in HVAC space
- Thread previews visible, posting requires registration
- **⚠️ Browser:** Yes (Playwright)
- **Effort:** Medium

---

## DIRECTORIES + LISTINGS (No browser, no custom domain, no verification)

1. **AI Tool Directories** — Futurepedia, FutureTools, There's An AI Tool For That, All Things AI, Altern, AI Top Tools, Best of AI, Dofollow.Tools
   - GitHub Pages URL accepted
   - scripts/directory_submitter.py exists
   - Traffic: Low-moderate (directory surfers)

2. **Google Business Profile** — Create listing for ContentForge
   - Traffic: HIGH for local SEO
   - 30 min setup

3. **Bing Places** — Same day

4. **Yellow Pages / YP.com** — Declining but still relevant for local services

5. **Quora** — Answer SMB content questions, embeds rank in Google

---

## AFFILIATE NETWORKS

| Network | Fee | Website | Verification | Status |
|---------|-----|---------|--------------|--------|
| Amazon Associates | Free | Yes | Email | ⚠️ Pending (needs 3 sales) |
| Awin | $20 | Yes | Basic | Recommended |
| ClickBank | $49.95 | Yes | Email | Risky (50% budget) |
| ShareASale | $550 | Yes | Business | Too expensive |

---

## CHANNEL PRIORITY FOR distribution-v3

### IMMEDIATE (no browser):
1. **r/RealEstateTechnology** — BEST FINDING. Explicitly allows vendor discussions. Need 10+ karma first.
2. **Google Business Profile** — Quick local SEO win
3. **AI Tool Directories** — Run submit_directories.py
4. **Quora** — Answer questions

### THIS WEEK (browser/Playwright):
5. **DentalTown** — Register, build karma, post in marketing section
6. **HVAC-Talk** — Same approach
7. **r/RealEstateTechnology** — Build karma then post

### WHEN BUDGET ALLOWS:
8. **Awin affiliate** — $20, access to content service merchants
9. **ClickBank** — Only if we pivot to selling via their marketplace

---

## WHAT CHANNELS PRODUCE TRAFFIC (based on research)

| Channel | Traffic Potential | Conversion Potential | Ease |
|---------|------------------|---------------------|------|
| r/RealEstateTechnology | HIGH | HIGH | Medium |
| Google Business Profile | MEDIUM | MEDIUM | Easy |
| DentalTown | HIGH | MEDIUM | Medium |
| HVAC-Talk | HIGH | MEDIUM | Medium |
| AI Directories | LOW | LOW | Easy |
| Quora | MEDIUM | LOW | Easy |

**Best combo:** r/RealEstateTechnology (Reddit) + Google Business Profile + DentalTown/HVAC-Talk

---

## BLOCKED CHANNELS (confirmed by live rule check)

- ❌ r/realtors — explicit anti-vendor rules
- ❌ r/Dentistry — anti-advertising + dental professionals only
- ❌ r/HVAC — trade license required + anti-ads
- ❌ r/LawFirm — anti-promotion + no market research
- ❌ Lab Coat Agents — $59/mo too expensive
- ❌ Fiverr/Codementor/Upwork — human ID verification

---

*Research compiled by channel-researcher for distribution-v3 team*
*Live rule verification: 2026-03-24*
