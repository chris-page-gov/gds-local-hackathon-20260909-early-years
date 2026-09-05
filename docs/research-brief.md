# Research and architecture brief

**Prepared for Chris — 5 September 2026.** Source identifiers refer to [the source register](sources.md). This brief separates inspected repository facts, primary-source research, design recommendations and actual execution evidence.

## Decision

Retain **OKF+** as a working name for an additive, standards-based application profile over OKF 0.2. Its distinctive contribution should be **inspectable, evidence-bearing relationship assertions**, not YAML syntax by itself and not a new universal ontology.

The repository already implements much of this direction. At commit `c8af0b05cab49a5341e0b787e17d49a674868d3a`, the authoring contract distinguishes permissive OKF core from Bundle Wiki semantics; maintains entity, predicate and assertion identities separately from browser routes; projects one authored semantic source into JSON-LD and Explorer rows; and preserves authority and provenance [R05–R07]. The current Foundry already separates research from construction using a hash-locked domain profile, consumer lock and two-stage fixture [R02–R04]. These are assets to reuse, not rediscover.

## What Astra changes

OpenAI presents Astra as an end-to-end coding/research/computer-use model and describes Codex's experimental notes-and-history-search context management [O01, O04]. Its guide specifically identifies more clarification, stronger sensitivity to skills and AGENTS files, less spontaneous delegation, and potentially over-broad testing [O03]. Consequently, the supplied execution prompts name the outcome, local authority, owner-only stops, worker limits and test budget. These are evidence-informed adaptations, not benchmark-proven optimisations.

The API identifier is `gpt-6-astra`; the model reference lists low/medium/high/xhigh/max reasoning, 1,050,000 context tokens and 128,000 maximum output tokens. Standard pricing is $10 input/$1 cached input/$50 output per million; exceeding 272K input changes full-request rates [O02]. These are API prices, not ChatGPT subscription tariffs. No API calls were made in preparing this kit.

Use the actual Codex model selector or recorded runtime model, not a conversational assistant's self-description. OpenAI's access material distinguishes ChatGPT conversational models from Work/Codex availability; Enterprise guidance lists Codex CLI 0.153.0 as a minimum for Astra [O05–O07]. Workspace policy and rollout remain the final availability check.

**Proposed starting configuration:** explicit Astra selection, medium effort for the first authoring pilot, and escalation only for a failed semantic task or difficult standards adjudication. This is a testable starting hypothesis, not OpenAI's prescribed optimum. For a migration, compare against the previous effective effort rather than silently changing two variables.

A new API harness is unnecessary for Wednesday. Astra's asynchronous tool calls and steering are application features, not things a Markdown prompt can independently enable. Tool-calling migration uses the Responses API and must omit unsupported sampling parameters [O03]. Prefer the supported Codex host. Try experimental context management separately before Tuesday's freeze; retain durable repository artefacts even when it works [O04].

Stronger model capability does not remove the need to inspect tool receipts. The safety overview and relevant system-card sections distinguish improved behaviour from monitoring limitations and residual failures [O08–O10]. The kit checks actual output files and records unrun work instead of treating a model's assurance as evidence.

## The semantic recasting that matters

### Syntax, meaning, evidence and execution are different layers

YAML-LD supplies a YAML representation compatible with JSON-LD's data model; the dated 26 August 2026 document is a Working Draft, not a Recommendation [S02]. An `@context` supplies term mappings. The ontology or application profile determines meaning. Source evidence supports assertions. Validation checks a defined contract. Neither metadata nor a protocol grants operational permission.

The authoring strategy is therefore: human-readable OKF notes; a small pinned context; task-justified predicates; explicit assertion evidence; deterministic delivery projections; and an independent enforcement boundary for anything operational. Keep ordinary Markdown navigation links distinct from domain claims [R03, R05, S01].

### A pending annotation does not neutralise an asserted triple

The existing rich pattern emits a direct triple plus an evidence-bearing reification [R05, R06]. RDF's reification vocabulary describes a statement without entailing it; a separately emitted direct triple is still present as an assertion [S04]. Thus a `review_status: pending` annotation beside `recordA owl:sameAs recordB` does not make ordinary RDF consumers treat that identity as merely a suggestion.

This is a design hazard to test, not a claim of a demonstrated production defect in Explorer. The rehearsal represents a **CandidateRecordLink entity** with source and target endpoints and a review state. It emits facts about the proposal's existence, not identity equivalence. All current candidate links are authored fixture inputs, not outputs of a matcher. There is no confidence score masquerading as a calibrated probability.

The same discipline preserves proposed, completed and cancelled actions separately. Explicit no-concern, explicit no-contact, reported no-record and unknown must not collapse to one null. Two different dates remain two sourced dates; the bundle does not decide which date is true or whether the records describe one person.

### Keep domain mappings proportionate

Wednesday's supplied data shape is unknown. Consequently this kit does not invent a national early-years ontology, FHIR profiles, CBDS identifiers, statutory powers or service eligibility. It uses DCMI membership and RDF statement structure, a small local candidate/action vocabulary, and source-native facts preserved as JSON literals. The latter are losslessly retained but are **not claimed to be fully interoperable domain semantics**.

Research FHIR/DfE/Open Referral mappings only when an actual field and a competency question justify them. Record the exact source standard, version, definition, mapping strength, loss and validator. Reusing a vocabulary prefix does not establish conformance. Avoid naming every standard in the wider M365 review as a Wednesday dependency.

### Two useful additions after the rehearsal

First, make assertion identity independent of the subject-predicate-object tuple when different organisations or times can make separate claims about the same relationship. The current single-plane uniqueness rule is a local contract, not a universal RDF requirement [R05, S04]. Retain multiple claim events or separate planes rather than overwriting conflicting evidence. The fixture's tuple-derived IDs are deliberately limited to one snapshot and must not become the general identity scheme.

Second, distinguish assertion observation time, source event time, validity interval and review freshness. The fixture uses a fixed snapshot date, preserving source review dates separately. It does not implement a full temporal provenance model.

## What to borrow from claude-obsidian

The project is not only a Claude-specific note-taking trick: its README describes portable Agent Skills and a Codex installation route [R13]. The useful transferable design ideas are immutable source capture, separate source and claim ledgers, explicit contradictions, delta/no-op ingestion, one writer applying an inspected transaction, and bounded read-only workers. Its ingest skill also asks whether a new page adds durable knowledge instead of merely paraphrasing a source [R14].

Borrow these ideas into the existing Foundry workflow; do not introduce an Obsidian dependency into Explorer publication. The project is a comparator, not evidence that its entire security or transaction implementation has been independently validated here. Its own high-risk evidence policies are project rules, not universal legal requirements.

Your Team DSIT A Challenge 2 implementation already provides the earlier source-backed wiki, non-AI inspection workbench and explicit evaluation lineage [R15]. Preserve that collaborative attribution. The user identifies Karpathy's LLM-Wiki as the conceptual origin; this preparation does not assert a newly verified release date or direct dependency on a specific Karpathy source revision.

## Research-to-build workflow

Use one bounded research contract, not several long reports handed to Codex without a stable interface. The two included research prompts answer separate questions: (A) which semantic contract is justified; (B) what the actual event data and rights permit. Their output is a small evidence and decision pack. For production, compile that pack into the real upstream `okf-domain-profile.v1` and run its validator; the rehearsal manifest does not impersonate it.

Keep no more than three workstreams: one writer, one semantic researcher and one independent reviewer. The researcher returns mapping decisions; the reviewer returns counterexamples and evidence, not broad rewrites. Human approval concerns substantive scope, authority and publication, not every local file save.

Do a tiny positive/negative fixture first, then the actual locked consumer. Only then scale. Test one frozen candidate and promote identical bytes if publication is later authorised [R02–R04]. No public URL or release claim is justified by an HTTP status probe, a similar schema or the fallback preview.

## What was actually produced and tested

The delivered fixture comprises 22 concepts, eleven fictional source records in three heterogeneous data families, three candidate proposals and 23 directed relationships. The independent compiler preserves exact source hashes and locators, checks source-fact equality, and projects Markdown into runtime JSON, JSON-LD, YAML-LD and 721 RDF triples. The plain-OKF control has identical facts and Markdown bodies. This is suitable for a controlled comparison, not proof of better model answers.

Thirty-six local tests passed. Sixteen Chromium DOM/interaction checks passed, including search, filters, source text rendering, candidate visibility and a mobile overflow check. These are not full accessibility certification or upstream Explorer acceptance. File and loopback navigation were blocked by the browser policy, so the recorded browser run renders the exact generated HTML in a blank document and does not claim a successful deployed URL journey.

Astra answer quality and authoring efficiency remain unmeasured. The actual pinned Svelte Explorer, complete upstream validators, SHACL and FHIR/CBDS validation remain unrun. Container DNS prevented fetching an executable upstream checkout. These limitations are explicit integration gates, not reasons to discard the working local fixture.
