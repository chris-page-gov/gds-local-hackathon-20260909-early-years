---
'@context': https://example.invalid/okf-plus/rehearsal/profile/context.jsonld
'@id': https://example.invalid/okf-plus/rehearsal/id/source/referral
'@type': ey:SourceCollection
type: Source collection
route: source/referral
title: Referral synthetic extract
description: A supplied fictional extract, not an official service or national schema.
tags:
- synthetic
- early-years
- rehearsal
generated:
  by: process:rehearsal-authoring-v0.1
  at: '2026-09-05T00:00:00Z'
sources:
- url: https://example.invalid/okf-plus/rehearsal/sources/referrals.csv
  source_artifact: sources/referrals.csv
  source_sha256: e2130273a639b41320fc7c24b220c373e59f0bfac6f7a369f6b87dd60f8a30d9
  locator: file
  retrieved_at: '2026-09-05T00:00:00Z'
  url_status: synthetic-identifier-not-dereferenced
facts:
  source_file: sources/referrals.csv
  scope: synthetic-fixture
fixture_scope: synthetic-fixture
status: experimental
assertions: []
---

# Referral synthetic extract

**Synthetic rehearsal only — not an official record or decision.**

A supplied fictional extract, not an official service or national schema.

## Source facts

```json
{
  "scope": "synthetic-fixture",
  "source_file": "sources/referrals.csv"
}
```

## Relationships

No directed relationship is asserted by this page. Incoming relationships may still exist.

## Evidence

Source file: `sources/referrals.csv`. Locator: `file`. SHA-256: `e2130273a639b41320fc7c24b220c373e59f0bfac6f7a369f6b87dd60f8a30d9`. The example.invalid URL is a synthetic identifier, not a retrieved website.

