# Fixed test set

Project: a private Python CLI project of mine (~10k lines including tests), cloned fresh for every run. Module and command names in the prompts are replaced with generic descriptions.
Run A gets `no routing. ` in front of the prompt, run B gets `Use the model-router skill. `.
`scripts/run_bench.sh` reads the prompt column from this table, so prompts must not contain a pipe character.

| # | Type | Prompt | Expected route |
| --- | --- | --- | --- |
| 01 | Search | Find every place in the main package that catches a broad Exception (except Exception or bare except) and group them by file. | Haiku |
| 02 | Search | List every place the user config file is read or written, and which fields each one uses. | Haiku |
| 03 | Search + summary | Which external Python libraries and system commands does this project depend on, and where is each one used? | Haiku |
| 04 | Explain | Explain end to end what happens when the main command runs: from the CLI, through the background helper, to the changes it makes on the system. | Sonnet |
| 05 | Bug fix | Fix this bug: on a detached launch, the launcher subprocess's stderr goes to /dev/null, so when that subprocess itself fails the CLI reports a misleading cause and the real error is lost. Keep the existing warning for the case it was meant for. Run the unit tests afterwards with python3 -m unittest discover -s tests/unit -t . | Haiku search, Sonnet fix |
| 06 | Tests | Write unit tests for two system-probing functions in the diagnostics module, mocking anything that touches the system, and run them with python3 -m unittest discover -s tests/unit -t . | Sonnet |
| 07 | Small feature | Add a --dry-run flag to the CLI's remove command that prints what it would remove (config entry, autostart entry) without changing anything. Add a unit test and run python3 -m unittest discover -s tests/unit -t . | Sonnet |
| 08 | Refactor | Split the main CLI module into smaller modules without changing behaviour. Run python3 -m unittest discover -s tests/unit -t . afterwards. | Sonnet |
| 09 | Mixed | Find every hardcoded filesystem path in the main package and move them into a single paths module, without changing behaviour. Run python3 -m unittest discover -s tests/unit -t . afterwards. | Haiku search, Sonnet fix |
| 10 | Design | The app's autostart can fire before the user's desktop session is fully ready, so the launch fails. Propose a design for retrying failed launches, with trade-offs. Don't write code. | Opus (orchestrator, inline) |
