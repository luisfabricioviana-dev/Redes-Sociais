"""Provider-agnostic adapters. No audiovisual execution or publication."""
from __future__ import annotations
from hashlib import sha256
import json
from .engine import LearningError, build_handoff, validate_final_package, record_learning, CHANNELS

def _digest(payload):
    return sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()

def create_exchange(candidate: dict) -> dict:
    """Build a transport envelope, preserving the original brief hash as trusted identity."""
    handoff = build_handoff(candidate)
    return {"protocol": "SOCIAL_AV_EXCHANGE_v1", "brief": handoff,
            "trusted_brief_sha256": handoff["sha256"], "channel": handoff["payload"]["channel"]}

def receive_av_result(exchange: dict, av_package: dict) -> dict:
    """Check round-trip identity and channel. Does not trust claims of QA without witnesses."""
    if not isinstance(exchange, dict) or exchange.get("protocol") != "SOCIAL_AV_EXCHANGE_v1":
        raise LearningError("invalid social AV exchange")
    brief = exchange.get("brief")
    if not isinstance(brief, dict) or brief.get("contract") != "SOCIAL_MEDIA_BRIEF_v1":
        raise LearningError("invalid originating brief")
    payload = brief.get("payload")
    if not isinstance(payload, dict) or payload.get("channel") not in CHANNELS:
        raise LearningError("invalid original channel")
    issues = []
    expected = brief.get("sha256")
    # Original handoff uses pretty/default JSON encoding; check using the same rule.
    actual = sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    if expected != actual or exchange.get("trusted_brief_sha256") != expected:
        issues.append("ORIGINATING_BRIEF_TAMPERED")
    if exchange.get("channel") != payload["channel"]:
        issues.append("EXCHANGE_CHANNEL_MISMATCH")
    if not isinstance(av_package, dict):
        raise LearningError("AV package must be a dict")
    if av_package.get("channel") != payload["channel"]:
        issues.append("AV_CHANNEL_MISMATCH")
    verdict = validate_final_package(av_package, expected)
    issues.extend(issue["code"] for issue in verdict["issues"])
    # Evidence identifiers must be present; these are assertions, not verified QA proofs.
    evidence = av_package.get("qa_evidence")
    needed = ("semantic_alignment", "factual_integrity", "provenance", "platform_preview", "audiovisual_qa")
    if not isinstance(evidence, dict):
        issues.append("MISSING_AV_QA_EVIDENCE")
    else:
        for key in needed:
            if not isinstance(evidence.get(key), str) or not evidence[key].strip():
                issues.append("MISSING_AV_QA_EVIDENCE:" + key)
    return {"status": "BLOCKED" if issues else "PASS", "publication_ready": not issues,
            "issues": sorted(set(issues)), "brief_sha256": expected}

def ingest_tutorial(observation: dict) -> dict:
    """Learning adapter: candidates only; no automatic canon promotion."""
    return record_learning(observation)
