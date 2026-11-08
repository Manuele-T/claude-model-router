# Task set v10: Sonnet alone on the Haiku-alone tasks

In v1 and v2, Sonnet only ran as a subagent, picked by the routing skill. As a helper it cost more than Haiku for about the same results, but it was never tested as the main model. This adds one setup to find out what Sonnet does on its own.

**Setup S ("Sonnet alone"):** no prompt prefix, `--model sonnet`, Agent and Skill tools blocked, effort medium. This is arm F with Sonnet as the main model, the same way setup H is arm F with Haiku.

**Tasks:** the six tasks Haiku alone ran on (`data/tasks-v9.md`), twice each (tags `r1`, `r2`), 12 runs:

- 53-55 from `data/tasks-v7.md`, on the small project at baseline commit `a3c99c4`.
- 56-57 from `data/tasks-v8.md`, on buildbot, with the same sources and venv.
- 43 from `data/tasks-v5.md`, the 85-page docs check on `buildbot-planted`.

Prompts, sources, hidden tests, answer keys and real-error lists are unchanged. Nothing was designed or tuned for this setup.

**Scoring:** the same as for setup H. That means hidden tests passed of total (both scores on 56), the full suite, diff size, verification cost and wall time on 53-57. It also means comparing each run's own claim of success with its hidden-test score, and checking the two care points no test scores: did the endpoint add an index, and did the bug report flag the symptom the bug doesn't cause. On 43, Claude Opus reads each report against the verified list of 92, then checks claims outside the list and citations past the end of the file, as for H.

**Written before the runs, not committed before them.** This note was written on 2026-11-07, before the first S run. Manuele does all commits, so it wasn't committed first, as was also the case for task 43 in v9.

**Limits:**
- These runs come after every other setup, not interleaved with them. Each run records its Claude Code version.
- The known flaws in the hidden tests for 54 and 56, and in the prompt for 57, apply here too.
- Two runs per task.
- The real-error list for 43 was built before S ran, as it was for H, so S's real errors outside the list are checked separately.
