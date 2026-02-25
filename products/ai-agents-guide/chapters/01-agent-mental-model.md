# Chapter 1: The Agent Mental Model

Before you write a single line of code, you need to internalize one idea. Everything else in this guide flows from it.

**An agent is a loop with a brain.**

That's it. Strip away all the complexity, and every autonomous agent — from a simple task runner to a multi-agent orchestration system — is some form of: *run, decide, act, repeat*.

Let's make this concrete.

---

## 1.1 The Fundamental Loop

Here's the simplest possible agent loop:

```python
import anthropic
import time

client = anthropic.Anthropic()

def run_agent():
    state = load_state()          # What do I know?
    
    while True:
        # 1. Observe: what's the current situation?
        context = build_context(state)
        
        # 2. Think: what should I do?
        decision = ask_claude(context)
        
        # 3. Act: do the thing
        result = execute(decision)
        
        # 4. Record: update what I know
        state = update_state(state, result)
        
        # 5. Wait, then repeat
        time.sleep(900)  # 15 minutes
```

This loop has five steps: **Observe, Think, Act, Record, Wait**. Every agent I've ever seen — every good one, anyway — is a variation of this.

The details differ wildly. "Observe" might mean reading a database, checking an API, or scanning a filesystem. "Think" might involve multiple Claude calls, tool use, and planning sub-steps. "Act" might mean sending an email, writing a file, or calling an API. "Record" might be a JSON file or a full SQLite database.

But the loop structure stays constant. Understanding this structure is understanding how agents work.

---

## 1.2 Why Agents Are Different from Chatbots

The conceptual gap between "chatbot" and "agent" is bigger than it looks.

A chatbot has this architecture:

```
User message → Claude → Response
```

Simple. Stateless (unless you add memory). Human-initiated. One round trip.

An agent has this architecture:

```
[State] → Decide → [Tools] → Act → Update [State] → Wait → [State] → Decide → ...
```

The critical differences:

1. **Self-initiated**: The agent doesn't wait for a human to prompt it. It wakes up and decides what to do based on its internal state.

2. **Has tools**: A chatbot only talks. An agent can *do* things — write files, call APIs, run searches, send messages.

3. **Maintains state**: Between cycles, the agent persists what it knows. It's not amnesiac.

4. **Loops**: The agent runs continuously (or on a schedule). Each cycle builds on the last.

5. **Handles failure**: When something breaks, the agent has to decide what to do — retry, escalate, or pivot. A chatbot just crashes.

This sounds simple when written out. In practice, each of these differences creates engineering challenges that aren't obvious until you hit them.

---

## 1.3 The Three Failure Modes

Most agents fail in one of three ways. Knowing these in advance saves you significant frustration.

### Failure Mode 1: The Infinite Loop

The agent starts an action, the action partially completes, the agent checks if it succeeded, decides it failed, tries again, the action partially completes again... forever.

**Why it happens:** The agent doesn't have good idempotency checks or state tracking. Each cycle, it re-evaluates the same incomplete state and re-triggers the same action.

**The fix:** Explicit state transitions. Once an action is *started*, the state records "started." Once it's *done*, it records "done." The agent checks state transitions, not just outcomes.

```python
# Bad: checks outcome on every cycle
if not file_exists("report.pdf"):
    generate_report()  # might fail halfway

# Better: tracks state transitions
if state["report_status"] == "not_started":
    state["report_status"] = "generating"
    generate_report()
    state["report_status"] = "done"
```

### Failure Mode 2: Hallucinated Actions

The agent confidently announces it did something. It didn't. It invented a successful outcome.

**Why it happens:** The agent is calling a tool, the tool fails silently (or the agent ignores the error), and the model generates a confident-sounding response about completing the task.

**The fix:** Verify before recording. Never update state to "completed" based on what Claude *said* happened — verify based on what actually happened.

```python
# Bad: trusts Claude's narration
result = client.messages.create(...)
# Claude says "I've sent the email"
state["email_sent"] = True

# Better: verify the actual outcome
response = send_email(to, subject, body)
if response.status_code == 200:
    state["email_sent"] = True
else:
    state["email_error"] = response.error
```

### Failure Mode 3: No Memory

The agent works fine on its first run. On its second run, it forgets everything it learned and starts over. By the fifth run, it's re-trying things that failed four times in a row.

**Why it happens:** All state is in-memory (Python variables). When the process restarts, it's gone.

**The fix:** Every meaningful state must be persisted before the process ends. State lives in files and databases, not in variables. Chapter 4 covers this in depth.

---

## 1.4 A Minimal Working Agent

Here's a complete, runnable agent — 30 lines of Python. It's not useful for anything in particular, but every concept in the rest of this guide appears in miniature here.

```python
import anthropic
import json
import time
from pathlib import Path

client = anthropic.Anthropic()
STATE_FILE = Path("state.json")

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"cycles": 0, "notes": []}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def think(state):
    """Ask Claude what to do next."""
    messages = [{
        "role": "user",
        "content": f"You are an agent. Current state: {json.dumps(state)}. "
                   f"Suggest one thing to do. Reply with: ACTION: <what to do>"
    }]
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=256,
        messages=messages
    )
    return response.content[0].text

def run():
    while True:
        state = load_state()
        state["cycles"] += 1
        
        decision = think(state)
        print(f"Cycle {state['cycles']}: {decision}")
        
        # Record that we thought about something
        state["notes"].append({
            "cycle": state["cycles"],
            "decision": decision
        })
        
        save_state(state)
        time.sleep(60)

if __name__ == "__main__":
    run()
```

This agent:
- Loads state from disk (persistent across restarts)
- Asks Claude what to do
- Records the decision
- Saves state back to disk
- Loops

It's not useful. But it's a real agent. Every more complex agent you'll build adds detail to these same pieces — richer state, more tools, better prompting, more reliable execution.

---

## 1.5 From Minimal to Real

The gap between this minimal agent and a production agent isn't a different architecture — it's the same architecture with more detail in each piece.

Here's the mapping:

| Minimal Agent | Production Agent |
|---------------|-----------------|
| `load_state()` — reads a JSON file | Chapter 4: State management with SQLite + backups |
| `think()` — one basic Claude call | Chapter 6-7: Planning loops, tool selection |
| `print(decision)` — no action | Chapter 3: Tool design and execution |
| `state["notes"].append(...)` — records text | Chapter 5: Memory systems with retrieval |
| `time.sleep(60)` — fixed interval | Chapter 10: Deployment patterns |

We'll fill in each of these over the course of this guide. By Chapter 11, the minimal agent will have become something genuinely capable.

---

## TL;DR

- Every agent is a loop: Observe → Think → Act → Record → Repeat
- Agents differ from chatbots in four ways: self-initiated, have tools, maintain state, handle failure
- Three failure modes to avoid: infinite loops (fix with state transitions), hallucinated actions (fix with verification), no memory (fix with persistence)
- The minimal 30-line agent contains all the concepts — subsequent chapters add depth to each piece

---

*Next: Chapter 2 — The Claude API for Agents*
