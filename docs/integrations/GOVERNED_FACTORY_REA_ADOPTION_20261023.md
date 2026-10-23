# Governed Factory + REA — destination adoption contract

Status: **CANDIDATE / NOT DEPLOYED**. This is an integration proposal, not evidence of active agent behavior.

Canonical source: [Agente de Aprendizagem e Inovação PR #23](https://github.com/luisfabricioviana-dev/Apredizagem-e-Inova-o/pull/23), merged SHA `857618df6a33f963dafde98f39d3ba359fad275b`.

Destination scope: Social/editorial agent; shared evidence and deployment controls only, no cross-channel profile data.

## Reusable security and learning invariants
- `SHIPPED_ARTIFACT_THREAT_MODEL_v1`: client-delivered compiled/binary content is inspectable.
- `SECRET_PLACEMENT_GATE_v1`: never embed long-lived credentials in client-side deliverables.
- `BINARY_RECONSTRUCTION_EVIDENCE_GATE_v1`: distinguish pseudocode, recovered source, behavioral equivalence and byte-identical rebuild.
- `REA_LEARNING_ROUTER_v1`: learning requires provenance, risk screening, sandbox validation, regression and governed release. REA is optional, not a mandatory runtime dependency.
- Shared Factory promotion requires trusted exact-SHA CI, approvals, provider policy checks and auditable release/rollback.

## Destination-specific gate
1. Map new contracts to existing local components and document the actual integration point.
2. Keep shared Core mechanisms separate from specialized domain memories, editorial rules and protected source data.
3. Implement destination tests for client secret leakage, fabricated evidence, stale commit, and runtime fail-closed behavior as applicable.
4. Run local regressions/CI and obtain a destination reviewer approval before merge.
5. Verify the resulting destination merge commit and runtime uptake before reporting distribution as complete.

Rollback is destination-PR-specific. No new credentials, private user cases or agent domain facts are included here.
