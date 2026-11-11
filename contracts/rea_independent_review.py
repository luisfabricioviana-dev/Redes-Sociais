"""Review-evidence gate for REA Social candidates; does not authorize promotion.

This checks structural coherence of externally supplied witnesses. It cannot
authenticate reviewer identity or independently establish scientific truth.
"""
from dataclasses import dataclass
import re
from typing import Any

_HEX = re.compile(r"[0-9a-f]{64}\Z")

@dataclass(frozen=True)
class IndependentReview:
    candidate_sha256: str
    source_id: str
    regression_id: str
    reviewer_id: str
    independent_reviewer_id: str
    regression_status: str
    witness_sha256: str
    witness_location: str
    domain: str = "SOCIAL"
    cross_profile_private_data: bool = False
    action_authorized: bool = False


def evaluate_independent_review(ticket: dict, review: IndependentReview) -> dict[str, Any]:
    """Review gate: success allows human governance review only."""
    reasons = []
    if not isinstance(ticket, dict) or ticket.get("status") != "CANDIDATE_FOR_REVIEW" or ticket.get("promoted") is not False:
        return {"status": "BLOCKED", "reasons": ["candidate_ticket_invalid"], "promotion_authorized": False}
    if not isinstance(review, IndependentReview):
        return {"status": "BLOCKED", "reasons": ["independent_review_missing"], "promotion_authorized": False}
    if not isinstance(review.candidate_sha256, str) or not _HEX.fullmatch(review.candidate_sha256) or ticket.get("artifact_sha256") != review.candidate_sha256:
        reasons.append("candidate_identity_mismatch")
    for key in ("source_id", "regression_id"):
        if not isinstance(getattr(review, key), str) or ticket.get(key) != getattr(review, key):
            reasons.append(key + "_mismatch")
    if review.reviewer_id != ticket.get("reviewer_id"):
        reasons.append("original_reviewer_mismatch")
    if not isinstance(review.independent_reviewer_id, str) or not review.independent_reviewer_id.strip() or review.independent_reviewer_id == review.reviewer_id:
        reasons.append("independent_reviewer_not_separate")
    if review.regression_status != "PASS":
        reasons.append("regression_not_passed")
    if not isinstance(review.witness_sha256, str) or not _HEX.fullmatch(review.witness_sha256) or not isinstance(review.witness_location, str) or not review.witness_location.strip():
        reasons.append("review_witness_missing")
    if review.domain != "SOCIAL" or ticket.get("learning_domain") != "SOCIAL":
        reasons.append("domain_mismatch")
    if review.cross_profile_private_data is not False:
        reasons.append("profile_isolation_unverified")
    if review.action_authorized is not False:
        reasons.append("action_boundary_not_safe")
    return {"status": "BLOCKED" if reasons else "REVIEW_EVIDENCE_COMPLETE",
            "reasons": reasons, "promotion_authorized": False,
            "next_gate": "AUTHENTICATE_WITNESSES_AND_HUMAN_PROMOTION_DECISION"}
