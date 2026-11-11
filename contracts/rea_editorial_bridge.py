"""Candidate-only bridge between REA learning admission and Social editorial review.

Reuses rea_learning_gate. No private-profile transfer or automatic promotion.
"""
from dataclasses import dataclass
from hashlib import sha256
from typing import Any

from contracts.rea_learning_gate import Candidate, evaluate_candidate, DOMAIN

@dataclass(frozen=True)
class EditorialLearningRequest:
    artifact: bytes
    expected_sha256: str
    source_id: str
    reviewer_id: str
    regression_id: str
    source_verified: bool
    evidence_reviewed: bool
    generalizable: bool
    domain: str = DOMAIN
    cross_profile_private_data: bool = False
    action_authorized: bool = False

def admit_editorial_learning(request: EditorialLearningRequest) -> dict[str, Any]:
    """Check REA admission + editorial metadata. Eligible means reviewable, never canon."""
    if not isinstance(request, EditorialLearningRequest):
        return {"status": "REJECTED", "reasons": ["request_invalid"], "promoted": False}
    admission = Candidate(
        expected_sha256=request.expected_sha256,
        source_verified=request.source_verified,
        evidence_reviewed=request.evidence_reviewed,
        generalizable=request.generalizable,
        domain=request.domain,
        cross_profile_private_data=request.cross_profile_private_data,
        action_authorized=request.action_authorized,
    )
    accepted, rea_reasons = evaluate_candidate(request.artifact, admission)
    reasons = list(rea_reasons)
    for field in ("source_id", "reviewer_id", "regression_id"):
        value = getattr(request, field)
        if not isinstance(value, str) or not value.strip():
            reasons.append("missing_" + field)
    if not accepted or reasons:
        return {"status": "REJECTED", "reasons": reasons, "promoted": False}
    # Hash and metadata are a review ticket, never independent proof of factual accuracy.
    return {
        "status": "CANDIDATE_FOR_REVIEW", "promoted": False,
        "learning_domain": DOMAIN,
        "artifact_sha256": sha256(request.artifact).hexdigest(),
        "source_id": request.source_id,
        "reviewer_id": request.reviewer_id,
        "regression_id": request.regression_id,
        "next_gate": "INDEPENDENT_REGRESSION_AND_PROFILE_ISOLATION_REVIEW",
    }
