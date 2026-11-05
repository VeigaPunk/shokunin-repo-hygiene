#!/usr/bin/env python3
"""Supplementary probe: show a surviving C2 mutant is behaviourally distinct.

Two modes, each building a throwaway repo under --outdir (fixture rule: the
repo is created with `git -C D init`, and `git -C D rev-parse --show-toplevel`
is asserted equal to D before the first commit):

  overwrite-outside : OUT pre-exists OUTSIDE the repo, so the dirty-tree guard
                      cannot mask the overwrite guard.  pristine must refuse
                      (rc=2, bytes unchanged); the mutant overwrites (rc=0).
  worktree-digest   : instrument committed as A, worktree rewritten to B,
                      run with --allow-dirty.  pristine refuses; the mutant
                      writes a receipt whose instrument_sha256 is sha256(B),
                      not the committed blob's sha256(A).

usage: probe_c2.py --tool P --outdir DIR --mode {overwrite-outside,worktree-digest}
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

IDENT = ["-c", "user.name=probe", "-c", "user.email=probe@example.invalid"]
KNOWN = b"KNOWN-BYTES-DO-NOT-OVERWRITE\n"


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo, *IDENT, *args], capture_output=True)
    if p.returncode != 0:
        raise SystemExit("git %s failed: %s" % (args, p.stderr.decode()))
    return p.stdout.decode().strip()


def build(outdir):
    repo = os.path.join(outdir, "repo")
    if os.path.isdir(repo):
        shutil.rmtree(repo)
    os.makedirs(os.path.join(repo, "tools"))
    subprocess.run(["git", "init", "-q", repo], check=True)
    top = git(repo, "rev-parse", "--show-toplevel")
    assert os.path.realpath(top) == os.path.realpath(repo), (top, repo)
    body = b"#!/bin/sh\necho instrument-ok\n"
    with open(os.path.join(repo, "tools", "instrument.sh"), "wb") as f:
        f.write(body)
    git(repo, "add", "tools/instrument.sh")
    git(repo, "commit", "-q", "-m", "instrument")
    return repo, git(repo, "rev-parse", "HEAD"), body


def run(tool, args, outdir, tag):
    argv = [sys.executable, "-B", tool] + args
    p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.stdout.decode("utf-8", "replace")
    with open(os.path.join(outdir, tag + ".txt"), "w", encoding="utf-8") as f:
        f.write("ARGV %s\n%sEXIT=%d\n" % (json.dumps(argv), out, p.returncode))
    return p.returncode, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--mode", required=True)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    repo, rev, blob = build(a.outdir)
    if a.mode == "overwrite-committed":
        # OUT lives INSIDE the root and is COMMITTED, so the tree stays clean and the
        # overwrite guard (not the dirty guard, not the outdir guard) is the only refusal.
        out = os.path.join(repo, "receipt.txt")
        with open(out, "wb") as f:
            f.write(KNOWN)
        git(repo, "add", "receipt.txt")
        git(repo, "commit", "-q", "-m", "receipt")
        args = ["--root", repo, "--rev", rev, "--instrument", "tools/instrument.sh",
                "--out", out, "--max-bytes", "65536", "--", "echo", "ok"]
        rc, _ = run(a.tool, args, a.outdir, "run")
        with open(out, "rb") as f:
            now = f.read()
        print("mode=%s rc=%d out_unchanged=%s out_sha256=%s"
              % (a.mode, rc, now == KNOWN, hashlib.sha256(now).hexdigest()))
        print("DIVERGENCE" if (rc == 2 and now == KNOWN) else
              ("MUTANT-OVERWROTE" if rc == 0 and now != KNOWN else "OTHER"))
    elif a.mode == "worktree-digest":
        wt = os.path.join(repo, "tools", "instrument.sh")
        body_b = b"#!/bin/sh\necho INSTRUMENT-REWRITTEN-IN-WORKTREE\n"
        with open(wt, "wb") as f:
            f.write(body_b)
        out = os.path.join(repo, "receipt.txt")
        args = ["--root", repo, "--rev", rev, "--instrument", "tools/instrument.sh",
                "--out", out, "--max-bytes", "65536", "--allow-dirty", "--", "echo", "ok"]
        rc, _ = run(a.tool, args, a.outdir, "run")
        committed = hashlib.sha256(blob).hexdigest()
        got = None
        if os.path.exists(out):
            for line in open(out, encoding="utf-8").read().splitlines():
                if line.startswith("instrument_sha256="):
                    got = line.split("=", 1)[1]
        print("mode=%s rc=%d committed_sha256=%s receipt_sha256=%s"
              % (a.mode, rc, committed, got))
        print("DIVERGENCE" if (rc == 2 and got is None) else
              ("MUTANT-WRONG-DIGEST" if (rc == 0 and got and got != committed) else "OTHER"))
    elif a.mode == "race-create":
        out = os.path.join(repo, "receipt.txt")
        outdir = os.path.dirname(out)
        args = ["--root", repo, "--rev", rev, "--instrument", "tools/instrument.sh",
                "--out", out, "--max-bytes", "65536", "--", "sleep", "1"]
        argv = [sys.executable, "-B", a.tool] + args
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        time.sleep(0.4)
        racer = b"RACER-BYTES-MUST-SURVIVE\n"
        with open(out, "wb") as f:
            f.write(racer)
        sout = p.communicate()[0].decode("utf-8", "replace")
        with open(out, "rb") as f:
            now = f.read()
        with open(os.path.join(a.outdir, "run.txt"), "w", encoding="utf-8") as f:
            f.write("ARGV %s\n%sEXIT=%d\n" % (json.dumps(argv), sout, p.returncode))
        print("mode=%s rc=%d racer_bytes_survived=%s" % (a.mode, p.returncode, now == racer))
        print("DIVERGENCE" if (p.returncode == 2 and now == racer) else
              ("MUTANT-CLOBBERED" if now != racer else "OTHER"))
    elif a.mode == "stale-temp":
        out = os.path.join(repo, "receipt.txt")
        outdir = os.path.dirname(out)
        stale = os.path.join(outdir, "receipt.txt.deadbeef.tmp")
        with open(stale, "wb") as f:
            f.write(b"STALE-RESIDUE\n")
        args = ["--root", repo, "--rev", rev, "--instrument", "tools/instrument.sh",
                "--out", out, "--max-bytes", "65536", "--allow-dirty", "--", "echo", "ok"]
        rc, _ = run(a.tool, args, a.outdir, "run")
        residue = [f for f in os.listdir(outdir) if f not in ("receipt.txt", "tools", ".git")]
        print("mode=%s rc=%d residue=%s out_written=%s"
              % (a.mode, rc, residue, os.path.exists(out)))
        print("DIVERGENCE" if (rc == 0 and not residue) else
              ("MUTANT-LEFT-RESIDUE" if residue else "OTHER"))
    elif a.mode == "outside-outdir":
        outside = os.path.join(a.outdir, "outside")
        os.makedirs(outside, exist_ok=True)
        out = os.path.join(outside, "receipt.txt")
        args = ["--root", repo, "--rev", rev, "--instrument", "tools/instrument.sh",
                "--out", out, "--max-bytes", "65536", "--", "echo", "ok"]
        rc, _ = run(a.tool, args, a.outdir, "run")
        print("mode=%s rc=%d out_exists=%s" % (a.mode, rc, os.path.exists(out)))
        print("DIVERGENCE" if (rc == 2 and not os.path.exists(out)) else
              ("MUTANT-WROTE-OUTSIDE" if os.path.exists(out) else "OTHER"))
    else:
        raise SystemExit("unknown mode")
    return 0


if __name__ == "__main__":
    sys.exit(main())
