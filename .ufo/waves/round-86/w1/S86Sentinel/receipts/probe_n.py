#!/usr/bin/env python3
"""Probe set N: FLAGFAIL reachability with an honest writer; the REFUSED branch's lost reason."""
import os
import subprocess
import sys

sys.path.insert(0, "/fast/scratch/hyaku/souji-r86/S86Sentinel")
from probe import (S, TOOL, WRITER, ENV, build_fixture, git, move_nest, run_tool, show,
                   k4_rows, fresh, tool_copy)

OUT = []


def emit(s):
    OUT.append(s)
    print(s)


def raw(p):
    return p.stdout.decode("utf-8", "replace")


def n1_flagfail_reachable():
    """Can `git ls-files -v -z :(top)` fail while `git status --porcelain` succeeds?"""
    d = fresh("n1")
    repo, rev, nest, nest1 = build_fixture(d)
    emit("=== N1 can the flag read fail while the status read succeeds? ===")
    # attempt 1: index with a broken extension checksum
    idx = os.path.join(repo, ".git", "index")
    original = open(idx, "rb").read()
    variants = {
        "index extension checksum broken": (lambda b: b[:-20] + b"\x00" * 20),
        "index header count inflated": (lambda b: b[:8] + b"\xff\xff\xff\x7f" + b[12:]),
        "index version 9": (lambda b: b[:4] + b"\x00\x00\x00\x09" + b[8:]),
    }
    for label, mangle in variants.items():
        open(idx, "wb").write(mangle(original))
        st = subprocess.run(["git", "-C", repo, "status", "--porcelain"], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=ENV)
        ls = subprocess.run(["git", "-C", repo, "ls-files", "-v", "-z", ":(top)"], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=ENV)
        emit("  %-34s status rc=%d  ls-files rc=%d  ls stderr=%r"
             % (label, st.returncode, ls.returncode, ls.stderr[:120]))
    open(idx, "wb").write(original)
    emit("  -> with an honest writer the FLAGFAIL branch needs ls-files to fail while status")
    emit("     succeeds; the corruption modes above fail both, so the tool's own status read")
    emit("     reports 'status-failed' first.")


def n2_refused_branch_drops_the_reason():
    """The REFUSED branch keeps only the exit code; the writer's actual reason goes to the
    child's stderr and is never read."""
    d = fresh("n2")
    repo, rev, nest, nest1 = build_fixture(d)
    # a repository whose index cannot be read -> the writer's refuse() path
    idx = os.path.join(repo, ".git", "index")
    original = open(idx, "rb").read()
    open(idx, "wb").write(b"XXXX" + original[4:])
    p = run_tool(TOOL, repo, rev)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("=== N2 the REFUSED branch and the writer's reason ===")
    emit("tool stderr: %r" % p.stderr[:200])
    for r in rows:
        emit("K4ROW %r" % r)
    emit("")
    emit("-> the writer prints 'refused: <reason>' on ITS stderr; the bootstrap catches the")
    emit("   SystemExit and prints only 'REFUSED <exit code>' on stdout; the tool's REFUSED")
    emit("   branch keeps only the code. The reason never reaches the record.")
    open(idx, "wb").write(original)


def n3_subdir_root_paths():
    """With --root inside a subdirectory, the paths the sweep would report are relative to
    the CWD, not to the repository top."""
    d = fresh("n3")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    sub = os.path.join(repo, "sub")
    ls = subprocess.run(["git", "-C", sub, "ls-files", "-v", "-z", ":(top)"], stdout=subprocess.PIPE,
                        env=ENV).stdout
    emit("=== N3 the paths the sweep would name under a subdirectory root ===")
    emit("git -C repo/sub ls-files -v -z :(top) -> %r" % [t for t in ls.split(b"\0") if t])
    emit("-> the paths carry '../' prefixes, i.e. they are relative to the CWD, not the repo")
    emit("   top; the writer's own entry point resolves the toplevel first (r64 C1) and the")
    emit("   K4 bootstrap does not, so it passes --root where the writer expects the toplevel.")
    p = run_tool(TOOL, sub, rev)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("tool with --root=repo/sub: %r" % rows)


if __name__ == "__main__":
    for fn in (n1_flagfail_reachable, n2_refused_branch_drops_the_reason, n3_subdir_root_paths):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-N.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
