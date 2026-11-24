# Early-years OKF rehearsal

A synthetic preparation kit for the Early Years Hackathon on **9 September 2026**.
Explore **22 concepts and 23 directed relationships** using the actual
[OKF Explorer](https://github.com/chris-page-gov/okf-explorer).

The fixture demonstrates competing candidate links, interpretation rules and
proposed, completed and cancelled actions. A candidate is not an identity match;
a proposed referral is not completed support. All eleven source records are
fictional. This is an experimental teaching and evaluation fixture, not a service
for handling real children's records.

For current and historical specifications, separately versioned profiles and
public bundle discovery, see the [central OKF standards register](https://github.com/chris-page-gov/okf-explorer/blob/main/docs/okf-standards.md)
and its [machine-readable register](https://raw.githubusercontent.com/chris-page-gov/okf-explorer/main/registry/okf-standards.json).
The current bundle implements **OKF 0.3**, published on **18 November 2026**,
with this producer implementation dated **24 November 2026**. Its independent
[early-years profile overlay](profile/v0.2.json) preserves the original domain
constraints. It does not claim the complete Bundle Wiki profile. The historical
comparison control retains its original OKF 0.2 declaration and every byte.

## Three bundle walkthroughs

The [authored walkthrough cases](walkthrough/cases.json) define a separate
complex question, qualified answer, source trail and negative controls for each
logical bundle. The static publication generates responsive diagrams and links
to the exact Explorer record and AI-readable evidence:

| Scope | Question | Published descriptor path |
|---|---|---|
| Current reference graph | Can linked records establish that support was delivered? | `bundle/core-reference.json` |
| Current typed domain graph | How should competing candidate links and different action states be read? | `bundle/okf-bundle.json` |
| Historical comparison control | What can the same facts show without structured domain relationships? | `baseline/control-explorer.json` |

The control's Reader transport adds identity metadata around its unchanged
original fields. Its original descriptor remains `baseline/okf-bundle.json`.
Zero structured relationships in this control does not mean that its prose
describes no relationships. The current core graph contains 23 Markdown
references; those references have a different meaning from the 23 domain
assertions, even where their endpoints coincide.

Read the [migration and acceptance guide](docs/okf-0.3-migration.md),
[semantic contract](okf.semantic.json) and [publication contract](okf.publication.json).
Each release must carry exact source, consumer and asset evidence; a local
fixture check alone does not establish publication acceptance.

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
| `baseline/` | Frozen historical control with identical source facts and prose, without structured domain relationships |
| `sources/` | Immutable fictional records, candidate ledger and fixture policy |
| `profile/` | Experimental context, schema, predicates and scope contract |
| `evaluation/` | Twenty questions, reference answers and A/B protocol |
| `tools/`, `tests/` | Deterministic compiler, checks and portable browser acceptance |
| `docs/`, `prompts/` | Research, provenance and practical instructions |

## Reproduce the fixture

Use [uv](https://docs.astral.sh/uv/getting-started/installation/) **0.13.4**.
The project selects Python **3.12.11** from `.python-version`; `uv` can install it
if needed. `pyproject.toml` declares the dependencies and `uv.lock` fixes their
transitive versions and distribution hashes. These commands apply to this kit;
Explorer retains its own locked Python and Node toolchains.
GitHub Actions uses Ubuntu 24.04 so `setup-python` can provision the pinned
CPython 3.12.11 toolchain; the Python, uv, browser and dependency locks are
retained. The uv certificate-store correction is recorded in the changelog.

Run commands from the repository root. No virtual environment activation is
needed; `uv` maintains the ignored `.venv/` directory.

```sh
uv sync --locked
uv run --locked python tools/build.py --check
uv run --locked python -m unittest discover -s tests -v
uv run --locked python tools/build_preview.py
uv run --locked python tools/build_publication.py
```

Optional preview browser smoke test, using genuine loopback navigation:

```sh
uv sync --locked --group browser
uv run --locked --group browser python -m playwright install chromium
uv run --locked --group browser python tests/browser_check.py
```

The optional `browser` dependency group is locked alongside the compiler
libraries. Browser binaries are installed separately. CI uses the Ubuntu runner’s
installed Google Chrome with browser sandboxing enabled; it does not download a
second browser. Every Python command uses `uv run --locked`; a stale lock fails
rather than resolving new versions.
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
The historical profile remains an independent OKF 0.2 structural subset. The
current overlay implements core 0.3 without claiming the complete Bundle Wiki
profile, FHIR, CBDS, SHACL or production readiness.
No paid model experiments have been run. Published reference answers cannot be
claimed as a secret held-out evaluation set.
