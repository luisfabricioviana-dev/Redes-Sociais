# Social ↔ Audiovisual: operational admission and blocked release

Status: **CANDIDATE / NO PRODUCTION PUBLICATION**.

## Important safety separation

The Social editorial engine checks candidate **contract compatibility**; it does not independently verify QA evidence identifiers, factual claims, licenses, or reviewer identity. Neither a `PASS` in a fixture nor `approval=approved` proves release authorization. `publication_ready` is **always false** in this candidate. Successful structural validation is reported under `contract_compatible`. All real publishing requires a separately implemented and independently validated release authority.

## Private cross-repository CI failure: access, not interoperability

The workflow `cross-repository-contract.yml` previously returned `Repository not found` when checking out `luisfabricioviana-dev/agente-youtube` from the `Redes-Sociais` repository. The default GITHUB_TOKEN is scoped to one repository, even for the same owner.

Configure a **fine-grained, read-only** GitHub token with access only to private `agente-youtube` (Contents: Read), then store it as the *Actions repository secret* `AV_REPO_READ_TOKEN` in **Redes-Sociais**. Never commit, print, paste, or include this token in reports. Rerun the specific workflow and verify that the checkout + cross-repository tests actually run. Missing token produces an explicit CI failure, not a green skip.

## Separate blockers

1. This PR #1 remains draft until its full tests and independent code review.
2. The corresponding AV branch `feature/social-av-exchange-v1` is a **planning contract**, not a rendering pipeline.
3. PR #479 in `agente-youtube` has a candidate PV86 import and ffprobe witness; 29 actual audio excerpts verified separately, but **no user source/edit pair of MP4 has been tested**.
4. AVIA PR #474 is still a standalone candidate, not automatically imported by this workflow.
5. PV86 reviewer independence is not certified; `low_025` is still UNCERTAIN, and other lexical revisions differ.
6. No causal retention gains or real platform engagement metrics are established.

Required for final promotion: true decoded user media, source/edit word-level fidelity checks, explicit source ownership/rights, independent editorial release sign-off, scoped channel identity, cross-repo CI, review and authorized merge.
