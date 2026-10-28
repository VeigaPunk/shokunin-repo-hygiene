#!/usr/bin/env python3
# R41w2sentinel01 driver: strace safety/operability battery for tools/souji-freeze-check.py at 119c26f
# (blob 3c3e80baedd8774848fb9ac786bbda0c07c47250a14884abf1409f328fc3340b). Fixtures are built only under
# SCR (scratch). The lane is touched read-only (git show, for-each-ref, and the tool itself).
import collections
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time

SEAT = "R41w2sentinel01"
SCR = f"/fast/scratch/hyaku/souji-r41/{SEAT}"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEATDIR = f"{LANE}/.ufo/waves/round-41/w2/{SEAT}"
TOOL_REV = "119c26fa3bbb85e215824de9538bd2eb34e9f874"
TOOL_SHA = "3c3e80baedd8774848fb9ac786bbda0c07c47250a14884abf1409f328fc3340b"
LANE_TIP = "1d41c13574db80fdd9a4bde490b712da7ce2a85f"
TOOL = f"{SCR}/tool/souji-freeze-check.py"
FX = f"{SCR}/fx"
SENT_DIR = f"{SCR}/sentinel"
SENT = f"{SENT_DIR}/OUTSIDE-SECRET.txt"
SENT_BYTES = b"OUTSIDE-SECRET-r41-w2\nEXIT=1\n"
FORGED_PATH = f"{SCR}/tool/forged.bin"
FORGED = b"forged-counter-content r41 w2\n"
MARKS = f"{SCR}/marks"
RUNS = f"{SCR}/runs"
CWD = f"{SCR}/cwd"
CLONES = f"{SCR}/clones"
HOME = os.path.expanduser("~")
HD = "census/round-41/hostile"
PRE = "census/round-41/preregistration.txt"
SYS_PREFIX = ("/usr/", "/lib", "/etc/", "/proc/", "/sys/", "/dev/", "/run/", "/var/", "/bin/", "/sbin/", "/boot/")
PATH_BINS = {"git", "python3", "python", "sh", "bash", "dash"}

BUILD_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
BUILD_ENV.update(GIT_AUTHOR_NAME="r41-sentinel", GIT_AUTHOR_EMAIL="r41-sentinel@example.invalid",
                 GIT_COMMITTER_NAME="r41-sentinel", GIT_COMMITTER_EMAIL="r41-sentinel@example.invalid",
                 GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
RUN_BASE_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def git(D, *a, env=None, check=True):
    p = subprocess.run(["git", "-C", D, *a], env=env or BUILD_ENV, capture_output=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"git -C {D} {' '.join(a[:3])} rc={p.returncode}: {p.stderr.decode(errors='replace')}")
    return p


def head(D):
    return git(D, "rev-parse", "HEAD").stdout.decode().strip()


_tick = [0]


def commit(D, msg, paths=None):
    if paths:
        git(D, "add", "--", *paths)
    _tick[0] += 1
    t = "2026-10-27T10:%02d:%02dZ" % (_tick[0] // 60 % 60, _tick[0] % 60)
    env = dict(BUILD_ENV, GIT_AUTHOR_DATE=t, GIT_COMMITTER_DATE=t)
    git(D, "commit", "-q", "--allow-empty", "-m", msg, env=env)
    return head(D)


def fresh(name):
    D = f"{FX}/{name}"
    if os.path.lexists(D):
        shutil.rmtree(D)
    os.makedirs(D)
    git(D, "init", "-q", "-b", "main")
    top = git(D, "rev-parse", "--show-toplevel").stdout.decode().strip()
    assert os.path.realpath(top) == os.path.realpath(D), (top, D)
    return D


def put(D, rel, spec):
    p = os.path.join(D, rel)
    if os.path.lexists(p):
        os.unlink(p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if isinstance(spec, tuple) and spec[0] == "link":
        os.symlink(spec[1], p)
    elif isinstance(spec, str) and spec == "FIFO":
        os.mkfifo(p)
    else:
        data = spec.encode() if isinstance(spec, str) else spec
        with open(p, "wb") as f:
            f.write(data)


def build(name, base, freeze=None, mid=None, gitlinks=None, post=None):
    D = fresh(name)
    for rel, spec in base.items():
        put(D, rel, spec)
    git(D, "add", "--", *base.keys())
    for rel, sha in (gitlinks or {}).items():
        git(D, "update-index", "--add", "--cacheinfo", f"160000,{sha},{rel}")
    B0 = commit(D, "base")
    c = {"B0": B0, "C1": sha256(base["census/c1.py"]), "POP": sha256(base["census/pop.tsv"]),
         "MYC": sha256(base["census/my c1.py"]) if "census/my c1.py" in base else "",
         "SENT": sha256(SENT_BYTES), "FORGED": sha256(FORGED)}
    if mid:
        for rel, spec in mid.items():
            put(D, rel, spec)
        commit(D, "mid", paths=list(mid.keys()))
    fr = {}
    for rel, spec in (freeze or {}).items():
        fr[rel] = spec(c) if callable(spec) else spec
    for rel, spec in fr.items():
        put(D, rel, spec)
    F = commit(D, "freeze", paths=list(fr.keys()))
    c["F"] = F
    if post:
        post(D, c)
    return {"D": D, "B0": B0, "F": F, "REV": head(D), "ctx": c}


def claim(c, label="C1", base=None, counter=None, pop=None, control=None, extra=""):
    b = c["B0"] if base is None else base
    k = f"census/c1.py sha256={c['C1']}" if counter is None else counter
    p = f"census/pop.tsv sha256={c['POP']}" if pop is None else pop
    t = "census/control.txt" if control is None else control
    return (f"## {label}\nBase: {b}\nCounter: {k}\nPopulation: {p}\nControl: {t}\n"
            f"Target: t\nKill: k\n{extra}")


def doc(*claims, round_line="Round: 41\n"):
    return "# hostile prereg fixture\n" + round_line + "".join(claims)


HOSTILE = {
    "clean": lambda c: doc(claim(c)),
    "bad-digest": lambda c: doc(claim(c, counter=f"census/c1.py sha256={'0' * 64}")),
    "trav-counter-up": lambda c: doc(claim(c, counter=f"../../sentinel/OUTSIDE-SECRET.txt sha256={c['SENT']}")),
    "trav-counter-abs": lambda c: doc(claim(c, counter=f"{SENT} sha256={c['SENT']}")),
    "trav-counter-deep": lambda c: doc(claim(c, counter="../" * 40 + "etc/passwd sha256=" + "0" * 64)),
    "trav-counter-inrepo": lambda c: doc(claim(c, counter=f"census/../census/c1.py sha256={c['C1']}")),
    "trav-pop-mid": lambda c: doc(claim(c, pop=f"census/../../../sentinel/OUTSIDE-SECRET.txt sha256={c['SENT']}")),
    "trav-control-up": lambda c: doc(claim(c, control="../../sentinel/OUTSIDE-SECRET.txt")),
    "trav-control-dotslash": lambda c: doc(claim(c, control="./../../sentinel/OUTSIDE-SECRET.txt")),
    "trav-control-abs": lambda c: doc(claim(c, control=SENT)),
    "trav-base-abs": lambda c: doc(claim(c, base=SENT)),
    "dash-counter": lambda c: doc(claim(c, counter=f"--output={MARKS}/dash-counter sha256={c['SENT']}")),
    "dash-pop": lambda c: doc(claim(c, pop=f"--output={MARKS}/dash-pop sha256={c['SENT']}")),
    "dash-base": lambda c: doc(claim(c, base=f"--output={MARKS}/dash-base")),
    "dash-control": lambda c: doc(claim(c, control=f"--output={MARKS}/dash-control")),
    "dash-counter-opt": lambda c: doc(claim(c, counter=f"--name-only sha256={c['C1']}")),
    "sym-counter-abs": lambda c: doc(claim(c, counter=f"census/link-abs.py sha256={c['SENT']}")),
    "sym-counter-rel": lambda c: doc(claim(c, counter=f"census/link-rel.py sha256={c['SENT']}")),
    "sym-pop-abs": lambda c: doc(claim(c, pop=f"census/link-p.tsv sha256={c['SENT']}")),
    "sym-control-abs": lambda c: doc(claim(c, control="census/link-ctl.txt")),
    "sym-counter-loop": lambda c: doc(claim(c, counter=f"census/link-loop sha256={c['C1']}")),
    "sym-counter-dangling": lambda c: doc(claim(c, counter=f"census/link-dangling sha256={c['SENT']}")),
    "gitlink-counter": lambda c: doc(claim(c, counter=f"census/sub sha256={c['SENT']}")),
    "gitlink-pop": lambda c: doc(claim(c, pop=f"census/sub sha256={c['SENT']}")),
    "dir-counter": lambda c: doc(claim(c, counter=f"census/adir sha256={c['SENT']}")),
    "space-path": lambda c: doc(claim(c, counter=f"census/my c1.py sha256={c['MYC']}")),
    "trailing-slash": lambda c: doc(claim(c, counter=f"census/c1.py/ sha256={c['C1']}")),
    "long-name-5000": lambda c: doc(claim(c, counter="census/" + "L" * 5000 + f".py sha256={c['SENT']}")),
    "long-arg-200k": lambda c: doc(claim(c, counter="census/" + "L" * 200000 + f" sha256={c['SENT']}")),
    "nul-counter": lambda c: doc(claim(c, counter=f"census/c1.py\x00 sha256={c['C1']}")),
    "nul-control": lambda c: doc(claim(c, control="census/control.txt\x00")),
    "nul-pop": lambda c: doc(claim(c, pop=f"census/pop.tsv\x00 sha256={c['POP']}")),
    "nul-base": lambda c: doc(claim(c, base=c["B0"] + "\x00")),
    "nul-digest-tail": lambda c: doc(claim(c, counter=f"census/c1.py sha256={c['C1']}\x00")),
    "dup-counter": lambda c: doc(claim(c, extra=f"Counter: {SENT} sha256={c['SENT']}\n")),
    "empty-counter": lambda c: doc(claim(c, counter="")),
    "empty-pop": lambda c: doc(claim(c, pop="")),
    "empty-control": lambda c: doc(claim(c, control="")),
    "empty-base": lambda c: doc(claim(c, base="")),
    "hidden-C2b": lambda c: doc(claim(c), claim(c, label="C2b", counter="census/c1.py sha256=" + "0" * 64)),
    "hidden-lower-c2": lambda c: doc(claim(c), claim(c, label="c2", counter="census/c1.py sha256=" + "0" * 64)),
    "hidden-underscore": lambda c: doc(claim(c), claim(c, label="C2_x", counter="census/c1.py sha256=" + "0" * 64)),
    "indented-keys": lambda c: doc(f"## C1\nBase: {c['B0']}\n  Counter: census/c1.py sha256={c['C1']}\n"
                                   f"Population: census/pop.tsv sha256={c['POP']}\nControl: census/control.txt\n"
                                   "Target: t\nKill: k\n"),
    "crlf": lambda c: doc(claim(c)).replace("\n", "\r\n"),
    "latin1-comment": lambda c: doc(claim(c)).encode() + b"# caf\xe9\n",
    "many-500": lambda c: doc(*[claim(c, label=f"C{i}") for i in range(1, 501)]),
    "many-2000": lambda c: doc(*[claim(c, label=f"C{i}") for i in range(1, 2001)]),
    "filler-30m": lambda c: doc(claim(c)) + "# filler line padding padding padding\n" * 800000,
    "real": lambda c: doc(claim(c)),
}
RSS_ONLY = {"many-2000", "filler-30m"}


def base_files():
    return {
        "census/c1.py": b"print('c1 counter r41 w2')\n",
        "census/control.txt": b"ok\nEXIT=1\n",
        "census/green.txt": b"ok\nEXIT=0\n",
        "census/pop.tsv": b"item\tA\nitem\tB\nitem\tC\n",
        "census/my c1.py": b"print('c1 counter r41 w2')\n",
        "census/adir/inner.txt": b"inner\n",
        "census/link-abs.py": ("link", SENT),
        "census/link-rel.py": ("link", "../../../sentinel/OUTSIDE-SECRET.txt"),
        "census/link-p.tsv": ("link", SENT),
        "census/link-ctl.txt": ("link", SENT),
        "census/link-loop": ("link", ".."),
        "census/link-dangling": ("link", "nope/none"),
    }


GITLINKS = {"census/sub": "1" * 40}
DISP_MID = {".ufo/waves/round-41/w1-dispatch.json": b'{"wave": 1}\n'}


def hostile_freeze():
    fr = {}
    for k, fn in HOSTILE.items():
        fr[f"{HD}/{k}.txt"] = (lambda fn=fn: (lambda c: fn(c)))()
    fr[f"{HD}/sym-prereg.txt"] = ("link", "real.txt")
    fr["-p.txt"] = lambda c: doc(claim(c))
    return fr


def clean_freeze():
    return {PRE: lambda c: doc(claim(c))}


def spawn(cmd, env, timeout):
    t0 = time.monotonic()
    p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=env, cwd=CWD, start_new_session=True)
    to = False
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        to = True
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = p.communicate()
    return p.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace"), to, time.monotonic() - t0


LINE = re.compile(r'^(\d+)\s+(\w+)\((.*)\)\s+=\s+(.*)$')
QUOT = re.compile(r'"((?:[^"\\]|\\.)*)"')
OPENS = {"openat", "open", "openat2"}
PROBES = {"newfstatat", "stat", "lstat", "statx", "access", "faccessat", "faccessat2", "readlink", "readlinkat"}
WRITE_SC = {"creat", "rename", "renameat", "renameat2", "unlink", "unlinkat", "mkdir", "mkdirat", "rmdir",
            "symlink", "symlinkat", "link", "linkat", "truncate", "chmod", "fchmodat", "chown", "fchownat",
            "utimensat", "mknod", "mknodat"}
WFLAGS = ("O_WRONLY", "O_RDWR", "O_CREAT", "O_TRUNC", "O_APPEND")
ESCAPE_CLASSES = {"SENTINEL", "OTHER", "SCRATCH-OUTSIDE-ROOT", "HOME-OTHER"}


def classify(path, root, gitdir, failed):
    # git runs with -C root, so its relative paths (.git/config, objects/...) are root-relative
    if not path.startswith("/"):
        path = os.path.normpath(os.path.join(root, path))
    r = root.rstrip("/")
    if "OUTSIDE-SECRET" in path or path.startswith(SENT_DIR + "/"):
        return "SENTINEL"
    if path == r:
        return "ROOT-DIR-STAT"
    if path.startswith(r + "/"):
        return "ROOT-GITDIR" if (path == r + "/.git" or path.startswith(r + "/.git/")) else "ROOT-WORKTREE"
    if gitdir and (path == gitdir or path.startswith(gitdir + "/")):
        return "ENV-GITDIR"
    if path == TOOL:
        return "TOOL"
    if r.startswith(path.rstrip("/") + "/"):
        return "ANCESTOR-STAT"
    if failed and os.path.basename(path) in PATH_BINS:
        return "PATH-LOOKUP"
    if "/site-packages" in path or "/lib/python3" in path:
        return "PY-IMPORT-PROBE"
    if path.startswith(SYS_PREFIX):
        return "SYSTEM"
    if path.startswith(HOME + "/.config/git") or path == HOME + "/.gitconfig":
        return "HOME-GITCONF"
    if path.startswith(HOME + "/"):
        return "HOME-OTHER"
    if path.startswith(SCR + "/"):
        return "SCRATCH-OUTSIDE-ROOT"
    return "OTHER"


def analyze(log, root, gitdir):
    gd = gitdir.rstrip("/") if gitdir else None
    classes = collections.Counter()
    worktree, escapes, sentinel, writes, execs, envgit, gitconf = set(), collections.Counter(), [], set(), set(), set(), set()
    with open(log, errors="replace") as f:
        text = f.read()
    for ln in text.splitlines():
        m = LINE.match(ln)
        if not m:
            continue
        _pid, sc, args, ret = m.groups()
        q = QUOT.findall(args)
        if not q:
            continue
        ok = not ret.startswith("-1")
        if sc in ("execve", "execveat"):
            if ok:
                execs.add(q[0])
            continue
        if sc in OPENS or sc in PROBES:
            path = q[0]
            cl = classify(path, root, gd, not ok)
            classes[cl] += 1
            tag = f"{sc} {path} {'ok' if ok else 'failed'}"
            if sc in OPENS and ok and any(fl in args[args.find(path) + len(path):] for fl in WFLAGS):
                writes.add(tag)
            if cl == "ROOT-WORKTREE":
                worktree.add(tag)
            elif cl == "SENTINEL":
                sentinel.append(tag)
            elif cl == "ENV-GITDIR":
                envgit.add(path)
            elif cl == "HOME-GITCONF":
                gitconf.add(path)
            elif cl in ESCAPE_CLASSES:
                escapes[f"{cl} {tag}"] += 1
        elif sc in WRITE_SC and ok:
            for path in q:
                writes.add(f"{sc} {path}")
    return {"classes": dict(classes), "worktree_opens": sorted(worktree), "sentinel_hits": sentinel,
            "escape_opens": sorted(escapes), "writes": sorted(writes), "execs_ok": sorted(execs),
            "env_gitdir_paths": len(envgit), "home_gitconf": sorted(gitconf)}


def run(tag, root, tokens, rev, env=None, timeout=60, markers=(), strace=True):
    log = f"{RUNS}/{tag}.strace"
    argv = ["python3", "-B", TOOL, "--root", root, *tokens, "--rev", rev]
    cmd = (["strace", "-f", "-qq", "-e", "trace=%file,%process", "-o", log] if strace else []) + argv
    e = dict(RUN_BASE_ENV)
    for k, v in (env or {}).items():
        if v is None:
            e.pop(k, None)
        else:
            e[k] = v
    rc, out, err, to, el = spawn(cmd, e, timeout)
    rec = {"tag": tag, "root": root, "tokens": tokens, "rev": rev, "env": env or {}, "argv": argv,
           "rc": rc, "timed_out": to, "secs": round(el, 3), "stdout": out[-3000:], "stderr": err[-1500:],
           "traceback": "Traceback (most recent call last)" in err,
           "markers_present": [m for m in markers if os.path.lexists(m)]}
    if strace and os.path.exists(log):
        rec.update(analyze(log, root, (env or {}).get("GIT_DIR")))
        rec["strace_log"] = log
    return rec


def rss_run(tag, root, tokens, rev, timeout=900):
    code = ("import subprocess,resource,sys,time\n"
            "t=time.monotonic()\n"
            "p=subprocess.run(sys.argv[1:],stdin=subprocess.DEVNULL,capture_output=True)\n"
            "print('WRAP rc=%d secs=%.3f maxrss_kb=%d' % (p.returncode, time.monotonic()-t, "
            "resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss))\n"
            "sys.stdout.write(p.stdout.decode(errors='replace')[-3000:])\n"
            "sys.stderr.write(p.stderr.decode(errors='replace')[-1500:])\n")
    argv = ["python3", "-c", code, "python3", "-B", TOOL, "--root", root, *tokens, "--rev", rev]
    rc, out, err, to, el = spawn(argv, dict(RUN_BASE_ENV), timeout)
    m = re.search(r"WRAP rc=(-?\d+) secs=([\d.]+) maxrss_kb=(\d+)", out)
    return {"tag": tag, "rss_wrapper": True, "timed_out": to, "wall": round(el, 3),
            "rc": int(m.group(1)) if m else None, "secs": float(m.group(2)) if m else None,
            "maxrss_kb": int(m.group(3)) if m else None, "stdout": out[-3000:], "stderr": err[-1500:]}


def setup():
    for d in (SCR, FX, SENT_DIR, MARKS, RUNS, CWD, f"{SCR}/tool", CLONES, f"{SCR}/other-wt/census",
              f"{SCR}/emptyobj", f"{SCR}/fx/notarepo"):
        os.makedirs(d, exist_ok=True)
    for f in os.listdir(MARKS):
        os.unlink(os.path.join(MARKS, f))
    with open(SENT, "wb") as f:
        f.write(SENT_BYTES)
    with open(f"{SCR}/fx/notarepo/README", "w") as f:
        f.write("not a repository\n")
    with open(f"{SCR}/other-wt/census/c1.py", "wb") as f:
        f.write(b"print('OTHER worktree c1')\n")
    with open(FORGED_PATH, "wb") as f:
        f.write(FORGED)
    blob = subprocess.run(["git", "-C", LANE, "show", f"{TOOL_REV}:tools/souji-freeze-check.py"],
                          capture_output=True, check=True, env=BUILD_ENV).stdout
    assert sha256(blob) == TOOL_SHA, sha256(blob)
    with open(TOOL, "wb") as f:
        f.write(blob)


def clone_bare(src, name):
    dst = f"{CLONES}/{name}.git"
    if os.path.lexists(dst):
        shutil.rmtree(dst)
    subprocess.run(["git", "clone", "--bare", "-q", src, dst], env=BUILD_ENV, check=True, cwd=CWD)
    return dst


def gitdir_run(gd, *a):
    return subprocess.run(["git", f"--git-dir={gd}", *a], env=BUILD_ENV, capture_output=True, check=True)


def main():
    setup()
    os.makedirs(f"{SEATDIR}/receipts", exist_ok=True)
    recs, rss = [], []
    extra = {"tool_sha256_pinned_copy": subprocess.run(["sha256sum", TOOL], capture_output=True, text=True).stdout.split()[0],
             "lane_tip_type": git(LANE, "cat-file", "-t", LANE_TIP, check=False).stdout.decode().strip(),
             "lane_replace_refs": git(LANE, "for-each-ref", "refs/replace", "refs/evil", check=False).stdout.decode().strip(),
             "lane_quotepath_config": git(LANE, "config", "--show-origin", "--get-all", "core.quotepath",
                                          check=False).stdout.decode().strip()}

    # ---- base fixture: clean control, argument attacks, env attacks
    B = build("base", base_files(), freeze=clean_freeze(), gitlinks=GITLINKS)
    base_clone = clone_bare(B["D"], "base")
    recs.append(run("base-clean", B["D"], ["--prereg", PRE], B["F"]))
    recs.append(run("base-rev-newline", B["D"], ["--prereg", PRE], B["F"] + "\n"))
    recs.append(run("base-rev-short", B["D"], ["--prereg", PRE], B["F"][:12]))
    recs.append(run("base-rev-is-base", B["D"], ["--prereg", PRE], B["B0"]))
    recs.append(run("base-prereg-dotdot", B["D"], ["--prereg", "../../sentinel/OUTSIDE-SECRET.txt"], B["F"]))
    recs.append(run("base-prereg-abs", B["D"], ["--prereg", SENT], B["F"]))
    recs.append(run("base-prereg-dash-eq", B["D"], ["--prereg=-x"], B["F"]))
    recs.append(run("base-prereg-dash-output", B["D"], [f"--prereg=--output={MARKS}/dash-prereg"], B["F"],
                    markers=[f"{MARKS}/dash-prereg"]))
    recs.append(run("base-env-gitdir-clone", B["D"], ["--prereg", PRE], B["F"], env={"GIT_DIR": base_clone}))
    empty_bare = f"{CLONES}/empty.git"
    if os.path.lexists(empty_bare):
        shutil.rmtree(empty_bare)
    subprocess.run(["git", "init", "-q", "--bare", empty_bare], env=BUILD_ENV, check=True, cwd=CWD)
    recs.append(run("base-env-gitdir-empty", B["D"], ["--prereg", PRE], B["F"], env={"GIT_DIR": empty_bare}))
    recs.append(run("base-env-gitdir-dotgit-plus-worktree", B["D"], ["--prereg", PRE], B["F"],
                    env={"GIT_DIR": f"{B['D']}/.git", "GIT_WORK_TREE": f"{SCR}/other-wt"}))
    recs.append(run("base-env-worktree-only", B["D"], ["--prereg", PRE], B["F"],
                    env={"GIT_WORK_TREE": f"{SCR}/other-wt"}))
    recs.append(run("base-env-objdir-empty", B["D"], ["--prereg", PRE], B["F"],
                    env={"GIT_OBJECT_DIRECTORY": f"{SCR}/emptyobj"}))
    recs.append(run("notarepo-root-no-env", f"{SCR}/fx/notarepo", ["--prereg", PRE], B["F"]))
    recs.append(run("notarepo-root-env-gitdir", f"{SCR}/fx/notarepo", ["--prereg", PRE], B["F"],
                    env={"GIT_DIR": f"{B['D']}/.git"}))

    # ---- Base ancestry: a Base that is a real commit but NOT an ancestor of the freeze
    SD = fresh("side")
    for rel, spec in base_files().items():
        put(SD, rel, spec)
    git(SD, "add", "--", *base_files().keys())
    SB0 = commit(SD, "base")
    tree = git(SD, "rev-parse", f"{SB0}^{{tree}}").stdout.decode().strip()
    side = subprocess.run(["git", "-C", SD, "commit-tree", tree, "-p", SB0, "-m", "side branch"],
                          env=dict(BUILD_ENV, GIT_AUTHOR_DATE="2026-10-27T11:00:00Z",
                                   GIT_COMMITTER_DATE="2026-10-27T11:00:00Z"),
                          capture_output=True, check=True).stdout.decode().strip()
    put(SD, PRE, doc(claim({"B0": side, "C1": sha256(base_files()["census/c1.py"]),
                            "POP": sha256(base_files()["census/pop.tsv"])})))
    SF = commit(SD, "freeze", paths=[PRE])
    S_bare = clone_bare(SD, "side")
    recs.append(run("side-base-not-ancestor", SD, ["--prereg", PRE], SF))
    recs.append(run("side-base-inrepo-replace-graft", SD, ["--prereg", PRE], SF, markers=[]) if False else None)
    git(SD, "replace", "--graft", SF, side)
    recs.append(run("side-base-inrepo-replace-graft", SD, ["--prereg", PRE], SF))
    recs.append(run("side-base-inrepo-replace-graft-nrepl", SD, ["--prereg", PRE], SF,
                    env={"GIT_NO_REPLACE_OBJECTS": "1"}))
    with open(f"{S_bare}/info/grafts", "w") as f:
        f.write(f"{SF} {side}\n")
    recs.append(run("side-base-env-gitdir-grafts", SD, ["--prereg", PRE], SF, env={"GIT_DIR": S_bare}))
    recs = [r for r in recs if r]

    # ---- dispatch (DISPATCH-BEFORE-FREEZE) fixtures
    D1 = build("disp", base_files(), freeze={PRE: lambda c: doc(claim(c))}, mid=DISP_MID, gitlinks=GITLINKS)
    recs.append(run("disp-control", D1["D"], ["--prereg", PRE], D1["F"]))
    dg = clone_bare(D1["D"], "disp")
    with open(f"{dg}/info/grafts", "w") as f:
        f.write(f"{D1['F']} {D1['B0']}\n")
    recs.append(run("disp-env-gitdir-grafts", D1["D"], ["--prereg", PRE], D1["F"], env={"GIT_DIR": dg}))
    D2 = build("disp-rg", base_files(), freeze={PRE: lambda c: doc(claim(c))}, mid=DISP_MID, gitlinks=GITLINKS,
               post=lambda D, c: git(D, "replace", "--graft", c["F"], c["B0"]))
    recs.append(run("disp-inrepo-replace-graft", D2["D"], ["--prereg", PRE], D2["F"]))
    D3 = build("disp-noround", base_files(), freeze={PRE: lambda c: doc(claim(c), round_line="")}, mid=DISP_MID,
               gitlinks=GITLINKS)
    recs.append(run("disp-no-round-line", D3["D"], ["--prereg", PRE], D3["F"]))
    D4 = build("disp-roundword", base_files(),
               freeze={PRE: lambda c: doc(claim(c), round_line="Round: forty-one\n")}, mid=DISP_MID)
    recs.append(run("disp-round-word", D4["D"], ["--prereg", PRE], D4["F"]))
    D5 = build("disp-roundtrav", base_files(),
               freeze={PRE: lambda c: doc(claim(c), round_line="Round: 41/../../x\n")}, mid=DISP_MID)
    recs.append(run("disp-round-traversal", D5["D"], ["--prereg", PRE], D5["F"]))
    QUOTED_MID = {".ufo/waves/round-41/ü-dispatch.json": b'{"wave": 1}\n',
                  '.ufo/waves/round-41/q"x-dispatch.json': b'{"wave": 1}\n'}
    D6 = build("disp-quoted", base_files(), freeze={PRE: lambda c: doc(claim(c))}, mid=QUOTED_MID)
    recs.append(run("disp-quoted-names", D6["D"], ["--prereg", PRE], D6["F"]))
    recs.append(run("disp-quoted-names-quotepath-off", D6["D"], ["--prereg", PRE], D6["F"],
                    env={"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.quotepath",
                         "GIT_CONFIG_VALUE_0": "false"}))
    recs.append(run("disp-control-quotepath-off-ascii", D1["D"], ["--prereg", PRE], D1["F"],
                    env={"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.quotepath",
                         "GIT_CONFIG_VALUE_0": "false"}))

    # ---- replace refs: digest stated for FORGED content; real bytes committed at F
    def repl_post(mode):
        def post(D, c):
            real = git(D, "rev-parse", f"{c['F']}:census/c1.py").stdout.decode().strip()
            forged = git(D, "hash-object", "-w", FORGED_PATH).stdout.decode().strip()
            if mode == "inrepo":
                git(D, "replace", real, forged)
            elif mode == "evil":
                git(D, "update-ref", f"refs/evil/{real}", forged)
        return post

    rfz = {PRE: lambda c: doc(claim(c, counter=f"census/c1.py sha256={c['FORGED']}"))}
    R0 = build("repl-none", base_files(), freeze=rfz, gitlinks=GITLINKS, post=repl_post("none"))
    recs.append(run("repl-none-digest-mismatch", R0["D"], ["--prereg", PRE], R0["F"]))
    rclone = clone_bare(R0["D"], "repl-none")
    real = git(R0["D"], "rev-parse", f"{R0['F']}:census/c1.py").stdout.decode().strip()
    forged = git(R0["D"], "hash-object", "-w", FORGED_PATH).stdout.decode().strip()
    gitdir_run(rclone, "update-ref", f"refs/replace/{real}", forged)
    recs.append(run("repl-none-env-gitdir-with-refs-replace", R0["D"], ["--prereg", PRE], R0["F"],
                    env={"GIT_DIR": rclone}))
    R1 = build("repl-inrepo", base_files(), freeze=rfz, gitlinks=GITLINKS, post=repl_post("inrepo"))
    recs.append(run("repl-inrepo-refs-replace", R1["D"], ["--prereg", PRE], R1["F"]))
    recs.append(run("repl-inrepo-refs-replace-nrepl", R1["D"], ["--prereg", PRE], R1["F"],
                    env={"GIT_NO_REPLACE_OBJECTS": "1"}))
    R2 = build("repl-env", base_files(), freeze=rfz, gitlinks=GITLINKS, post=repl_post("evil"))
    recs.append(run("repl-env-no-env", R2["D"], ["--prereg", PRE], R2["F"]))
    recs.append(run("repl-env-replace-ref-base", R2["D"], ["--prereg", PRE], R2["F"],
                    env={"GIT_REPLACE_REF_BASE": "refs/evil/"}))

    # ---- post-freeze and worktree-only fixtures
    def p_tamper(D, c):
        put(D, "census/c1.py", b"tampered after freeze\n")
        commit(D, "post-freeze tamper", paths=["census/c1.py"])
    P1 = build("post-tamper", base_files(), freeze=clean_freeze(), gitlinks=GITLINKS, post=p_tamper)
    recs.append(run("post-freeze-tamper", P1["D"], ["--prereg", PRE], P1["REV"]))

    def wt(name, fn):
        X = build(name, base_files(), freeze=clean_freeze(), gitlinks=GITLINKS)
        fn(X["D"], X["ctx"])
        return X

    X = wt("wt-fifo-pop", lambda D, c: put(D, "census/pop.tsv", "FIFO"))
    recs.append(run("wt-fifo-pop", X["D"], ["--prereg", PRE], X["F"], timeout=60))
    X = wt("wt-fifo-prereg", lambda D, c: put(D, PRE, "FIFO"))
    recs.append(run("wt-fifo-prereg", X["D"], ["--prereg", PRE], X["F"], timeout=60))
    X = wt("wt-fifo-counter", lambda D, c: put(D, "census/c1.py", "FIFO"))
    recs.append(run("wt-fifo-counter", X["D"], ["--prereg", PRE], X["F"], timeout=60))
    X = wt("wt-symlink-sentinel", lambda D, c: put(D, "census/c1.py", ("link", SENT)))
    recs.append(run("wt-symlink-sentinel-counter", X["D"], ["--prereg", PRE], X["F"], timeout=60))
    X = wt("wt-tamper", lambda D, c: put(D, "census/c1.py", b"uncommitted tamper\n"))
    recs.append(run("wt-uncommitted-tamper", X["D"], ["--prereg", PRE], X["F"], timeout=60))

    # ---- hostile prereg battery (one fixture; every prereg path committed at the freeze)
    H = build("hostile", base_files(), freeze=hostile_freeze(), gitlinks=GITLINKS)
    for k in HOSTILE:
        if k in RSS_ONLY:
            continue
        recs.append(run(f"hostile-{k}", H["D"], ["--prereg", f"{HD}/{k}.txt"], H["F"],
                        markers=[f"{MARKS}/dash-counter", f"{MARKS}/dash-pop", f"{MARKS}/dash-base",
                                 f"{MARKS}/dash-control"]))
    recs.append(run("hostile-sym-prereg", H["D"], ["--prereg", f"{HD}/sym-prereg.txt"], H["F"]))
    recs.append(run("hostile-leading-dash-prereg-file", H["D"], ["--prereg=-p.txt"], H["F"]))

    # ---- huge inputs: wall time and max RSS (no strace); strace for the 500-claim variant above
    rss.append(rss_run("hostile-many-2000", H["D"], ["--prereg", f"{HD}/many-2000.txt"], H["F"]))
    rss.append(rss_run("hostile-filler-30m", H["D"], ["--prereg", f"{HD}/filler-30m.txt"], H["F"]))
    big = dict(base_files())
    big["census/pop.tsv"] = (b"item\tAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\n"
                             * (300 * 1024 * 1024 // 100))
    HP = build("huge-pop", big, freeze=clean_freeze(), gitlinks=GITLINKS)
    del big
    rss.append(rss_run("huge-pop-300MiB", HP["D"], ["--prereg", PRE], HP["F"], timeout=1200))
    recs.append(run("huge-pop-300MiB-strace", HP["D"], ["--prereg", PRE], HP["F"], timeout=1200))

    # ---- real lane (read-only): the frozen R41 prereg at the lane tip, and the round-40 control
    recs.append(run("lane-tip-r41-prereg", LANE, ["--prereg", PRE], LANE_TIP, timeout=300))
    recs.append(run("lane-tip-r40-prereg", LANE, ["--prereg", "census/round-40/preregistration.txt"], LANE_TIP,
                    timeout=300))

    with open(f"{SEATDIR}/receipts/runs.json", "w") as f:
        json.dump({"extra": extra, "runs": recs, "rss": rss}, f, indent=1, sort_keys=True)
    for r in recs:
        print(f"{r['tag']:<40} rc={r['rc']} to={r['timed_out']} tb={r['traceback']} secs={r['secs']} "
              f"sent={len(r.get('sentinel_hits', []))} esc={len(r.get('escape_opens', []))} "
              f"wt={len(r.get('worktree_opens', []))} writes={r.get('writes', [])} "
              f"execs={len(r.get('execs_ok', []))} | {(r['stdout'].strip().splitlines() or [''])[-1][:100]}"
              f" | {r['stderr'].strip().splitlines()[-1][:100] if r['stderr'].strip() else ''}")
    for r in rss:
        print("RSS", json.dumps(r)[:400])
    print("EXTRA", json.dumps(extra))


if __name__ == "__main__":
    sys.exit(main())
