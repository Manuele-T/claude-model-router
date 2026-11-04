#!/usr/bin/env python3
"""Score a module-summaries answer (tasks 31, 41) against the source tree.

Usage:
  python3 scripts/score_summaries.py SRC ANSWER [--pkg DIR ...] [--exclude DIR ...] [--list-missing]

  SRC      checkout of the bench project (e.g. ~/bench-src/buildbot-planted)
  ANSWER   the run's answer as text or markdown (from the run JSON's "result",
           or the file the run wrote)
  --pkg    package directory relative to SRC, repeatable
           (buildbot: master/buildbot and worker/buildbot_worker)
  --exclude  directory relative to SRC to leave out, repeatable
           (buildbot: master/buildbot/test and worker/buildbot_worker/test)

Reports:
  coverage   modules named in a heading line (markdown heading, bold line, or
             a line that is just the path), out of all modules
  mentioned  modules named anywhere in the answer
  backed     of the "works with" links in each module's section (other project
             modules it names), the share backed by an import in either
             direction, from the AST import graph

Stdlib only. Names are matched as dotted names (buildbot.process.buildstep) or
paths (buildbot/process/buildstep.py, with or without the leading master/).
"""
import argparse
import ast
import re
import sys
from pathlib import Path


def find_modules(src, pkgs, excludes):
    """Return {dotted name: path} and {dotted name: path stem relative to the package's parent}."""
    mods, stems = {}, {}
    for pkg in pkgs:
        base = src / pkg
        root = base.parent
        for f in sorted(base.rglob("*.py")):
            rel = f.relative_to(src).as_posix()
            if any(rel == e or rel.startswith(e.rstrip("/") + "/") for e in excludes):
                continue
            parts = list(f.relative_to(root).with_suffix("").parts)
            if parts[-1] == "__init__":
                parts = parts[:-1]
            name = ".".join(parts)
            mods[name] = f
            # Paths keep dots that are part of a file name (e.g. 059_v3.4_initial.py).
            stems[name] = "/".join(parts)
    return mods, stems


def import_graph(mods):
    """Undirected set of (a, b) module pairs linked by an import."""
    names = set(mods)
    edges = set()
    for name, path in mods.items():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        is_pkg = path.name == "__init__.py"
        pkg = name if is_pkg else name.rpartition(".")[0]
        for node in ast.walk(tree):
            targets = []
            if isinstance(node, ast.Import):
                targets = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    base = pkg.split(".")
                    base = base[: len(base) - node.level + 1] if node.level > 1 else base
                    mod = ".".join(base + ([node.module] if node.module else []))
                else:
                    mod = node.module or ""
                targets = [mod] + [f"{mod}.{a.name}" for a in node.names]
            for t in targets:
                # Walk up to the longest known module ("x.y.Class" -> "x.y").
                while t and t not in names:
                    t = t.rpartition(".")[0]
                if t and t != name:
                    edges.add(frozenset((name, t)))
    return edges


def name_patterns(mods, stems):
    """Regex per module matching its dotted name or its path."""
    pats = {}
    for name in mods:
        path = stems[name]
        alts = [re.escape(name), re.escape(path) + r"(?:/__init__)?\.py"]
        if mods[name].name == "__init__.py":
            alts.append(re.escape(path) + r"/?(?![\w/.])")
        # Not part of a longer dotted name or path on either side.
        pats[name] = re.compile(r"(?<![\w.])(?:" + "|".join(alts) + r")(?![\w])(?!\.[a-z_])(?!/\w)")
    return pats


def short_patterns(mods):
    """Regex per module for its name without the top package, in backticks (`process.build`).

    Only used inside sections of the same top package, where answers often drop the prefix.
    """
    pats = {}
    for name in mods:
        root, _, short = name.partition(".")
        if short:
            pats[name] = (root, re.compile(r"`" + re.escape(short) + r"`"))
    return pats


# A line that opens a module's section: a markdown heading, a bold line, a list item that starts
# with a bold or code name ("- `x/y.py`: ..."), or a line holding just the name.
HEADING = re.compile(r"^\s*(?:#{1,6}\s|\*\*|__|[-*]\s+(?:\*\*|`)|`?[\w/.]+\.py`?\s*:?\s*$|`[\w.]+`\s*$)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path)
    ap.add_argument("answer", type=Path)
    ap.add_argument("--pkg", action="append", required=True)
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--list-missing", action="store_true")
    args = ap.parse_args()

    mods, stems = find_modules(args.src.expanduser(), args.pkg, args.exclude)
    edges = import_graph(mods)
    pats = name_patterns(mods, stems)
    shorts = short_patterns(mods)
    lines = args.answer.read_text(encoding="utf-8", errors="replace").splitlines()

    headed, mentioned = set(), set()
    sections = []  # (module, [body lines])
    for line in lines:
        found = [n for n, p in pats.items() if p.search(line)]
        mentioned.update(found)
        if HEADING.match(line) and found:
            # The heading's module is the longest name on the line.
            mod = max(found, key=len)
            headed.add(mod)
            sections.append((mod, [line]))  # a list-item heading may carry the summary too
        elif sections:
            sections[-1][1].append(line)

    links = backed = 0
    for mod, body in sections:
        text = "\n".join(body)
        root = mod.partition(".")[0]
        for other, p in pats.items():
            if other == mod:
                continue
            sroot, sp = shorts.get(other, (None, None))
            if p.search(text) or (sroot == root and sp.search(text)):
                links += 1
                backed += frozenset((mod, other)) in edges

    total = len(mods)
    print(f"modules     {total}")
    print(f"coverage    {len(headed)}/{total} headed ({len(headed) / total:.0%})")
    print(f"mentioned   {len(mentioned)}/{total}")
    if links:
        print(f"backed      {backed}/{links} links import-backed ({backed / links:.0%})")
    else:
        print("backed      no links found")
    if args.list_missing:
        for n in sorted(set(mods) - headed):
            print(f"missing     {n}")


if __name__ == "__main__":
    sys.exit(main())
