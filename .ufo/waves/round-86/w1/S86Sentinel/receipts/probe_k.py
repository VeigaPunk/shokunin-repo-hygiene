#!/usr/bin/env python3
"""Probe set K: final verification of the env-route chain and index immutability."""
import hashlib
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


ENVROUTE = {"GIT_CONFIG_PARAMETERS": "'core.sparseCheckout=true'"}
TOOLVIEW = {k: v for k, v in ENV.items() if not k.startswith("GIT_CONFIG_")}


def k1_status_views_differ():
    """Under the env route the tool's status read and the writer's status read disagree."""
    d = fresh("k1")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    with open(os.path.join(repo, "a.txt"), "wb") as f:
        f.write(b"alpha v2 CHANGED\n")

    def st(envkw, label):
        e = dict(ENV)
        e.update(envkw)
        r = subprocess.run(["git", "-C", repo, "-c", "status.showUntrackedFiles=all",
                            "status", "--porcelain"], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, env=e)
        emit("  %-46s rc=%d out=%r" % (label, r.returncode, r.stdout))

    emit("=== K1 the two status views ===")
    st(TOOLVIEW, "TOOL view (GIT_CONFIG_* scrubbed)")
    st(ENVROUTE, "WRITER view (GIT_CONFIG_PARAMETERS kept)")
    emit("-> _truth_refusal SKIPS every path the writer's own status lists, so a path the")
    emit("   tool's status calls clean but the writer's status calls modified is neither")
    emit("   reported by K4 nor re-hashed by the truth check.")


def k2_index_not_mutated():
    """Does the sweep mutate the index? (A read-only instrument must not.)"""
    d = fresh("k2")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "nest")
    idx = os.path.join(repo, ".git", "index")
    before = hashlib.sha256(open(idx, "rb").read()).hexdigest()
    p = run_tool(TOOL, repo, rev, env=ENVROUTE)
    after = hashlib.sha256(open(idx, "rb").read()).hexdigest()
    emit("=== K2 index bytes across a run under the env route ===")
    emit("index sha256 before: %s" % before)
    emit("index sha256 after : %s" % after)
    emit("unchanged: %s" % (before == after))
    emit("-> the tag difference is a READING difference, not index damage: the index still")
    emit("   carries the skip-worktree bit (flags 40004000 in the default view), the writer's")
    emit("   git() just renders the same entry as 'H' under core.sparseCheckout=true.")


def k3_flags_debug():
    d = fresh("k3")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "nest")
    for label, envkw in (("default view", TOOLVIEW), ("writer view (sparseCheckout=true)", ENVROUTE)):
        e = dict(ENV)
        e.update(envkw)
        r = subprocess.run(["git", "-C", repo, "ls-files", "--debug", ":(top)"],
                           stdout=subprocess.PIPE, env=e)
        txt = r.stdout.decode("utf-8", "replace")
        i = txt.find("nest\n")
        seg = txt[i:i + 320] if i >= 0 else "?"
        emit("=== K3 ls-files --debug, %s ===" % label)
        for ln in seg.split("\n")[:9]:
            emit("  " + ln)


def k4_summary_of_the_two_halves():
    """One table: every route, the verdict, and whether the record names the mechanism."""
    emit("=== K4 route summary ===")
    d = fresh("k4")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    routes = [
        ("no env override (control)", {}),
        ("GIT_CONFIG_PARAMETERS='core.sparseCheckout=true'", ENVROUTE),
        ("GIT_CONFIG_COUNT core.sparseCheckout=true",
         {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.sparseCheckout",
          "GIT_CONFIG_VALUE_0": "true"}),
    ]
    for label, envkw in routes:
        p = run_tool(TOOL, repo, rev, env=envkw)
        rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
        emit("%-52s k4_rows=%d %s" % (label, len(rows), rows[0][:120] if rows else "(SILENT)"))


if __name__ == "__main__":
    for fn in (k1_status_views_differ, k2_index_not_mutated, k3_flags_debug, k4_summary_of_the_two_halves):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-K.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
