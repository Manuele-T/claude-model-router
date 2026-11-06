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
COLORS = {"opus": "#2b7bd6", "natural": "#c2407f", "routed": "#ea6a36", "haiku": "#2e9e6b", "solo": "#b8860b"}
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
"""


def esc(s):
    return html.escape(s)


def section(title, note, rows, base="forced Opus"):
    top = max(r["cost"] for r in rows)
    out = [f"<h2>{esc(title)} <span>· {esc(note)}</span></h2>",
           '<div class="thead"><div>Run</div><div>Models used</div><div>Quality (higher is better)</div>'
           f'<div>Est. API cost</div><div>vs {esc(base)}</div></div>']
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


def page(title, subtitle, sections, explanation, checker, foot_note):
    expl = ('<div class="expl"><h3>What the quality column measures</h3>'
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
        "Opus, Opus plus Haiku, or Haiku alone?",
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
         ], base="Opus alone")],
        ["<b>Coding:</b> a bug with a trap, a vague feature, a refactor, a REST endpoint and a far-off bug. Scored by "
         "hidden tests written before the runs (some with flaws that penalised careful runs; see the write-up). "
         "The speed index (on the endpoint task) and flagging a symptom it couldn't reproduce (on the far-off bug) aren't hidden-test scores: they come from reading those runs' results.",
         "<b>Docs check:</b> real errors on a list of 92 verified against the code by Claude Opus. The list predates Haiku alone. "
         "Adding true claims checked later: forced Haiku 62 and 66, Haiku alone 52 and 45. <b>Combined</b> = distinct issues found by the two runs together."],
        [],
        "Two runs per setup · Haiku alone ran later, on the same Claude Code version · API list prices as a proxy for subscription usage"), 4000),
    "v2-reading": (page(
        "Delegating to cheaper models: reading a ~100k-line codebase",
        "buildbot (open source), 408 modules · estimated API cost",
        [section("All three tasks", "module summaries + 2 docs checks, mean per run", [
            {"name": "Opus only, blocked", "models": "Opus, no subagents", "kind": "opus", "cost": 8.98,
             "quality": ["Summaries: all 400 modules", "2-page check: 10 and 17 of 42 (22 combined)"]},
            {"name": "Opus only, spontaneous", "models": "Opus, no subagents", "small": "could delegate, never did",
             "kind": "natural", "cost": 8.26, "delta": "−8%",
             "quality": ["Summaries: all 400 modules", "2-page check: 9 and 9 of 42 (12 combined)"]},
            {"name": "Skill-routed", "models": "Opus + Sonnet", "small": "4-10 subagents per task", "kind": "routed",
             "cost": 10.19, "delta": "+13%",
             "quality": ["Summaries: all 400 modules", "2-page check: 17 and 21 of 42 (26 combined)"]},
            {"name": "Forced Haiku", "models": "Opus + Haiku", "small": "4-12 subagents per task", "kind": "haiku",
             "cost": 4.44, "delta": "−51%",
             "quality": ["Summaries: all 400 modules", "2-page check: 20 and 23 of 42 (28 combined)"]},
         ], base="Opus alone"),
         section("Biggest job: docs check", "85 doc pages, mean of 2 runs", [
            {"name": "Opus only, blocked", "models": "Opus, no subagents", "small": "~7 min per run", "kind": "opus",
             "cost": 4.11, "quality": ["36 and 38 of 92 (49 combined)"]},
            {"name": "Opus only, spontaneous", "models": "Opus, no subagents", "small": "~9 min per run", "kind": "natural",
             "cost": 4.02, "delta": "−2%", "quality": ["39 and 35 of 92 (43 combined)"]},
            {"name": "Skill-routed", "models": "Opus + Sonnet", "small": "~4.5 min per run", "kind": "routed",
             "cost": 3.88, "delta": "−5%", "quality": ["55 and 70 of 92 (77 combined)"]},
            {"name": "Forced Haiku", "models": "Opus + Haiku", "small": "~6.5 min per run", "kind": "haiku",
             "cost": 1.93, "delta": "−53%", "quality": ["58 and 63 of 92 (72 combined)"]},
            {"name": "Haiku alone", "models": "Haiku, no Opus", "small": "~12 min per run", "kind": "solo",
             "cost": 1.93, "delta": "−53%", "quality": ["42 and 41 of 92 (54 combined)"]},
         ], base="Opus alone")],
        ["<b>Summaries:</b> one paragraph per module, saying what it does and what it works with. Scored on coverage. "
         "83-98% of named links were backed by a real import, with no clear gap between setups.",
         "<b>Docs checks:</b> find where the docs disagree with the code. 30 errors were planted first, and every run found them all. "
         "The scores are real errors on lists verified against the code by Claude Opus, built from the runs' own findings, so \"of 92\" isn't true recall. "
         "<b>Combined</b> = distinct issues found by the two runs together."],
        [("Skill-routed", "32-39%", "5% cheaper to 32% more expensive"),
         ("Forced Haiku", "82-88%", "actually 46-53% cheaper")],
        "Mean of 2-3 runs · Haiku alone ran later, and only on the 85-page check · API list prices as a proxy for subscription usage"), 4300),
    "v2-coding": (page(
        "Delegating to cheaper models: writing code",
        "7 coding tasks, 2 runs per setup · estimated API cost per task group",
        [section("2 simple tasks, small project", "a clear feature + a planted bug", [
            {"name": "Opus only, blocked", "models": "Opus, no subagents", "kind": "opus", "cost": 0.89,
             "quality": ["Hidden tests: 13 of 13, both runs"]},
            {"name": "Opus only, spontaneous", "models": "Opus, no subagents", "kind": "natural", "cost": 1.04,
             "delta": "+17%", "quality": ["Hidden tests: 13 of 13, both runs"]},
            {"name": "Skill-routed", "models": "Opus + Sonnet or Haiku", "kind": "routed", "cost": 1.05, "delta": "+18%",
             "quality": ["Hidden tests: 13 of 13, both runs"]},
            {"name": "Forced Haiku", "models": "Opus + Haiku", "kind": "haiku", "cost": 0.70, "delta": "−21%",
             "quality": ["Hidden tests: 13 of 13, both runs"]},
         ], base="Opus alone"),
         section("3 harder tasks, small project", "a bug with a trap, a vague feature, a refactor", [
            {"name": "Opus only, blocked", "models": "Opus, no subagents", "kind": "opus", "cost": 2.41,
             "quality": ["Hidden tests: 43 and 42 of 43"]},
            {"name": "Opus only, spontaneous", "models": "Opus, no subagents", "kind": "natural", "cost": 2.61,
             "delta": "+8%", "quality": ["Hidden tests: 43 and 42 of 43"]},
            {"name": "Skill-routed", "models": "Opus + Sonnet and Haiku", "kind": "routed", "cost": 2.89, "delta": "+20%",
             "quality": ["Hidden tests: 43 and 42 of 43"]},
            {"name": "Forced Haiku", "models": "Opus + Haiku", "kind": "haiku", "cost": 1.80, "delta": "−25%",
             "quality": ["Hidden tests: 43 and 42 of 43"]},
            {"name": "Haiku alone", "models": "Haiku, no Opus", "kind": "solo", "cost": 0.11, "delta": "−95%",
             "quality": ["Hidden tests: 43 and 43 of 43"]},
         ], base="Opus alone"),
         section("2 harder tasks, ~100k lines", "a REST endpoint, a bug far from its symptom", [
            {"name": "Opus only, blocked", "models": "Opus, no subagents", "kind": "opus", "cost": 1.95,
             "quality": ["Official tests: 17 and 17 of 21", "Corrected tests: 21 and 21 of 21", "Speed index: 2 of 2", "Flagged symptom: 2 of 2"]},
            {"name": "Opus only, spontaneous", "models": "Opus, no subagents", "kind": "natural", "cost": 1.88, "delta": "−4%",
             "quality": ["Official tests: 17 and 17 of 21", "Corrected tests: 21 and 21 of 21", "Speed index: 2 of 2", "Flagged symptom: 2 of 2"]},
            {"name": "Skill-routed", "models": "Opus + Sonnet and Haiku", "kind": "routed", "cost": 1.82, "delta": "−7%",
             "quality": ["Official tests: 17 and 21 of 21", "Corrected tests: 21 and 21 of 21", "Speed index: 2 of 2", "Flagged symptom: 2 of 2"]},
            {"name": "Forced Haiku", "models": "Opus + Haiku", "kind": "haiku", "cost": 1.36, "delta": "−30%",
             "quality": ["Official tests: 21 and 17 of 21", "Corrected tests: 21 and 21 of 21", "Speed index: 2 of 2", "Flagged symptom: 2 of 2"]},
            {"name": "Haiku alone", "models": "Haiku, no Opus", "kind": "solo", "cost": 0.15, "delta": "−93%",
             "quality": ["Official tests: 17 and 17 of 21", "Corrected tests: 21 and 21 of 21", "Speed index: 0 of 2", "Flagged symptom: 0 of 2"]},
         ], base="Opus alone")],
        ["<b>Hidden tests:</b> written before the runs and copied in afterwards, so no run could see them. Each run's two scores are shown. "
         "The whole unit suite also passed in every run, once a rare flaky test was re-run.",
         "<b>Lost points are my test flaws, not bugs:</b> the 42s are runs that added a useful field my test didn't expect. The official 17s are runs that "
         "sensibly required a completion time my test data left out. The corrected test fixes only that, and was written after seeing the first failure.",
         "<b>Speed index and flagged symptom</b> aren't test scores. Runs were asked for an endpoint fast on millions of builds, and whether they added a database index "
         "comes from reading the code. The bug report also described a symptom the bug doesn't seem to cause, and whether a run said so comes from reading its report."],
        [],
        "Sum of each task's mean cost · Haiku alone ran later, and not on the simple tasks · API list prices as a proxy for subscription usage"), 5400),
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
