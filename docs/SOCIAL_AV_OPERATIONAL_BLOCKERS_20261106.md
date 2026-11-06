# Social ↔ Audiovisual operational admission ledger (2026-11-06)

Status: **CANDIDATE / NO PUBLICATION**.

## CI architecture — private-origin cross-repository test

The old public Social → private AV checkout failed: a standard GITHUB_TOKEN of one repository does not grant access to another private repository. No token should be placed in code or public workflows.

**Resolved in the opposite direction:** private `agente-youtube` PR #479 has workflow `.github/workflows/pv86-social-av-cross-repo.yml`, checking out public `Redes-Sociais` branch `feature/editorial-learning-core-v1`, and runs both repositories' actual Python contracts. Run 42299527464 = SUCCESS for SHA `6b0d0379ff9db1d2ae0a57e4688b6ed12e703c41`. This is **contract interoperability** only, not video rendering or editorial authorization.

The Social branch's local CI does not access private repositories, has no `AV_REPO_READ_TOKEN` requirement, and must not claim to test cross-repo interop on its own. An AV branch ref should be pinned to commit SHA for promotion, and future Social changes require a new cross-repo check.

## Release boundary hardening

Social candidate `contract_compatible` measures schema/identity consistency only. `publication_ready=false` regardless of fixture `approval=approved`, because self-reported PASS and evidence string IDs do not authenticate human/technical observation.

## Outstanding pre-merge requirements

1. Cross-repo tests with **actual user original and edited MP4 pair** remain absent. PR #479 includes FFprobe identity and synthetic MP4 regression, not speech preservation.
2. PV86 29 clips are integrity-checked, 29 + 8 user decisions linked, but one task `low_025` is UNCERTAIN and corrections conflict. No independent certification.
3. AVIA #474 is draft, tested with technical real media in isolation; no full PT-BR semantics parity or merged interface.
4. Private PR #479 and Social PR #1 require human review, full suite and authorized merge.
5. Platform telemetry and causal impact estimates are not independently measured.

Operational gates: `HUMAN_REVIEW_CERTIFIED=false`, `SPEECH_PRESERVATION=NOT_VERIFIED`, `PUBLICATION=BLOCKED`.
