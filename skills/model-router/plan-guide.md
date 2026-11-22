# Plan guide (v1, not measured yet)

Read this when the user asks for a coding plan with the model-router skill, or asks for a plan and doesn't name another format. If they give their own format, use theirs.

## Why plans come in chunks

A Haiku session starts cold and sees only its prompt, so each piece of work has to stand on its own. Every piece sent to Haiku costs one Opus handoff and one Opus review, so tiny pieces waste money. A piece with a check it can run is easier for Haiku to finish and for you to review.

## How to write the plan

1. Do the planning yourself (mode 1). Read what you need, then log one line with mode `opus-alone`, model `inline`, reason `plan`.
2. Write the plan as numbered **chunks**. Each chunk is one task for this skill:

   ```
   ## Chunk <n>: <short title>
   - Goal: <one or two lines>
   - Files or area: <paths, modules>
   - Done: <a command or test to run, and what it should show>
   - Depends on: <chunk numbers, or none>
   - Risk: <none, or: security-sensitive, data migration, unclear ask, ...>
   - Mode hint: <1, 2 or 3, and why in a few words>
   - Status: todo
   ```

3. Size the chunks:
   - Group small related steps into one chunk: one handoff and one review instead of several.
   - Give risky steps, and steps that need another chunk's result, a chunk of their own.
   - Keep each chunk to a few steps, so a Haiku session stays short (its requests cost about 5x more once its context passes about 100k tokens).
   - Every chunk gets a **Done** check that can be run. If you can't name one, the chunk is too vague: split it or ask the user.
4. Put shared rules once at the top (project conventions, test command, things never to touch), so each handoff can copy them.
5. If you're in plan mode, show the plan in this format and stop. After the user approves, save it as `PLAN.md` in the project root (or the path they name).
6. Tell the user to commit `PLAN.md` before the first chunk, so mode 3's clean-start check passes. Then: `Use the model-router skill. Do chunk 1 of PLAN.md.`

## How a chunk is run

The skill's own sections cover this ("Do chunk <n> of PLAN.md"): read that chunk and the shared rules, pick the mode (a Risk entry counts as a reason for mode 2), quote the chunk in full in any Haiku prompt, review against its Done check, and in the review set its `Status: done`. The user commits the chunk's code and the updated `PLAN.md` together.
