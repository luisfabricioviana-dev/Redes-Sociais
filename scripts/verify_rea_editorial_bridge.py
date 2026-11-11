"""Auditable offline test receipt for a clean, exact Git commit. No publication rights."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

REQUIRED = (
    "contracts/rea_learning_gate.py",
    "contracts/rea_editorial_bridge.py",
    "contracts/rea_independent_review.py",
    "contracts/rea_review_artifacts.py",
    "tests/test_rea_editorial_bridge.py",
    "tests/test_rea_independent_review.py",
    "tests/test_rea_review_artifacts.py",
)

def _run(args, root):
    return subprocess.run(args, cwd=root, text=True, capture_output=True, check=False)

def audit(root: Path, out: Path) -> dict:
    root = root.resolve()
    out = out.resolve()
    if out == root or root in out.parents:
        raise ValueError("Audit receipt must be written outside the repository")
    git = _run(["git", "rev-parse", "--verify", "HEAD"], root)
    status = _run(["git", "status", "--porcelain", "--untracked-files=normal"], root)
    head = git.stdout.strip() if git.returncode == 0 else None
    clean = status.returncode == 0 and not status.stdout.strip()
    files = {}
    missing = []
    for rel in REQUIRED:
        target = root / rel
        if not target.is_file():
            missing.append(rel)
        else:
            files[rel] = hashlib.sha256(target.read_bytes()).hexdigest()
    run = None if missing else _run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_rea_*py", "-v"], root)
    tests_pass = run is not None and run.returncode == 0
    verified = bool(head and len(head) == 40 and clean and not missing and tests_pass)
    report = {
        "contract": "REA_SOCIAL_OFFLINE_VERIFICATION_v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": head,
        "git_clean": clean,
        "git_status_exit_code": status.returncode,
        "missing_files": missing,
        "input_sha256": files,
        "python": sys.version.split()[0],
        "test_command": "python -m unittest discover -s tests -p 'test_rea_*py' -v",
        "test_exit_code": run.returncode if run is not None else None,
        "test_stdout": (run.stdout if run else "")[-12000:],
        "test_stderr": (run.stderr if run else "")[-12000:],
        "status": "LOCAL_COMMIT_TESTED" if verified else "UNVERIFIED",
        "ci_validated": False,
        "promotion_authorized": False,
        "publication_authorized": False,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    report = audit(args.repo, args.out)
    print("STATUS=" + report["status"])
    print("HEAD=" + str(report["git_head"]))
    print("CLEAN=" + str(report["git_clean"]))
    print("TEST_EXIT=" + str(report["test_exit_code"]))
    return 0 if report["status"] == "LOCAL_COMMIT_TESTED" else 2

if __name__ == "__main__":
    raise SystemExit(main())
