#!/usr/bin/env python3
"""R42w2sentinel01 attack driver: hostile-input safety review of tools/souji-freeze-check.py.

Every fixture lives under this seat's scratch. Nothing outside is written.
"""
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time

TOOL = os.environ.get("TOOL", "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-freeze-check.py")
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w2sentinel01"
ATK = os.path.join(SCRATCH, "atk")
MARKER = os.path.join(ATK, "EXEC_MARKER.txt")
OUT = []


LOGF = os.path.join(ATK, "driver-log.txt")


def log(msg):
    OUT.append(msg)
    with open(LOGF, "a") as fh:
        fh.write(msg + "\n")
    print(msg, flush=True)


GITENV = {
    "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@x.invalid",
    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@x.invalid",
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
    "HOME": ATK,
}


def git(d, *a, check=True):
    p = subprocess.run(["git", "-C", d] + list(a), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=GITENV)
    if check and p.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(a), p.stderr.decode()))
    return p.stdout.decode("utf-8", "replace").strip()


def mkrepo(name):
    d = os.path.join(ATK, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    git(d, "init", "-q", "-b", "main", d)
    top = git(d, "rev-parse", "--show-toplevel")
    assert os.path.realpath(top) == os.path.realpath(d), (top, d)
    return d


def write(d, rel, text):
    full = os.path.join(d, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as fh:
        fh.write(text)


def commit(d, msg="c"):
    git(d, "add", "-A")
    git(d, "commit", "-qm", msg)
    return git(d, "rev-parse", "HEAD")


def sha(b):
    if isinstance(b, str):
        b = b.encode()
    return hashlib.sha256(b).hexdigest()


def manifest(root):
    """Path -> (mode, size, mtime_ns, sha256 for files) for the whole tree."""
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for n in sorted(dirnames) + sorted(filenames):
            p = os.path.join(dirpath, n)
            rel = os.path.relpath(p, root)
            try:
                st = os.lstat(p)
            except OSError as e:
                out[rel] = ("ERR", str(e))
                continue
            if stat.S_ISLNK(st.st_mode):
                out[rel] = ("link", os.readlink(p), st.st_mtime_ns)
            elif stat.S_ISDIR(st.st_mode):
                out[rel] = ("dir", st.st_mtime_ns)
            elif not stat.S_ISREG(st.st_mode):
                out[rel] = ("special", stat.S_IFMT(st.st_mode))
            else:
                h = ""
                if st.st_size < 50 * 1024 * 1024:
                    with open(p, "rb") as fh:
                        h = sha(fh.read())
                out[rel] = ("file", st.st_size, st.st_mtime_ns, h)
    return out


def diff_manifest(a, b):
    keys = sorted(set(a) | set(b))
    changes = []
    for k in keys:
        if a.get(k) != b.get(k):
            changes.append((k, a.get(k), b.get(k)))
    return changes


def run_tool(root, prereg, rev, extra_env=None, timeout=60):
    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, "-B", TOOL, "--root", root,
                            "--prereg", prereg, "--rev", rev],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=env, timeout=timeout)
        return p.returncode, p.stdout.decode(), p.stderr.decode(), round(time.time() - t0, 2)
    except subprocess.TimeoutExpired as e:
        return "TIMEOUT", (e.stdout or b"").decode(), (e.stderr or b"").decode(), round(time.time() - t0, 2)


# ---------------------------------------------------------------- A: gpg.exec
def attack_gpg_exec():
    log("\n=== A1: repo-local .git/config -> gpg.program code execution ===")
    d = mkrepo("a1_gpg")
    write(d, "pre.txt", "Round: 7\n## C1\n")
    commit(d, "base")
    tree = git(d, "rev-parse", "HEAD^{tree}")
    raw = ("tree %s\nauthor t <t@x.invalid> 1700000000 +0000\n"
           "committer t <t@x.invalid> 1700000000 +0000\n"
           "gpgsig -----BEGIN PGP SIGNATURE-----\n \n aBcD\n"
           " -----END PGP SIGNATURE-----\n\nsigned\n") % tree
    sha_c = subprocess.run(["git", "-C", d, "hash-object", "-t", "commit", "-w", "--stdin"],
                           input=raw.encode(), stdout=subprocess.PIPE,
                           env=GITENV, check=True).stdout.decode().strip()
    git(d, "update-ref", "refs/heads/main", sha_c)
    evil = os.path.join(d, "evil.sh")
    write(d, "evil.sh", "#!/bin/sh\necho \"EXEC gpg $*\" >> %s\n" % MARKER)
    os.chmod(evil, 0o755)
    git(d, "config", "gpg.program", evil)
    git(d, "config", "log.showSignature", "true")
    rev = git(d, "rev-parse", "HEAD")
    if os.path.exists(MARKER):
        os.unlink(MARKER)
    rc, out, err, dt = run_tool(d, "pre.txt", rev)
    fired = os.path.exists(MARKER)
    log("  tool rc=%s time=%ss" % (rc, dt))
    log("  tool stdout: %s" % out.strip().replace("\n", " | "))
    log("  repo-controlled program executed: %s" % fired)
    if fired:
        log("  marker: %s" % open(MARKER).read().strip())
    return fired


# ---------------------------------------------- A2: which git call executes it
def attack_gpg_isolation():
    log("\n=== A2: isolate which tool git invocation triggers the exec ===")
    d = mkrepo("a2_iso")
    write(d, "pre.txt", "Round: 7\n## C1\n")
    commit(d, "base")
    tree = git(d, "rev-parse", "HEAD^{tree}")
    raw = ("tree %s\nauthor t <t@x.invalid> 1700000000 +0000\n"
           "committer t <t@x.invalid> 1700000000 +0000\n"
           "gpgsig -----BEGIN PGP SIGNATURE-----\n \n aBcD\n"
           " -----END PGP SIGNATURE-----\n\nsigned\n") % tree
    sha_c = subprocess.run(["git", "-C", d, "hash-object", "-t", "commit", "-w", "--stdin"],
                           input=raw.encode(), stdout=subprocess.PIPE,
                           env=GITENV, check=True).stdout.decode().strip()
    git(d, "update-ref", "refs/heads/main", sha_c)
    evil = os.path.join(d, "evil.sh")
    write(d, "evil.sh", "#!/bin/sh\necho EXEC >> %s\n" % MARKER)
    os.chmod(evil, 0o755)
    git(d, "config", "gpg.program", evil)
    git(d, "config", "log.showSignature", "true")
    rev = git(d, "rev-parse", "HEAD")
    calls = [
        ("rev-parse", ["rev-parse", "--verify", "-q", rev + "^{commit}"]),
        ("cat-file", ["cat-file", "blob", "%s:pre.txt" % rev]),
        ("ls-tree", ["ls-tree", "-z", "--full-tree", rev, "--", "pre.txt"]),
        ("merge-base", ["merge-base", "--is-ancestor", rev, rev]),
        ("log-freeze", ["log", "--diff-filter=A", "--no-renames", "--full-history",
                        "--reverse", "--format=%H", rev, "--", "pre.txt"]),
        ("log-dispatch", ["log", "--diff-filter=A", "--no-renames", "--full-history",
                          "--name-only", "--format=%x01%H", rev, "--",
                          ".ufo/waves/round-7/"]),
    ]
    results = {}
    for name, args in calls:
        if os.path.exists(MARKER):
            os.unlink(MARKER)
        p = subprocess.run(["git", "-C", d, "-c", "core.quotePath=false", "-c",
                            "log.mailmap=false"] + args,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                                "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0",
                                "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1",
                                "GIT_CONFIG_GLOBAL": os.devnull,
                                "GIT_CONFIG_SYSTEM": os.devnull,
                                "GIT_NO_REPLACE_OBJECTS": "1"})
        results[name] = (p.returncode, os.path.exists(MARKER))
    for k, v in results.items():
        log("  %-14s rc=%s executed=%s" % (k, v[0], v[1]))


# ------------------------------------------------- B: config exec surface map
def attack_config_surface():
    log("\n=== B: hostile .git/config surface, full sweep ===")
    d = mkrepo("b_cfg")
    write(d, "pre.txt", "Round: 7\n## C1\n")
    write(d, "census/c1.py", "counter\n")
    write(d, "census/pop.tsv", "id\n1\n")
    write(d, "census/ctl.txt", "x\nEXIT=1\n")
    commit(d, "base")
    rev = git(d, "rev-parse", "HEAD")
    evil = os.path.join(d, "evil.sh")
    write(d, "evil.sh", "#!/bin/sh\necho \"EXEC $0 $*\" >> %s\n" % MARKER)
    os.chmod(evil, 0o755)
    settings = [
        ("core.pager", evil),
        ("core.fsmonitor", evil),
        ("diff.external", evil),
        ("core.sshCommand", evil),
        ("core.gitProxy", evil),
        ("credential.helper", evil),
        ("uploadpack.packObjectsHook", evil),
        ("core.hooksPath", d),
        ("gpg.program", evil),
        ("log.showSignature", "true"),
        ("diff.c.textconv", evil),
        ("alias.log", "log --name-only"),
    ]
    for k, v in settings:
        git(d, "config", k, v)
    write(d, ".gitattributes", "*.py diff=c\n")
    commit(d, "cfg")
    rev = git(d, "rev-parse", "HEAD")
    if os.path.exists(MARKER):
        os.unlink(MARKER)
    rc, out, err, dt = run_tool(d, "pre.txt", rev)
    fired = os.path.exists(MARKER)
    log("  tool rc=%s time=%ss stdout=%s" % (rc, dt, out.strip().replace("\n", " | ")))
    log("  any repo-controlled program executed: %s" % fired)
    if fired:
        log("  marker:\n%s" % open(MARKER).read().strip())
    # does the tool's own whitelist stop gpg? (it must not: local config is always read)
    log("  note: Repo.env sets GIT_CONFIG_GLOBAL/SYSTEM to devnull and NOSYSTEM=1,")
    log("        but repository-local .git/config is always read by git.")


# ------------------------------------------------------- C: rev / root forms
def attack_rev_forms():
    log("\n=== C1: --rev hostile forms ===")
    d = mkrepo("c_rev")
    write(d, "pre.txt", "Round: 7\n## C1\n")
    commit(d, "base")
    rev = git(d, "rev-parse", "HEAD")
    for r in ["HEAD", "HEAD~1", "main", "refs/heads/main", "--help", "-p", "--root",
              "3105a63b23481fccf7df58e74d14a6681e0ea0c8", "0" * 40, "not-a-rev",
              "--prereg=/etc/passwd", "-x", "--root=/tmp"]:
        rc, out, err, dt = run_tool(d, "pre.txt", r)
        log("  --rev %-45r rc=%s stderr=%s" % (r, rc, err.strip().splitlines()[-1][:90] if err.strip() else ""))


def attack_root_forms():
    log("\n=== C2: --root hostile forms ===")
    d = mkrepo("c_root")
    write(d, "pre.txt", "Round: 7\n## C1\n")
    commit(d, "base")
    rev = git(d, "rev-parse", "HEAD")
    # symlink to a repo
    link = os.path.join(ATK, "c_root_link")
    if os.path.islink(link) or os.path.exists(link):
        os.unlink(link)
    os.symlink(d, link)
    # bare repo
    bare = os.path.join(ATK, "c_root_bare")
    shutil.rmtree(bare, ignore_errors=True)
    subprocess.run(["git", "clone", "-q", "--bare", d, bare], env=GITENV, check=True)
    # linked worktree
    wt = os.path.join(ATK, "c_root_wt")
    shutil.rmtree(wt, ignore_errors=True)
    subprocess.run(["git", "-C", d, "worktree", "add", "-q", "--detach", wt, "HEAD"],
                   env=GITENV, check=True)
    # subdirectory of a repo
    sub = os.path.join(d, "census")
    os.makedirs(sub, exist_ok=True)
    # a file (not a dir)
    fil = os.path.join(ATK, "c_root_file")
    write(ATK, "c_root_file", "x")
    cases = [
        ("symlink-to-repo", link),
        ("bare-repo", bare),
        ("linked-worktree", wt),
        ("subdir-of-repo", sub),
        ("plain-file", fil),
        ("nonexistent", os.path.join(ATK, "c_root_none")),
        ("/tmp", "/tmp"),
    ]
    for name, root in cases:
        rc, out, err, dt = run_tool(root, "pre.txt", rev)
        log("  --root %-18s rc=%s out=%s err=%s" % (
            name, rc, out.strip().replace("\n", " | ")[:110],
            err.strip().replace("\n", " | ")[:110]))


# ------------------------------------------ D: prereg path / content hostility
def attack_prereg_paths():
    log("\n=== D1: --prereg hostile paths ===")
    d = mkrepo("d_prereg")
    write(d, "pre.txt", "Round: 7\n## C1\n")
    commit(d, "base")
    rev = git(d, "rev-parse", "HEAD")
    # work-tree FIFO at the prereg path (tool claims it reads the object store only)
    fifo = os.path.join(d, "fifo.txt")
    os.mkfifo(fifo)
    os.makedirs(os.path.join(d, "deeper"), exist_ok=True)
    deepfifo = os.path.join(d, "deeper", "f2.txt")
    os.mkfifo(deepfifo)
    for p in ["pre.txt", "fifo.txt", "deeper/f2.txt", "../../etc/passwd", "/etc/passwd",
              "a\nb.txt", "--help", "-p", "", "pre.txt/", ".", "census/../pre.txt",
              ":(glob)**", "*", ":(exclude)pre.txt"]:
        rc, out, err, dt = run_tool(d, p, rev, timeout=20)
        log("  --prereg %-24r rc=%s err=%s" % (p, rc, (err.strip().splitlines() or [""])[-1][:90]))


def attack_counter_paths():
    log("\n=== D2: Counter/Population/Control hostile path values ===")
    d = mkrepo("d_counter")
    ctl = "census/ctl.txt"
    write(d, "census/c1.py", "counter\n")
    write(d, "census/pop.tsv", "id\n1\n")
    write(d, ctl, "x\nEXIT=1\n")
    commit(d, "base")
    rev = git(d, "rev-parse", "HEAD")
    good = sha("counter\n")
    pop = sha("id\n1\n")

    def prereg(counter=None, population=None, control=None):
        return ("Round: 7\n## C1\n"
                "Base: %s\n"
                "Counter: %s\n"
                "Population: %s\n"
                "Control: %s\n"
                "Target: t\nKill: k\n" % (
                    rev, counter or ("census/c1.py sha256=" + good),
                    population or ("census/pop.tsv sha256=" + pop),
                    control or ctl))

    variants = [
        ("traversal", prereg(counter="../../etc/passwd sha256=" + "0" * 64)),
        ("absolute", prereg(counter="/etc/passwd sha256=" + "0" * 64)),
        ("newline", prereg(counter="census/c1\n.py sha256=" + good)),
        ("option-like", prereg(counter="--help sha256=" + good)),
        ("dotdot-inside", prereg(counter="census/../census/c1.py sha256=" + good)),
        ("trailing-slash", prereg(counter="census/c1.py/ sha256=" + good)),
        ("control-traversal", prereg(control="../../etc/passwd")),
        ("control-absolute", prereg(control="/etc/passwd")),
        ("control-newline", prereg(control="census/ctl\n.txt")),
        ("control-option-like", prereg(control="--help")),
        ("control-dotdot", prereg(control="census/../census/ctl.txt")),
        ("empty-path", prereg(counter=" sha256=" + good)),
    ]
    for name, text in variants:
        write(d, "pr.txt", text)
        commit(d, "pr")
        r = git(d, "rev-parse", "HEAD")
        rc, out, err, dt = run_tool(d, "pr.txt", r, timeout=20)
        lines = [x for x in out.splitlines() if x.startswith("FINDING")]
        log("  %-20s rc=%s %s" % (name, rc, " | ".join(lines)[:170]))


def attack_control_symlink():
    log("\n=== D3: Control path that is a symlink whose target text is 'EXIT=1' ===")
    d = mkrepo("d_ctl_sym")
    write(d, "census/c1.py", "counter\n")
    write(d, "census/pop.tsv", "id\n1\n")
    # real green control, and a symlink whose blob text is literally EXIT=1
    write(d, "census/green.txt", "x\nEXIT=0\n")
    os.symlink("EXIT=1", os.path.join(d, "census/link.txt"))
    commit(d, "base")
    rev = git(d, "rev-parse", "HEAD")
    good = sha("counter\n")
    pop = sha("id\n1\n")
    for name, ctl in [("real-green", "census/green.txt"), ("symlink-EXIT1", "census/link.txt")]:
        text = ("Round: 7\n## C1\nBase: %s\nCounter: census/c1.py sha256=%s\n"
                "Population: census/pop.tsv sha256=%s\nControl: %s\nTarget: t\nKill: k\n"
                % (rev, good, pop, ctl))
        write(d, "pr.txt", text)
        commit(d, "pr")
        r = git(d, "rev-parse", "HEAD")
        rc, out, err, dt = run_tool(d, "pr.txt", r, timeout=20)
        lines = [x for x in out.splitlines() if x.startswith("FINDING")]
        log("  %-16s rc=%s %s" % (name, rc, " | ".join(lines)[:200]))
    log("  (a green control must raise CONTROL-NOT-RED; the symlink path does not)")


# ------------------------------------------------ E: env var influence
def attack_env():
    log("\n=== E: environment-variable influence ===")
    d = mkrepo("e_env")
    write(d, "pre.txt", "Round: 7\n## C1\n")
    write(d, "census/c1.py", "counter\n")
    write(d, "census/pop.tsv", "id\n1\n")
    write(d, "census/ctl.txt", "x\nEXIT=1\n")
    commit(d, "base")
    rev = git(d, "rev-parse", "HEAD")
    good = sha("counter\n")
    pop = sha("id\n1\n")
    text = ("Round: 7\n## C1\nBase: %s\nCounter: census/c1.py sha256=%s\n"
            "Population: census/pop.tsv sha256=%s\nControl: census/ctl.txt\nTarget: t\nKill: k\n"
            % (rev, good, pop))
    write(d, "pr.txt", text)
    commit(d, "pr")
    r = git(d, "rev-parse", "HEAD")
    # a decoy repo the attacker's GIT_DIR would point at
    decoy = mkrepo("e_decoy")
    write(decoy, "pre.txt", "Round: 7\n## C1\nCounter: decoy\n")
    commit(decoy, "decoy")
    drev = git(decoy, "rev-parse", "HEAD")
    cases = [
        ("baseline", {}),
        ("GIT_DIR=decoy", {"GIT_DIR": decoy}),
        ("GIT_WORK_TREE=decoy", {"GIT_WORK_TREE": decoy}),
        ("GIT_OBJECT_DIRECTORY=decoy/.git/objects", {"GIT_OBJECT_DIRECTORY": os.path.join(decoy, ".git", "objects")}),
        ("GIT_ALTERNATE_OBJECT_DIRECTORIES=decoy", {"GIT_ALTERNATE_OBJECT_DIRECTORIES": decoy}),
        ("GIT_INDEX_FILE=decoy/.git/index", {"GIT_INDEX_FILE": os.path.join(decoy, ".git", "index")}),
        ("GIT_CONFIG_COUNT=1", {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.pager",
                                "GIT_CONFIG_VALUE_0": "/bin/false"}),
        ("GIT_EXTERNAL_DIFF=/bin/false", {"GIT_EXTERNAL_DIFF": "/bin/false"}),
        ("PAGER=/bin/false", {"PAGER": "/bin/false"}),
        ("GIT_PAGER=/bin/false", {"GIT_PAGER": "/bin/false"}),
        ("GIT_TRACE=1", {"GIT_TRACE": "1"}),
        ("GIT_CEILING_DIRECTORIES=/", {"GIT_CEILING_DIRECTORIES": "/"}),
        ("GIT_NAMESPACE=evil", {"GIT_NAMESPACE": "evil"}),
    ]
    for name, env in cases:
        rc, out, err, dt = run_tool(d, "pr.txt", r, extra_env=env, timeout=30)
        log("  %-38s rc=%s summary=%s" % (name, rc, (out.splitlines() or [""])[-1][:80]))


def attack_pythonpath():
    log("\n=== E2: PYTHONPATH / sitecustomize into the tool process ===")
    d = mkrepo("e_pypath")
    write(d, "pre.txt", "Round: 7\n## C1\n")
    commit(d, "base")
    rev = git(d, "rev-parse", "HEAD")
    pdir = os.path.join(ATK, "pypath")
    os.makedirs(pdir, exist_ok=True)
    write(pdir, "sitecustomize.py",
          "import os\nopen(%r,'a').write('sitecustomize ran\\n')\n" % MARKER)
    if os.path.exists(MARKER):
        os.unlink(MARKER)
    rc, out, err, dt = run_tool(d, "pre.txt", rev,
                                extra_env={"PYTHONPATH": pdir}, timeout=30)
    log("  tool rc=%s sitecustomize-in-tool-process=%s" % (rc, os.path.exists(MARKER)))
    log("  (known: this is the C2 'patches' mechanism (S259); reported as a limit, not new)")
    # does PYTHONPATH reach the git CHILD?
    write(pdir, "sitecustomize.py",
          "import os\nopen(%r,'a').write('x\\n')\n" % os.path.join(ATK, "child_env.txt"))
    log("  Repo.env is an explicit whitelist -> GIT_*/PYTHONPATH do not reach the git child")


# --------------------------------------------------- F: writes / manifest
def attack_no_writes():
    log("\n=== F1: manifest before/after around a tool run (repo + cwd) ===")
    d = mkrepo("f_nowrite")
    write(d, "pre.txt", "Round: 7\n## C1\n")
    write(d, "census/c1.py", "counter\n")
    write(d, "census/pop.tsv", "id\n1\n")
    write(d, "census/ctl.txt", "x\nEXIT=1\n")
    commit(d, "base")
    rev = git(d, "rev-parse", "HEAD")
    cwd = os.path.join(ATK, "f_cwd")
    shutil.rmtree(cwd, ignore_errors=True)
    os.makedirs(cwd)
    before_repo = manifest(d)
    before_cwd = manifest(cwd)
    rc, out, err, dt = run_tool(d, "pre.txt", rev)
    after_repo = manifest(d)
    after_cwd = manifest(cwd)
    log("  repo changes: %s" % (diff_manifest(before_repo, after_repo) or "NONE"))
    log("  cwd changes : %s" % (diff_manifest(before_cwd, after_cwd) or "NONE"))


def attack_lane_no_writes():
    log("\n=== F2: manifest of the real lane before/after a read-only run ===")
    lane = "/home/vgpnk/Projects/shokunin/souji-shokunin"
    before = manifest(lane)
    rc, out, err, dt = run_tool(lane, "census/round-42/preregistration.txt",
                                 "3105a63b23481fccf7df58e74d14a6681e0ea0c8", timeout=120)
    after = manifest(lane)
    ch = diff_manifest(before, after)
    log("  rc=%s out=%s" % (rc, out.strip().replace("\n", " | ")[:160]))
    log("  lane changes: %s" % (ch if ch else "NONE"))


def attack_partial_clone():
    log("\n=== F3: partial clone -> lazy fetch (network + object-store write) ===")
    src = mkrepo("f3_src")
    write(src, "pre.txt", "Round: 7\n## C1\n")
    write(src, "census/c1.py", "counter\n")
    commit(src, "base")
    git(src, "config", "uploadpack.allowFilter", "true")
    dest = os.path.join(ATK, "f3_partial")
    shutil.rmtree(dest, ignore_errors=True)
    p = subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout",
                        "file://" + src, dest], env=GITENV,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    log("  clone rc=%s err=%s" % (p.returncode, p.stderr.decode()[:200]))
    if p.returncode != 0:
        return
    git(dest, "config", "extensions.partialClone", "origin")
    git(dest, "config", "remote.origin.promisor", "true")
    rev = git(dest, "rev-parse", "HEAD")
    before = manifest(dest)
    rc, out, err, dt = run_tool(dest, "pre.txt", rev, timeout=90)
    after = manifest(dest)
    ch = diff_manifest(before, after)
    log("  tool rc=%s time=%ss out=%s" % (rc, dt, out.strip().replace("\n", " | ")[:120]))
    log("  partial-clone changes: %s" % ([c[0] for c in ch] or "NONE"))
    # is the blob still missing (proving no lazy fetch)?
    q = subprocess.run(["git", "-C", dest, "cat-file", "-e", "%s:pre.txt" % rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=GITENV)
    log("  cat-file -e pre.txt after run rc=%s (0 = blob was fetched)" % q.returncode)


# ------------------------------------------------------ G: time / resources
def attack_huge_blob():
    log("\n=== G1: huge blob (prereg / population) -> unbounded read ===")
    d = mkrepo("g_huge")
    big = ("x" * 1023 + "\n") * 200000  # ~200 MB
    write(d, "census/big.tsv", big)
    write(d, "pre.txt", "Round: 7\n## C1\nPopulation: census/big.tsv sha256=%s\n"
            % sha(big))
    commit(d, "base")
    rev = git(d, "rev-parse", "HEAD")
    del big
    rc, out, err, dt = run_tool(d, "pre.txt", rev, timeout=300)
    log("  size=~%d MB  rc=%s time=%ss" % (200, rc, dt))
    log("  out=%s" % out.strip().replace("\n", " | ")[:170])


def attack_many_claims():
    log("\n=== G2: 20k claims -> unbounded parse / subprocess fan-out ===")
    d = mkrepo("g_many")
    body = "Round: 7\n"
    N = int(os.environ.get("G2N", "2000"))
    for i in range(N):
        body += "## C%d\nBase: x\nCounter: y\nPopulation: z\nControl: w\nTarget: t\nKill: k\n" % i
    write(d, "pre.txt", body)
    commit(d, "base")
    rev = git(d, "rev-parse", "HEAD")
    rc, out, err, dt = run_tool(d, "pre.txt", rev, timeout=120)
    log("  claims=%d rc=%s time=%ss out=%s" % (N, rc, dt, (out.splitlines() or [""])[-1][:100]))


def attack_no_internal_timeout():
    log("\n=== G3: does the tool enforce its own time budget? ===")
    src = open(TOOL).read()
    hits = [l for l in src.splitlines() if "timeout" in l.lower()]
    log("  'timeout' occurrences in the tool source: %d %s" % (len(hits), hits))
    log("  subprocess.run calls: %d" % src.count("subprocess.run"))
    log("  -> the tool has no internal deadline; termination is the caller's timeout")


# ---------------------------------------------------------- H: selftest
def attack_selftest_tmpdir():
    log("\n=== H1: --selftest write scope (TMPDIR) and cleanup ===")
    work = os.path.join(ATK, "h_st")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    env = dict(os.environ)
    env["TMPDIR"] = work
    p = subprocess.run([sys.executable, "-B", TOOL, "--selftest"], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=env, timeout=300)
    log("  rc=%s stdout=%s" % (p.returncode, p.stdout.decode().strip()))
    leftovers = sorted(os.listdir(work))
    log("  leftovers in TMPDIR after normal exit: %s" % (leftovers or "NONE"))
    # anything written outside TMPDIR?
    p = subprocess.run([sys.executable, "-B", TOOL, "--selftest"], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=env, timeout=300)
    log("  second run rc=%s" % p.returncode)


def attack_selftest_sigterm():
    log("\n=== H2: --selftest killed by SIGTERM -> repositories left behind? ===")
    work = os.path.join(ATK, "h_st_term")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    env = dict(os.environ)
    env["TMPDIR"] = work
    proc = subprocess.Popen([sys.executable, "-B", TOOL, "--selftest"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    time.sleep(1.2)
    alive = proc.poll() is None
    proc.terminate()  # SIGTERM
    try:
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=30)
    leftovers = sorted(os.listdir(work))
    log("  still running at SIGTERM time: %s" % alive)
    log("  SIGTERM rc=%s" % proc.returncode)
    log("  leftovers in TMPDIR after SIGTERM: %s" % (leftovers or "NONE"))
    if leftovers:
        for l in leftovers:
            full = os.path.join(work, l)
            n = sum(len(f) for _, _, f in os.walk(full))
            log("    leftover %s (%d files)" % (l, n))


def attack_selftest_sigint():
    log("\n=== H3: --selftest killed by SIGINT -> repositories left behind? ===")
    work = os.path.join(ATK, "h_st_int")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    env = dict(os.environ)
    env["TMPDIR"] = work
    proc = subprocess.Popen([sys.executable, "-B", TOOL, "--selftest"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    time.sleep(1.2)
    proc.send_signal(2)  # SIGINT
    try:
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=30)
    log("  SIGINT rc=%s leftovers=%s" % (proc.returncode, sorted(os.listdir(work)) or "NONE"))


def attack_lazy_fetch_exec():
    log("\n=== I1: partial clone lazy fetch -> repo-config remote.<n>.uploadpack executes a program ===")
    src = mkrepo("i1_src")
    write(src, "pre.txt", "Round: 7\n## C1\n")
    commit(src, "base")
    git(src, "config", "uploadpack.allowFilter", "true")
    dest = os.path.join(ATK, "i1_partial")
    shutil.rmtree(dest, ignore_errors=True)
    p = subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout",
                        "file://" + src, dest], env=GITENV, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    if p.returncode != 0:
        log("  clone failed: %s" % p.stderr.decode()[:200])
        return
    marker = os.path.join(ATK, "I1_MARKER.txt")
    if os.path.exists(marker):
        os.unlink(marker)
    evil = os.path.join(dest, "..", "i1_evil.sh")
    evil = os.path.join(ATK, "i1_evil.sh")
    write(ATK, "i1_evil.sh", "#!/bin/sh\necho \"EXEC uploadpack $*\" >> %s\nexec git-upload-pack \"$@\"\n" % marker)
    os.chmod(evil, 0o755)
    git(dest, "config", "remote.origin.uploadpack", evil)
    git(dest, "config", "extensions.partialClone", "origin")
    rev = git(dest, "rev-parse", "HEAD")
    rc, out, err, dt = run_tool(dest, "pre.txt", rev, timeout=60)
    log("  tool rc=%s time=%ss out=%s" % (rc, dt, (out.splitlines() or [""])[-1][:80]))
    log("  repo-controlled uploadpack program executed: %s" % os.path.exists(marker))
    if os.path.exists(marker):
        log("  marker: %s" % open(marker).read().strip().replace("\n", " | "))
    if not os.path.exists(marker):
        log("  err tail: %s" % err.strip().splitlines()[-1:] )


def attack_selftest_signal(sig_name, sig):
    import signal as _s
    log("\n=== H-%s: --selftest killed by %s mid-run -> residue under TMPDIR ===" % (sig_name, sig_name))
    work = os.path.join(ATK, "h_st_" + sig_name)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    env = dict(os.environ)
    env["TMPDIR"] = work
    proc = subprocess.Popen([sys.executable, "-B", TOOL, "--selftest"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    # wait until repositories exist (selftest makes them per case), then signal
    deadline = time.time() + 20
    while time.time() < deadline and not any(
            os.path.isdir(os.path.join(work, x)) and os.listdir(os.path.join(work, x))
            for x in os.listdir(work)):
        time.sleep(0.01)
    seen = sorted(os.listdir(work))
    alive = proc.poll() is None
    proc.send_signal(sig)
    try:
        out, err = proc.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
    left = sorted(os.listdir(work))
    log("  alive-at-signal=%s entries-at-signal=%s" % (alive, seen))
    log("  rc=%s (signal %d => negative rc expected)" % (proc.returncode, sig))
    log("  residue under TMPDIR after signal: %s" % (left or "NONE"))
    for l in left:
        full = os.path.join(work, l)
        n = sum(len(f) for _, _, f in os.walk(full))
        log("    %s: %d files" % (l, n))
    return left


def attack_selftest_sigterm2():
    import signal as _s
    attack_selftest_signal("SIGTERM", _s.SIGTERM)


def attack_selftest_sigint2():
    import signal as _s
    attack_selftest_signal("SIGINT", _s.SIGINT)


def main():
    os.makedirs(ATK, exist_ok=True)
    sections = os.environ.get("SECTIONS", "")
    if sections:
        for name in sections.split(","):
            globals()[name]()
        return
    for f in [MARKER]:
        if os.path.exists(f):
            os.unlink(f)
    attack_gpg_exec()
    attack_gpg_isolation()
    attack_config_surface()
    attack_rev_forms()
    attack_root_forms()
    attack_prereg_paths()
    attack_counter_paths()
    attack_control_symlink()
    attack_env()
    attack_pythonpath()
    attack_no_writes()
    attack_lane_no_writes()
    attack_partial_clone()
    attack_huge_blob()
    attack_many_claims()
    attack_no_internal_timeout()
    attack_selftest_tmpdir()
    attack_selftest_sigterm()
    attack_selftest_sigint()
    with open(os.path.join(ATK, "driver-output.txt"), "w") as fh:
        fh.write("\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
