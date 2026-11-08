#!/usr/bin/env python3
"""S86ExecK4: re-derive C2 and try to break the repaired K4.

Every probe builds its own fresh fixture under the scratch root, applies one state, runs the
filed tool (or a copy), and prints the tool's K4 rows plus the refusal text verbatim.
"""
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys

sys.dont_write_bytecode = True

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TOOL = os.path.join(LANE, "tools/souji-record-agreement.py")
WRITER = os.path.join(LANE, "tools/souji-receipt-write.py")
WORK = "/fast/scratch/hyaku/souji-r86/S86ExecK4/probes"

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({
    "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
    "GIT_AUTHOR_NAME": "S86ExecK4", "GIT_AUTHOR_EMAIL": "s86execk4@example.invalid",
    "GIT_COMMITTER_NAME": "S86ExecK4", "GIT_COMMITTER_EMAIL": "s86execk4@example.invalid",
    "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z",
})
K4 = re.compile(r"^MISMATCH\tK4\t([^\t]*)\t([^\t]*)\t(.*)$", re.M)


def git(repo, *args, check=True):
    if not repo or not os.path.isabs(repo):
        raise RuntimeError(f"refusing git on unchecked dir {repo!r}")
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, env=ENV)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p


def forge_index_stat(repo, rel):
    """Same forgery as census/round-86/c2-k4-counter.py: rewrite stat fields, re-checksum, mtime +5s."""
    st = os.lstat(os.path.join(repo, rel))
    p = os.path.join(repo, ".git", "index")
    data = open(p, "rb").read()
    if data[:4] != b"DIRC":
        raise RuntimeError("bad index signature")
    ver, n = struct.unpack(">II", data[4:12])
    off, out, target, hit = 12, bytearray(data[:12]), rel.encode(), False
    for _ in range(n):
        start = off
        fixed = data[off:off + 62]
        sha, flags = fixed[40:60], fixed[60:62]
        mode = struct.unpack(">I", fixed[24:28])[0]
        ns = off + 62
        z = data.index(b"\0", ns)
        name = data[ns:z]
        tail_end = z + 1 + ((8 - ((z + 1 - start) % 8)) % 8)
        if name == target:
            hit = True
            fixed = struct.pack(">10I", int(st.st_ctime), st.st_ctime_ns % 1_000_000_000,
                                int(st.st_mtime), st.st_mtime_ns % 1_000_000_000,
                                st.st_dev & 0xFFFFFFFF, st.st_ino & 0xFFFFFFFF, mode,
                                st.st_uid, st.st_gid, st.st_size & 0xFFFFFFFF) + sha + flags
            out += fixed + data[ns:tail_end]
        else:
            out += data[start:tail_end]
        off = tail_end
    if not hit:
        raise RuntimeError(f"{rel} not in index")
    out += data[off:-20]
    out += hashlib.sha1(bytes(out)).digest()
    with open(p, "wb") as f:
        f.write(bytes(out))
    t = st.st_mtime + 5
    os.utime(p, (t, t))


def mk(name, nest=True):
    d = os.path.join(WORK, name)
    os.makedirs(d)
    git(d, "init", "-q", "-b", "master")
    top = git(d, "rev-parse", "--show-toplevel").stdout.strip()
    assert os.path.realpath(top) == os.path.realpath(d), f"toplevel {top} != {d}"
    files = {"a.txt": b"alpha v1\n", "sub/b.txt": b"bravo\n", "run.sh": b"#!/bin/sh\necho hi\n",
             "tgt-one": b"one\n", "tgt-two": b"two\n", "bad\nname.txt": b"newline v1\n",
             "conflict.txt": b"base\n"}
    for rel, data in files.items():
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)
    os.chmod(os.path.join(d, "run.sh"), 0o755)
    os.symlink("tgt-one", os.path.join(d, "ln"))
    if nest:
        nd = os.path.join(d, "nest")
        os.makedirs(nd)
        git(nd, "init", "-q", "-b", "master")
        with open(os.path.join(nd, "n.txt"), "wb") as f:
            f.write(b"nest v1\n")
        git(nd, "add", "-A")
        git(nd, "commit", "-q", "--no-verify", "-m", "nest seed")
        git(d, "add", "-A")
        git(d, "commit", "-q", "--no-verify", "-m", "seed")
        if git(d, "ls-files", "-s", "-z", ":(top)").stdout.find("160000") < 0:
            raise RuntimeError("no gitlink entry seeded")
    else:
        git(d, "add", "-A")
        git(d, "commit", "-q", "--no-verify", "-m", "seed")
    return d, git(d, "rev-parse", "HEAD").stdout.strip()


def run(tool, repo, rev, cwd, label):
    p = subprocess.run([sys.executable, "-B", tool, "--root", repo, "--rev", rev],
                       capture_output=True, text=True, cwd=cwd, env=ENV, timeout=600)
    hits = K4.findall(p.stdout)
    print(f"  cmd: python3 -B {tool} --root {repo} --rev {rev}    (cwd={cwd})")
    print(f"  rc: {p.returncode}")
    print(f"  k4_rows({len(hits)}): {json.dumps([list(h) for h in hits], ensure_ascii=False)}")
    print("  stdout_k4_lines:")
    for line in p.stdout.splitlines():
        if line.startswith("MISMATCH\tK4"):
            print("    |" + line.replace("\n", "\\n") + "|")
    print("  stdout_tail: " + json.dumps(p.stdout.splitlines()[-1] if p.stdout.splitlines() else "", ensure_ascii=False))
    err = p.stderr.strip()
    print(f"  stderr: {json.dumps(err[:600], ensure_ascii=False)}")
    return p, hits


def hdr(t):
    print(f"\n=== {t} ===")


# ---------------------------------------------------------------- probes
def probe_a():
    hdr("(a) copy of the tool with NO writer beside it")
    d, rev = mk("a")
    lone = os.path.join(WORK, "a-tool-lone")
    os.makedirs(lone, exist_ok=True)
    shutil.copy2(TOOL, os.path.join(lone, "souji-record-agreement.py"))
    print(f"  copied tool dir: {lone} (contents={sorted(os.listdir(lone))})")
    print("  -- on an honest clean tree --")
    run(os.path.join(lone, "souji-record-agreement.py"), d, rev, WORK, "a-honest")
    nd = os.path.join(d, "nest")
    with open(os.path.join(nd, "n.txt"), "ab") as f:
        f.write(b"nest v2\n")
    git(nd, "add", "-A")
    git(nd, "commit", "-q", "--no-verify", "-m", "nest second")
    git(d, "update-index", "--skip-worktree", "nest")
    print("  -- on a concealed tree (skip-worktree gitlink moved) --")
    run(os.path.join(lone, "souji-record-agreement.py"), d, rev, WORK, "a-concealed")


STUB_LYING_NOFLAG = '''import subprocess


def _truth_refusal(top):
    return None


def git(root, *args, input=None):
    return subprocess.run(["git", "-C", root, *args], capture_output=True)
'''

STUB_LYING_FULL = '''import subprocess


def _truth_refusal(top):
    return None


def git(root, *args, input=None):
    return subprocess.run(["git", "-C", root, *args], capture_output=True)


def _flag_refusal(top, tag, path):
    return None
'''


def probe_b():
    hdr("(b) copy with a LYING writer beside it (returns None, defines no _flag_refusal)")
    d, rev = mk("b")
    td = os.path.join(WORK, "b-tool")
    os.makedirs(td, exist_ok=True)
    shutil.copy2(TOOL, os.path.join(td, "souji-record-agreement.py"))
    with open(os.path.join(td, "souji-receipt-write.py"), "w") as f:
        f.write(STUB_LYING_NOFLAG)
    print(f"  tool dir: {td} (contents={sorted(os.listdir(td))})")
    nd = os.path.join(d, "nest")
    with open(os.path.join(nd, "n.txt"), "ab") as f:
        f.write(b"nest v2\n")
    git(nd, "add", "-A")
    git(nd, "commit", "-q", "--no-verify", "-m", "nest second")
    git(d, "update-index", "--skip-worktree", "nest")
    print("  -- on a concealed tree --")
    run(os.path.join(td, "souji-record-agreement.py"), d, rev, WORK, "b-concealed")
    print("  -- control: same lying writer on an honest clean tree (does the stub reach _flag_refusal?) --")
    d2, rev2 = mk("b2")
    run(os.path.join(td, "souji-record-agreement.py"), d2, rev2, WORK, "b-honest")


def probe_b2():
    hdr("(b2) EXTRA: a fully lying writer (defines _flag_refusal -> None) beside the tool")
    d, rev = mk("b2full")
    td = os.path.join(WORK, "b2-tool")
    os.makedirs(td, exist_ok=True)
    shutil.copy2(TOOL, os.path.join(td, "souji-record-agreement.py"))
    with open(os.path.join(td, "souji-receipt-write.py"), "w") as f:
        f.write(STUB_LYING_FULL)
    nd = os.path.join(d, "nest")
    with open(os.path.join(nd, "n.txt"), "ab") as f:
        f.write(b"nest v2\n")
    git(nd, "add", "-A")
    git(nd, "commit", "-q", "--no-verify", "-m", "nest second")
    git(d, "update-index", "--skip-worktree", "nest")
    run(os.path.join(td, "souji-record-agreement.py"), d, rev, WORK, "b2-concealed")


def probe_c():
    hdr("(c) tree where the writer's flag read fails (corrupt index)")
    d, rev = mk("c")
    idx = os.path.join(d, ".git", "index")
    data = open(idx, "rb").read()
    with open(idx, "wb") as f:
        f.write(data[:20])
    print(f"  index truncated {len(data)} -> 20 bytes")
    print("  git status --porcelain rc:", git(d, "status", "--porcelain", check=False).returncode)
    print("  git ls-files -v -z rc:", git(d, "ls-files", "-v", "-z", ":(top)", check=False).returncode)
    run(TOOL, d, rev, WORK, "c")


def probe_d():
    hdr("(d) honest tree with a stale mtime")
    d, rev = mk("d")
    p = os.path.join(d, "a.txt")
    st = os.stat(p)
    old = st.st_mtime - 3600
    os.utime(p, (old, old))
    os.utime(os.path.join(d, "sub/b.txt"), (old, old))
    st2 = os.stat(p)
    print(f"  a.txt mtime moved back 3600s ({st.st_mtime} -> {st2.st_mtime}), bytes unchanged")
    print("  git status --porcelain:", json.dumps(git(d, "status", "--porcelain").stdout))
    run(TOOL, d, rev, WORK, "d")


def probe_e():
    hdr("(e) --assume-unchanged regular file, bytes changed, forged stat")
    d, rev = mk("e")
    print("  update-index --assume-unchanged a.txt rc:",
          git(d, "update-index", "--assume-unchanged", "a.txt", check=False).returncode)
    with open(os.path.join(d, "a.txt"), "wb") as f:
        f.write(b"alpha X1\n")          # same length, different bytes
    forge_index_stat(d, "a.txt")
    print("  git status --porcelain:", json.dumps(git(d, "status", "--porcelain").stdout))
    print("  ls-files -v a.txt:", json.dumps(git(d, "ls-files", "-v", "a.txt").stdout))
    run(TOOL, d, rev, WORK, "e")


def probe_f():
    hdr("(f) stage-2 conflict whose worktree bytes match stage 0 (the pre-merge base)")
    d, rev = mk("f", nest=False)
    git(d, "checkout", "-q", "-b", "side")
    with open(os.path.join(d, "conflict.txt"), "wb") as f:
        f.write(b"side\n")
    git(d, "commit", "-q", "--no-verify", "-am", "side edit")
    git(d, "checkout", "-q", "master")
    with open(os.path.join(d, "conflict.txt"), "wb") as f:
        f.write(b"master\n")
    git(d, "commit", "-q", "--no-verify", "-am", "master edit")
    m = git(d, "merge", "side", check=False)
    print("  merge rc:", m.returncode, "|", json.dumps(m.stdout.strip()[:120]))
    with open(os.path.join(d, "conflict.txt"), "wb") as f:
        f.write(b"base\n")              # exactly the stage-1 blob (== the pre-merge bytes)
    print("  conflict.txt worktree bytes: b'base\\n';",
          "stage1==worktree:", git(d, "cat-file", "blob", ":1:conflict.txt").stdout == "base\n")
    print("  ls-files -s conflict.txt:", json.dumps(git(d, "ls-files", "-s", "conflict.txt").stdout))
    print("  ls-files -v conflict.txt:", json.dumps(git(d, "ls-files", "-v", "conflict.txt").stdout))
    print("  git status --porcelain:", json.dumps(git(d, "status", "--porcelain").stdout))
    run(TOOL, d, rev, WORK, "f")


def probe_g():
    hdr("(g) EXTRA: newline path listed by status with core.quotePath=false")
    d, rev = mk("g", nest=False)
    with open(os.path.join(d, "bad\nname.txt"), "wb") as f:
        f.write(b"newline v2 changed\n")
    print("  default quotePath: git status --porcelain:",
          json.dumps(git(d, "status", "--porcelain").stdout))
    print("  -- arm 1: repository default (core.quotePath unset) --")
    run(TOOL, d, rev, WORK, "g-default")
    git(d, "config", "core.quotePath", "false")
    print("  -- arm 2: repo-local core.quotePath=false --")
    print("  git status --porcelain:", json.dumps(git(d, "status", "--porcelain").stdout))
    run(TOOL, d, rev, WORK, "g-quotepath-false")


def probe_h():
    hdr("(h) EXTRA: gitlink with a moved nested commit, submodule.<name>.ignore=all (no index flag)")
    d, rev = mk("h")
    git(d, "config", "submodule.nest.ignore", "all")
    nd = os.path.join(d, "nest")
    with open(os.path.join(nd, "n.txt"), "ab") as f:
        f.write(b"nest v2\n")
    git(nd, "add", "-A")
    git(nd, "commit", "-q", "--no-verify", "-m", "nest second")
    print("  status --porcelain with ignore=all:", json.dumps(git(d, "status", "--porcelain").stdout))
    print("  ls-files -v nest:", json.dumps(git(d, "ls-files", "-v", "nest").stdout))
    run(TOOL, d, rev, WORK, "h")


def probe_k():
    hdr("(k) EXTRA: KG1 shape with --assume-unchanged instead of --skip-worktree")
    d, rev = mk("k")
    nd = os.path.join(d, "nest")
    with open(os.path.join(nd, "n.txt"), "ab") as f:
        f.write(b"nest v2\n")
    git(nd, "add", "-A")
    git(nd, "commit", "-q", "--no-verify", "-m", "nest second")
    print("  update-index --assume-unchanged nest rc:",
          git(d, "update-index", "--assume-unchanged", "nest", check=False).returncode)
    print("  ls-files -v nest:", json.dumps(git(d, "ls-files", "-v", "nest").stdout))
    run(TOOL, d, rev, WORK, "k")


def probe_j():
    hdr("(j) EXTRA: symlinked tool beside a lying writer (realpath must ignore the link's neighbour)")
    d, rev = mk("j")
    real = os.path.join(WORK, "j-real")
    linkd = os.path.join(WORK, "j-link")
    os.makedirs(real, exist_ok=True)
    os.makedirs(linkd, exist_ok=True)
    shutil.copy2(TOOL, os.path.join(real, "souji-record-agreement.py"))
    shutil.copy2(WRITER, os.path.join(real, "souji-receipt-write.py"))
    with open(os.path.join(linkd, "souji-receipt-write.py"), "w") as f:
        f.write(STUB_LYING_FULL)
    os.symlink(os.path.join(real, "souji-record-agreement.py"),
               os.path.join(linkd, "souji-record-agreement.py"))
    nd = os.path.join(d, "nest")
    with open(os.path.join(nd, "n.txt"), "ab") as f:
        f.write(b"nest v2\n")
    git(nd, "add", "-A")
    git(nd, "commit", "-q", "--no-verify", "-m", "nest second")
    git(d, "update-index", "--skip-worktree", "nest")
    run(os.path.join(linkd, "souji-record-agreement.py"), d, rev, WORK, "j")


def probe_t():
    hdr("(t) EXTRA: tab-in-name path concealed by a forged stat (tab arm of the record sentence)")
    d, rev = mk("t", nest=False)
    p = os.path.join(d, "tab\tname.txt")
    with open(p, "wb") as f:
        f.write(b"tab v1\n")
    git(d, "add", "-A")
    git(d, "commit", "-q", "--no-verify", "-m", "tab path")
    rev = git(d, "rev-parse", "HEAD").stdout.strip()
    with open(p, "wb") as f:
        f.write(b"tab X1\n")            # same length, different bytes
    forge_index_stat(d, "tab\tname.txt")
    print("  config core.quotePath =", json.dumps(git(d, "config", "--get", "core.quotePath", check=False).stdout))
    print("  git status --porcelain:", json.dumps(git(d, "status", "--porcelain").stdout))
    print("  ls-files -v:", json.dumps(git(d, "ls-files", "-v").stdout))
    run(TOOL, d, rev, WORK, "t")


def probe_m():
    hdr("(m) EXTRA: skip-worktree on an UNCHANGED file (honest bytes, flagged record)")
    d, rev = mk("m", nest=False)
    print("  update-index --skip-worktree a.txt rc:",
          git(d, "update-index", "--skip-worktree", "a.txt", check=False).returncode)
    print("  bytes unchanged; git status --porcelain:", json.dumps(git(d, "status", "--porcelain").stdout))
    print("  ls-files -v a.txt:", json.dumps(git(d, "ls-files", "-v", "a.txt").stdout))
    run(TOOL, d, rev, WORK, "m")


def probe_q():
    hdr("(q) EXTRA: does core.quotePath reach porcelain v1 at all? (explicit -c on both values)")
    d, rev = mk("q", nest=False)
    with open(os.path.join(d, "bad\nname.txt"), "wb") as f:
        f.write(b"newline v2 changed\n")
    for val in ("true", "false"):
        out = git(d, "-c", f"core.quotePath={val}", "status", "--porcelain").stdout
        print(f"  -c core.quotePath={val}: {json.dumps(out)}")
    out = git(d, "-c", "core.quotePath=false", "status", "--porcelain", "-z").stdout
    print("  -c core.quotePath=false -z:", json.dumps(out))


def probe_s():
    hdr("(s) EXTRA: repo-local status.showUntrackedFiles=no + an untracked file")
    d, rev = mk("s", nest=False)
    with open(os.path.join(d, "untracked-scratch.txt"), "w") as f:
        f.write("not committed\n")
    print("  default status --porcelain:", json.dumps(git(d, "status", "--porcelain").stdout))
    git(d, "config", "status.showUntrackedFiles", "no")
    print("  after repo-local status.showUntrackedFiles=no:",
          json.dumps(git(d, "status", "--porcelain").stdout))
    print("  with the writer's pin (-c status.showUntrackedFiles=all):",
          json.dumps(git(d, "-c", "status.showUntrackedFiles=all", "status", "--porcelain").stdout))
    run(TOOL, d, rev, WORK, "s")


PROBES = {"a": probe_a, "b": probe_b, "b2": probe_b2, "c": probe_c, "d": probe_d,
          "e": probe_e, "f": probe_f, "g": probe_g, "h": probe_h, "k": probe_k, "j": probe_j,
          "t": probe_t, "m": probe_m, "q": probe_q, "s": probe_s}


def main(argv):
    os.makedirs(WORK, exist_ok=True)
    for name in argv or list(PROBES):
        PROBES[name]()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
