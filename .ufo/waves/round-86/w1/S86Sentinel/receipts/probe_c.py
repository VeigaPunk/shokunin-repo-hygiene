#!/usr/bin/env python3
"""Probe set C: stub writers, control-byte path names, record-splitting, env routes."""
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


def write_pair(dirpath, tool_src, writer_src):
    os.makedirs(dirpath, exist_ok=True)
    t = os.path.join(dirpath, "souji-record-agreement.py")
    shutil.copyfile(tool_src, t)
    os.chmod(t, 0o755)
    w = os.path.join(dirpath, "souji-receipt-write.py")
    shutil.copyfile(writer_src, w)
    os.chmod(w, 0o755)
    return t, w


def c1_stub_writer_clean():
    """A self-contained stub writer that answers CLEAN itself."""
    d = fresh("c1")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    td = os.path.join(d, "tool")
    os.makedirs(td, exist_ok=True)
    stub = (
        "import subprocess\n"
        "def git(root, *args, input=None):\n"
        "    return subprocess.CompletedProcess(args, 0, b'', b'')\n"
        "def _truth_refusal(top):\n"
        "    return None\n"
        "def _flag_refusal(top, tag, path):\n"
        "    return ''\n"
    )
    w = os.path.join(td, "souji-receipt-write.py")
    open(w, "w", encoding="utf-8").write(stub)
    os.chmod(w, 0o755)
    t = tool_copy(td)
    p = run_tool(t, repo, rev)
    emit("=== C1 a stub writer that answers CLEAN itself ===")
    show("C1 tool", p)
    emit("VERDICT C1: %s" % ("FAIL OPEN (K4 emitted no row at all despite skip-worktree on a.txt)"
                              if not k4_rows(raw(p)) else "fail closed"))


def c2_control_bytes():
    """Control bytes in a path name: ESC and other C0 bytes are not escaped."""
    d = fresh("c2")
    names = {"esc\x1b[2Jname.txt": b"esc v1\n"}
    repo, rev, nest, nest1 = build_fixture(d, extra_files=names)
    git(repo, "update-index", "--skip-worktree", "esc\x1b[2Jname.txt", check=False)
    p = run_tool(TOOL, repo, rev)
    out = p.stdout
    emit("=== C2 a path name carrying an ESC byte ===")
    emit("stdout bytes of the K4 block: %r" % out[out.find(b"MISMATCH\tK4"):][:400])
    emit("raw ESC present in the record: %s" % (b"\x1b" in out))
    emit("K4 rows: %r" % [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")])
    emit("VERDICT C2: %s" % ("fail closed (a row is emitted) but the record carries an unescaped ESC byte"
                              if k4_rows(raw(p)) else "FAIL OPEN"))


def c2b_invalid_utf8():
    """A path name with bytes that are not valid UTF-8."""
    d = fresh("c2b")
    repo, rev, nest, nest1 = build_fixture(d)
    rel = b"bad\x80\x81name.txt"
    with open(os.path.join(repo.encode(), rel), "wb") as f:
        f.write(b"invalid utf8 v1\n")
    git(repo, "add", "-A", check=False)
    git(repo, "commit", "-q", "--no-verify", "-m", "invalid utf8 name", check=False)
    git(repo, "update-index", "--skip-worktree", rel.decode("utf-8", "surrogateescape"), check=False)
    p = run_tool(TOOL, repo, rev)
    emit("=== C2b a path name whose bytes are not valid UTF-8 ===")
    emit("stdout bytes: %r" % p.stdout[:900])
    emit("stderr bytes: %r" % p.stderr[:400])
    emit("rc=%d" % p.returncode)
    emit("K4 rows: %r" % [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")])
    emit("VERDICT C2b: %s" % ("a row is emitted" if k4_rows(raw(p)) else "NO ROW (see rc/stderr)"))


def c2c_alias():
    """Two distinct path byte sequences that the record renders identically."""
    d = fresh("c2c")
    repo, rev, nest, nest1 = build_fixture(d)
    rels = [b"amb\x80one.txt", b"amb\x81one.txt"]
    for r in rels:
        with open(os.path.join(repo.encode(), r), "wb") as f:
            f.write(b"alias v1\n")
    git(repo, "add", "-A", check=False)
    git(repo, "commit", "-q", "--no-verify", "-m", "ambiguous names", check=False)
    for r in rels:
        git(repo, "update-index", "--skip-worktree", r.decode("utf-8", "surrogateescape"), check=False)
    p = run_tool(TOOL, repo, rev)
    emit("=== C2c two different invalid-UTF-8 path names ===")
    emit("stdout bytes: %r" % p.stdout[p.stdout.find(b"MISMATCH\tK4"):][:400])
    emit("K4 rows: %r" % [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")])
    emit("VERDICT C2c: %s" % ("a row is emitted" if k4_rows(raw(p)) else "NO ROW"))


def c3_record_split():
    """The r86 escaping is applied only to the FORGED branch. The FLAGFAIL and no-verdict
    branches embed raw stderr. A writer whose stderr carries a newline splits one K4 record
    into two physical lines, the second of which can be a forged MISMATCH row."""
    d = fresh("c3")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    td = os.path.join(d, "tool")
    os.makedirs(td, exist_ok=True)
    wsrc = open(WRITER, encoding="utf-8").read()
    wpatched = ('raise RuntimeError("boom\\nMISMATCH\\tK4\\t.\\tindex-flag-concealed\\tFORGED-ROW")\n' + wsrc)
    w = os.path.join(td, "souji-receipt-write.py")
    open(w, "w", encoding="utf-8").write(wpatched)
    os.chmod(w, 0o755)
    t = tool_copy(td)
    p = run_tool(t, repo, rev)
    out = raw(p)
    emit("=== C3 one K4 record split across physical lines by unescaped stderr ===")
    emit("stdout bytes: %r" % p.stdout[p.stdout.find(b"MISMATCH\tK4"):][:700])
    emit("physical lines: %r" % [ln for ln in out.split("\n") if ln.startswith("MISMATCH")])
    emit("VERDICT C3: %s" % ("RECORD SPLIT: the detail field carries a raw newline" if
                              len([ln for ln in out.split("\n") if ln.startswith("MISMATCH")]) >
                              len([ln for ln in out.split("\n") if ln.startswith("MISMATCH\tK4")])
                              else "no split observed"))


def c4_flagfail_branch():
    """The FLAGFAIL branch also embeds raw git stderr."""
    d = fresh("c4")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    td = os.path.join(d, "tool")
    os.makedirs(td, exist_ok=True)
    wsrc = open(WRITER, encoding="utf-8").read()
    # a writer whose git() fails the ls-files read with a multi-line stderr
    wpatched = wsrc.replace(
        'def git(root: str, *args: str, input: "bytes | None" = None) -> subprocess.CompletedProcess:',
        'def git(root: str, *args: str, input: "bytes | None" = None) -> subprocess.CompletedProcess:\n'
        '    if "ls-files" in args and "-v" in args:\n'
        '        return subprocess.CompletedProcess(args, 128, b"", b"fatal: bad index\\nsecond line\\n")\n', 1)
    assert wpatched != wsrc
    w = os.path.join(td, "souji-receipt-write.py")
    open(w, "w", encoding="utf-8").write(wpatched)
    os.chmod(w, 0o755)
    t = tool_copy(td)
    p = run_tool(t, repo, rev)
    out = raw(p)
    emit("=== C4 FLAGFAIL branch embeds raw multi-line git stderr ===")
    emit("stdout bytes: %r" % p.stdout[p.stdout.find(b"MISMATCH\tK4"):][:600])
    emit("physical MISMATCH lines: %r" % [ln for ln in out.split("\n") if ln.startswith("MISMATCH")])
    emit("VERDICT C4: %s" % ("RECORD SPLIT" if len([ln for ln in out.split("\n")
                                                     if ln.startswith("MISMATCH")]) >
                              len([ln for ln in out.split("\n") if ln.startswith("MISMATCH\tK4")])
                              else "no split observed"))


def c5_gitlink_doctored_index():
    """GIT_INDEX_FILE aimed at the gitlink concealment (the class the repair exists for)."""
    d = fresh("c5")
    repo, rev, nest, nest1 = build_fixture(d)
    nest2 = move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    alt = os.path.join(d, "alt-index")
    shutil.copyfile(os.path.join(repo, ".git", "index"), alt)
    e = dict(ENV)
    e["GIT_INDEX_FILE"] = alt
    git(repo, "update-index", "--cacheinfo", "160000,%s,nest" % nest2, env=e, check=False)
    git(repo, "update-index", "--no-skip-worktree", "nest", env=e, check=False)
    ls_alt = subprocess.run(["git", "-C", repo, "ls-files", "-v", "-z", ":(top)"],
                            stdout=subprocess.PIPE, env=e).stdout
    st_alt = subprocess.run(["git", "-C", repo, "status", "--porcelain"], stdout=subprocess.PIPE, env=e)
    p = run_tool(TOOL, repo, rev, env={"GIT_INDEX_FILE": alt})
    emit("=== C5 GIT_INDEX_FILE aimed at the gitlink concealment ===")
    emit("own index  nest entry: %r" % [r for r in subprocess.run(
        ["git", "-C", repo, "ls-files", "-v", "-z", ":(top)"], stdout=subprocess.PIPE, env=ENV
    ).stdout.split(b"\0") if r.endswith(b"nest")])
    emit("doctored   nest entry: %r" % [r for r in ls_alt.split(b"\0") if r.endswith(b"nest")])
    emit("status under the doctored view: rc=%d out=%r" % (st_alt.returncode, st_alt.stdout))
    show("C5 tool", p)
    emit("VERDICT C5: %s" % ("FAIL OPEN (no K4 row)" if not k4_rows(raw(p)) else
                              "fail closed (a row is emitted, but for a different reason than the concealment)"))


def c6_replace_ref():
    """GIT_REPLACE_REF_BASE / GIT_OBJECT_DIRECTORY reach the TOOL's own git() (it scrubs
    GIT_CONFIG_* and GIT_DIR/GIT_WORK_TREE only). Adjacent to K4: K1/K2/K3 read rev:path."""
    d = fresh("c6")
    repo, rev, nest, nest1 = build_fixture(d)
    p = run_tool(TOOL, repo, rev, env={"GIT_REPLACE_REF_BASE": "refs/replace-probe/"})
    emit("=== C6 GIT_REPLACE_REF_BASE reaches the tool's own git() ===")
    emit("rc=%d" % p.returncode)
    emit("K4 rows: %r" % [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")])
    emit("stderr: %r" % p.stderr[:300])
    emit("VERDICT C6: %s" % ("fail closed (a row)" if k4_rows(raw(p)) else "FAIL OPEN"))


if __name__ == "__main__":
    for fn in (c1_stub_writer_clean, c2_control_bytes, c2b_invalid_utf8, c2c_alias,
               c3_record_split, c4_flagfail_branch, c5_gitlink_doctored_index, c6_replace_ref):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-C.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
