import unittest
from dataclasses import replace
from contracts.rea_independent_review import IndependentReview, evaluate_independent_review
from test_rea_editorial_bridge import request
from contracts.rea_editorial_bridge import admit_editorial_learning

TICKET = admit_editorial_learning(request())

def review(**kwargs):
    obj = IndependentReview(candidate_sha256=TICKET['artifact_sha256'],source_id=TICKET['source_id'],
        regression_id=TICKET['regression_id'], reviewer_id=TICKET['reviewer_id'],
        independent_reviewer_id='second-auditor', regression_status='PASS',
        witness_sha256='a'*64, witness_location='fixture://signed-evidence')
    return replace(obj, **kwargs)

class IndependentReviewTests(unittest.TestCase):
    def test_review_only_never_promotes(self):
        v=evaluate_independent_review(TICKET,review())
        self.assertEqual(v['status'],'REVIEW_EVIDENCE_COMPLETE')
        self.assertFalse(v['promotion_authorized'])
    def test_wrong_candidate_hash(self):
        self.assertIn('candidate_identity_mismatch',evaluate_independent_review(TICKET,review(candidate_sha256='0'*64))['reasons'])
    def test_same_reviewer(self):
        self.assertIn('independent_reviewer_not_separate',evaluate_independent_review(TICKET,review(independent_reviewer_id=TICKET['reviewer_id']))['reasons'])
    def test_regression_failed(self):
        self.assertIn('regression_not_passed',evaluate_independent_review(TICKET,review(regression_status='FAIL'))['reasons'])
    def test_wrong_regression_link(self):
        self.assertIn('regression_id_mismatch',evaluate_independent_review(TICKET,review(regression_id='unrelated'))['reasons'])
    def test_missing_witness(self):
        self.assertIn('review_witness_missing',evaluate_independent_review(TICKET,review(witness_location=''))['reasons'])
    def test_domain_isolation(self):
        self.assertIn('domain_mismatch',evaluate_independent_review(TICKET,review(domain='AV'))['reasons'])
    def test_actions_denied(self):
        self.assertIn('action_boundary_not_safe',evaluate_independent_review(TICKET,review(action_authorized=True))['reasons'])
    def test_invalid_ticket(self):
        altered=dict(TICKET, promoted=True)
        self.assertEqual(evaluate_independent_review(altered,review())['status'],'BLOCKED')
    def test_invalid_review(self):
        self.assertEqual(evaluate_independent_review(TICKET,{})['status'],'BLOCKED')

if __name__ == '__main__': unittest.main()
