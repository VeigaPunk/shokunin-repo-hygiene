#!/usr/bin/env python3
"""Mutation triplet driver: pristine -> mutant -> restored on one fixture.

Every run installs exact bytes at --dest (the instrument path the fixture
executes), runs the fixture command with {dest}/{work} substituted, records
argv, rc and combined output, then re-hashes --dest.  The triplet is
KILLED only when pristine=PASS and mutant=FAIL and restored=PASS; a mutant
that still passes is SURVIVED; a non-passing pristine/restored is
INCONCLUSIVE (baseline failure, never a kill).

stdlib only. Read-only outside --work and --dest.
"""
import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def install(src, dest):
    tmp = dest + ".install-tmp"
    shutil.copyfile(src, tmp)
    os.chmod(tmp, 0o755)
    os.replace(tmp, dest)


def run(fixture, dest, work, tag, outdir):
    argv = shlex.split(fixture.replace("{dest}", dest).replace("{work}", work))
    p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       cwd=os.path.dirname(outdir) or ".", timeout=1800)
    out = p.stdout.decode("utf-8", "replace")
    with open(os.path.join(outdir, tag + ".txt"), "w", encoding="utf-8") as fh:
        fh.write("ARGV %s\n" % json.dumps(argv))
        fh.write(out)
        fh.write("EXIT=%d\n" % p.returncode)
    return p.returncode, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--pristine", required=True)
    ap.add_argument("--mutant", required=True)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--label", default="mutant")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    os.makedirs(a.work, exist_ok=True)
    rows = []
    for tag, src in (("pristine", a.pristine), ("mutant", a.mutant), ("restored", a.pristine)):
        install(src, a.dest)
        before = sha(a.dest)
        rc, out = run(a.fixture, a.dest, a.work, tag, a.outdir)
        after = sha(a.dest)
        rows.append({"tag": tag, "rc": rc, "sha_before": before, "sha_after": after,
                     "verdict": "PASS" if rc == 0 else "FAIL"})
    pr, mu, re_ = rows
    if pr["verdict"] == "PASS" and mu["verdict"] == "FAIL" and re_["verdict"] == "PASS":
        verdict = "KILLED"
    elif mu["verdict"] == "PASS" and pr["verdict"] == "PASS":
        verdict = "SURVIVED"
    else:
        verdict = "INCONCLUSIVE"
    summary = {"label": a.label, "fixture": a.fixture, "pristine_sha": sha(a.pristine),
               "mutant_sha": sha(a.mutant), "rows": rows, "verdict": verdict}
    with open(os.path.join(a.outdir, "triplet.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    print("%s pristine=%s(%d) mutant=%s(%d) restored=%s(%d) -> %s"
          % (a.label, pr["verdict"], pr["rc"], mu["verdict"], mu["rc"],
             re_["verdict"], re_["rc"], verdict))
    return 0 if verdict in ("KILLED", "SURVIVED") else 2


if __name__ == "__main__":
    sys.exit(main())
