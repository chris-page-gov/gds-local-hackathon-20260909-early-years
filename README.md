# Early-years OKF rehearsal

A synthetic preparation kit for the Early Years Hackathon on **9 September 2026**.
Explore **22 concepts and 23 directed relationships** using the actual
[OKF Explorer](https://github.com/chris-page-gov/okf-explorer).

The fixture demonstrates competing candidate links, interpretation rules and
proposed, completed and cancelled actions. A candidate is not an identity match;
a proposed referral is not completed support. All eleven source records are
fictional. This is an experimental teaching and evaluation fixture, not a service
for handling real children's records.

## Start here

- [Run the actual Svelte Explorer locally](docs/local-integration-run.md).
- [Research and architecture brief](docs/research-brief.md) and [hackathon runbook](docs/wednesday-runbook.md).
- [Integration contract](docs/upstream-integration.md) and [preflight prompt](prompts/00-preflight.md).
- [Public evidence and remaining boundaries](evidence/acceptance.json).

`preview/index.html` is a self-contained independent inspection aid. It is useful
for reading the fixture offline; its tests do not establish Explorer acceptance.

## Contents

| Path | Purpose |
|---|---|
| `bundle/` | Authored concepts and generated JSON, JSON-LD, YAML-LD and RDF projections |
| `baseline/` | Control with identical source facts and prose, without structured relationships |
| `sources/` | Immutable fictional records, candidate ledger and fixture policy |
| `profile/` | Experimental context, schema, predicates and scope contract |
| `evaluation/` | Twenty questions, reference answers and A/B protocol |
| `tools/`, `tests/` | Deterministic compiler, checks and portable browser acceptance |
| `docs/`, `prompts/` | Research, provenance and practical instructions |

## Reproduce the fixture

Use [uv](https://docs.astral.sh/uv/getting-started/installation/) **0.12.2**.
The project selects Python **3.12.11** from `.python-version`; `uv` can install it
if needed. `pyproject.toml` declares the dependencies and `uv.lock` fixes their
transitive versions and distribution hashes. These commands apply to this kit;
Explorer retains its own locked Python and Node toolchains.

Run commands from the repository root. No virtual environment activation is
needed; `uv` maintains the ignored `.venv/` directory.

```sh
uv sync --locked
uv run --locked python tools/build.py --check
uv run --locked python -m unittest discover -s tests -v
uv run --locked python tools/build_preview.py
```

Optional preview browser smoke test, using genuine loopback navigation:

```sh
uv sync --locked --group browser
uv run --locked --group browser python -m playwright install chromium
uv run --locked --group browser python tests/browser_check.py
```

The optional `browser` dependency group is locked alongside the compiler
libraries. Browser binaries are installed separately. In CI, every Python command
uses `uv run --locked`; a stale lock fails rather than resolving new versions.
See the [uv migration receipt](evidence/uv-migration.json) for executed checks.

Raw local logs, screenshots, host settings and caches are ignored by Git. CI
retains execution artefacts separately. The public source is selected by an
explicit allowlist and checked by `uv run --locked python tools/check_public_package.py`.

## Demonstration

Open `record/h-01` and compare its two competing candidates. Inspect
`candidate/c-01` for source, target and interpretation rule. Compare proposed
A-01, completed leaflet dispatch A-02 and cancelled A-03. H-03, H-04 and E-04
illustrate distinct meanings of no concern, no contact and no record.

## Reuse and limits

Code is MIT; authored content is CC-BY-NC-4.0. See [licences](LICENSE.md),
[terms](TERMS.md) and [publication scope](docs/publication.md).
The historical profile is an independent OKF 0.2 structural subset. It does not
claim the complete Bundle Wiki profile, FHIR, CBDS, SHACL or production readiness.
No paid model experiments have been run. Published reference answers cannot be
claimed as a secret held-out evaluation set.
