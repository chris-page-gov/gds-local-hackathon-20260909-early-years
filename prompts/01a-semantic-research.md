# Deep Research prompt A — settle the OKF+ semantic contract

## Purpose and sources

Research the minimum semantic extension needed for an inspectable early-years rehearsal. Start with the actual `chris-page-gov/okf-explorer` checkout and its Foundry prompt kit, semantic-authoring guide, assertion schemas and beginner material. The inspected preparation baseline is commit `c8af0b05cab49a5341e0b787e17d49a674868d3a`; record a newer revision explicitly rather than mixing versions silently.

Use official upstream OKF, W3C YAML-LD/JSON-LD/RDF/PROV documents and authoritative domain documentation only where a concrete source field or competency question requires it. Use the supplied M365 review only as a hypothesis register. It is not the original Discovery report or approval of its thresholds.

Time budget: 45 minutes of focused research. Start with the supplied source register; inspect at most 12 additional primary documents unless a named blocking uncertainty requires more. Record unavailable sources rather than inventing their content. Do not perform API spending or modify/publish the repository.

## Questions to resolve

A. What capability is already present in OKF core and the Explorer semantic profile, and what is genuinely missing for this use case?
B. Does a direct triple plus an assertion annotation correctly express a candidate, dispute, conditional statement or time-bounded claim to ordinary RDF consumers? Compare a candidate-link entity, assertion-only proposal store, and separate accepted/candidate graph planes. Do not assume named graphs alone enforce trust.
C. Which identifiers belong to source records, people, organisations, proposals and assertion events? Can repeated or conflicting claims about one triple be retained without overwriting evidence?
D. Which minimum relationships answer the selected competency questions? Separate document navigation from domain predicates; labels from IRIs; synthetic scope from authority; confidence from verification; event, observation, validity and review times.
E. Is YAML-LD in front matter justified compared with plain OKF plus a generated JSON-LD sidecar? Compare authoring burden, meaningful diffs, evidence locality, consumer support and reproducibility. Both must compile from one source of truth.
F. Which existing standards are normative, projections, source-native, conditional, reference-only or not applicable? Do not manufacture FHIR or CBDS RDF terms from a familiar label. A local term may be justified when explicitly defined and not falsely equated with an external standard.

## Required deliverable

Produce a compact research pack, not a general early-years report: `decision-brief.md` (maximum 1,500 words), `source-register.json`, `term-decisions.json`, `competency-questions.json`, `counterexamples.json`, and `open-decisions.json`.

Every proposed term must state its IRI or explicitly local namespace, definition, subject/object kinds, source/version, exact/close/broad/narrow/unmapped status where relevant, information loss and the question it helps answer. Every decision must distinguish inspected fact, standards interpretation, proposal and unresolved assumption.

Include runnable or unambiguous test fixtures for candidate-not-identity, proposed-not-completed, no-record-not-no-contact, conflicting evidence, repeated assertion events, unknown context terms and stale context bytes.

Stop broadening when the chosen demonstration has a justified term set, supported source mappings, named remaining uncertainties and falsifiable tests. Return negative findings when the simpler plain-OKF representation is sufficient. Do not invent evidence in order to favour OKF+.

## Handoff boundary

This output is a draft input to the real Foundry domain-profile compiler. Do not label it `okf-domain-profile.v1` approved/conformant until the actual schema, consumer lock and approval requirements have been satisfied. A separate local rehearsal contract may be used for synthetic, non-release work, with its limitations explicit.
