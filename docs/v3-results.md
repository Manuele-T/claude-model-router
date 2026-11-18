# v3.0 results and discussion

[Back to the README](../README.md) · [v1.0 results](v1-results.md) · [v2.0 results](v2-results.md)

v3 has three parts, all done and written up below. Part 1 (with follow-ups 1b, 1c and 1d) is about coding; Parts 2 and 3 are about one big review.

**The questions:**

1. **Haiku then an Opus review:** if Haiku alone does a coding task and a fresh Opus session reviews it once, does that get back the care Opus added in v2, at close to Haiku's cost? *(Part 1, with 1b and 1c, done)*
2. **Coverage:** on the 85-page docs check where Opus plus Haiku found the most, how do errors found and cost change with the number of Haiku subagents? *(Part 2, done)*
3. **Cheap model or split:** with the same split, do Opus subagents find clearly more than Haiku subagents, and at what cost? *(Part 3, done)*

Costs are API list prices used as a proxy for subscription usage. Where a setup uses more than one model, the cost is split per model. Per-run numbers and scoring rules are in [`data/results.md`](../data/results.md).

## Part 1: Haiku does the work, Opus reviews it once

v2 found that on coding tasks every setup produced working code, and what Opus added was care the hidden tests didn't see: a database index when asked for speed, flagging a symptom it couldn't reproduce, a release note, and the third planted bug in a code review. Haiku alone did none of these. (One of these, the flag, turned out not to hold: see [Parts 1b and 1c](#parts-1b-and-1c-five-runs-for-the-other-setups-too).)

So I added one setup: **Haiku alone does the task, then a fresh Opus session is told another session did it, checks the changes and the answer against the task, and fixes anything wrong or missing.** Same four buildbot tasks as v2, prompts and hidden tests unchanged, 5 runs each, 20 runs. The [design was committed before any run](../data/tasks-v13.md), and the answers were scored blind, shuffled together with every v2 answer to the same tasks.

| Mean cost per run | Opus alone | Opus plus Haiku | Haiku alone | **Haiku, then Opus review** |
| --- | --- | --- | --- | --- |
| REST endpoint, fast on millions of builds | $1.16 | $0.93 | $0.14 | **$0.46** |
| Wrong blamelists across branches | $0.79 | $0.43 | $0.01 | **$0.17** |
| Change a default timeout | $0.16 | $0.23 | $0.01 | **$0.13** |
| Review a commit with planted bugs | $0.12 | $0.22 | under $0.01 | **$0.11** |
| **All four** | **$2.23** | **$1.81** | **about $0.17** | **$0.86 (-61%)** |

| Care point | Opus alone | Opus plus Haiku | Haiku alone (v2, then v3 step 1) | **Haiku, then Opus review** |
| --- | --- | --- | --- | --- |
| Index with a migration | 2 of 2 | 2 of 2 | 0 of 2, then 4 of 5 | **5 of 5** |
| Said it couldn't reproduce part of the bug report | 2 of 2 | 2 of 2 | 0 of 2, then 0 of 5 | **0 of 5** |
| Release note | 2 of 2 | 2 of 2 | 0 of 2, then 0 of 5 | **5 of 5** |
| Planted bugs found in the review, of 3 | 3, 3 | 3, 3 | 2, 2, then 3, 2, 2, 2, 3 | **3, 3, 3, 2, 3** |

- **It cost 61% less than Opus alone and 52% less than Opus plus Haiku**, about 5 times Haiku alone. The review is about 85% of the bill.
- **Every run passed every hidden test**, before and after the review. The review broke nothing.
- **The review catches what Haiku leaves out.** It added the release note every time, added the index the one time Haiku skipped it, found the missed bug in 2 of 3 reviews, and fixed a real race condition in one run where two builds finishing at once could make one fail.
- **It doesn't question the problem.** My bug report on one task describes a symptom the planted bug doesn't seem to cause. Every Opus-led run in v2 said it couldn't reproduce that part. Haiku explained it away instead, and all 5 reviews accepted that explanation. *Correction (2026-11-13): Parts 1b and 1c show this isn't about the review. Opus alone and Opus plus Haiku, 5 new runs each, also explained it away every time.*
- **Haiku alone did better than v2 suggested** on the speed index: 4 of 5 this time, against 0 of 2. Two runs per setup was too few.

So on small, well-defined coding tasks, Haiku plus one Opus review got most of Opus's care at about half the cost of Opus plus Haiku. Omissions get caught.

## Parts 1b and 1c: five runs for the other setups too

Part 1 compared 5 runs of the review setup with v2's 2 runs per setup. So I re-ran **Opus plus Haiku** 5 more times on all four tasks (Part 1b), and, after seeing that result, **Opus alone** 5 more times on the blamelist task (Part 1c). Setups, prompts and tests unchanged; [design committed before each part](../data/tasks-v14.md); answers scored blind again.

| Mean cost per run | Opus plus Haiku (5 new runs) | **Haiku, then Opus review** |
| --- | --- | --- |
| REST endpoint | $0.62 | **$0.46** |
| Wrong blamelists | $0.30 | **$0.17** |
| Change a default timeout | $0.23 | **$0.13** |
| Review a commit | $0.19 | **$0.11** |
| **All four** | **$1.34** | **$0.86 (-36%)** |

- **Opus plus Haiku was the more reliable of the two.** Every hidden test passed. It added the index and the release note in all 5 runs and found all 3 planted bugs in all 5 reviews, against 4 of 5 for the review setup.
- **The review setup stayed 36% cheaper.** On these tasks the gap in care was one missed bug in 5 reviews.
- **But it was slower** *(added 2026-11-16)*. Wall time, summed over the four tasks' means: 11.6 minutes for the review setup against 8.2 for Opus plus Haiku, about 40% more, because the review can only start once Haiku has finished. On the blamelist task, Opus alone took 1.4 minutes, Opus plus Haiku 2.0 and the review setup 2.8. This compares runs from 12-13 November only: v2's runs of the same setups, a week earlier, took up to twice as long, so speed drifts between days too.
- **The "couldn't reproduce" flag depends on the day, not the setup.** All 8 Opus-led runs from 6 November said it. None of the 15 Opus-led runs from 12-13 November did, including 5 runs of Opus alone doing the whole investigation itself. Same Claude Code version, model, code and prompt, though the starting context differed by about 100 tokens (the runs load my global Claude Code setup, which changed slightly in between). So this point no longer counts as evidence for any setup.
- **The cause is still unknown.** Comparing the requests saved in the transcripts, Claude Code's own instructions changed between the two days with the same version number. I put back the one change I could, an instruction to tell the user the plan and give updates, in 5 more runs of Opus alone (Part 1d). None flagged the symptom, so that instruction isn't the cause on its own. What's left is two other changes in Claude Code's instructions, a change on Anthropic's side, or a lucky batch.

**Correction (2026-11-13).** v2 and Part 1 read that flag as care Opus adds, and Part 1 said Opus questioned the report only when it led the investigation. Neither holds with more runs. The [v2 results](v2-results.md) carry a note pointing here.

**Takeaway (Part 1): on small coding tasks, a single Opus review recovers most of what Haiku leaves out, and Opus plus Haiku is a little more reliable and quicker for about 1.5x the cost. Two runs per setup weren't enough to see that.**

## Limitations (Part 1)

- Four tasks, chosen because Opus was already known to add something there. This doesn't show what a review catches on tasks nobody has studied.
- The review prompt tells Opus to look for problems, which Opus alone never got. A fair reading is "Opus reviewing Haiku's work", not "Haiku plus a review is as careful as Opus alone".
- v2's comparison setups ran twice per task. Parts 1b and 1c added 5 runs for Opus plus Haiku on all four tasks and for Opus alone on one, but Opus alone still has only 2 runs on the other three.
- Results can shift between days with the same Claude Code version (Parts 1c and 1d), so a batch run on one day may not represent the setup. Later parts spread each setup's runs across days.
- Claude Opus wrote the tests and the criteria, and a fresh Opus session scored the answers. Blinding was imperfect: review answers read like reviews, and some v2 answers mention their helpers.
- Costs use API list prices as a proxy for subscription usage.


## Part 2: how many Haiku helpers for a big review?

In v2, the biggest review was an 85-page docs check on buildbot (about 6,000 lines of docs against ~100k lines of code). There, Opus plus Haiku found over 60% more real errors than Opus alone at half the cost, and the skill picked 6 or 7 Haiku helpers by itself. So: does the number of helpers matter?

I cut the 85 pages into fixed groups of about equal size and told Opus to use exactly 1, 4, 8 or 16 Haiku helpers, one per group, then check and merge their findings. I also ran Haiku, then Opus review from Part 1 on the same task. 5 runs each, 25 runs, spread over three days (14-16 November) after the day effect in Part 1c. The [design was committed before any run](../data/tasks-v15.md), including the rule for picking Part 3's setup.

**Scoring.** Every claim from every run was checked against the code, blind, by fresh sessions, and every new real error went on the list. That list grew from 92 (v2) to 160 real errors, plus 20 planted ones. Each batch was scored on the list as it stood then, so earlier runs weren't re-checked for the errors added later.

| Mean per run | 1 Haiku helper | 4 helpers | 8 helpers | **16 helpers** | Haiku, then Opus review |
| --- | --- | --- | --- | --- | --- |
| Real errors found | 20 | 69 | 63 | **86** | 50 |
| Cost | $1.25 | $2.12 | $1.63 | **$1.69** | $3.04 |
| Split per model | Opus $0.46, Haiku $0.79 | Opus $0.94, Haiku $1.19 | Opus $1.04, Haiku $0.59 | **Opus $1.30, Haiku $0.39** | Haiku $1.72, Opus review $1.32 |
| Real errors per $ | 16 | 32 | 38 | **51** | 17 |
| False claims | 0.2 | 3.2 | 2.8 | 10.0 | 3.0 |
| Wall time | 7.1 min | 6.3 min | 4.6 min | **4.4 min** | 12.4 min |

- **More helpers found far more, for about the same money.** 16 helpers found 4 times what 1 helper found, for 35% more. They were also the quickest.
- **One helper is too few.** It has to read everything, finds a fifth of what 16 find, and still isn't cheap: almost all its Haiku cost is at the higher price Haiku charges past 100k tokens per request. The same price step is why 4 helpers cost more than 8.
- **The cost moves from Haiku to Opus as the split grows.** With 16 helpers, Opus is about three quarters of the bill, because it has 16 reports to check and merge. The helpers themselves get cheaper, since each one stays small.
- **The catch is false claims.** 16 helpers made the most (10 per run, against 3 for 4 or 8 helpers). Opus merged them without catching all of them.
- **Haiku, then Opus review was the worst value here.** It found 50 for $3.04 and varied a lot (34 to 66). One Haiku session reading 85 pages misses a lot, and a review can only check what Haiku reported.
- **Every run found all 20 planted errors** except the 1-helper runs (17 to 20). They don't separate the setups.
- **For comparison** (v2 runs, re-scored blind on the same list, labelled): Opus alone found 37 and 40 for $3.96 and $4.25, and Opus plus Haiku with the skill choosing the split found 62 and 63 for $1.85 (Opus $1.04, Haiku $0.81) and $2.01 (Opus $1.12, Haiku $0.88).

**A measurement trap, and a labelled correction.** The method scores each run's final answer. One 16-helper run ended with a short addendum about one group, after its full report in the message before, so its final answer scored 9. Re-scored blind on the full report plus the addendum, it found 88. The 16-helper row above uses the re-score; as originally scored, 16 helpers averaged 71 real errors (42 per $), still the best value. Every Part 3 answer was checked to be the whole report.

**Choosing Part 3's setup.** The committed rule picks the count with the most real errors per dollar, and the one that found more if the next is within 10%. That's 16 helpers either way (8 helpers were within 10% only before the re-score, and found fewer).

## Part 3: Opus helpers, or Haiku helpers?

Part 2 says splitting helps. But is that because the work is split, or because Haiku happens to be good enough? So Part 3 used the same 16 groups and the same wording with Opus helpers instead. 5 runs on two days (17-18 November). One run hit the subscription's usage limit after 2 minutes; it was set aside, not scored, and run again under the same rules.

| Mean per run | **16 Haiku helpers** (Part 2) | 16 Opus helpers |
| --- | --- | --- |
| Real errors found | **86** | 89 |
| Excluding borderline errors | 74 | 73 |
| False claims | 10.0 | 3.8 |
| Cost | **$1.69 (Opus $1.30, Haiku $0.39)** | $8.12 (Opus $8.12: lead $1.16, helpers $6.96) |
| Real errors per $ | **51** | 11 |
| Wall time | 4.4 min | 3.7 min |

- **Opus helpers found about the same, at nearly 5 times the cost.** 89 against 86 real errors per run, and equal once borderline errors are left out. Part 3's count also includes 12 new errors only its batch could be scored for; without them it's about 85.
- **They were cleaner.** Fewer than half the false claims. That's the one real gain.
- **The helpers are the whole bill.** The Opus lead cost about the same in both setups ($1.16 against $1.30). The difference is the helpers: $6.96 on Opus against $0.39 on Haiku.
- **Opus helpers eat into the usage limit fast.** On the first day, the third run hit the 5-hour limit 2 minutes in, after two full runs that evening.
- **Every run followed the split:** 30 of 30 runs across Parts 2 and 3 used exactly the helpers asked for, on the model asked for.

So on this big review, **splitting the work is what helps, and Haiku is good enough for each piece.** Opus helpers buy fewer false claims, not more finds.

<p align="center">
  <img src="../charts/v3-splitting.png" alt="85-page docs check on buildbot, mean per run over 5 runs. 1 Haiku helper: 20 real errors, $1.25 (Opus $0.46 + Haiku $0.79), about 7 minutes. 4 Haiku helpers: 69, $2.12 (Opus $0.94 + Haiku $1.19), about 6 minutes. 8 Haiku helpers: 63, $1.63 (Opus $1.04 + Haiku $0.59), about 5 minutes. 16 Haiku helpers: 86, $1.69 (Opus $1.30 + Haiku $0.39), about 4 minutes. 16 Opus helpers: 89, $8.12 (lead $1.16 + helpers $6.96), about 4 minutes. Haiku, then Opus review: 50, $3.04 (Haiku $1.72 + Opus $1.32), about 12 minutes. For comparison, v2 runs re-scored on the same list: Opus alone 37 and 40 for $4.11, Opus plus Haiku 62 and 63 for $1.93 (Opus $1.08 + Haiku $0.85)" width="800">
</p>


## Why does Opus alone miss so much on big reviews?

Opus alone found 37-40 real errors on this check, against 86 for Opus with 16 Haiku helpers. People on Reddit suggested two reasons: Opus skims the later pages, or it compacts its context and forgets the early ones. I checked both from the transcripts of the 8 solo Opus runs on the two biggest docs checks (this one and an 80-page one on beets).

- **It isn't coverage.** Every run put every page in front of the model, and almost every missed error was on a line the run had in its output.
- **It isn't late skimming.** Pages opened late weren't missed more often than early ones.
- **It isn't compaction.** No run compacted: context grew steadily to 233k-393k tokens, with no drop.

So it's attention per line. Opus alone saw the same lines as the split setups and missed more of them. A small fresh context per group seems to look harder. What I can't rule out is that a long context blurs attention all through a run, without any compaction.

## Limitations (Parts 2 and 3)

- One task, one codebase. The groups cut pages by size, not topic, so an error that spans two pages may fall between helpers.
- The split wording is mine. Telling Opus exactly how to split is a different setup from v2's, where the skill chose.
- The list of real errors grew batch by batch, and earlier runs weren't re-checked for errors added later. That favours later batches a little; Part 3 is the last.
- Claude Code changed version during Part 2 (2.1.317 for the first two rounds, 2.1.325 after), and Part 3 ran on 2.1.325. Haiku, then Opus review found less in its last two runs; I can't tell whether that's the version, the day or chance.
- Claude Opus verified the errors and judged the claims, and fresh Opus sessions did the blind scoring. Blinding stripped model and setup names, but answers that mention their helpers still show that some delegation happened.
- Costs use API list prices as a proxy for subscription usage.

**Takeaway: on a big review, split the work into small pieces and give them to Haiku. 16 Haiku helpers found more than twice what Opus alone found, for 40% of the cost, and Opus helpers didn't find more.**
