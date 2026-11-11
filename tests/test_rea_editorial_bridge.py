import hashlib
import unittest
from dataclasses import replace
from contracts.rea_editorial_bridge import EditorialLearningRequest, admit_editorial_learning

PAYLOAD=b"reusable editing principle; no personal source data"

def request(**overrides):
    base=EditorialLearningRequest(
        artifact=PAYLOAD,
        expected_sha256=hashlib.sha256(PAYLOAD).hexdigest(),
        source_id="tutorial:fixture",
        reviewer_id="fixture-reviewer",
        regression_id="regression:fixture",
        source_verified=True,
        evidence_reviewed=True,
        generalizable=True,
    )
    return replace(base, **overrides)

class EditorialBridgeTests(unittest.TestCase):
    def test_eligible_is_not_promoted(self):
        result=admit_editorial_learning(request())
        self.assertEqual(result["status"], "CANDIDATE_FOR_REVIEW")
        self.assertFalse(result["promoted"])
        self.assertEqual(result["artifact_sha256"],hashlib.sha256(PAYLOAD).hexdigest())
    def test_changed_payload_rejected(self):
        result=admit_editorial_learning(request(artifact=b"tampered"))
        self.assertIn("artifact_integrity_unverified", result["reasons"])
    def test_cross_domain_rejected(self):
        result=admit_editorial_learning(request(domain="AUDIOVISUAL"))
        self.assertIn("domain_mismatch",result["reasons"])
    def test_private_profile_data_rejected(self):
        result=admit_editorial_learning(request(cross_profile_private_data=True))
        self.assertIn("data_isolation_unproven",result["reasons"])
    def test_unsafe_action_rejected(self):
        result=admit_editorial_learning(request(action_authorized=True))
        self.assertIn("action_boundary_not_safe",result["reasons"])
    def test_missing_regression_rejected(self):
        result=admit_editorial_learning(request(regression_id=""))
        self.assertIn("missing_regression_id",result["reasons"])
    def test_missing_reviewer_rejected(self):
        result=admit_editorial_learning(request(reviewer_id=""))
        self.assertIn("missing_reviewer_id",result["reasons"])
    def test_unverified_source_rejected(self):
        result=admit_editorial_learning(request(source_verified=False))
        self.assertIn("source_unverified",result["reasons"])
    def test_malformed_request_rejected(self):
        self.assertEqual(admit_editorial_learning({})["status"],"REJECTED")
if __name__=="__main__": unittest.main()
