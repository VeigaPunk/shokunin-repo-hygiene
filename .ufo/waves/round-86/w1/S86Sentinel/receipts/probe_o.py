#!/usr/bin/env python3
"""Probe set O: record splitting with an HONEST writer and a corrupt index."""
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


def o1_status_failed_multiline():
    """The tool's own status read fails with a MULTI-LINE git stderr; the 'status-failed'
    detail embeds it raw, so one K4 record splits across physical lines."""
    d = fresh("o1")
    repo, rev, nest, nest1 = build_fixture(d)
    idx = os.path.join(repo, ".git", "index")
    original = open(idx, "rb").read()
    open(idx, "wb").write(original[:4] + b"\x00\x00\x00\x09" + original[8:])
    st = subprocess.run(["git", "-C", repo, "status", "--porcelain"], stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, env=ENV)
    emit("=== O1 a corrupt index makes the tool's own status read fail ===")
    emit("git status --porcelain rc=%d stderr=%r" % (st.returncode, st.stderr))
    p = run_tool(TOOL, repo, rev)
    out = raw(p)
    phys = out.split("\n")
    emit("tool stdout bytes around the K4 row: %r" % p.stdout[p.stdout.find(b"MISMATCH\tK4"):][:300])
    emit("physical lines starting with MISMATCH: %r" % [ln for ln in phys if ln.startswith("MISMATCH")])
    emit("physical lines NOT starting with MISMATCH but inside the K4 detail: %r"
         % [ln for ln in phys if ln and not ln.startswith("MISMATCH")
            and not ln.startswith("keys=") and "census/" not in ln and "LOG.md" not in ln
            and "corpus/" not in ln])
    emit("RECORD SPLIT: %s" % any(ln.startswith("fatal:") for ln in phys))
    open(idx, "wb").write(original)


def o2_is_the_escape_applied_to_status_failed():
    """The r86 escaping is applied ONLY inside truth_refusal's FORGED branch. The
    status-failed branch is in k4() and never passes through it."""
    import re
    filed = open(TOOL, encoding="utf-8").read()
    emit("=== O2 where the r86 escaping is applied ===")
    for ln in filed.split("\n"):
        if "replace(" in ln and "\\\\n" in ln:
            emit("  truth_refusal: %s" % ln.strip())
    for ln in filed.split("\n"):
        if "status-failed" in ln:
            emit("  k4():        %s" % ln.strip())
    for ln in filed.split("\n"):
        if "exemption-not-allowed" in ln or "uncommitted-path" in ln:
            emit("  k4():        %s" % ln.strip())
    emit("")
    emit("  -> only the FORGED branch inside truth_refusal() is escaped; the status-failed")
    emit("     branch (and the exemption-not-allowed branch) are not.")


def o3_git_error_multiline_reachable():
    """Which git failures produce a multi-line stderr on the status read?"""
    d = fresh("o3")
    repo, rev, nest, nest1 = build_fixture(d)
    idx = os.path.join(repo, ".git", "index")
    original = open(idx, "rb").read()
    emit("=== O3 multi-line git stderr on the status read ===")
    for label, blob in (("bad index version 9", original[:4] + b"\x00\x00\x00\x09" + original[8:]),
                        ("bad signature", b"XXXX" + original[4:])):
        open(idx, "wb").write(blob)
        st = subprocess.run(["git", "-C", repo, "status", "--porcelain"], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=ENV)
        emit("  %-22s rc=%d stderr=%r" % (label, st.returncode, st.stderr))
    open(idx, "wb").write(original)


if __name__ == "__main__":
    for fn in (o1_status_failed_multiline, o2_is_the_escape_applied_to_status_failed,
               o3_git_error_multiline_reachable):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-O.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
