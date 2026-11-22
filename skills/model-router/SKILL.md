---
name: model-router
description: Pick how to run a task, Opus alone, Opus with Haiku helpers, or a separate Haiku session followed by one Opus review (for that mode it hands the user a ready-to-paste Haiku command, then reviews Haiku's work when it's done), and log the choice. Use at the start of any coding, reading or review task bigger than a quick fix, and always before spawning any Agent.
---

# Model Router

You are Opus. Before doing the task, pick one of three modes, say which one and why in one line, log it, then follow that mode. These rules come from benchmark runs (v1 to v3 in this skill's repo), not from guesses about which model is "good enough".

## 1. Overrides first

- `no routing` or `don't delegate`: mode 1. Do it all yourself and log nothing.
- `haiku only`: mode 3.
- `use haiku`, `use sonnet` or `use opus`: mode 2, and every helper uses that model. Log the reason as `user override`.
- `do it here` (after a mode 3 answer): mode 2 on the same task.
- `Follow <handoff folder>/review-prompt.md`: the mode 3 review step (end of section 5).

## 2. Pick the mode

Go down this list and stop at the first match.

1. **A big reading or review job: mode 2.** The result is a report, not a code change: checking docs against code, auditing many files, summarising a whole package, reviewing a large change. Anything where you would otherwise read more than about 3,000 lines yourself. A coding task in a big codebase is not this; it goes to rule 3.
2. **A small job: mode 1.** A quick fix whose place you already know, a question answerable from a few files, a single small edit, or anything a short script can answer (counting, listing, searching). Write the script instead of reading file by file.
3. **A coding task (a feature, a bug to find and fix, a change with tests): mode 3**, unless one of these holds, then mode 2:
   - the user wants to stay in this session, or said `do it here`;
   - speed matters more than cost;
   - every case has to be covered (a review where missing one bug is costly, security-sensitive code);
   - what the user wants is unclear and you'd have to ask before anyone could write a clear brief. (An unknown cause is fine: finding the cause of a bug is a normal Haiku task.)
4. **Unsure: mode 2.**

State it in one line before your first tool call, and repeat it as the first line of your final answer, for example: `Mode 2 (Opus plus Haiku helpers): 85 doc pages to check against the code.`

## 3. Mode 1: Opus alone

Do the work yourself. No subagents. Log one line with model `inline`.

## 4. Mode 2: Opus plus Haiku helpers

You plan, split, brief and merge. Haiku helpers do the reading. Delegation is expected in this mode, not optional.

**Split first, with a fixed split.** Before spawning anything:

1. List every piece of material (files, pages, modules) and count lines (`wc -l`).
2. Number of helpers = total lines ÷ 400, rounded up, at most 16. Count only the material being checked or summarised, not the code it's checked against.
3. Cut the material into that many groups of about equal line count, in path order, so related pages stay together. No group over 1,500 lines.
4. If 16 groups of 1,500 lines can't hold it (over 24,000 lines), stop and tell the user: that's bigger than anything tested. Offer to narrow the scope, or to run more than 16 helpers in batches of 16, and wait for their answer.
5. Write the groups down, then spawn exactly one helper per group. Don't change the count after you start.

**Model:** every helper uses `model: "haiku"` unless the user forced another. Don't use Sonnet or Opus helpers for reading. An Opus helper is only for a subtask that needs Opus-level judgement in a fresh, separate context. Always pass `model` explicitly on every Agent call.

**Brief each helper completely.** A helper sees only its prompt. Put in it:

- its exact files or pages, and nothing else to read beyond what it must check against;
- what to check or do, and what you already know (paths, names, facts you found), so it doesn't re-read what you read;
- the exact format to return (for a review: file, line, the claim, what the code says, where in the code);
- for reading jobs: report only, change nothing.

Start independent helpers in parallel, several Agent calls in one message.

**Coding in mode 2:** you read enough to plan, give helpers scoped pieces (find where something lives, write one function with its test, update one doc page), then review the whole diff yourself, run the tests, and add what helpers tend to skip: docs, a release note if the project keeps them, a migration or index when speed was asked for.

**Merge and check:**

- Read every result. Check each finding against the code before keeping it, and drop what you can't confirm. Many small helpers find more but also make more false claims.
- If a helper's result is wrong, empty or clearly weak, do that piece yourself. Log it with reason `escalated: <what went wrong>`. Don't loop and don't step through Sonnet.

**The final answer is the whole report.** Give the complete, merged result in your last message, in one piece. Never end with only an addendum, a correction or a note about one group: if you need to add something after writing the report, write the whole report again with it included.

## 5. Mode 3: Haiku only, then one Opus review

A skill can't switch this session to Haiku, so in this mode you don't do the task. You save two prompts for the user, tell them exactly what to run, wait in the background for Haiku's answer, then review it.

1. Read only enough to brief well: where the relevant code is, how tests run, project conventions. Don't start the work.
2. Get the starting point and make the handoff folder, in one Bash call:

   ```bash
   git rev-parse HEAD && git status --short && pwd && d=~/.claude/model-router/handoff/$(basename "$PWD")-$(date -u +%Y%m%dT%H%M%SZ) && mkdir -p "$d" && echo "$d"
   ```

   If the folder isn't a git repo or has uncommitted changes, say so and suggest committing first, so the review can compare against a clean start. Use the printed folder path, written out in full, everywhere below as `<dir>`, and the printed working directory as `<project>`.
3. Write the **Haiku prompt**. It must be complete, since that session starts cold and sees only this prompt and the project's CLAUDE.md:
   - the user's task, word for word;
   - what you already found: files, functions, conventions, how to run the tests;
   - what done looks like: working code, tests that pass, docs and a release note if the project keeps them;
   - "Leave your changes uncommitted. When you're done, write your final answer (what you changed, how you tested it, and anything you didn't do) to `<dir>/haiku-answer.md`, then show the same text as your last message."
4. Write the **Opus review prompt**:

   ```
   Another session was given the task below and has finished working on it in <project>. It started from commit <starting commit>. Its final answer is in <dir>/haiku-answer.md; if that file is missing, review from the diff alone. Review its work: check its changes against that commit (git status, git diff <starting commit>) and its final answer, against what the task asks. Fix anything that is wrong or missing, then give your own final answer to the task.

   Task:
   <the user's task, word for word>
   ```

5. Save both in `<dir>`, so a script can pick them up later:

   ```bash
   cat > "<dir>/haiku-prompt.md" <<'ROUTER_PROMPT_END'
   <Haiku prompt>
   ROUTER_PROMPT_END
   cat > "<dir>/review-prompt.md" <<'ROUTER_PROMPT_END'
   <Opus review prompt>
   ROUTER_PROMPT_END
   ls "<dir>"
   ```

6. Show the user exactly this, filled in, and nothing more. Use full paths, never `~` shortened or `...`, and put each command in its own fenced block so it can be copied in one go. For the Haiku prompt block, use a fence longer than any backtick run inside the prompt (for example four or five backticks), so the whole prompt copies as one piece:

   ````
   <the mode line>

   Haiku will: <2 to 4 short lines on what the Haiku prompt asks for>. Full prompts: <dir>

   **Step 1. Open a second terminal** (in the desktop app, a new Terminal tab). Keep this session open. Run:

   ```bash
   cd <project> && claude --model haiku "$(cat <dir>/haiku-prompt.md)"
   ```

   Check the banner says Haiku. When it asks to write `haiku-answer.md` in the handoff folder, say yes. When it has finished, type `/exit`. (This command always starts a fresh Haiku session, so there's nothing to clear.)

   **Or, in an open Haiku chat** (for example a desktop app session with Haiku picked, in <project>): if the chat isn't brand new, first type `/clear` on its own and press Enter. Then copy everything in the block below and paste it as a separate message:

   <the full Haiku prompt, exactly as saved in haiku-prompt.md, in one fenced block>

   **Step 2. Nothing to do here.** I'm waiting for Haiku's answer (up to 60 minutes) and will start the review by myself when it's saved. Keep this session open. If I haven't started after Haiku finishes, paste this line:

   ```
   Follow <dir>/review-prompt.md
   ```

   Both steps run on your normal Claude Code login. A script that runs the Haiku step for you would bill an API key instead.

   Say "do it here" to run it in this session with Haiku helpers instead.
   ````

7. Start the wait, as a **background** Bash command (`run_in_background`), so this session stays free and you're woken up when it ends:

   ```bash
   for i in $(seq 720); do [ -s "<dir>/haiku-answer.md" ] && sleep 5 && echo "haiku-answer ready" && exit 0; sleep 5; done; echo "no haiku-answer after 60 minutes"; exit 1
   ```

   Then end your turn. Don't do the task yourself unless the user says `do it here`.
8. When the wait ends: if it printed `haiku-answer ready`, do the review step below right away, without being asked. If it timed out, say so in one line and remind the user of the `Follow <dir>/review-prompt.md` line.

**The review step.** When your background wait reports `haiku-answer ready`, or the user says `Follow <dir>/review-prompt.md` (or pastes a review prompt), that's the second half of mode 3, not a new task: read that file and do what it says yourself. Don't pick a mode again, don't spawn helpers, don't write a new handoff. Log one line with mode `haiku-only`, model `review`.

## 6. Log every decision

Before each Agent call, and once per task for modes 1 and 3, append one line with Bash:

```bash
mkdir -p ~/.claude/model-router && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | $(basename "$PWD") | <mode> | <model> | <short task description> | <reason>" >> ~/.claude/model-router/routing.log
```

- `<mode>` is exactly `opus-alone`, `opus+haiku` or `haiku-only`.
- `<model>` is `inline` for mode 1, `haiku-session` for the mode 3 handoff, `review` for the mode 3 review, and the helper's model (`haiku`, `sonnet` or `opus`) for each helper in mode 2.
- `<short task description>` matches the Agent call's `description` field word for word.
- `<reason>` is a few words: `small fix`, `85 pages, group 3 of 16`, `coding task`, `user override`, `escalated: empty result`.
- Don't use the `|` character inside the description or reason.

## 7. Never

- Never change `CLAUDE_CODE_SUBAGENT_MODEL` or any settings file. That variable silently overrides every helper's model.
- Never write these rules into the project's CLAUDE.md.
- Never start a `claude` session yourself in mode 3. The user runs it.
- Never skip the log line.
