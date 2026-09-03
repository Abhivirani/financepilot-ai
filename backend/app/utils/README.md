# `utils/` — Shared Helpers

Small, generic, stateless helper functions used across layers (e.g. date
normalization, currency formatting, ID generation). If a helper starts
encoding business rules, it belongs in `domain/` instead — this folder is for
plumbing only.
