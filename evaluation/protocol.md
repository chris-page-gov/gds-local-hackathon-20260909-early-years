# Evaluation protocol — not-run model experiments

## Separate three questions

**Compiler conformance:** did the local producer preserve the declared inputs and relationships? This has executable results in receipts.

**Authoring:** does the revised prompt produce better bundles than the existing prompt, holding input, model, effort, tools, budget and grading fixed? Not run. Compare validity, supported relation coverage, unsupported assertions, correction effort and elapsed cost. Then compare models separately if useful.

**Answering:** does typed representation improve answers compared with plain OKF containing the same facts? Not run. The delivered control contains the identical source facts and Markdown bodies, so the experiment does not reward extra information. The typed condition adds a deterministic relationship projection and its structured qualifiers.

## Pilot

Use Q01–Q04, two conditions and two fresh-context repeats: 16 answer attempts. This is a proposed budget unit, not permission to spend API credits. Both conditions use the same model/effort and maximum evidence/tool budget. Alternate condition order and preserve every outcome, including abstention, tool failure and timeout. Separate authoring runs from answering runs.

Create an isolated answering workspace for each condition containing only its bundle, permitted source evidence and the questions. Do not merely tell an agent not to inspect gold while leaving evaluator-only files in its working scope. Keep `EVALUATOR-ONLY-gold.json`, other-condition files, prior answers and reviewer discussions outside that workspace. For a stronger trial, have a human create an independent holdout not seen during prompt development.

## Output and scoring

For each question, retain answer text, exact evidence locators, relation identifiers where used, unresolved ambiguity, abstention reason, wall time, tools, input/output tokens when available and measured cost when available. Record runtime model evidence; use unknown rather than guessing hidden model versions.

Score each attempt 0–2 for substantive correctness and 0–2 for evidence/locator support. Additionally record binary flags for invented identity, upgraded action state, collapsed missingness, suppressed contradiction and fabricated authority. Human review of entailment should be blind to condition where practicable. Do not replace evidence quality with a single model-confidence score.

The prototype target is **zero observed** unsupported identity/action/authority upgrades in the selected attempts, not a claim that the population error rate is zero. With a small synthetic pilot, report counts and concrete examples rather than a statistically established superiority or fairness claim. A statistically useful comparison needs a larger independently sampled benchmark and uncertainty estimates.

The full rehearsal has 20 questions. Three repeats across two conditions would be 120 answer attempts; authorise that budget separately. Stop expansion when the pilot exposes a contract error that should be fixed first.

## Reproducibility manifest

Record model selection evidence; effort; host/version; prompts and hashes; source/profile/consumer hashes; condition; question set; attempt order; retriever/tool budget; context isolation; timestamps; outcome and token/cost availability. SHA-256 of the data does not freeze a mutable model alias. Report that limitation.

## Result state

No Astra model benchmark or old/new prompt trial was executed in this preparation. Do not infer model improvement from the deterministic compiler's passing tests. `model-results.json` explicitly records the unrun state.
