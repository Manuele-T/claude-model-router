# claude-model-router

Does delegating work to cheaper models actually save money?

This repo is an experiment to find out. It has two parts:

- **A Claude Code skill** (`skills/model-router/SKILL.md`) that makes Opus the manager, handing work to cheaper subagents and logging every decision.
- **A Python checker** (`scripts/verify_models.py`) that reads Claude Code's own transcripts to prove which model actually ran and how many tokens each one used.

## The experiments

### v1: reading code

20 tasks on three codebases, up to ~52k lines, comparing Opus alone, Opus free to delegate, my routing skill, and Opus delegating only to Haiku.

- **Small codebase:** Opus alone was the most accurate per run, and the skill cost 14-30% more for no gain.
- **~22k lines:** Opus plus Haiku matched Opus's quality at 41% less.
- **~52k lines:** Opus plus Haiku cost 75% less, but forced Opus found the most on the biggest docs check.
- **Paper estimates misled:** re-pricing delegated work at Opus rates suggested 34-85% savings, while real results ranged from 30% more expensive to 75% cheaper.

**[Read the v1.0 results and discussion](docs/v1-results.md)**

### v2: bigger code, writing code, and no Opus at all

234 runs: 3 reading tasks on buildbot (~100k lines), 7 coding tasks scored by hidden tests, and 16 short coding tasks, 14 of them hiding a trap. It also added Haiku alone and Sonnet alone, with no Opus anywhere.

- **Coding:** every setup produced working code. On five harder tasks, Haiku alone cost 94% less than Opus alone.
- **Big reviews:** on an 85-page docs check, Opus plus Haiku cost half as much as Opus alone and found over 60% more real errors. It also found about 30% more than Haiku alone at the same price.
- **What Opus adds is care:** all 8 Opus-led runs added a speed index when asked for speed and flagged a symptom they couldn't reproduce. Neither Haiku-alone run did either. *(Correction: the flag didn't hold up in 15 later Opus-led runs; see v3.)*
- **Sonnet alone** cost 70% less than Opus alone on the five harder tasks, but 5 times Haiku alone, and landed between them on care.
- **Time:** on big reading jobs Opus plus Haiku was no slower than Opus alone (about 6 against 7 minutes on the 85-page check, 14 against 20 for all three reading tasks). On coding it was a few minutes slower (27 against 21 on the five harder tasks), while Haiku and Sonnet alone took about 13 and 11.
- **I tried to make the cheap models fail, and mostly couldn't.** Across those 16 short tasks, there was one real hidden-test miss in 128 runs, and Haiku alone cost about 5% of Opus alone. Opus was more thorough, finding every planted bug in a code review where Haiku found 2 of 3, but it wasn't better across the board: on a timing bug, all 4 Opus-led runs failed and the only pass was Haiku.
- **My routing skill rarely paid off**, and left alone, Opus never delegated.

**[Read the v2.0 results and discussion](docs/v2-results.md)**

### v3: Haiku with an Opus review, and why splitting work helps

80 scored runs in three parts. **Part 1:** Haiku does a coding task, then a fresh Opus session reviews it once. 20 runs on the four buildbot tasks where Opus added care in v2, plus 25 more runs giving Opus plus Haiku and Opus alone 5 runs each to compare with.

- **It cost 61% less than Opus alone** and 52% less than Opus plus Haiku, with every hidden test passing.
- **The review caught what Haiku left out:** a release note, a missing index, a missed bug, a race condition.
- **With 5 runs each, Opus plus Haiku was a little more reliable** (every planted bug in every review) and cost about 1.5x as much as the review setup.
- **The review setup is slower:** about 40% more wall time than Opus plus Haiku (12 against 8 minutes over the four tasks), because the review waits for Haiku to finish.
- **A v2 finding didn't hold.** Every Opus-led run in v2 flagged a symptom it couldn't reproduce. None of 15 later Opus-led runs did, Opus alone included, with the same prompt and model. It changed with the day, not the setup, and restoring the one Claude Code instruction that had changed in between didn't bring it back.

**Parts 2 and 3:** the 85-page docs check split across exactly 1, 4, 8 or 16 Haiku helpers, then 16 Opus helpers, 5 runs each, scored blind against a list of 160 real errors.

- **More Haiku helpers found far more for about the same money.** 1 helper found 20 real errors per run for $1.25, 16 helpers found 86 for $1.69 (Opus $1.30, Haiku $0.39). Opus alone found 37-40 for about $4 (v2 runs, re-scored on the same list).
- **Opus helpers didn't find more.** With the same 16 groups, Opus helpers found 89 for $8.12 (lead $1.16, helpers $6.96), almost 5 times the cost. They made fewer false claims (4 per run against 10).
- **So splitting is what helps, not the model.** Small pieces seem to get read more carefully, and Haiku is good enough for each one.
- **The review setup was the worst value on this big review** (50 for $3.04): the review can only check what Haiku reported.
- **Opus alone didn't miss errors because it skipped pages or compacted its context.** It saw every page and still missed the lines.

<p align="center">
  <img src="charts/v3-splitting.png" alt="85-page docs check on buildbot, mean per run over 5 runs. 1 Haiku helper: 20 real errors, $1.25 (Opus $0.46 + Haiku $0.79), about 7 minutes. 4 Haiku helpers: 69, $2.12 (Opus $0.94 + Haiku $1.19), about 6 minutes. 8 Haiku helpers: 63, $1.63 (Opus $1.04 + Haiku $0.59), about 5 minutes. 16 Haiku helpers: 86, $1.69 (Opus $1.30 + Haiku $0.39), about 4 minutes. 16 Opus helpers: 89, $8.12 (lead $1.16 + helpers $6.96), about 4 minutes. Haiku, then Opus review: 50, $3.04 (Haiku $1.72 + Opus $1.32), about 12 minutes. For comparison, v2 runs re-scored on the same list: Opus alone 37 and 40 for $4.11, Opus plus Haiku 62 and 63 for $1.93 (Opus $1.08 + Haiku $0.85)" width="800">
</p>


**[Read the v3.0 results and discussion](docs/v3-results.md)**

## What I'd use today

| What you're doing | What I'd use | Why |
| --- | --- | --- |
| A small, testable coding task you'll review yourself | **Haiku alone** | 1-12% of Opus alone's cost on five harder coding tasks, with working code in every run, in about 60% of the time |
| Coding where care matters | **Opus delegating to Haiku** | 28% cheaper than Opus alone on those tasks, and Opus reviews the work, but a few minutes slower |
| A big review or audit | **Opus with many Haiku helpers, one small piece each** | On an 85-page docs check, 16 Haiku helpers found more than twice what Opus alone found, for 40% of the cost, and as much as 16 Opus helpers for a fifth of theirs |
| Reviewing code, or anything where every case has to be covered | **Keep Opus involved** | Found all 3 planted bugs in every review run, where Haiku alone found 2 of 3 both times |

<p align="center">
  <img src="charts/haiku-alone.png" alt="Five harder coding tasks: Opus alone $4.36, spontaneous Opus $4.49, skill-routed $4.71, forced Haiku $3.16, Haiku alone $0.26, Sonnet alone $1.31, all with working code. Docs check: Opus alone $4.11 finding 36 and 38 of 92 real errors, spontaneous Opus $4.02 finding 39 and 35, skill-routed $3.88 finding 55 and 70, forced Haiku $1.93 finding 58 and 63, Haiku alone $1.93 finding 42 and 41, Sonnet alone $3.21 finding 39 and 64. Wall time per run: about 21, 22, 24, 27, 13 and 11 minutes for the coding tasks, and about 7, 9, 4, 6, 12 and 6 minutes for the docs check, in the same order" width="800">
</p>

**Treat these as strong hints, not proof.** Most setups ran twice per task, costs are API prices used as a proxy for subscription usage, and Claude Opus wrote my hidden tests and verified the errors. Three of those tests had flaws, reported in the results. Even tasks built to trip it up didn't make Haiku alone clearly fail, so I don't know where its limit is. Test on your own work.

**Takeaway: cheaper tokens don't necessarily mean cheaper tasks, and the most expensive model isn't always the one doing the useful work. Measure the whole workflow.**

## Setup

Requires Claude Code 2.1.305 or later, Python 3.8+, and `CLAUDE_CODE_SUBAGENT_MODEL` unset.

```bash
ln -s ~/Documents/Coding/claude-model-router/skills/model-router ~/.claude/skills/model-router
python3 scripts/verify_models.py --since 2026-10-25
```

Start a prompt with `Use the model-router skill.` to trigger it, or `no routing.` to turn it off. Per-run numbers are in [`data/results.md`](data/results.md).

## Credits

The routing skill's design (default to Haiku, escalate only with a reason, a routing log, user overrides) follows [Maleko91/claude-code-adaptive-subagents](https://github.com/Maleko91/claude-code-adaptive-subagents), which reports 3-15x token savings. The `SKILL.md` here was written separately. What this repo adds is the checker, which verifies which model actually ran, and the head-to-head comparison against forced Opus.

## License

[MIT](LICENSE). Use, modify and share it freely; keep the copyright notice so the credit stays with the work.
