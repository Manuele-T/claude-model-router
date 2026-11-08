# Task set v11: focused coding tasks that hide a judgement call

v2 found that on short, well-specified coding tasks every setup passed the hidden tests, and that Haiku alone missed only "care" points the prompt never stated (a speed index, a symptom it couldn't reproduce). That was a handful of points, noticed rather than planned. These tasks test it directly: each one is short, but the prompt leaves something important unsaid.

This file is committed before any scored run. The real prompts, hidden tests, care tests and reference fixes stay private because some name the small project, so their SHA-256 hashes are listed below.

## Setups

Two runs each (`r1`, `r2`), headless, medium effort, `--permission-mode auto`, on the unchanged `scripts/run_bench.sh`:

- **F, Opus alone:** no prefix, Agent and Skill tools blocked. The baseline.
- **C, Opus plus Haiku:** prefix `Use the model-router skill. use haiku.` (every subagent on Haiku).
- **H, Haiku alone:** F with `--model haiku`.
- **S, Sonnet alone:** F with `--model sonnet`.

That makes 7 tasks × 4 setups × 2 runs = 56 runs.

## Tasks

Prompts are paraphrased here. Small project: the private ~10k-line Python CLI from earlier task sets, at `a3c99c4`. Buildbot: `c5cdcf3`, unmodified, with no planted bugs in this set.

| # | Codebase | Task (paraphrased) | What the prompt leaves unsaid |
| --- | --- | --- | --- |
| 61 | small | Add an optional per-profile setting for extra environment variables at launch, with a CLI option, strict validation, and the list command showing which profiles use it | Environment values often hold secrets |
| 62 | small | A user reports that the tool can't see an app that is clearly running, after a system update, and names a cause | The user's cause is wrong; the real cause is a real, unplanted bug |
| 63 | small | Add a JSON output option to the list command, with exact keys and types given | Nothing (control) |
| 64 | buildbot | Add a REST endpoint returning a builder's latest finished build, with the API spec | A builder can have millions of builds |
| 65 | buildbot | Change one build step's default timeout | The docs state the old default, and the project wants a release note for every change |
| 66 | buildbot | Make a frequent builder lookup avoid the database on repeated calls | Builders change after they're first read, so a cache can go stale |
| 67 | buildbot | Add a compact output option to an interval-formatting function, with examples | Nothing (control) |

## How runs are scored

**Hidden tests** are copied in after the run and reported as passed of total, then the project's whole suite is run. **Care tests** are separate, reported as yes or no per point, and never mixed into the hidden-test score. Task 62's care point is read from the answer: does it say the user's cause is wrong. Task 64's is also checked by reading the diff. Task 66's counts only for runs that actually cache, since with no cache nothing can go stale.

The tests were checked in scratch clones before any run:

| Task | Hidden, unmodified code | Hidden, reference fix | Care, unmodified | Care, reference |
| --- | --- | --- | --- | --- |
| 61 | 4 of 10 | 10 of 10 | 0 of 1 | 1 of 1 |
| 62 | 3 of 6 | 6 of 6 | read from answer | read from answer |
| 63 | 2 of 5 | 5 of 5 | none | none |
| 64 | 1 of 13 | 13 of 13 | 0 of 1 | 1 of 1 |
| 65 | 2 of 4 | 4 of 4 | 0 of 2 | 2 of 2 |
| 66 | 3 of 4 | 4 of 4 | 4 of 4 (nothing cached) | 4 of 4 |
| 67 | 0 of 3 | 3 of 3 | none | none |

The tests that pass on unmodified code guard behaviour that must not change. With the reference fixes applied, each project's whole suite passes. **Cost and time** as before: the checker's API-price proxy and transcript timestamps.

## Rules and known weaknesses

- No task or test edits after the first scored run. A task that fails to separate the setups stays in the results as it is.
- Runs are interleaved across setups within each task.
- Tasks and tests were written by Claude Opus after it had seen v2's results, so they may lean towards finding what v2 suggested. Committing them first reduces that risk but doesn't remove it. The scorer isn't blind.
- The care tests check one reasonable form of each care point. A run that handles a point another valid way is read by hand before it's scored down.
- A few trial runs of tasks 61 and 63 were made while checking the setup. They were discarded and aren't scored.
- **Known mistake in a prompt:** task 61's prompt says one launch path shares the same code as the others. On this baseline it doesn't (the bug behind task 53). A trial run noticed it. The prompt is left as it is, and whether a run noticed is recorded separately from the scores.

## Private file hashes (SHA-256)

```
0b6d8285fec0c6c56f62789339533d7e729d11c1ae1dceeff0365768d942260f  tasks-v11.md
8e4e3b7f9f5243fc7d90423ba98caa5a2973ba4203e9fc9a911eb1cd5883893c  ref_small.py
2e985b65bad9a9ec1e8322ac8f27e0606851729a4cb51c4e4cb606a322fc3d52  ref_bb.py
7a33e1aecddb265e52028995121a7c95d319ed127f6928fb7a43c79886f0e08d  hidden-tests/test_hidden_t61.py
2a8a913d0a7edda68ded09736a8012db683e4858de40c0443bc495e1abf57c16  hidden-tests/test_hidden_t62.py
31170a479816a54f0cda7c795b4c2963d0cc76fe6bc21a80f157d7c4ccae84ad  hidden-tests/test_hidden_t63.py
5ec1ccdf6fc3245f9382661bf0e63744ce869323455858de188f623a88d29771  hidden-tests/test_hidden_t64.py
f9f0946c272a23dde557082a9d31cdfe4842471ccc48f1ff3207b2a96333cb55  hidden-tests/test_hidden_t65.py
587960e4cdeabbc8e1bf66d465da0d81bd59ddc87989057e2ed04c6e07b4bb45  hidden-tests/test_hidden_t66.py
665877f17a1ec81ae4d9067287e60df555bc36cb96316a7ea43e1aae0efb5edf  hidden-tests/test_hidden_t67.py
21ff4db2b906386a27bfb6fb7e37e22b46572c09fcadd9f2c83342f63950add6  hidden-tests/test_care_t61.py
990f5347694e7ee529b38b86a1185b5439ce889fb1d64e03e26e6fd56512a61a  hidden-tests/test_care_t64.py
16c5435551593514b85ea700691f38248c0a5e8d0d1f5b065a495fefa4311dd3  hidden-tests/test_care_t65.py
e7fa6633a9179833aea89cc37ea86f5bc83c2d51d22a62db7d5ccd8d160fec6e  hidden-tests/test_care_t66.py
```
