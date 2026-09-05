# Astra evaluation prompt — test the representation, not the branding

Compare the plain-OKF control and the typed OKF+ bundle using the same source snapshot, questions, selected model, reasoning level, retrieval budget and output contract. The control must retain the same facts, relationship sentences and evidence in prose. Otherwise the experiment confounds information content with representation.

Follow evaluation/protocol.md. Begin with the four-question pilot only after its usage budget is approved. Run each condition in an isolated context restricted to that condition's files. Do not expose evaluator-only answers, the other condition, builder discussions or previous answers to the answering model. Alternate condition order and record every failed or timed-out attempt.

For each question return only: answer, evidence locators, relevant relationship identifiers when available, unresolved ambiguity, and abstention/review reason. Do not infer a missing identity or outcome merely to complete an answer.

Score source support, exact locator correctness, relationship direction, candidate-versus-identity, action status, missingness, contradictions, abstention and time/cost. Use deterministic matching for identifiers and a blinded reviewer for entailment. A small exploratory result is not a national performance, fairness or safety guarantee.

Distinguish two experiments: authoring quality (old versus revised prompt on the same frozen inputs) and answering quality (plain versus typed representation). Do not attribute an improvement to Astra when the model, prompt, data and retriever all changed at once.

Publish a result only when real runs exist. Otherwise deliver the questions, harness contract and honest `not_run` status. Finish with a two-minute demo of the strongest observed benefit and one explicit failure/uncertainty case. A null result is a valid outcome: retain simpler plain OKF where the extra semantics do not justify their cost.
