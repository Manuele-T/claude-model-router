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
