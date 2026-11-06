#!/usr/bin/env python3
"""souji r73 pre-freeze feasibility probe (QUALITY Q70) for the C2 byte-truth witness.

For every row of the FROZEN r72 matrix this probe rebuilds the row's base-slot fixture with the
FROZEN r72 counter's own builders (imported, not copied), computes the worktree-vs-rev tree
divergence before the slot runs (pre) and after it (post), runs ONE writer slot over the row
exactly as the counter's evaluate() does, and prints one line per row:

  ROW <case> expect=<e> base_expect=<b> verdict=<accept|refuse|error> pre=<n> post=<n> witnessed=<yes|no> first=<path:kind>

Divergence (no git status, no stat cache, no filter): `git ls-tree -r -z <rev>` entries vs the
worktree -- missing path, wrong type, wrong exec bit (100644/100755), different raw bytes, different
symlink target -- plus every worktree file under the repo top that is not in the tree (`.git`
excluded). witnessed=yes iff pre+post > 0.

The question it answers before any r73 instrument byte exists: for which refuse rows does the
reference-weak base writer's acceptance coincide with an observable byte divergence?

Usage: witness-probe.py --counter census/round-72/c1-counter.py --matrix census/round-72/c1-matrix.tsv
         --slot <writer.py> --work <scratch dir> [--rows A,B,...] [--defang <mutants.json> --defang-id D1]
"""
import argparse
import importlib.util
import json
import os
import stat
import subprocess
import sys


def load_counter(path):
    spec = importlib.util.spec_from_file_location("c1counter", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def tree_entries(mod, repo, rev):
    r = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "-z", "--full-tree", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=mod.clean_env(), timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"ls-tree failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    out = {}
    for rec in r.stdout.split(b"\0"):
        if not rec:
            continue
        meta, _, path = rec.partition(b"\t")
        mode, typ, oid = meta.split()
        out[path] = (mode, oid)
    return out


def blob(mod, repo, oid):
    r = subprocess.run(["git", "-C", repo, "cat-file", "blob", oid.decode()], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=mod.clean_env(), timeout=120)
    if r.returncode != 0:
        raise RuntimeError("cat-file failed")
    return r.stdout


def divergence(mod, repo, rev):
    """List of (path, kind) where the worktree differs from rev's tree."""
    ents = tree_entries(mod, repo, rev)
    diffs = []
    for path, (mode, oid) in sorted(ents.items()):
        full = os.path.join(os.fsencode(repo), path)
        try:
            st = os.lstat(full)
        except FileNotFoundError:
            diffs.append((path, "missing"))
            continue
        if mode == b"160000":
            continue
        if mode == b"120000":
            if not stat.S_ISLNK(st.st_mode):
                diffs.append((path, "type"))
            elif os.readlink(full) != blob(mod, repo, oid):
                diffs.append((path, "target"))
            continue
        if not stat.S_ISREG(st.st_mode):
            diffs.append((path, "type"))
            continue
        want_x = mode == b"100755"
        if bool(st.st_mode & 0o111) != want_x:
            diffs.append((path, "mode"))
        with open(full, "rb") as f:
            if f.read() != blob(mod, repo, oid):
                diffs.append((path, "bytes"))
    tracked_dirs = set()
    for path in ents:
        parts = path.split(b"/")
        for i in range(1, len(parts)):
            tracked_dirs.add(b"/".join(parts[:i]))
    top = os.fsencode(repo)
    for dirpath, dirnames, filenames in os.walk(top):
        rel_dir = os.path.relpath(dirpath, top)
        if rel_dir == b".":
            rel_dir = b""
        dirnames[:] = [d for d in dirnames if not (rel_dir == b"" and d == b".git")]
        for name in filenames + [d for d in dirnames if os.path.islink(os.path.join(dirpath, d))]:
            rel = (rel_dir + b"/" + name) if rel_dir else name
            if rel not in ents:
                diffs.append((rel, "untracked"))
    return diffs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True)
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--slot", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--rows")
    ns = ap.parse_args()
    mod = load_counter(os.path.abspath(ns.counter))
    rows, err = mod.load_matrix(os.path.abspath(ns.matrix))
    if rows is None:
        print(f"FATAL matrix {err}")
        return 2
    want = set(ns.rows.split(",")) if ns.rows else None
    slot = os.path.abspath(ns.slot)
    work = os.path.abspath(ns.work)
    n_ref_acc = n_ref_acc_wit = 0
    for letter, expect, klass, base_expect in rows:
        if want and letter not in want:
            continue
        spec = mod.CASE_SPECS[letter]
        try:
            repo, rev = mod.build_case(work, letter, "base", spec)
        except mod.CaseError as exc:
            print(f"ROW {letter} build_error={exc}")
            continue
        pre = divergence(mod, repo, rev)
        rootsub = spec.get("rootsub")
        root = os.path.join(repo, rootsub) if rootsub else repo
        instrument = "instr.sh" if rootsub else "tools/instr.sh"
        cwd = (os.path.dirname(repo) if spec.get("cwd_parent")
               else os.path.join(repo, ".git") if spec.get("cwd_gitdir") else None)
        if spec.get("cwd_parent"):
            instrument = "instr.sh"
        out = os.path.join(work, letter, "base", "out", "receipt.txt")
        rc, _, se = mod.run_slot(slot, repo, rev, out, bool(spec.get("allow_dirty")),
                                 mod.wrapped_argv(spec, repo), root=root, instrument=instrument,
                                 env_extra=mod.case_env(spec, repo), cwd=cwd)
        v = mod.judge(rc, out)
        post = divergence(mod, repo, rev)
        wit = "yes" if (pre or post) else "no"
        first = (pre or post or [(b"-", "-")])[0]
        if expect == "refuse" and v == "accept":
            n_ref_acc += 1
            n_ref_acc_wit += wit == "yes"
        print(f"ROW {letter} expect={expect} base_expect={base_expect} verdict={v} pre={len(pre)} "
              f"post={len(post)} witnessed={wit} first={first[0].decode('utf-8', 'replace')}:{first[1]}",
              flush=True)
    print(f"SUMMARY refuse_rows_accepted={n_ref_acc} witnessed={n_ref_acc_wit} "
          f"unwitnessed={n_ref_acc - n_ref_acc_wit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
