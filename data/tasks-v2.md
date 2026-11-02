# Task set v2: reading-heavy

Same project and arms as `tasks.md` (the same private project; run A `no routing. `, run B `Use the model-router skill. `). These tasks are mostly mechanical reading across many files, where routing to cheaper models should pay off if it pays off anywhere. Each arm runs twice (tags `r1`, `r2`). Numbered 11-15 so their clones and transcripts never collide with v1.

| # | Type | Prompt | Expected route |
| --- | --- | --- | --- |
| 11 | Inventory | For every Python file under the main package, list each top-level function and class with a one-line description of what it does. One section per file. | Haiku |
| 12 | Inventory | For every test file in tests/unit/, list which package module or modules it tests and how many test methods it has. Then list the package modules that have no dedicated test file. | Haiku |
| 13 | Audit | Find every function and method in the main package that has no docstring. List them grouped by file, with line numbers, and give the total count. | Haiku |
| 14 | Map | For every module in the main package, list which other package modules it imports. Then point out any import cycles. | Haiku |
| 15 | Docs check | Read README.md and every file in docs/ and list every claim they make about CLI commands, flags or file paths. Check each claim against the code and report which ones are out of date. | Haiku reading, Sonnet or Opus checking |
