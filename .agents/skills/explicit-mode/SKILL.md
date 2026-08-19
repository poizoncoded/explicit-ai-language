---
name: explicit-mode
description: Use when the user enters $explicit-mode or !explicit with on, off, or status to control explicit Russian response mode for the current task.
---

# Explicit Mode

Maintain a conversational on/off flag for explicit Russian response styling in the current task only. A fresh task starts with the mode off.

## Commands

Treat these canonical invocations and textual aliases identically:

```text
$explicit-mode on
$explicit-mode off
$explicit-mode status
!explicit on
!explicit off
!explicit status
```

Handle one command at a time:

- `on`: set the current-task flag to on and return exactly `explicit mode: on`.
- `off`: set the current-task flag to off and return exactly `explicit mode: off`.
- `status`: do not change the flag; return exactly `explicit mode: on` or `explicit mode: off`.
- Any missing, extra, or invalid argument: do not change the flag; return exactly `usage: $explicit-mode on|off|status`.

All command responses are neutral. Do not add profanity, explanations, Markdown, or punctuation.

## State Rules

- Keep state only in the active conversation/task context.
- Never write state to files, repository configuration, Codex configuration, memory, goals, environment variables, external services, or tool state.
- Never infer state from another task or conversation.
- Explicit `off` suppresses `rewriting-explicitly` and every style layer until a later `on` in the same task.
- Explicit `on` permits the orchestrator on later Russian responses; it does not rewrite the command acknowledgement itself.
- Direct invocation of `rewriting-explicitly` turns the mode on for the current task unless `off` was issued later.
- A status query in a fresh task returns exactly `explicit mode: off`.

Do not claim or implement custom slash-command support. `$explicit-mode` is the canonical skill invocation.
