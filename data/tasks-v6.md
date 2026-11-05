# Task set v6: building tasks on the small codebase

Project: the same private Python CLI project as task sets 1-2 (~10k lines including tests, 214 unit tests), cloned fresh for every run. Prompts are paraphrased here, as in `tasks.md`; module and command names are replaced with generic descriptions.

These tasks write code rather than read it. Each is scored by the project's existing unit suite plus a hidden test file written before any run and copied into the clone afterwards, so the run can't see it.

Arms: F (baseline: no prefix, Agent and Skill tools blocked), D (no prefix, Skill blocked), B (`Use the model-router skill. `), C (`Use the model-router skill. use haiku. `). Each arm runs twice (tags `r1`, `r2`).

| # | Type | Prompt (paraphrased) | Expected route |
| --- | --- | --- | --- |
| 51 | Feature | Add an optional free-text field to the app-profile records: the data model, config parsing with validation rules given in the prompt (length and character limits), saving and round-tripping, a new option on the CLI's add command and the field shown by its list command, plus docs and unit tests, with the whole unit suite passing. Touches 4-5 files. | Sonnet or Haiku per layer |
| 52 | Bug hunt | A user reports that saving app profiles whose commands contain certain characters fails with a config error, and gives two example commands. Find the cause, fix it, add a regression test, and keep the whole unit suite passing. The run's copy of the project contains one planted bug that the existing suite doesn't catch. | Haiku search, Sonnet fix |
