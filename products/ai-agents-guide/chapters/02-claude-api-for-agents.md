# Chapter 2: The Claude API for Agents

Most Claude tutorials show you how to build a chatbot. That's fine if you want a chatbot. But agents have different requirements, and the patterns that work well for chatbots actively hurt you in agents.

This chapter covers the Claude API specifically from an agent-builder's perspective — the parts that matter most and the pitfalls that aren't obvious until you're in production.

---

## 2.1 The Messages API: The Right Mental Model

The Claude API is built around a list of messages. Here's the simplest call:

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "What should I do next?"}
    ]
)

print(response.content[0].text)
```

Simple enough. But here's the mental model that matters: **the messages list is not a log — it's the full context Claude uses to decide what to do**.

Every call is stateless from the API's perspective. Claude doesn't remember your previous calls. If you want Claude to know what happened before, you put it in the messages list. If you leave it out, Claude doesn't know.

This is the fundamental tension in agent design: you need Claude to know your history, but context windows are finite and expensive. Managing this tension is a core skill. We'll cover it in depth in Chapter 5.

---

## 2.2 System Prompts That Work for Agents

The system prompt is where you define Claude's role, constraints, and operating context. For chatbots, system prompts tend to be short personality blurbs. For agents, they're operational contracts.

Here's a weak system prompt (chatbot style):

```
You are a helpful research assistant. Help the user with their research tasks.
```

Here's a strong system prompt (agent style):

```python
SYSTEM_PROMPT = """You are an autonomous research agent. You run in a loop every 15 minutes.

IDENTITY:
- You are task-oriented and methodical, not conversational
- You act on your state, not on chat messages (there is no chat)
- You complete tasks, then update your state, then stop

CURRENT STATE:
{state_json}

AVAILABLE TOOLS:
{tool_list}

OPERATING RULES:
1. Always check your state before deciding what to do
2. Complete exactly ONE meaningful action per cycle (don't chain actions without recording)
3. After any action, update your state to reflect what happened
4. If you cannot complete a task, record WHY in state["blockers"] — don't silently fail
5. If you are stuck (same task failing 3+ times), escalate to your human operator

OUTPUT FORMAT:
Respond ONLY with a JSON object containing:
- "action": the tool to call, or "none" if nothing to do
- "params": parameters for the tool
- "reasoning": one sentence explaining why
- "state_update": key-value pairs to update in state after action completes
"""
```

The key differences:
- **Tells Claude its operating context** (runs in a loop, no human chat)
- **Injects current state** (Claude knows what's happening)
- **Defines operating rules** (prevent common failure modes)
- **Specifies output format** (structured JSON, not prose)

Let's look at how to inject state dynamically:

```python
import json

def build_system_prompt(state: dict) -> str:
    return SYSTEM_PROMPT.format(
        state_json=json.dumps(state, indent=2),
        tool_list="\n".join(f"- {t['name']}: {t['description']}" 
                           for t in AVAILABLE_TOOLS)
    )
```

Every cycle, Claude sees the current state. It doesn't need to remember — you tell it.

---

## 2.3 Tool/Function Calling: The Right Structure

Tools are how agents act. Without tools, Claude can only *say* things. With tools, it can *do* things.

Here's how to define a tool:

```python
TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web for information. Use this when you need to find current information about a topic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Be specific — vague queries return poor results."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return. Default 5, max 20.",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "save_to_database",
        "description": "Save a piece of information to the research database. Use after finding something worth keeping.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic this information relates to"
                },
                "content": {
                    "type": "string",
                    "description": "The information to save"
                },
                "source_url": {
                    "type": "string",
                    "description": "URL where this was found, if applicable"
                }
            },
            "required": ["topic", "content"]
        }
    }
]
```

Tool definitions have three critical parts:
1. **name** — used by Claude to call the tool; should be a clear verb phrase
2. **description** — the most important part; this is how Claude decides *when* to use the tool
3. **input_schema** — the parameters Claude must provide; follows JSON Schema format

**The description is everything.** Claude reads descriptions to decide which tool to use. Vague descriptions lead to wrong tool selection. Good descriptions answer: "When should I use this?" and "What does this do exactly?"

Bad description: `"Search for things"`
Good description: `"Search the web for current information about a topic. Use when you need facts, news, prices, or anything that might have changed recently."`

---

## 2.4 Making a Tool Call and Handling the Result

Here's the complete flow for one agent cycle with tool use:

```python
import anthropic
import json

client = anthropic.Anthropic()

def run_agent_cycle(state: dict) -> dict:
    """Run one cycle of the agent loop. Returns updated state."""
    
    # Build the prompt with current state
    messages = [
        {
            "role": "user",
            "content": f"Current state: {json.dumps(state)}. What should you do next?"
        }
    ]
    
    # First call: ask Claude what to do
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system=build_system_prompt(state),
        tools=TOOLS,
        messages=messages
    )
    
    # Check if Claude wants to use a tool
    if response.stop_reason == "tool_use":
        # Extract the tool call
        tool_use_block = next(
            block for block in response.content 
            if block.type == "tool_use"
        )
        
        tool_name = tool_use_block.name
        tool_input = tool_use_block.input
        tool_use_id = tool_use_block.id
        
        print(f"Claude is calling: {tool_name}({tool_input})")
        
        # Execute the tool (your code, not Claude's)
        tool_result = execute_tool(tool_name, tool_input)
        
        # Add Claude's response + tool result to messages
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": json.dumps(tool_result)
                }
            ]
        })
        
        # Second call: ask Claude what it learned from the tool result
        follow_up = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=512,
            system=build_system_prompt(state),
            tools=TOOLS,
            messages=messages
        )
        
        # Extract state updates from Claude's follow-up
        state_updates = extract_state_updates(follow_up.content[0].text)
        state.update(state_updates)
    
    elif response.stop_reason == "end_turn":
        # Claude decided not to use a tool
        # Extract any state updates from its response
        state_updates = extract_state_updates(response.content[0].text)
        state.update(state_updates)
    
    return state


def execute_tool(name: str, params: dict) -> dict:
    """Dispatch tool calls to actual implementations."""
    if name == "web_search":
        return do_web_search(params["query"], params.get("max_results", 5))
    elif name == "save_to_database":
        return do_save(params["topic"], params["content"], params.get("source_url"))
    else:
        return {"error": f"Unknown tool: {name}"}
```

Notice the flow:
1. Call Claude → it returns a tool_use block
2. You execute the actual tool (Claude only *requests* the call, you run it)
3. Send the result back to Claude
4. Claude processes the result and responds

This two-step dance is how all tool use works. Claude decides; you execute; Claude interprets.

**Critical:** Claude requests tool calls. It does not make them. You write the implementation of every tool. If Claude's `web_search` tool doesn't actually do a web search, it will hallucinate results.

---

## 2.5 Context Window Management

The context window is your most constrained resource. Claude Sonnet has a 200K token context, but that doesn't mean you should use it all.

Here's why context bloat hurts:
- **Cost**: longer contexts cost more per call
- **Speed**: longer contexts take longer to process
- **Quality**: very long contexts can cause Claude to miss things near the beginning
- **State drift**: if your messages list keeps growing without pruning, old decisions affect new ones

**Strategy 1: Summarize old context**

Instead of keeping the full history, keep a running summary:

```python
def compress_history(messages: list, keep_last_n: int = 5) -> list:
    """Keep only recent messages; summarize older ones."""
    if len(messages) <= keep_last_n:
        return messages
    
    old_messages = messages[:-keep_last_n]
    recent_messages = messages[-keep_last_n:]
    
    # Summarize old messages
    summary = client.messages.create(
        model="claude-haiku-4-5",  # cheaper model for summarization
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": f"Summarize what happened in these agent actions in 2-3 sentences: {json.dumps(old_messages)}"
        }]
    ).content[0].text
    
    return [
        {"role": "user", "content": f"[Previous context summary]: {summary}"},
        *recent_messages
    ]
```

**Strategy 2: State is your memory, not messages**

Don't use the messages list as memory. Use it only for the current exchange. Put everything important into state, and inject state into the system prompt each cycle. The messages list resets; state persists.

```python
# Bad: accumulating history
messages.append({"role": "assistant", "content": response.content})
messages.append({"role": "user", "content": tool_result})
# messages grows forever

# Better: fresh messages each cycle, state carries history
def build_messages(state: dict) -> list:
    return [
        {
            "role": "user",
            "content": f"Current state: {json.dumps(state)}. What's next?"
        }
    ]
    # fresh each time; history is in state, not messages
```

---

## 2.6 Model Selection for Agents

Not every agent action needs your most powerful model. Smart model selection reduces cost dramatically.

| Task | Recommended Model | Why |
|------|-----------------|-----|
| Planning, complex decisions | claude-sonnet-4-5 | Needs strong reasoning |
| Tool selection in a loop | claude-haiku-4-5 | Fast, cheap, accurate enough |
| Summarization, formatting | claude-haiku-4-5 | Straightforward task |
| Final report generation | claude-sonnet-4-5 | Quality matters |

A practical pattern: use Haiku for the "what to do next" loop, and Sonnet for actions that actually matter.

```python
def decide_next_action(state: dict) -> dict:
    """Use cheap model just to decide what to do."""
    response = client.messages.create(
        model="claude-haiku-4-5",  # fast and cheap
        max_tokens=256,
        messages=[{"role": "user", "content": f"State: {json.dumps(state)}. Next action?"}]
    )
    return parse_action(response.content[0].text)

def execute_and_synthesize(action: dict, result: dict) -> str:
    """Use powerful model when it matters."""
    response = client.messages.create(
        model="claude-sonnet-4-5",  # worth the cost
        max_tokens=2048,
        messages=[{"role": "user", "content": f"Synthesize this research: {json.dumps(result)}"}]
    )
    return response.content[0].text
```

---

## TL;DR

- The messages list is Claude's entire context for each call — it has no memory between calls; you provide history by including it
- Agent system prompts should inject current state, define operating rules, and specify output format — not just describe personality
- Tool descriptions are critical: Claude reads them to decide which tool to use; be specific about *when* and *what*
- Tool execution flow: Claude requests → you run it → you return result → Claude interprets
- Manage context window deliberately: keep messages short and stateless; put history in state (persisted between cycles), not in messages
- Use cheaper/faster models for routine decisions; save stronger models for things that matter

---

*Next: Chapter 3 — Tool Design*
