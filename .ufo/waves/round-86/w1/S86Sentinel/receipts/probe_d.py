#!/usr/bin/env python3
"""Probe set D: corrected timeout probe, escaping injectivity, env routes, scope, masking."""
import hashlib
import os
import shutil
import subprocess
import sys

sys.path.insert(0, "/fast/scratch/hyaku/souji-r86/S86Sentinel")
from probe import (S, TOOL, WRITER, ENV, build_fixture, git, move_nest, run_tool, show,
                   k4_rows, fresh, tool_copy, forge_index_stat)

OUT = []


def emit(s):
    OUT.append(s)
    print(s)


def raw(p):
    return p.stdout.decode("utf-8", "replace")


def patched_writer(dirpath, patch):
    """Copy the writer and apply a text patch (after the __future__ import)."""
    os.makedirs(dirpath, exist_ok=True)
    src = open(WRITER, encoding="utf-8").read()
    out = patch(src)
    assert out != src, "patch did not apply"
    w = os.path.join(dirpath, "souji-receipt-write.py")
    open(w, "w", encoding="utf-8").write(out)
    os.chmod(w, 0o755)
    t = tool_copy(dirpath)
    return t, w


def d1_timeout():
    """A writer that hangs. The filed tool uses timeout=600; the copy lowers it to 3 s so the
    probe is bounded. The ONLY difference from the filed bytes is that one constant."""
    d = fresh("d1")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    td = os.path.join(d, "tool")
    os.makedirs(td, exist_ok=True)
    tsrc = open(TOOL, encoding="utf-8").read()
    patched = tsrc.replace("timeout=600", "timeout=3")
    assert patched != tsrc
    t = os.path.join(td, "souji-record-agreement.py")
    open(t, "w", encoding="utf-8").write(patched)
    os.chmod(t, 0o755)
    wsrc = open(WRITER, encoding="utf-8").read()
    wpatched = wsrc.replace("from __future__ import annotations",
                            "from __future__ import annotations\nimport time as _t\n_t.sleep(120)", 1)
    assert wpatched != wsrc
    w = os.path.join(td, "souji-receipt-write.py")
    open(w, "w", encoding="utf-8").write(wpatched)
    os.chmod(w, 0o755)
    p = run_tool(t, repo, rev, timeout=120)
    emit("=== D1 a writer that hangs (tool copy: timeout=3 instead of 600) ===")
    show("D1 tool", p)
    emit("VERDICT D1: %s" % ("FAIL CLOSED (a row names the timeout)" if k4_rows(raw(p)) else "FAIL OPEN"))
    emit("NOTE: the filed bytes carry timeout=600; TimeoutExpired is a subprocess.SubprocessError "
         "subclass, so the same branch fires at 600 s. The only difference is the constant.")


def _escaping_case(name_bytes, label):
    d = fresh("d_" + label)
    repo, rev, nest, nest1 = build_fixture(d)
    with open(os.path.join(repo.encode(), name_bytes), "wb") as f:
        f.write(b"v1\n")
    git(repo, "add", "-A", check=False)
    git(repo, "commit", "-q", "--no-verify", "-m", "name case", check=False)
    git(repo, "update-index", "--skip-worktree", name_bytes.decode("utf-8", "surrogateescape"), check=False)
    p = run_tool(TOOL, repo, rev)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    detail = rows[0].split("\t", 4)[4] if rows and len(rows[0].split("\t", 4)) > 4 else ""
    emit("case %-22s path bytes=%r" % (label, name_bytes))
    emit("  K4 row: %r" % (rows[0] if rows else None))
    emit("  detail: %r" % detail)
    return detail


def d2_escaping_injectivity():
    """The r86 escaping maps a real newline to the two characters backslash-n. A path whose
    NAME literally contains backslash-n therefore renders identically."""
    d_real = _escaping_case(b"a\nb.txt", "realnewline")
    d_lit = _escaping_case(b"a\\nb.txt", "literalbackslashn")
    emit("=== D2 escaping injectivity ===")
    emit("detail(real newline)      = %r" % d_real)
    emit("detail(literal backslash-n)= %r" % d_lit)
    emit("COLLISION: %s" % (d_real == d_lit))
    emit("VERDICT D2: %s" % ("the record cannot distinguish a newline path from a literal "
                             "backslash-n path: the escaped form is not injective"
                             if d_real == d_lit else "no collision"))


def d3_invalid_utf8_ambiguity():
    """Two distinct invalid-UTF-8 path names render identically in the record."""
    a = _escaping_case(b"amb\x80one.txt", "invalid80")
    b = _escaping_case(b"amb\x81one.txt", "invalid81")
    emit("=== D3 invalid-UTF-8 path names ===")
    emit("detail(bad\\x80) = %r" % a)
    emit("detail(bad\\x81) = %r" % b)
    emit("COLLISION: %s" % (a == b))
    emit("VERDICT D3: %s" % ("two different files render the same record text: the path is not "
                             "unambiguously named" if a == b else "no collision"))


def d4_no_worktree():
    d = fresh("d4")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    with open(os.path.join(repo, "a.txt"), "wb") as f:
        f.write(b"alpha v2 CHANGED\n")
    p = run_tool(TOOL, repo, rev, extra=("--no-worktree",))
    emit("=== D4 --no-worktree on a tree with a concealed change ===")
    show("D4 tool", p)
    emit("VERDICT D4: %s" % ("FAIL OPEN (K4 skipped entirely; no K4 row)" if not k4_rows(raw(p))
                              else "fail closed"))


def d5_object_dir():
    """GIT_OBJECT_DIRECTORY / GIT_ALTERNATE_OBJECT_DIRECTORIES: the writer's entry point
    refuses them; the K4 bootstrap calls the writer's helpers directly, so the refusal is
    never reached."""
    d = fresh("d5")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    alt = os.path.join(d, "empty-objects")
    os.makedirs(alt, exist_ok=True)
    for var in ("GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
        p = run_tool(TOOL, repo, rev, env={var: alt})
        emit("=== D5 %s redirected ===" % var)
        show("D5 tool (%s)" % var, p)
        emit("VERDICT D5 %s: %s" % (var, "FAIL OPEN (no K4 row: the concealment is not reported)"
                                    if not k4_rows(raw(p)) else "fail closed (a row is emitted)"))


def d6_subdir_root_reason():
    d = fresh("d6")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    sub = os.path.join(repo, "sub")
    p = run_tool(TOOL, sub, rev)
    emit("=== D6 --root inside a subdirectory: the exact refusal ===")
    show("D6 tool", p)
    emit("VERDICT D6: %s" % ("FAIL CLOSED (a row is emitted)" if k4_rows(raw(p)) else "FAIL OPEN"))
    emit("NOTE: the writer's own entry point resolves the repository toplevel before calling "
         "_truth_refusal; the K4 bootstrap calls it with --root, so a subdirectory root changes "
         "the measurement (here: a refusal), never a clean verdict.")


def d7_masking():
    """Both a stat-cache concealment and a gitlink concealment at once."""
    d = fresh("d7")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    with open(os.path.join(repo, "a.txt"), "wb") as f:
        f.write(b"alpha v2 CHANGED\n")
    forge_index_stat(repo, "a.txt")
    p = run_tool(TOOL, repo, rev)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("=== D7 a stat-cache concealment and a gitlink concealment together ===")
    for r in rows:
        emit("K4ROW %r" % r)
    emit("VERDICT D7: %s" % ("only the stat-cache row is reported: the gitlink flag is masked "
                              "(the sweep runs only when the truth check is clean)"
                              if len(rows) == 1 else "%d rows" % len(rows)))


def d8_scope_outside_root():
    """Does the flag sweep observe index entries outside the --root subtree?"""
    d = fresh("d8")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    sub = os.path.join(repo, "sub")
    ls = subprocess.run(["git", "-C", sub, "ls-files", "-v", "-z", ":(top)"],
                        stdout=subprocess.PIPE, env=ENV).stdout
    emit("=== D8 scope of 'git ls-files -v -z :(top)' from a subdirectory ===")
    emit("entries seen from repo/sub: %r" % ls.split(b"\0")[:8])
    emit("VERDICT D8: the :(top) pathspec widens the sweep to the whole index" if b"a.txt" in ls
         else "the sweep from a subdirectory does NOT see paths outside it")


if __name__ == "__main__":
    for fn in (d1_timeout, d2_escaping_injectivity, d3_invalid_utf8_ambiguity, d4_no_worktree,
               d5_object_dir, d6_subdir_root_reason, d7_masking, d8_scope_outside_root):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-D.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
