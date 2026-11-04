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
#   scripts/run_bench.sh 07 B v2 # optional tag: a repeat run in its own clone, ~/bench/t07-Bv2
#   TASKS=data/tasks-v2.md scripts/run_bench.sh 11 A r1   # another task table
#
# Clones SRC into ~/bench/t<NN>-<A|B><tag> (committed files only, no remote), runs Claude Code
# on Opus in auto permission mode, and saves the JSON result to data/runs/t<NN>-<A|B><tag>.json.
# Afterwards: python3 scripts/verify_models.py --project bench-t<NN>-<A|B><tag>/
# (the trailing slash stops t07-B from also matching t07-Bv2)
set -euo pipefail

task="${1:?task number, e.g. 07}"
run="${2:?A, B, C, D, E or F}"
tag="${3:-}"
SRC="${SRC:-$HOME/bench-src/small}"   # default: symlink to the private ~10k-line project
repo="$(cd "$(dirname "$0")/.." && pwd)"
dest="$HOME/bench/t${task}-${run}${tag}"
out="$repo/data/runs/t${task}-${run}${tag}.json"

tasks="$repo/${TASKS:-data/tasks.md}"
prompt="$(awk -F' \\| ' -v t="| $task" '$1 == t { print $3 }' "$tasks")"
[ -n "$prompt" ] || { echo "task $task not found in $tasks" >&2; exit 1; }

# Run A also blocks the Agent tool: on large tasks a global CLAUDE.md delegation rule can
# otherwise make "no routing" runs spawn Sonnet subagents anyway.
extra=()
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
  *) echo "run must be A, B, C, D, E or F" >&2; exit 1 ;;
esac

[ -e "$dest" ] && { echo "$dest already exists; remove it first" >&2; exit 1; }
mkdir -p "$HOME/bench" "$repo/data/runs"
git clone -q --no-hardlinks "$SRC" "$dest"
git -C "$dest" remote remove origin

echo "== t${task}-${run}${tag}: $prompt"
cd "$dest"
claude -p "$prompt" --model opus --effort medium --permission-mode auto --output-format json "${extra[@]}" > "$out"
python3 - "$out" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
print(f"turns {d.get('num_turns')}  {d.get('duration_ms', 0) / 1000:.0f}s  "
      f"denials {len(d.get('permission_denials') or [])}  error {d.get('is_error')}")
for m, u in (d.get("modelUsage") or {}).items():
    print(f"  {m:<20} out {u['outputTokens']:>7,}")
EOF

# Long answers often land in the child session's scratchpad under /tmp, which a reboot wipes.
# Keep a copy next to the run JSON.
scratch="/tmp/claude-$(id -u)/$(echo "$dest" | tr '/' '-')"
if compgen -G "$scratch/*/scratchpad/*" > /dev/null; then
  mkdir -p "${out%.json}-scratch"
  cp -r "$scratch"/*/scratchpad/. "${out%.json}-scratch/"
  echo "  scratchpad copied to ${out%.json}-scratch/"
fi
