# `domain/` — Business Rules (the core of Clean Architecture)

The heart of FinancePilot AI. Pure Python, framework-agnostic, no imports from
FastAPI, pandas, or any AI SDK. This is where the *meaning* of reconciliation
lives:

- `entities/` — core objects such as `Transaction`, `ReconciliationRecord`,
  `Exception`, `MatchResult` — plain data + invariants, no I/O.
- `value_objects/` — small immutable types such as `Money`, `MatchStatus`,
  `TransactionSource` (bank / gateway / settlement / invoice).

Matching rules, duplicate-detection rules, and exception classification logic
will be expressed here as plain functions/classes so they can be unit-tested
without spinning up a server or touching a real file.
