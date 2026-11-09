"""Domain-isolated SOCIAL -> REA Visual Service v1 adapter.

Produces inert PNG-instance-segmentation requests; this is neither a
georeferencing measurement nor an editorial publication authorization.
"""
import json
import re
from pathlib import Path


def build_job(*, job_id, png_path, reference_path=None, min_area=5):
    if (type(job_id) is not str or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,71}", job_id) is None):
        raise ValueError("INVALID_JOB_ID")
    if type(png_path) is not str or not png_path.lower().endswith(".png"):
        raise ValueError("PNG_REQUIRED")
    if (reference_path is not None and
            (type(reference_path) is not str or not reference_path.lower().endswith(".json"))):
        raise ValueError("REFERENCE_JSON_REQUIRED")
    if type(min_area) is not int or not 1 <= min_area <= 100000:
        raise ValueError("INVALID_MIN_AREA")
    return {
        "schema":"rea.visual_job.v1",
        "job_id":job_id,
        "agent":"SOCIAL",
        "problem_type":"instance_segmentation",
        "source_png":png_path,
        "reference_labels_json":reference_path,
        "baseline_parameters":{
            "method":"otsu","threshold":None,"invert":False,
            "min_area":min_area,"connectivity":8,
        },
        "candidate":{"change":"retain_border_only"},
        "evaluation_split":"development",
    }


def write_job(path, **args):
    target=Path(path)
    if target.exists():
        raise ValueError("NO_CLOBBER")
    raw=(json.dumps(build_job(**args),sort_keys=True,indent=2)+"\n").encode("utf8")
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("xb") as f:
        f.write(raw)
    return str(target)


def release_gate(report):
    if (type(report) is not dict or report.get("schema")!="rea.visual_service_report.v1"
            or report.get("agent")!="SOCIAL"):
        raise ValueError("DOMAIN_EVIDENCE_MISMATCH")
    return {
        "REA_VISUAL_REPORT_ACCEPTED":True,
        "AUTOMATIC_PUBLICATION_ALLOWED":False,
        "HUMAN_DOMAIN_REVIEW_REQUIRED":True,
        "SEMANTIC_PUBLICATION_APPROVED":False,
        "PROMOTED_TO_PRODUCTION":False,
    }
