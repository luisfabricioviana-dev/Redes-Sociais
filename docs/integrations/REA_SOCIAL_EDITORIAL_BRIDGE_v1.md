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
