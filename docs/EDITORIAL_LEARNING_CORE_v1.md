# EDITORIAL_LEARNING_CORE_v1 — Candidate

This is a dependency-free, fail-closed executable **social-editorial** contract.
It does not research external evidence, prove claims, verify rights, render media or publish.
Source URLs, verification flags and approval must come from separately audited workflows.

## Components
- `evaluate_candidate`: claim ledger, provenance assertions, visual mapping, hook, promise, retention hypothesis, and isolated channel rules.
- `build_handoff`: immutable content snapshot and SHA-256 for `SOCIAL_MEDIA_BRIEF_v1`; rejects blocked content.
- `validate_final_package`: checks AV-reported QA and explicit social publication approval; **does not publish**.
- `record_learning`: tutorials/cases always enter as `CANDIDATE`. Independent regression and review are required for canon promotion.

## Ownership and integration
Social: editorial truth, creative strategy, source/rights review, platform preview and final approval.
Audiovisual: editing, source binding in scenes, audio, render, observed semantic QA and post-render evidence.
Learning shared: reusable mechanisms, regression fixtures, promotion workflow; no shared channel identity.
The adapter may consume structured JSON from upstream systems but must never treat self-attested `verified` flags as independent proof.

## Run tests
`python -m unittest discover -s tests -v`

## Promotion gates
`CANDIDATE → CODE_TESTED → INTEGRATION_TESTED → RUNTIME_VALIDATED → CANONICAL`.
Do not label as runtime validated without real AV round-trip, source audit and publication preview tests.

## Hardening v1.1 (2026-10-13)
- Final-candidate publication gate now accepts `expected_brief_sha256` from the trusted originating handoff. Absent or mismatched hash is BLOCKED.
- Each `verified` claim requires `verification_record` with `reviewer`, `evidence_id`, and `reviewed_at`. This is auditable traceability, **not** independent truth verification.
- Never derive the expected hash from the untrusted AV return package itself.
- QA statuses remain declarations pending validation from upstream auditable services; production integration has not been established.
