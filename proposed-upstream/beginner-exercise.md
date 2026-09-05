# Proposed beginner exercise — a link is not an identity claim

Status: draft learning exercise for the existing OKF Explorer beginner path. Not merged or approved as a canonical profile.

## What you will learn

Distinguish a readable page, a navigation link, a typed relationship and evidence for that relationship. You need no ontology expertise to begin.

## Read the example first

Open the synthetic H-01 record. There are two candidate links, C-01 and C-02. A candidate is a proposal to review; it is not a confirmed child identity. Open each candidate and inspect its source record, target record and interpretation rule.

Open A-01 and A-02. The first is proposed. The second records a completed leaflet dispatch. Neither permits a wider claim that a child received effective support.

Open H-03, H-04 and E-04. An explicit record of no concern is different from no contact and from no record. An empty field cannot settle all three questions.

## Inspect the Markdown

Read `bundle/concepts/candidate/c-01.md`. The ordinary `type` is an OKF display/category field. The `@type` is a semantic class. The `@id` identifies the proposal; `route` supports local navigation. These fields have different purposes.

The direct relationships point from the candidate proposal to its source and target records. Each has an evidence-bearing assertion. There is deliberately no `owl:sameAs` statement.

Source hashes and locators are produced from actual local fixture files, not invented by a prompt. Example web identifiers are not live authoritative URLs.

## Build and break a copy

Run the local check and tests. In a disposable copy, change a proposed-action relationship into a completed-action relationship without changing the cited source. Validation must fail. Restore the copy and run the tests again. Do not alter the original fixture or its recorded receipts.

## Ask the AI

Use the same source facts in two separate sessions. In one, provide plain OKF; in the other, provide typed OKF+. Ask whether H-01 and E-01 are confirmed to be the same child, whether A-01 was completed, and what H-04 establishes. Demand precise evidence and an explicit unknown where appropriate.

The two sessions must not see the answer key or each other's answers. Record the actual model and settings. A fluent response is not proof: inspect its source support and any unwarranted conclusions.

## Success

You can explain what the relationship asserts, who or what supplied it, where the evidence is, and what it does not establish. You can read the knowledge without AI and validate the machine-readable projection. You do not need to add more semantic machinery unless it improves a real task.
