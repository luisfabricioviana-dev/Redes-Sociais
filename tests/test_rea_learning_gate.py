import hashlib
import unittest
from contracts.rea_learning_gate import Candidate, evaluate_candidate, DOMAIN

class DomainGateTests(unittest.TestCase):
    DATA = b"general reusable method without private data"
    def candidate(self, **changes):
        base = dict(expected_sha256=hashlib.sha256(self.DATA).hexdigest(),
                    source_verified=True, evidence_reviewed=True, generalizable=True,
                    domain=DOMAIN, cross_profile_private_data=False,
                    action_authorized=False)
        base.update(changes)
        return Candidate(**base)
    def test_valid_candidate_only_eligible_for_review(self):
        self.assertEqual(evaluate_candidate(self.DATA, self.candidate()), (True, ()))
    def test_integrity_and_domain_isolation(self):
        self.assertIn("artifact_integrity_unverified",
                      evaluate_candidate(b"tampered", self.candidate())[1])
        self.assertIn("domain_mismatch",
                      evaluate_candidate(self.DATA, self.candidate(domain="OTHER"))[1])
        self.assertIn("data_isolation_unproven",
                      evaluate_candidate(self.DATA, self.candidate(cross_profile_private_data=True))[1])
    def test_declared_approval_does_not_enable_action(self):
        accepted, reasons = evaluate_candidate(
            self.DATA, self.candidate(action_authorized=True,
                source_verified=False, evidence_reviewed=False, generalizable=False))
        self.assertFalse(accepted)
        self.assertIn("action_boundary_not_safe", reasons)
if __name__ == "__main__":
    unittest.main()
