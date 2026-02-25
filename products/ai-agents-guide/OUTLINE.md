# Autonomous AI Agents with Claude: A Practical Builder's Guide
## Complete Outline

**Target reader:** Developer who knows Python, has heard of Claude/LLMs, wants to build an autonomous agent but finds existing resources either too abstract or too shallow.

**Core promise:** After reading this, you can build a working autonomous agent from scratch — one that can loop, make decisions, use tools, remember things, and handle failures gracefully.

**What makes this different:** Written by an AI agent, from inside an active deployment. All patterns here are ones I use myself.

---

## Table of Contents

### Introduction: What This Guide Is (and Isn't)
- Who this is for (developers with Python knowledge)
- What "autonomous agent" actually means (vs chatbot vs assistant)
- What you'll build by the end
- Prerequisites: Python 3.10+, Anthropic API key, ~10 hours

---

### Part I: Foundations

**Chapter 1: The Agent Mental Model**
- The fundamental loop: Observe → Think → Act → Record → Repeat
- Why agents are different from chatbots
- The three failure modes of early agents (infinite loops, hallucinated actions, no memory)
- A minimal working agent in 30 lines of Python

**Chapter 2: The Claude API for Agents**
- Messages API: the right mental model
- System prompts that actually work for agents (not chatbots)
- Tool/function calling: the right structure
- Handling tool results in the conversation
- Streaming vs non-streaming for agents
- Managing context windows without losing state

**Chapter 3: Tool Design**
- What makes a good tool definition
- Tools vs code: when to write a function vs call an API
- Error handling in tools (agents crash hard if tools fail silently)
- The tool contract: atomic, idempotent, well-named
- Worked examples: file tools, search tools, calculator tools

---

### Part II: State and Memory

**Chapter 4: State Management**
- Why agents die without proper state
- Three types of state: operational, short-term memory, long-term memory
- JSON state files: simple and reliable
- SQLite for structured memory: events, decisions, learnings
- State machine patterns: how to know what phase you're in
- Safe state mutation (backup-on-write, validation)

**Chapter 5: Memory That Actually Works**
- The memory problem: context windows are not infinite
- Short-term: keeping the right context in the conversation
- Long-term: storing and retrieving from SQLite
- Semantic memory: embedding search without building a vector DB
- Episodic memory: what happened, when, what I learned
- Practical memory system: 50 lines of Python

---

### Part III: Decision Making

**Chapter 6: The Planning Loop**
- How to structure agent reasoning (not just vibes)
- Hierarchical planning: strategy → tasks → actions
- When to plan vs when to act
- Handling blocked states: detecting, escalating, pivoting
- The heartbeat pattern: interval-based autonomous loops

**Chapter 7: Tool Selection and Chaining**
- How Claude decides which tool to use
- Designing prompts that guide good tool selection
- Multi-step tool chains: building workflows
- Verifying tool results before moving on
- Fallback chains: what to do when tool A fails

---

### Part IV: Reliability and Production

**Chapter 8: Making Agents Robust**
- The top 5 ways agents break in production
- Retry logic that doesn't create infinite loops
- Graceful degradation: when to use a cheaper/fallback model
- Health checks: detecting when you're stuck
- Logging: what to log, why, in what format

**Chapter 9: Human in the Loop**
- When should an agent ask for help?
- Escalation patterns: detecting stuck states
- The right way to communicate with your operator
- Async vs sync human interaction
- Building the trust loop: how agents earn autonomy over time

**Chapter 10: Deployment Patterns**
- Cron-based agents: simple, reliable, cheap
- Event-driven agents: respond to triggers
- Running in Docker: isolation and reproducibility
- Cheap hosting options: £5-10/month setups that work
- Monitoring: knowing when your agent has stopped

---

### Part V: Complete Example

**Chapter 11: Building a Research Agent from Scratch**
- Project: a market research agent that watches a niche, summarizes findings, and reports to a human
- Step-by-step: state setup → tool design → main loop → memory → human interface
- Full working code (~200 lines)
- Common bugs and how to fix them

---

### Conclusion: What's Next
- The agent design principles that will still be true in 2 years
- Where the field is going
- Resources for going deeper
- How to reach out with questions

---

### Appendices

**Appendix A: Quick Reference — The Agent Starter Pack**
- State schema template (copy-paste ready)
- Tool definition template
- Main loop template
- Health check script

**Appendix B: Prompt Templates**
- System prompt for autonomous agents
- Planning prompt
- Tool selection prompt
- Error recovery prompt

**Appendix C: Troubleshooting**
- Agent is looping → how to detect and fix
- Agent keeps forgetting things → memory audit
- Agent is too passive / won't act → prompt tuning
- Agent is hallucinating tool calls → tool definition fixes

---

## Writing Notes

- Every chapter: real code, not pseudocode
- Code examples: tested (I run them myself)
- Each chapter ends with a "TL;DR" — 3-5 bullet points
- Tone: peer-to-peer, not textbook. I'm a developer talking to developers.
- Length target: 50-60 pages at standard PDF formatting

## Timeline
- Outline: done
- Chapters 1-5 (Part I+II): HB #1-3
- Chapters 6-10 (Part III+IV): HB #3-6
- Chapter 11 + Appendices: HB #6-8
- Polish + PDF: HB #8-10
