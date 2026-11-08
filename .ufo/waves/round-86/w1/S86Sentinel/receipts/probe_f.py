#!/usr/bin/env python3
"""Probe set F: the config-route fail-open, and the writer's own refusal of the same env."""
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


def f1_config_route_skipworktree():
    """GIT_CONFIG_PARAMETERS='core.sparseCheckout=true' masks the skip-worktree tag from
    `git ls-files -v`, so the r86 sweep sees nothing to refuse."""
    d = fresh("f1")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    with open(os.path.join(repo, "a.txt"), "wb") as f:
        f.write(b"alpha v2 CHANGED\n")
    forge = None
    e = {"GIT_CONFIG_PARAMETERS": "'core.sparseCheckout=true'"}
    p = run_tool(TOOL, repo, rev, env=e)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("=== F1 GIT_CONFIG_PARAMETERS masks the index flag the sweep reads ===")
    emit("repo index: a.txt carries skip-worktree; worktree bytes changed")
    emit("rc=%d k4_rows=%d" % (p.returncode, len(rows)))
    for r in rows:
        emit("K4ROW %r" % r)
    emit("VERDICT F1: %s" % ("FAIL OPEN (K4 emitted no row; the concealment is unreported)"
                              if not rows else "fail closed"))


def f2_config_route_gitlink():
    """Same route against the gitlink class the repair exists for (KG1)."""
    d = fresh("f2")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    e = {"GIT_CONFIG_PARAMETERS": "'core.sparseCheckout=true'"}
    p = run_tool(TOOL, repo, rev, env=e)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("=== F2 the same route against the KG1 gitlink concealment ===")
    emit("rc=%d k4_rows=%d" % (p.returncode, len(rows)))
    for r in rows:
        emit("K4ROW %r" % r)
    emit("VERDICT F2: %s" % ("FAIL OPEN (KG1 concealment unreported)" if not rows else "fail closed"))
    p2 = run_tool(TOOL, repo, rev)
    rows2 = [ln for ln in raw(p2).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("control (no env override): k4_rows=%d" % len(rows2))
    for r in rows2:
        emit("K4ROW %r" % r)


def f3_writer_own_entry_refuses_same_env():
    """The receipt writer's own entry point refuses GIT_CONFIG_PARAMETERS. The K4 bootstrap
    calls the writer's git() helper directly, so that refusal is never reached."""
    d = fresh("f3")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    out = os.path.join(d, "receipt.txt")
    e = dict(ENV)
    e["GIT_CONFIG_PARAMETERS"] = "'core.sparseCheckout=true'"
    p = subprocess.run([sys.executable, "-B", WRITER, "--root", repo, "--rev", rev,
                        "--instrument", "a.txt", "--out", out, "--command", "/bin/true"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=e, timeout=120, cwd=d)
    emit("=== F3 the writer's own entry point refuses the same environment ===")
    emit("rc=%d" % p.returncode)
    emit("stderr: %r" % p.stderr.decode("utf-8", "replace").strip()[:400])
    emit("receipt written: %s" % os.path.exists(out))
    emit("VERDICT F3: %s" % ("the writer REFUSES this env (RECEIPT-ENV-CONFIG-SET)"
                              if p.returncode == 2 else "the writer did not refuse (rc=%d)" % p.returncode))


def f4_tool_status_vs_writer_sweep_disagree():
    """Under the same env, the TOOL's own status read (GIT_CONFIG_* scrubbed) and the
    WRITER's flag sweep (GIT_CONFIG_* NOT scrubbed) read different config views."""
    d = fresh("f4")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    base = {k: v for k, v in ENV.items() if not k.startswith("GIT_CONFIG_")}
    e = dict(base)
    e["GIT_CONFIG_PARAMETERS"] = "'core.sparseCheckout=true'"
    tool_view = subprocess.run(["git", "-C", repo, "ls-files", "-v", "-z", ":(top)"],
                               stdout=subprocess.PIPE, env=base)
    writer_view = subprocess.run(["git", "-C", repo, "ls-files", "-v", "-z", ":(top)"],
                                 stdout=subprocess.PIPE, env=e)
    emit("=== F4 two config views inside one K4 measurement ===")
    emit("TOOL view   (GIT_CONFIG_* scrubbed): %r" % [t for t in tool_view.stdout.split(b"\0")
                                                       if t.endswith(b"a.txt")])
    emit("WRITER view (GIT_CONFIG_* kept)    : %r" % [t for t in writer_view.stdout.split(b"\0")
                                                       if t.endswith(b"a.txt")])
    emit("VERDICT F4: the two halves of the K4 measurement do not share one config view")


def f5_git_config_count_route():
    """The same route via GIT_CONFIG_COUNT, which the writer's git() also does not scrub."""
    d = fresh("f5")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    e = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.sparseCheckout",
         "GIT_CONFIG_VALUE_0": "true"}
    p = run_tool(TOOL, repo, rev, env=e)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("=== F5 the same route via GIT_CONFIG_COUNT ===")
    emit("rc=%d k4_rows=%d" % (p.returncode, len(rows)))
    for r in rows:
        emit("K4ROW %r" % r)
    emit("VERDICT F5: %s" % ("FAIL OPEN" if not rows else "fail closed"))


if __name__ == "__main__":
    for fn in (f1_config_route_skipworktree, f2_config_route_gitlink,
               f3_writer_own_entry_refuses_same_env, f4_tool_status_vs_writer_sweep_disagree,
               f5_git_config_count_route):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-F.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
