# How to use the model-router skill

## Install (once)

```bash
ln -s ~/Documents/Coding/claude-model-router/skills/model-router ~/.claude/skills/model-router
```

Change the first path to wherever you cloned this repo. The skill itself is the `skills/model-router/` folder: `SKILL.md` (the rules) and `plan-guide.md` (how it writes coding plans).

## What it does

Start your prompt with `Use the model-router skill.` and describe the task. Opus picks one of three modes and tells you which:

- **Mode 1, Opus alone:** small jobs. It just does it.
- **Mode 2, Opus with Haiku helpers:** big reading or review jobs. It just does it.
- **Mode 3, Haiku does the work, then Opus reviews it:** most coding tasks. This is the cheap one, and the only one where you may have to do something.

## Two ways to run it: Manual or API key

Modes 1 and 2 work the same either way. The difference is only in mode 3, where a separate Haiku session has to be started:

- **Manual:** runs on your subscription (Pro, Max). You start Haiku yourself, in a second terminal, with one command. Works in a terminal and in the desktop app.
- **API key:** one terminal only. Opus starts Haiku by itself. Everything (Opus and Haiku) bills your API key. Runs in a terminal only (a Terminal tab in the desktop app counts); the desktop app's chat ignores API keys.

Manual is the default. API key is off until you turn it on.

### Manual (subscription)

1. Start `claude` as usual and give it the task (`Use the model-router skill. ...`).
2. If it picks mode 3, it shows a command. Open a second terminal (in the desktop app, a new Terminal tab) and run:

   ```bash
   bash ~/.claude/model-router/next.sh
   ```

3. Haiku does the work there. Say yes when it asks to write `haiku-answer.md`. Type `/exit` when it's done.
4. Go back to the first session and wait. Opus notices Haiku is done and reviews its work by itself (it waits up to 60 minutes).
5. Commit. Before each mode 3 task the skill asks for a clean project (everything committed), so the review sees only Haiku's changes.

Using a Haiku chat in the desktop app instead of a terminal? Type `/clear` first if the chat isn't new, then paste the prompt the skill prints.

### API key

1. **Once:** put your key in a file. Copy the repo's example and fill in your key by hand:

   ```bash
   cd ~/Documents/Coding/claude-model-router && cp .env.example .env && chmod 600 .env
   ```

   `.env` is gitignored. Don't add other variables to it: the load command below sets everything in the file. Never load it from your shell startup files (`~/.bashrc` and so on), or every terminal would bill the key. VS Code's Python extension can load `.env` into its terminals by itself: turn off its `python.terminal.useEnvFile` setting.
2. **Once:** turn on API mode for every mode 3 task:

   ```bash
   echo api > ~/.claude/model-router/mode3
   ```

   Run it once, ever: it's a file on your disk, so it stays across sessions, terminals and reboots until you delete it (`rm ~/.claude/model-router/mode3`). The skill still picks the mode by itself; whenever it picks mode 3, it starts Haiku itself instead of asking you to. While the file is set:
   - **Session started with the key, and you said yes:** mode 3 runs Haiku by itself.
   - **Session with no key** (a normal terminal, the desktop app): the skill sees no key and uses manual. No harm.
   - **Session with the key loaded, but you said no:** Haiku would bill the key while Opus bills your subscription. Avoid this.

   To try it on a single task instead, skip this step and add `haiku api` to that prompt. That also forces mode 3.
3. **Each time:** in a new terminal (a Terminal tab in the desktop app works too), load the key into that terminal only, then start `claude`:

   ```bash
   set -a; source ~/Documents/Coding/claude-model-router/.env; set +a
   claude
   ```

   (Change the path to where you cloned the repo.) When `claude` asks whether to use the API key, say **yes**. The banner should say "API Usage Billing".
4. Give it the task as usual (`Use the model-router skill. ...`). If it picks mode 3, wait. Opus starts Haiku in the background (capped at $0.50 and 60 minutes), then reviews its work when it's done. Nothing to do in between. If Haiku fails (no credit, the cap, a crash), Opus stops and tells you; it doesn't redo the work itself.
5. Commit, then close the terminal so the key goes with it.

Tested once on a small task: $0.56 (Opus $0.54, Haiku $0.03). Opus is most of the bill.

**Two things to watch with a key:**

- **Don't use API mode in a session where you said no to the key.** Haiku would bill the key while Opus bills your subscription, and the skill can't tell. With the `mode3` file set to `api`, that means: in a terminal with the key loaded, always say yes.
- **Your yes or no only covers that one session.** `claude -p` (the headless mode scripts use) never asks: if the key is set in that terminal, it always uses it. So close the terminal when you're done. To check any terminal (prints yes or no, never the key):

  ```bash
  [ -n "${ANTHROPIC_API_KEY+x}" ] && echo "KEY IS SET in this terminal" || echo "no key here"
  ```

## Handy phrases

- `no routing`: Opus does it all itself.
- `haiku only`: force mode 3.
- `haiku api` / `haiku manual`: force mode 3 and run it the API key way or the manual way, for this task only.
- `do it here` (after a mode 3 answer): run it in the same session with Haiku helpers instead.
- `Write a coding plan for ...`: a plan in Haiku-sized chunks, saved as `PLAN.md`. Then `Do chunk 1 of PLAN.md`.

## Good to know

- If the review doesn't start by itself, paste the `Follow .../review-prompt.md` line the skill gave you.
- Inside a session, `/status` shows which login it's using.
- Every decision is logged in `~/.claude/model-router/routing.log`.
