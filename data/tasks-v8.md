# Task set v8: coding tasks on a much bigger codebase

Project: [buildbot/buildbot](https://github.com/buildbot/buildbot) at commit `c5cdcf3` (~100k hand-written lines; the unit suite ran 6,448 tests on this setup, all passing or skipped), cloned fresh for every run. Tasks 51-55 on the small project didn't separate the setups on correctness, so these ask whether a much larger codebase does, because finding the right code is harder here. They're reported as their own group and never mixed with other task sets.

This file is committed before any run, to fix the design in advance. The exact prompts stay private until the runs are done, because they could give away the planted bug, so their SHA-256 hashes are listed below.

Arms, skill, effort and runs per arm are unchanged: F (baseline: no prefix, Agent and Skill tools blocked), D (no prefix, Skill blocked), B (`Use the model-router skill. `), C (`Use the model-router skill. use haiku. `), Opus at medium effort, tags `r1` and `r2`, interleaved across arms. That makes 16 runs. Runs have buildbot's pinned test requirements available in a venv and import the clone's own code.

| # | Type | Prompt (paraphrased) | Expected route |
| --- | --- | --- | --- |
| 56 | Cross-module feature | Add a REST API endpoint giving, for one builder, the number of finished builds per result. It must follow the conventions of the existing API, stay fast on a builder with millions of builds, and include unit tests. The run has to find out what a proper endpoint involves. | Haiku search, Sonnet implementation |
| 57 | Far-off bug | Users report wrong blamelists when two builders follow one repository on different branches. Find the cause, fix it, add a regression test. The run's copy contains one planted bug that the whole existing unit suite doesn't catch. The symptom appears far from the cause, and patching where the symptom shows leaves part of the problem. | Haiku search, Sonnet fix |

## How runs are scored

Same as `data/tasks-v7.md`: hidden tests reported as passed of total, the whole unit suite, diff size and complexity, verification cost, cost and wall time from the same checker, and the Claude Code version per run. Paths under a `test` directory count as tests in the diff. A suite failure is repeated before counting it, and any repeat is reported.

The tests were checked in scratch clones before any run:

| Task | Unmodified or planted code | Shortcut fix | Reference fix |
| --- | --- | --- | --- |
| 56 | 1 of 13 | 10 of 13 | 13 of 13 |
| 57 | 1 of 8 | 3 of 8 | 8 of 8 |

The whole unit suite stayed green with the 56 reference fix. The 57 reference is the unmodified buildbot code, so it needed no separate suite run: the baseline run covers it.

## Rules

The rules in `data/tasks-v7.md` apply. In addition, after what happened on task 54, the hidden tests here look up named fields rather than comparing whole records, so an extra field doesn't lose a point.

Known weaknesses: there are only two tasks, chosen and written by Claude Opus after seeing that Haiku did well so far. One bug is planted rather than found in the wild, and a run that notices the unused `branch` argument near the cause gets a strong hint.

## Amendment before any run

The first script for task 57's source, `make_t57_source.sh`, lost 17 of buildbot's 1,912 files, because `git archive` honours export-ignore and `git add -A` honours global ignore rules. A check of the staged files caught this before any run. `make_t57_source_v2.sh` replaces it, with the same single planted line. No task, prompt or hidden test changed, and the original hashes below still match their files. In a simulated build without the commit, the full unit suite still passed with the plant in place, and the hidden test scored 1 of 8. The commit in that copy skips the local secret-scanning hook, because it flags fixtures in buildbot's public test files, unchanged from upstream.

## Private file hashes (SHA-256)

```
67ebea2845aec0f2847ec4c220b59ab29ff48fb1794d722860125efb2055a4a5  tasks-v8.md
dd43549d191815734377010282dedb4798126ae9b34c5119a9a8f72a9f79be20  make_t57_source.sh
e9de3198e19b77362fc2f7f5d8456e317fe71ad4640858238a0e3d597b25c9c1  test_hidden_t56.py
92477b60a953ec420b187bcc85e9d8dd93194a18a6bfe1a5c8910cd7b996bdd8  test_hidden_t57.py
3eda33a710c78e787fcceea513695c71a4cd76d17439796c64507f87c66d60d6  make_t57_source_v2.sh
```
