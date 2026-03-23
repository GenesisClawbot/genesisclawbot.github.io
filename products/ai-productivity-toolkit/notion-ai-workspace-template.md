# The AI Command Centre — Notion Workspace Template
### Complete Setup Guide and Implementation Blueprint

*This is not a Notion template file — it's a comprehensive implementation guide. Follow the steps below to build your AI Command Centre inside Notion. Estimated setup time: 60–90 minutes. Estimated time saved per week: 3–5 hours.*

---

## What Is the AI Command Centre?

The AI Command Centre is a Notion workspace designed around a single principle: **make AI the first tool you reach for, not the last.**

Most people open Notion to take notes. With this setup, you'll open Notion to feed AI your context, get AI to draft your content, and use Notion as the launchpad for AI-powered work across your entire day.

The workspace consists of 5 interconnected systems:
1. **Daily AI Dashboard** — Your command centre for daily AI-assisted work
2. **Project Management Hub** — AI-augmented project tracking
3. **Reading & Research System** — Capture, comprehend, and recall information
4. **Writing Pipeline** — From raw idea to polished output
5. **Weekly Review Template** — Structured reflection and planning

---

## How to Use This Guide

For each section below, you'll see:
- **What to create** in Notion
- **Properties to set**
- **How to connect it to the wider system**
- **Specific AI prompts to use with each page**

Follow the sections in order. Set aside 60–90 minutes for the initial build. After that, daily maintenance takes under 10 minutes.

---

## System 1: Daily AI Dashboard

### What to Create

Create a new **database** called "Daily Dashboard" with the following views:

1. **Calendar view** — by date, showing all daily entries
2. **Table view** — full list, filterable by status
3. **Board view** — by energy level (Morning Sharp / Afternoon Steady / Evening Wind-down)

### Database Properties

Create these properties for each daily entry:

| Property | Type | Notes |
|----------|------|-------|
| Date | Date | One entry per day |
| Day Rating | Select | 1–5 scale: 1 = terrible, 5 = excellent |
| Energy Level | Select | Morning Sharp / Afternoon Steady / Evening Wind-down |
| AI Tasks | Text | List AI-assisted tasks completed today |
| Top 3 Priorities | Text | Written each morning |
| Evening Reflection | Text | Written each evening |
| Tags | Multi-select | Work, Personal, Health, Learning, Creative |

### The Daily Page Template

Each daily entry should contain this **inline template** of blocks:

```
## Good morning — [DATE]

**Today's Focus:** (3 words that capture your main focus today)

**Top 3 Priorities:**
1. [ ]
2. [ ]
3. [ ]

**AI Assistance Log:**
- Task: [What you asked AI to do] → Result: [Outcome]
- Task: [What you asked AI to do] → Result: [Outcome]

**Notes & Captures:**
[Space for in-meeting notes, ideas, links captured during the day]

---

## Evening Wind-Down — [DATE]

**What went well today:**
-

**What could have gone better:**
-

**Tomorrow's top priority:**
-

**AI productivity score:** [1–10 — how much did AI help today?]
```

### AI Prompts for the Daily Dashboard

**Morning AI Prompt (copy and paste into ChatGPT/Claude each morning):**

```
It's [DAY, DATE]. My three most important tasks today are:
1. [TASK]
2. [TASK]
3. [TASK]

My energy is [HIGH/MEDIUM/LOW]. My main challenge today is [CHALLENGE].

Based on this, what's the optimal order to tackle these tasks, and what should I delegate or defer?

Also draft a morning email check-in to myself (3 sentences) covering what I need to focus on.
```

**Evening AI Prompt:**

```
Review my day: [WHAT YOU DID TODAY]. My biggest achievement was [ACHIEVEMENT]. My biggest frustration was [FRUSTRATION].

Help me write my evening reflection. Then based on today's experience, suggest my top 3 priorities for tomorrow and why.

Also: rate my AI usage today (1–10) and tell me one specific way I could have used AI more effectively.
```

---

## System 2: Project Management with AI Assist

### What to Create

Create a **database** called "Projects" with the following views:

1. **Gallery view** — visual project cards (use project cover images or colour coding)
2. **Table view** — full project list with all properties
3. **Calendar view** — deadline-centric view

### Database Properties

| Property | Type | Notes |
|----------|------|-------|
| Project Name | Title | Name of the project |
| Status | Select | Ideation / Planning / In Progress / Review / Done / On Hold |
| Priority | Select | Critical / High / Medium / Low |
| Client/Owner | Text | Who this is for (can be internal) |
| Start Date | Date | When the project begins |
| Deadline | Date | When it's due |
| AI Status | Select | Not started / AI drafted / AI reviewed / Human finalised |
| Next AI Action | Text | What AI should help with next |
| Tags | Multi-select | Content / Code / Design / Research / Admin |
| Progress | Number | 0–100% (updated manually weekly) |

### Project Page Template

Each project page should include:

```
## [PROJECT NAME]

**Status:** [STATUS — colour coded]
**Priority:** [PRIORITY]
**Client/Owner:** [CLIENT OR INTERNAL OWNER]
**Timeline:** [START DATE] → [DEADLINE]
**AI Status:** [STATUS]

---

## Project Overview
[2–3 sentences: what is this project, why does it matter, what does success look like?]

## AI Brief
[Copy and paste the AI prompt you used for this project here — keeps a record of AI assistance]

## Deliverables
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]
- [ ] [Deliverable 3]

## Key Milestones
| Milestone | Owner | Deadline | Status |
|-----------|-------|----------|--------|
| [Milestone 1] | [Name] | [Date] | [ ] |
| [Milestone 2] | [Name] | [Date] | [ ] |

## AI Integration Log
| Date | AI Task | Output | Used? |
|------|---------|--------|-------|
| [Date] | [Task description] | [One-line summary] | [Yes/No/Modified] |

## Notes
[Space for ongoing notes, decisions, links]
```

### AI Prompts for Project Management

**Kickoff AI Prompt:**

```
I'm starting a new project. Help me create a project brief.

Project name: [NAME]
Deadline: [DATE]
Client/stakeholder: [NAME]
What I need to deliver: [DESCRIPTION]

Create:
1. A clear project scope (what's in and what's explicitly out)
2. 5 key deliverables (specific, measurable)
3. A risk register — top 3 risks and how to mitigate them
4. A communication plan — what to communicate, when, and to whom
5. An AI integration plan — where in this project should I use AI and how?

Write this as a professional project brief.
```

**Weekly Progress AI Prompt:**

```
It's the end of week [NUMBER] of the [PROJECT NAME] project.

Here's where we are:
- Completed: [LIST COMPLETED ITEMS]
- Still in progress: [LIST IN-PROGRESS ITEMS]
- Blockers: [LIST BLOCKERS]

Based on this, help me:
1. Update my project status (be honest)
2. Identify what's behind schedule and why
3. Create a focused action plan for next week (top 5 actions only)
4. Draft a status update email for [STAKEHOLDER]

Write the update now.
```

---

## System 3: Reading & Research Notes

### What to Create

Create a **database** called "Reading & Research" with views:

1. **Table view** — all sources, sortable by date, tag, status
2. **Card gallery** — visual cards for each source (use favicon or category colour)
3. **Board view** — by reading status: To Read / Reading / Processed / Archived

### Database Properties

| Property | Type | Notes |
|----------|------|-------|
| Source Title | Title | Article, book, or document name |
| Source Type | Select | Article / Book / Report / Video / Podcast / Document |
| Author/Source | Text | Who created it |
| URL | URL | Link to source |
| Date Added | Date | Auto or manual |
| Status | Select | To Read / Reading / Processed / Archived |
| Key Insight | Text | One-sentence takeaway |
| Tags | Multi-select | [Topic tags — e.g., AI, Marketing, Finance] |
| AI Summary | Text | Summary generated by AI |
| Action Items | Text | What to do with this information |

### Reading Note Page Template

Each reading entry page should contain:

```
## [SOURCE TITLE]
**Author/Creator:** [NAME]
**Type:** [TYPE]
**URL:** [LINK]
**Date:** [DATE]
**Status:** [STATUS]

---

## Why I Saved This
[2 sentences: why this is relevant to me right now]

## AI Summary
[Use the AI Summary Prompt below to generate this]

## Key Takeaways
1. [Takeaway 1]
2. [Takeaway 2]
3. [Takeaway 3]

## Quotes & Passages
> "[Quote or passage from the source]"
> "[Another quote]"

## How This Connects to My Work
[How this information applies to your current projects or thinking]

## Action Items
- [ ] [Action derived from this reading]
- [ ] [Action derived from this reading]

## Related Notes
[[Link to related notes in your workspace]]
```

### AI Prompts for Reading & Research

**Article/Video Summary Prompt:**

```
Read and summarise the following: [PASTE ARTICLE TEXT OR VIDEO TRANSCRIPT / URL]

Structure your summary:
- 1-paragraph executive summary (what this is about and why it matters)
- 5 key facts or insights (each 1–2 sentences)
- 3 specific things I can apply immediately
- 1 thing that challenges my current thinking
- Questions I'd want to ask the author

Target length: 300 words.
```

**Book Chapter Summary Prompt:**

```
Summarise the following book chapter:

Chapter: [CHAPTER NAME]
Book: [BOOK TITLE]
Author: [AUTHOR]

Include:
- Core thesis of this chapter (1 sentence)
- 4 key arguments or concepts (each explained in 2 sentences)
- Specific examples or case studies the author uses
- How this chapter connects to [PREVIOUSLY READ CHAPTER OR RELATED TOPIC]
- 2 actionable takeaways I can implement today
- 1 quote worth remembering

Write this as a useful reference note I can return to.
```

**Research Synthesis Prompt:**

```
I'm researching [TOPIC]. I've gathered the following sources:
1. [SOURCE 1] — Key finding: [ONE SENTENCE]
2. [SOURCE 2] — Key finding: [ONE SENTENCE]
3. [SOURCE 3] — Key finding: [ONE SENTENCE]

Help me synthesise this into:
1. Where these sources agree (the consensus)
2. Where they disagree (the debates)
3. The most surprising or counterintuitive finding
4. What the field/topic still doesn't know or where there's a gap
5. A conclusion I can draw with confidence
6. 3 specific angles to explore further

Write this as a research synthesis note.
```

---

## System 4: Writing Pipeline with AI Editing Stages

### What to Create

Create a **database** called "Writing Pipeline" with views:

1. **Board view** — by stage (Ideas / Drafting / AI Review / Human Edit / Final / Published)
2. **Table view** — full list with all metadata
3. **Calendar view** — by publication deadline

### Database Properties

| Property | Type | Notes |
|----------|------|-------|
| Piece Title | Title | Title of the content piece |
| Format | Select | Blog Post / Email / Social Post / Report / Landing Page Copy / Other |
| Stage | Select | Idea / Drafting / AI Review / Human Edit / Final / Published |
| Word Count | Number | Target or actual |
| Deadline | Date | When it needs to be done/published |
| Audience | Text | Who this is written for |
| Primary Goal | Select | Inform / Persuade / Convert / Entertain |
| SEO Keyword | Text | Primary keyword if applicable |
| AI Prompts Used | Text | Record which prompts were used |
| Published | Checkbox | Has this been published? |
| Published URL | URL | Link if published |
| Tags | Multi-select | [Topic tags] |

### Writing Page Template

Each writing piece page should follow this pipeline structure:

```
## [PIECE TITLE]
**Format:** [FORMAT]
**Stage:** [CURRENT STAGE — colour coded]
**Deadline:** [DATE]
**Audience:** [AUDIENCE]
**Goal:** [GOAL]
**SEO Keyword:** [KEYWORD IF APPLICABLE]

---

## Stage 1: The Brief
**What am I writing?** [Clear description]
**Who am I writing for?** [Detailed audience description]
**What should they do/feel/know after reading?** [Call to desired outcome]
**Key message:** [The one thing this piece must communicate]
**Word count target:** [TARGET]

---

## Stage 2: Research & Context
[Summarise what research you did — links, notes, key facts to include]
AI research prompt used: [PASTE THE PROMPT YOU USED]

---

## Stage 3: AI First Draft
**Prompt used:**
[PASTE THE EXACT PROMPT YOU FED TO AI]

**AI Output:**
[PASTE THE RAW AI OUTPUT HERE]

---

## Stage 4: Human Edit
**Changes made from AI draft:**
1. [Change 1 and why]
2. [Change 2 and why]
3. [Change 3 and why]

**What the AI got right:**
- [ ]
- [ ]
- [ ]

**What needed significant revision:**
- [ ]

**Final word count:** [COUNT]
**Read time:** [CALCULATE — ~200 words per minute]

---

## Stage 5: SEO Check (if applicable)
- Primary keyword in title: [YES/NO]
- Primary keyword in first 100 words: [YES/NO]
- Primary keyword in meta description: [YES/NO]
- Subheadings use related keywords: [YES/NO]
- Internal links included: [YES/NO]
- Word count adequate for topic: [YES/NO]

---

## Stage 6: Publication
**Published:** [YES/NO]
**URL:** [IF PUBLISHED]
**Published date:** [DATE]
**Performance notes:** [HOW DID IT PERFORM — traffic, engagement, conversions]

---

## Feedback Loop
**What worked well in this piece?**
-

**What would I do differently next time?**
-

**AI prompt to reuse:** [PASTE PROMPT]
```

### AI Prompts for the Writing Pipeline

**Brief Generator (for new content):**

```
I need to write a piece of content. Help me define the brief first.

Topic: [TOPIC OR ANGLE]
Format: [FORMAT — e.g., 800-word blog post, email newsletter, LinkedIn post]
Audience: [AUDIENCE DESCRIPTION]
Goal: [WHAT THE READER SHOULD DO OR FEEL]

Based on this, give me:
1. A working title (3 options)
2. The core thesis in one sentence
3. 3 key points to cover
4. A recommended structure (opening hook, middle sections, closing CTA)
5. 5 SEO-friendly subheading options
6. A meta description under 155 characters

Write the brief now.
```

**AI Draft Prompt:**

```
Using the brief above, write a complete first draft.

Requirements:
- Word count: approximately [TARGET] words
- Tone: [TONE — conversational / professional / authoritative / friendly]
- Audience: [AUDIENCE — describe them specifically]
- Include a hook in the first 2 lines
- Use [NUMBER] subheadings
- End with [SPECIFIC CTA — e.g., "subscribe to my newsletter" / "book a call" / "leave a comment"]

Write the full draft now. Do not include the brief — just the content.
```

**Edit & Refine Prompt:**

```
I wrote the following content and need a thorough edit:

[PASTE YOUR DRAFT HERE]

Edit this for:
1. Clarity — simplify any confusing sentences
2. Flow — improve transitions between paragraphs
3. Engagement — strengthen the opening hook and closing
4. Readability — aim for sentences under 25 words average
5. Tone consistency — make sure it sounds like [DESCRIBE YOUR PREFERRED VOICE]
6. Filler words — remove "actually," "very," "really," "that," "just" where unnecessary

Provide the edited version, then list the 5 most significant changes you made and why.
```

---

## System 5: Weekly Review Template

### What to Create

Create a **database** called "Weekly Reviews" with a **Calendar view** by week.

### Database Properties

| Property | Type | Notes |
|----------|------|-------|
| Week Of | Date | Monday of the week |
| Week Number | Formula | Week number of the year |
| Energy Score | Number | 1–10 average self-assessment |
| AI Usage Score | Number | 1–10 how effectively did AI help this week |
| Top Win | Text | The single biggest win of the week |
| Focus Goal | Text | One word for next week's focus |
| Tags | Multi-select | Work, Personal, Health, Learning |

### Weekly Review Page Template

```
## Weekly Review — Week of [DATE]

---

## SECTION 1: WINDSCREEN CHECK
*5 minutes — quick reflection on the week as a whole*

In one sentence, describe this week:
-

Rate the week: [1 = worst / 10 = best] → [NUMBER]

Rate your AI usage this week: [1 = barely used it / 10 = AI was core to everything I did]

---

## SECTION 2: ACCOMPLISHMENTS
*10 minutes — document what actually happened*

**Work/Projects completed:**
- [Accomplishment 1]
- [Accomplishment 2]
- [Accomplishment 3]

**Meetings and outcomes:**
- [Meeting 1]: [OUTCOME]
- [Meeting 2]: [OUTCOME]

**Things I learned:**
- [Learning 1]
- [Learning 2]

---

## SECTION 3: AI INTEGRATION REVIEW
*5 minutes — how effectively did you use AI this week?*

AI tasks completed this week:
- [ ] [Task AI helped with]
- [ ] [Task AI helped with]
- [ ] [Task AI helped with]

Best AI moment this week (where AI genuinely saved time or improved quality):
-

Where did AI let me down or produce poor output?
-

Next week, my AI goal is: [ONE SPECIFIC GOAL]

---

## SECTION 4: WHAT DIDN'T GET DONE
*5 minutes — honest assessment*

**Intended to do but didn't:**
- [Task] — Why? [Reason]
- [Task] — Why? [Reason]

**What blocked progress?**
1. [Blocker 1]
2. [Blocker 2]

---

## SECTION 5: HEALTH & ENERGY
*3 minutes*

Energy rating this week: [1–10] — [Brief explanation]

Best thing I did for my health/energy:
-

Worst habit that drained my energy:
-

---

## SECTION 6: NEXT WEEK — THE PLAN
*10 minutes — this is the most important section*

**Next week's ONE word focus:** [WORD]

**Top 3 priorities for next week:**
1. [Priority 1] — Why it matters: [One sentence]
2. [Priority 2] — Why it matters: [One sentence]
3. [Priority 3] — Why it matters: [One sentence]

**AI prompts to use next week:**
- [Prompt description or paste the actual prompt]
- [Prompt description or paste the actual prompt]

**What's scheduled / committed:**
- [Commitment 1 — meeting, deadline, etc.]
- [Commitment 2]

**What I'm protecting for deep work:**
- [Time block 1 — what I'll work on]
- [Time block 2 — what I'll work on]

---

## SECTION 7: GRATITUDE & PERSPECTIVE
*3 minutes — for long-term resilience*

I'm grateful for:
-

The thing I'm most proud of this week:
-

One thing I'm looking forward to next week:
-
```

### AI Prompts for Weekly Review

**AI Weekly Review Assistant Prompt:**

```
It's the end of week [NUMBER] of [YEAR]. Help me conduct my weekly review.

Here's a summary of my week:
- Main accomplishments: [LIST]
- Things I didn't get to: [LIST]
- My biggest frustration: [DESCRIPTION]
- My biggest win: [DESCRIPTION]
- Hours worked: [APPROXIMATE]

I use AI for: [WHAT YOU USE AI FOR — e.g., "writing drafts, coding, research" / "everything"]

My AI usage this week was [LOW/MEDIUM/HIGH] — [SPECIFIC EXAMPLE OF WHERE AI HELPED AND WHERE IT DIDN'T]

Help me write my full weekly review covering:
1. An honest assessment of the week (2–3 paragraphs)
2. What I should celebrate
3. What I need to do differently next week
4. My top 3 priorities for next week
5. One AI experiment to try next week (something specific and actionable)
```

---

## Putting It All Together — The AI Command Centre Dashboard

Create a **single page** called "AI Command Centre" that serves as your home base. Include:

```
# AI Command Centre

**Date:** [CURRENT DATE]
**Week:** [WEEK NUMBER]
**My Focus Word:** [YOUR WORD]

---

## Today's Snapshot
[Embed your Today's Daily Dashboard entry]

## Active Projects
[Filtered view of Projects database — showing only "In Progress" items]

## Writing Pipeline — In Progress
[Filtered view of Writing Pipeline — showing only items in Drafting, AI Review, or Human Edit]

## This Week's Reading
[Filtered view of Reading & Research — showing "Reading" and "To Read" items]

## Quick AI Prompts
[Buttons/links to your most-used prompts — copy these as linked sub-pages or templates]

---

## AI Usage This Week
Tasks completed with AI: [NUMBER]
AI time saved: [ESTIMATE — e.g., "approximately 3 hours"]
Most useful AI task this week: [TASK]

## Last Week's AI Score: [NUMBER]/10
## This Week's AI Goal: [ONE SENTENCE]
```

---

## Setup Checklist

Before you start using the workspace daily, complete this checklist:

- [ ] Created "Daily Dashboard" database with all properties and views
- [ ] Set up 3-day template pages in Daily Dashboard
- [ ] Created "Projects" database with all properties and views
- [ ] Set up 1 sample project page as a template
- [ ] Created "Reading & Research" database with all properties and views
- [ ] Set up 1 sample reading note page
- [ ] Created "Writing Pipeline" database with all properties and views
- [ ] Set up 1 sample writing piece page through the full pipeline
- [ ] Created "Weekly Reviews" database with all properties and views
- [ ] Built the "AI Command Centre" home dashboard page
- [ ] Copied all AI prompts into a "Prompt Library" sub-page or separate database
- [ ] Tested the morning AI prompt with ChatGPT or Claude
- [ ] Scheduled weekly review for the same time each week

---

## Recommended Notion AI Add-on

If you're on Notion Plus or higher, the Notion AI add-on (included at $10/user/month) allows you to:
- Generate page summaries directly inside Notion
- Draft content within Notion pages
- Auto-tag and categorise entries
- Translate and improve writing in-place

Enable Notion AI on your workspace and use it for:
- Generating initial summaries in Reading & Research notes
- Drafting within writing pages
- Quick improvements to meeting notes

For more complex tasks (long documents, multi-step analysis, coding), continue using ChatGPT or Claude in a separate tab.

---

*Last updated: March 2026. Notion's interface may have changed since publication — adapt the structure to match your current Notion version.*
