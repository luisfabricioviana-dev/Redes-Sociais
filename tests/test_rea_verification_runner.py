"""Safety checks for offline audit receipt generation."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from scripts.verify_rea_editorial_bridge import audit, REQUIRED

class OfflineVerificationTests(unittest.TestCase):
    def test_non_git_directory_never_verified(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            report=audit(root, Path(d + "-receipt.json"))
            self.assertEqual(report["status"],"UNVERIFIED")
            self.assertFalse(report["promotion_authorized"])
            self.assertIsNone(report["git_head"])
            self.assertTrue(report["missing_files"])
    def test_receipt_has_machine_readable_fail_closed_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            report=audit(root, Path(d + "-audit.json"))
            stored=json.loads(Path(d + "-audit.json").read_text())
            self.assertEqual(stored["status"],"UNVERIFIED")
            self.assertFalse(stored["ci_validated"])
            self.assertFalse(stored["publication_authorized"])
            self.assertEqual(report["status"],stored["status"])
    def test_receipt_inside_repo_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with self.assertRaises(ValueError):
                audit(root,root/"receipt.json")
    def test_clean_committed_tree_verified(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"repo";root.mkdir()
            origin=Path(__file__).resolve().parents[1]
            for rel in REQUIRED:
                dst=root/rel;dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(origin/rel,dst)
            subprocess.run(["git","init","-q"],cwd=root,check=True)
            subprocess.run(["git","-c","user.name=Fixture","-c","user.email=fixture@example.invalid",
                            "add","."],cwd=root,check=True)
            subprocess.run(["git","-c","user.name=Fixture","-c","user.email=fixture@example.invalid",
                            "commit","-qm","fixture"],cwd=root,check=True)
            result=audit(root,Path(d)/"receipt.json")
            self.assertEqual(result["status"],"LOCAL_COMMIT_TESTED")
            self.assertFalse(result["promotion_authorized"])
            (root/"dirty.txt").write_text("dirty")
            result=audit(root,Path(d)/"dirty-receipt.json")
            self.assertEqual(result["status"],"UNVERIFIED")

    def test_assume_unchanged_required_file_tampering_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"repo";root.mkdir()
            origin=Path(__file__).resolve().parents[1]
            for rel in REQUIRED:
                dst=root/rel;dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(origin/rel,dst)
            subprocess.run(["git","init","-q"],cwd=root,check=True)
            subprocess.run(["git","add","."],cwd=root,check=True)
            subprocess.run(["git","-c","user.name=Fixture",
                            "-c","user.email=fixture@example.invalid",
                            "commit","-qm","fixture"],cwd=root,check=True)
            rel=REQUIRED[0]
            subprocess.run(["git","update-index","--assume-unchanged",rel],
                           cwd=root,check=True)
            (root/rel).write_text("# altered after commit\n",encoding="utf-8")
            status=subprocess.run(["git","status","--porcelain"],cwd=root,
                                  check=True,capture_output=True,text=True)
            self.assertEqual(status.stdout.strip(),"")
            result=audit(root,Path(d)/"tampered-receipt.json")
            self.assertEqual(result["status"],"UNVERIFIED")
            self.assertIn(rel,result["commit_content_mismatches"])

    def test_running_tests_that_mutate_checkout_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"repo";root.mkdir()
            origin=Path(__file__).resolve().parents[1]
            for rel in REQUIRED:
                dst=root/rel;dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(origin/rel,dst)
            mutator=root/"tests/test_rea_mutates_checkout.py"
            mutator.write_text(
                "import unittest\n"
                "from pathlib import Path\n"
                "class MutatesCheckout(unittest.TestCase):\n"
                "    def test_mutate(self):\n"
                "        Path('contracts/rea_learning_gate.py').write_text('# changed by test\\\n')\n",
                encoding="utf-8")
            subprocess.run(["git","init","-q"],cwd=root,check=True)
            subprocess.run(["git","add","."],cwd=root,check=True)
            subprocess.run(["git","-c","user.name=Fixture",
                            "-c","user.email=fixture@example.invalid",
                            "commit","-qm","fixture"],cwd=root,check=True)
            result=audit(root,Path(d)/"mutated-receipt.json")
            self.assertEqual(result["test_exit_code"],0)
            self.assertEqual(result["status"],"UNVERIFIED")
            self.assertFalse(result["git_clean_after_tests"])

    def test_running_tests_with_hidden_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"repo";root.mkdir()
            origin=Path(__file__).resolve().parents[1]
            for rel in REQUIRED:
                dst=root/rel;dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(origin/rel,dst)
            mutator=root/"tests/test_rea_hidden_mutation.py"
            mutator.write_text(
                "import unittest,subprocess\n"
                "from pathlib import Path\n"
                "class HiddenMutator(unittest.TestCase):\n"
                "    def test_mutate(self):\n"
                "        subprocess.run(['git','update-index','--assume-unchanged','contracts/rea_learning_gate.py'],check=True)\n"
                "        Path('contracts/rea_learning_gate.py').write_text('# concealed edit\\\n')\n",
                encoding="utf-8")
            subprocess.run(["git","init","-q"],cwd=root,check=True)
            subprocess.run(["git","add","."],cwd=root,check=True)
            subprocess.run(["git","-c","user.name=Fixture",
                            "-c","user.email=fixture@example.invalid",
                            "commit","-qm","fixture"],cwd=root,check=True)
            result=audit(root,Path(d)/"hidden-mutation-receipt.json")
            self.assertEqual(result["test_exit_code"],0)
            self.assertTrue(result["git_clean_after_tests"])
            self.assertEqual(result["status"],"UNVERIFIED")
            self.assertIn(REQUIRED[0],result["commit_content_mismatches"])

if __name__=="__main__": unittest.main()
