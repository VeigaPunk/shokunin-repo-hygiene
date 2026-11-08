#!/usr/bin/env python3
"""Probe set E: environment routes that reach the writer's git() inside the r86 sweep."""
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


def e_case(label, env, conceal="skip-worktree", row=None):
    d = fresh("e_" + label.replace("/", "_").replace("=", "_"))
    repo, rev, nest, nest1 = build_fixture(d)
    if conceal == "skip-worktree":
        git(repo, "update-index", "--skip-worktree", "a.txt")
    elif conceal == "gitlink":
        move_nest(nest)
        git(repo, "update-index", "--skip-worktree", "nest")
    p = run_tool(TOOL, repo, rev, env=env)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("=== E %s ===" % label)
    emit("env: %r" % env)
    emit("rc=%d k4_rows=%d" % (p.returncode, len(rows)))
    for r in rows:
        emit("K4ROW %r" % r)
    if p.stderr.strip():
        emit("stderr: %r" % p.stderr[:200])
    emit("VERDICT E %s: %s" % (label, "FAIL OPEN (no K4 row: the concealment is unreported)" if not rows
                              else "fail closed (%d row(s))" % len(rows)))
    return rows


def e1_git_config_parameters_core_bare():
    """GIT_CONFIG_PARAMETERS reaches the WRITER's git() (the writer's git() does not scrub it;
    only the writer's entry point refuses it). core.bare changes what ls-files sees."""
    return e_case("GIT_CONFIG_PARAMETERS/core.bare",
                  {"GIT_CONFIG_PARAMETERS": "'core.bare=true'"})


def e2_git_config_count_core_bare():
    return e_case("GIT_CONFIG_COUNT/core.bare",
                  {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.bare", "GIT_CONFIG_VALUE_0": "true"})


def e3_sparse_checkout():
    return e_case("GIT_CONFIG_PARAMETERS/core.sparseCheckout",
                  {"GIT_CONFIG_PARAMETERS": "'core.sparseCheckout=true'"})


def e4_ignorecase():
    return e_case("GIT_CONFIG_PARAMETERS/core.ignorecase",
                  {"GIT_CONFIG_PARAMETERS": "'core.ignorecase=true'"})


def e5_object_directory_gitlink():
    """GIT_OBJECT_DIRECTORY with the gitlink concealment: the class the repair exists for."""
    d = fresh("e5")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    alt = os.path.join(d, "empty-objects")
    os.makedirs(alt, exist_ok=True)
    p = run_tool(TOOL, repo, rev, env={"GIT_OBJECT_DIRECTORY": alt})
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("=== E5 GIT_OBJECT_DIRECTORY with a gitlink concealment ===")
    emit("rc=%d k4_rows=%d" % (p.returncode, len(rows)))
    for r in rows:
        emit("K4ROW %r" % r)
    emit("VERDICT E5: %s" % ("FAIL OPEN" if not rows else "fail closed"))


def e6_tool_git_reads_index_file():
    """Does the TOOL's own git() honour GIT_INDEX_FILE? (It scrubs GIT_CONFIG_* only.)"""
    d = fresh("e6")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    alt = os.path.join(d, "alt-index")
    shutil.copyfile(os.path.join(repo, ".git", "index"), alt)
    e = dict(ENV)
    e["GIT_INDEX_FILE"] = alt
    git(repo, "update-index", "--no-skip-worktree", "a.txt", env=e, check=False)
    st = subprocess.run(["git", "-C", repo, "status", "--porcelain"], stdout=subprocess.PIPE, env=e)
    emit("=== E6 the tool's own status read follows GIT_INDEX_FILE ===")
    emit("status under the doctored index: rc=%d out=%r" % (st.returncode, st.stdout))
    emit("VERDICT E6: the tool's own git() does NOT scrub GIT_INDEX_FILE, so the status read and "
         "the writer's flag sweep can be pointed at DIFFERENT index views by one env var")


def e7_orphan_after_timeout():
    """Does the tool clean up the writer's git children when the bootstrap times out?"""
    d = fresh("e7")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    td = os.path.join(d, "tool")
    os.makedirs(td, exist_ok=True)
    tsrc = open(TOOL, encoding="utf-8").read()
    patched = tsrc.replace("timeout=600", "timeout=3")
    t = os.path.join(td, "souji-record-agreement.py")
    open(t, "w", encoding="utf-8").write(patched)
    os.chmod(t, 0o755)
    wsrc = open(WRITER, encoding="utf-8").read()
    # the writer's own git() hangs: it spawns no child, it sleeps inside the call
    wpatched = wsrc.replace(
        "    return subprocess.run([\"git\", \"-C\", root,",
        "    import time as _t; _t.sleep(120)\n    return subprocess.run([\"git\", \"-C\", root,", 1)
    assert wpatched != wsrc
    w = os.path.join(td, "souji-receipt-write.py")
    open(w, "w", encoding="utf-8").write(wpatched)
    os.chmod(w, 0o755)
    p = run_tool(t, repo, rev, timeout=90)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("=== E7 process cleanup after a bootstrap timeout ===")
    emit("rc=%d k4_rows=%d" % (p.returncode, len(rows)))
    for r in rows:
        emit("K4ROW %r" % (r[:160] + "..."))
    # look for a leftover python child of ours
    ps = subprocess.run(["ps", "-eo", "pid,ppid,etimes,args"], stdout=subprocess.PIPE)
    leftover = [ln for ln in ps.stdout.decode("utf-8", "replace").split("\n")
                if "souji-receipt-write" in ln or ("-I" in ln and "souji" in ln)]
    emit("leftover writer processes: %r" % leftover)
    emit("VERDICT E7: %s" % ("the timeout kills the direct child only" if not leftover
                              else "a writer process survived the timeout"))


if __name__ == "__main__":
    for fn in (e1_git_config_parameters_core_bare, e2_git_config_count_core_bare,
               e3_sparse_checkout, e4_ignorecase, e5_object_directory_gitlink,
               e6_tool_git_reads_index_file, e7_orphan_after_timeout):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-E.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
