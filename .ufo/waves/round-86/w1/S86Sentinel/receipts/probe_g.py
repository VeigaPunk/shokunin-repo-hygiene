#!/usr/bin/env python3
"""Probe set G: tight record-forging, writer provenance, class taxonomy of the new failure modes."""
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


def g1_forge_second_row():
    """A writer whose stderr carries a complete MISMATCH row. The no-verdict branch embeds
    stderr raw (no escaping), so the row becomes its own physical line."""
    d = fresh("g1")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    td = os.path.join(d, "tool")
    os.makedirs(td, exist_ok=True)
    w = os.path.join(td, "souji-receipt-write.py")
    open(w, "w", encoding="utf-8").write(
        "import os, sys\n"
        "os.write(2, b'MISMATCH\\tK4\\t.\\tindex-flag-concealed\\tFORGED-BY-WRITER\\n')\n"
        "sys.exit(1)\n")
    os.chmod(w, 0o755)
    t = tool_copy(td)
    p = run_tool(t, repo, rev)
    out = raw(p)
    emit("=== G1 a forged MISMATCH row inside a K4 detail field ===")
    emit("stdout bytes: %r" % p.stdout[p.stdout.find(b"MISMATCH\tK4"):][:400])
    phys = [ln for ln in out.split("\n") if ln.startswith("MISMATCH")]
    emit("physical MISMATCH lines: %r" % phys)
    forged = [ln for ln in phys if "FORGED-BY-WRITER" in ln]
    emit("VERDICT G1: %s" % ("RECORD FORGED: a second, fully-formed K4 row appears in the output"
                              if forged else "no forged row"))
    emit("NOTE: this needs a substituted writer, which the preregistration's stated limits put "
         "outside the claim; it is reported as a mechanism K4 does not measure.")


def g2_writer_provenance():
    """The writer beside the tool is loaded by path; a symlink at that path is followed."""
    d = fresh("g2")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    td = os.path.join(d, "tool")
    os.makedirs(td, exist_ok=True)
    t = tool_copy(td)
    outside = os.path.join(d, "outside.py")
    open(outside, "w", encoding="utf-8").write(
        "import os, sys\n"
        "def git(root, *a, input=None):\n"
        "    import subprocess\n"
        "    return subprocess.CompletedProcess(a, 0, b'', b'')\n"
        "def _truth_refusal(top):\n"
        "    return None\n"
        "def _flag_refusal(top, tag, path):\n"
        "    return ''\n")
    os.symlink(outside, os.path.join(td, "souji-receipt-write.py"))
    p = run_tool(t, repo, rev)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("=== G2 the writer beside the tool is a symlink to an outside file ===")
    emit("isfile(writer path) is what the tool checks; a symlink to a file passes it")
    emit("rc=%d k4_rows=%d" % (p.returncode, len(rows)))
    emit("VERDICT G2: %s" % ("FAIL OPEN (the symlinked writer was loaded and K4 reported CLEAN)"
                              if not rows else "fail closed"))


def g3_class_taxonomy():
    """Every new r86 failure mode lands in the 'stat-cache-concealed' class, which names the
    wrong mechanism."""
    cases = {}

    # (a) the writer lacks _flag_refusal entirely
    d = fresh("g3a")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    td = os.path.join(d, "tool")
    os.makedirs(td, exist_ok=True)
    wsrc = open(WRITER, encoding="utf-8").read()
    w = os.path.join(td, "souji-receipt-write.py")
    open(w, "w", encoding="utf-8").write(wsrc.replace("def _flag_refusal(", "def _flag_refusal_RENAMED(", 1))
    os.chmod(w, 0o755)
    t = tool_copy(td)
    p = run_tool(t, repo, rev)
    cases["writer has no _flag_refusal"] = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]

    # (b) the writer's ls-files read fails -> FLAGFAIL
    d = fresh("g3b")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    td = os.path.join(d, "tool")
    os.makedirs(td, exist_ok=True)
    wsrc = open(WRITER, encoding="utf-8").read()
    w = os.path.join(td, "souji-receipt-write.py")
    open(w, "w", encoding="utf-8").write(wsrc.replace(
        'def git(root: str, *args: str, input: "bytes | None" = None) -> subprocess.CompletedProcess:',
        'def git(root: str, *args: str, input: "bytes | None" = None) -> subprocess.CompletedProcess:\n'
        '    if "ls-files" in args and "-v" in args:\n'
        '        return subprocess.CompletedProcess(args, 128, b"", b"fatal: bad index\\n")\n', 1))
    os.chmod(w, 0o755)
    t = tool_copy(td)
    p = run_tool(t, repo, rev)
    cases["the index-flag read fails (FLAGFAIL)"] = [ln for ln in raw(p).split("\n")
                                                     if ln.startswith("MISMATCH\tK4")]

    emit("=== G3 the class each new r86 failure mode is reported under ===")
    for label, rows in cases.items():
        for r in rows:
            parts = r.split("\t")
            emit("%-40s -> class=%r record=%r" % (label, parts[3] if len(parts) > 3 else "?",
                                                  parts[2] if len(parts) > 2 else "?"))
            emit("   detail: %r" % (parts[4][:120] if len(parts) > 4 else ""))
    emit("VERDICT G3: the index-flag read failure and the missing _flag_refusal are both reported "
         "as class 'stat-cache-concealed', a class name that names the WRONG mechanism; only a "
         "message that literally begins with 'RECEIPT-GITLINK-CONCEALED' or 'RECEIPT-INDEX-' "
         "reaches the new 'index-flag-concealed' class.")


def g4_writer_git_index_file_leak():
    """Does the WRITER's git() (used by the new sweep) honour GIT_INDEX_FILE? The writer's own
    entry point refuses that env; the bootstrap bypasses the entry point."""
    d = fresh("g4")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    alt = os.path.join(d, "alt-index")
    shutil.copyfile(os.path.join(repo, ".git", "index"), alt)
    e = dict(ENV)
    e["GIT_INDEX_FILE"] = alt
    nest2 = git(nest, "rev-parse", "HEAD").stdout.decode().strip()
    git(repo, "update-index", "--cacheinfo", "160000,%s,nest" % nest2, env=e, check=False)
    git(repo, "update-index", "--no-skip-worktree", "nest", env=e, check=False)
    p = run_tool(TOOL, repo, rev, env={"GIT_INDEX_FILE": alt})
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("=== G4 GIT_INDEX_FILE reaches the writer's git() inside the new sweep ===")
    emit("rc=%d k4_rows=%d" % (p.returncode, len(rows)))
    for r in rows:
        emit("K4ROW %r" % r)
    emit("VERDICT G4: %s" % ("a row is emitted, but the class names a different mechanism than "
                              "the concealment" if rows else "FAIL OPEN"))
    emit("NOTE: the receipt writer's own entry point refuses GIT_INDEX_FILE "
         "(RECEIPT-INDEX-ENV-SET); the K4 bootstrap calls mod.git() directly and never reaches "
         "that refusal.")


if __name__ == "__main__":
    for fn in (g1_forge_second_row, g2_writer_provenance, g3_class_taxonomy,
               g4_writer_git_index_file_leak):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-G.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
