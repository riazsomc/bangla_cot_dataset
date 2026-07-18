#!/usr/bin/env python3
"""Validator for the Bangla CoT dataset (JSONL).

Usage: python3 validate_cot.py cot_bangla.jsonl
Exit code 0 = clean, 1 = errors found. Run before every commit.
"""
import json, re, sys
from collections import Counter

DOMAINS = {"public_health", "law", "math", "civics", "linguistics",
           "general_science", "daily_reasoning", "document_reasoning",
           "misinformation_rebuttal", "literature"}
REGISTERS = {"cholito", "sadhu", "mixed"}
STEP_TYPES = {"recall", "deduce", "calculate", "eliminate", "verify"}
ANSWER_TYPES = {"numeric", "mcq", "short_text", "yes_no"}
STATUSES = {"active", "retired"}
ID_RE = re.compile(r"^bn-cot-\d{6}$")
REQUIRED = ["id", "domain", "register", "difficulty", "question",
            "reasoning_steps", "final_answer", "answer_type",
            "wrong_paths", "author", "license", "created"]

def err(lineno, rid, msg, errors):
    errors.append(f"  line {lineno} [{rid or '?'}]: {msg}")

def validate(path):
    errors, warnings = [], []
    ids = Counter()
    n = 0
    for lineno, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.strip()
        if not line:
            continue
        n += 1
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as e:
            err(lineno, None, f"invalid JSON: {e}", errors)
            continue
        rid = rec.get("id")
        for k in REQUIRED:
            if k not in rec:
                err(lineno, rid, f"missing field '{k}'", errors)
        if rid:
            ids[rid] += 1
            if not ID_RE.match(rid):
                err(lineno, rid, "id must match bn-cot-NNNNNN", errors)
        if rec.get("domain") not in DOMAINS:
            err(lineno, rid, f"unknown domain '{rec.get('domain')}'", errors)
        if rec.get("register") not in REGISTERS:
            err(lineno, rid, f"unknown register '{rec.get('register')}'", errors)
        d = rec.get("difficulty")
        if not isinstance(d, int) or not 1 <= d <= 5:
            err(lineno, rid, "difficulty must be int 1-5", errors)
        if rec.get("answer_type") not in ANSWER_TYPES:
            err(lineno, rid, f"unknown answer_type '{rec.get('answer_type')}'", errors)
        steps = rec.get("reasoning_steps", [])
        if not isinstance(steps, list) or len(steps) < 2:
            err(lineno, rid, "need >=2 reasoning_steps", errors)
        else:
            for i, s in enumerate(steps, 1):
                if s.get("step") != i:
                    err(lineno, rid, f"step numbering broken at position {i}", errors)
                if s.get("type") not in STEP_TYPES:
                    err(lineno, rid, f"step {i}: unknown type '{s.get('type')}'", errors)
                if not s.get("text", "").strip():
                    err(lineno, rid, f"step {i}: empty text", errors)
            if not any(s.get("type") == "verify" for s in steps):
                warnings.append(f"  line {lineno} [{rid}]: no 'verify' step (recommended)")
        wps = rec.get("wrong_paths", [])
        if not isinstance(wps, list) or len(wps) < 1:
            err(lineno, rid, "need >=1 wrong_path", errors)
        else:
            for j, w in enumerate(wps, 1):
                if not w.get("answer", "").strip() or not w.get("error", "").strip():
                    err(lineno, rid, f"wrong_path {j}: answer/error missing", errors)
        if not rec.get("final_answer", "").strip():
            err(lineno, rid, "empty final_answer", errors)
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(rec.get("created", ""))):
            err(lineno, rid, "created must be YYYY-MM-DD", errors)
        if "status" in rec and rec["status"] not in STATUSES:
            err(lineno, rid, f"unknown status '{rec['status']}'", errors)
    for rid, c in ids.items():
        if c > 1:
            errors.append(f"  duplicate id: {rid} ({c}x)")
    print(f"{n} records checked.")
    if warnings:
        print(f"{len(warnings)} warnings:")
        print("\n".join(warnings))
    if errors:
        print(f"{len(errors)} ERRORS:")
        print("\n".join(errors))
        return 1
    print("All records valid.")
    return 0

if __name__ == "__main__":
    sys.exit(validate(sys.argv[1] if len(sys.argv) > 1 else "cot_bangla.jsonl"))
