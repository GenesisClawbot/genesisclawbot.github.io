# Chapter 7: Tool Selection and Chaining

Claude is remarkably good at picking the right tool for a task — when you've designed your tools well. This chapter covers the details of tool selection, chaining tools into multi-step workflows, and handling the cases where Claude's judgment needs a nudge.

---

## 7.1 How Claude Selects Tools

When you pass tools to Claude and ask it to complete a task, Claude reads the tool definitions and picks based on:

1. **The tool name** — the first thing Claude sees
2. **The tool description** — the most important factor
3. **The current context** — what the prompt says, what phase you're in, what the task requires
4. **The input schema** — Claude checks if it has the required information to call the tool

This means tool selection quality is mostly about description quality. Here's a concrete example:

```python
# Poor tool definitions — Claude will make bad choices
tools = [
    {"name": "get_data", "description": "Gets data"},
    {"name": "process", "description": "Processes things"},
    {"name": "save", "description": "Saves stuff"},
]

# Strong tool definitions — Claude makes good choices
tools = [
    {
        "name": "fetch_webpage",
        "description": "Download and extract readable text from a public webpage URL. "
                      "Use when you need to read the content of a specific URL. "
                      "NOT for search — this requires you to already have the URL.",
    },
    {
        "name": "search_web",
        "description": "Search the web and return a list of URLs and snippets. "
                      "Use when you need to find URLs for a topic. "
                      "Use BEFORE fetch_webpage when you don't have a specific URL yet.",
    },
    {
        "name": "save_finding",
        "description": "Save an important research finding to the database for later use. "
                      "Use AFTER reading a page, when you've found information worth keeping. "
                      "NOT for temporary notes — only for findings you'll want to reference later.",
    },
]
```

The capitalized NOT and AFTER/BEFORE in descriptions actively guide Claude's tool sequencing. It sounds simple. It works.

---

## 7.2 Steering Tool Selection with the System Prompt

Beyond tool definitions, your system prompt can actively guide which tools to use in which situations:

```python
SYSTEM_PROMPT = """You are a research agent. You have the following tools:

TOOL USAGE RULES:
- Always check saved findings FIRST (query_findings) before fetching new URLs
  This avoids re-researching things you already know
- Use search_web to discover URLs, then fetch_webpage to read them
  Never guess URLs — always search first
- Save findings IMMEDIATELY after reading a useful page
  Don't wait until the end — you may not get another chance

NEVER:
- Fetch a URL without checking existing findings first
- Save the same finding twice
- Use fetch_webpage on a URL you found in search results without actually fetching it
"""
```

This is system-prompt-level constraint specification. Claude follows it reliably.

---

## 7.3 Multi-Step Tool Chains

Some tasks require multiple tool calls in sequence. The challenge: each tool call requires a Claude API call, so you need to decide how much autonomy to give Claude in chaining.

**Option 1: Single-tool-per-cycle** (simplest, most predictable)

Each agent cycle executes exactly one tool call. The agent records the result, updates state, and decides the next action in the next cycle.

```python
def one_tool_cycle(state: dict) -> dict:
    """Execute exactly one tool per cycle."""
    
    # Get action from Claude
    action = decide_action(state)
    
    if action["tool"] == "none":
        return state
    
    # Execute one tool
    result = execute_tool(action["tool"], action["params"])
    
    # Record and return
    mem.log(f"Used {action['tool']}: {action['reasoning']}")
    return update_state_from_result(state, action, result)
```

**Pros:** Maximum debuggability; each action is logged separately; easy to resume after failures.
**Cons:** Slower; multi-step tasks require multiple cycles.

**Option 2: Agentic loop within a cycle** (faster, more powerful)

Let Claude chain multiple tool calls within a single cycle, stopping when it decides the task is done.

```python
def agentic_cycle(state: dict, max_steps: int = 5) -> dict:
    """Allow Claude to chain multiple tool calls per cycle."""
    
    messages = [{"role": "user", "content": build_task_prompt(state)}]
    
    for step in range(max_steps):
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=build_system_prompt(state),
            tools=TOOL_DEFINITIONS,
            messages=messages
        )
        
        if response.stop_reason == "end_turn":
            # Claude finished — no more tools needed
            print(f"Agentic cycle complete in {step + 1} steps")
            break
        
        if response.stop_reason == "tool_use":
            # Execute the tool Claude requested
            tool_use = next(b for b in response.content if b.type == "tool_use")
            result = execute_tool(tool_use.name, tool_use.input)
            
            mem.log(f"[Step {step+1}] {tool_use.name}", 
                   outcome="success" if result.get("success") else "failure",
                   meta={"params": tool_use.input})
            
            # Add Claude's message and tool result to conversation
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result)
                }]
            })
        
        if step == max_steps - 1:
            print(f"WARNING: Reached max steps ({max_steps}) in agentic cycle")
    
    return load_state()

```

**Pros:** Efficient for multi-step tasks; lets Claude handle natural sub-steps.
**Cons:** Harder to debug; failures mid-chain are harder to recover from.

**Recommendation:** Use single-tool-per-cycle until you have a clear need for chaining. Then add it for specific task types, not globally.

---

## 7.4 Verifying Tool Results

Never trust Claude's interpretation of tool results as ground truth. Verify.

```python
def execute_and_verify(tool_name: str, params: dict) -> tuple[dict, bool]:
    """Execute a tool and independently verify the result."""
    result = execute_tool(tool_name, params)
    
    if tool_name == "write_file":
        # Verify the file actually exists and has content
        path = Path("./workspace") / params["path"]
        verified = path.exists() and path.stat().st_size > 0
        if not verified:
            result["success"] = False
            result["error"] = "File write verification failed"
    
    elif tool_name == "save_finding":
        # Verify the finding is in the database
        findings = mem.recall(params["topic"], limit=1)
        verified = len(findings) > 0 and findings[0]["content"] == params["content"]
        if not verified:
            result["success"] = False
            result["error"] = "Database write verification failed"
    
    elif tool_name == "fetch_url":
        # Verify we actually got content
        verified = result.get("success") and len(result.get("text", "")) > 100
        if not verified and result.get("success"):
            result["success"] = False
            result["error"] = "Fetched page has insufficient content"
    
    return result, verified
```

---

## 7.5 Fallback Chains

When a tool fails, have a fallback:

```python
FALLBACK_CHAINS = {
    "search_web": ["fetch_url_directly", "use_cached_results", "mark_blocked"],
    "fetch_webpage": ["retry_with_different_headers", "try_archive_url", "skip_and_continue"],
    "save_finding": ["retry_save", "log_to_file", "raise_error"],
}

def execute_with_fallback(tool_name: str, params: dict) -> dict:
    """Execute a tool with automatic fallback on failure."""
    result = execute_tool(tool_name, params)
    
    if result.get("success"):
        return result
    
    fallbacks = FALLBACK_CHAINS.get(tool_name, [])
    for fallback in fallbacks:
        print(f"Tool {tool_name} failed. Trying fallback: {fallback}")
        
        if fallback == "retry_with_different_headers":
            result = fetch_with_different_headers(params["url"])
        elif fallback == "try_archive_url":
            archive_url = f"https://web.archive.org/web/{params['url']}"
            result = fetch_url(archive_url)
        elif fallback == "skip_and_continue":
            return {"success": True, "skipped": True, "reason": "Could not fetch, continuing"}
        elif fallback == "mark_blocked":
            return {"success": False, "blocked": True, "reason": result.get("error")}
        
        if result.get("success"):
            print(f"Fallback {fallback} succeeded")
            return result
    
    return result  # all fallbacks failed
```

---

## TL;DR

- Tool selection quality depends primarily on description quality: be specific about *when* to use each tool and what it's NOT for
- Use system-prompt-level rules to guide tool sequencing (ALWAYS check X before Y, NEVER do Z)
- Choose single-tool-per-cycle for maximum debuggability; use agentic multi-tool loops only when you have a clear need
- Always verify tool results independently — don't trust Claude's interpretation of success
- Build explicit fallback chains so tool failures have a graceful path rather than crashing the cycle

---

*Next: Chapter 8 — Making Agents Robust*
