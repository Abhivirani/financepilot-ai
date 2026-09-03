# `tests/`

- `unit/` — fast, isolated tests for `domain/` and `services/` logic (no
  network, no disk I/O, no AI calls — mock the infrastructure layer).
- `integration/` — tests that exercise the API endpoints end-to-end,
  including file upload and parsing.

No tests have been written yet since no application logic exists yet.
