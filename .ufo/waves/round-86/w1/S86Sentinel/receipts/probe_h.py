#!/usr/bin/env python3
"""Probe set H: the core.sparseCheckout tag-masking mechanism, in-tree and via env."""
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


def h1_mechanism():
    d = fresh("h1")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    base = {k: v for k, v in ENV.items() if not k.startswith("GIT_CONFIG_")}
    def go(label, extra):
        r = subprocess.run(["git", "-C", repo, *extra, "ls-files", "-v", "-z", ":(top)"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=base)
        a = [t for t in r.stdout.split(b"\0") if t.endswith(b"a.txt")]
        emit("%-40s -> %r" % (label, a))
    go("default", ())
    go("-c core.sparseCheckout=true", ("-c", "core.sparseCheckout=true"))
    go("-c core.sparseCheckout=1", ("-c", "core.sparseCheckout=1"))
    go("-c index.sparse=true", ("-c", "index.sparse=true"))
    go("-c core.sparseCheckout=true -c core.sparseCheckoutCone=true",
       ("-c", "core.sparseCheckout=true", "-c", "core.sparseCheckoutCone=true"))
    emit("")
    emit("--- is the skip-worktree bit still in the index? (ls-files --debug) ---")
    for label, extra in (("default", ()), ("sparseCheckout=true", ("-c", "core.sparseCheckout=true"))):
        r = subprocess.run(["git", "-C", repo, *extra, "ls-files", "--debug", ":(top)"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=base)
        txt = r.stdout.decode("utf-8", "replace")
        i = txt.find("a.txt")
        emit("%s:\n%s" % (label, txt[i:i + 400] if i >= 0 else txt[:200]))


def h2_in_tree_config():
    """core.sparseCheckout=true written into the repository's own .git/config: the attack
    needs no environment variable at all."""
    d = fresh("h2")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    git(repo, "config", "core.sparseCheckout", "true")
    p = run_tool(TOOL, repo, rev)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("=== H2 core.sparseCheckout=true in the repository's own .git/config ===")
    emit("the gitlink concealment (KG1 shape) is present; the repo config masks the index flag")
    emit("rc=%d k4_rows=%d" % (p.returncode, len(rows)))
    for r in rows:
        emit("K4ROW %r" % r)
    emit("VERDICT H2: %s" % ("FAIL OPEN (the KG1-shaped concealment is unreported; the repair's "
                              "own sweep sees H)" if not rows else "fail closed"))
    # control: same fixture without the config
    d2 = fresh("h2b")
    repo2, rev2, nest2, nest1b = build_fixture(d2)
    move_nest(nest2)
    git(repo2, "update-index", "--skip-worktree", "nest")
    p2 = run_tool(TOOL, repo2, rev2)
    rows2 = [ln for ln in raw(p2).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("control (no repo config): k4_rows=%d" % len(rows2))
    for r in rows2:
        emit("K4ROW %r" % r)


def h3_does_the_truth_check_also_see_it():
    """Under core.sparseCheckout=true, does the truth check (_truth_refusal) also change view?"""
    d = fresh("h3")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    with open(os.path.join(repo, "a.txt"), "wb") as f:
        f.write(b"alpha v2 CHANGED\n")
    p_env = run_tool(TOOL, repo, rev, env={"GIT_CONFIG_PARAMETERS": "'core.sparseCheckout=true'"})
    git(repo, "config", "core.sparseCheckout", "true")
    p_cfg = run_tool(TOOL, repo, rev)
    for label, p in (("env route", p_env), ("in-tree config route", p_cfg)):
        rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
        emit("%-24s k4_rows=%d %r" % (label, len(rows), rows))


def h4_flagfail_real_git_stderr():
    """Can a repository make the flag read fail with attacker-chosen stderr? A corrupt index
    makes `git ls-files -v` fail; the FLAGFAIL branch embeds that stderr RAW (no escaping)."""
    d = fresh("h4")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    with open(os.path.join(repo, ".git", "index"), "r+b") as f:
        f.seek(0)
        f.write(b"XXXX")  # corrupt the index signature
    e = dict(ENV)
    r = subprocess.run(["git", "-C", repo, "ls-files", "-v", "-z", ":(top)"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=e)
    emit("=== H4 a corrupt index makes the flag read fail ===")
    emit("git ls-files -v rc=%d stderr=%r" % (r.returncode, r.stderr))
    p = run_tool(TOOL, repo, rev)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("rc=%d k4_rows=%d" % (p.returncode, len(rows)))
    for rr in rows:
        emit("K4ROW %r" % rr)
    emit("physically-split detail: %s" % any("\n" in rr for rr in rows))
    emit("VERDICT H4: %s" % ("a row is emitted (fail closed) but the detail field is not escaped"
                              if rows else "FAIL OPEN"))


if __name__ == "__main__":
    for fn in (h1_mechanism, h2_in_tree_config, h3_does_the_truth_check_also_see_it,
               h4_flagfail_real_git_stderr):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-H.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
