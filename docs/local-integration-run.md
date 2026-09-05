# Run the rehearsal in the actual Explorer

Use sibling checkouts named `okf-explorer` and
`gds-local-hackathon-20260909-early-years`, or pass an explicit Explorer path.
No local Codex configuration or historical receipt directory is required.

## Build the consumer

Follow Explorer's own setup instructions, using its locked dependencies:

First complete the kit’s [locked uv setup](../README.md#reproduce-the-fixture).
Each checkout manages its own environment; no activation is needed. If the sibling
Explorer checkout already exists, use it and skip the clone command.

```sh
git clone https://github.com/chris-page-gov/okf-explorer.git ../okf-explorer
cd ../okf-explorer
uv sync --locked
pnpm --dir apps/okf-explorer install --frozen-lockfile
pnpm --dir apps/okf-explorer build
cd ../gds-local-hackathon-20260909-early-years
```

The current application build is used for UI acceptance. Schema validation remains
bound to the historical inspected commit, read with `git show`; your checkout does
not need to be reset to that old commit.

```sh
uv run --locked python tools/check_explorer_integration.py --explorer ../okf-explorer
uv run --locked python tools/serve_explorer.py --build-dir ../okf-explorer/apps/okf-explorer/build
```

Open the URL printed by the server. It serves the actual Svelte build and only the
fictional bundle and corrupted test copies, bound to `127.0.0.1:4175`.
In another terminal run the browser check using Explorer's installed Playwright:

```sh
node tools/check_explorer.mjs --explorer ../okf-explorer
```

The runner uses installed Google Chrome by default. Pass `--browser chromium`
to use Playwright's Chromium. Browser installation is a separate environment step.
Tests navigate a real URL, exercise the 22-concept/23-relationship fixture and
corrupted JSON, and write results under ignored `output/explorer/`.
They do not replace Explorer's full release matrix or production semantic gates.

The original pinned-consumer acceptance and macOS IPC diagnostic receipts are
retained privately. [Public evidence](../evidence/acceptance.json) records selected
results without workstation paths or raw browser traces.
