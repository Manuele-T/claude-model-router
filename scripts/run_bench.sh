#!/usr/bin/env bash
# run_bench.sh - run one benchmark task headless in a fresh clone of the bench project.
#
# Usage
#   scripts/run_bench.sh 07 A    # run A: "no routing." (Opus does everything)
#   scripts/run_bench.sh 07 B    # run B: "Use the model-router skill."
#   scripts/run_bench.sh 07 C    # run C: the skill with the "use haiku" override (every subagent on Haiku)
#   scripts/run_bench.sh 07 D    # run D: "natural", plain prompt; Opus decides on subagents, no skills
#   scripts/run_bench.sh 07 E    # run E: D plus the "no routing." prefix (framing test)
#   scripts/run_bench.sh 07 F    # run F: D with the Agent tool blocked too (tool-setup test)
#   scripts/run_bench.sh 07 H    # run H: F with Haiku as the main model, no Opus at all
#   scripts/run_bench.sh 07 S    # run S: F with Sonnet as the main model, no Opus at all
#   scripts/run_bench.sh 57 G r1 # run G: F plus one system-prompt line Claude Code dropped (data/tasks-v14.md, Part 1d)
#   scripts/run_bench.sh 07 R    # run R: H, then a fresh Opus session in the same clone reviews and fixes
#   scripts/run_bench.sh 07 B v2 # optional tag: a repeat run in its own clone, ~/bench/t07-Bv2
#   TASKS=data/tasks-v2.md scripts/run_bench.sh 11 A r1   # another task table
#
# Clones SRC into ~/bench/t<NN>-<A|B><tag> (committed files only, no remote), runs Claude Code
# on Opus in auto permission mode, and saves the JSON result to data/runs/t<NN>-<A|B><tag>.json.
# Afterwards: python3 scripts/verify_models.py --project bench-t<NN>-<A|B><tag>/
# (the trailing slash stops t07-B from also matching t07-Bv2)
set -euo pipefail

task="${1:?task number, e.g. 07}"
run="${2:?A, B, C, D, E, F, G, H, R or S}"
tag="${3:-}"
SRC="${SRC:-$HOME/bench-src/small}"   # default: symlink to the private ~10k-line project
repo="$(cd "$(dirname "$0")/.." && pwd)"
bench="${BENCH:-$HOME/bench}"     # override only for dry runs
runs="${RUNS:-$repo/data/runs}"
dest="$bench/t${task}-${run}${tag}"
out="$runs/t${task}-${run}${tag}.json"

tasks="$repo/${TASKS:-data/tasks.md}"
prompt="$(awk -F' \\| ' -v t="| $task" '$1 == t { print $3 }' "$tasks")"
[ -n "$prompt" ] || { echo "task $task not found in $tasks" >&2; exit 1; }

# Run A also blocks the Agent tool: on large tasks a global CLAUDE.md delegation rule can
# otherwise make "no routing" runs spawn Sonnet subagents anyway.
extra=()
model=opus
review=
case "$run" in
  A) prompt="no routing. $prompt"; extra=(--disallowedTools Agent) ;;
  B) prompt="Use the model-router skill. $prompt" ;;
  C) prompt="Use the model-router skill. use haiku. $prompt" ;;
  # D is plain Claude Code: no prefix, subagents allowed. Skills are blocked so the installed
  # model-router skill can't load itself and turn the run into B.
  D) extra=(--disallowedTools Skill) ;;
  # E is D with A's prefix: tests whether "no routing." alone makes Opus more thorough.
  E) prompt="no routing. $prompt"; extra=(--disallowedTools Skill) ;;
  # F is D with the Agent tool blocked as well: tests whether losing subagents alone makes Opus more thorough.
  F) extra=(--disallowedTools Agent,Skill) ;;
  # G is F plus one instruction that was in Claude Code's own system prompt on 2026-11-06 and gone by
  # 2026-11-12 with the same version number (data/tasks-v14.md, Part 1d).
  G) extra=(--disallowedTools Agent,Skill --append-system-prompt "Before you start, tell the user in a sentence or two what you plan to do. While you work, give the user a short update alongside your next tool call whenever you start a major new part of the work, change your plan, or launch something slow.") ;;
  # H is F with Haiku as the main model: Haiku alone, with no Opus briefing, reviewing or testing.
  H) model=haiku; extra=(--disallowedTools Agent,Skill) ;;
  # S is F with Sonnet as the main model: Sonnet alone, no Opus and no subagents.
  S) model=sonnet; extra=(--disallowedTools Agent,Skill) ;;
  # R is H followed by a review: step 1 is exactly H, then a fresh Opus session (Agent and Skill
  # blocked) in the same clone checks the work against the task and fixes it (data/tasks-v13.md).
  R) model=haiku; extra=(--disallowedTools Agent,Skill); review=1 ;;
  *) echo "run must be A, B, C, D, E, F, G, H, R or S" >&2; exit 1 ;;
esac

[ -e "$dest" ] && { echo "$dest already exists; remove it first" >&2; exit 1; }
mkdir -p "$bench" "$runs"
git clone -q --no-hardlinks "$SRC" "$dest"
git -C "$dest" remote remove origin

echo "== t${task}-${run}${tag}: $prompt"
cd "$dest"
# Tasks that need their own test dependencies: VENV puts a venv first on PATH, and buildbot's
# code is imported from this clone rather than from the venv's editable install.
if [ -n "${VENV:-}" ]; then
  export PATH="$VENV/bin:$PATH" PYTHONPATH="$dest/master:$dest/worker"
fi
claude --version > "${out%.json}.version"
base="$(git rev-parse HEAD)"
summary() {
  python3 - "$1" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
print(f"turns {d.get('num_turns')}  {d.get('duration_ms', 0) / 1000:.0f}s  "
      f"denials {len(d.get('permission_denials') or [])}  error {d.get('is_error')}")
for m, u in (d.get("modelUsage") or {}).items():
    print(f"  {m:<20} out {u['outputTokens']:>7,}")
EOF
}
claude -p "$prompt" --model "$model" --effort medium --permission-mode auto --output-format json "${extra[@]}" > "$out"
summary "$out"

if [ -n "$review" ]; then
  # Keep step 1's work as a patch (new files included) so it can also be scored on its own.
  git add -A -N
  git diff --binary "$base" > "${out%.json}-step1.patch"
  git reset -q
  answer="$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1])).get("result") or "(no final answer)")' "$out")"
  rprompt="Another session was given the task below and has finished working on it in this directory. It started from commit $base. Review its work: check its changes against that commit (git status, git diff $base) and its final answer, against what the task asks. Fix anything that is wrong or missing, then give your own final answer to the task.

Task:
$prompt

The other session's final answer:
$answer"
  echo "== t${task}-${run}${tag} review step (opus)"
  claude -p "$rprompt" --model opus --effort medium --permission-mode auto --output-format json \
    --disallowedTools Agent,Skill > "${out%.json}-review.json"
  summary "${out%.json}-review.json"
fi

# Long answers often land in the child session's scratchpad under /tmp, which a reboot wipes.
# Keep a copy next to the run JSON.
scratch="/tmp/claude-$(id -u)/$(echo "$dest" | tr '/' '-')"
if compgen -G "$scratch/*/scratchpad/*" > /dev/null; then
  mkdir -p "${out%.json}-scratch"
  cp -r "$scratch"/*/scratchpad/. "${out%.json}-scratch/"
  echo "  scratchpad copied to ${out%.json}-scratch/"
fi
