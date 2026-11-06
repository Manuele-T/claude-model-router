# Task set v9: Haiku alone on the harder coding tasks

Every setup so far has Opus as the main model, reviewing and testing, so the earlier results describe "Opus plus Haiku", not Haiku. This adds one setup to find out what Haiku does with no Opus behind it.

**Setup H ("Haiku alone"):** no prompt prefix, `--model haiku`, Agent and Skill tools blocked, effort medium, as arm F but with Haiku as the main model.

**Tasks:** 53-57, run twice each (tags `r1`, `r2`), 10 runs. Prompts, sources and hidden tests are unchanged from `data/tasks-v7.md` and `data/tasks-v8.md`, committed before any run of those tasks and matching the hashes listed there. Nothing was designed for this setup.

**Scoring:** the same as those files, including both scores on 56 (the official test and the corrected test data), and diff size, verification cost and wall time. No Opus means nothing else checks the work, so a run's own claim that it succeeded will also be compared with its hidden-test score.

**Added before its runs, not committed before them:** task 43 from `data/tasks-v5.md` (the 85-page docs check), twice, unchanged, with the same answer key and real-error list. Its real errors were scored by Claude Opus reading each report against the verified list, since line numbers in the reports weren't reliable. This note itself was also written, but not yet committed, when the runs started. Nothing was tuned, since the prompts and tests were already fixed.

**Limits:**
- These runs happen after arms F, D, B and C, not interleaved with them, so a model or tool update could affect the comparison. Each run records the Claude Code version.
- The hidden tests' known flaws on 54 and 56 apply here too, and the prompt flaw on 57.
- Two runs per task.
- The result is already partly expected to be cheap. Cost matters here only alongside the scores.
