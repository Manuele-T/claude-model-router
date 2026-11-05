#!/usr/bin/env python3
"""Diff size, complexity and verification cost for building runs (definitions: data/tasks-v7.md).

    python3 scripts/run_metrics.py t51-Fr1 t52-Cr2 ...
    python3 scripts/run_metrics.py --csv data/metrics.csv --task 51 --task 52

Reads ~/bench/<run> and the run's transcripts. Changes nothing in the clone: the diff goes through
a temporary git index and object directory. Hidden test files are left out of the diff.
Costs are the checker's API-price proxy, not a real bill.
"""

from __future__ import annotations

import argparse
import ast
import csv
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from verify_models import HAIKU_LONG_PROMPT, PROJECTS_DIR, cost, family, read_jsonl  # noqa: E402

BENCH = Path.home() / "bench"
BASELINES = {"52": "b975531"}      # default below; 52 ran on the copy with one planted bug
DEFAULT_BASELINE = "a3c99c4"
ARMS = "FDBC"
EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}
AGENT_TOOLS = {"Agent", "Task"}
TEST_RE = re.compile(r"\bunittest\b|\bpytest\b")
HIDDEN = ":(exclude)tests/unit/test_hidden_*"


# --- diff -------------------------------------------------------------------------------------

def git(clone: Path, *args: str, env: dict | None = None) -> str:
    return subprocess.run(["git", "-C", str(clone), *args], capture_output=True, text=True, check=True,
                          env=env).stdout


def changed_files(clone: Path, base: str) -> list[tuple[str, int, int]]:
    """(path, added, removed) for working tree vs base, including new files."""
    with tempfile.TemporaryDirectory() as tmp:
        objects = str(git(clone, "rev-parse", "--path-format=absolute", "--git-path", "objects").strip())
        env = {**os.environ, "GIT_INDEX_FILE": f"{tmp}/index", "GIT_OBJECT_DIRECTORY": tmp,
               "GIT_ALTERNATE_OBJECT_DIRECTORIES": objects}
        git(clone, "read-tree", base, env=env)
        git(clone, "add", "-A", "--", ".", HIDDEN, env=env)
        out = git(clone, "diff", "--cached", "--numstat", "--no-renames", base, "--", ".", HIDDEN, env=env)
    rows = []
    for line in out.splitlines():
        added, removed, path = line.split("\t", 2)
        rows.append((path, int(added) if added != "-" else 0, int(removed) if removed != "-" else 0))
    return rows


def at_base(clone: Path, base: str, path: str) -> str | None:
    r = subprocess.run(["git", "-C", str(clone), "show", f"{base}:{path}"], capture_output=True, text=True, check=False)
    return r.stdout if r.returncode == 0 else None


# --- complexity -------------------------------------------------------------------------------

def _own_nodes(fn: ast.AST):
    """Nodes in a function, not descending into nested functions or classes (they count on their own)."""
    stack = list(ast.iter_child_nodes(fn))
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            stack.extend(ast.iter_child_nodes(node))


def fn_complexity(fn: ast.AST) -> int:
    score = 1
    for n in _own_nodes(fn):
        if isinstance(n, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.IfExp,
                          ast.comprehension, ast.match_case)):
            score += 1
        elif isinstance(n, ast.BoolOp):
            score += len(n.values) - 1
    return score


def complexity(source: str | None) -> tuple[int, int]:
    """(total, highest single function)."""
    if not source:
        return 0, 0
    scores = [fn_complexity(n) for n in ast.walk(ast.parse(source))
              if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    return sum(scores), max(scores, default=0)


def top_level_defs(source: str | None) -> set[str]:
    if not source:
        return set()
    return {n.name for n in ast.parse(source).body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}


def diff_metrics(run: str) -> dict:
    clone = BENCH / run
    task = run[1:3]
    base = BASELINES.get(task, DEFAULT_BASELINE)
    m = defaultdict(int)
    old_defs, new_defs = set(), set()
    before_total = after_total = 0
    highest = 0
    for path, added, removed in changed_files(clone, base):
        old = at_base(clone, base, path)
        if path.startswith("tests/"):
            m["test_added"] += added
            m["test_removed"] += removed
            if old is not None:
                m["existing_test_files_edited"] += 1
                m["existing_test_lines_edited"] += added + removed
            continue
        if path.endswith(".py") or path.endswith(".sh"):
            m["code_added"] += added
            m["code_removed"] += removed
            m["code_files"] += 1
        else:
            m["docs_added"] += added
            m["docs_removed"] += removed
            m["docs_files"] += 1
        if path.endswith(".py"):
            full = clone / path
            new = full.read_text() if full.exists() else None
            old_defs |= top_level_defs(old)
            new_defs |= top_level_defs(new)
            before_total += complexity(old)[0]
            total, top = complexity(new)
            after_total += total
            highest = max(highest, top)
    m["new_top_level_defs"] = len(new_defs - old_defs)
    m["complexity_before"] = before_total
    m["complexity_after"] = after_total
    m["complexity_added"] = after_total - before_total
    m["complexity_highest_fn"] = highest
    return dict(m)


# --- transcripts ------------------------------------------------------------------------------

def transcripts(run: str) -> list[Path]:
    project = PROJECTS_DIR / f"-home-manu-bench-{run}"
    return sorted(p for p in project.rglob("*.jsonl"))


_PY_WRITE = re.compile(r"""open\([^)\n]*,\s*['"][wa]|\.write_text\(""")
_SHELL_WRITE = re.compile(r"\bsed\s+-\S*i|\bperl\s+-\S*i|\bgit\s+apply\b|\bpatch\s|\btee\s")
_REDIRECT = re.compile(r"(?<![0-9&>])>>?\s*([^\s&>|;]+)")


def bash_edits(command: str) -> bool:
    """Does this command write project files? A heuristic, because many runs edit through
    `python3 - <<EOF` scripts or shell redirects rather than the Edit tool."""
    if _PY_WRITE.search(command):
        return True
    shell = re.split(r"<<-?\s*['\"]?\w+", command, maxsplit=1)
    head = shell[0]      # a heredoc body is code or text, so `>` in it isn't a redirect
    if _SHELL_WRITE.search(head):
        return True
    return any(not t.startswith(("/dev/", "/tmp/", "$", "~/.claude")) and "routing.log" not in t
               for t in _REDIRECT.findall(head))


def is_project_edit(tool: dict, clone: Path) -> bool:
    if tool.get("name") == "Bash":
        return bash_edits((tool.get("input") or {}).get("command", ""))
    if tool.get("name") not in EDIT_TOOLS:
        return False
    target = (tool.get("input") or {}).get("file_path") or (tool.get("input") or {}).get("notebook_path") or ""
    return target.startswith(str(clone) + "/") or not target.startswith("/")


def messages(path: Path) -> list[dict]:
    """Assistant messages in order, with the tool calls merged by message id (one message can
    span several lines). Usage comes from the first line, as in the checker."""
    out, by_id = [], {}
    for e in read_jsonl(path):
        msg = e.get("message") or {}
        if e.get("type") != "assistant" or not msg.get("model"):
            continue
        mid = msg.get("id") or e.get("uuid")
        if mid not in by_id:
            by_id[mid] = {"id": mid, "model": msg["model"], "usage": msg.get("usage") or {},
                          "ts": e.get("timestamp", ""), "tools": []}
            out.append(by_id[mid])
        content = msg.get("content")
        if isinstance(content, list):
            by_id[mid]["tools"] += [c for c in content if isinstance(c, dict) and c.get("type") == "tool_use"]
    return out


def msg_cost(m: dict) -> float:
    u = m["usage"]
    fam = family(m["model"])
    prompt = sum(u.get(k, 0) or 0 for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    if fam == "haiku" and prompt > HAIKU_LONG_PROMPT:
        fam = "haiku>100k"
    return cost(fam, {"in": u.get("input_tokens", 0) or 0, "out": u.get("output_tokens", 0) or 0,
                      "cache_read": u.get("cache_read_input_tokens", 0) or 0,
                      "cache_write": u.get("cache_creation_input_tokens", 0) or 0})


def transcript_metrics(run: str) -> dict:
    clone = BENCH / run
    seen: set[str] = set()
    own = subagent = 0.0
    timeline = []
    for path in transcripts(run):
        is_sub = "subagents" in path.parts or path.name.startswith("agent-")
        for m in messages(path):
            if m["id"] in seen:
                continue
            seen.add(m["id"])
            c = msg_cost(m)
            if is_sub:
                subagent += c
            else:
                own += c
            timeline.append((m["ts"], c, m["tools"]))
    timeline.sort(key=lambda row: row[0])

    post_edit = 0.0
    edits = tests = rework = 0
    edited = tested_after_edit = False
    for _, c, tools in timeline:
        has_edit = any(is_project_edit(t, clone) for t in tools)
        spawns = any(t.get("name") in AGENT_TOOLS for t in tools)
        if edited and not has_edit and not spawns:
            post_edit += c
        for t in tools:
            if is_project_edit(t, clone):
                edits += 1
                edited = True
                rework += tested_after_edit
            if t.get("name") == "Bash" and TEST_RE.search((t.get("input") or {}).get("command", "")):
                tests += 1
                tested_after_edit = tested_after_edit or edited
    total = own + subagent
    return {"cost": round(total, 4), "own_cost": round(own, 4), "subagent_cost": round(subagent, 4),
            "post_edit_cost": round(post_edit, 4), "post_edit_share": round(post_edit / total, 3) if total else 0.0,
            "test_runs": tests, "edits": edits, "rework_edits": rework}


# --- output -----------------------------------------------------------------------------------

COLUMNS = ["code_added", "code_removed", "code_files", "docs_added", "test_added", "test_removed",
           "existing_test_files_edited", "existing_test_lines_edited", "new_top_level_defs", "complexity_added",
           "complexity_highest_fn", "cost", "own_cost", "subagent_cost", "post_edit_cost", "post_edit_share",
           "test_runs", "edits", "rework_edits"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("runs", nargs="*", help="run names, e.g. t51-Fr1")
    ap.add_argument("--task", action="append", default=[], help="all r1/r2 runs of this task, arms F D B C")
    ap.add_argument("--csv", help="also write one row per run")
    args = ap.parse_args()
    runs = list(args.runs) + [f"t{t}-{a}{r}" for t in args.task for a in ARMS for r in ("r1", "r2")]
    rows = []
    for run in runs:
        if not (BENCH / run).is_dir():
            print(f"{run}: no clone, skipped", file=sys.stderr)
            continue
        rows.append({"run": run, **{c: 0 for c in COLUMNS}, **diff_metrics(run), **transcript_metrics(run)})
    print(f"{'run':<9}{'code+/-':>10}{'test+/-':>10}{'oldtst':>7}{'defs':>5}{'cx+':>5}{'cxmax':>6}"
          f"{'cost':>7}{'own':>7}{'subs':>7}{'check':>7}{'share':>6}{'suite':>6}{'edits':>6}{'rework':>7}")
    for r in rows:
        print(f"{r['run']:<9}{str(r['code_added']) + '/' + str(r['code_removed']):>10}"
              f"{str(r['test_added']) + '/' + str(r['test_removed']):>10}{r['existing_test_lines_edited']:>7}"
              f"{r['new_top_level_defs']:>5}{r['complexity_added']:>5}{r['complexity_highest_fn']:>6}"
              f"{r['cost']:>7.2f}{r['own_cost']:>7.2f}{r['subagent_cost']:>7.2f}{r['post_edit_cost']:>7.2f}"
              f"{r['post_edit_share']:>6.0%}{r['test_runs']:>6}{r['edits']:>6}{r['rework_edits']:>7}")
    if args.csv and rows:
        with open(args.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["run", *COLUMNS], extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
