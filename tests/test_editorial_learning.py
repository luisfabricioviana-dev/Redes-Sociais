import unittest
from social_core import evaluate_candidate, build_handoff, validate_final_package, record_learning, LearningError

def good(channel="curiosos_conhecimentos"):
    return {"channel": channel, "hook": "Por que isso acontece?", "editorial_promise": "Explicação verificável",
            "script": "Uma descoberta explicada com contexto.", "claims": [
                {"id": "c1", "statement": "Afirmação de teste", "sources": [{"url": "https://example.org/study", "title": "Estudo"}],
                 "verification": "verified", "visual_proof": "mapped"}],
            "source_rights": "cleared", "retention_hypothesis": "Hook contextual reduz abandono."}

class EditorialCoreTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(evaluate_candidate(good())["status"], "PASS")
    def test_missing_claims_fail_closed(self):
        c=good(); c["claims"]=[]
        self.assertEqual(evaluate_candidate(c)["status"], "BLOCKED")
    def test_unsourced_claim(self):
        c=good(); c["claims"][0]["sources"]=[]
        self.assertEqual(evaluate_candidate(c)["status"], "BLOCKED")
    def test_unverified_claim(self):
        c=good(); c["claims"][0]["verification"]="unverified"
        self.assertEqual(evaluate_candidate(c)["status"], "BLOCKED")
    def test_visual_proof(self):
        c=good(); c["claims"][0]["visual_proof"]="not_mapped"
        self.assertEqual(evaluate_candidate(c)["status"], "REPAIR_REQUIRED")
    def test_rights(self):
        c=good(); c["source_rights"]="unknown"
        self.assertEqual(evaluate_candidate(c)["status"], "BLOCKED")
    def test_geo(self):
        c=good("fronteiras_do_mundo_360"); c["claims"][0].update({"geospatial":True,"geo_anchor":"unverified"})
        self.assertEqual(evaluate_candidate(c)["status"], "BLOCKED")
    def test_behavior(self):
        c=good("natureza_em_360"); c["claims"][0].update({"animal_behavior":True})
        self.assertEqual(evaluate_candidate(c)["status"], "BLOCKED")
    def test_isolation(self):
        c=good(); c["cross_channel_style"]=True
        self.assertEqual(evaluate_candidate(c)["status"], "BLOCKED")
    def test_handoff(self):
        h=build_handoff(good())
        self.assertEqual(h["contract"],"SOCIAL_MEDIA_BRIEF_v1")
        self.assertEqual(len(h["sha256"]),64)
    def test_block_handoff(self):
        c=good(); c["source_rights"]="unknown"
        with self.assertRaises(LearningError): build_handoff(c)
    def test_final_no_approval(self):
        p={"contract":"AUDIOVISUAL_FINAL_CANDIDATE_PACKAGE_v1","editorial_brief_sha256":"abc","render_id":"x",
           **{k:"PASS" for k in ("semantic_alignment","factual_integrity","provenance","platform_preview","audiovisual_qa")}}
        self.assertFalse(validate_final_package(p)["publication_ready"])
        p["approval"]="approved"
        self.assertTrue(validate_final_package(p)["publication_ready"])
    def test_learning_candidate(self):
        l=record_learning({"source_id":"tutorial1","observation":"retenção","hypothesis":"gancho melhora","owner":"social","channel":"curiosos_conhecimentos"})
        self.assertEqual(l["status"],"CANDIDATE")
    def test_no_auto_promotion(self):
        with self.assertRaises(LearningError):
            record_learning({"source_id":"x","observation":"x","hypothesis":"x","owner":"social","channel":"curiosos_conhecimentos","status":"CANONICAL"})
    def test_unknown_channel(self):
        with self.assertRaises(LearningError): evaluate_candidate(good("other"))

if __name__ == "__main__":
    unittest.main()
