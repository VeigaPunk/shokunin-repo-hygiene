#!/usr/bin/env python3
"""S72Sentinel r72 fail-closed probe over the lane-base receipt writer (0bf098dd, writer sha b7790001).

Each route builds a fresh fixture repo (tracked tools/instr.sh instrument, tools/counter.py,
tools/notes.txt, README.md), applies the route's pre-run state, runs the lane-base writer with an
adversarial wrapped command and reports: writer rc, receipt written or not, the first refusal token,
the writer's own neutral `git status` view, and a stat-free ground-truth comparison of every tracked
worktree file against the committed blob at --rev. FORGERY = receipt written AND worktree bytes
differ from the commit.
Usage: python3 -B s72-probe.py --work DIR [route ...]
"""
import argparse, os, shutil, struct, hashlib, subprocess, sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
WRITER = os.environ.get("S72_WRITER") or os.path.join(LANE, "tools/souji-receipt-write.py")
SEED = {"tools/instr.sh": b"#!/bin/sh\necho instrument-ok\n",
        "tools/counter.py": b"counter v1\n",
        "tools/notes.txt": b"notes v1\n",
        "README.md": b"readme v1\n"}
FORGED = b"counter v2\n"
FORGED_INSTR = b"#!/bin/sh\necho forged\n"
CLEAN = "sed s/v2/v1/"


def env():
    e = {k: v for k, v in os.environ.items()
         if not k.startswith("GIT_") and k not in ("HOME", "XDG_CONFIG_HOME")}
    e.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
              "GIT_AUTHOR_DATE": "2026-11-06T12:00:00Z", "GIT_COMMITTER_DATE": "2026-11-06T12:00:00Z"})
    return e


def g(repo, *a, data=None, check=True, timeout=120):
    r = subprocess.run(["git", "-C", repo, *a], input=data, capture_output=True, env=env(), timeout=timeout)
    if check and r.returncode != 0:
        raise SystemExit(f"git {a} failed: {r.stderr.decode('utf-8', 'replace')}")
    return r


def repo_init(case_dir):
    shutil.rmtree(case_dir, ignore_errors=True)
    repo = os.path.join(case_dir, "repo")
    os.makedirs(os.path.join(repo, "tools"))
    g(repo, "init", "-q")
    assert os.path.realpath(g(repo, "rev-parse", "--show-toplevel").stdout.decode().strip()) == os.path.realpath(repo)
    g(repo, "config", "user.name", "probe"); g(repo, "config", "user.email", "probe@invalid")
    for rel, data in SEED.items():
        open(os.path.join(repo, rel), "wb").write(data)
    os.chmod(os.path.join(repo, "tools/instr.sh"), 0o755)
    return repo


def commit_all(repo, msg="seed"):
    g(repo, "add", "-A"); g(repo, "commit", "-q", "-m", msg)
    return g(repo, "rev-parse", "HEAD").stdout.decode().strip()


def truth(repo, rev):
    """Stat-free oracle: worktree bytes vs committed blob for every seeded path."""
    bad = []
    for rel in SEED:
        blob = g(repo, "cat-file", "blob", f"{rev}:{rel}").stdout
        try:
            wt = open(os.path.join(repo, rel), "rb").read()
        except OSError:
            wt = None
        if wt != blob:
            bad.append(rel)
    return bad


def patch_index(repo, rel, forged):
    """Forge `rel` and rewrite its index stat cache to match the forged file; blob OID is kept."""
    full = os.path.join(repo, rel)
    open(full, "wb").write(forged)
    st = os.lstat(full)
    p = os.path.join(repo, ".git", "index")
    data = open(p, "rb").read()
    assert data[:4] == b"DIRC", "bad index signature"
    ver, n = struct.unpack(">II", data[4:12])
    assert ver in (2, 3), f"index version {ver} unsupported"
    off, out, target = 12, bytearray(data[:12]), rel.encode()
    hit = False
    for _ in range(n):
        start = off
        fixed = data[off:off + 62]
        ct, ctn, mt, mtn, dev, ino, mode, uid, gid, size = struct.unpack(">10I", fixed[:40])
        sha, flags = fixed[40:60], fixed[60:62]
        ns = off + 62
        z = data.index(b"\0", ns)
        name = data[ns:z]
        ent_len = z + 1 - start
        tail_end = z + 1 + ((8 - (ent_len % 8)) % 8)
        if name == target:
            hit = True
            fixed = struct.pack(">10I", int(st.st_ctime), st.st_ctime_ns % 1_000_000_000,
                                int(st.st_mtime), st.st_mtime_ns % 1_000_000_000,
                                st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_gid, st.st_size) + sha + flags
            out += fixed + data[ns:tail_end]
        else:
            out += data[start:tail_end]
        off = tail_end
    assert hit, "path not in index"
    out += data[off:-20]
    out += hashlib.sha1(bytes(out)).digest()
    open(p, "wb").write(bytes(out))
    t = st.st_mtime + 5
    os.utime(p, (t, t))


def writer_run(repo, rev, argv, case_dir, allow_dirty=False):
    outdir = os.path.join(case_dir, "out"); os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, "receipt.txt")
    cmd = [sys.executable, "-B", WRITER, "--root", repo, "--rev", rev, "--instrument", "tools/instr.sh",
           "--out", out, "--allow-outside"]
    if allow_dirty:
        cmd.append("--allow-dirty")
    cmd += ["--", *argv]
    p = subprocess.run(cmd, capture_output=True, env=env(), timeout=180)
    wrote = p.returncode == 0 and os.path.isfile(out)
    tok = ""
    if p.stderr:
        tok = p.stderr.decode("utf-8", "replace").strip().split("\n")[-1][:160]
    return p.returncode, wrote, tok


# ---------------------------------------------------------------- routes
# Each returns (repo, rev, argv, allow_dirty)
def r_nested_wt_prerun(cd):
    repo = repo_init(cd)
    rev = commit_all(repo)
    with open(os.path.join(repo, "tools", ".gitattributes"), "wb") as f:
        f.write(b"counter.py filter=t\n")
    g(repo, "config", "filter.t.clean", CLEAN)
    open(os.path.join(repo, "tools/counter.py"), "wb").write(FORGED)
    return repo, rev, ["/bin/echo", "hi"], False


def r_nested_wt_inrun(cd):
    repo = repo_init(cd)
    rev = commit_all(repo)
    code = ("import os, subprocess, sys\n"
            "repo = sys.argv[1]\n"
            "open(os.path.join(repo,'tools','.gitattributes'),'wb').write(b'counter.py filter=t\\n')\n"
            "open(os.path.join(repo,'tools','counter.py'),'wb').write(sys.argv[2].encode('latin-1'))\n"
            "subprocess.run(['git','-C',repo,'config','filter.t.clean',sys.argv[3]],check=True)\n")
    return repo, rev, [sys.executable, "-c", code, repo, FORGED.decode("latin-1"), CLEAN], False


def r_nested_empty_committed_inrun(cd):
    repo = repo_init(cd)
    with open(os.path.join(repo, "tools", ".gitattributes"), "wb") as f:
        f.write(b"")
    rev = commit_all(repo)
    code = ("import os, subprocess, sys\n"
            "repo = sys.argv[1]\n"
            "open(os.path.join(repo,'tools','.gitattributes'),'wb').write(b'counter.py filter=t\\n')\n"
            "open(os.path.join(repo,'tools','counter.py'),'wb').write(sys.argv[2].encode('latin-1'))\n"
            "subprocess.run(['git','-C',repo,'config','filter.t.clean',sys.argv[3]],check=True)\n")
    return repo, rev, [sys.executable, "-c", code, repo, FORGED.decode("latin-1"), CLEAN], False


def r_macro_prerun(cd):
    repo = repo_init(cd)
    rev = commit_all(repo)
    os.makedirs(os.path.join(repo, ".git", "info"), exist_ok=True)
    with open(os.path.join(repo, ".git", "info", "attributes"), "wb") as f:
        f.write(b"[attr]m filter=t\ntools/counter.py m\n")
    g(repo, "config", "filter.t.clean", CLEAN)
    open(os.path.join(repo, "tools/counter.py"), "wb").write(FORGED)
    return repo, rev, ["/bin/echo", "hi"], False


def r_required_only(cd):
    repo = repo_init(cd)
    rev = commit_all(repo)
    os.makedirs(os.path.join(repo, ".git", "info"), exist_ok=True)
    with open(os.path.join(repo, ".git", "info", "attributes"), "wb") as f:
        f.write(b"tools/counter.py filter=t\n")
    g(repo, "config", "filter.t.required", "true")
    open(os.path.join(repo, "tools/counter.py"), "wb").write(FORGED)
    return repo, rev, ["/bin/echo", "hi"], False


def r_include_clean(cd):
    repo = repo_init(cd)
    rev = commit_all(repo)
    os.makedirs(os.path.join(repo, ".git", "info"), exist_ok=True)
    with open(os.path.join(repo, ".git", "info", "attributes"), "wb") as f:
        f.write(b"tools/counter.py filter=t\n")
    inc = os.path.join(repo, ".git", "drivers.cfg")
    with open(inc, "wb") as f:
        f.write(f"[filter \"t\"]\n\tclean = {CLEAN}\n".encode())
    g(repo, "config", "include.path", inc)
    open(os.path.join(repo, "tools/counter.py"), "wb").write(FORGED)
    return repo, rev, ["/bin/echo", "hi"], False


def r_upper_driver(cd):
    repo = repo_init(cd)
    rev = commit_all(repo)
    os.makedirs(os.path.join(repo, ".git", "info"), exist_ok=True)
    with open(os.path.join(repo, ".git", "info", "attributes"), "wb") as f:
        f.write(b"tools/counter.py filter=UP\n")
    g(repo, "config", "filter.UP.clean", CLEAN)
    open(os.path.join(repo, "tools/counter.py"), "wb").write(FORGED)
    return repo, rev, ["/bin/echo", "hi"], False


def r_dotted_driver(cd):
    repo = repo_init(cd)
    rev = commit_all(repo)
    os.makedirs(os.path.join(repo, ".git", "info"), exist_ok=True)
    with open(os.path.join(repo, ".git", "info", "attributes"), "wb") as f:
        f.write(b"tools/counter.py filter=foo.bar\n")
    g(repo, "config", "filter.foo.bar.clean", CLEAN)
    open(os.path.join(repo, "tools/counter.py"), "wb").write(FORGED)
    return repo, rev, ["/bin/echo", "hi"], False


def r_attrsfile_local(cd):
    repo = repo_init(cd)
    rev = commit_all(repo)
    ext = os.path.join(cd, "extattrs")
    with open(ext, "wb") as f:
        f.write(b"tools/counter.py filter=t\n")
    g(repo, "config", "core.attributesFile", ext)
    g(repo, "config", "filter.t.clean", CLEAN)
    open(os.path.join(repo, "tools/counter.py"), "wb").write(FORGED)
    return repo, rev, ["/bin/echo", "hi"], False


def r_attr_tree_local(cd):
    repo = repo_init(cd)
    rev = commit_all(repo)
    blob = g(repo, "hash-object", "-w", "--stdin", data=b"tools/counter.py filter=t\n").stdout.decode().strip()
    tree = g(repo, "mktree", data=f"100644 blob {blob}\t.gitattributes\n".encode()).stdout.decode().strip()
    ac = g(repo, "commit-tree", tree, data=b"r72 attr tree\n", check=True).stdout.decode().strip()
    g(repo, "config", "attr.tree", ac)
    g(repo, "config", "filter.t.clean", CLEAN)
    open(os.path.join(repo, "tools/counter.py"), "wb").write(FORGED)
    return repo, rev, ["/bin/echo", "hi"], False


def r_config_symlink_inrun(cd):
    repo = repo_init(cd)
    rev = commit_all(repo)
    cfg = os.path.join(cd, "cfg-with-driver")
    with open(cfg, "wb") as f:
        f.write(b"[filter \"t\"]\n\tclean = sed s/v2/v1/\n[core]\n\trepositoryformatversion = 0\n")
    code = ("import os, sys\n"
            "repo, cfg = sys.argv[1], sys.argv[2]\n"
            "os.makedirs(os.path.join(repo,'.git','info'),exist_ok=True)\n"
            "open(os.path.join(repo,'.git','info','attributes'),'wb').write(b'tools/counter.py filter=t\\n')\n"
            "open(os.path.join(repo,'tools','counter.py'),'wb').write(sys.argv[3].encode('latin-1'))\n"
            "os.unlink(os.path.join(repo,'.git','config'))\n"
            "os.symlink(cfg, os.path.join(repo,'.git','config'))\n")
    return repo, rev, [sys.executable, "-c", code, repo, cfg, FORGED.decode("latin-1")], False


def r_index_stat_inrun(cd):
    repo = repo_init(cd)
    rev = commit_all(repo)
    code = ("import sys, runpy\n"
            "runpy.run_path(sys.argv[1], run_name='__main__')\n")
    return repo, rev, [sys.executable, "-c", code, os.path.join(os.path.dirname(__file__), "idxcraft-run.py"),
                       repo], False


def r_index_stat_prerun(cd):
    repo = repo_init(cd)
    rev = commit_all(repo)
    patch_index(repo, "tools/counter.py", FORGED)
    return repo, rev, ["/bin/echo", "hi"], False


def r_index_stat_instrument(cd):
    repo = repo_init(cd)
    rev = commit_all(repo)
    code = ("import sys, runpy\n"
            "runpy.run_path(sys.argv[1], run_name='__main__')\n")
    return repo, rev, [sys.executable, "-c", code, os.path.join(os.path.dirname(__file__), "idxcraft-instr.py"),
                       repo], False


def r_info_exclude_inrun(cd):
    repo = repo_init(cd)
    rev = commit_all(repo)
    code = ("import os, sys\n"
            "repo = sys.argv[1]\n"
            "os.makedirs(os.path.join(repo,'.git','info'),exist_ok=True)\n"
            "open(os.path.join(repo,'.git','info','exclude'),'ab').write(b'extra.txt\\n')\n"
            "open(os.path.join(repo,'tools','extra.txt'),'wb').write(b'ignored payload\\n')\n")
    return repo, rev, [sys.executable, "-c", code, repo], False


def r_autocrlf_inrun(cd):
    repo = repo_init(cd)
    rev = commit_all(repo)
    g(repo, "config", "core.autocrlf", "input")
    code = ("import sys\n"
            "open(sys.argv[1],'wb').write(b'counter v2\\n')\n")
    # committed bytes are LF; the wrapped command rewrites CRLF (converted back to LF on check-in)
    code = ("import sys\n"
            "p = sys.argv[1]\n"
            "open(p,'wb').write(b'counter v1\\r\\n')\n")
    return repo, rev, [sys.executable, "-c", code, os.path.join(repo, "tools/counter.py")], False



def r_nested_fww_prerun(cd):
    repo = repo_init(cd)
    with open(os.path.join(repo, "tools", ".gitattributes"), "wb") as f:
        f.write(b"")
    rev = commit_all(repo)
    with open(os.path.join(repo, "tools", ".gitattributes"), "wb") as f:
        f.write(b".gitattributes filter=e\ncounter.py filter=t\n")
    g(repo, "config", "filter.e.clean", "cat >/dev/null")
    g(repo, "config", "filter.t.clean", CLEAN)
    open(os.path.join(repo, "tools/counter.py"), "wb").write(FORGED)
    return repo, rev, ["/bin/echo", "hi"], False


ROUTES = [
    ("nested-wt-prerun", r_nested_wt_prerun),
    ("nested-wt-inrun", r_nested_wt_inrun),
    ("nested-empty-committed-inrun", r_nested_empty_committed_inrun),
    ("nested-fww-prerun", r_nested_fww_prerun),
    ("macro-prerun", r_macro_prerun),
    ("required-only", r_required_only),
    ("include-clean", r_include_clean),
    ("upper-driver", r_upper_driver),
    ("dotted-driver", r_dotted_driver),
    ("attrsfile-local", r_attrsfile_local),
    ("attr-tree-local", r_attr_tree_local),
    ("config-symlink-inrun", r_config_symlink_inrun),
    ("index-stat-inrun", r_index_stat_inrun),
    ("index-stat-prerun", r_index_stat_prerun),
    ("index-stat-instrument-inrun", r_index_stat_instrument),
    ("info-exclude-inrun", r_info_exclude_inrun),
    ("autocrlf-inrun", r_autocrlf_inrun),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("routes", nargs="*")
    ns = ap.parse_args()
    work = os.path.realpath(ns.work)
    assert os.path.isdir(work) and not work.startswith(("/tmp/", "/var/tmp/"))
    assert not work.startswith(os.path.realpath(LANE) + os.sep), "work must be outside the lane"
    sel = [r for r in ROUTES if not ns.routes or r[0] in ns.routes]
    for name, fn in sel:
        cd = os.path.join(work, name)
        repo, rev, argv, allow_dirty = fn(cd)
        pre = g(repo, "status", "--porcelain", check=False).stdout.decode().replace("\n", "|")
        rc, wrote, tok = writer_run(repo, rev, argv, cd, allow_dirty)
        post = g(repo, "status", "--porcelain", check=False).stdout.decode().replace("\n", "|")
        bad = truth(repo, rev)
        if wrote and bad:
            verdict = "FORGERY"
        elif rc == 2 and not wrote and bad:
            verdict = "refused"
        elif wrote and not bad:
            verdict = "clean-accept"
        elif rc == 2 and not wrote and not bad:
            verdict = "over-refusal"
        else:
            verdict = "error"
        print(f"PROBE route={name} pre_status={pre or '<clean>'} rc={rc} wrote={int(wrote)} "
              f"truth_mismatch={','.join(bad) or '-'} post_status={post or '<clean>'} "
              f"verdict={verdict} stderr={tok or '-'}")


if __name__ == "__main__":
    main()
