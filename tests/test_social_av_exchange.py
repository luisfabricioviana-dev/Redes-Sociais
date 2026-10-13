import unittest
from social_core.adapters import create_exchange, receive_av_result, ingest_tutorial
from social_core import LearningError
from test_editorial_learning import good

def returned(ex):
    return {"contract": "AUDIOVISUAL_FINAL_CANDIDATE_PACKAGE_v1",
            "editorial_brief_sha256": ex["trusted_brief_sha256"],
            "channel": ex["channel"], "render_id": "fixture-render",
            **{key: "PASS" for key in ("semantic_alignment", "factual_integrity", "provenance", "platform_preview", "audiovisual_qa")},
            "qa_evidence": {key: "fixture:" + key for key in ("semantic_alignment", "factual_integrity", "provenance", "platform_preview", "audiovisual_qa")},
            "approval": "approved"}

class IntegrationContracts(unittest.TestCase):
    def test_round_trip_fixture(self):
        ex = create_exchange(good())
        self.assertTrue(receive_av_result(ex, returned(ex))["publication_ready"])
    def test_tampered_origin(self):
        ex = create_exchange(good())
        out = returned(ex)
        ex["brief"]["payload"]["script"] = "mutated"
        self.assertFalse(receive_av_result(ex,out)["publication_ready"])
    def test_cross_channel_rejected(self):
        ex = create_exchange(good())
        out = returned(ex); out["channel"] = "natureza_em_360"
        self.assertFalse(receive_av_result(ex,out)["publication_ready"])
    def test_missing_qa_witnesses(self):
        ex = create_exchange(good())
        out = returned(ex); out.pop("qa_evidence")
        self.assertFalse(receive_av_result(ex,out)["publication_ready"])
    def test_bad_hash_rejected(self):
        ex = create_exchange(good())
        out = returned(ex); out["editorial_brief_sha256"] = "0" * 64
        self.assertFalse(receive_av_result(ex,out)["publication_ready"])
    def test_tutorial_not_promoted(self):
        result = ingest_tutorial({"source_id":"test-video","observation":"Hook", "hypothesis":"Better attention",
                                  "owner":"learning_shared","channel":"curiosos_conhecimentos"})
        self.assertEqual(result["status"], "CANDIDATE")
    def test_unknown_exchange(self):
        with self.assertRaises(LearningError):
            receive_av_result({}, {})
if __name__ == "__main__": unittest.main()
