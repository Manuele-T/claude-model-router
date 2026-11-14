# v3.0 results and discussion (work in progress)

[Back to the README](../README.md) · [v1.0 results](v1-results.md) · [v2.0 results](v2-results.md)

**Work in progress.** v3 has three parts and only Part 1 has run so far, plus two follow-ups (1b and 1c) that gave the comparison setups 5 runs each. The numbers below are final for Part 1, but the conclusions may change once Parts 2 and 3 are in.

**The questions:**

1. **Haiku then an Opus review:** if Haiku alone does a coding task and a fresh Opus session reviews it once, does that get back the care Opus added in v2, at close to Haiku's cost? *(Part 1, with 1b and 1c, done)*
2. **Coverage:** on the 85-page docs check where Opus plus Haiku found the most, how do errors found and cost change with the number of Haiku subagents? *(Part 2, not run yet)*
3. **Cheap model or split:** with the same split, do Opus subagents find clearly more than Haiku subagents, and at what cost? *(Part 3, not run yet)*

Costs are API list prices used as a proxy for subscription usage. Per-run numbers and scoring rules are in [`data/results.md`](../data/results.md).

## Part 1: Haiku does the work, Opus reviews it once

v2 found that on coding tasks every setup produced working code, and what Opus added was care the hidden tests didn't see: a database index when asked for speed, flagging a symptom it couldn't reproduce, a release note, and the third planted bug in a code review. Haiku alone did none of these. (One of these, the flag, turned out not to hold: see [Parts 1b and 1c](#parts-1b-and-1c-five-runs-for-the-other-setups-too).)

So I added one setup: **Haiku alone does the task, then a fresh Opus session is told another session did it, checks the changes and the answer against the task, and fixes anything wrong or missing.** Same four buildbot tasks as v2, prompts and hidden tests unchanged, 5 runs each, 20 runs. The [design was committed before any run](../data/tasks-v13.md), and the answers were scored blind, shuffled together with every v2 answer to the same tasks.

| Mean cost per run | Opus alone | Opus plus Haiku | Haiku alone | **Haiku, then Opus review** |
| --- | --- | --- | --- | --- |
| REST endpoint, fast on millions of builds | $1.16 | $0.93 | $0.14 | **$0.46** |
| Wrong blamelists across branches | $0.79 | $0.43 | $0.01 | **$0.17** |
| Change a default timeout | $0.16 | $0.23 | $0.01 | **$0.13** |
| Review a commit with planted bugs | $0.12 | $0.22 | under $0.01 | **$0.11** |
| **All four** | **$2.23** | **$1.81** | **about $0.17** | **$0.86 (-61%)** |

| Care point | Opus alone | Opus plus Haiku | Haiku alone (v2, then v3 step 1) | **Haiku, then Opus review** |
| --- | --- | --- | --- | --- |
| Index with a migration | 2 of 2 | 2 of 2 | 0 of 2, then 4 of 5 | **5 of 5** |
| Said it couldn't reproduce part of the bug report | 2 of 2 | 2 of 2 | 0 of 2, then 0 of 5 | **0 of 5** |
| Release note | 2 of 2 | 2 of 2 | 0 of 2, then 0 of 5 | **5 of 5** |
| Planted bugs found in the review, of 3 | 3, 3 | 3, 3 | 2, 2, then 3, 2, 2, 2, 3 | **3, 3, 3, 2, 3** |

- **It cost 61% less than Opus alone and 52% less than Opus plus Haiku**, about 5 times Haiku alone. The review is about 85% of the bill.
- **Every run passed every hidden test**, before and after the review. The review broke nothing.
- **The review catches what Haiku leaves out.** It added the release note every time, added the index the one time Haiku skipped it, found the missed bug in 2 of 3 reviews, and fixed a real race condition in one run where two builds finishing at once could make one fail.
- **It doesn't question the problem.** My bug report on one task describes a symptom the planted bug doesn't seem to cause. Every Opus-led run in v2 said it couldn't reproduce that part. Haiku explained it away instead, and all 5 reviews accepted that explanation. *Correction (2026-11-13): Parts 1b and 1c show this isn't about the review. Opus alone and Opus plus Haiku, 5 new runs each, also explained it away every time.*
- **Haiku alone did better than v2 suggested** on the speed index: 4 of 5 this time, against 0 of 2. Two runs per setup was too few.

So on small, well-defined coding tasks, Haiku plus one Opus review got most of Opus's care at about half the cost of Opus plus Haiku. Omissions get caught.

## Parts 1b and 1c: five runs for the other setups too

Part 1 compared 5 runs of the review setup with v2's 2 runs per setup. So I re-ran **Opus plus Haiku** 5 more times on all four tasks (Part 1b), and, after seeing that result, **Opus alone** 5 more times on the blamelist task (Part 1c). Setups, prompts and tests unchanged; [design committed before each part](../data/tasks-v14.md); answers scored blind again.

| Mean cost per run | Opus plus Haiku (5 new runs) | **Haiku, then Opus review** |
| --- | --- | --- |
| REST endpoint | $0.62 | **$0.46** |
| Wrong blamelists | $0.30 | **$0.17** |
| Change a default timeout | $0.23 | **$0.13** |
| Review a commit | $0.19 | **$0.11** |
| **All four** | **$1.34** | **$0.86 (-36%)** |

- **Opus plus Haiku was the more reliable of the two.** Every hidden test passed. It added the index and the release note in all 5 runs and found all 3 planted bugs in all 5 reviews, against 4 of 5 for the review setup.
- **The review setup stayed 36% cheaper.** On these tasks the gap in care was one missed bug in 5 reviews.
- **The "couldn't reproduce" flag depends on the day, not the setup.** All 8 Opus-led runs from 6 November said it. None of the 15 Opus-led runs from 12-13 November did, including 5 runs of Opus alone doing the whole investigation itself. Same Claude Code version, model, code and prompt, though the starting context differed by about 100 tokens (the runs load my global Claude Code setup, which changed slightly in between). So this point no longer counts as evidence for any setup.
- **The cause is still unknown.** Comparing the requests saved in the transcripts, Claude Code's own instructions changed between the two days with the same version number. I put back the one change I could, an instruction to tell the user the plan and give updates, in 5 more runs of Opus alone (Part 1d). None flagged the symptom, so that instruction isn't the cause on its own. What's left is two other changes in Claude Code's instructions, a change on Anthropic's side, or a lucky batch.

**Correction (2026-11-13).** v2 and Part 1 read that flag as care Opus adds, and Part 1 said Opus questioned the report only when it led the investigation. Neither holds with more runs. The [v2 results](v2-results.md) carry a note pointing here.

**Takeaway so far: on small coding tasks, a single Opus review recovers most of what Haiku leaves out, and Opus plus Haiku is a little more reliable for about 1.5x the cost. Two runs per setup weren't enough to see that.**

## Limitations (Part 1)

- Four tasks, chosen because Opus was already known to add something there. This doesn't show what a review catches on tasks nobody has studied.
- The review prompt tells Opus to look for problems, which Opus alone never got. A fair reading is "Opus reviewing Haiku's work", not "Haiku plus a review is as careful as Opus alone".
- v2's comparison setups ran twice per task. Parts 1b and 1c added 5 runs for Opus plus Haiku on all four tasks and for Opus alone on one, but Opus alone still has only 2 runs on the other three.
- Results can shift between days with the same Claude Code version (Parts 1c and 1d), so a batch run on one day may not represent the setup. Later parts spread each setup's runs across days.
- Claude Opus wrote the tests and the criteria, and a fresh Opus session scored the answers. Blinding was imperfect: review answers read like reviews, and some v2 answers mention their helpers.
- Costs use API list prices as a proxy for subscription usage.

## Still to come

- **Part 2:** the 85-page docs check with exactly 1, 4, 8 and 16 Haiku subagents, 5 runs each, scored against a re-verified list of real errors.
- **Part 3:** the same split with Opus subagents, to separate "Haiku is good enough" from "splitting the work is what helps".
