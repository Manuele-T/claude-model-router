# Task set v15: splitting a big docs check (v3 Parts 2 and 3)

v2's biggest review task, 43, asks for a check of 85 doc pages (about 6,000 lines) against buildbot's code. There, Opus orchestrator + Haiku found over 60% more real errors than Opus alone at half the cost, and about 30% more than Haiku alone at the same price. The skill chose how many Haiku subagents to use (6 or 7). That leaves two questions:

- **Part 2, coverage:** how do real errors found and cost change with the number of Haiku subagents, from 1 to 16? And does Haiku + Opus checker (arm R from Part 1) find as much?
- **Part 3, cheap model or split:** with the same split, do Opus subagents find clearly more than Haiku subagents, and at what cost? This separates "Haiku is good enough" from "splitting the work is what helps".

This file is committed before any Part 2 run. Part 3's arm depends on Part 2's result through the rule below, which is fixed now.

## Setup

- **Task 43, prompt unchanged** from `data/tasks-v5.md`. Source: the same one-commit copy of buildbot at `c5cdcf3` with planted doc errors (`SRC=~/bench-src/buildbot-planted`), cloned fresh per run.
- **Fixed page groups.** The 85 pages, sorted by path, are cut into N contiguous groups of about equal line count, for N = 1, 4, 8 and 16. The groups are in `data/splits-v15.txt`, so every run of an arm gets the same groups. Group sizes are 1,450 to 1,523 lines for N = 4, 696 to 810 for N = 8 and 320 to 473 for N = 16.
- **Split wording**, added by `scripts/run_bench.sh` before the task prompt (N = 4 shown; N = 1 says "exactly 1 Haiku subagent for the group of pages below"):

  > Use the model-router skill. use haiku. Split this task by page: use exactly 4 Haiku subagents, one for each group of pages below, and no other subagents. Give each subagent only its own group's pages: it checks their claims against the code and reports each claim that is wrong or out of date, with the doc file and line. Then check and merge their findings yourself and give the final report.
  > Group 1: (paths) ...
  >
  > Task: (the task 43 prompt)

- Headless, medium effort, `--permission-mode auto`, Opus as the main model, fresh clone. Claude Code version recorded per run, as before. The installed skill is the same copy every v2 C run used, checked unchanged before the first run.

### Part 2 arms

| Arm | What runs | Runs |
| --- | --- | --- |
| C1, C4, C8, C16 | Opus orchestrator + Haiku with the split wording: exactly 1, 4, 8 or 16 Haiku subagents | 5 each |
| R | Haiku + Opus checker, unchanged from Part 1: Haiku alone does task 43, then a fresh Opus session gets the fixed review prompt | 5 |

25 runs, tags `r1` to `r5` (run names `t43-C4r1`, `t43-Rr1` and so on).

### Part 3 arm

| Arm | What runs | Runs |
| --- | --- | --- |
| O<N> | The same split and groups with `use opus`: N Opus subagents | 5 |

**Choosing N, fixed now:** N is the Part 2 count with the most real errors found per dollar (means over 5 runs, on the re-verified list below). If the next count is within 10% on that measure, take the one that found more real errors in total. If no compliant runs exist for a count, it can't be chosen. If every count is unusable, Part 3 doesn't run and I ask again.

## Order: spread across days

Part 1c showed that a batch of runs on one day may not represent a setup. So:

- Runs go in rounds. Each round runs C1, C4, C8, C16 and R once, in an order rotated by one place each round (round 1: C1, C4, C8, C16, R; round 2: C4, C8, C16, R, C1; and so on).
- **No more than 2 rounds per calendar day,** so Part 2 spans at least 3 days.
- Part 3's 5 runs go on at least 2 different days.
- One run at a time, with a short report after each.

## Compliance

- Every run is checked with `scripts/verify_models.py`: the number of subagents, and the model each one actually ran on.
- **A run counts in its arm only if it used exactly N subagents, all on the named tier.** Other runs are reported with their count and scored, but kept out of the arm's means.
- If 2 or more of the first 10 Part 2 runs miss the count, I stop and ask before going on. Part 3 uses the same rule on its first 2 runs.

## How runs are scored

- **A re-verified list of real errors.** v3 scores overall performance, not agreement with v2's list of 92. Every claim from every v3 run is checked against the unmodified buildbot checkout at the same commit, and new real errors are added. The final list scores every v3 run, and v2's task 43 runs are re-scored against it too, so all setups are compared on the same denominator. v2's published scores stay as published; the re-scored numbers are reported separately, with a label.
- **Judged blind:** claims are judged with run and setup names removed, in batches, by a fresh session. I spot-check its verdicts against the code.
- **Planted errors** (20 on this task's pages) are scored but not expected to separate setups: every v2 run found all of them. The list stays private.
- **Per run:** real errors found, planted errors found, claims confirmed false, citations past the end of a file, cost, cost per real error, and wall time from transcript timestamps.
- **Cost:** from the checker, an API-price proxy for subscription usage. Haiku past 100k tokens in one request costs more, so C1 and R may cost more than their size suggests.

## Weaknesses

- One task. The groups cut pages by line count, not by topic, so a subagent may get unrelated pages, and a cross-page error may fall between two groups.
- The split wording is mine. Telling Opus how to split is a different setup from v2's C, where the skill chose. v2's C stays a comparison point (2 runs), not a replacement.
- R's step 1 may leave a long report in its scratchpad instead of its final answer. The review then sees only what the final answer says or points to, as in Part 1.
- C1 asks one Haiku subagent to read every page, which may run out of room or hit the higher Haiku price. That's a result too, but it may cost more than expected.
- Judging over 1,000 claims takes its own sessions, and the judge is Claude Opus, as are the setups being judged.
- **Safety:** every run is on a buildbot copy. None touches the small private project, network services, Docker, package installs or `sudo`. Commands are audited after each part.

## Cost estimate

About $1.50-2.50 per C run (more at C1 and C16) and $2-4 per R run: roughly $50-70 for Part 2. O<N> may be $8 or more per run: about $40-50 for Part 3.

## Files

- `data/splits-v15.txt`: the page groups.
- `scripts/run_bench.sh`: arms `C<N>` and `O<N>`, which build the split wording from that file.
- Private run helper, `data/private/v15_one_run.sh`; its hash is below.

```
b9fa53ec6ae501cce0e7478c8cd7748368f46214bb74cf115078225c0b26641f  v15_one_run.sh
```
