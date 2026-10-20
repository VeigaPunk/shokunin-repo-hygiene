#!/usr/bin/env python3
"""seat-audit-replay.py — replay the seat audit on a pinned transcript bundle
and bind every input digest into one output record (round 17, C2/D4).

Verifies census/round-16/transcripts/MANIFEST.sha256 with
census/round-17/transcript-manifest.py --check, then runs
tools/souji-seat-audit.py (imported as a module) on the bundled w1 and w2
transcripts against the matching .ufo/waves/round-16/w{1,2}-spec.json.

Usage:
    seat-audit-replay.py --lane LANE --transcripts DIR --specs W1.json:W2.json \
        --auditor PATH --output OUT.json

--output is written atomically and an existing file is never overwritten.
The record binds auditor/spec/manifest sha256s, the manifest check output,
per-wave summaries and the full per-seat violation rows.

Exit: 0 record written; 1 audit produced major violations (record still
written); 2 usage, unreadable input, or manifest check failed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--transcripts", required=True,
                    help="bundle dir containing MANIFEST.sha256 and w1/, w2/")
    ap.add_argument("--specs", required=True,
                    help="w1 spec : w2 spec, colon-separated")
    ap.add_argument("--auditor", required=True, help="tools/souji-seat-audit.py")
    ap.add_argument("--auditor-rev", default="unbound",
                    help="git rev of the audited auditor bytes, for binding")
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    # Importing the auditor must not leave a lane-side bytecode cache.
    sys.dont_write_bytecode = True

    lane = a.lane.rstrip("/")
    tdir = Path(a.transcripts)
    auditor_path = Path(a.auditor)
    spec_paths = [Path(p) for p in a.specs.split(":")]
    out = Path(a.output)
    waves = ["w1", "w2"]
    if len(spec_paths) != 2:
        print("seat-audit-replay: --specs must be w1.json:w2.json", file=sys.stderr)
        return 2
    if out.exists():
        print(f"seat-audit-replay: refusing to overwrite {out}", file=sys.stderr)
        return 2

    manifest = tdir / "MANIFEST.sha256"
    manifest_tool = Path(__file__).with_name("transcript-manifest.py")
    rec = {
        "tool": "seat-audit-replay.py",
        "argv": sys.argv,
        "lane": lane,
        "fleet": str(Path(lane).parent),
        "auditor": {"path": str(auditor_path), "sha256": sha256_file(auditor_path),
                    "git_rev": a.auditor_rev},
        "tool_sha256": sha256_file(Path(__file__)),
        "python": sys.version.split()[0],
        "transcripts_dir": str(tdir),
        "manifest": {"path": str(manifest), "sha256": sha256_file(manifest)},
        "manifest_check": {},
        "specs": {},
        "waves": {},
    }

    # 1. Verify the transcript bundle before auditing it.
    try:
        p = subprocess.run(
            [sys.executable, str(manifest_tool), "--check", str(tdir)],
            capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"seat-audit-replay: manifest check could not run: {exc}", file=sys.stderr)
        return 2
    rec["manifest_check"] = {
        "tool": str(manifest_tool), "tool_sha256": sha256_file(manifest_tool),
        "exit": p.returncode,
        "stdout": p.stdout.strip(), "stderr": p.stderr.strip(),
    }
    if p.returncode != 0:
        print(f"seat-audit-replay: manifest check failed:\n{p.stdout}{p.stderr}",
              file=sys.stderr)
        return 2

    try:
        auditor = load_module(auditor_path, "souji_seat_audit")
        for wave, sp in zip(waves, spec_paths):
            wdir = tdir / wave
            result = auditor.run(sp, wdir, lane)
            rec["specs"][wave] = {"path": str(sp), "sha256": sha256_file(sp)}
            rec["waves"][wave] = {
                "transcripts": wdir.name,
                "transcript_count": sum(1 for f in wdir.iterdir() if f.is_file()),
                "summary": result["summary"],
                "missing_transcripts": result["missing_transcripts"],
                "seats": {
                    name: {"role": s["role"], "calls": s["calls"],
                           "violations": s["violations"]}
                    for name, s in result["seats"].items()
                },
            }
    except (OSError, ValueError, KeyError, AttributeError) as exc:
        print(f"seat-audit-replay: could not evaluate: {exc}", file=sys.stderr)
        return 2

    majors = sum(w["summary"]["major"] for w in rec["waves"].values())
    body = json.dumps(rec, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    # Atomic write via tempfile in the destination directory.
    fd, tmp = tempfile.mkstemp(dir=str(out.parent), prefix=out.name + ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(body)
        os.replace(tmp, out)
    except OSError:
        os.unlink(tmp)
        raise
    print(f"seat-audit-replay: wrote {out} sha256={hashlib.sha256(body.encode()).hexdigest()}")
    for wave in waves:
        s = rec["waves"][wave]["summary"]
        print(f"SUMMARY {wave}\tseats={s['seats_audited']}\tcalls={s['calls']}"
              f"\tmajor={s['major']}\tminor={s['minor']}\tmissing={len(rec['waves'][wave]['missing_transcripts'])}")
    return 1 if majors else 0


if __name__ == "__main__":
    sys.exit(main())
