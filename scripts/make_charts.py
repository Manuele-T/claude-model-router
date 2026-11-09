"""Render the README charts as HTML pages, then screenshot them with headless Firefox.

Usage:
  python3 scripts/make_charts.py OUT_DIR [CHART ...]

CHART is one of the keys in CHARTS (default: all). Needs Firefox and the Noto Sans font.
"""
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Checked for colour-blind separation; every bar is also labelled by name.
COLORS = {"opus": "#2b7bd6", "natural": "#c2407f", "routed": "#ea6a36", "haiku": "#2e9e6b", "solo": "#b8860b", "sonnet": "#7a4fbf"}
FOOT = "github.com/Manuele-T/claude-model-router"
WIDTH = 3000

CSS = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ background: #fbfaf8; }}
body {{ font-family: 'Noto Sans', 'DejaVu Sans', sans-serif; color: #111; width: {WIDTH}px; padding: 160px 160px 120px; }}
h1 {{ font-size: 88px; font-weight: 700; letter-spacing: -1px; line-height: 1.15; }}
.sub {{ font-size: 46px; color: #555; margin-top: 28px; }}
h2 {{ font-size: 54px; font-weight: 700; margin-top: 150px; }}
h2 span {{ font-size: 44px; font-weight: 400; color: #555; }}
.thead, .row {{ display: grid; grid-template-columns: 380px 600px 700px 1fr 250px; align-items: center; column-gap: 30px; }}
.thead {{ white-space: nowrap; color: #777; font-size: 36px; margin-top: 56px; padding-bottom: 26px; border-bottom: 2px solid #ddd; }}
.thead div:last-child, .row .d {{ text-align: right; }}
.row {{ min-height: 172px; border-bottom: 2px solid #ddd; padding: 24px 0; }}
.row .n {{ font-size: 46px; font-weight: 700; }}
.row .m, .row .q {{ font-size: 42px; color: #444; line-height: 1.35; }}
.row .q small {{ display: block; font-size: 32px; color: #777; margin: 2px 0 10px; }}
.row .m small {{ display: block; font-size: 32px; color: #777; margin-top: 8px; }}
.row .q b {{ color: #111; }}
.bar {{ display: flex; align-items: center; gap: 26px; font-size: 42px; color: #444; }}
.bar i {{ display: block; height: 44px; border-radius: 6px; }}
.row .d {{ font-size: 54px; font-weight: 700; }}
.row .d.good {{ color: #1f7a4f; }}
.expl {{ margin-top: 110px; }}
.expl h3 {{ font-size: 46px; font-weight: 700; margin-bottom: 26px; }}
.expl p {{ font-size: 38px; color: #444; line-height: 1.5; margin-bottom: 18px; }}
.box {{ background: #f1efec; border-radius: 26px; padding: 64px 64px 50px; margin-top: 110px; }}
.box h3 {{ font-size: 52px; font-weight: 700; margin-bottom: 34px; }}
.box .l {{ display: grid; grid-template-columns: 760px 600px 80px 1fr; font-size: 44px; color: #444; margin-bottom: 26px; }}
.box .l b {{ color: #111; }}
.foot {{ margin-top: 110px; padding-top: 50px; border-top: 2px solid #ddd; color: #777; font-size: 36px; line-height: 1.9; }}
.depth {{ grid-template-columns: 390px 400px 360px 630px 410px 340px; }}
.bar small {{ display: block; font-size: 32px; color: #777; margin-top: 2px; }}
.thead.depth div:last-child {{ text-align: left; }}
"""


def esc(s):
    return html.escape(s)


def section(title, note, rows, base="forced Opus", cost_label="Est. API cost"):
    top = max(r["cost"] for r in rows)
    out = [f"<h2>{esc(title)} <span>· {esc(note)}</span></h2>",
           '<div class="thead"><div>Run</div><div>Models used</div><div>Quality (higher is better)</div>'
           f'<div>{esc(cost_label)}</div><div>vs {esc(base)}</div></div>']
    for r in rows:
        width = int(440 * r["cost"] / top)
        small = f"<small>{esc(r['small'])}</small>" if r.get("small") else ""
        delta = r.get("delta", "–")
        cls = "d good" if delta.startswith("−") else "d"
        parts = []
        for x in r.get("quality", []):
            m = re.match(r"(.*) \((\d+) combined\)$", x)
            parts.append(f"{esc(m.group(1))}<small>{m.group(2)} combined</small>" if m else esc(x) + "<br>")
        quality = "".join(parts)
        out.append(
            f'<div class="row"><div class="n">{esc(r["name"])}</div>'
            f'<div class="m">{esc(r["models"])}{small}</div>'
            f'<div class="q">{quality}</div>'
            f'<div class="bar"><i style="width:{width}px;background:{COLORS[r["kind"]]}"></i>${r["cost"]:.2f}</div>'
            f'<div class="{cls}">{esc(delta)}</div></div>')
    return "\n".join(out)


def depth_section(title, note, rows, read_max=1450, written_max=212.5, cost_max=9.20):
    """Two bar columns, read and written, each on one scale shared by every section of the chart."""
    out = [f"<h2>{esc(title)} <span>· {esc(note)}</span></h2>",
           '<div class="thead depth"><div>Run</div><div>Models used</div><div>Real errors found</div>'
           "<div>Tool output read, per run</div><div>Tokens written, per run</div><div>Est. API cost</div></div>"]
    for r in rows:
        read_mean = sum(r["read"]) / 2
        written_mean = sum(r["written"]) / 2
        small = f"<small>{esc(r['small'])}</small>" if r.get("small") else ""
        color = COLORS[r["kind"]]
        lo, hi = sorted(r["written"])
        out.append(
            f'<div class="row depth"><div class="n">{esc(r["name"])}</div>'
            f'<div class="m">{esc(r["models"])}{small}</div>'
            f'<div class="q">{esc(r["errors"])}<small>{r["combined"]} combined</small></div>'
            f'<div class="bar"><i style="width:{int(340 * read_mean / read_max)}px;background:{color}"></i>'
            f'{min(r["read"]):,}-{max(r["read"]):,}k</div>'
            f'<div class="bar"><i style="width:{int(200 * written_mean / written_max)}px;background:{color}"></i>'
            f"{lo}-{hi}k</div>"
            f'<div class="bar"><i style="width:{int(170 * r["cost"] / cost_max)}px;background:{color}"></i>'
            f'<span>${r["cost"]:.2f}<small>{esc(r.get("delta", "baseline"))}</small></span></div></div>')
    return "\n".join(out)


def page(title, subtitle, sections, explanation, checker, foot_note, expl_title="What the quality column measures"):
    expl = (f'<div class="expl"><h3>{esc(expl_title)}</h3>'
            + "".join(f"<p>{x}</p>" for x in explanation) + "</div>")
    lines = "".join(
        f'<div class="l"><div>{esc(a)}</div><div>estimated {esc(b)} saved</div><div>→</div><b>{esc(c)}</b></div>'
        for a, b, c in checker)
    box = f'<div class="box"><h3>The checker’s savings estimate vs reality</h3>{lines}</div>' if checker else ""
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
            f"<h1>{esc(title)}</h1><div class='sub'>{esc(subtitle)}</div>"
            + "".join(sections) + expl + box
            + f"<div class='foot'>{esc(foot_note)}<br>{FOOT}</div></body></html>")


OPUS = {"name": "Opus only, forced", "models": "Opus, no subagents", "small": "told not to delegate", "kind": "opus"}
NAT = {"name": "Opus only, spontaneous", "models": "Opus, no subagents", "small": "could delegate, never did", "kind": "natural"}
LEGEND = "Forced = Opus told no routing · Spontaneous = plain Claude Code, no skill (it never delegated) · Skill-routed = the skill picks Opus's helpers · Forced Haiku = every helper on Haiku · API list prices as a proxy for subscription usage"

V2_OPUS = {"name": "Opus alone", "models": "Opus, no subagents", "small": "subagents blocked", "kind": "opus"}
V2_FREE = {"name": "Free Opus", "models": "Opus, no subagents", "small": "could delegate, never did", "kind": "natural"}
V2_SKILL = {"name": "Skill-routed", "models": "Opus + Sonnet and Haiku", "small": "my skill picks the helpers", "kind": "routed"}
V2_OH = {"name": "Opus plus Haiku", "models": "Opus + Haiku", "small": "Opus plans and reviews", "kind": "haiku"}
V2_H = {"name": "Haiku alone", "models": "Haiku, no Opus", "kind": "solo"}
V2_S = {"name": "Sonnet alone", "models": "Sonnet, no Opus", "kind": "sonnet"}
V2_KEY = "Costs are API list prices, a proxy for subscription usage · Mostly 2 runs per setup, so treat these as strong hints"
EXPL = "What the tasks and numbers mean"

CHARTS = {
    "smaller-codebase": (page(
        "Delegating to cheaper models: smaller codebase",
        "My own Python project, ~10k lines · estimated API cost",
        [section("Everyday tasks", "10 tasks (search, fix, tests, refactor…)", [
            {**OPUS, "cost": 3.81, "quality": ["10/10 tasks passed"]},
            {**NAT, "cost": 3.77, "delta": "−1%", "quality": ["10/10 tasks passed"]},
            {"name": "Skill-routed", "models": "Opus + 3 Haiku + 6 Sonnet", "kind": "routed", "cost": 4.34, "delta": "+14%",
             "quality": ["10/10 tasks passed"]},
            {"name": "Forced Haiku", "models": "Opus + 14 Haiku", "kind": "haiku", "cost": 3.63, "delta": "−5%",
             "quality": ["10/10 tasks passed"]},
         ]),
         section("Reading-heavy tasks", "5 tasks, mean of 2 runs", [
            {**OPUS, "cost": 1.80, "quality": ["Counts: all correct", "Docs: 7 and 8 of 9 (8 combined)"]},
            {**NAT, "cost": 1.50, "delta": "−16%",
             "quality": ["Counts: 1 miscount in one run", "Docs: 5 and 7 of 9 (7 combined)"]},
            {"name": "Skill-routed", "models": "Opus + 10 Haiku + 6 Sonnet", "small": "subagents across both runs",
             "kind": "routed", "cost": 2.33, "delta": "+30%",
             "quality": ["Counts: 1 miscount in each run", "Docs: 5 and 6 of 9 (9 combined)"]},
            {"name": "Forced Haiku", "models": "Opus + 20 Haiku", "small": "subagents across both runs",
             "kind": "haiku", "cost": 1.79, "delta": "0%",
             "quality": ["Counts: 1 miscount in one run", "Docs: 3 and 2 of 9 (4 combined)"]},
         ])],
        ["<b>Everyday tasks:</b> 3 searches, 5 code jobs (a bug fix, new tests, a small feature, a refactor, "
         "a mixed job), 1 explanation and 1 design question. A code job passes when the full test suite passes "
         "and the change does what was asked; the other answers were checked against the code.",
         "<b>Reading-heavy, counts:</b> four tasks with an exact answer computed from the source: list every "
         "function, count the tests in each test file, find every missing docstring, and look for import cycles.",
         "<b>Reading-heavy, docs:</b> check the project's docs against the code. The score is how many of the "
         "9 known out-of-date claims each run found (two runs per setup). <b>Combined</b> = distinct issues found by the two runs together."],
        [("Everyday, skill-routed", "44%", "actually cost 14% more"),
         ("Everyday, forced Haiku", "68%", "actually 5% cheaper"),
         ("Reading-heavy, skill-routed", "52%", "actually cost 30% more"),
         ("Reading-heavy, forced Haiku", "77%", "actually break-even")],
        LEGEND), 4300),
    "larger-codebase": (page(
        "Delegating to cheaper models: larger codebase",
        "rich (open source), ~22k lines · estimated API cost",
        [section("Module summaries and docs check", "2 tasks, mean of 2 runs", [
            {**OPUS, "cost": 2.38, "quality": ["Summaries: 76/76 modules", "Docs: 10 and 10 of 12 (10 combined)"]},
            {**NAT, "cost": 2.06, "delta": "−14%",
             "quality": ["Summaries: 76/76 modules", "Docs: 8 and 9 of 12 (11 combined)"]},
            {"name": "Skill-routed", "models": "Opus + 3 Haiku + 16 Sonnet", "small": "subagents across both runs",
             "kind": "routed", "cost": 2.64, "delta": "+11%",
             "quality": ["Summaries: 76/76 modules", "Docs: 6 and 9 of 12 (10 combined)"]},
            {"name": "Forced Haiku", "models": "Opus + 21 Haiku", "small": "subagents across both runs",
             "kind": "haiku", "cost": 1.41, "delta": "−41%",
             "quality": ["Summaries: 76/76 modules", "Docs: 9 and 10 of 12 (11 combined)"]},
         ])],
        ["<b>Summaries:</b> write one paragraph for every module, saying what it does and which other modules "
         "it works with. Scored on coverage: did each run cover all 76 modules.",
         "<b>Docs:</b> check rich's 25 doc pages against the code. The score is how many of the 12 known "
         "out-of-date or wrong claims each run found (two runs per setup). <b>Combined</b> = distinct issues found by the two runs together."],
        [("Skill-routed", "45%", "actually cost 11% more"),
         ("Forced Haiku", "84%", "actually 41% cheaper")],
        LEGEND), 3050),
    "largest-codebase": (page(
        "Delegating to cheaper models: largest codebase",
        "beets (open source), ~52k lines · estimated API cost",
        [section("All three tasks", "summaries + 2 docs checks, mean of 2 runs", [
            {**OPUS, "cost": 13.49, "quality": ["Summaries: 167/167 modules", "Reference docs: 10 and 16 of 35 (17 combined)"]},
            {**NAT, "cost": 9.20, "delta": "−32%",
             "quality": ["Summaries: 167/167 modules", "Reference docs: 10 and 9 of 35 (12 combined)"]},
            {"name": "Skill-routed", "models": "Opus + 39 Sonnet", "small": "subagents across both runs",
             "kind": "routed", "cost": 8.34, "delta": "−38%",
             "quality": ["Summaries: 167/167 modules", "Reference docs: 18 and 13 of 35 (23 combined)"]},
            {"name": "Forced Haiku", "models": "Opus + 40 Haiku", "small": "subagents across both runs",
             "kind": "haiku", "cost": 3.33, "delta": "−75%",
             "quality": ["Summaries: 167/167 modules", "Reference docs: 20 and 11 of 35 (24 combined)"]},
         ]),
         section("Biggest job: plugin docs check", "80 doc pages, mean of 2 runs", [
            {**OPUS, "cost": 9.20, "small": "~15 min per run",
             "quality": ["41 and 33 of 61 (44 combined)"]},
            {**NAT, "small": "~9 min per run", "cost": 6.01, "delta": "−35%",
             "quality": ["27 and 35 of 61 (36 combined)"]},
            {"name": "Skill-routed", "models": "Opus + 8 Sonnet", "small": "~3 min per run", "kind": "routed",
             "cost": 3.95, "delta": "−57%", "quality": ["30 and 28 of 61 (35 combined)"]},
            {"name": "Forced Haiku", "models": "Opus + 8 Haiku", "small": "~4 min per run", "kind": "haiku",
             "cost": 1.49, "delta": "−84%", "quality": ["30 and 30 of 61 (39 combined)"]},
         ])],
        ["<b>Summaries:</b> one paragraph for every module, saying what it does and which other modules it "
         "works with. Scored on coverage (all 167 modules) and by checking each named module link against the "
         "real imports: 97-98% backed for both Opus-only setups and forced Haiku, 94-95% for skill-routed.",
         "<b>Reference docs:</b> check 5 reference pages against the code. The score is how many of the 35 "
         "known out-of-date or wrong claims each run found (two runs per setup). <b>Combined</b> = distinct issues found by the two runs together.",
         "<b>Plugin docs:</b> the same check on all 80 plugin pages, against 61 known issues (re-checked: every run's claims verified). The cost of the "
         "plugin check is included in the \"All three tasks\" total above."],
        [("Skill-routed", "34%", "actually 38% cheaper"),
         ("Forced Haiku", "85%", "actually 75% cheaper")],
        LEGEND), 4200),
    "haiku-alone": (page(
        "Opus with helpers, or a cheaper model alone?",
        "v2, 5 harder coding tasks and an 85-page docs check · estimated API cost",
        [section("5 harder coding tasks", "sum of each task's mean, 2 runs each, 2 of them on ~100k lines", [
            {"name": "Opus only, blocked", "models": "Opus, no subagents", "kind": "opus", "cost": 4.36,
             "quality": ["Working code in every run", "Added a speed index: 2 of 2", "Flagged a symptom: 2 of 2"]},
            {"name": "Opus only, spontaneous", "models": "Opus, no subagents", "small": "could delegate, never did",
             "kind": "natural", "cost": 4.49, "delta": "+3%",
             "quality": ["Working code in every run", "Added a speed index: 2 of 2", "Flagged a symptom: 2 of 2"]},
            {"name": "Skill-routed", "models": "Opus + Haiku and Sonnet", "kind": "routed", "cost": 4.71, "delta": "+8%",
             "quality": ["Working code in every run", "Added a speed index: 2 of 2", "Flagged a symptom: 2 of 2"]},
            {"name": "Forced Haiku", "models": "Opus + Haiku subagents", "small": "Opus briefs and reviews", "kind": "haiku",
             "cost": 3.16, "delta": "−28%",
             "quality": ["Working code in every run", "Added a speed index: 2 of 2", "Flagged a symptom: 2 of 2"]},
            {"name": "Haiku alone", "models": "Haiku, no Opus at all", "kind": "solo", "cost": 0.26, "delta": "−94%",
             "quality": ["Working code in every run", "Added a speed index: 0 of 2", "Flagged a symptom: 0 of 2"]},
            {"name": "Sonnet alone", "models": "Sonnet, no Opus at all", "kind": "sonnet", "cost": 1.31, "delta": "−70%",
             "quality": ["Working code in every run", "Added a speed index: 2 of 2", "Flagged a symptom: 0 of 2"]},
         ], base="Opus alone"),
         section("Biggest review: docs check", "85 doc pages, mean of 2 runs", [
            {"name": "Opus only, blocked", "models": "Opus, no subagents", "kind": "opus", "cost": 4.11,
             "quality": ["36 and 38 of 92 (49 combined)"]},
            {"name": "Opus only, spontaneous", "models": "Opus, no subagents", "kind": "natural", "cost": 4.02,
             "delta": "−2%", "quality": ["39 and 35 of 92 (43 combined)"]},
            {"name": "Skill-routed", "models": "Opus + Sonnet subagents", "kind": "routed", "cost": 3.88, "delta": "−5%",
             "quality": ["55 and 70 of 92 (77 combined)"]},
            {"name": "Forced Haiku", "models": "Opus + Haiku subagents", "kind": "haiku", "cost": 1.93, "delta": "−53%",
             "quality": ["58 and 63 of 92 (72 combined)"]},
            {"name": "Haiku alone", "models": "Haiku, no Opus at all", "small": "up to 20% of line citations don't exist",
             "kind": "solo", "cost": 1.93, "delta": "−53%", "quality": ["42 and 41 of 92 (54 combined)"]},
            {"name": "Sonnet alone", "models": "Sonnet, no Opus at all", "small": "up to 32% of line citations don't exist",
             "kind": "sonnet", "cost": 3.21, "delta": "−22%", "quality": ["39 and 64 of 92 (67 combined)"]},
         ], base="Opus alone")],
        ["<b>Coding:</b> a bug with a trap, a vague feature, a refactor, a REST endpoint and a far-off bug. Scored by "
         "hidden tests written before the runs (some with flaws that penalised careful runs; see the write-up). "
         "The speed index (on the endpoint task) and flagging a symptom it couldn't reproduce (on the far-off bug) aren't hidden-test scores: they come from reading those runs' results.",
         "<b>Docs check:</b> real errors on a list of 92 verified against the code by Claude Opus. The list predates Haiku and Sonnet alone. "
         "Adding true claims checked later: forced Haiku 62 and 66, Haiku alone 52 and 45, Sonnet alone 39 and 69. <b>Combined</b> = distinct issues found by the two runs together."],
        [],
        "Two runs per setup · Haiku and Sonnet alone ran later, on the same Claude Code version · API list prices as a proxy for subscription usage"), 4420),
    "v2-reading": (page(
        "Reading a ~100k-line codebase",
        "buildbot (open source), v2 · estimated API cost per run",
        [section("All three reading tasks", "summaries + 2 doc checks, mean of 2-3 runs", [
            {**V2_OPUS, "cost": 8.98,
             "quality": ["Summaries: all 400 modules", "2-page doc check: 10 and 17 of 42 (22 combined)"]},
            {**V2_FREE, "cost": 8.26, "delta": "−8%",
             "quality": ["Summaries: all 400 modules", "2-page doc check: 9 and 9 of 42 (12 combined)"]},
            {**V2_SKILL, "models": "Opus + Sonnet", "small": "4-10 subagents per task", "cost": 10.19, "delta": "+13%",
             "quality": ["Summaries: all 400 modules", "2-page doc check: 17 and 21 of 42 (26 combined)"]},
            {**V2_OH, "small": "4-12 subagents per task", "cost": 4.44, "delta": "−51%",
             "quality": ["Summaries: all 400 modules", "2-page doc check: 20 and 23 of 42 (28 combined)"]},
         ], base="Opus alone"),
         section("Biggest job: 85-page doc check", "mean of 2 runs", [
            {**V2_OPUS, "small": "~7 min per run", "cost": 4.11, "quality": ["36 and 38 of 92 (49 combined)"]},
            {**V2_FREE, "small": "~9 min per run", "cost": 4.02, "delta": "−2%", "quality": ["39 and 35 of 92 (43 combined)"]},
            {**V2_SKILL, "models": "Opus + Sonnet", "small": "~4.5 min per run", "cost": 3.88, "delta": "−5%",
             "quality": ["55 and 70 of 92 (77 combined)"]},
            {**V2_OH, "small": "~6.5 min per run", "cost": 1.93, "delta": "−53%", "quality": ["58 and 63 of 92 (72 combined)"]},
            {**V2_H, "small": "~12 min per run", "cost": 1.93, "delta": "−53%", "quality": ["42 and 41 of 92 (54 combined)"]},
            {**V2_S, "small": "~6 min per run", "cost": 3.21, "delta": "−22%", "quality": ["39 and 64 of 92 (67 combined)"]},
         ], base="Opus alone")],
        ["<b>Summaries:</b> read about 400 code files (a “module” is one source code file) and write a short paragraph on what each does and what it works with. "
         "Every run covered all 400. 83-98% of the links they named matched a real import, with no clear gap between setups.",
         "<b>Doc check:</b> read buildbot's documentation pages and list where they disagree with the code, such as a wrong default value. There's a 2-page check and an 85-page check.",
         "<b>“36 and 38 of 92”:</b> each setup ran twice. Its first run found 36 and its second found 38 of the 92 real errors on the list. Higher is better. <b>Combined</b> = different errors found across both runs.",
         "<b>The list:</b> real errors the runs reported, each confirmed against the code by Claude Opus. It can't include errors every run missed, so 92 isn't every error in the docs. "
         "30 errors I planted were also found by every run, so they aren't scored here."],
        [("Skill-routed", "32-39%", "5% cheaper to 32% more expensive"),
         ("Opus plus Haiku", "82-88%", "actually 46-53% cheaper"),
         ("Haiku alone, 85-page check", "81%", "actually 53% cheaper"),
         ("Sonnet alone, 85-page check", "25%", "actually 22% cheaper")],
        V2_KEY + " · Haiku and Sonnet alone ran later, and only on the 85-page check", EXPL), 4900),
    "v2-coding-small": (page(
        "Writing code on a small project",
        "My own Python project, ~10k lines, v2 · estimated API cost for each group of tasks",
        [section("2 simple tasks", "a clearly specified feature + a planted bug, mean of 2 runs", [
            {**V2_OPUS, "cost": 0.89, "quality": ["Hidden tests: 13 and 13 of 13"]},
            {**V2_FREE, "cost": 1.04, "delta": "+17%", "quality": ["Hidden tests: 13 and 13 of 13"]},
            {**V2_SKILL, "cost": 1.05, "delta": "+18%", "quality": ["Hidden tests: 13 and 13 of 13"]},
            {**V2_OH, "cost": 0.70, "delta": "−21%", "quality": ["Hidden tests: 13 and 13 of 13"]},
         ], base="Opus alone"),
         section("3 harder tasks", "a bug with a trap, a vague feature, a refactor, mean of 2 runs", [
            {**V2_OPUS, "cost": 2.41, "quality": ["Hidden tests: 43 and 42 of 43"]},
            {**V2_FREE, "cost": 2.61, "delta": "+8%", "quality": ["Hidden tests: 43 and 42 of 43"]},
            {**V2_SKILL, "cost": 2.89, "delta": "+20%", "quality": ["Hidden tests: 43 and 42 of 43"]},
            {**V2_OH, "cost": 1.80, "delta": "−25%", "quality": ["Hidden tests: 43 and 42 of 43"]},
            {**V2_H, "cost": 0.11, "delta": "−95%", "quality": ["Hidden tests: 43 and 43 of 43"]},
            {**V2_S, "cost": 0.76, "delta": "−68%", "quality": ["Hidden tests: 43 and 43 of 43"]},
         ], base="Opus alone")],
        ["<b>Clear feature:</b> add an optional description to app profiles, following exact rules. <b>Planted bug:</b> from a user's report, find and fix a bug I added to the code.",
         "<b>Bug with a trap:</b> fix a real bug where apps set to start at login didn't start properly, and where the obvious fix fails. <b>Vague feature:</b> add a command to rename a profile, with one rule: whatever worked under the old name must keep working. <b>Refactor:</b> split a ~700-line file into smaller ones without changing behaviour.",
         "<b>“43 and 42 of 43”:</b> each setup ran twice. Its first run passed 43 and its second passed 42 of the 43 hidden tests. Higher is better. Hidden tests were written before the runs and added afterwards, so no run could see them. The project's own tests also passed in every run, once a rare flaky test was re-run.",
         "<b>The lost points are a flaw in my test, not bugs:</b> those runs added a useful extra field that my test didn't expect."],
        [("Simple, skill-routed", "32%", "actually cost 18% more"),
         ("Simple, Opus plus Haiku", "65%", "actually 21% cheaper"),
         ("Harder, skill-routed", "32%", "actually cost 20% more"),
         ("Harder, Opus plus Haiku", "66%", "actually 25% cheaper"),
         ("Harder, Haiku alone", "96%", "actually 95% cheaper"),
         ("Harder, Sonnet alone", "39%", "actually 68% cheaper")],
        V2_KEY + " · Haiku and Sonnet alone ran later, and not on the simple tasks", EXPL), 4900),
    "v2-coding-large": (page(
        "Writing code on a ~100k-line codebase",
        "buildbot (open source), v2 · estimated API cost for both tasks, mean of 2 runs",
        [section("2 harder tasks", "a REST endpoint + a bug far from its symptom", [
            {**V2_OPUS, "cost": 1.95, "quality": ["Official tests: 17 and 17 of 21", "Corrected tests: 21 and 21 of 21", "Speed index: 2 of 2", "Flagged the odd symptom: 2 of 2"]},
            {**V2_FREE, "cost": 1.88, "delta": "−4%", "quality": ["Official tests: 17 and 17 of 21", "Corrected tests: 21 and 21 of 21", "Speed index: 2 of 2", "Flagged the odd symptom: 2 of 2"]},
            {**V2_SKILL, "cost": 1.82, "delta": "−7%", "quality": ["Official tests: 17 and 21 of 21", "Corrected tests: 21 and 21 of 21", "Speed index: 2 of 2", "Flagged the odd symptom: 2 of 2"]},
            {**V2_OH, "cost": 1.36, "delta": "−30%", "quality": ["Official tests: 21 and 17 of 21", "Corrected tests: 21 and 21 of 21", "Speed index: 2 of 2", "Flagged the odd symptom: 2 of 2"]},
            {**V2_H, "cost": 0.15, "delta": "−93%", "quality": ["Official tests: 17 and 17 of 21", "Corrected tests: 21 and 21 of 21", "Speed index: 0 of 2", "Flagged the odd symptom: 0 of 2"]},
            {**V2_S, "cost": 0.56, "delta": "−71%", "quality": ["Official tests: 21 and 21 of 21", "Corrected tests: 21 and 21 of 21", "Speed index: 2 of 2", "Flagged the odd symptom: 0 of 2"]},
         ], base="Opus alone")],
        ["<b>REST endpoint:</b> add a web API address returning how many of a builder's builds passed, failed and so on, staying fast with millions of builds. "
         "<b>Far-off bug:</b> notifications blamed the wrong people, and the cause was elsewhere, in buildbot's database code. I planted this bug, and buildbot's 6,400+ existing tests don't catch it.",
         "<b>“17 and 17 of 21”:</b> each setup ran twice, and each run's hidden tests passed are shown. Higher is better. Hidden tests were written before the runs. Buildbot's own tests also passed in every run.",
         "<b>Official vs corrected:</b> my test data wrongly left out a completion time, so careful runs lost 4 points. The official scores stand. The corrected test fixes only that, and was written after seeing the first failure.",
         "<b>Speed index</b> (endpoint task): did the run add a database index? <b>Flagged the odd symptom</b> (bug task): the report described a symptom the bug doesn't seem to cause, so did the run say it couldn't reproduce it? "
         "Tests don't score either one: they come from reading the runs' code and reports. 2 of 2 means both runs did it."],
        [("Skill-routed", "38%", "actually 7% cheaper"),
         ("Opus plus Haiku", "67%", "actually 30% cheaper"),
         ("Haiku alone", "93%", "actually 93% cheaper"),
         ("Sonnet alone", "35%", "actually 71% cheaper")],
        V2_KEY + " · Haiku and Sonnet alone ran later", EXPL), 4400),
    "v2-quality-price": (page(
        "Quality vs price: what does each real error cost?",
        "v2, doc checks on two codebases · estimated API cost per real error found",
        [section("85-page doc check", "buildbot, ~100k lines", [
            {**V2_OPUS, "cost": 0.11, "quality": ["Found 36 and 38 of 92", "Both runs missed 43", "False claims: 0"]},
            {**V2_FREE, "cost": 0.11, "delta": "−2%", "quality": ["Found 39 and 35 of 92", "Both runs missed 49", "False claims: 0"]},
            {**V2_SKILL, "models": "Opus + Sonnet", "cost": 0.06, "delta": "−44%", "quality": ["Found 55 and 70 of 92", "Both runs missed 15", "False claims: 0"]},
            {**V2_OH, "cost": 0.03, "delta": "−71%", "quality": ["Found 58 and 63 of 92", "Both runs missed 20", "False claims: 0"]},
            {**V2_H, "small": "up to 20% of line citations don't exist", "cost": 0.05, "delta": "−58%", "quality": ["Found 42 and 41 of 92", "Both runs missed 38", "False claims: 1"]},
            {**V2_S, "small": "up to 32% of line citations don't exist", "cost": 0.06, "delta": "−44%", "quality": ["Found 39 and 64 of 92", "Both runs missed 25", "False claims: 1"]},
         ], base="Opus alone", cost_label="Cost per real error"),
         section("80-page doc check", "beets, ~52k lines, v1 runs re-scored", [
            {"name": "Forced Opus", "models": "Opus, no subagents", "small": "told not to delegate", "kind": "opus", "cost": 0.25, "quality": ["Found 41 and 33 of 61", "Both runs missed 17"]},
            {**V2_FREE, "cost": 0.19, "delta": "−22%", "quality": ["Found 27 and 35 of 61", "Both runs missed 25"]},
            {**V2_SKILL, "models": "Opus + Sonnet", "cost": 0.14, "delta": "−45%", "quality": ["Found 30 and 28 of 61", "Both runs missed 26"]},
            {**V2_OH, "cost": 0.05, "delta": "−80%", "quality": ["Found 30 and 30 of 61", "Both runs missed 22"]},
         ], base="forced Opus", cost_label="Cost per real error")],
        ["<b>Doc check:</b> read a project's documentation pages and list where they disagree with the code, such as a wrong default value.",
         "<b>Cost per real error:</b> a setup's mean cost per run, divided by the real errors it found per run. Lower is better, but it treats a typo and a serious error the same, and a cheap setup can win while finding fewer errors.",
         "<b>“36 and 38 of 92”:</b> each setup ran twice. Its first run found 36 and its second found 38 of the 92 real errors on the list. Higher is better. The list holds errors the runs reported, each confirmed against the code by Claude Opus, so it can't include errors every run missed.",
         "<b>Both runs missed:</b> errors on the list that neither of the setup's two runs found. Lower is better. <b>False claims:</b> errors a run reported that I confirmed were wrong. This is a minimum, judged by Claude Opus knowing which setup wrote each report, and not counted on beets."],
        [],
        V2_KEY, EXPL), 4320),
    "v2-reading-depth": (page(
        "How much did each setup actually read?",
        "v2 doc checks, measured from the run transcripts · two runs per setup",
        [depth_section("85-page doc check", "buildbot, ~100k lines", [
            {**V2_FREE, "read": (454, 471), "written": (31, 26), "errors": "39 and 35 of 92", "combined": 43,
             "cost": 4.02, "delta": "−2%"},
            {**V2_OPUS, "read": (532, 563), "written": (30, 25), "errors": "36 and 38 of 92", "combined": 49,
             "cost": 4.11},
            {**V2_S, "read": (532, 719), "written": (31, 43), "errors": "39 and 64 of 92", "combined": 67,
             "cost": 3.21, "delta": "−22%"},
            {**V2_H, "read": (620, 697), "written": (107, 103), "errors": "42 and 41 of 92", "combined": 54,
             "cost": 1.93, "delta": "−53%"},
            {**V2_SKILL, "models": "Opus + Sonnet", "small": "5-7 subagents", "read": (928, 981), "written": (61, 60),
             "errors": "55 and 70 of 92", "combined": 77, "cost": 3.88, "delta": "−5%"},
            {**V2_OH, "small": "6-7 subagents", "read": (1252, 1649), "written": (188, 237),
             "errors": "58 and 63 of 92", "combined": 72, "cost": 1.93, "delta": "−53%"},
         ]),
         depth_section("80-page doc check", "beets, ~52k lines, v1 runs re-scored", [
            {**V2_FREE, "read": (618, 835), "written": (34, 30), "errors": "27 and 35 of 61", "combined": 36,
             "cost": 6.01, "delta": "−35%"},
            {"name": "Forced Opus", "models": "Opus, no subagents", "small": "told not to delegate", "kind": "opus",
             "read": (868, 698), "written": (50, 44), "errors": "41 and 33 of 61", "combined": 44, "cost": 9.20},
            {**V2_SKILL, "models": "Opus + Sonnet", "small": "8 subagents", "read": (1075, 1134), "written": (53, 60),
             "errors": "30 and 28 of 61", "combined": 35, "cost": 3.95, "delta": "−57%"},
            {**V2_OH, "small": "8 subagents", "read": (1291, 1283), "written": (167, 188),
             "errors": "30 and 30 of 61", "combined": 39, "cost": 1.49, "delta": "−84%"},
         ])],
        ["<b>What it shows:</b> on buildbot, real errors rose with the amount read. On beets they didn't: forced Opus read less than either delegated setup and still found the most. So volume can't be the whole story. The model matters too: Sonnet alone's second run read about as much as Haiku alone's runs and found 64, against their 41 and 42.",
         "<b>Tool output read:</b> characters returned to the agents by their tools, mostly files and command output, summed across Opus and its subagents. Subagents' reports back to Opus aren't counted. Re-reads are, so this measures work done, not distinct pages. Bars show the mean of two runs.",
         "<b>Tokens written:</b> all output tokens, thinking included, summed across Opus and its subagents.",
         "<b>Est. API cost:</b> mean cost per run at API list prices, a proxy for subscription usage. Percentages compare with the baseline: Opus alone on buildbot, forced Opus on beets. Bars use one scale across both checks.",
         "<b>“36 and 38 of 92”:</b> each setup ran twice. Its first run found 36 and its second found 38 of the 92 real errors on the list. Higher is better. The list holds errors the runs reported, each confirmed against the code by Claude Opus, so it can't include errors every run missed. <b>Combined</b> = different errors found across both runs."],
        [],
        "Measured after the runs on two tasks, not a planned test, so treat this as a hint · Haiku and Sonnet alone ran later", EXPL), 4140),
    "opus-token-comparison": (page(
        "Same model, same task: what did the instruction change?",
        "beets 80-page doc check, ~52k lines, v1 runs re-scored · two runs per setup",
        [depth_section("Opus told not to delegate vs Opus left alone", "neither used subagents", [
            {"name": "Forced Opus", "models": "Opus, no subagents", "small": "told not to delegate", "kind": "opus",
             "read": (868, 698), "written": (50, 44), "errors": "41 and 33 of 61", "combined": 44, "cost": 9.20},
            {**V2_FREE, "read": (618, 835), "written": (34, 30), "errors": "27 and 35 of 61", "combined": 36,
             "cost": 6.01, "delta": "−35%"},
         ], read_max=783, written_max=47, cost_max=9.20)],
        ["<b>What it shows:</b> compared with Opus left alone, Opus told not to delegate read about the same (about 8% more on average), but wrote about 47% more and cost 53% more. It also found more real errors: 44 across its two runs, against 36.",
         "<b>Tool output read:</b> characters returned to Opus by its tools, mostly files and command output. These are characters, not tokens. Bars show the mean of two runs.",
         "<b>Tokens written:</b> all output tokens, thinking included. Bars show the mean of two runs.",
         "<b>Est. API cost:</b> mean cost per run at API list prices, a proxy for subscription usage. The percentage compares with Forced Opus.",
         "<b>“41 and 33 of 61”:</b> each setup ran twice, and each number is one run's real errors found, out of 61 on the list. Higher is better. <b>Combined</b> = different errors found across both runs."],
        [],
        "Two runs per setup, and the effect of the instruction wasn't tested on its own, so treat this as a hint", EXPL), 2220),
}


def main():
    out_dir = Path(sys.argv[1]).resolve()
    names = sys.argv[2:] or list(CHARTS)
    with tempfile.TemporaryDirectory() as work:
        for name in names:
            doc, height = CHARTS[name]
            src = Path(work) / f"{name}.html"
            src.write_text(doc, encoding="utf-8")
            prof = Path(work) / f"profile-{name}"
            prof.mkdir()
            subprocess.run(["firefox", "--headless", "--no-remote", "--profile", str(prof),
                            "--screenshot", str(out_dir / f"{name}.png"),
                            f"--window-size={WIDTH},{height}", src.as_uri()],
                           check=True, capture_output=True, timeout=120)
            print(name, "done")


if __name__ == "__main__":
    main()
