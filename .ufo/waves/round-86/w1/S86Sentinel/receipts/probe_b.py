#!/usr/bin/env python3
"""Probe set B: index-view redirection, scope, escaping, stub writers, timeout."""
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


def b1_doctored_index_file():
    """GIT_INDEX_FILE redirects BOTH the truth check and the flag sweep to a caller-chosen
    index view in which the concealment does not exist."""
    d = fresh("b1")
    repo, rev, nest, nest1 = build_fixture(d)
    # a real worktree change on a tracked file, concealed in the repository's OWN index
    with open(os.path.join(repo, "a.txt"), "wb") as f:
        f.write(b"alpha v2 CHANGED\n")
    git(repo, "update-index", "--skip-worktree", "a.txt")
    st_real = subprocess.run(["git", "-C", repo, "status", "--porcelain"], stdout=subprocess.PIPE, env=ENV)
    # the doctored view: no flag, oid = the changed bytes
    alt = os.path.join(d, "alt-index")
    shutil.copyfile(os.path.join(repo, ".git", "index"), alt)
    blob = subprocess.run(["git", "-C", repo, "hash-object", "-w", "--stdin"],
                          input=b"alpha v2 CHANGED\n", stdout=subprocess.PIPE, env=ENV).stdout.decode().strip()
    e = dict(ENV)
    e["GIT_INDEX_FILE"] = alt
    git(repo, "update-index", "--cacheinfo", "100644,%s,a.txt" % blob, env=e, check=False)
    git(repo, "update-index", "--no-skip-worktree", "a.txt", env=e, check=False)
    st_alt = subprocess.run(["git", "-C", repo, "status", "--porcelain"], stdout=subprocess.PIPE, env=e)
    ls_real = subprocess.run(["git", "-C", repo, "ls-files", "-v", "-z", ":(top)"],
                             stdout=subprocess.PIPE, env=ENV).stdout
    ls_alt = subprocess.run(["git", "-C", repo, "ls-files", "-v", "-z", ":(top)"],
                            stdout=subprocess.PIPE, env=e).stdout
    p_clean = run_tool(TOOL, repo, rev)
    p_doc = run_tool(TOOL, repo, rev, env={"GIT_INDEX_FILE": alt})
    emit("=== B1 GIT_INDEX_FILE redirects the whole K4 measurement ===")
    emit("repository's own index  a.txt entry: %r" % [r for r in ls_real.split(b"\0") if r.endswith(b"a.txt")])
    emit("doctored index view    a.txt entry: %r" % [r for r in ls_alt.split(b"\0") if r.endswith(b"a.txt")])
    emit("status --porcelain (own index): rc=%d out=%r" % (st_real.returncode, st_real.stdout))
    emit("status --porcelain (doctored) : rc=%d out=%r" % (st_alt.returncode, st_alt.stdout))
    emit("--- tool WITHOUT GIT_INDEX_FILE ---")
    show("B1a own index", p_clean)
    emit("--- tool WITH GIT_INDEX_FILE=%s ---" % os.path.basename(alt))
    show("B1b doctored index", p_doc)
    verdict = "FAIL OPEN (K4 reported no K4 row at all: a CLEAN verdict for a tree whose own index conceals the change)" \
        if not k4_rows(raw(p_doc)) else "fail closed"
    emit("VERDICT B1: %s" % verdict)
    emit("NOTE: the writer's own entry point refuses GIT_INDEX_FILE (RECEIPT-INDEX-ENV-SET); "
         "the K4 bootstrap calls the writer's helpers directly and never reaches that refusal.")


def b2_subdir_root():
    """--root inside a subdirectory: the writer resolves the repository toplevel, the K4
    bootstrap does not."""
    d = fresh("b2")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    sub = os.path.join(repo, "sub")
    p = run_tool(TOOL, sub, rev)
    emit("=== B2 --root points inside a subdirectory ===")
    emit("repo=%s sub=%s" % (repo, sub))
    show("B2 tool", p)
    emit("VERDICT B2: %s" % ("FAIL CLOSED (a row is emitted)" if k4_rows(raw(p)) else "FAIL OPEN"))


def b3_escaping():
    """Path names that carry control bytes: newline, tab, CR, ESC, invalid UTF-8, and a
    literal backslash-n that collides with the escaped form."""
    d = fresh("b3")
    names = {
        "nl\nname.txt": b"nl v1\n",
        "tab\tname.txt": b"tab v1\n",
        "cr\rname.txt": b"cr v1\n",
        "esc\x1b[31mname.txt": b"esc v1\n",
        "bad\xff\xfename.txt": b"invalid utf8 v1\n",
        "lit\\nname.txt": b"literal backslash n v1\n",
    }
    repo, rev, nest, nest1 = build_fixture(d, extra_files=names)
    # conceal each of them behind skip-worktree so the flag sweep is what must name them
    for rel in names:
        git(repo, "update-index", "--skip-worktree", rel, check=False)
    p = run_tool(TOOL, repo, rev)
    out = p.stdout
    emit("=== B3 record escaping for control-byte path names ===")
    emit("path names planted: %r" % sorted(names))
    k4 = [ln for ln in out.decode("utf-8", "replace").split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("k4 rows emitted: %d" % len(k4))
    for ln in k4:
        emit("K4ROW %r" % ln)
    physical = out.decode("utf-8", "replace").split("\n")
    mism = [ln for ln in physical if ln.startswith("MISMATCH")]
    emit("total physical lines starting with MISMATCH: %d" % len(mism))
    emit("raw bytes of the MISMATCH block: %r" % out[out.find(b"MISMATCH"):][:600])
    emit("VERDICT B3: %s" % ("fail closed" if k4 else "FAIL OPEN"))


def b3b_newline_only():
    """One planted path whose name carries a newline; check the record is ONE physical line
    and still names the path, and that a literal backslash-n name collides with it."""
    d = fresh("b3b")
    repo, rev, nest, nest1 = build_fixture(d, extra_files={"bad\nname.txt": b"nl v1\n"})
    git(repo, "update-index", "--skip-worktree", "bad\nname.txt", check=False)
    p = run_tool(TOOL, repo, rev)
    out = p.stdout.decode("utf-8", "replace")
    emit("=== B3b a newline in the path name ===")
    emit("stdout bytes: %r" % p.stdout[:500])
    emit("physical lines: %r" % out.split("\n"))
    emit("K4 rows: %r" % [ln for ln in out.split("\n") if ln.startswith("MISMATCH\tK4")])
    emit("VERDICT B3b: %s" % ("fail closed" if [ln for ln in out.split("\n") if ln.startswith("MISMATCH\tK4")]
                              else "FAIL OPEN"))


def b4_stub_writer_prints_clean():
    """A writer whose source prints CLEAN on stdout at import time."""
    d = fresh("b4")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    td = os.path.join(d, "tool")
    os.makedirs(td, exist_ok=True)
    src = open(WRITER, encoding="utf-8").read()
    patched = 'import sys as _s\n_s.stdout.write("CLEAN\\n")\n' + src
    w = os.path.join(td, "souji-receipt-write.py")
    open(w, "w", encoding="utf-8").write(patched)
    os.chmod(w, 0o755)
    t = tool_copy(td)
    p = run_tool(t, repo, rev)
    emit("=== B4 a writer that prints CLEAN on stdout when imported ===")
    show("B4 tool", p)
    emit("VERDICT B4: %s" % ("FAIL OPEN (no K4 row)" if not k4_rows(raw(p)) else "fail closed"))


def b5_timeout():
    """A writer that hangs. The filed tool uses timeout=600; this copy lowers it to 3 s so
    the probe is bounded (the ONLY difference from the filed bytes is that constant)."""
    d = fresh("b5")
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
    wpatched = "import time as _t\n_t.sleep(60)\n" + wsrc
    w = os.path.join(td, "souji-receipt-write.py")
    open(w, "w", encoding="utf-8").write(wpatched)
    os.chmod(w, 0o755)
    p = run_tool(t, repo, rev, timeout=60)
    emit("=== B5 a writer that hangs (tool copy with timeout=3; filed bytes use timeout=600) ===")
    show("B5 tool", p)
    emit("VERDICT B5: %s" % ("FAIL CLOSED (a row naming the timeout)" if k4_rows(raw(p)) else "FAIL OPEN"))


def b6_git_common_dir():
    """GIT_COMMON_DIR: the writer's git() scrubs it, the tool's own git() does not."""
    d = fresh("b6")
    repo, rev, nest, nest1 = build_fixture(d)
    other = os.path.join(d, "other.git")
    subprocess.run(["git", "init", "-q", "--bare", other], env=ENV, check=True)
    p = run_tool(TOOL, repo, rev, env={"GIT_COMMON_DIR": other})
    emit("=== B6 GIT_COMMON_DIR redirected to a foreign common dir ===")
    show("B6 tool", p)
    emit("VERDICT B6: %s" % ("FAIL CLOSED (a row)" if k4_rows(raw(p)) else "FAIL OPEN"))


def b7_git_config_parameters():
    """GIT_CONFIG_PARAMETERS reaches the writer's git() inside the bootstrap (the writer's
    git() scrubs GIT_DIR/GIT_WORK_TREE but not GIT_CONFIG_PARAMETERS; the writer's own
    entry point refuses it)."""
    d = fresh("b7")
    repo, rev, nest, nest1 = build_fixture(d)
    with open(os.path.join(repo, "a.txt"), "wb") as f:
        f.write(b"alpha v2 CHANGED\n")
    git(repo, "update-index", "--skip-worktree", "a.txt")
    e = {"GIT_CONFIG_PARAMETERS": "'core.checkStat=minimal' 'core.trustctime=false'"}
    p = run_tool(TOOL, repo, rev, env=e)
    emit("=== B7 GIT_CONFIG_PARAMETERS injected ===")
    show("B7 tool", p)
    emit("VERDICT B7: %s" % ("FAIL CLOSED (a row)" if k4_rows(raw(p)) else "FAIL OPEN"))


if __name__ == "__main__":
    for fn in (b1_doctored_index_file, b2_subdir_root, b3_escaping, b3b_newline_only,
               b4_stub_writer_prints_clean, b5_timeout, b6_git_common_dir, b7_git_config_parameters):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-B.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
