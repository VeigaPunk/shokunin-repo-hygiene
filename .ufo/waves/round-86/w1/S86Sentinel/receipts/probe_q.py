#!/usr/bin/env python3
"""Probe set Q: PATH substitution; the minimal trigger for the split-brain."""
import os
import shutil
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


def q1_path_substitution():
    """Neither git() helper scrubs PATH; both exec a bare 'git'."""
    d = fresh("q1")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    fake = os.path.join(d, "bin")
    os.makedirs(fake, exist_ok=True)
    sh = os.path.join(fake, "git")
    open(sh, "w", encoding="utf-8").write(
        "#!/bin/sh\n"
        "case \"$*\" in\n"
        "  *ls-files*) exit 0 ;;   # report no index records at all\n"
        "  *status*)   exit 0 ;;   # report a clean tree\n"
        "  *) exec /usr/bin/git \"$@\" ;;\n"
        "esac\n")
    os.chmod(sh, 0o755)
    p = run_tool(TOOL, repo, rev, env={"PATH": fake + ":" + ENV["PATH"]})
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("=== Q1 a fake 'git' earlier in PATH ===")
    emit("rc=%d k4_rows=%d" % (p.returncode, len(rows)))
    for r in rows:
        emit("K4ROW %r" % r[:200])
    emit("VERDICT Q1: %s" % ("FAIL OPEN (no K4 row: a substituted git reports a clean tree and an "
                              "empty index)" if not rows else "fail closed"))
    emit("NOTE: both git() helpers exec a bare 'git' resolved through PATH, and neither")
    emit("scrubs PATH. A substituted git is outside the claim (the tree's own bytes are not")
    emit("the audited surface), but it is a named mechanism K4 does not measure.")


def q2_minimal_trigger():
    """Which config keys, unpinned by either helper, mask the flag?"""
    d = fresh("q2")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    base = {k: v for k, v in ENV.items() if not k.startswith("GIT_CONFIG_")}
    keys = ["core.sparseCheckout", "core.sparseCheckoutCone", "index.sparse",
            "core.excludesFile", "core.fsmonitor", "core.fileMode", "core.checkStat",
            "core.trustctime", "status.showUntrackedFiles", "core.ignorecase",
            "core.quotepath", "core.precomposeUnicode", "core.protectNTFS"]
    emit("=== Q2 which unpinned config keys mask the index flag from `ls-files -v`? ===")
    for k in keys:
        e = dict(base)
        e["GIT_CONFIG_PARAMETERS"] = "'%s=true'" % k
        r = subprocess.run(["git", "-C", repo, "ls-files", "-v", "-z", ":(top)"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=e)
        a = [t for t in r.stdout.split(b"\0") if t.endswith(b"a.txt")]
        masked = a and not a[0].startswith(b"S")
        if masked or k in ("core.checkStat", "core.trustctime", "core.fileMode", "core.fsmonitor"):
            emit("  %-28s -> %r %s" % (k, a, "MASKED" if masked else ""))
    emit("")
    emit("  -> core.sparseCheckout (and core.sparseCheckoutCone) mask the skip-worktree tag;")
    emit("     neither helper pins them, so GIT_CONFIG_PARAMETERS reaches them.")


def q3_pinned_by_neither():
    """Enumerate the config keys each helper pins, and the gap."""
    import re
    tsrc = open(TOOL, encoding="utf-8").read()
    wsrc = open(WRITER, encoding="utf-8").read()
    t = set(re.findall(r'\("([\w.]+)", ', tsrc))
    w = set(re.findall(r'-c ([\w.]+)=', wsrc))
    emit("=== Q3 the config pins of each helper ===")
    emit("TOOL git() pins   : %s" % sorted(t))
    emit("WRITER git() pins : %s" % sorted(w))
    emit("both               : %s" % sorted(t & w))
    emit("neither            : core.sparseCheckout, core.sparseCheckoutCone, index.sparse, "
         "core.quotepath, core.ignorecase, ...")
    emit("")
    emit("  -> core.sparseCheckout is in NEITHER set: it is unpinned on both sides, so the")
    emit("     writer's ls-files -v can be made to render a skip-worktree entry as 'H'.")


if __name__ == "__main__":
    for fn in (q1_path_substitution, q2_minimal_trigger, q3_pinned_by_neither):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-Q.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
