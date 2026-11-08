#!/usr/bin/env python3
"""Probe set A: index-view redirection, writer substitution, writer absence."""
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


def p1_git_index_file_doctored():
    """GIT_INDEX_FILE points at a caller-chosen index view: skip-worktree cleared and the
    gitlink oid advanced, so both the status read and the flag sweep see a clean index."""
    d = fresh("p1")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    # the REAL index now conceals the nested HEAD move
    real = subprocess.run(["git", "-C", repo, "ls-files", "-v", "-z", ":(top)"],
                          stdout=subprocess.PIPE, env=ENV).stdout
    real_nest = [r for r in real.split(b"\0") if r.endswith(b"nest")]
    alt = os.path.join(d, "alt-index")
    shutil.copyfile(os.path.join(repo, ".git", "index"), alt)
    nest2 = git(nest, "rev-parse", "HEAD").stdout.decode().strip()
    e = dict(ENV)
    e["GIT_INDEX_FILE"] = alt
    git(repo, "update-index", "--cacheinfo", "160000,%s,nest" % nest2, env=e)
    git(repo, "update-index", "--no-skip-worktree", "nest", env=e)
    alt_nest = [r for r in subprocess.run(["git", "-C", repo, "ls-files", "-v", "-z", ":(top)"],
                                          stdout=subprocess.PIPE, env=e).stdout.split(b"\0")
                if r.endswith(b"nest")]
    st = subprocess.run(["git", "-C", repo, "status", "--porcelain"], stdout=subprocess.PIPE, env=e)
    p = run_tool(TOOL, repo, rev, env={"GIT_INDEX_FILE": alt})
    emit("=== P1 GIT_INDEX_FILE doctored index view ===")
    emit("real index nest entry: %r" % (real_nest,))
    emit("alt  index nest entry: %r" % (alt_nest,))
    emit("nested HEAD moved %s -> %s ; real index still carries skip-worktree" % (nest1[:8], nest2[:8]))
    emit("git status --porcelain under GIT_INDEX_FILE=%s: rc=%d out=%r"
         % (os.path.basename(alt), st.returncode, st.stdout))
    show("P1 tool under GIT_INDEX_FILE", p)
    emit("VERDICT P1: %s" % ("FAIL OPEN (K4 reported CLEAN for a tree whose real index conceals the "
                              "nested HEAD move)" if not k4_rows(p.stdout.decode("utf-8", "replace"))
                              else "fail closed"))


def p2_git_index_file_missing():
    d = fresh("p2")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    p = run_tool(TOOL, repo, rev, env={"GIT_INDEX_FILE": os.path.join(d, "no-such-index")})
    emit("=== P2 GIT_INDEX_FILE naming a nonexistent index ===")
    show("P2 tool", p)
    emit("VERDICT P2: %s" % ("FAIL CLOSED (a row naming the failed index read)" if k4_rows(
        p.stdout.decode("utf-8", "replace")) else "FAIL OPEN"))


def _patched_writer(dirpath, patch):
    """Copy the real writer, apply a text patch, return the dir with tool+writer."""
    os.makedirs(dirpath, exist_ok=True)
    src = open(WRITER, encoding="utf-8").read()
    out = patch(src)
    assert out != src, "patch did not apply"
    w = os.path.join(dirpath, "souji-receipt-write.py")
    open(w, "w", encoding="utf-8").write(out)
    os.chmod(w, 0o755)
    t = tool_copy(dirpath)
    return t, w


def p3_writer_flag_refusal_empty():
    """A writer whose _flag_refusal returns an empty message: the tool treats a falsy
    message as 'nothing concealed' and prints CLEAN."""
    d = fresh("p3")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")

    def patch(src):
        return src.replace(
            'def _flag_refusal(top: str, tag: bytes, path: bytes) -> str:',
            'def _flag_refusal(top: str, tag: bytes, path: bytes) -> str:\n    return ""  # P3 stub',
            1)

    t, w = _patched_writer(os.path.join(d, "tool"), patch)
    p = run_tool(t, repo, rev)
    emit("=== P3 writer whose _flag_refusal returns an empty message ===")
    emit("writer sha256=%s (patched copy)" % __import__("hashlib").sha256(open(w, "rb").read()).hexdigest()[:16])
    show("P3 tool", p)
    emit("VERDICT P3: %s" % ("FAIL OPEN (K4 reported CLEAN although the index carries skip-worktree)"
                              if not k4_rows(p.stdout.decode("utf-8", "replace")) else "fail closed"))


def p4_writer_without_flag_refusal():
    """A writer that does not define _flag_refusal at all."""
    d = fresh("p4")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")

    def patch(src):
        return src.replace("def _flag_refusal(", "def _flag_refusal_RENAMED(", 1)

    t, w = _patched_writer(os.path.join(d, "tool"), patch)
    p = run_tool(t, repo, rev)
    emit("=== P4 writer with no _flag_refusal attribute ===")
    show("P4 tool", p)
    emit("VERDICT P4: %s" % ("FAIL CLOSED (a row naming the missing verdict)" if k4_rows(
        p.stdout.decode("utf-8", "replace")) else "FAIL OPEN"))


def p5_writer_git_returns_empty():
    """A writer whose git() reports no index records for the flag sweep."""
    d = fresh("p5")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")

    def patch(src):
        return src.replace(
            'def git(root: str, *args: str, input: "bytes | None" = None) -> subprocess.CompletedProcess:',
            'def git(root: str, *args: str, input: "bytes | None" = None) -> subprocess.CompletedProcess:\n'
            '    if "ls-files" in args:\n'
            '        return subprocess.CompletedProcess(args, 0, b"", b"")  # P5 stub\n', 1)

    t, w = _patched_writer(os.path.join(d, "tool"), patch)
    p = run_tool(t, repo, rev)
    emit("=== P5 writer whose git() hides the index from the flag sweep ===")
    show("P5 tool", p)
    emit("VERDICT P5: %s" % ("FAIL OPEN (K4 reported CLEAN although the index carries skip-worktree)"
                              if not k4_rows(p.stdout.decode("utf-8", "replace")) else "fail closed"))


def p6_writer_absent():
    """A copy of the tool with no writer beside it."""
    d = fresh("p6")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    t = tool_copy(os.path.join(d, "tool"))
    p = run_tool(t, repo, rev)
    emit("=== P6 tool copy with no writer beside it ===")
    show("P6 tool", p)
    emit("VERDICT P6: %s" % ("FAIL CLOSED (a row naming the missing writer)" if k4_rows(
        p.stdout.decode("utf-8", "replace")) else "FAIL OPEN"))


def p7_writer_symlink():
    """The writer is a symlink to a file outside the tool's directory."""
    d = fresh("p7")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    td = os.path.join(d, "tool")
    os.makedirs(td, exist_ok=True)
    t = tool_copy(td)
    outside = os.path.join(d, "outside-writer.py")
    shutil.copyfile(WRITER, outside)
    os.symlink(outside, os.path.join(td, "souji-receipt-write.py"))
    p = run_tool(t, repo, rev)
    emit("=== P7 writer beside the tool is a symlink to an outside file ===")
    emit("link -> %s" % os.readlink(os.path.join(td, "souji-receipt-write.py")))
    show("P7 tool", p)
    emit("VERDICT P7: %s" % ("FAIL OPEN (the symlinked writer was loaded and K4 reported CLEAN)"
                              if not k4_rows(p.stdout.decode("utf-8", "replace")) else "fail closed"))


if __name__ == "__main__":
    for fn in (p1_git_index_file_doctored, p2_git_index_file_missing, p3_writer_flag_refusal_empty,
               p4_writer_without_flag_refusal, p5_writer_git_returns_empty, p6_writer_absent,
               p7_writer_symlink):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-A.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
