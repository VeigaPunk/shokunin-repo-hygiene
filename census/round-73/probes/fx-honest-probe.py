#!/usr/bin/env python3
"""souji r73 pre-freeze probe for the two honest byte-truth rows (FXh, FXc) of the planned r73 matrix.

Fixtures are built with the FROZEN r72 counter's own builder (build_repo_at, imported). Shapes:
  FXh  honest stale stat: tools/notes.txt bytes unchanged, its mtime moved 10 s forward (git status
       re-reads the file, finds equal content, reports clean).
  FXc  honest check-in conversion: repository-local core.autocrlf=true, tools/notes.txt rewritten
       with CRLF line endings, then `git add tools/notes.txt` (the fixture, not the writer, re-stages it:
       the converted blob is the committed blob, so only the index stat cache changes; without it,
       and also after `update-index --refresh`, git status reports the size change as M). git status
       reports clean; the raw worktree bytes differ from the blob, the converted bytes do not.
For each shape and each writer slot given: the writer verdict (counter judge), `git status
--porcelain` before the run, and the raw-byte comparison of tools/notes.txt against the revision.
Usage: fx-honest-probe.py --counter census/round-72/c1-counter.py --work <dir> <slot.py>...
"""
import argparse
import importlib.util
import os
import subprocess
import sys


def load(path):
    spec = importlib.util.spec_from_file_location("c1counter", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def shape(mod, repo, name):
    notes = os.path.join(repo, "tools", "notes.txt")
    if name == "FXh":
        st = os.stat(notes)
        os.utime(notes, ns=(st.st_atime_ns, st.st_mtime_ns + 10_000_000_000))
    elif name == "FXc":
        r = mod.git_run(repo, ["config", "core.autocrlf", "true"])
        assert r.returncode == 0
        with open(notes, "wb") as f:
            f.write(mod.SEED_NOTES.replace(b"\n", b"\r\n"))
        r = mod.git_run(repo, ["add", "tools/notes.txt"])
        assert r.returncode == 0, r.stderr
    else:
        raise SystemExit(f"unknown shape {name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("slots", nargs="+")
    ns = ap.parse_args()
    mod = load(os.path.abspath(ns.counter))
    work = os.path.abspath(ns.work)
    for si, slot in enumerate(ns.slots):
        for name in ("FXh", "FXc"):
            repo, rev = mod.build_repo_at(os.path.join(work, f"s{si}", name, "repo"))
            shape(mod, repo, name)
            st = mod.git_run(repo, ["status", "--porcelain"]).stdout.decode().strip() or "<clean>"
            blob = mod.git_run(repo, ["cat-file", "blob", f"{rev}:tools/notes.txt"]).stdout
            raw_equal = open(os.path.join(repo, "tools", "notes.txt"), "rb").read() == blob
            out = os.path.join(work, f"s{si}", name, "out", "receipt.txt")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            rc, _, se = mod.run_slot(os.path.abspath(slot), repo, rev, out, False, list(mod.ECHO_ARGV))
            print(f"PROBE slot={os.path.basename(slot)} shape={name} status={st} raw_equal={str(raw_equal).lower()} "
                  f"rc={rc} verdict={mod.judge(rc, out)} stderr={mod.one_line(se) or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
