# Task set v4: ~50k-line codebase

Project: [beetbox/beets](https://github.com/beetbox/beets) at commit `ab4bdfd` (shallow clone, cloned fresh per run). 167 hand-written modules in `beets/` and `beetsplug/` (including 4 test-helper modules shipped in the package), about 52k lines, plus `docs/reference/` (5 pages, 2.8k lines) for task 32 and `docs/plugins/` (80 pages, 8.3k lines) for task 33. Chosen to be about 2.3x the size of rich and far less famous, so the model can rely less on what it already knows.

Same two task types as `tasks-v3.md`, same arms (A `no routing. `, B `Use the model-router skill. `), plus arm C (`Use the model-router skill. use haiku. `, every subagent forced onto Haiku). Each arm runs twice. B's runs are tagged `r3`, `r4`; task 31's A runs are `r1n`, `r2n` (Agent tool blocked). Task 33's first runs hit the usage limit after ~3 minutes except `B r2`; the complete re-runs are `A r1b`, `A r2b`, `B r1b`, `C r1b`, `C r2b`.

Run with `SRC=<beets checkout> TASKS=data/tasks-v4.md scripts/run_bench.sh 31 A r1`.

| # | Type | Prompt | Expected route |
| --- | --- | --- | --- |
| 31 | Summaries | Write a one-paragraph summary of every Python module in beets/ and beetsplug/, saying what it does and which other modules in the project it works with. One section per module. | Haiku or Sonnet, in parallel chunks |
| 32 | Docs check | Read every file in docs/reference/ and check each claim about beets' commands, options, configuration settings, defaults and behaviour against the code in beets/ and beetsplug/. Report every claim that is wrong or out of date, with the doc file and line. | Haiku reading, Sonnet or Opus checking |
| 33 | Docs check (plugins) | Read every file in docs/plugins/ and check each claim about the plugins' commands, options, configuration settings, defaults and behaviour against the code in beetsplug/ and beets/. Report every claim that is wrong or out of date, with the doc file and line. | Haiku reading, Sonnet or Opus checking |
