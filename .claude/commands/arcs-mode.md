---
description: Set how this session works. /arcs-mode <mode> [stakes=] [horizon=] [grug=on|off] [loki=on|off]
argument-hint: quickmove|plan|court [stakes=low|medium|high|critical] [horizon=today|this-week|this-quarter|1-3y] [grug=on] [loki=on]
---

# /arcs-mode

Arguments: $ARGUMENTS

Read the arguments in plain words. Anything missing takes its default. The words are the
same ones the decision_receipt ledger enforces (AGENTS.md, column constraints), so a receipt
written later in this session can copy them as-is.

| Arg | Values | Default | What it changes |
|---|---|---|---|
| mode | `quickmove` · `plan` · `court` | `quickmove` | quickmove: act, few words. plan: plan first, confirm before building. court: argue both sides before deciding. |
| stakes | `low` · `medium` · `high` · `critical` | `low` | high or critical: verify every claim against the repo before stating it, and ask before any outward action. |
| horizon | `today` · `this-week` · `this-quarter` · `1-3y` | `today` | How far ahead a plan should reach. |
| grug | `on` · `off` | `on` for plan and court | Before any plan or new tool, ask the `grug` agent. |
| loki | `on` · `off` | `on` for court | Ask `chief-loki` on the same prompt. If he and grug agree, do the simple thing; where they differ, think there. |

Reply with one line that confirms the settings, e.g.
`mode=court stakes=high horizon=this-week grug=on loki=on`, then wait for the task.

Hold these settings until the session ends or `/arcs-mode` runs again. If an argument isn't in
the table, say which one and ignore it; do not invent a new parameter.
