"""Optional domain-isolated learning admission; never executes domain actions."""
from dataclasses import dataclass
import hashlib
import hmac
import re

DOMAIN = "SOCIAL"

@dataclass(frozen=True)
class Candidate:
    expected_sha256: str
    source_verified: bool
    evidence_reviewed: bool
    generalizable: bool
    domain: str
    cross_profile_private_data: bool
    action_authorized: bool

def evaluate_candidate(payload: bytes, candidate: Candidate) -> tuple[bool, tuple[str, ...]]:
    if not isinstance(payload, bytes) or not payload:
        return False, ("payload_missing",)
    if not isinstance(candidate, Candidate):
        return False, ("candidate_missing",)
    reasons = []
    digest = hashlib.sha256(payload).hexdigest()
    if (not isinstance(candidate.expected_sha256, str)
        or not re.fullmatch(r"[0-9a-f]{64}", candidate.expected_sha256)
        or not hmac.compare_digest(digest, candidate.expected_sha256)):
        reasons.append("artifact_integrity_unverified")
    if candidate.source_verified is not True: reasons.append("source_unverified")
    if candidate.evidence_reviewed is not True: reasons.append("evidence_review_missing")
    if candidate.generalizable is not True: reasons.append("generalizability_unproven")
    if candidate.domain != DOMAIN: reasons.append("domain_mismatch")
    if candidate.cross_profile_private_data is not False: reasons.append("data_isolation_unproven")
    if candidate.action_authorized is not False: reasons.append("action_boundary_not_safe")
    return not reasons, tuple(reasons)
