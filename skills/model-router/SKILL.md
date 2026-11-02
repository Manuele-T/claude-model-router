---
name: model-router
description: Route every subagent to the cheapest model that can do the job (Haiku, Sonnet or Opus) and log each routing decision. Use whenever a task can be split into subtasks or would benefit from delegating work to subagents, before spawning any Agent.
---

# Model Router

You are the orchestrator. Your job is to plan, delegate and review — not to do bulk work yourself. Send each subtask to the cheapest model that can do it well, and log every decision.

## 1. Decide whether to delegate

- **Stay inline** (no subagent) if the whole task is tiny: a one-line fix, a direct question you can answer from what is already in context, or a single small edit.
- **Delegate** everything else. Break the task into subtasks first, then route each subtask separately.

## 2. Pick the model for each subtask

Default to **Haiku**. Move up a tier only when you can name the reason.

| Tier | Use for | Examples |
|---|---|---|
| `haiku` | Mechanical work: finding, listing, counting, formatting. No judgment about code. | Find files that mention X; list a folder's structure; grep for a string; check whether a function exists; reformat a list; summarise a short, simple file |
| `sonnet` | Anything that needs understanding or writing code or prose. | Implement a function; refactor; write or fix tests; debug an error; explain how a module works; review a diff |
| `opus` | Hard reasoning where a mistake is expensive. | Architecture or design decisions; security-sensitive changes; ambiguous requirements; tricky concurrency or data-loss risks |

Rules of thumb:
- Any subtask where the agent must **understand code and decide something** about it goes to `sonnet` or higher.
- When a subtask could fit either of two tiers, choose the **lower** tier.
- Prefer handling `opus`-level reasoning yourself (you are the orchestrator) rather than spawning an Opus subagent, unless the work needs a fresh, isolated context.
- Run independent subtasks in parallel: launch several Agent calls in one message.

Always pass the model explicitly in the Agent call, for example:

```
Agent(subagent_type: "Explore", model: "haiku", description: "Find config files", prompt: "...")
Agent(subagent_type: "general-purpose", model: "sonnet", description: "Implement parser", prompt: "...")
```

Give every subagent a self-contained prompt: it cannot see this conversation. Include file paths, the goal, constraints and the exact format you want back.

## 3. Log every decision

Immediately before each Agent call, append one line to the routing log with Bash:

```bash
mkdir -p ~/.claude/model-router && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | $(basename "$PWD") | <model> | <short task description> | <reason>" >> ~/.claude/model-router/routing.log
```

- `<model>` is exactly `haiku`, `sonnet` or `opus`.
- `<short task description>` must match the Agent call's `description` field word for word, so the verifier can pair them.
- `<reason>` is a few words, e.g. `mechanical lookup`, `needs code comprehension`, `security-sensitive`.
- Do not use the `|` character inside the description or reason.

Also log tasks you keep inline, with model `inline`:

```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | $(basename "$PWD") | inline | <task> | <reason>" >> ~/.claude/model-router/routing.log
```

## 4. Review results and escalate on failure

When a subagent returns:
- Check the result actually answers the subtask. Do not pass along output you have not read.
- If a `haiku` result is wrong, empty or clearly low quality, **re-run the same subtask once on `sonnet`** and log it with reason `escalated: <what went wrong>`.
- If a `sonnet` result fails, handle it yourself or ask the user. Do not loop.

## 5. User overrides

- "no routing" or "don't delegate" → do everything inline, log nothing.
- "use haiku" / "use sonnet" / "use opus" → every subagent in this task uses the named model; log the reason as `user override`.

## 6. Never

- Never change `CLAUDE_CODE_SUBAGENT_MODEL` or any settings file.
- Never write routing rules into the project's CLAUDE.md.
- Never skip the log line — the experiment depends on it.
