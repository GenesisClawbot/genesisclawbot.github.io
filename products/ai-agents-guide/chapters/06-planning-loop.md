# Chapter 6: The Planning Loop

Your agent has tools, state, and memory. Now: how does it decide what to do?

Most beginners assume "just ask Claude" is the answer. It partly is. But raw "tell me what to do" prompts produce inconsistent, unfocused behavior. Agents need structured planning — a way of translating high-level goals into specific, executable steps, and then choosing which step to execute right now.

This chapter gives you a planning system that's simple enough to implement in an afternoon and robust enough for production use.

---

## 6.1 The Planning Hierarchy

Good agent planning has three levels:

```
STRATEGY (days to weeks)
  "I am researching the AI tools market and will publish a weekly report"
  
    PLAN (hours to a day)
    "Today: research 5 competitors, summarize pricing, draft comparison table"
    
      TASK (minutes to hours)
      "Right now: fetch pricing page for Competitor A, extract price tiers"
```

Strategy is set by you (or your human operator). The agent handles plan and task level.

In practice, you encode the strategy into the system prompt and initial state. The agent generates and executes at the task level, with occasional replanning when tasks fail or circumstances change.

```python
# Strategy is embedded in the system prompt (static)
STRATEGY = """
Your goal is to produce a weekly competitive intelligence report on AI coding tools.
Every cycle, advance toward this goal by:
1. Discovering new competitors or product updates
2. Documenting pricing, features, and positioning
3. Identifying market trends
Once you have sufficient research (20+ findings), generate the report.
"""

# Plan is dynamic state managed by the agent
initial_state = {
    "tasks": {
        "queued": [
            {"id": "t001", "name": "Research GitHub Copilot pricing", "type": "research"},
            {"id": "t002", "name": "Research Cursor pricing", "type": "research"},
            {"id": "t003", "name": "Research Tabnine pricing", "type": "research"},
            {"id": "t004", "name": "Identify 3 additional competitors", "type": "discovery"},
        ],
        "active": [],
        "completed": []
    }
}
```

---

## 6.2 The Heartbeat Pattern

The heartbeat is the simplest reliable agent scheduling pattern. The agent runs, does one meaningful thing, records it, and sleeps until the next cycle.

```python
import time
import signal
import sys

class AgentRunner:
    def __init__(self, agent_fn, interval_seconds: int = 900):
        self.agent_fn = agent_fn
        self.interval = interval_seconds
        self.running = True
        
        # Handle graceful shutdown
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)
    
    def _shutdown(self, signum, frame):
        print("Shutdown signal received. Finishing current cycle...")
        self.running = False
    
    def run(self):
        print(f"Agent starting. Heartbeat interval: {self.interval}s")
        
        while self.running:
            cycle_start = time.time()
            
            try:
                print(f"\n--- Heartbeat at {datetime.utcnow().isoformat()} ---")
                self.agent_fn()
            except Exception as e:
                print(f"ERROR in agent cycle: {e}")
                import traceback
                traceback.print_exc()
                # Don't crash the runner — log and continue
            
            elapsed = time.time() - cycle_start
            sleep_time = max(0, self.interval - elapsed)
            
            if sleep_time > 0:
                print(f"Cycle complete in {elapsed:.1f}s. Sleeping {sleep_time:.0f}s...")
                time.sleep(sleep_time)
        
        print("Agent shutdown complete.")

# Usage
def my_agent():
    state = load_state()
    # ... agent logic
    save_state(state)

runner = AgentRunner(my_agent, interval_seconds=900)
runner.run()
```

Key design decisions:
- **One meaningful action per cycle**: prevents chains of actions that are hard to debug
- **Catch exceptions at the runner level**: agent bugs shouldn't kill the runner
- **Graceful shutdown**: lets the current cycle finish cleanly before stopping

---

## 6.3 The Task Selection Algorithm

How does the agent decide which task to work on? You need a priority function:

```python
from dataclasses import dataclass
from typing import Optional
import memory_system as mem

@dataclass
class Task:
    id: str
    name: str
    type: str
    priority: int = 5  # 1 (highest) to 10 (lowest)
    attempts: int = 0
    blocked_reason: Optional[str] = None
    depends_on: list = None


def select_next_task(tasks: list[Task]) -> Optional[Task]:
    """
    Pick the highest-priority unblocked task.
    
    Priority factors:
    1. Explicitly set priority
    2. How many times it's been attempted (deprioritize repeated failures)
    3. Whether it's been tried recently
    """
    eligible = [t for t in tasks if not t.blocked_reason]
    
    if not eligible:
        return None
    
    def task_score(task: Task) -> float:
        score = task.priority  # lower = higher priority
        
        # Penalize tasks with many failures
        failure_count = mem.failure_count(task.name, hours=48)
        score += failure_count * 2  # each failure adds 2 to score (makes it lower priority)
        
        return score
    
    return min(eligible, key=task_score)


def pick_action_for_task(task: Task, state: dict) -> dict:
    """
    Ask Claude what specific action to take for a given task.
    Uses a smaller model for speed and cost.
    """
    # Get relevant context
    recent = mem.recent_events(5)
    relevant = mem.recall(task.name, limit=3)
    
    prompt = f"""You are executing a specific task.

Task: {task.name} (type: {task.type}, attempt #{task.attempts + 1})

Recent agent actions:
{format_events(recent)}

Relevant prior findings:
{format_findings(relevant)}

Current state:
{json.dumps(state['context'], indent=2)}

What is the single most useful action to take right now to advance this task?
Respond with JSON:
{{
  "action": "tool_name",
  "params": {{}},
  "reasoning": "one sentence"
}}"""
    
    response = client.messages.create(
        model="claude-haiku-4-5",  # fast, cheap for action selection
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        return json.loads(response.content[0].text)
    except json.JSONDecodeError:
        # Extract JSON from response if wrapped in prose
        import re
        match = re.search(r'\{.*\}', response.content[0].text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"action": "none", "params": {}, "reasoning": "Could not parse response"}
```

---

## 6.4 Handling Blocked States

The most dangerous agent failure is the one you don't detect: a task that's failing silently, cycle after cycle, while the agent thinks it's making progress.

Explicit stuck detection prevents this:

```python
MAX_FAILURES = 3
MAX_IDLE_CYCLES = 5

def check_stuck(state: dict) -> tuple[bool, str]:
    """
    Returns (is_stuck, reason).
    Check this at the start of every cycle.
    """
    # Check for idle cycles
    idle = state["system"].get("consecutive_idle", 0)
    if idle >= MAX_IDLE_CYCLES:
        return True, f"No meaningful action for {idle} cycles"
    
    # Check for repeatedly failing tasks
    for task in state["tasks"]["active"]:
        failures = mem.failure_count(task["name"], hours=48)
        if failures >= MAX_FAILURES:
            return True, f"Task '{task['name']}' has failed {failures} times in 48h"
    
    # Check for tasks in active too long
    for task in state["tasks"]["active"]:
        if "started" in task:
            started = datetime.fromisoformat(task["started"])
            hours_active = (datetime.utcnow() - started).total_seconds() / 3600
            if hours_active > 4:
                return True, f"Task '{task['name']}' has been active for {hours_active:.1f} hours"
    
    return False, ""


def handle_stuck(reason: str, state: dict) -> dict:
    """
    When stuck: try replanning. If still stuck, escalate to human.
    """
    stuck_count = state["system"].get("stuck_count", 0) + 1
    state["system"]["stuck_count"] = stuck_count
    
    print(f"STUCK (count={stuck_count}): {reason}")
    mem.log(f"Stuck detected: {reason}", "warning")
    
    if stuck_count <= 2:
        # First stuck: try replanning
        print("Attempting replan...")
        state = replan(state, reason)
        state["system"]["consecutive_idle"] = 0
    else:
        # Repeatedly stuck: escalate to human
        notify_human(
            title="[STUCK] Agent needs help",
            message=f"I've been stuck for {stuck_count} consecutive detections.\n"
                   f"Reason: {reason}\n"
                   f"State: {json.dumps(state['tasks'], indent=2)}\n\n"
                   f"Please check HUMAN_REQUEST.md for what I need."
        )
        write_human_request(reason, state)
        state["system"]["phase"] = "waiting_for_human"
    
    return state


def replan(state: dict, stuck_reason: str) -> dict:
    """Ask Claude to generate a new plan given the stuck state."""
    prompt = f"""The agent is stuck. Reason: {stuck_reason}

Current tasks:
{json.dumps(state['tasks'], indent=2)}

Recent events:
{format_events(mem.recent_events(10))}

Generate a revised task list that might unblock progress. 
Consider: different approach, smaller steps, or explicit blockers to document.

Respond with JSON:
{{
  "analysis": "what went wrong",
  "new_tasks": [
    {{"id": "t_new_001", "name": "...", "type": "...", "priority": 1}}
  ],
  "blocked_tasks": ["id of tasks to mark blocked"],
  "blocked_reasons": ["reason for each"]
}}"""
    
    response = client.messages.create(
        model="claude-sonnet-4-5",  # use full model for replanning
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        plan = json.loads(response.content[0].text)
        print(f"New plan: {plan['analysis']}")
        
        # Apply the new plan
        for new_task in plan.get("new_tasks", []):
            state["tasks"]["queued"].append(new_task)
        
        # Mark blocked tasks
        for i, task_id in enumerate(plan.get("blocked_tasks", [])):
            for task in state["tasks"]["active"]:
                if task["id"] == task_id:
                    task["blocked_reason"] = plan["blocked_reasons"][i] if i < len(plan["blocked_reasons"]) else "blocked during replan"
        
        save_state(state)
    except Exception as e:
        print(f"Replan failed: {e}")
    
    return load_state()
```

---

## 6.5 The Complete Planning Loop

Here's the main loop with all planning components integrated:

```python
def agent_main():
    """One complete agent cycle with full planning logic."""
    
    # 1. Load state and record heartbeat
    state = load_state()
    state["system"]["heartbeat_count"] += 1
    state["system"]["last_heartbeat"] = datetime.utcnow().isoformat()
    
    # 2. Check for stuck state
    is_stuck, reason = check_stuck(state)
    if is_stuck:
        state = handle_stuck(reason, state)
        save_state(state)
        return  # let next cycle handle after unstuck
    
    # 3. Check for phase completion
    if state["system"]["phase"] == "waiting_for_human":
        print("Waiting for human input. Skipping cycle.")
        return
    
    # 4. Move a queued task to active if none are active
    if not state["tasks"]["active"] and state["tasks"]["queued"]:
        next_task = state["tasks"]["queued"].pop(0)
        next_task["status"] = "in_progress"
        next_task["started"] = datetime.utcnow().isoformat()
        next_task["attempts"] = 0
        state["tasks"]["active"].append(next_task)
        save_state(state)
    
    # 5. Get the current task
    if not state["tasks"]["active"]:
        print("No tasks. Checking if done...")
        if len(state["tasks"]["completed"]) >= MIN_TASKS_FOR_REPORT:
            state["system"]["phase"] = "writing"
        else:
            state["system"]["consecutive_idle"] += 1
        save_state(state)
        return
    
    current_task = state["tasks"]["active"][0]
    
    # 6. Decide what action to take
    action = pick_action_for_task(Task(**current_task), state)
    print(f"Action: {action['action']} — {action['reasoning']}")
    
    if action["action"] == "none":
        state["system"]["consecutive_idle"] += 1
        save_state(state)
        return
    
    state["system"]["consecutive_idle"] = 0
    
    # 7. Execute the action
    result = execute_tool(action["action"], action["params"])
    
    # 8. Record what happened
    success = result.get("success", True)
    mem.log(
        description=f"[{current_task['name']}] {action['action']}: {action['reasoning']}",
        outcome="success" if success else "failure",
        meta={"task_id": current_task["id"], "result_summary": str(result)[:200]}
    )
    
    # 9. Update task based on result
    current_task["attempts"] = current_task.get("attempts", 0) + 1
    
    if success and is_task_complete(current_task, result):
        # Task done
        state["tasks"]["active"].remove(current_task)
        state["tasks"]["completed"].append(current_task["id"])
        print(f"✓ Task complete: {current_task['name']}")
    elif current_task["attempts"] >= MAX_FAILURES:
        # Too many failures — mark blocked
        current_task["blocked_reason"] = f"Failed {current_task['attempts']} times"
        print(f"✗ Task blocked: {current_task['name']}")
    
    save_state(state)
```

---

## TL;DR

- Planning has three levels: strategy (embedded in prompts), plan (dynamic task list), task (what to do right now)
- The heartbeat pattern — run, act, sleep — is the simplest reliable agent scheduling method
- Task selection should consider priority, failure history, and time active — not just FIFO queue
- Stuck detection is mandatory: check at every cycle for idle count, repeated failures, and overdue tasks
- When stuck, try replan first; if still stuck after N attempts, escalate to human with specific ask

---

*Next: Chapter 7 — Tool Selection and Chaining*
