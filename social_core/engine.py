"""Dependency-free editorial gates. Never performs publishing or audiovisual edits."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json

CHANNELS = frozenset({"fronteiras_do_mundo_360", "curiosos_conhecimentos", "natureza_em_360"})
STATUSES = ("BLOCKED", "REPAIR_REQUIRED", "PASS_WITH_NOTES", "PASS")
SEVERITY = {"PASS": 0, "PASS_WITH_NOTES": 1, "REPAIR_REQUIRED": 2, "BLOCKED": 3}

class LearningError(ValueError):
    pass

def _text(value):
    return isinstance(value, str) and bool(value.strip())

def _status(issues):
    if not issues:
        return "PASS"
    return max((s for s, _ in issues), key=SEVERITY.__getitem__)

def evaluate_candidate(candidate: dict) -> dict:
    """Evaluate script claims, source provenance, visual proof and channel isolation.
    Input is untrusted: absence of evidence fails closed, not replaced by guessed facts.
    """
    if not isinstance(candidate, dict):
        raise LearningError("candidate must be a dict")
    channel = candidate.get("channel")
    if channel not in CHANNELS:
        raise LearningError("unknown channel: identity isolation required")
    issues = []
    if not _text(candidate.get("hook")):
        issues.append(("REPAIR_REQUIRED", "MISSING_HOOK"))
    if not _text(candidate.get("editorial_promise")):
        issues.append(("REPAIR_REQUIRED", "MISSING_PROMISE"))
    if not _text(candidate.get("script")):
        issues.append(("BLOCKED", "MISSING_SCRIPT"))
    claims = candidate.get("claims")
    if not isinstance(claims, list) or not claims:
        issues.append(("BLOCKED", "MISSING_CLAIM_LEDGER"))
        claims = []
    ids = set()
    for idx, claim in enumerate(claims):
        if not isinstance(claim, dict):
            issues.append(("BLOCKED", f"INVALID_CLAIM:{idx}"))
            continue
        cid = claim.get("id")
        if not _text(cid) or cid in ids:
            issues.append(("BLOCKED", f"INVALID_CLAIM_ID:{idx}"))
        else:
            ids.add(cid)
        if not _text(claim.get("statement")):
            issues.append(("BLOCKED", f"EMPTY_CLAIM:{idx}"))
        sources = claim.get("sources")
        if not isinstance(sources, list) or not any(isinstance(s, dict) and _text(s.get("url")) and _text(s.get("title")) for s in sources):
            issues.append(("BLOCKED", f"UNSOURCED_CLAIM:{cid or idx}"))
        if claim.get("verification") != "verified":
            issues.append(("BLOCKED", f"UNVERIFIED_CLAIM:{cid or idx}"))
        if claim.get("visual_proof") != "mapped":
            issues.append(("REPAIR_REQUIRED", f"MISSING_VISUAL_PROOF:{cid or idx}"))
        if channel == "fronteiras_do_mundo_360" and claim.get("geospatial") is True and claim.get("geo_anchor") != "verified":
            issues.append(("BLOCKED", f"UNVERIFIED_GEO_ANCHOR:{cid or idx}"))
        if channel == "natureza_em_360" and claim.get("animal_behavior") is True and claim.get("footage_provenance") != "verified":
            issues.append(("BLOCKED", f"UNPROVEN_BEHAVIOR_FOOTAGE:{cid or idx}"))
    if candidate.get("source_rights") != "cleared":
        issues.append(("BLOCKED", "SOURCE_RIGHTS_UNCLEAR"))
    if candidate.get("cross_channel_style") is True:
        issues.append(("BLOCKED", "CHANNEL_STYLE_CONTAMINATION"))
    if candidate.get("retention_hypothesis") is None:
        issues.append(("PASS_WITH_NOTES", "NO_RETENTION_HYPOTHESIS"))
    return {"channel": channel, "status": _status(issues), "issues": [{"severity": s, "code": c} for s,c in issues],
            "can_handoff": not any(SEVERITY[s] >= SEVERITY["REPAIR_REQUIRED"] for s,_ in issues)}

def build_handoff(candidate: dict) -> dict:
    """Emit SOCIAL_MEDIA_BRIEF only after editorial gates pass."""
    result = evaluate_candidate(candidate)
    if not result["can_handoff"]:
        raise LearningError("editorial gate blocks audiovisual handoff")
    approved = {k: deepcopy(candidate.get(k)) for k in
                ("channel", "hook", "editorial_promise", "script", "claims", "retention_hypothesis")}
    payload = json.dumps(approved, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return {"contract": "SOCIAL_MEDIA_BRIEF_v1", "gate": result["status"],
            "sha256": sha256(payload).hexdigest(), "payload": approved,
            "audiovisual_instructions": {"no_unsourced_visual_assertions": True,
                                        "claim_visual_binding_required": True}}

def validate_final_package(package: dict) -> dict:
    """Fail closed on render review: Social approves publication; AV reports observed QA."""
    if not isinstance(package, dict) or package.get("contract") != "AUDIOVISUAL_FINAL_CANDIDATE_PACKAGE_v1":
        raise LearningError("invalid audiovisual return contract")
    issues = []
    for field in ("editorial_brief_sha256", "render_id", "semantic_alignment", "factual_integrity",
                  "provenance", "platform_preview", "audiovisual_qa"):
        if not _text(package.get(field)):
            issues.append(("BLOCKED", f"MISSING_{field.upper()}"))
    for field in ("semantic_alignment", "factual_integrity", "provenance", "platform_preview", "audiovisual_qa"):
        if package.get(field) != "PASS":
            issues.append(("BLOCKED", f"NONPASS_{field.upper()}"))
    if package.get("approval") != "approved":
        issues.append(("BLOCKED", "FINAL_APPROVAL_REQUIRED"))
    return {"status": _status(issues), "publication_ready": not issues,
            "issues": [{"severity": s, "code": c} for s,c in issues]}

def record_learning(case: dict) -> dict:
    """Record candidate learning; promotions are NEVER inferred from one tutorial."""
    if not isinstance(case, dict):
        raise LearningError("case must be a dict")
    for key in ("source_id", "observation", "hypothesis", "owner", "channel"):
        if not _text(case.get(key)):
            raise LearningError(f"missing {key}")
    if case["channel"] not in CHANNELS:
        raise LearningError("invalid channel")
    if case["owner"] not in ("social", "audiovisual", "learning_shared"):
        raise LearningError("invalid owner")
    if case.get("status") not in (None, "CANDIDATE"):
        raise LearningError("promotion requires independent review and regression")
    return {"record_type": "LEARNING_CANDIDATE_v1", "status": "CANDIDATE",
            "source_id": case["source_id"], "observation": case["observation"],
            "hypothesis": case["hypothesis"], "owner": case["owner"],
            "channel": case["channel"], "regression_id": case.get("regression_id"),
            "created_at": datetime.now(timezone.utc).isoformat()}
