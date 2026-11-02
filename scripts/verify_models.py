#!/usr/bin/env python3
"""
verify_models.py - checks Claude Code subagent routing and counts tokens per model.

What it does
  1. Scans Claude Code transcripts (~/.claude/projects/**/*.jsonl).
  2. Finds every Agent/Task call the orchestrator made and the model it asked for.
  3. Finds the matching subagent transcript and the model that actually ran.
  4. Flags mismatches (asked for haiku, got opus) and fallbacks (switched model mid-run).
  5. Totals tokens per model and estimates "limit cost" vs. running everything on Opus.

Usage
  python3 verify_models.py                     # everything
  python3 verify_models.py --since 2026-10-14  # only sessions from this date (UTC)
  python3 verify_models.py --project myrepo    # only projects whose folder name contains this
  python3 verify_models.py --csv out.csv       # also write per-subagent rows to a CSV

The cost figures use API prices as a proxy for how fast each model drains a
subscription's usage limits. That is an assumption - label it as one.
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# USD per million tokens: Haiku 5.5, Sonnet 5.5, Opus 5.5, Fable 5.1 list prices (as of 2026-10-06).
# Check https://docs.claude.com pricing and update if needed.
# Haiku 5.5 rises to $0.50 / $2.50 for prompts over 100K tokens: those requests are
# totalled separately as "haiku>100k".
HAIKU_LONG_PROMPT = 100_000
PRICES = {
    "haiku":  {"in": 0.10, "out": 0.50, "cache_read": 0.01},
    "haiku>100k": {"in": 0.50, "out": 2.50, "cache_read": 0.05},
    "sonnet": {"in": 2.0,  "out": 10.0, "cache_read": 0.20},
    "opus":   {"in": 4.0,  "out": 20.0, "cache_read": 0.20},
    "fable":  {"in": 10.0, "out": 50.0, "cache_read": 0.25},
}
CACHE_WRITE_MULT = 1.25  # cache writes billed at ~125% of input price (5-minute cache)

PROJECTS_DIR = Path(os.path.expanduser("~/.claude/projects"))
AGENT_TOOL_NAMES = {"Agent", "Task"}


def family(model: str) -> str:
    """Map a full model id (claude-haiku-5-5-...) or alias to a family name."""
    m = (model or "").lower()
    for fam in ("haiku", "sonnet", "opus", "fable"):
        if fam in m:
            return fam
    if m in ("", "inherit", None):
        return "inherit"
    return m


def read_jsonl(path: Path):
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def text_of(content) -> str:
    """Flatten a message's content (string or list of blocks) into plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return ""


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def is_subagent_file(path: Path, first_entries) -> bool:
    if "subagents" in path.parts or path.name.startswith("agent-"):
        return True
    return any(e.get("isSidechain") for e in first_entries)


def scan(since, project_filter):
    usage = defaultdict(lambda: {"in": 0, "out": 0, "cache_read": 0, "cache_write": 0, "calls": 0})
    requested = {}      # prompt text -> (requested family, description, session file)
    subagents = []      # dicts describing each subagent transcript
    seen_msg_ids = set()

    if not PROJECTS_DIR.exists():
        sys.exit(f"No transcripts found at {PROJECTS_DIR}")

    for path in PROJECTS_DIR.rglob("*.jsonl"):
        if project_filter and project_filter not in str(path):
            continue
        entries = list(read_jsonl(path))
        if not entries:
            continue

        first_ts = next((parse_ts(e.get("timestamp")) for e in entries if e.get("timestamp")), None)
        if since and first_ts and first_ts < since:
            continue

        sub = is_subagent_file(path, entries[:5])
        actual_models = set()
        first_prompt = None
        sub_tokens = {"in": 0, "out": 0, "cache_read": 0, "cache_write": 0}

        for e in entries:
            msg = e.get("message") or {}
            role = msg.get("role") or e.get("type")

            # The first user message of a subagent transcript is the prompt it was given.
            if sub and first_prompt is None and role == "user":
                first_prompt = text_of(msg.get("content")).strip()

            if role != "assistant":
                continue

            model = msg.get("model")
            if model and model != "<synthetic>":
                actual_models.add(family(model))

            # Orchestrator side: record what model each Agent call asked for.
            if not sub and isinstance(msg.get("content"), list):
                for block in msg["content"]:
                    if (isinstance(block, dict) and block.get("type") == "tool_use"
                            and block.get("name") in AGENT_TOOL_NAMES):
                        inp = block.get("input") or {}
                        prompt = (inp.get("prompt") or "").strip()
                        if prompt:
                            requested[prompt] = (family(inp.get("model") or "inherit"),
                                                 inp.get("description", ""), str(path))

            # Token usage, de-duplicated by message id (one message can span several lines).
            u = msg.get("usage")
            if not u or not model:
                continue
            mid = msg.get("id") or e.get("uuid")
            if mid in seen_msg_ids:
                continue
            seen_msg_ids.add(mid)

            fam = family(model)
            prompt_tokens = sum(u.get(k, 0) or 0 for k in
                                ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
            if fam == "haiku" and prompt_tokens > HAIKU_LONG_PROMPT:
                fam = "haiku>100k"
            bucket = usage[fam]
            bucket["in"] += u.get("input_tokens", 0) or 0
            bucket["out"] += u.get("output_tokens", 0) or 0
            bucket["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
            bucket["cache_write"] += u.get("cache_creation_input_tokens", 0) or 0
            bucket["calls"] += 1
            if sub:
                sub_tokens["in"] += u.get("input_tokens", 0) or 0
                sub_tokens["out"] += u.get("output_tokens", 0) or 0
                sub_tokens["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
                sub_tokens["cache_write"] += u.get("cache_creation_input_tokens", 0) or 0

        if sub:
            subagents.append({
                "file": str(path),
                "prompt": first_prompt or "",
                "actual": ",".join(sorted(actual_models)) or "unknown",
                "tokens": sub_tokens,
            })

    return usage, requested, subagents


def cost(fam, t, as_family=None):
    p = PRICES.get(as_family or fam)
    if not p:
        return 0.0
    return (t["in"] * p["in"]
            + t["cache_read"] * p["cache_read"]
            + t["cache_write"] * p["in"] * CACHE_WRITE_MULT
            + t["out"] * p["out"]) / 1_000_000


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", help="only sessions starting on/after this date, YYYY-MM-DD (UTC)")
    ap.add_argument("--project", help="only transcript paths containing this text")
    ap.add_argument("--csv", help="write per-subagent rows to this CSV file")
    args = ap.parse_args()

    since = None
    if args.since:
        since = datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    usage, requested, subagents = scan(since, args.project)

    # 1. Routing check
    rows, mismatches, fallbacks, unmatched = [], 0, 0, 0
    for s in subagents:
        req = requested.get(s["prompt"])
        if req:
            want, desc, _ = req
        else:
            want, desc = "unknown", ""
            unmatched += 1
        ran = [m for m in s["actual"].split(",") if m and m != "unknown"]
        if len(ran) > 1:
            status = "FALLBACK"          # switched model mid-run
            fallbacks += 1
        elif want in ("unknown", "inherit") or want in ran:
            status = "yes"
        else:
            status = "MISMATCH"
            mismatches += 1
        rows.append({"description": desc, "requested": want, "actual": s["actual"],
                     "ok": status,
                     "in": s["tokens"]["in"], "out": s["tokens"]["out"],
                     "cache_read": s["tokens"]["cache_read"], "cache_write": s["tokens"]["cache_write"],
                     "file": s["file"]})

    print("\n=== Routing check ===")
    print(f"Subagents found: {len(subagents)}   mismatches: {mismatches}   "
          f"fallbacks: {fallbacks}   could not pair with an Agent call: {unmatched}")
    for r in rows:
        if r["ok"] in ("MISMATCH", "FALLBACK"):
            print(f"  {r['ok']:<9} asked {r['requested']:<7} ran {r['actual']:<14} {r['description'][:60]}")

    # 2. Tokens and estimated cost per model
    print("\n=== Tokens by model (all sessions in scope) ===")
    print(f"{'model':<11}{'calls':>7}{'input':>12}{'output':>12}{'cache rd':>13}{'cache wr':>12}{'est. $':>10}")
    total, total_if_opus = 0.0, 0.0
    for fam in sorted(usage):
        t = usage[fam]
        c = cost(fam, t)
        total += c
        total_if_opus += cost(fam, t, as_family="opus")
        print(f"{fam:<11}{t['calls']:>7}{t['in']:>12,}{t['out']:>12,}{t['cache_read']:>13,}{t['cache_write']:>12,}{c:>10.2f}")
    print(f"\nEstimated cost as routed:       ${total:.2f}")
    print(f"Same tokens if all ran on Opus: ${total_if_opus:.2f}")
    if total_if_opus:
        print(f"Saving vs all-Opus:             {100 * (1 - total / total_if_opus):.0f}%")
    print("(API prices used as a proxy for subscription limit usage. Assumes the same"
          " token counts on Opus, which is only approximate.)")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["description"])
            w.writeheader()
            w.writerows(rows)
        print(f"\nWrote {len(rows)} rows to {args.csv}")


if __name__ == "__main__":
    main()
