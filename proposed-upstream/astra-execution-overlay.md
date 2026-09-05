# Proposed GPT-6 Astra execution overlay

Status: evidence-informed proposal, 5 September 2026. Not merged into OKF Explorer and not empirically benchmarked. Use alongside the existing Foundry warm-up/build prompts, not as a replacement for their approved contracts.

The [5 September local integration run](../docs/local-integration-run.md) records `gpt-6-astra` with `ultra` reasoning from the actual Codex task. It demonstrates repository work and deterministic consumer validation, not comparative evidence that this overlay improves model outcomes. The generic upstream Foundry prompts and release gates remain unchanged.

## Runtime inputs

Record the effective model, reasoning level, Codex/client version, source/profile/consumer locks, instruction files, execution budget and exact permitted actions. Verify Astra availability in the actual host. Do not assume conversational GPT-6 Pro establishes Astra execution.

## Add this to the run contract

> Complete the selected outcome within its authorised boundary. Carry out reversible local research, implementation and validation without asking again for permission already given. Ask only when the unresolved answer changes the intended outcome, data-processing authority, paid spending, destructive action or external publication. Continue independent permitted work while a genuine decision remains pending.
>
> Audit the actual AGENTS/skill instructions before work. Resolve conflicts according to the real instruction hierarchy; do not let an optional helper silently replace the outcome or escalate the authority granted to this run. Name the exact governing rule when it causes a stop.
>
> Use one integrating writer and at most two bounded read-only workers. Delegate only separable research or review with named outputs. Do not start an expanding agent tree. Independent review must use source evidence and the frozen candidate, not just another model's conclusion.
>
> Use deterministic code for parsing, transformation, hashing, validation and publishing checks. Run the tests affected by each edit and one final selected suite on the frozen candidate. Do not repeat large operations without a changed input or diagnosed condition. Record failures and unrun gates rather than claiming completion.
>
> Preserve progress in the repository: source register, decision log, contract, tests, receipts and next action. Experimental host context management may supplement these files; it does not replace them or grant new tool access.
>
> Finish with artefact paths, exact executed checks, limitations and any remaining owner decision. Distinguish reviewed evidence, local prototype conformance, actual-consumer acceptance and publication. Never relabel one as another.

## Assessment plan

Compare the existing and overlaid authoring prompt with identical source snapshot, model, effort, tooling and acceptance tests. Assess validity, supported relationship coverage, unsupported claims, correction effort and cost. Keep representation A/B tests separate. Promote the overlay only after observed results justify it.

Sources: OpenAI Astra model guidance, model reference, Codex configuration reference and access documentation; see O01–O07 in the preparation source register. This overlay does not prescribe a universally optimal reasoning level.
