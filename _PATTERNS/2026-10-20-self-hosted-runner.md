# Self-hosted GitHub Actions runner (arcs-mac)

Backlog row `ci-self-hosted-runner`. Repo is private (required: never use a self-hosted runner on a public repo).

- Location: `~/actions-runner/arcs-v9` (v2.338.0, osx-arm64, SHA-256 verified). Labels: self-hosted, macOS, ARM64, arcs-mac.
- Runs as Zach's user via launchd (`~/Library/LaunchAgents/actions.runner.flashesofbrilliance-arcs-v9.arcs-mac.plist`).
- A `package.json` containing `{"type":"commonjs"}` sits in the runner folder because `~/package.json` is `"type":"module"`, which crashes `bin/RunnerService.js`. Do not delete it.
- Scheduled workflows run only while the Mac is awake and logged in.
- `services:` containers are Linux-runner only, so ci.yml and preview-db-migrate.yml start Postgres with `docker run` (fixed names `arcs-ci-pg-ci`, `arcs-ci-pg-migrate`, ports 55432/55433, removed at the start of the next run). Needs Docker/OrbStack running.
- `playwright install --with-deps` is Linux-only; dropped `--with-deps`.

## Commands (run in `~/actions-runner/arcs-v9`)
- Status: `./svc.sh status`; start: `./svc.sh start`; stop: `./svc.sh stop`
- Remove: `./svc.sh stop && ./svc.sh uninstall`, then `./config.sh remove --token "$(gh api -X POST repos/flashesofbrilliance/arcs-v9/actions/runners/remove-token --jq .token)"`
- Never print or store registration tokens.
