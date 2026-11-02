# Task set v3: larger codebase, reading a script can't replace

Project: [Textualize/rich](https://github.com/Textualize/rich) at commit `9d8f9a3` (shallow clone in `~/bench-src/rich`, cloned fresh per run). 76 hand-written modules, about 22k lines, plus about 16k lines of generated Unicode and emoji tables the prompts tell the agent to skip, and 25 `.rst` doc pages (2.6k lines).

Same arms as before (A `no routing. `, B `Use the model-router skill. `), each run twice (tags `r1`, `r2`). Both tasks need the code to be read and understood, so a counting script can't answer them.

Run with `SRC=~/bench-src/rich TASKS=data/tasks-v3.md scripts/run_bench.sh 21 A r1`.

| # | Type | Prompt | Expected route |
| --- | --- | --- | --- |
| 21 | Summaries | Write a one-paragraph summary of every Python module in rich/, saying what it does and which other rich modules it works with. Skip rich/_unicode_data/ and rich/_emoji_codes.py, which are generated tables. One section per module. | Haiku, in parallel chunks |
| 22 | Docs check | Read every .rst file in docs/source/ and check each claim about rich's API (class and function names, parameters, defaults, behaviour) and each code example against the code in rich/. Report every claim that is wrong or out of date, with the doc file and line. | Haiku reading, Sonnet or Opus checking |
