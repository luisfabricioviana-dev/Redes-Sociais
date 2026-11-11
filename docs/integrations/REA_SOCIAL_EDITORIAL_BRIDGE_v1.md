# REA → Agente de Redes Sociais: learning admission bridge v1

**Status: candidate, not deployed.** The bridge reuses the already merged
`contracts/rea_learning_gate.py`, rather than duplicating REA governance.

The call `admit_editorial_learning(EditorialLearningRequest(...))` checks the
artifact digest, source/evidence assertions, domain isolation, forbidden action
authorization, reviewer and regression identifiers. The only positive result
is `CANDIDATE_FOR_REVIEW`; no canon promotion, runtime action or publication.

- Inputs are untrusted; `source_verified` and `evidence_reviewed` flags still
  require a separately audited evidence service to become trustworthy.
- SHA-256 provides integrity, not authenticity or scientific verification.
- `reviewer_id` and `regression_id` are trace pointers, not completion proof.
- Never pass content or identities from other channel profiles through this bridge.
- This module does not connect to the remote Agent of Learning runtime. It is
  an explicit in-repository boundary for future inter-agent transport.
- A production adapter must independently authenticate evidence records and
  run regressions before any reviewed promotion, subject to code review.

Local test: `python -m unittest discover -s tests -p 'test_rea_*py' -v`.

## Independent review gate (v1.1)

`contracts/rea_independent_review.py` adds a second, separate review-evidence
gate: the independent reviewer must differ from the originating reviewer, the
candidate digest and regression/source identifiers must match the admission
ticket, and regression status must be `PASS`. Missing witness digest or
location, cross-profile data and action authorization are rejected.

The positive state `REVIEW_EVIDENCE_COMPLETE` is **not** a promotion or a
publication grant: externally supplied reviewer IDs, witness hashes and status
claims must still be independently authenticated. No capability may be
automatically promoted or deployed by this code. The executable review
tests reside at `tests/test_rea_independent_review.py`.

## Byte-bound witness audit v1.2 (2026-11-11)

The separate `rea_review_artifacts.verify_review_artifacts` function accepts real
witness bytes and regression-report bytes. It validates SHA-256 of both payloads,
and the parsed regression record must match the candidate hash, regression ID,
independent reviewer ID, witness digest, domain SOCIAL, and status PASS. The
record must explicitly deny automatic promotion. Missing/altered bytes fail closed.

This is **structural evidence integrity**, not proof that the evidence is true,
scientifically adequate or authored by the identified reviewer. Hashes of
untrusted submissions alone cannot establish authenticity. Publication and
promotion are always disabled by this contract.

New regression fixtures: `tests/test_rea_review_artifacts.py`. A standalone
9-test local mirror of the new byte-binding logic passed on 2026-11-11; this
does not certify the entire GitHub checkout. Remote Actions remains blocked
before step-level logs, and no production integration was performed.
