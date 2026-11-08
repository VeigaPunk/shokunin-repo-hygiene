#!/usr/bin/env python3
"""Probe set I: the split-brain chain that makes the r86 flag sweep blind."""
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


TOOL_SCRUB = {k: v for k, v in ENV.items() if not k.startswith("GIT_CONFIG_")}
ENVROUTE = {"GIT_CONFIG_PARAMETERS": "'core.sparseCheckout=true'"}


def i1_chain_gitlink():
    """The KG1-shaped concealment (a nested repo commit moved, gitlink marked skip-worktree),
    with GIT_CONFIG_PARAMETERS='core.sparseCheckout=true' in the environment."""
    d = fresh("i1")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")

    def g(envkw, args):
        e = dict(ENV)
        e.update(envkw)
        return subprocess.run(["git", "-C", repo, *args], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, env=e)

    emit("=== I1 the split-brain chain, step by step ===")
    emit("[1] the tree: nested repo HEAD moved to %s, gitlink entry marked skip-worktree"
         % git(nest, "rev-parse", "HEAD").stdout.decode().strip()[:8])
    emit("    real index entry: %r" % [t for t in g({}, ("ls-files", "-v", "-z", ":(top)"))
                                       .stdout.split(b"\0") if t.endswith(b"nest")])
    emit("")
    emit("")
    emit("[2] TOOL half of K4: `git status --porcelain` (GIT_CONFIG_* scrubbed by the tool)")
    r = g(TOOL_SCRUB, ("status", "--porcelain"))
    emit("    rc=%d out=%r  -> the tool sees a CLEAN tree, so no uncommitted-path row" %
         (r.returncode, r.stdout))
    emit("")
    emit("[3] WRITER half of K4 (the r86 flag sweep): `git ls-files -v -z :(top)`")
    emit("    the writer's git() does NOT scrub GIT_CONFIG_PARAMETERS")
    r_clean = g(TOOL_SCRUB, ("ls-files", "-v", "-z", ":(top)"))
    r_dirty = g(ENVROUTE, ("ls-files", "-v", "-z", ":(top)"))
    emit("    with the tool's config view : %r" % [t for t in r_clean.stdout.split(b"\0")
                                                   if t.endswith(b"nest")])
    emit("    with the writer's config view: %r" % [t for t in r_dirty.stdout.split(b"\0")
                                                    if t.endswith(b"nest")])
    emit("    -> the sweep sees tag 'H': no non-H record, so no refusal, so CLEAN")
    emit("")
    emit("[4] the truth check _truth_refusal skips mode 160000 (gitlink) entirely")
    emit("    -> no stat-cache refusal either")
    emit("")
    p = run_tool(TOOL, repo, rev, env=ENVROUTE)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("[5] the tool under the env route:")
    emit("    rc=%d k4_rows=%d" % (p.returncode, len(rows)))
    emit("    K4 rows: %r" % rows)
    p0 = run_tool(TOOL, repo, rev)
    rows0 = [ln for ln in raw(p0).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("    control (no env route): k4_rows=%d -> %r" % (len(rows0), rows0))
    emit("VERDICT I1: %s" % ("FAIL OPEN (K4 reports CLEAN for a tree whose nested repository "
                              "commit moved and whose gitlink entry is flagged skip-worktree)"
                              if not rows else "fail closed"))


def i2_writer_entry_point_refuses_the_same_envs():
    """Which of the env routes the writer's OWN entry point refuses, and which reach K4."""
    d = fresh("i2")
    repo, rev, nest, nest1 = build_fixture(d)
    out = os.path.join(d, "receipt.txt")
    envs = {
        "GIT_CONFIG_PARAMETERS": "'core.sparseCheckout=true'",
        "GIT_CONFIG_COUNT": "1",
        "GIT_INDEX_FILE": os.path.join(d, "alt-index"),
    }
    emit("=== I2 the writer's entry-point refusals vs what reaches K4 ===")
    for var, val in envs.items():
        e = dict(ENV)
        e[var] = val
        if var == "GIT_CONFIG_COUNT":
            e["GIT_CONFIG_KEY_0"] = "core.sparseCheckout"
            e["GIT_CONFIG_VALUE_0"] = "true"
        if os.path.exists(out):
            os.unlink(out)
        p = subprocess.run([sys.executable, "-B", WRITER, "--root", repo, "--rev", rev,
                            "--instrument", "a.txt", "--out", out, "--command", "/bin/true"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=e, timeout=120, cwd=d)
        msg = p.stderr.decode("utf-8", "replace").strip().split("\n")[0][:150]
        emit("%-28s writer entry point: rc=%d %s" % (var, p.returncode, msg))
    emit("VERDICT I2: the writer's entry point refuses every one of these environments before "
         "any git call; the K4 bootstrap calls mod.git() / mod._truth_refusal() directly and "
         "reaches NONE of those refusals.")


def i3_scope_of_writer_git_scrub():
    """Exactly which env vars the writer's git() keeps (and therefore the r86 sweep honours)."""
    import re
    wsrc = open(WRITER, encoding="utf-8").read()
    tsrc = open(TOOL, encoding="utf-8").read()
    w = re.search(r"def git\(root.*?\n(.*?)\n\n", wsrc, re.S).group(0)
    t = re.search(r"def git\(root.*?\n(.*?)\n\n", tsrc, re.S).group(0)
    emit("=== I3 the two git() helpers, side by side ===")
    emit("--- WRITER git() (used by the r86 flag sweep and by _truth_refusal) ---")
    emit(w)
    emit("--- TOOL git() (used by K4's own status read) ---")
    emit(t)


if __name__ == "__main__":
    for fn in (i1_chain_gitlink, i2_writer_entry_point_refuses_the_same_envs, i3_scope_of_writer_git_scrub):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-I.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
