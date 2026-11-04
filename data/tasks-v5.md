# Task set v5: ~100k-line codebase

Project: [buildbot/buildbot](https://github.com/buildbot/buildbot) at commit `c5cdcf3`, cloned fresh per run from a one-commit local copy. 408 hand-written modules in `master/buildbot/` and `worker/buildbot_worker/` (excluding their `test/` packages), about 91k lines, plus `master/docs/manual/configuration/changesources.rst` and `schedulers.rst` (3.7k lines) for task 42 and the 85 pages in `master/docs/manual/configuration/steps/`, `reporters/` and `report_generators/` (6k lines) for task 43. Chosen to be about 1.8x the size of beets.

Same three task types as `tasks-v4.md`. The doc pages for 42 and 43 contain known errors: some real, some planted for scoring (disclosed in `results.md`). The planted list stays private until the runs are done.

Arms: F (baseline: no prefix, Agent and Skill tools blocked), D (no prefix, Skill blocked), B (`Use the model-router skill. `), C (`Use the model-router skill. use haiku. `). Each arm runs twice (tags `r1`, `r2`), interleaved; a third run (`r3`) only where results are close.

Run with `SRC=<buildbot checkout> TASKS=data/tasks-v5.md scripts/run_bench.sh 41 F r1`.

| # | Type | Prompt | Expected route |
| --- | --- | --- | --- |
| 41 | Summaries | Write a one-paragraph summary of every Python module in master/buildbot/ and worker/buildbot_worker/, excluding their test/ packages, saying what it does and which other modules in the project it works with. One section per module, headed with the module's path. | Haiku or Sonnet, in parallel chunks |
| 42 | Docs check | Read master/docs/manual/configuration/changesources.rst and master/docs/manual/configuration/schedulers.rst and check each claim about buildbot's change sources and schedulers (class names, parameters, defaults and behaviour) against the code in master/buildbot/. Report every claim that is wrong or out of date, with the doc file and line. | Haiku reading, Sonnet or Opus checking |
| 43 | Docs check (steps and reporters) | Read every file in master/docs/manual/configuration/steps/, master/docs/manual/configuration/reporters/ and master/docs/manual/configuration/report_generators/ and check each claim about build steps, reporters and report generators (parameters, defaults and behaviour) against the code in master/buildbot/ and worker/buildbot_worker/. Report every claim that is wrong or out of date, with the doc file and line. | Haiku reading, Sonnet or Opus checking |
