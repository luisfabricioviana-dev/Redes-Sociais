"""Strict offline artifact binding for independent REA editorial review.

Checks actual bytes and a regression receipt. Does not establish that the
reviewer is independently authenticated, or that a scientific claim is true.
"""
import hashlib
import hmac
import json
import re
from contracts.rea_independent_review import evaluate_independent_review

_HEX = re.compile(r"[0-9a-f]{64}\Z")
_MAX = 2_000_000

def _sha(data):
    return hashlib.sha256(data).hexdigest()

def verify_review_artifacts(ticket, review, witness_bytes, regression_bytes, regression_sha256):
    """Return fail-closed structural result; never grant promotion."""
    base = evaluate_independent_review(ticket, review)
    reasons = list(base["reasons"])
    if base["status"] != "REVIEW_EVIDENCE_COMPLETE":
        return {"status": "BLOCKED", "reasons": reasons, "promotion_authorized": False}
    if not isinstance(witness_bytes, bytes) or not witness_bytes or len(witness_bytes) > _MAX:
        reasons.append("witness_bytes_unavailable")
    elif not hmac.compare_digest(_sha(witness_bytes), review.witness_sha256):
        reasons.append("witness_bytes_digest_mismatch")
    if not isinstance(regression_bytes, bytes) or not regression_bytes or len(regression_bytes) > _MAX:
        reasons.append("regression_bytes_unavailable")
    if not isinstance(regression_sha256, str) or not _HEX.fullmatch(regression_sha256):
        reasons.append("regression_digest_missing")
    if reasons:
        return {"status": "BLOCKED", "reasons": reasons, "promotion_authorized": False}
    if not hmac.compare_digest(_sha(regression_bytes), regression_sha256):
        reasons.append("regression_bytes_digest_mismatch")
    else:
        try:
            record = json.loads(regression_bytes.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            record = None
        if not isinstance(record, dict):
            reasons.append("regression_record_invalid")
        else:
            matching = {
                "regression_id": review.regression_id,
                "candidate_sha256": review.candidate_sha256,
                "independent_reviewer_id": review.independent_reviewer_id,
                "witness_sha256": review.witness_sha256,
                "status": "PASS",
                "domain": "SOCIAL",
            }
            for key, expected in matching.items():
                if record.get(key) != expected:
                    reasons.append("regression_record_mismatch:" + key)
            if record.get("promotion_authorized") is not False:
                reasons.append("regression_record_unsafe_promotion")
    return {"status": "BLOCKED" if reasons else "ARTIFACTS_BOUND_FOR_REVIEW",
            "reasons": reasons, "promotion_authorized": False,
            "next_gate": "AUTHENTICATE_REVIEWER_AND_VERIFY_EVIDENCE_MEANING"}
