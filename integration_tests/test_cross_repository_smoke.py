"""Cross-repository contract smoke test; requires AV repo source on PYTHONPATH.

Never invokes audiovisual runtime. A passing test certifies schema interoperability ONLY.
"""
import unittest
from test_editorial_learning import good
from social_core.adapters import create_exchange, receive_av_result
from contracts.social_av_exchange_v1 import accept_social_brief, build_final_candidate, ContractError

FIELDS=("semantic_alignment","factual_integrity","provenance","platform_preview","audiovisual_qa")

class CrossRepositorySmoke(unittest.TestCase):
    def test_round_trip_with_explicit_social_approval(self):
        original=create_exchange(good("natureza_em_360"))
        accepted=accept_social_brief(original)
        self.assertFalse(accepted["runtime_authorized"])
        package=build_final_candidate(accepted,"test-render-1",
            {k:"PASS" for k in FIELDS},{k:"fixture:qa:"+k for k in FIELDS})
        self.assertEqual(package["approval"],"pending")
        self.assertFalse(receive_av_result(original,package)["publication_ready"])
        # Independent editorial approval decision; only exercised in a fixture.
        package["approval"]="approved"
        self.assertTrue(receive_av_result(original,package)["publication_ready"])
    def test_changed_source_blocked_by_av(self):
        original=create_exchange(good())
        original["brief"]["payload"]["script"]+=" altered"
        with self.assertRaises(ContractError):
            accept_social_brief(original)
    def test_mismatched_return_blocked_by_social(self):
        original=create_exchange(good())
        accepted=accept_social_brief(original)
        package=build_final_candidate(accepted,"test-render-2",
            {k:"PASS" for k in FIELDS},{k:"fixture:qa:"+k for k in FIELDS})
        package["approval"]="approved"
        package["channel"]="fronteiras_do_mundo_360"
        self.assertFalse(receive_av_result(original,package)["publication_ready"])

if __name__=="__main__": unittest.main()
