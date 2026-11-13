# Task set v14: Opus orchestrator + Haiku, five more runs on the Part 1 tasks

Part 1 (`data/tasks-v13.md`) tested **Haiku + Opus checker** (arm R): Haiku alone does the task, then one fresh Opus session checks it. It got most of the care Opus added in v2 at about half the cost of **Opus orchestrator + Haiku** (arm C). But C ran only twice per task in v2, so that comparison is rough. This part runs C five more times on the same four tasks, so the two setups can be compared run for run.

**This part was added after Part 1's results were seen,** and the Part 1 design didn't plan it. This file is committed before any of its runs. Nothing about C, the tasks, the prompts, the hidden tests or the scoring changes from v2 and Part 1. The private files and their hashes are the ones listed in `data/tasks-v13.md`, plus the run helper below.

## Setup

- **Arm C, unchanged from v2:** Opus is the main model, and the prompt starts with `Use the model-router skill. use haiku.`, so every subagent runs on Haiku while Opus plans, briefs and checks. The skill that runs is the same installed copy every v2 C run used. It's checked to be unchanged before the first run.
- **Tasks 56, 57, 65, 78**, with the same sources as Part 1.
- **5 runs per task, tags `r3` to `r7`** (v2's two runs keep `r1` and `r2`). 20 runs, interleaved: 56, 57, 65, 78 for `r3`, then the same order for `r4` and so on.
- Headless, medium effort, `--permission-mode auto`, fresh clone, Claude Code 2.1.317 (the version v2 and Part 1 used).
- Every run is checked with `scripts/verify_models.py` for the number of subagents and the model each one actually ran on. A run with no subagents is reported, and is still counted as C, since that's what the setup did.

## How runs are scored

- **As in Part 1:** hidden tests passed of total (56 reports both the official and the corrected test), the whole buildbot unit suite, and each task's care point: 56 from the diff (index with a migration), 65 by its care test, 57 and 78 from the final answer, against the criteria already fixed in v2's private files.
- **Blind:** the answers to 57 and 78 are shuffled together with Part 1's R answers and the v2 answers to the same tasks, with setup names removed, and scored by a fresh session. The new verdicts on the older answers are compared with their earlier scores, as a consistency check.
- **Cost:** from the same checker, an API-price proxy for subscription usage.
- **Reported:** C with these 5 runs, and with v2's two added (7 runs), both stated.

## Weaknesses

- Added after seeing Part 1's results, so the question was picked knowing where R was weak (task 57).
- The skill chooses how many subagents to use, which varied in v2 (1 or 2 per run on these tasks). That's part of the setup, not controlled.
- The same Opus-written tests, criteria and blind scoring as Part 1, with the same limits.
- **Safety:** all four tasks are on buildbot copies. None touches the small private project, network services, Docker, package installs or `sudo`. Commands are audited after the runs.

## Private file hashes (SHA-256)

As in `data/tasks-v13.md`, plus:

```
080dce133dc3aa9cb0a1baaf9c1d2c3753269b0ae306cba6760bbc8c4b59b129  v14_one_run.sh
```

## Part 1c: Opus alone, five more runs on task 57 (added 2026-11-13, after Part 1b)

Part 1b's blind scores changed a v2 finding. In v2, all 8 Opus-led runs on task 57 said they couldn't reproduce the "missing names" part of the bug report. In Part 1b, Opus orchestrator + Haiku did it in 0 of 5 new runs. In each of those runs a Haiku helper searched the code and Opus accepted its explanation. Opus alone also ran only twice on 57 in v2, so this part checks whether Opus doing the investigation itself flags the symptom reliably.

**Added after Part 1b's results were seen.** Committed before any of its runs.

- **Arm F, unchanged from v2** (Opus alone: no prefix, Agent and Skill blocked). Task 57 only, same source, prompt, hidden test and criteria. 5 runs, tags `r3` to `r7`. Same Claude Code version and settings as Part 1b.
- **Scoring:** the 5 answers are shuffled with the other 27 answers to 57, labels removed, and scored blind by a fresh session against the same criteria. Hidden test and suite as before.
- **Weakness:** the question was picked knowing the result it might overturn.

The run helper gained an optional arm argument for this part (`v14_one_run.sh TASK TAG [ARM]`, with F allowed only for task 57). Part 1b ran with the version whose hash is listed above. The new version:

```
0fc29ee2184d10add2d165d75bd7d0bd2ac6f09c337538d31822a0972b33ab76  v14_one_run.sh (Part 1c)
```

## Part 1d: does one dropped instruction explain the 57 flip? (added 2026-11-13, after Part 1c)

Part 1c's blind scores: Opus alone flagged the "missing names" part in 0 of 5 new runs. Across all runs of 57, every Opus-led run from 2026-11-06 flagged it (8 of 8) and none from 2026-11-12 and 13 did (0 of 15), with the same Claude Code version (2.1.317), model ID, source commit and prompt.

Claude Code records each API request in its transcripts, so I compared the first request of the v2 F runs with the Part 1c ones. Apart from paths, dates and IDs, five things differ:

1. **Removed from Claude Code's system prompt:** "Before you start, tell the user in a sentence or two what you plan to do. While you work, give the user a short update alongside your next tool call whenever you start a major new part of the work, change your plan, or launch something slow."
2. **Removed from the Bash tool's description:** a line telling the model to avoid `cat`, `head`, `tail`, `sed`, `awk` and `echo` in favour of the dedicated tools.
3. **Added to the first message:** a paragraph saying that in auto mode the model may do much of its work through Bash.
4. **Changed in my own global rules:** two lines of a style rule for social media posts, unrelated to coding.
5. **Minor:** a kernel version and two more deferred tool names.

1 to 3 come from Claude Code itself and changed without a version change. I can only control 1 cleanly.

- **Arm G:** arm F plus `--append-system-prompt` with the removed instruction, word for word. It lands at the end of the same system-prompt block it used to sit in, one paragraph from its old position (checked on a one-line Haiku run before this design was committed). Everything else is as in Part 1c.
- **Task 57 only, 5 runs, tags `r3` to `r7`.** Same source, prompt, hidden test and criteria.
- **Scoring:** the 5 answers are shuffled with the 32 earlier answers to 57, labels removed, and scored blind by a fresh session against the same criteria.
- **Reading the result, fixed now:** 3 or more of 5 flags means the instruction plausibly matters. 0 or 1 means it doesn't explain the flip on its own, and the cause stays open (differences 2 and 3 can't be undone from the command line). 2 of 5 is inconclusive.
- **Weaknesses:** a change on the service side can't be ruled out. Differences 2 to 5 stay as they are now. 5 runs can only show a large effect.

`scripts/run_bench.sh` gained arm G, and the run helper accepts G for task 57 only. New hashes:

```
d3716f15a58cb7647fbbe1a25b1f6192f9caf3adbf6c36846b76dd0483d6cfb1  v14_one_run.sh (Part 1d)
```
