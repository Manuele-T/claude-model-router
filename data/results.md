# Results

Run on 2026-10-25 to 2026-11-01. Est. $ = `verify_models.py` API-price estimate (Haiku 5.5 / Sonnet 5.5 / Opus 5.5 list prices, including Haiku's higher rate for prompts over 100K tokens, which the checker priced from 2026-10-28 on; only the beets Haiku runs crossed it). Per-task costs are rounded to the cent; every percentage and total is computed from unrounded costs. Wall times come from transcript timestamps (the result JSON's `duration_ms` undercounts runs that wait on subagents). Opus 5.5 orchestrator at effort medium, headless (`claude -p`), auto permission mode, Claude Code 2.1.310.

Arm A ("Opus only, forced") runs everything on Opus (`no routing.`; from task 31's `r1n` runs on, the Agent tool is also blocked, so beets 31, 33 and 32 `r3`/`r4` had no Agent tool, while sets 1-3 and 32 `r1`/`r2` did); arm B uses the skill; arm C uses the skill with every subagent forced onto Haiku (`Use the model-router skill. use haiku.`); arm D is plain Claude Code ("Opus only, spontaneous": no prefix, subagents allowed, the Skill tool blocked so the installed router skill can't load itself). Saving = 1 - B/A (or C/A, D/A), so a negative saving means the setup cost more than forced Opus.

## Task set 1: everyday tasks (tasks 01-10)

Bench project: a private Python CLI project of mine (~10k lines including tests), fresh clone per run. One run per arm per task.

| Task | Type | A est. $ | A result |
| --- | --- | --- | --- |
| 01 | Search | 0.14 | pass |
| 02 | Search | 0.33 | pass |
| 03 | Search + summary | 0.34 | pass |
| 04 | Explain | 0.50 | pass |
| 05 | Bug fix | 0.49 | pass* |
| 06 | Tests | 0.21 | pass |
| 07 | Small feature | 0.22 | pass |
| 08 | Refactor | 0.57 | pass |
| 09 | Mixed | 0.70 | pass |
| 10 | Design | 0.31 | pass |
| **Total** | | **3.81** | 10/10 |

\* Unit tests pass and the diff reads correctly, but the fix was not exercised against a real failing launcher subprocess.

Pass criteria: code tasks = full unit suite passes (214+ tests) and the diff does what was asked; 08/09 also checked that the CLI's argument parser still builds all 12 subcommands; search/explain/design tasks = answer checked against the code (01 against a direct grep: 5 `except Exception` + 2 `except BaseException`).

Wall time: A 776 s total.

### B: skill-routed (2026-10-28)

One run per task (`~/bench/t<NN>-Bv3`), current global CLAUDE.md.

| Task | A est. $ | B est. $ | Saving | B result | B route |
| --- | --- | --- | --- | --- | --- |
| 01 | 0.14 | 0.16 | -14% | pass (7 = 5 + 2) | haiku |
| 02 | 0.33 | 0.47 | -42% | pass | sonnet |
| 03 | 0.34 | 0.36 | -6% | pass | haiku |
| 04 | 0.50 | 0.75 | -50% | pass | 2 sonnet in parallel |
| 05 | 0.49 | 0.58 | -18% | pass* | inline |
| 06 | 0.21 | 0.30 | -43% | pass | sonnet (19 tests written) |
| 07 | 0.22 | 0.23 | -5% | pass | inline |
| 08 | 0.57 | 0.60 | -5% | pass | sonnet |
| 09 | 0.70 | 0.58 | 17% | pass | sonnet |
| 10 | 0.31 | 0.31 | 0% | pass | haiku lookup, inline design |
| **Total** | **3.81** | **4.34** | **-14%** | 10/10 | 3 haiku, 6 sonnet |

Wall time: B 1186 s (+53% vs A; the 10 tasks ran 5 at a time). Mismatches 0, fallbacks 0, unpaired 0. The checker's own estimate for these runs was a 44% saving.

\* As for A. 05's suite also failed twice (once an error, once a failure) while 14 other bench runs were running in parallel, then passed 14 times in a row; that looks like a timing-sensitive test under load.

The orchestrator picked Haiku for the three lookup tasks and Sonnet for most code jobs. The total still came out 14% above forced Opus; only 09 was cheaper routed.

### C: forced Haiku (2026-10-29)

One run per task (`~/bench/t<NN>-Cv1`), current global CLAUDE.md.

| Task | A est. $ | C est. $ | Saving | C result | C subagents |
| --- | --- | --- | --- | --- | --- |
| 01 | 0.14 | 0.25 | -79% | pass (7) | 1 haiku |
| 02 | 0.33 | 0.31 | 6% | pass (Opus added reads the agent missed) | 1 haiku |
| 03 | 0.34 | 0.48 | -41% | pass | 2 haiku |
| 04 | 0.50 | 0.46 | 8% | pass | 3 haiku |
| 05 | 0.49 | 0.50 | -2% | pass* | 1 haiku |
| 06 | 0.21 | 0.20 | 5% | pass | 1 haiku |
| 07 | 0.22 | 0.21 | 5% | pass | 1 haiku |
| 08 | 0.57 | 0.38 | 32% | pass | 1 haiku |
| 09 | 0.70 | 0.59 | 16% | pass | 2 haiku |
| 10 | 0.31 | 0.25 | 19% | pass | 1 haiku, design inline |
| **Total** | **3.81** | **3.63** | **5%** | 10/10 | 14 haiku |

Wall time: C 1615 s (+108% vs A; 5 runs at a time). Mismatches 0. The checker's own estimate was a 68% saving.

\* As for A and B: tests pass, fix not exercised against a real failing launcher subprocess.

Unlike skill routing, forced Haiku didn't cost more than forced Opus on this set, though it saved only 5%. It lost on the small lookups (01, 03), where briefing outweighs any saving, and won on the bigger code jobs (08-10).

### D: Opus only, spontaneous (no skill) (2026-10-31)

One run per task (`~/bench/t<NN>-Dv1`), current global CLAUDE.md. Opus was free to spawn subagents but never did.

| Task | A est. $ | D est. $ | Saving | D result |
| --- | --- | --- | --- | --- |
| 01 | 0.14 | 0.23 | -64% | pass (7 = 5 + 2) |
| 02 | 0.33 | 0.34 | -3% | pass |
| 03 | 0.34 | 0.32 | 6% | pass |
| 04 | 0.50 | 0.41 | 18% | pass |
| 05 | 0.49 | 0.50 | -2% | pass* |
| 06 | 0.21 | 0.18 | 14% | pass (11 tests written) |
| 07 | 0.22 | 0.17 | 23% | pass |
| 08 | 0.57 | 0.73 | -28% | pass |
| 09 | 0.70 | 0.60 | 14% | pass |
| 10 | 0.31 | 0.29 | 6% | pass |
| **Total** | **3.81** | **3.77** | **1%** | 10/10, 0 subagents |

Wall time: D 850 s (+10% vs A). No `Skill` calls and no routing-log lines in any run.

\* As before: tests pass, fix not exercised against a real failing launcher subprocess.

Spontaneous Opus behaved like forced Opus on this set: same pass rate, cost within 1%.

### What the numbers say (task set 1)

- **Routing happened as asked:** 9 subagents in B and 14 in C, 0 mismatches, 0 fallbacks, 0 unpaired. Every subagent ran the model it was given.
- **Skill routing did not save usage on this workload.** Head-to-head, B cost 14% more than forced Opus with the same pass rate. Forced Haiku came out 5% cheaper and spontaneous Opus 1% cheaper.
- **Why:** Opus 5.5 at medium effort already does small searches cheaply with Grep, and Opus cache reads are cheap ($0.20/MTok). Routing adds fixed overhead (loading the skill, Bash log calls, writing a subagent brief) and Opus re-reads files to check a subagent's work, so the work is partly done twice.
- **The checker's "saving vs forced Opus" figure is misleading on its own.** On the B runs it estimates a 44% saving, because it re-prices the cheap-model tokens at Opus rates and can't see the overhead routing adds. Head-to-head, those same runs cost 14% more. The head-to-head number is the one to publish.

### Caveats (task set 1)

- Each arm was run once, so run-to-run variance is unknown here.
- Costs are API list prices used as a proxy for subscription usage.
- One project, one person's tasks.

## Task set 2: reading-heavy (tasks 11-15)

Prompts in `data/tasks-v2.md`. Same project and setup. **Each arm ran twice** (r1, r2) to see the noise. Accuracy was scored against ground truth computed from the source with Python's `ast` module (11-14), or against a list of 9 real doc problems collected from the runs' findings and checked against the docs (15).

| Task | A r1 / r2 $ | A mean | A accuracy |
| --- | --- | --- | --- |
| 11 Inventory | 0.49 / 0.49 | 0.49 | 215/215 defs, both |
| 12 Test map | 0.14 / 0.20 | 0.17 | 17/17 counts, both |
| 13 Docstrings | 0.19 / 0.19 | 0.19 | 184, both |
| 14 Import map | 0.16 / 0.15 | 0.16 | no cycles, both |
| 15 Docs check | 0.80 / 0.79 | 0.79 | 7 and 8 of 9 issues |
| **Total** | **1.78 / 1.81** | **1.80** | |

Wall time: A 662 s total.

How 15 was scored: the 9 real out-of-date or incomplete doc claims are an outdated packaging rule, outdated installer entry points, a README feature list, a prototype script's subcommand list, two stale test counts, a CLI command table missing two commands, undocumented installer flags, and a stale "until packaged" note. Every run also flagged a hard-coded home-directory path in a planning doc; that is the real checkout path and only differed in the bench clone, so it is not counted. Both A runs also cited some line numbers that don't exist (for example line 239 of a 49-line planning doc).

What the forced Opus runs show:

- **Opus didn't read, it computed.** For 12, 13 and 14 it wrote a short `ast` or grep script instead of reading files one by one, which is cheaper than any subagent. "Mechanical reading" mostly isn't reading once the orchestrator can script it, so there's little for a cheaper model to take over.
- **Forced Opus is steady.** Its two runs were within about 10% of each other on every task except 12 (37%).

### B: skill-routed (r5, r6; 2026-10-28)

Two runs with the current global CLAUDE.md. (Tags r3/r4 hit the usage limit before answering and are not used.)

| Task | A mean | B r5 / r6 $ | B mean | Saving | B accuracy | B route r5 / r6 |
| --- | --- | --- | --- | --- | --- | --- |
| 11 Inventory | 0.49 | 0.41 / 1.01 | 0.71 | -45% | 215/215 defs, both | 3 haiku / 3 sonnet |
| 12 Test map | 0.17 | 0.20 / 0.21 | 0.21 | -21% | 16/17 both (test_validate: 12, truth 14) | haiku / haiku |
| 13 Docstrings | 0.19 | 0.24 / 0.24 | 0.24 | -26% | 184, both | haiku / haiku |
| 14 Import map | 0.16 | 0.19 / 0.26 | 0.23 | -45% | no cycles, both | haiku / haiku |
| 15 Docs check | 0.79 | 0.70 / 1.21 | 0.96 | -20% | 5 and 6 of 9 issues | haiku + sonnet / 2 sonnet |
| **Total** | **1.80** | **1.74 / 2.93** | **2.33** | **-30%** | | 10 of 10 runs delegated |

Wall time: B 1222 s total (+85% vs A). Mismatches 0. The checker's own estimate for these runs was a 52% saving.

Every routed run delegated, mostly to Haiku, and cost went up: 30% above forced Opus. Accuracy didn't improve: both runs miscounted test_validate on 12, and on 15 they found 5 and 6 of 9 issues against 7 and 8 for forced Opus. Routes also changed between the two runs (11: 3 haiku in one, 3 sonnet in the other), and B r6 cost 68% more than r5.

### C: forced Haiku (r1, r2; 2026-10-29)

| Task | A mean | C r1 / r2 $ | C mean | Saving | C accuracy | C subagents r1 / r2 |
| --- | --- | --- | --- | --- | --- | --- |
| 11 Inventory | 0.49 | 0.42 / 0.45 | 0.44 | 10% | 215/215 defs, both | 4 / 4 |
| 12 Test map | 0.17 | 0.18 / 0.17 | 0.18 | -6% | r1 17/17, r2 16/17 (test_validate: 12) | 1 / 1 |
| 13 Docstrings | 0.19 | 0.21 / 0.22 | 0.22 | -18% | 184, both | 1 / 1 |
| 14 Import map | 0.16 | 0.21 / 0.18 | 0.19 | -23% | no cycles, both | 1 / 1 |
| 15 Docs check | 0.79 | 0.65 / 0.90 | 0.78 | 2% | 3 and 2 of 9 issues | 4 / 2 |
| **Total** | **1.80** | **1.67 / 1.92** | **1.79** | **0%** | | 20 haiku |

Wall time: C 1324 s total (+100% vs A). Mismatches 0. The checker's own estimate was a 77% saving.

Forced Haiku broke even on cost. The counting tasks were as accurate as forced Opus apart from one miscount, but the docs check was the weakest of any arm: 3 and 2 of the 9 issues, against 7 and 8 for forced Opus. C r2 also flagged one claim outside the list (a README line about re-adding an existing entry), not verified. Its docs agent ran an integration test and left an empty temp directory behind.

### D: Opus only, spontaneous (no skill) (r1, r2; 2026-10-31)

| Task | A mean | D r1 / r2 $ | D mean | Saving | D accuracy |
| --- | --- | --- | --- | --- | --- |
| 11 Inventory | 0.49 | 0.40 / 0.47 | 0.44 | 11% | 215/215 defs, both |
| 12 Test map | 0.17 | 0.14 / 0.12 | 0.13 | 24% | r1 17/17, r2 16/17 (test_validate: 12, truth 14) |
| 13 Docstrings | 0.19 | 0.13 / 0.14 | 0.14 | 29% | 184, both |
| 14 Import map | 0.16 | 0.14 / 0.13 | 0.14 | 16% | no cycles, both |
| 15 Docs check | 0.79 | 0.67 / 0.67 | 0.67 | 15% | 5 and 7 of 9 issues |
| **Total** | **1.80** | **1.48 / 1.53** | **1.50** | **16%** | 0 subagents |

Wall time: D 584 s total (-12% vs A). Every task came out cheaper than forced Opus. Behaviour was the same as A (Opus alone, scripts for 12-14), so the saving comes from shorter sessions: fewer requests and less cached context re-read (t15: 12 requests and 0.78M cache reads, against 17 and 1.22M for A r1). Same Claude Code version (2.1.310); the first prompt was ~4k tokens smaller than A's, worth a few cents per run at most. The follow-up below finds forced Opus consistently puts in more effort (more output and thinking per run). The `test_validate` miscount happened here too, on Opus alone, so it isn't a Haiku weakness.

## Task set 3: larger codebase (rich, tasks 21-22)

Prompts in `data/tasks-v3.md`: Textualize/rich at `9d8f9a3`, 76 hand-written modules (~22k lines) plus 25 `.rst` doc pages. Both tasks need the code to be read and understood. Each arm ran twice.

| Task | A r1 / r2 $ | A mean | A result |
| --- | --- | --- | --- |
| 21 Module summaries | 0.88 / 0.50 | 0.69 | 76/76 and 75/76 modules (r2 left out `pager.py`); ~3.5k words |
| 22 Docs vs code | 2.00 / 1.39 | 1.70 | 10 and 10 of 12 verified issues (r2 had 2 wrong line numbers) |
| **Total** | **2.88 / 1.89** | **2.38** | |

Wall time: A 806 s.

How 22 was scored: 12 doc problems collected from the runs' findings, each checked against the source: the Python 3.8 requirement, `FORCE_COLOR` vs `TERM=dumb`, `RichHandler` `suppress`, the broken `Print.print` and `ScreenContext.update` cross-references, `safe_box` (it does not force ASCII), the IPython `extensions` typo, `reference/control.rst` missing from the toctree, the outdated `Layout` sample output, nested Live since 14.1.0 not 14.0.0, Jupyter auto-refresh, and column `width` described as a row.

- **A famous repo leaks training knowledge.** A r1 said its summaries were "partly from my own knowledge of Rich". That favours the forced Opus arm, which can skip reading what it already knows. An unfamiliar private codebase of this size would be a fairer test.

### B: skill-routed (r5, r6; 2026-10-28)

Two runs with the current global CLAUDE.md, rich cloned at `9d8f9a3`. (Tags r3/r4 hit the usage limit and are not used.)

| Task | A mean | B r5 / r6 $ | B mean | Saving | B result | B route r5 / r6 |
| --- | --- | --- | --- | --- | --- | --- |
| 21 Module summaries | 0.69 | 1.65 / 0.99 | 1.32 | -91% | 76/76 both; ~6k and ~5k words | 5 sonnet / 2 haiku + 3 sonnet |
| 22 Docs vs code | 1.70 | 1.13 / 1.51 | 1.32 | 22% | 6 and 9 of 12 verified issues | 4 sonnet / 1 haiku + 4 sonnet |
| **Total** | **2.38** | **2.78 / 2.50** | **2.64** | **-11%** | | 3 haiku, 16 sonnet |

Wall time: B 655 s (-19% vs A). Mismatches 0. The checker's own estimate for these runs was a 45% saving.

Routing was used as designed here, with the work split across 4-5 parallel subagents per run, but the orchestrator judged most batches to need code comprehension and sent them to Sonnet. Overall it cost 11% more than forced Opus: the summaries nearly twice as much, while the docs check came out 22% cheaper. Quality on 22 stayed slightly below A (6 and 9 of 12, against 10 and 10). r6 also reported three problems outside the 12-issue list (a `Table` import missing from a box example, an empty `:special-members: __call__`, an old GitHub link); these weren't verified and aren't counted.

### C: forced Haiku (r1, r2; 2026-10-29)

| Task | A mean | C r1 / r2 $ | C mean | Saving | C result | C subagents r1 / r2 |
| --- | --- | --- | --- | --- | --- | --- |
| 21 Module summaries | 0.69 | 0.48 / 0.65 | 0.56 | 18% | 76/76 both; ~6.2k and ~6.1k words | 4 / 4 |
| 22 Docs vs code | 1.70 | 0.81 / 0.87 | 0.84 | 51% | 9 and 10 of 12 verified issues | 7 / 6 |
| **Total** | **2.38** | **1.29 / 1.52** | **1.41** | **41%** | | 21 haiku |

Mismatches 0. The checker's own estimate was an 84% saving. Wall time isn't comparable: C r2 on 21 finished its summaries early, then kept the session open about 25 minutes on a "backup timer" Opus set in case an agent hung (1854 s in all, at little cost). The other three C runs took 143-270 s each.

Forced Haiku was cheaper than forced Opus on both tasks, and on the docs check it found as much as forced Opus (9 and 10 of 12, against 10 and 10) while costing half. Both C runs also reported claims outside the 12-issue list (`Live` reusing the global console, the style-name rule, the `track()` refresh wording, the `from_ansi` example); these weren't verified and aren't counted. In C r1, one Haiku agent tried to `rm` a file in its bench clone; the permission guard blocked it.

### D: Opus only, spontaneous (no skill) (r1, r2; 2026-10-31)

| Task | A mean | D r1 / r2 $ | D mean | Saving | D result |
| --- | --- | --- | --- | --- | --- |
| 21 Module summaries | 0.69 | 0.45 / 0.35 | 0.40 | 42% | 76/76 both; ~3.4k and ~2.9k words |
| 22 Docs vs code | 1.70 | 1.78 / 1.53 | 1.66 | 3% | 8 and 9 of 12 verified issues (11 combined) |
| **Total** | **2.38** | **2.23 / 1.88** | **2.06** | **14%** | 0 subagents |

Wall time: D 742 s (-8% vs A). Opus again worked alone, reading the code itself even for "summarise every module". Per run it found slightly fewer doc issues than forced Opus (8, 9 against 10, 10), but its two runs found different ones, so pooled they cover 11 of 12.

## Task set 4: ~50k-line codebase (beets, tasks 31-33)

Prompts in `data/tasks-v4.md`: beetbox/beets at `ab4bdfd`, 167 modules (~52k lines) in `beets/` and `beetsplug/`, far less famous than rich. Three tasks: summarise every module (31), check `docs/reference/` (5 pages, 2.8k lines) against the code (32), check `docs/plugins/` (80 pages, 8.3k lines) against the code (33). Three arms, each run twice: A forced Opus (`no routing.`; Agent tool blocked except in 32 `r1`/`r2`), B routed, and **C forced Haiku** (`Use the model-router skill. use haiku.`: every subagent on Haiku). All with the current global CLAUDE.md. The spontaneous arm (D) is in its own section below.

| Task | A run 1 / 2 $ | B run 1 / 2 $ | C run 1 / 2 $ | A mean | B mean (vs A) | C mean (vs A) |
| --- | --- | --- | --- | --- | --- | --- |
| 31 Module summaries | 1.47 / 1.38 | 2.28 / 2.34 | 0.84 / 0.73 | 1.43 | 2.31 (-62%) | 0.79 (45%) |
| 32 Docs check, reference | 2.77 / 2.95 | 2.35 / 1.82 | 1.22 / 0.90 | 2.86 | 2.09 (27%) | 1.06 (63%) |
| 33 Docs check, plugins | 9.39 / 9.01 | 3.82 / 4.07 | 1.42 / 1.55 | 9.20 | 3.95 (57%) | 1.49 (84%) |
| **Total** | **13.63 / 13.34** | **8.45 / 8.23** | **3.48 / 3.18** | **13.49** | **8.34 (38%)** | **3.33 (75%)** |

Percentages are savings (positive = cheaper than A). Mismatches 0, fallbacks 0. Checker's own estimate: 34% saving for B, 85% for C.

| Task | A | B | C |
| --- | --- | --- | --- |
| 31 coverage | 167/167 both | 167/167 both | 167/167 both |
| 31 "works with" links backed by a real import | 98%, 97% | 95%, 94% | 98%, 97% |
| 32 issues found (of 35 verified) | 10, 16 | 18, 13 | 20, 11 |
| 33 issues found (of 51 verified) | 38, 34 | 27, 27 | 26, 29 |
| 33 re-checked (of 61 verified, 2026-11-04) | 41, 33 | 30, 28 | 30, 30 |
| Wall time per run, 31 / 32 / 33 | ~300 / ~325 / ~890 s | ~186 / ~210 / ~190 s | ~176 / ~336 / ~260 s |
| Subagents | 0 | 13 / 10 / 16, all Sonnet | 14 / 10 / 16, all Haiku |

How it was scored:
- **31:** coverage and every `beets.*`/`beetsplug.*` module a summary mentions, checked by script against the real import graph (mentions with no import either way are plausible indirect links, not counted as errors). A run 1 also named two module paths that no longer exist (`beets.vfs`, `beets.art`). A hand check of 10 Haiku paragraphs (~40 facts) found 1 small error and 1 omission.
- **32 and 33:** the union of every run's findings, each checked against the code (and against the `confuse` library for config-file claims). 32: 35 confirmed, 1 false positive (an A run). 33: 51 confirmed, 2 false positives (one A run, one claim made by both an A run and a B run), and about 24 borderline or single-run claims left uncounted, most of them from C r2. In B and C, Opus re-checked every subagent finding before answering, and in one C run it added two issues the Haiku agents missed, so C's quality is partly Opus's.
- **Tags:** 31's A runs are `r1n`/`r2n` (Agent tool blocked); B's runs of 31/32 are `r3`/`r4`. Most of 33's first runs hit the usage limit after ~3 minutes; the complete re-runs are `r1b`/`r2b` (B r2 completed first time).

What task set 4 shows:

- **On the biggest job, routing finally saved money.** On 33 (80 doc pages) A had to read everything in one long session ($9.20, ~15 min); B and C split the pages across 8 parallel subagents and finished in 3-4 minutes for 57% and 84% less.
- **But the savings cost thoroughness there.** On 33, A found 34-38 of 51 issues per run; B and C found 26-29. On the two smaller tasks, quality was level. (Re-checked on 2026-11-04 with every claim verified: A 41 and 33 of 61, B 30 and 28, C 30 and 30; see "Re-check of task 33" below.)
- **Haiku is where the money is, and the skill never picks it on its own for this work.** B sent every batch to Sonnet ("needs code comprehension"); forcing Haiku saved 45-84% per task.
- **Haiku's long-prompt rate matters.** Haiku 5.5 costs 5x more on prompts over 100K tokens; up to 45 of a C run's Haiku requests crossed that line. Pricing it raised C's cost by up to 36% on a task, without changing the result.

### D: Opus only, spontaneous (no skill) (r1, r2; 2026-10-31 to 2026-11-01)

| Task | A mean | D r1 / r2 $ | D mean | Saving | D result |
| --- | --- | --- | --- | --- | --- |
| 31 Module summaries | 1.43 | 0.95 / 1.05 | 1.00 | 30% | 167/167 both; links 98% and 97% import-backed |
| 32 Docs check, reference | 2.86 | 2.17 / 2.21 | 2.19 | 23% | 10 and 9 of 35 (12 combined) |
| 33 Docs check, plugins | 9.20 | 6.15 / 5.87 | 6.01 | 35% | 24 and 29 of 51 (30 combined) |
| **Total** | **13.49** | **9.27 / 9.13** | **9.20** | **32%** | 0 subagents |

Wall time per run, 31 / 32 / 33: ~240 / ~265 / ~520 s. No `Skill` calls, no routing-log lines. The first 33 runs (`r1`, `r2`) hit the usage limit after 66 pages and are not used; the complete re-runs are `r1b`/`r2b`.

- **Plain Claude Code never delegated, even on 80 pages.** Every D run on every set used 0 subagents.
- **Cheaper than forced Opus, through shorter sessions.** On 32, D made 52-53 requests and re-read 5.5-5.8M cached tokens; A made 65-66 and re-read 7.6-8.1M. On 33, D made 78 and 121 requests against about 140-175 for A.
- **Less thorough on the big audit.** On 33, D found 24 and 29 of 51 issues, against 38 and 34 for forced Opus, about the same as the delegated arms (26-29) at four times forced Haiku's cost. On 32, it found 10 and 9 of 35, the fewest of any arm.
- **One new verified issue,** found by both D runs on 32 and not in the 35-issue list (so not counted): `config.rst` says `max_filename_length` is a number of characters, but `truncate_str` truncates `os.fsencode(s)`, i.e. bytes.
- **Not counted:** each 33 run repeated the `musicbrainz` `external_ids` beatport claim already judged false. Other claims outside the 51-issue list (embedart `quality` ignored on auto-embed, deezer `rank` vs `deezer_track_rank`, lyrics USLT timestamps, metasync `source` splitting, a "playlists" wording in playlist.rst) were not verified. D r1's summaries also used the stale `beets.art` / `beets.vfs` paths, as A r1 did.

## Follow-up: why forced Opus cost more than spontaneous Opus (2026-11-01)

Forced Opus (A) and spontaneous Opus (D) both ran Opus alone, yet A cost more on every set and, on the 80-page beets check, found far more. Three differences could explain it: A's `no routing.` prefix, A's older global CLAUDE.md and earlier date, and the tool setup (A leaves the Skill tool and skill list visible, and its later runs block the Agent tool; D blocks the Skill tool and allows Agent). A r1/r2 on 32 ran before the Agent block was added, so they had the Agent tool available. Task 32 (beets reference docs) was run twice more as A, today with the current CLAUDE.md (`r3`, `r4`), and twice as **arm E**: D plus the `no routing.` prefix (`--disallowedTools Skill`, Agent allowed). A second round isolated the Agent tool: **arm F** is D with the Agent tool blocked too (`--disallowedTools Agent,Skill`, no prefix), run three times, plus a third D run.

| Variant | Issues found (of 35) | Combined | Est. $ per run | Requests | Output tokens | Wall time | First prompt |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A r1 / r2 (2026-10-30) | 10, 16 | 17 | 2.77 / 2.95 | 66 / 65 | 22.5k / 25.4k | 306 / 343 s | 34.6k / 36.5k |
| A r3 / r4 (today) | 12, 14 | 16 | 3.44 / 3.16 | 78 / 69 | 27.4k / 25.9k | 428 / 447 s | 32.0k / 32.0k |
| D r1 / r2 | 10, 9 | 12 | 2.17 / 2.21 | 53 / 52 | 16.5k / 17.7k | 266 / 261 s | 31.9k / 31.9k |
| E r1 / r2 (D + `no routing.`) | 8, 9 | 11 | 2.48 / 3.00 | 58 / 73 | 18.9k / 22.3k | 249 / 310 s | 30.0k / 30.0k |
| D r3 (today) | 13 | - | 3.02 | 77 | 22.2k | 377 s | 30.0k |
| F r1 / r2 / r3 (D + Agent blocked) | 12, 11, 13 | - | 2.93 / 2.82 / 2.92 | 66 / 58 / 65 | 22.8k / 21.1k / 24.5k | 282 / 383 / 303 s | 27.7k |

0 subagents in every run. Output tokens include thinking. Scored as before: only claims a run states as wrong count; config-path claims a run marked as unverified (they live in the `confuse` library) don't. Every new run also reported the `max_filename_length` bytes issue, which stays outside the 35.

What the transcripts show (the thinking text itself is encrypted, so only its volume and the working pattern can be measured):

| Task 33, plugin docs | Output tokens | Thinking blocks | Issues found (of 51) |
| --- | --- | --- | --- |
| A r1b / r2b | 50.2k / 43.9k | 216 / 205 | 38 / 34 |
| D r1b / r2b | 34.4k / 30.7k | 175 / 59 | 24 / 29 |

- **Forced Opus puts in more effort.** Every A run produced more output than every D run on the same task (32: 22.5-27.4k against 16.5-22.2k; 33: 44-50k against 31-34k). On 32, the chance of that ordering by luck is about 3%.
- **It works more methodically on long jobs.** On 33, both A runs went one plugin at a time (read the doc page, read that plugin's code, check, move on). D r2b read 5-10 pages per command and thought about a third as much.
- **Not the old CLAUDE.md or the date.** Run today with the same prompt size as D, A was again the most effortful and thorough (12 and 14).
- **Neither the prefix nor the Agent block reproduces it alone.** The prefix without the skill list (E: 8 and 9 issues) and the Agent block without the prefix (F: 12, 11 and 13) both landed between D and A. The Agent block isn't required: A r1/r2 had the Agent tool and still out-produced D. What every A run had is the `no routing.` instruction with the router skill visible, so the instruction may read differently when Opus can see the skill it's being told not to use. Untested.
- **Run-to-run variance is still large.** A found 10 to 16 issues across four runs, and D r3 ran as long as A (77 requests, 13 issues). Within D, more thinking didn't mean more found (r1b thought most and found 24; r2b least and found 29). The direction is consistent; the size of the effect is uncertain with 2-4 runs per variant.

## Doc checks: both runs combined

Distinct verified issues found by a setup's two runs together. A setup whose runs find different issues covers more ground when pooled; one whose runs overlap doesn't gain much.

| Docs check | Opus only, forced | Opus only, spontaneous | Skill-routed | Forced Haiku |
| --- | --- | --- | --- | --- |
| Task 15, my project (of 9) | 7, 8 → 8 | 5, 7 → 7 | 5, 6 → 9 | 3, 2 → 4 |
| Task 22, rich (of 12) | 10, 10 → 10 | 8, 9 → 11 | 6, 9 → 10 | 9, 10 → 11 |
| Task 32, beets reference (of 35) | 10, 16 → 17 | 10, 9 → 12 | 18, 13 → 23 | 20, 11 → 24 |
| Task 33, beets plugins (of 51) | 38, 34 → 45 | 24, 29 → 30 | 27, 27 → 31 | 26, 29 → 34 |
| Task 33 re-checked (of 61, see below) | 41, 33 → 44 | 27, 35 → 36 | 30, 28 → 35 | 30, 30 → 39 |

Forced Opus's two runs overlap heavily (on rich they found exactly the same 10). The delegated setups' runs overlap less, so pooled they cover more on the smaller doc sets, but on the 80-page plugin check forced Opus still covers the most. Spontaneous Opus works alone too, but with shorter sessions it covers less than forced Opus on both beets checks.

## Re-check of task 33, beets plugin docs (2026-11-04)

A reader asked how the 51-issue list was built: if it leaned on the Opus runs, anything Haiku found outside it couldn't score. The list was the union of the A, B and C runs' findings, checked against the code by Claude Opus, but about 24 borderline or single-run claims had been left unverified (most from a Haiku run), and the list itself was never saved. So task 33 was re-scored the way v2 is: every claim from all 8 complete runs (A r1b/r2b, B r1b/r2, C r1b/r2b, D r1b/r2b), single-run ones included, grouped by page and checked against beets at `ab4bdfd`, again by Claude Opus. Borderline errors (same effect in practice, wrong counts, wording) are counted and flagged; about 20 claims that couldn't be confirmed or refuted from the code are left out and listed.

| | Forced Opus (A) | Spontaneous Opus (D) | Skill-routed (B) | Forced Haiku (C) |
| --- | --- | --- | --- | --- |
| v1 score (of 51) | 38, 34 → 45 | 24, 29 → 30 | 27, 27 → 31 | 26, 29 → 34 |
| Re-checked (of 61) | 41, 33 → **44** | 27, 35 → 36 | 30, 28 → 35 | 30, 30 → **39** |
| Strict, without borderline (of 41) | 32, 26 → 34 | 24, 27 → 28 | 22, 21 → 24 | 22, 25 → 29 |

- **Haiku was undercounted, and so were the others.** Per run, every setup gained; combined, Haiku gained the most (+5) and forced Opus went from 45 to 44. The two passes grouped and excluded claims slightly differently, so shifts of one or two are noise.
- **The conclusion holds.** Forced Opus is still the most thorough on the 80-page check, by 5 combined instead of 11 (by 5 strict).
- **The forced vs spontaneous gap shrinks.** Spontaneous Opus's r2b now scores 35, above forced Opus's r2b (33); combined, 36 against 44. Forced Opus still out-produces it, but "found far more" overstated it.
- About 20 claims left out (not verified), from all setups. Same caveat as before: "of 61" counts errors found by any run, not true recall, and the judge is an Opus model.

## Across all three sets

The checker's "saving vs forced Opus" estimate overstated every routed set:

| Setup | Checker's estimated saving | Head-to-head vs forced Opus |
| --- | --- | --- |
| Everyday tasks, B skill-routed | 44% | 14% more expensive |
| Everyday tasks, C forced Haiku | 68% | 5% cheaper |
| Reading-heavy tasks, B skill-routed | 52% | 30% more expensive |
| Reading-heavy tasks, C forced Haiku | 77% | break-even |
| rich, B skill-routed | 45% | 11% more expensive |
| rich, C forced Haiku | 84% | 41% cheaper |
| beets, B skill-routed | 34% | 38% cheaper |
| beets, C forced Haiku | 85% | 75% cheaper |

The estimate overstated the saving on every set except beets B, where it understated it slightly. Forced Haiku is the only routed arm that never cost more than forced Opus.

Spontaneous Opus (D) used no subagents anywhere, so the checker has nothing to re-price (estimate 0%). Head-to-head it cost 1% less than forced Opus on everyday tasks, 16% less on reading-heavy, 14% less on rich and 32% less on beets. Only the head-to-head numbers measure the real effect.

## v2, Part 1: ~100k-line codebase (buildbot, tasks 41-43; 2026-11-03 to 2026-11-04)

Prompts in `data/tasks-v5.md`: buildbot/buildbot at `c5cdcf3`, 408 hand-written modules (~91k lines) in `master/buildbot/` and `worker/buildbot_worker/`, excluding their `test/` packages. Three tasks, mirroring beets 31-33: summarise every module (41), check `changesources.rst` + `schedulers.rst` (3.7k lines) against the code (42), check the 85 pages in `steps/`, `reporters/` and `report_generators/` (6k lines) against the code (43). Each run cloned a one-commit local copy, so `git log` couldn't reveal anything.

**Planted errors.** Before any run, 30 one-line doc edits were planted in that copy (10 in task 42's pages, 20 in task 43's: wrong defaults, renamed parameters, wrong module paths), each with a code reference, so recall on them is true recall. Real (non-planted) errors were collected from every run's findings and verified against the unmodified checkout, as in v1. They're reported separately and never added to the planted count.

**Arms.** New baseline **F**, Opus only, blocked: no prompt prefix, Agent and Skill tools blocked, so no wording effect and no way to delegate. **D** Opus only, spontaneous (Skill blocked, Agent allowed), **B** skill-routed and **C** forced Haiku as before, with the same v1 skill. Each arm ran twice, interleaved; task 41 got a third F and C run because C's two costs were far apart. Percentages are against F.

### Costs

| Task | F | D | B | C |
| --- | --- | --- | --- | --- |
| 41 Module summaries | 2.70 / 3.40 / 3.61 → **3.24** | 3.46 / 2.46 → **2.96 (-9%)** | 5.06 / 3.52 → **4.29 (+32%)** | 1.08 / 3.03 / 1.11 → **1.74 (-46%)** |
| 42 Reference docs (2 pages) | 1.56 / 1.72 → **1.64** | 1.16 / 1.41 → **1.29 (-22%)** | 1.83 / 2.21 → **2.02 (+23%)** | 0.81 / 0.72 → **0.77 (-53%)** |
| 43 Steps and reporters docs (85 pages) | 3.96 / 4.25 → **4.11** | 4.19 / 3.84 → **4.02 (-2%)** | 3.84 / 3.92 → **3.88 (-5%)** | 1.85 / 2.01 → **1.93 (-53%)** |
| **All three, mean per run** | **8.98** | **8.26 (-8%)** | **10.19 (+13%)** | **4.44 (-51%)** |

Mismatches 0, fallbacks 0 in every run. The checker's own estimate (delegated tokens re-priced at Opus rates) was a 32-39% saving for B and 82-88% for C; head to head, B cost 5% less to 32% more, and C 46-53% less.

| | F | D | B | C |
| --- | --- | --- | --- | --- |
| Wall time per run, 41 / 42 / 43 | ~615 / ~170 / ~400 s | ~670 / ~160 / ~535 s | ~265 / ~160 / ~270 s | ~265 / ~180 / ~390 s |
| Subagents per run, 41 / 42 / 43 | 0 | 0 | 9-10 / 4 / 5-7, all Sonnet | 10-12 / 4-6 / 6-7, all Haiku |

C r2 on 41 is the outlier ($3.03): its Haiku batches grew past 100K-token prompts (Haiku's 5x long-prompt rate) and it wrote twice as much (~30k words). The other two C runs cost $1.08 and $1.11.

### Quality

| | F | D | B | C |
| --- | --- | --- | --- | --- |
| 41 coverage (of 400) | 400, 400, 400 | 400, 400 | 400, 400 | 400, 400, 400 |
| 41 "works with" links backed by a real import | 98%, 88%, 88% | 83%, 87% | 86%, 83% | 88%, 86%, 89% |
| 42 planted errors (of 10) | 10, 10 | 10, 10 | 10, 10 | 10, 10 |
| 42 real errors (of 42 verified) | 10, 17 → 22 | 9, 9 → 12 | 17, 21 → 26 | 20, 23 → **28** |
| 43 planted errors (of 20) | 20, 20 | 20, 20 | 20, 20 | 20, 20 |
| 43 real errors (of 92 verified) | 36, 38 → 49 | 39, 35 → 43 | 55, 70 → **77** | 58, 63 → 72 |

"→" is the two runs combined. Without the borderline errors (task 42: 33 strict, task 43: 71 strict) the order is the same: on 42, F 18, D 11, B 24, C 24 combined; on 43, F 45, D 42, B 66, C 58.

How it was scored:
- **41:** `scripts/score_summaries.py` checks that every module has a heading, and checks every project module a section names against the AST import graph (in either direction). Mentions without an import are plausible indirect links, not errors. The 8 modules in buildbot's secret-provider package (`master/buildbot/secrets`) are left out of every run's score: a local permission rule blocked shell commands naming that path, and several runs also declined to read it, so coverage there measured the rule, not the setup. F r1's 98% came from computing every import with a script; the other runs listed fewer or looser links.
- **42 and 43:** a run "found" an error when it named the page and the claim. The automatic scorers (`data/ground-truth/score42.py`, `score43.py`, local only) match line numbers within one line; a handful of correct finds with wrong line numbers (on 43: 2 in F r2, 5 in B r2) were counted by content. Real errors are the union of every run's claims, each checked against the unmodified code: 42 on task 42, 92 on task 43. About 15 claims couldn't be confirmed or refuted quickly and are left out, not counted as wrong; false positives weren't counted per run. "Of 42" and "of 92" count errors found by any run, not true recall; only the planted counts are true recall.
- **Tags:** 42 C r1 and 43 B r2 hit the usage limit on their first attempt (one at 0 tokens, one after $0.77 of an unfinished run); both were deleted and re-run under the same tag.

What Part 1 shows:

- **Forced Haiku halved the cost on every task** (-46%, -53%, -53%) and found more real doc errors than Opus alone on both doc checks (per run, 20-23 against 9-17 on 42, and 58-63 against 35-39 on 43). On 42 its Haiku readers plus Opus re-checking beat every other setup; on 43 only B found more.
- **This reverses beets.** There, forced Opus found the most on the 80-page check (44 of 61 after the re-check, against 35-39). At 100k lines, Opus alone made 80-105 turns and still covered less than 4-7 parallel readers whose findings Opus then re-checked.
- **The skill still picked Sonnet for everything** ("needs code comprehension") and saved at most 5% against F. It was the most thorough on 43 (70 real errors in one run) and the fastest on 41 and 43.
- **Opus left alone never delegated** (0 subagents in 6 D runs) and cost about the same as F, so blocking delegation changed nothing measurable here. D found the fewest real errors on 42.
- **The planted errors were too easy.** Every run caught all 30, so the real errors are what separate the setups.
- **Run-to-run variance is large.** F's three 41 runs cost $2.70-3.61 and backed 88-98% of links; one C run cost 2.8x the other two.

## v2, Part 2: building tasks on the small codebase (tasks 51-52; 2026-11-04)

Task descriptions in `data/tasks-v6.md`: the same private ~10k-line project as sets 1-2 (214 unit tests). These tasks write code instead of reading it. **51:** a well-specified feature, an optional validated field on a config record, touching the model, parsing and saving, the CLI, docs and tests (7-9 files changed). **52:** a bug hunt from a user's symptom: one bug planted in the config writer's string escaping before any run, in a one-commit copy of the project. The existing suite doesn't catch it. Same arms as Part 1 (F baseline, D, B, C), each run twice.

**Scoring.** A hidden test file for each task, written before any run and checked to fail on the unmodified code, was copied into the clone after the run (9 tests for 51; 4 for 52, one of which tries every printable character after a backslash). Then the whole unit suite was run, including the tests the run itself wrote.

| Task | F r1 / r2 $ | D r1 / r2 $ | B r1 / r2 $ | C r1 / r2 $ |
| --- | --- | --- | --- | --- |
| 51 Feature | 0.54 / 0.80 | 0.73 / 0.68 | 0.60 / 0.69 | 0.38 / 0.54 |
| Mean (vs F) | **0.67** | **0.71 (+5%)** | **0.65 (-4%)** | **0.46 (-31%)** |
| 52 Bug hunt | 0.17 / 0.26 | 0.39 / 0.27 | 0.37 / 0.43 | 0.22 / 0.26 |
| Mean (vs F) | **0.22** | **0.33 (+53%)** | **0.40 (+86%)** | **0.24 (+12%)** |

| | F | D | B | C |
| --- | --- | --- | --- | --- |
| Hidden tests passed | all, all 4 runs | all, all 4 runs | all, all 4 runs | all, all 4 runs |
| Full suite | pass | pass | pass | pass |
| Wall time 51, r1 / r2 | 84 / 143 s | 134 / 138 s | 137 / 207 s | 120 / 209 s |
| Wall time 52, r1 / r2 | 51 / 64 s | 107 / 62 s | 58 / 98 s | 83 / 289 s |
| Subagents 51, r1 / r2 | 0 | 0 | 1 Sonnet / 1 Haiku + 1 Sonnet | 1 Haiku / 1 Haiku |
| Subagents 52, r1 / r2 | 0 | 0 | 0 (kept inline) / 1 Sonnet | 1 Haiku / 1 Haiku |

Mismatches 0, fallbacks 0; no `Skill` calls or routing-log lines in the D runs. All 16 runs together cost $7.33.

What Part 2 shows:

- **Quality didn't separate the setups.** All 16 runs passed everything. These tasks were too easy to expose a gap, so this doesn't show that Haiku codes as well as Opus. It shows Haiku can do a small, well-specified job with Opus reviewing, and in C on 51 Opus's review added a small validation fix of its own in one run, so C's quality is partly Opus's.
- **The feature: forced Haiku was cheapest** (-31%), though slower than Opus alone because of the hand-off. Almost all of a C run's cost is Opus: Haiku's share was 2-3 cents, Opus's 37-51.
- **The small fix: Opus alone was cheapest and fastest.** On a job this small, delegation overhead outweighs the cheaper tokens. In one run Haiku took 17 requests and nearly 5 minutes for a fix Opus alone made in about a minute, at the same cost.
- **The skill isn't free.** On 52 r1 it correctly kept the fix inline with no subagent, and still cost about twice F's run, because of loading the skill and logging.
- **Opus left alone never delegated** (0 subagents in 4 more D runs; 0 in 10 across v2).
- **Next: harder coding tasks**, such as a vaguely specified feature, a multi-file refactor or a subtler bug, where a quality gap could actually appear.
- **Variance is large relative to the gaps.** F's own two runs on 51 differ by 48%, and the differences between setups are under $0.30 per run. With 2 runs per setup, only C's feature saving stands out.
