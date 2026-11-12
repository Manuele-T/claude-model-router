# Task set v13: Haiku does the work, Opus reviews it once

v2 found that on coding tasks every setup produced working code, and that what Opus added was care the hidden tests didn't see: a database index on task 56, flagging a symptom it couldn't reproduce on 57, a release note on 65 and the third planted bug in the review on 78. Haiku alone did none of these, at a small fraction of the cost. This part asks whether one Opus review at the end gets that care back while keeping most of Haiku's saving.

This file is committed before any run. No new tasks are written: the four tasks, prompts, sources and hidden tests are the ones v2 used, unchanged. Their private files stay private, and their SHA-256 hashes, which match the ones published in `data/tasks-v8.md`, `tasks-v11.md` and `tasks-v12.md`, are listed below.

## Setup

One new arm, **R (Haiku, then an Opus review)**, run by `scripts/run_bench.sh <NN> R <tag>`:

1. **Step 1 is exactly arm H:** Haiku as the main model, no prefix, Agent and Skill blocked. Its changes are saved as a patch, and its final answer is kept.
2. **Step 2 is a fresh Opus session** in the same clone, Agent and Skill blocked, given this prompt and nothing else:

```
Another session was given the task below and has finished working on it in this directory. It started from commit <starting commit>. Review its work: check its changes against that commit (git status, git diff <starting commit>) and its final answer, against what the task asks. Fix anything that is wrong or missing, then give your own final answer to the task.

Task:
<the task's prompt, unchanged>

The other session's final answer:
<step 1's final answer>
```

Both steps: headless, medium effort, `--permission-mode auto`, fresh clone, Claude Code 2.1.317 (the version v2 used). 4 tasks × 5 runs (`r1` to `r5`) = 20 runs, interleaved: 56, 57, 65, 78 for `r1`, then the same order for `r2` and so on.

## Tasks

| # | Task (paraphrased, from v2) | Care point | v2 results on the care point |
| --- | --- | --- | --- |
| 56 | Add a REST endpoint counting finished builds per result for one builder, fast on millions of builds, with tests (buildbot at `c5cdcf3`) | Adds a database index with a migration | Opus alone 2 of 2, Opus plus Haiku 2 of 2, Sonnet alone 2 of 2, Haiku alone 0 of 2 |
| 57 | Find and fix the cause of wrong blamelists across branches (one-commit copy with one planted bug) | Says the "missing names" part of the report couldn't be reproduced | Opus alone 2 of 2, Opus plus Haiku 2 of 2, Sonnet alone 0 of 2, Haiku alone 0 of 2 |
| 65 | Change one build step's default timeout (buildbot at `c5cdcf3`) | Updates the docs and adds a release note | Release note: Opus alone 2 of 2, Opus plus Haiku 2 of 2, Sonnet alone 0 of 2, Haiku alone 0 of 2 |
| 78 | Review a commit with three planted bugs and two things that only look wrong (one-commit copy) | Planted bugs found, of 3, and false alarms on the two decoys | Bugs: Opus alone 3, 3; Opus plus Haiku 3, 3; Sonnet alone 3, 2; Haiku alone 2, 2. No false alarms in any run |

## How runs are scored

- **Final state** (after step 2): hidden tests reported as passed of total (56 reports both the official test and the corrected `test_hidden_t56b.py`, as in v2), the whole buildbot unit suite, and the care point.
- **Step 1 on its own:** step 1's patch is applied to a fresh clone and scored the same way, minus the suite. Since step 1 is exactly arm H, these also count as 5 more Haiku-alone runs per task, reported separately from v2's two.
- **Care points:** 65 by its existing care test. 56 from the diff (index plus migration). 57 and 78 from the final answer, and for step 1 from step 1's answer, using the criteria already fixed in v2's private files. **Answers are scored blind:** setup and step names removed, order shuffled.
- **Cost:** both steps added together, from the same checker (`scripts/verify_models.py`), and the review step's share of it. Costs are an API-price proxy for subscription usage.
- **What the review did:** for each run, whether step 2 changed anything, what it added or fixed, and whether it broke anything that passed after step 1.
- **Compared with** v2's H, F, C and S runs on the same tasks (two runs each). The headline comparison is R against F (Opus alone) on cost and against H on care.

## Rules and known weaknesses

- No task, prompt, test or scoring change after the first run. If the review prompt turns out badly worded, it stays as it is for all 20 runs and the problem is reported.
- **The review prompt tells Opus another session did the work and asks it to check it.** That's how this setup would be used, but it's also an instruction to look for problems that Opus alone never got in v2. A fair reading of any gain is "Opus reviewing Haiku's work", not "Opus plus Haiku is as careful as Opus alone".
- **v2's comparison setups ran twice per task**, so differences against them are rough. Step 1 gives Haiku alone 5 more runs per task, which helps on that side only.
- **The v2 care points were noticed after v2's runs, not planned.** They're used here because they're the known differences, which means this test is aimed at the places where Opus is already known to add something. It doesn't show whether a review catches things nobody has listed.
- Claude Opus wrote v2's hidden tests and scores the answers. Blind scoring reduces this but doesn't remove it.
- **Safety:** all four tasks are on buildbot copies. None touches the small private project, network services, Docker, package installs or `sudo`. Commands are audited after the runs.

## Private file hashes (SHA-256)

```
67ebea2845aec0f2847ec4c220b59ab29ff48fb1794d722860125efb2055a4a5  tasks-v8.md
0b6d8285fec0c6c56f62789339533d7e729d11c1ae1dceeff0365768d942260f  tasks-v11.md
2fd78d10e5d137c3cbddafceb0cb6e7a70f5e4b09723ac133023ee9cf359e60b  tasks-v12.md
3eda33a710c78e787fcceea513695c71a4cd76d17439796c64507f87c66d60d6  make_t57_source_v2.sh
5c227c77f5ef022512391352bfbc331fb182fad172125999502646c3259546dd  make_v12_sources.sh
e9de3198e19b77362fc2f7f5d8456e317fe71ad4640858238a0e3d597b25c9c1  hidden-tests/test_hidden_t56.py
77add85d565cea263c202c46f5bad9834d65991e227161de3f851ed8008526f0  hidden-tests/test_hidden_t56b.py
92477b60a953ec420b187bcc85e9d8dd93194a18a6bfe1a5c8910cd7b996bdd8  hidden-tests/test_hidden_t57.py
f9f0946c272a23dde557082a9d31cdfe4842471ccc48f1ff3207b2a96333cb55  hidden-tests/test_hidden_t65.py
16c5435551593514b85ea700691f38248c0a5e8d0d1f5b065a495fefa4311dd3  hidden-tests/test_care_t65.py
671b9a125faca31879dcd60d6ca6e41a72c534350f70c43148d51362d79da5a4  v13_one_run.sh
```
