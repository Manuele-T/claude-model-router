# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code skill experiment: Opus orchestrates and routes subagents to Haiku/Sonnet/Opus (`skills/model-router/SKILL.md`), and a standalone Python checker (`scripts/verify_models.py`) reads Claude Code's own transcripts to confirm which model actually ran and to total tokens per model. `BUILD_PLAN.md` (local only, gitignored) is the original plan for phases, the 10-task benchmark, and troubleshooting; read it before changing scope if it exists. It assumes the repo lives at `~/claude-model-router`; it actually lives at `~/Documents/Coding/claude-model-router`. Results and conclusions live in `README.md` and `data/results.md`.

## Commands

No build, lint or test suite. The checker is stdlib-only Python 3.8+:

```bash
python3 scripts/verify_models.py                          # all transcripts
python3 scripts/verify_models.py --since 2026-10-26       # sessions starting on/after date (UTC)
python3 scripts/verify_models.py --project <substring>    # filter on transcript path
python3 scripts/verify_models.py --csv data/<date>.csv    # also write per-subagent rows
```

Skill install (symlink, so edits apply immediately):

```bash
ln -s ~/Documents/Coding/claude-model-router/skills/model-router ~/.claude/skills/model-router
```

Routing log written by the skill: `~/.claude/model-router/routing.log` (`time | project | model | description | reason`).

Benchmark (Phase 3): `scripts/run_bench.sh <NN> <A|B|C|D|E|F>` clones `SRC` (default `~/bench-src/small`, a symlink to the private ~10k-line project; committed files only, origin removed) into `~/bench/t<NN>-<arm>`, runs the prompt from row `<NN>` of `data/tasks.md` headless on Opus, and writes `data/runs/t<NN>-<arm>.json`. Arms (README names in brackets): A ("Opus only, forced") prefixes `no routing.` and passes `--disallowedTools Agent`, so a delegation rule in the global CLAUDE.md can't make its runs spawn subagents (the block was added on 2026-10-27; sets 1-3 and t32 A r1/r2 ran without it); B ("Skill-routed") prefixes `Use the model-router skill.`; C ("Forced Haiku") prefixes `Use the model-router skill. use haiku.` (every subagent forced onto Haiku); D ("Opus only, spontaneous") adds no prefix and passes `--disallowedTools Skill`, so Opus may spawn subagents but the installed router skill (whose description tells Opus to load it before any Agent call) can't load itself and turn the run into B. Check D runs for zero `Skill` calls and zero routing-log lines. E (D plus the `no routing.` prefix) was a one-off test of the forced vs spontaneous gap on task 32. F (no prefix, `--disallowedTools Agent,Skill`) started as the same kind of test and is the **v2 baseline** ("Opus only, blocked"): v2 reports every percentage against F, and runs F, D, B, C (A only to measure the wording effect). Optional third arg tags a repeat run (`07 B v2` → `~/bench/t07-Bv2`); the script refuses an existing clone, so a retry needs a new tag. `TASKS=data/tasks-v2.md` picks the reading-heavy set (tasks 11-15); `SRC=~/bench-src/rich TASKS=data/tasks-v3.md` the larger-codebase set (tasks 21-22, shallow clone of Textualize/rich at `9d8f9a3`); `SRC=~/bench-src/beets TASKS=data/tasks-v4.md` the ~50k-line set (tasks 31-33, beetbox/beets at `ab4bdfd`); `SRC=~/bench-src/buildbot-planted TASKS=data/tasks-v5.md` the v2 ~100k-line set (tasks 41-43, buildbot/buildbot at `c5cdcf3`). `buildbot-planted` is a one-commit local copy (no remote) with 30 planted doc errors; `~/bench-src/buildbot` is the unmodified checkout used to verify real errors. The answer key, real-error lists and doc-check scorers live in `data/ground-truth/` (gitignored: `buildbot-plants.md`, `t42-real.md`, `t43-real.md`, `score42.py`, `score43.py`); keep the planted list private so it can be reused. Score summaries (tasks 31, 41) with `python3 -I scripts/score_summaries.py <SRC> <answer> --pkg master/buildbot --pkg worker/buildbot_worker --exclude master/buildbot/test --exclude worker/buildbot_worker/test` (task 41 also excludes buildbot's secret-provider package, whose reads a local guard hook blocks); it reports coverage and the share of "works with" links backed by the AST import graph. The doc-check scorers match page plus line within one line, so check apparent misses by content before scoring a run down. `run_bench.sh` also copies the child session's scratchpad to `data/runs/<run>-scratch/`, because `/tmp` is wiped on reboot. Runs share the subscription's usage limit: a run that hits it still exits 0 but its `result` is "You've hit your session limit", so check `result` before scoring. Use transcript timestamps, not the result JSON's `duration_ms`, for wall time: it undercounts runs that wait on subagents. Long answers may land in the child session's scratchpad (`/tmp/claude-1000/-home-manu-bench-<run>/`), not in `result`. A run that hits the limit before finishing leaves a clone and transcripts (`~/.claude/projects/-home-manu-bench-t<NN>-<arm><tag>/`) behind; delete both before re-running under the same tag, or the checker adds the dead run's cost. Check a run with `python3 scripts/verify_models.py --project bench-t<NN>-<A|B|C|D|F><tag>/`; the trailing slash stops `t07-B` matching `t07-Bv2`. Bench project tests: `python3 -m unittest discover -s tests/unit -t .`.

Headless runs must use `--permission-mode auto`: the skill's log line uses `$(...)` substitutions, which `--allowedTools` prefix rules never match, so in `dontAsk` mode every log line is silently denied.

The skill is also installed as a claude.ai-synced copy (`~/.claude/skills/synced/.../model-router`, shown as `anthropic-skills:model-router`). Until `SKILL.md` is edited they are identical and the synced copy is what runs; once you edit it, symlink the repo copy and remove the synced one so only one exists.

## Architecture

Two independent halves joined only by Claude Code's transcript format:

- **SKILL.md** (instructions to the orchestrator): default to `haiku`, step up only with a nameable reason; always pass `model` explicitly on Agent calls; log a line before every Agent call (and `inline` for kept-inline tasks); escalate a failed Haiku result once to Sonnet; honour `no routing` / `use <tier>` overrides. It must never touch `CLAUDE_CODE_SUBAGENT_MODEL` or settings files — that env var silently overrides every subagent's model and is the #1 cause of "everything ran on Opus".
- **verify_models.py** scans `~/.claude/projects/**/*.jsonl`:
  - A file is a subagent transcript if its path contains `subagents/`, its name starts with `agent-`, or an early entry has `isSidechain`.
  - Orchestrator side: collects `tool_use` blocks named `Agent`/`Task` and records requested model keyed by the **exact prompt text**.
  - Subagent side: first user message = prompt; models seen in assistant messages = actual. Pairing is by exact prompt-string match, so any transcript-format drift shows up as "could not pair".
  - Status: >1 model in a subagent → `FALLBACK`; requested ∉ actual → `MISMATCH`; `inherit`/unpaired → treated as ok.
  - Tokens de-duplicated by message id; cost uses the `PRICES` table (USD/MTok) plus cache read/write multipliers, compared against re-pricing everything at Opus rates. Cost is an API-price proxy for subscription usage, not a real number — keep that caveat in any output/README.
  - The checker does **not** read `routing.log`; the log is for the human write-up. SKILL.md's claim that the log description must match "so the verifier can pair them" is aspirational unless log-pairing is added.

When editing the script, update `PRICES` against current Anthropic pricing rather than guessing, and keep it stdlib-only.

## Data

`data/` holds CSVs, `tasks.md` and `results.md` from benchmark runs. The CSVs and `data/runs/*.json` contain local file paths, so `.gitignore` ignores `data/*` except `.gitkeep`, the task files `tasks.md` and `tasks-v2.md` to `tasks-v5.md` (needed by `run_bench.sh`) and `results.md` — publish summary numbers only. The small private project's original prompts are in `data/private/` (gitignored); public files describe it only in generic terms, so re-scan them for identifying names before each commit.
