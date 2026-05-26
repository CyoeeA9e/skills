---
name: waibao
description: Use waibao to outsource coding tasks — only when the user explicitly asks to delegate work. Do NOT use waibao proactively.
---

# waibao — AI 编程助手

## Overview

waibao ("outsourced") is an AI agent for delegating coding tasks. **Only use waibao when the user explicitly asks to outsource a task** — e.g., "帮我把这个外包出去", "outsource this", "用 waibao 做". Do not invoke waibao proactively.

Verify waibao is available:
```bash
python3 --version && test -f "$(dirname "$(realpath "${BASH_SOURCE[0]:-$0}")")/waibao.py" || test -f ./waibao.py
```
If waibao.py is not found, do things by yourself.

## CLI Usage

```
python3 waibao.py [OPTIONS] [PROMPT...]
```

| Flag | Description |
|------|-------------|
| `-t, --task <ID>` | Continue a previously started task by its task ID (e.g., waibao-abc12345) |
| `-c, --continue` | Continue the last session |
| `prompt` | Trailing var-args: the task description (joins with spaces) |

Prompt can also be piped via stdin:
```bash
echo "Add a dark mode toggle to the settings page" | python3 waibao.py

# Writing detailed plan into the file
cat PLAN.md | python3 waibao.py
```

After execution completion, waibao prints a `[TASK: waibao-xxx]` tag at the end. Use this task ID to resume: `python3 waibao.py --task waibao-xxx "<ANSWER>"`.

## Prompt Engineering for waibao

waibao is a plan-following executor. It will:
- Analyze and understand your plan
- Execute each step exactly
- Ask questions when something is ambiguous
- Make suggestions for improvements
- Summarize when done

**Best practices:**
- Provide a detailed, step-by-step implementation plan
- Specify exact file paths, function names, and expected behaviors
- Include verification steps (how to test/run after each step)
- Be explicit about constraints (don't touch X, must use Y pattern)
- The more detailed the plan, the less the agent will need to ask

**Example prompt:**
```
Implement a rate limiter middleware for the API server.

Plan:
1. Add `tokio` and `governor` crates to Cargo.toml
2. Create src/rate_limiter.rs with a RateLimiter struct
3. Add a middleware layer in src/main.rs
4. Write tests in src/rate_limiter.rs
5. Run `cargo test` to verify
6. Run `cargo build` to ensure compilation
```

## When to Use waibao

**Only when the user explicitly asks to outsource a task.** waibao is not the default tool for coding — only invoke it when the user says they want to delegate work to waibao.

For all other coding tasks, use direct tools (`bash`, `read`, `edit`, etc.) or opencode's built-in agents yourself. Do NOT route routine coding work through waibao unless explicitly requested.

## Interacting with waibao

During task execution, waibao may:

- **Ask clarifying questions**: When the task description is ambiguous, waibao will ask questions to clarify the intent. Always answer these questions directly to keep the task moving. Use the task ID printed as `[TASK: waibao-xxx]` to respond: `python3 waibao.py --task waibao-xxx "<ANSWER>"`.
- **Make suggestions**: waibao may propose alternative approaches, improvements, or optimizations. Carefully evaluate each suggestion — it may be insightful or it may be wrong. If a suggestion is incorrect, correct it immediately and clearly explain why. Use the task ID to respond: `python3 waibao.py --task waibao-xxx "<CORRECTION>"`.
