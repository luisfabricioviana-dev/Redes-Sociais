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

def _has_symlink_component(root: Path, relative: str) -> bool:
    """Reject external or internal link indirection concealed by Git index flags."""
    current = root
    for component in Path(relative).parts:
        current = current / component
        if current.is_symlink():
            return True
    return False

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
        # Do not read external files through concealed symlinks even for hashing.
        if _has_symlink_component(root, rel) or not target.is_file():
            missing.append(rel)
        else:
            files[rel] = hashlib.sha256(target.read_bytes()).hexdigest()
    # Compare each required checkout file with the blob stored in HEAD.
    # git status alone is not sufficient: assume-unchanged/skip-worktree
    # can conceal content drift while still reporting a clean repository.
    # Bind the receipt to the entire tracked checkout. Checking only REQUIRED
    # leaves an integrity gap for CI, documentation and other committed files.
    tracked_result = subprocess.run(["git", "ls-files", "-z"], cwd=root,
                                    capture_output=True, check=False)
    tracked = ([entry.decode("utf-8", "surrogateescape")
                for entry in tracked_result.stdout.split(b"\0") if entry]
               if tracked_result.returncode == 0 else [])
    # unittest discovers ignored Python files even when git status is clean.
    # Such files must never run as part of an exact-commit receipt.
    discovered_tests = [test.relative_to(root).as_posix()
                        for test in (root / "tests").rglob("test_rea_*.py")]
    tracked_set = set(tracked)
    untracked_discovered_tests = sorted(path for path in discovered_tests
                                        if path not in tracked_set)
    commit_content_mismatches = []
    if head and len(head) == 40:
        for rel in tracked:
            if _has_symlink_component(root, rel):
                if rel not in commit_content_mismatches:
                    commit_content_mismatches.append(rel)
                continue
            expected = _run(["git", "rev-parse", f"HEAD:{rel}"], root)
            actual = _run(["git", "hash-object", f"--path={rel}", rel], root)
            if (expected.returncode != 0 or actual.returncode != 0
                    or expected.stdout.strip() != actual.stdout.strip()):
                commit_content_mismatches.append(rel)
    # Never execute test code from a checkout that has already failed preflight.
    # A post-run UNVERIFIED receipt cannot undo execution of modified code.
    preflight_ok = bool(head and len(head) == 40 and clean and not missing
                        and tracked_result.returncode == 0 and bool(tracked)
                        and not commit_content_mismatches and not untracked_discovered_tests)
    run = (_run([sys.executable, "-B", "-m", "unittest", "discover", "-s",
                 "tests", "-p", "test_rea_*py", "-v"], root)
           if preflight_ok else None)
    # Validate again after tests. A passing suite is not sufficient if
    # executing it mutates the exact input tree being certified.
    post_status = _run(["git", "status", "--porcelain", "--untracked-files=normal"], root)
    clean_after_tests = post_status.returncode == 0 and not post_status.stdout.strip()
    if head and len(head) == 40:
        for rel in tracked:
            if _has_symlink_component(root, rel):
                if rel not in commit_content_mismatches:
                    commit_content_mismatches.append(rel)
                continue
            expected = _run(["git", "rev-parse", f"HEAD:{rel}"], root)
            actual = _run(["git", "hash-object", f"--path={rel}", rel], root)
            if (expected.returncode != 0 or actual.returncode != 0
                    or expected.stdout.strip() != actual.stdout.strip()):
                if rel not in commit_content_mismatches:
                    commit_content_mismatches.append(rel)
    tests_pass = run is not None and run.returncode == 0
    verified = bool(head and len(head) == 40 and clean and clean_after_tests and not missing and tracked_result.returncode == 0 and bool(tracked) and not commit_content_mismatches and not untracked_discovered_tests and tests_pass)
    report = {
        "contract": "REA_SOCIAL_OFFLINE_VERIFICATION_v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": head,
        "git_clean": clean,
        "git_clean_after_tests": clean_after_tests,
        "git_status_exit_code": status.returncode,
        "missing_files": missing,
        "untracked_discovered_tests": untracked_discovered_tests,
        "tracked_file_count": len(tracked),
        "tracked_listing_exit_code": tracked_result.returncode,
        "commit_content_mismatches": commit_content_mismatches,
        "input_sha256": files,
        "python": sys.version.split()[0],
        "test_command": "python -B -m unittest discover -s tests -p 'test_rea_*py' -v",
        "test_exit_code": run.returncode if run is not None else None,
        "tests_executed": run is not None,
        "test_skip_reason": None if preflight_ok else "PREFLIGHT_INTEGRITY_FAILED",
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
