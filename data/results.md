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

## v2, Part 3: harder building tasks on the small codebase (tasks 53-55; 2026-11-05 to 2026-11-06)

Task descriptions, scoring definitions and SHA-256 hashes of the private prompts and hidden tests are in `data/tasks-v7.md`, committed before any run (`4ac6b5d`). Same private project (baseline `a3c99c4`, 214 unit tests) and same arms as Part 2, each run twice, interleaved across arms. All 24 runs used Claude Code 2.1.317. **53:** a real bug in the project's start-at-login feature, where the obvious one-line fix fails. **54:** a vaguely worded feature, renaming a profile. **55:** split the ~700-line CLI module, with no behaviour change and no edits to existing tests. For 55, scoring restored the existing tests from the baseline first.

| Task | F r1 / r2 $ | D r1 / r2 $ | B r1 / r2 $ | C r1 / r2 $ |
| --- | --- | --- | --- | --- |
| 53 Domain trap | 0.73 / 0.52 | 0.69 / 0.70 | 0.51 / 0.64 | 0.42 / 0.28 |
| Mean (vs F) | **0.63** | **0.69 (+11%)** | **0.57 (-8%)** | **0.35 (-44%)** |
| 54 Vague feature | 1.04 / 0.98 | 1.15 / 0.94 | 1.17 / 1.36 | 0.74 / 0.68 |
| Mean (vs F) | **1.01** | **1.04 (+3%)** | **1.26 (+25%)** | **0.71 (-30%)** |
| 55 Refactor | 0.78 / 0.77 | 0.88 / 0.86 | 1.10 / 1.01 | 0.77 / 0.70 |
| Mean (vs F) | **0.77** | **0.87 (+13%)** | **1.05 (+36%)** | **0.74 (-5%)** |
| All three, mean per run (vs F) | **2.41** | **2.61 (+8%)** | **2.89 (+20%)** | **1.80 (-25%)** |

Hidden tests, passed of total, r1 / r2. The whole suite without the hidden test passed in all 24 runs (see the flake note below):

| Task | F | D | B | C |
| --- | --- | --- | --- | --- |
| 53 (of 9) | 9 / 9 | 9 / 9 | 9 / 9 | 9 / 9 |
| 54 (of 12) | 12 / 11 | 12 / 11 | 12 / 11 | 12 / 11 |
| 55 (of 22) | 22 / 22 | 22 / 22 | 22 / 22 | 22 / 22 |
| Subagents per run | 0 | 0 | 53, 55: 1 Sonnet; 54: 1 Haiku + 1 Sonnet | 53, 55: 1 Haiku; 54: 2 Haiku / 1 Haiku |

Mismatches 0, fallbacks 0; no `Skill` calls or routing-log lines in the D runs. All 24 runs together cost $19.41. D has now made no subagent call in 16 v2 runs.

Means per run, from `scripts/run_metrics.py`. Code lines exclude tests and docs. "Check" is the post-edit check cost as defined in `data/tasks-v7.md`. Edit counts include shell commands that write files, detected by a heuristic.

| Task, arm | Code +/- | Test lines + | Complexity added | Opus $ | Subagents $ | Check $ (share) | Suite runs | Edits | Rework | Wall min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 53 F | 3.5 / 1 | 46.5 | 0 | 0.63 | 0 | 0.04 (7%) | 4.5 | 5 | 3 | 1.9 |
| 53 D | 4 / 1 | 34.5 | 0 | 0.69 | 0 | 0.15 (22%) | 4.5 | 4.5 | 0.5 | 3.7 |
| 53 B | 4 / 1 | 13 | 0 | 0.32 | 0.25 | 0.15 (26%) | 2 | 2 | 0 | 2.0 |
| 53 C | 2.5 / 1 | 33 | 0 | 0.32 | 0.03 | 0.10 (28%) | 7 | 7 | 5 | 2.9 |
| 54 F | 111 / 7.5 | 167 | 32 | 1.01 | 0 | 0.10 (10%) | 3.5 | 8 | 3.5 | 4.3 |
| 54 D | 106 / 10 | 164 | 33 | 1.04 | 0 | 0.10 (9%) | 4.5 | 3.5 | 2.5 | 4.2 |
| 54 B | 88 / 5 | 174.5 | 28 | 0.87 | 0.40 | 0.45 (35%) | 4.5 | 4 | 2.5 | 6.0 |
| 54 C | 70 / 5 | 138 | 21 | 0.61 | 0.10 | 0.12 (17%) | 6 | 16.5 | 1.5 | 7.1 |
| 55 F | 842 / 649 | 48 | 4 | 0.77 | 0 | 0.20 (26%) | 2.5 | 1 | 0 | 3.3 |
| 55 D | 714.5 / 567 | 45.5 | 4 | 0.87 | 0 | 0.12 (14%) | 3.5 | 2 | 1 | 3.8 |
| 55 B | 815 / 606 | 48.5 | 4.5 | 0.77 | 0.28 | 0.33 (31%) | 7 | 5.5 | 3.5 | 4.9 |
| 55 C | 690 / 565.5 | 0 | 2.5 | 0.71 | 0.02 | 0.22 (31%) | 3.5 | 3.5 | 0 | 4.4 |

The same measures on Part 2:

| Task, arm | Code +/- | Check $ | Suite runs | Rework |
| --- | --- | --- | --- | --- |
| 51 F | 43.5 / 5 | 0.08 | 2 | 0.5 |
| 51 D | 45 / 5 | 0.07 | 2 | 0 |
| 51 B | 35.5 / 5 | 0.17 | 2.5 | 1 |
| 51 C | 37.5 / 5 | 0.15 | 5.5 | 3.5 |
| 52 F | 3 / 4 | 0.03 | 2.5 | 1 |
| 52 D | 2.5 / 4 | 0.04 | 4 | 1.5 |
| 52 B | 2 / 4 | 0.07 | 3.5 | 1.5 |
| 52 C | 6 / 7 | 0.08 | 4 | 1 |

What Part 3 shows:

- **Quality still didn't separate the setups.** No run fell for the trap on 53, Haiku included. Opus reviews and tests in every setup, so a helper's mistake may be fixed before scoring; the cost of that shows up as checking and rework instead of a lower score. These results support "Opus plus Haiku holds up", not "Haiku alone is as good as Opus".
- **Forced Haiku was cheapest on all three, by very different margins:** -44%, -30% and -5%. On the refactor the writing is mechanical, and Opus's own reading and checking dominate. Almost all of a C run's cost is Opus.
- **It was also slower** than F on all three tasks, by the wall-time means above.
- **Delegating moves cost into checking.** B and C spent 17-35% on checking against 7-26% for F. The largest single case is 54 B r2, at 56%.
- **No over-engineering from cheaper helpers.** On 54, F and D wrote the most code and added the most complexity.
- **The skill was the most expensive setup on 54 and 55**, with no better scores.

**A flaw in my hidden test for 54.** `test_keeps_other_fields_and_order` compares whole records, so a run that adds an optional field to the record fails it, even with every original field kept. Runs F r2, D r2, B r2 and C r2 lost their point this way. D r1 added a similar field but left it empty in this test's case, so it passed. The test wasn't changed after seeing results, so the scores stand as above. Each of those fields is there to keep a renamed profile linked to its entry in the GUI's app menu, a requirement I hadn't thought of when designing the task. 5 of 8 runs handled it: F 1, D 2, B 1, C 1. That count comes from reading the diffs, wasn't defined before the runs, and those links weren't tested separately.

**A flaky existing test.** An IPC test in the project, `test_errors_are_replies_not_crashes`, fails rarely. The combined suite showed one failure once each on 55 B r1 and 55 B r2 during scoring, with hidden tests at 22 of 22 and the suite passing without the hidden test. Repeat runs of B r1 caught this test failing in 1 of 14, and B r2 passed all 9 repeats. D r2 on 53 also reported an intermittent error in the same test, in 1 of 96 parallel runs. The named failure was only captured in the B r1 repeat, so the two scoring failures are attributed to it, not confirmed. Both B runs are counted as passes.

**Limits.** Two runs per setup. The tasks were designed after seeing that Haiku did well on 51-52, which could bias them, and committing them before any run reduces that risk without removing it. The task designer knew the project's code, and a task the designer can solve in a reference fix may be easier than real work.

**Next:** coding tasks on a much bigger codebase, a bug the existing tests can't reveal, and a bug whose symptom appears far from its cause, as new task numbers.

## v2, Part 4: coding tasks on buildbot (tasks 56-57; 2026-11-06)

Design, scoring rules and hashes of the private files are in `data/tasks-v8.md`, committed before any run (`c6b8cd7`, amended before any run in `9847b2d`). Project: buildbot at `c5cdcf3`, with its pinned test requirements in a venv; the unit suite ran 6,448 tests on this setup, all passing or skipped. Same arms as Parts 2-3, each run twice, interleaved across arms. All 16 runs used Claude Code 2.1.317.

**56:** add `/api/v2/builders/{builderid_or_buildername}/result_counts`, returning the number of finished builds per result. It must follow the API's conventions, including its specification, and stay fast on a builder with millions of builds. **57:** a blamelist bug report. One line was removed from `getParentChangeIds` in `master/buildbot/db/changes.py` (its branch filter), so a change's parent can be on another branch. The symptom shows in the build's changes and in notifications. The whole unit suite still passes with the plant in place.

| Task | F r1 / r2 $ | D r1 / r2 $ | B r1 / r2 $ | C r1 / r2 $ |
| --- | --- | --- | --- | --- |
| 56 Endpoint | 1.07 / 1.26 | 1.09 / 1.04 | 1.20 / 1.13 | 0.85 / 1.01 |
| Mean (vs F) | **1.16** | **1.07 (-8%)** | **1.17 (0%)** | **0.93 (-20%)** |
| 57 Far-off bug | 0.67 / 0.90 | 0.82 / 0.80 | 0.80 / 0.51 | 0.30 / 0.55 |
| Mean (vs F) | **0.79** | **0.81 (+3%)** | **0.65 (-17%)** | **0.43 (-46%)** |
| Both, mean per run (vs F) | **1.95** | **1.88 (-4%)** | **1.82 (-7%)** | **1.36 (-30%)** |

Hidden tests, passed of total, r1 / r2. The whole unit suite without the hidden test passed in all 16 runs:

| Task | F | D | B | C |
| --- | --- | --- | --- | --- |
| 56, official (of 13) | 9 / 9 | 9 / 9 | 9 / 13 | 13 / 9 |
| 56, corrected test data (of 13) | 13 / 13 | 13 / 13 | 13 / 13 | 13 / 13 |
| 57 (of 8) | 8 / 8 | 8 / 8 | 8 / 8 | 8 / 8 |
| Subagents, 56 | 0 | 0 | 1 Haiku + 1 Sonnet each | 2 Haiku each |
| Subagents, 57 | 0 | 0 | 1 Haiku + 1 Sonnet / 1 Haiku | 1 Haiku / 2 Haiku |

Mismatches 0, fallbacks 0; no `Skill` calls or routing-log lines in the D runs. All 16 runs together cost $14.02. D has now made no subagent call in 20 v2 runs. The usage limit wasn't hit.

Means per run, defined as in Part 3:

| Task, arm | Code +/- | Test lines + | Complexity added | Opus $ | Subagents $ | Check $ (share) | Suite runs | Edits | Rework | Wall min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 56 F | 112 / 0 | 259 | 9 | 1.16 | 0 | 0.18 (16%) | 7.5 | 9 | 5 | 6.3 |
| 56 D | 102.5 / 0 | 197.5 | 8 | 1.07 | 0 | 0.20 (19%) | 5 | 5 | 3.5 | 5.4 |
| 56 B | 111 / 0 | 262.5 | 10 | 0.74 | 0.43 | 0.52 (44%) | 9 | 6.5 | 3 | 7.3 |
| 56 C | 109.5 / 0 | 267 | 9 | 0.88 | 0.05 | 0.31 (33%) | 8.5 | 13.5 | 8 | 7.3 |
| 57 F | 1 / 0 | 105.5 | 0 | 0.79 | 0 | 0.14 (18%) | 7 | 3.5 | 2.5 | 4.9 |
| 57 D | 1 / 0 | 100.5 | 0 | 0.81 | 0 | 0.13 (16%) | 6 | 5 | 2.5 | 4.6 |
| 57 B | 1 / 0 | 63.5 | 0 | 0.56 | 0.10 | 0.28 (43%) | 4.5 | 5 | 2.5 | 4.2 |
| 57 C | 1 / 0 | 81.5 | 0 | 0.39 | 0.04 | 0.16 (37%) | 8 | 6.5 | 3 | 5.2 |

What Part 4 shows:

- **Quality still didn't separate the setups, on a codebase about 10 times bigger.** All 8 bug runs added back the one missing line, rather than patching the symptom. All 8 endpoint runs added a database index with a migration and a spec entry. That index wasn't required by a hidden test and wasn't in the reference solution.
- **Forced Haiku was cheapest on both**, by 20% and 46%, with C r1 on 57 at $0.30 against $0.67-0.90 for Opus alone.
- **Skill routing was cheaper than F on 57**, unlike on 54 and 55. On 57 r2 it used only a Haiku subagent, and its Opus cost was the largest part.
- **Delegating costs checking.** B and C spent 33-44% on post-edit checking, against 16-19% for F and D. The largest single case is 56 B r2, at 57%.
- **Opus is doing real work.** In 56 C r2, by its own report, Opus's review fixed `row.count` in Haiku's code, which clashed with a tuple method and failed type checking, plus a repeated sentence in the docs. I didn't check whether it also failed at runtime. So part of C's result is Opus's. These results describe Opus plus Haiku, not Haiku alone.
- **Forced Haiku was not faster than Opus alone** by wall time on either task.

**A flaw in my hidden test for 56.** The test data sets `results` on finished builds but leaves `complete_at` empty, unlike real finished builds. 6 of 8 runs lost the same 4 tests because they count a build only when both are set. I read the code of F r1 and confirmed this there. The other 5 failed the same 4 tests and passed the corrected test, which is consistent with the same cause, but I didn't read each one. The official scores stand. The corrected test is a second score, written after seeing the first failure, so it isn't pre-registered. Its only change is setting `complete_at`. My reference solution had the same blind spot, which is why validating against it didn't catch this. The official numbers shouldn't be read as a quality difference.

**A flaw in my prompt for 57.** It says some `release` committers are missing from the blamelist. From reading the code, the planted bug adds wrong names but doesn't appear to lose any, though I haven't proven that. All 8 runs said they couldn't reproduce that part, and none claimed it was fixed. It may have cost them some extra investigation, equally across setups as far as I can tell.

**Limits.** Two runs per setup and two tasks. The bug is planted rather than found in the wild, and its fix is a single line next to an unused `branch` argument, a strong hint once a run gets there. These tasks were written by Claude Opus after seeing that Haiku did well, and two hidden tests in this batch and the last had flaws that only runs exposed.

**Next:** every setup so far has Opus reviewing and testing. The open question is Haiku with no Opus behind it, as a new setup on the same tasks.

## v2, Part 5: Haiku alone (setup H; tasks 53-57 and 43; 2026-11-06)

Design in `data/tasks-v9.md`. H has no prompt prefix, `--model haiku`, Agent and Skill tools blocked, effort medium, so no Opus is involved. Tasks, sources and hidden tests are unchanged. Each ran twice, on Claude Code 2.1.317 (the same version as the others), but after the other arms rather than interleaved with them. Mismatches 0, fallbacks 0, no subagents. All 12 runs together cost $4.37.

### Coding tasks (10 runs, $0.51 in total; the same 10 runs of F cost about $8.72)

| Task | H r1 / r2 $ | Mean | F mean | C mean | H vs F | Hidden tests r1 / r2 | Suite without hidden test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 53 Domain trap | 0.019 / 0.017 | **0.02** | 0.63 | 0.35 | -97% | 9 / 9 of 9 | pass |
| 54 Vague feature | 0.092 / 0.025 | **0.06** | 1.01 | 0.71 | -94% | 12 / 12 of 12 | pass |
| 55 Refactor | 0.037 / 0.032 | **0.04** | 0.77 | 0.74 | -95% | 22 / 22 of 22 | pass |
| 56 Endpoint | 0.152 / 0.118 | **0.14** | 1.16 | 0.93 | -88% | official 9 / 9, corrected 13 / 13 of 13 | pass |
| 57 Far-off bug | 0.011 / 0.012 | **0.01** | 0.79 | 0.43 | -99% | 8 / 8 of 8 | pass |

| Task, H | Code +/- | Test lines + | Complexity added | Check $ | Suite runs | Edits | Rework | Wall min (F) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 53 | 4 / 1 | 19 | 0 | 0.003 | 4 | 4 | 1 | 1.6 (1.9) |
| 54 | 63 / 3 | 134.5 | 20 | 0.028 | 3.5 | 11.5 | 2 | 2.6 (4.3) |
| 55 | 591 / 511 | 0 | 0 | 0.009 | 1.5 | 7 | 0 | 2.9 (3.3) |
| 56 | 107 / 0 | 254 | 6 | 0.081 | 4.5 | 10.5 | 2.5 | 4.1 (6.3) |
| 57 | 1.5 / 0.5 | 45.5 | 0 | 0.003 | 3 | 3 | 1 | 1.4 (4.9) |

The hidden-test results are as good as the other arms'. On 56, the official 9 of 13 reflects the test-data flaw from Part 4. On 54, both H runs scored 12 of 12: H r1 added an app-menu link in a field that stays empty in the test's case, so the strict comparison from Part 3 didn't catch it, and H r2 didn't add a link at all. So the app-menu link was handled by 1 of 2 runs, as in F, B and C. H r1 also reports an unrequested fix for the start-at-login bug from task 53. These run reports weren't verified beyond the tests.

**What the hidden tests don't score, where H differed:**

- **56, no index.** Both H runs counted in the database without adding an index and migration, while all 8 F, D, B and C runs added one. H still meets every hidden test. F r1's own benchmark suggests about 1 s without its index against 0.2 s with it on 5M builds, in-memory SQLite only.
- **57, the unreproducible symptom.** Both H runs fixed the bug correctly. Neither said it couldn't reproduce the "missing names" part of the report, while all 8 runs with Opus did. H r1's summary says the bug produced wrong authors "in both directions".

### Docs check, task 43 (2 runs)

| | F | D | B | C | H |
| --- | --- | --- | --- | --- | --- |
| Cost r1 / r2 $ | 3.96 / 4.25 | 4.19 / 3.84 | 3.84 / 3.92 | 1.85 / 2.01 | 1.77 / 2.09 |
| Mean (vs F) | 4.11 | 4.02 (-2%) | 3.88 (-5%) | 1.93 (-53%) | **1.93 (-53%)** |
| Real errors (of 92) r1, r2 | 36, 38 | 39, 35 | 55, 70 | 58, 63 | **42, 41** |
| Both runs combined | 49 | 43 | 77 | 72 | **54** |
| Planted errors (of 20), by content | 20, 20 | 20, 20 | 20, 20 | 20, 20 | 20, 20 |
| Line citations past end of file | 0%, 0% | 0%, 0% | 0%, 10% | 0%, 0% | **9%, 20%** |
| Wall time per run | ~400 s | ~535 s | ~270 s | ~390 s | **~725 s** |

Almost all of H's cost was Haiku's 5x rate on prompts over 100K tokens ($1.74 of $1.77 on r1; $2.06 of $2.09 on r2).

- **This is the first task where H clearly loses.** At the same cost as C, it found 42 and 41 real errors against 58 and 63. C's fan-out to Haiku subagents, with Opus combining and re-checking, appears to find more than one Haiku working through the pages alone, though two runs can't show why.
- **H still found slightly more per run than F or D**, at under half the price.
- **Its reports are harder to use.** The line-based scorer showed only 17 and 14 of 20 planted errors, because some cited lines don't exist (line 48 of a 32-line page), and r2 gave some wrong file paths. By content, both runs found all 20.

**How the real errors were scored.** Claude Opus read both H reports against the verified list of 92, built earlier from the other 8 runs. Matches are in `data/ground-truth/t43-H-scored.md` (gitignored). This judgement wasn't made blind, because I knew the setup. Claims outside the list (about 75 rows in H r1's report and 68 items in r2's, of which 42 and 41 matched) weren't verified, so H may have found real errors that aren't counted, and some of its claims may be wrong. False positives haven't been counted for any setup yet. The past-end-of-file figure only catches citations that can't exist, not ones that point to the wrong line.

**What Part 5 shows, across all parts.** On small, testable coding tasks, Haiku alone got the same hidden-test results as anything with Opus, at 1-12% of the cost of Opus alone, and faster. On the largest review task, Opus plus Haiku found clearly more for the same money. The care Opus adds (indexes, flagging what it couldn't reproduce, accurate citations) doesn't show in my hidden tests but does show in the work. Results are 2 runs per setup, and no coding task here made Haiku alone fail, so where its limit lies is still unknown.
