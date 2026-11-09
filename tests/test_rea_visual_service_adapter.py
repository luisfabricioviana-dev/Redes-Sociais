import json
import tempfile
import unittest
from pathlib import Path
from adapters.rea_visual_service_v1 import build_job,write_job,release_gate

class TestREAVisualAdapter(unittest.TestCase):
    def test_job_schema(self):
        data=build_job(job_id="example_1",png_path="frame.png")
        self.assertEqual(data["schema"],"rea.visual_job.v1")
        self.assertEqual(data["agent"],"SOCIAL")
        self.assertEqual(data["candidate"],{"change":"retain_border_only"})
        self.assertEqual(data["evaluation_split"],"development")

    def test_invalid_requests_rejected(self):
        for opts in ({"job_id":"../x","png_path":"a.png"},
                     {"job_id":"x","png_path":"a.pdf"},
                     {"job_id":"x","png_path":"a.png","reference_path":"a.exe"},
                     {"job_id":"x","png_path":"a.png","min_area":True}):
            with self.subTest(opts=opts),self.assertRaises(ValueError):
                build_job(**opts)

    def test_no_clobber(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"job.json"
            write_job(p,job_id="x",png_path="a.png")
            previous=p.read_bytes()
            self.assertEqual(json.loads(previous)["agent"],"SOCIAL")
            with self.assertRaisesRegex(ValueError,"NO_CLOBBER"):
                write_job(p,job_id="x",png_path="a.png")
            self.assertEqual(p.read_bytes(),previous)

    def test_release_is_always_blocked(self):
        gate=release_gate({"schema":"rea.visual_service_report.v1",
                           "agent":"SOCIAL",
                           "regression_completed":True,
                           "promoted_to_core":True})
        self.assertFalse(gate["AUTOMATIC_PUBLICATION_ALLOWED"])
        self.assertFalse(gate["PROMOTED_TO_PRODUCTION"])
        self.assertFalse(gate["SEMANTIC_PUBLICATION_APPROVED"])
        with self.assertRaises(ValueError):
            release_gate({"schema":"rea.visual_service_report.v1","agent":"LAF"})

if __name__=="__main__":
    unittest.main()
