import hashlib
import json
import unittest
from dataclasses import replace
from contracts.rea_editorial_bridge import admit_editorial_learning
from contracts.rea_review_artifacts import verify_review_artifacts
from contracts.rea_independent_review import IndependentReview
from test_rea_editorial_bridge import request

TICKET = admit_editorial_learning(request())
WITNESS = b"independent human inspection evidence -- fixture"
SHA = hashlib.sha256(WITNESS).hexdigest()

def fixture(**overrides):
    review = IndependentReview(
        candidate_sha256=TICKET["artifact_sha256"], source_id=TICKET["source_id"],
        regression_id=TICKET["regression_id"], reviewer_id=TICKET["reviewer_id"],
        independent_reviewer_id="second-auditor", regression_status="PASS",
        witness_sha256=SHA, witness_location="fixture://inspection",
    )
    rec = {"regression_id": review.regression_id, "candidate_sha256": review.candidate_sha256,
           "independent_reviewer_id": review.independent_reviewer_id, "witness_sha256": SHA,
           "status": "PASS", "domain": "SOCIAL", "promotion_authorized": False}
    rec.update(overrides)
    data = json.dumps(rec, sort_keys=True).encode()
    return review, data, hashlib.sha256(data).hexdigest()

class ArtifactBindingTests(unittest.TestCase):
    def test_happy_path_not_promotion(self):
        rev, data, digest=fixture()
        result=verify_review_artifacts(TICKET, rev, WITNESS, data, digest)
        self.assertEqual(result["status"],"ARTIFACTS_BOUND_FOR_REVIEW")
        self.assertFalse(result["promotion_authorized"])
    def test_wrong_witness_bytes(self):
        rev,data,digest=fixture()
        result=verify_review_artifacts(TICKET, rev, b"fabricated",data,digest)
        self.assertIn("witness_bytes_digest_mismatch",result["reasons"])
    def test_wrong_regression_digest(self):
        rev,data,_=fixture()
        result=verify_review_artifacts(TICKET, rev,WITNESS,data,"0"*64)
        self.assertIn("regression_bytes_digest_mismatch",result["reasons"])
    def test_mismatched_candidate_record(self):
        rev,data,digest=fixture(candidate_sha256="0"*64)
        result=verify_review_artifacts(TICKET,rev,WITNESS,data,digest)
        self.assertIn("regression_record_mismatch:candidate_sha256",result["reasons"])
    def test_regression_failing(self):
        rev,data,digest=fixture(status="FAIL")
        result=verify_review_artifacts(TICKET,rev,WITNESS,data,digest)
        self.assertIn("regression_record_mismatch:status",result["reasons"])
    def test_unauthorized_promotion(self):
        rev,data,digest=fixture(promotion_authorized=True)
        result=verify_review_artifacts(TICKET,rev,WITNESS,data,digest)
        self.assertIn("regression_record_unsafe_promotion",result["reasons"])
    def test_invalid_json_regression(self):
        rev,_,_=fixture()
        data=b"not json"
        result=verify_review_artifacts(TICKET,rev,WITNESS,data,hashlib.sha256(data).hexdigest())
        self.assertIn("regression_record_invalid",result["reasons"])
    def test_missing_bytes(self):
        rev,data,digest=fixture()
        result=verify_review_artifacts(TICKET,rev,None,data,digest)
        self.assertIn("witness_bytes_unavailable",result["reasons"])
    def test_changed_reviewer(self):
        rev,data,digest=fixture()
        rev=replace(rev,independent_reviewer_id=rev.reviewer_id)
        result=verify_review_artifacts(TICKET,rev,WITNESS,data,digest)
        self.assertIn("independent_reviewer_not_separate",result["reasons"])
if __name__=="__main__": unittest.main()
