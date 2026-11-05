# Task set v7: harder building tasks on the small codebase

Project: the same private Python CLI project as task sets 1, 2 and 6, at commit `a3c99c4`, cloned fresh for every run. Prompts are paraphrased here; module and command names are replaced with generic descriptions.

Tasks 51 and 52 were too easy: every run passed. These three are meant to be harder. They are reported as their own group and never mixed with the reading tasks or with 51-52.

This file is committed before any run, to fix the design in advance. The real prompts and hidden tests stay private because they name the project, so their SHA-256 hashes are listed below.

Arms, skill, effort and runs per arm are unchanged: F (baseline: no prefix, Agent and Skill tools blocked), D (no prefix, Skill blocked), B (`Use the model-router skill. `), C (`Use the model-router skill. use haiku. `), Opus at medium effort, tags `r1` and `r2`. That makes 24 runs.

| # | Type | Prompt (paraphrased) | Expected route |
| --- | --- | --- | --- |
| 53 | Domain trap | A user reports that a feature which starts an app at login does nothing, though it says it is enabled and running the app by hand works. Find the cause, fix it, add a regression test, and keep the whole unit suite passing. The bug is real, not planted. The obvious one-line fix doesn't work, because of how another part of the code reads its arguments. | Haiku search, Sonnet fix |
| 54 | Vague feature | Add a command that renames an app profile. The only requirement beyond the command's name and arguments: anything that works under the old name should keep working under the new one. Add unit tests and keep the suite passing. The prompt doesn't say what depends on the name, so the run has to find out. | Sonnet |
| 55 | Refactor | Split the project's ~700-line command-line module into focused modules, with line limits given in the prompt. No behaviour change for users or for other code that uses the module, and existing tests may not be edited. Other code reaches into that module in ways that a simple move breaks. | Sonnet per module |

## How runs are scored

**Correctness.** Each task has a hidden test file, copied into the clone after the run, so the run can't see it. Scores are reported as tests passed of total, not just pass or fail: 53 has 9 tests, 54 has 12, 55 has 22. The project's whole unit suite is then run as well. For 55, the existing tests are restored from the baseline commit first, because the prompt forbids editing them.

The tests were checked in a scratch clone before any run:

| Task | Unmodified code | Shortcut fix | Reference fix |
| --- | --- | --- | --- |
| 53 | 6 of 9 pass (3 fail on the bug; the rest guard behaviour that must not change) | 5 of 9 | 9 of 9 |
| 54 | 0 of 12 | 7 of 12 | 12 of 12 |
| 55 | 20 of 22 (only the line limits fail; the rest pin current behaviour) | not built | 22 of 22 |

**Diff size and complexity**, measured against the baseline commit by a stdlib-only script, also on the 16 Part 2 runs (tasks 51-52):

- lines added and removed, and files touched, split into non-test code and tests;
- existing test files edited, and how many lines;
- new top-level functions and classes;
- cyclomatic complexity from the `ast` module, before and after, for each changed Python file: one per function, plus one for each `if`, `for`, `while`, `except`, conditional expression, comprehension, `match` case and extra boolean operand. Reported as the total and the highest single function.

**Verification cost**, from the transcripts at the same API-price proxy, also on the 16 Part 2 runs:

- Opus's own cost and the subagents' cost, as the checker already splits them;
- post-edit check cost: messages from any agent, after the run's first file edit by any agent, that neither edit a file nor spawn a subagent, in dollars and as a share of the run. This includes Opus reviewing a subagent's work;
- number of test-suite runs;
- rework: file edits made after the first test-suite run that follows the run's first edit, so a baseline test run before any edit doesn't count.

File edits include Edit and Write calls in the project and shell commands that write files (`python3` scripts, `sed -i`, redirects). Many runs edit that way, so detecting those commands is a heuristic and may miscount a few.

**Cost and time** as before: the checker's API-price proxy and transcript timestamps. Each run also records the Claude Code version.

## Rules

- No skill edits, and no changes to tasks 51-52, their scores or their hidden tests.
- A task isn't tuned after a run. If it fails to separate the arms, it stays in the results as it is, and any new task gets a new number.
- Runs are interleaved across arms within each task, so a model or tool update can't fall entirely on one arm.
- Known weakness: these tasks were designed after seeing that Haiku did well on 51-52, which could bias them. Fixing them here before any run is the protection, and the bias can't be ruled out entirely.

## Private file hashes (SHA-256)

```
ca7400c28e02735c707ca71c5841378db3caf788f0fbaeab85d47d9cbac25426  tasks-v7.md
cd985c4e8670cb9410e98ac211f2232f43b95b0b6c7f0cfd3791ca5de4871f37  test_hidden_t53.py
16b4c298eb90e673e42f7ac844a25c47ca3d709a06f6cb8cd22395757937d9e6  test_hidden_t54.py
6d1f6a13ca982d7bc62e17b0c6ae736c6824fb2314fe8b9a06099e28c423554c  test_hidden_t55.py
```
