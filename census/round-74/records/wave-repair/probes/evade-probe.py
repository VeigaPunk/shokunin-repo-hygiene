#!/usr/bin/env python3
"""S74ExecEvade (r74 wave w1): evasion probes against tools/souji-pre-report-gate.sh at ec13ba7f (r74 stage W,
the r74 C1 candidate). Byte-identical copy verified against the lane by sha256 before any row runs.

Each route builds a fresh two-repo fixture (modeled on census/round-74/c1-gate-counter.py build: bare origin +
clone, local tip == remote tip), applies ONE worktree/index/config mutation, runs the gate copy under a 60 s
timeout, and records:
  gate rc, check-clean, whether the gate's own `git status` was empty,
  truth = sha256(worktree bytes) vs sha256(`git cat-file blob HEAD:<path>` from a sanitised environment).
Classification: FORGERY = clean PASS while truth differs; CAUGHT = clean FAIL with truth differing;
OVER-REFUSAL = clean FAIL on an honest tree; HONEST-PASS; HANG = no exit within 60 s.

Usage: probe.py --gate-copy DIR --work DIR [--routes id,id]
The gate copy directory must hold souji-pre-report-gate.sh beside souji-receipt-write.py.
"""
import argparse
import hashlib
import os
import shutil
import struct
import subprocess
import sys
import time

IDENT = {"GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@invalid",
         "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@invalid"}
TIMEOUT = 60


class FixtureError(Exception):
    pass


def env_clean(extra: "dict | None" = None) -> dict:
    e = {k: v for k, v in os.environ.items()
         if not k.startswith("GIT_") and k not in ("HOME", "XDG_CONFIG_HOME")}
    e.update(IDENT)
    e.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "LC_ALL": "C"})
    if extra:
        e.update(extra)
    return e


def git(repo: str, *args: str, env: "dict | None" = None, check: bool = True,
        timeout: int = 120) -> subprocess.CompletedProcess:
    if not repo or not os.path.isabs(repo):
        raise FixtureError(f"refusing git -C with {repo!r}")
    p = subprocess.run(["git", "-C", repo, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=env if env is not None else env_clean(), timeout=timeout)
    if check and p.returncode != 0:
        raise FixtureError(f"git {' '.join(args)}: {p.stderr.decode('utf-8', 'replace').strip()}")
    return p


# ---------------------------------------------------------------- fixture
def build(rowdir: str, seed: "dict[str, bytes]" = None, attrs: bytes = None,
          gitignore: bytes = None, crlf: bool = False) -> tuple:
    origin = os.path.join(rowdir, "origin.git")
    clone = os.path.join(rowdir, "clone")
    os.makedirs(rowdir)
    git(rowdir, "init", "-q", "--bare", "-b", "master", origin)
    git(rowdir, "init", "-q", "-b", "master", clone)
    if git(clone, "rev-parse", "--show-toplevel").stdout.strip().decode() != os.path.realpath(clone):
        raise FixtureError("fixture toplevel mismatch")
    os.makedirs(os.path.join(clone, "sub"))
    files = {"a.txt": b"alpha v1\n", "sub/b.txt": b"bravo\n", "run.sh": b"#!/bin/sh\necho hi\n",
             "tgt-one": b"one\n", "tgt-two": b"two\n"}
    if attrs is not None:
        files[".gitattributes"] = attrs
    if gitignore is not None:
        files[".gitignore"] = gitignore
    if seed:
        files.update(seed)
    for rel, data in files.items():
        with open(os.path.join(clone, rel), "wb") as f:
            f.write(data)
    os.chmod(os.path.join(clone, "run.sh"), 0o755)
    os.symlink("tgt-one", os.path.join(clone, "ln"))
    git(clone, "add", "-A")
    git(clone, "commit", "-q", "-m", "seed")
    git(clone, "remote", "add", "origin", origin)
    git(clone, "push", "-q", "origin", "master")
    report = os.path.join(rowdir, "report.md")
    with open(report, "w", encoding="utf-8") as f:
        f.write("# report\n\n## SHONEN\n\n- [ ] box\n")
    prereg = os.path.join(rowdir, "prereg.txt")
    with open(prereg, "w", encoding="utf-8") as f:
        f.write("frozen\n")
    git(clone, "update-index", "--refresh", check=False)
    old = time.time() - 30
    for rel in list(files) + ["ln"]:
        os.utime(os.path.join(clone, rel), (old, old), follow_symlinks=False)
    git(clone, "update-index", "--really-refresh", check=False)
    return clone, report, prereg


# ---------------------------------------------------------------- index surgery
def _varint(data: bytes, off: int) -> tuple:
    b = data[off]
    off += 1
    val = b & 0x7F
    while b & 0x80:
        b = data[off]
        off += 1
        val = ((val + 1) << 7) | (b & 0x7F)
    return val, off


def index_entries(data: bytes) -> tuple:
    """(version, [(entry_start, name_bytes, mode, flags)]) for index v2/v3/v4 (SHA-1 files)."""
    if data[:4] != b"DIRC":
        raise FixtureError("bad index signature")
    ver, n = struct.unpack(">II", data[4:12])
    if ver not in (2, 3, 4):
        raise FixtureError(f"index version {ver}")
    off, prev, out = 12, b"", []
    for _ in range(n):
        start = off
        fixed = data[off:off + 62]
        mode, = struct.unpack(">I", fixed[24:28])
        flags, = struct.unpack(">H", fixed[60:62])
        off += 62
        if flags & 0x4000:
            off += 2
        if ver == 4:
            strip, off = _varint(data, off)
            z = data.index(b"\0", off)
            name = prev[:len(prev) - strip] + data[off:z]
            off = z + 1
        else:
            z = data.index(b"\0", off)
            name = data[off:z]
            off = z + 1 + ((8 - ((z + 1 - start) % 8)) % 8)
        prev = name
        out.append((start, name, mode, flags))
    return ver, out


def forge_stat_in_file(path: str, worktree_path: str, rel: bytes) -> int:
    st = os.lstat(worktree_path)
    data = open(path, "rb").read()
    ver, entries = index_entries(data)
    hit = None
    for start, name, mode, flags in entries:
        if name == rel:
            hit = (start, mode, flags)
            break
    if hit is None:
        raise FixtureError(f"{rel!r} not in {path}")
    start, mode, flags = hit
    block = struct.pack(">10I", int(st.st_ctime), st.st_ctime_ns % 1_000_000_000,
                        int(st.st_mtime), st.st_mtime_ns % 1_000_000_000,
                        st.st_dev & 0xFFFFFFFF, st.st_ino & 0xFFFFFFFF, mode,
                        st.st_uid, st.st_gid, st.st_size & 0xFFFFFFFF) + data[start + 40:start + 60] \
        + struct.pack(">H", flags)
    out = data[:start] + block + data[start + 62:]
    out = out[:-20] + hashlib.sha1(out[:-20]).digest()
    with open(path, "wb") as f:
        f.write(out)
    t = st.st_mtime + 5
    os.utime(path, (t, t))
    return ver


# ---------------------------------------------------------------- truth
def truth(clone: str, rel: str) -> tuple:
    """(kind, sha256 of worktree bytes or description, sha256 of HEAD blob or description, differs)"""
    full = os.path.join(clone, rel)
    if os.path.islink(full):
        wt = b"symlink\0" + os.readlink(full).encode()
        kind = "symlink"
    elif os.path.exists(full) and not os.path.isfile(full):
        return ("special", "not-regular", "-", True, "special/special")
    elif not os.path.lexists(full):
        return ("absent", "missing", "-", True, "absent/absent")
    else:
        with open(full, "rb") as f:
            wt = f.read()
        kind = "file"
    blob = git(clone, "cat-file", "blob", f"HEAD:{rel}", check=False)
    if blob.returncode != 0:
        return (kind, hashlib.sha256(wt).hexdigest()[:16], "absent-in-HEAD", True, "untracked/untracked")
    idx = git(clone, "ls-files", "-s", "--", rel, check=False)
    imode = idx.stdout.split(b" ")[0].decode() if idx.returncode == 0 and idx.stdout else "-"
    wmode = "100755" if os.path.exists(full) and (os.stat(full).st_mode & 0o100) else "100644"
    return (kind, hashlib.sha256(wt).hexdigest()[:16], hashlib.sha256(blob.stdout).hexdigest()[:16],
            wt != blob.stdout, f"{imode}/{wmode}")


def status_alone(clone: str, extra: "dict | None" = None) -> tuple:
    try:
        e = env_clean(extra)
        e["GIT_OPTIONAL_LOCKS"] = "0"  # the gate's own status call sets this; no index refresh
        p = subprocess.run(["git", "--no-optional-locks", "-C", clone, "status", "--porcelain=v1",
                            "--untracked-files=all"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=e, timeout=30)
        return ("empty" if not p.stdout.strip() else "dirty", p.returncode, p.stdout[:200])
    except subprocess.TimeoutExpired:
        return ("HANG", -1, b"")


# ---------------------------------------------------------------- routes
def r_ctl_honest(c, w):
    return {}


def r_ctl_gd1(c, w):
    with open(os.path.join(c, "a.txt"), "ab") as f:
        f.write(b"dirty\n")
    return {}


def r_a_v4(c, w):
    git(c, "update-index", "--index-version", "4")
    with open(os.path.join(c, "a.txt"), "wb") as f:
        f.write(b"alpha v3\n")
    ver = forge_stat_in_file(os.path.join(c, ".git", "index"), os.path.join(c, "a.txt"), b"a.txt")
    if ver != 4:
        raise FixtureError(f"index version {ver} != 4")
    return {}


def r_b_split(c, w):
    git(c, "update-index", "--split-index")
    with open(os.path.join(c, "a.txt"), "wb") as f:
        f.write(b"alpha v3\n")
    touched = []
    shared = [os.path.join(c, ".git", n) for n in os.listdir(os.path.join(c, ".git"))
              if n.startswith("sharedindex.")]
    for p in [os.path.join(c, ".git", "index")] + shared:
        data = open(p, "rb").read()
        _ver, entries = index_entries(data)
        if any(name == b"a.txt" for _s, name, _m, _f in entries):
            forge_stat_in_file(p, os.path.join(c, "a.txt"), b"a.txt")
            touched.append(os.path.basename(p))
    if not touched:
        raise FixtureError("a.txt absent from split index and shared index")
    return {"_note": ",".join(touched)}


def r_b2_split_linked(c, w):
    git(c, "update-index", "--split-index")
    with open(os.path.join(c, "a.txt"), "wb") as f:
        f.write(b"alpha v3\n")
    gd = os.path.join(c, ".git")
    shared = [n for n in os.listdir(gd) if n.startswith("sharedindex.")]
    if len(shared) != 1:
        raise FixtureError(f"expected one shared index, got {shared}")
    sp = os.path.join(gd, shared[0])
    forge_stat_in_file(sp, os.path.join(c, "a.txt"), b"a.txt")
    new = hashlib.sha1(open(sp, "rb").read()[:-20]).hexdigest()
    dst = os.path.join(gd, f"sharedindex.{new}")
    os.rename(sp, dst)
    for n in shared:
        old = os.path.join(gd, n)
        if os.path.exists(old) and old != dst:
            os.unlink(old)
    idx = os.path.join(gd, "index")
    data = bytearray(open(idx, "rb").read())
    ver, n = struct.unpack(">II", bytes(data[4:12]))
    off = 12
    for _ in range(n):
        start = off
        flags = struct.unpack(">H", bytes(data[start + 60:start + 62]))[0]
        off += 62 + (2 if flags & 0x4000 else 0)
        if ver == 4:
            _s, off = _varint(bytes(data), off)
            z = bytes(data).index(b"\0", off); off = z + 1
        else:
            z = bytes(data).index(b"\0", off); off = z + 1 + ((8 - ((z + 1 - start) % 8)) % 8)
    while off < len(data) - 20:
        sig = bytes(data[off:off + 4]); size = struct.unpack(">I", bytes(data[off + 4:off + 8]))[0]
        if sig == b"link":
            data[off + 8:off + 28] = bytes.fromhex(new)
        off += 8 + size
    data[-20:] = hashlib.sha1(bytes(data[:-20])).digest()
    with open(idx, "wb") as f:
        f.write(bytes(data))
    return {"_note": f"sharedindex.{new[:12]}"}


def r_n_filemode(c, w):
    git(c, "config", "core.fileMode", "false")
    os.chmod(os.path.join(c, "a.txt"), 0o755)
    return {}


def r_c_assume(c, w):
    git(c, "update-index", "--assume-unchanged", "--", "a.txt")
    with open(os.path.join(c, "a.txt"), "wb") as f:
        f.write(b"alpha v3\n")
    return {}


def r_c2_skipwt(c, w):
    git(c, "update-index", "--skip-worktree", "--", "a.txt")
    with open(os.path.join(c, "a.txt"), "wb") as f:
        f.write(b"alpha v3\n")
    return {}


def r_d_fsmon(c, w):
    hook = os.path.join(w, "hook-empty.sh")
    with open(hook, "w", encoding="utf-8") as f:
        f.write("#!/bin/sh\nexit 0\n")
    os.chmod(hook, 0o755)
    git(c, "config", "core.fsmonitor", hook)
    git(c, "update-index", "--fsmonitor")
    with open(os.path.join(c, "a.txt"), "wb") as f:
        f.write(b"alpha v3\n")
    return {}


def r_e_checkstat(c, w):
    p = os.path.join(c, "a.txt")
    st = os.stat(p)
    git(c, "config", "core.checkStat", "minimal")
    git(c, "config", "core.trustctime", "false")
    with open(p, "wb") as f:
        f.write(b"alpha vX\n")  # same size (9 bytes), bytes differ
    os.utime(p, (st.st_atime, st.st_mtime))
    return {}


def r_f_exclude(c, w):
    with open(os.path.join(c, ".git", "info", "exclude"), "a", encoding="utf-8") as f:
        f.write("new.txt\n")
    with open(os.path.join(c, "new.txt"), "wb") as f:
        f.write(b"untracked\n")
    return {}


def r_f_gitignore(c, w):
    with open(os.path.join(c, "new.txt"), "wb") as f:
        f.write(b"untracked\n")
    return {}


def r_g_fifo(c, w):
    p = os.path.join(c, "a.txt")
    os.unlink(p)
    os.mkfifo(p)
    return {}


def r_g_symzero(c, w):
    p = os.path.join(c, "a.txt")
    os.unlink(p)
    os.symlink("/dev/zero", p)
    return {}


def r_h_env_filter(c, w):
    attrs = os.path.join(w, "attrs")
    with open(attrs, "w", encoding="utf-8") as f:
        f.write("a.txt filter=fix\n")
    with open(os.path.join(c, "a.txt"), "wb") as f:
        f.write(b"alpha v2\n")
    return {"GIT_CONFIG_COUNT": "2",
            "GIT_CONFIG_KEY_0": "core.attributesFile", "GIT_CONFIG_VALUE_0": attrs,
            "GIT_CONFIG_KEY_1": "filter.fix.clean",
            "GIT_CONFIG_VALUE_1": "printf 'alpha v1\\n'"}


def r_h_env_filter_info(c, w):
    with open(os.path.join(c, ".git", "info", "attributes"), "a", encoding="utf-8") as f:
        f.write("a.txt filter=fix\n")
    with open(os.path.join(c, "a.txt"), "wb") as f:
        f.write(b"alpha v2\n")
    return {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "filter.fix.clean",
            "GIT_CONFIG_VALUE_0": "printf 'alpha v1\\n'"}


def r_h_repo_filter(c, w):
    with open(os.path.join(c, ".git", "info", "attributes"), "a", encoding="utf-8") as f:
        f.write("a.txt filter=fix\n")
    git(c, "config", "filter.fix.clean", "printf 'alpha v1\\n'")
    with open(os.path.join(c, "a.txt"), "wb") as f:
        f.write(b"alpha v2\n")
    return {}


def r_i_ident(c, w):
    with open(os.path.join(c, "a.txt"), "wb") as f:
        f.write(b"$Id: forged 2 $\n")
    return {}


def r_k_gitlink(c, w):
    oid = git(c, "rev-parse", "HEAD").stdout.strip().decode()
    git(c, "update-index", "--cacheinfo", f"160000,{oid},a.txt")
    with open(os.path.join(c, "a.txt"), "wb") as f:
        f.write(b"alpha v3\n")
    return {}


def r_l_worktree_cfg(c, w):
    wt = os.path.join(w, "pristine")
    shutil.copytree(c, wt, ignore=shutil.ignore_patterns(".git"))
    git(c, "config", "core.worktree", wt)
    with open(os.path.join(c, "a.txt"), "wb") as f:
        f.write(b"alpha v3\n")
    return {}


ROUTES = [
    # id, mutate, seed, attrs, gitignore, truth paths, note
    ("ctl-honest", r_ctl_honest, None, None, None, ["a.txt"]),
    ("ctl-gd1", r_ctl_gd1, None, None, None, ["a.txt"]),
    ("a-v4-forge", r_a_v4, None, None, None, ["a.txt"]),
    ("b-split-forge", r_b_split, None, None, None, ["a.txt"]),
    ("b2-split-linked", r_b2_split_linked, None, None, None, ["a.txt"]),
    ("n-filemode-config", r_n_filemode, None, None, None, ["a.txt"]),
    ("c-assume-unchanged", r_c_assume, None, None, None, ["a.txt"]),
    ("c2-skip-worktree", r_c2_skipwt, None, None, None, ["a.txt"]),
    ("d-fsmonitor-empty", r_d_fsmon, None, None, None, ["a.txt"]),
    ("e-checkstat-minimal", r_e_checkstat, None, None, None, ["a.txt"]),
    ("f-info-exclude", r_f_exclude, None, None, None, ["new.txt"]),
    ("f2-gitignore", r_f_gitignore, None, None, b"new.txt\n", ["new.txt"]),
    ("g-fifo", r_g_fifo, None, None, None, ["a.txt"]),
    ("g2-symlink-dev-zero", r_g_symzero, None, None, None, ["a.txt"]),
    ("h-envconfig-filter", r_h_env_filter, None, None, None, ["a.txt"]),
    ("h2-envconfig-filter-infoattrs", r_h_env_filter_info, None, None, None, ["a.txt"]),
    ("h3-repo-filter", r_h_repo_filter, None, None, None, ["a.txt"]),
    ("i-ident", r_i_ident, {"a.txt": b"$Id$\n"}, b"a.txt ident\n", None, ["a.txt"]),
    ("k-gitlink-mode", r_k_gitlink, None, None, None, ["a.txt"]),
    ("l-core-worktree", r_l_worktree_cfg, None, None, None, ["a.txt"]),
]


def run_route(gate: str, work: str, rid: str, mutate, seed, attrs, gitignore, paths) -> dict:
    rowdir = os.path.join(work, rid)
    out = {"route": rid}
    try:
        clone, report, prereg = build(rowdir, seed=seed, attrs=attrs, gitignore=gitignore)
        extra = mutate(clone, rowdir) or {}
    except (FixtureError, OSError, subprocess.SubprocessError) as exc:
        out.update(error=f"{type(exc).__name__}: {exc}")
        return out
    out["note"] = extra.get("_note", "")
    env = env_clean({k: v for k, v in extra.items() if not k.startswith("_")})
    st_kind, st_rc, st_bytes = status_alone(clone, {k: v for k, v in extra.items() if not k.startswith("_")})
    out["status"] = f"{st_kind}(rc={st_rc})"
    try:
        p = subprocess.run(["bash", gate, "--lane", clone, "--branch", "master", "--report", report,
                            "--prereg", prereg], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=env, timeout=TIMEOUT)
        text = p.stdout.decode("utf-8", "replace") + p.stderr.decode("utf-8", "replace")
        out["rc"] = p.returncode
        out["clean"] = next((l.split("=", 1)[1] for l in text.splitlines()
                             if l.startswith("check-clean=")), "-")
        out["detail"] = " | ".join(l for l in text.splitlines()
                                   if l.startswith(("detail-", "check-clean")))
    except subprocess.TimeoutExpired:
        out["rc"] = None
        out["clean"] = "HANG"
        out["detail"] = f"no exit within {TIMEOUT}s"
    out["truth"] = {p: truth(clone, p) for p in paths}
    out["differs"] = any(t[3] for t in out["truth"].values())
    out["mode_diff"] = any(v[4].split("/")[0] != v[4].split("/")[1] for v in out["truth"].values())
    out["verdict"] = classify(out)
    if out.get("clean") == "PASS" and out["differs"] and "text" in dir():
        with open(os.path.join(work, rid, "gate-reproduction.txt"), "w", encoding="utf-8") as f:
            f.write(text)
    return out


def classify(o: dict) -> str:
    if o.get("clean") == "HANG":
        return "HANG"
    if o.get("error"):
        return "FIXTURE-ERROR"
    dif = o["differs"]
    if o["clean"] == "PASS":
        return "FORGERY" if dif else ("FORGERY-MODE" if o.get("mode_diff") else "HONEST-PASS")
    if o["clean"] == "FAIL":
        return "CAUGHT" if dif else "OVER-REFUSAL"
    return "OTHER"


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate-copy", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--routes")
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    gate = os.path.join(os.path.abspath(ns.gate_copy), "souji-pre-report-gate.sh")
    if not (os.path.isfile(gate) and os.path.isfile(os.path.join(os.path.dirname(gate),
                                                                 "souji-receipt-write.py"))):
        print(f"gate copy incomplete: {gate}", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"--work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    print(f"# gate sha256={hashlib.sha256(open(gate, 'rb').read()).hexdigest()} path={gate}")
    print(f"# writer sha256={hashlib.sha256(open(os.path.join(os.path.dirname(gate), 'souji-receipt-write.py'), 'rb').read()).hexdigest()}")
    want = ns.routes.split(",") if ns.routes else None
    routes = [r for r in ROUTES if not want or r[0] in want]
    if want and len(routes) != len(want):
        print("unknown route id", file=sys.stderr)
        return 2
    results = []
    for rid, mut, seed, attrs, gi, paths in routes:
        o = run_route(gate, work, rid, mut, seed, attrs, gi, paths)
        results.append(o)
        t = " ".join(f"{p}:wt={v[1]}/head={v[2]}/mode={v[4]}" for p, v in o.get("truth", {}).items())
        print(f"ROUTE {rid} status={o.get('status')} rc={o.get('rc')} clean={o.get('clean')} "
              f"verdict={o.get('verdict')} truth={t} note={o.get('note', '')}")
        if o.get("detail"):
            print(f"#  {rid} {o['detail'][:600]}")
        if o.get("error"):
            print(f"#  {rid} error {o['error']}")
    tally = {}
    for o in results:
        tally[o.get("verdict")] = tally.get(o.get("verdict"), 0) + 1
    print("SUMMARY rows=%d %s" % (len(results), " ".join(f"{k}={v}" for k, v in sorted(tally.items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
