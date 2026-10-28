#!/usr/bin/env python3
"""R41sentinel02 attack driver: crafted preregistrations against the r41 C2 freeze-check protocol.

Builds one scratch repository per case under SCRATCH/fx/<case> (every git call names -C; the
toplevel is asserted before the first commit), runs each candidate souji-freeze-check.py under
strace (openat/execve trace) in its own process group with a timeout, and runs a naive-primitive
probe (what a straightforward implementation would do with the same path strings).

Writes receipts only to SEAT/receipts. Never runs git in LANE. Fixtures, runs and markers live in
SCRATCH and are deleted by the caller after the receipts are copied.
"""
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = os.path.join(LANE, ".ufo/waves/round-41/w1/R41sentinel02")
SCRATCH = "/fast/scratch/hyaku/souji-r41/R41sentinel02"
FX = os.path.join(SCRATCH, "fx")
RUNS = os.path.join(SCRATCH, "runs")
RECEIPTS = os.path.join(SEAT, "receipts")
CANDS = ["executor07", "executor08", "executor09", "executor10", "executor11", "executor12"]
TIMEOUT = 60

GIT_ENV = {
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    "LC_ALL": "C",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_TERMINAL_PROMPT": "0",
    "TMPDIR": SCRATCH,
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}

COUNTER = b"# counter\nprint('counter')\n"
POP = b"id\tname\n1\talpha\n2\tbeta\n"
CTL_RED = b"SUMMARY items=2 corrected=0\nEXIT=1\n"
CTL_GREEN = b"SUMMARY items=2 corrected=2\nEXIT=0\n"
CTL_00 = b"SUMMARY items=2 corrected=0\nEXIT=00\n"
CTL_BIG = b"SUMMARY items=2 corrected=0\nEXIT=99999999999999999999999999999999\n"
OUT = b"OUTSIDE-SECRET-r41\nEXIT=1\n"
BIG = b"id\tname\n" + b"x" * (50 * 1024 * 1024) + b"\n"
VENDOR_OID = "0123456789abcdef0123456789abcdef01234567"

S_ABS = os.path.join(FX, "OUTSIDE-SECRET.txt")
S_PRE_ABS = os.path.join(FX, "OUTSIDE-PREREG.txt")
PWN_C = os.path.join(FX, "PWN-DASH-COUNTER.txt")
PWN_P = os.path.join(FX, "PWN-DASH-POP.txt")
PWN_T = os.path.join(FX, "PWN-DASH-CTL.txt")
PWN_B = os.path.join(FX, "PWN-DASH-BASE.txt")


def H(b):
    return hashlib.sha256(b).hexdigest()


def git(d, *args, inp=None, ok=True):
    assert d.startswith(FX + os.sep), "git may only run in fixtures: %s" % d
    p = subprocess.run(["git", "-C", d] + list(args), env=GIT_ENV, input=inp,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if ok and p.returncode != 0:
        raise RuntimeError("git %r rc=%d %s" % (args, p.returncode, p.stderr.decode("utf-8", "replace")))
    return p


def put(d, rel, val):
    full = os.path.join(d, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if isinstance(val, tuple) and val[0] == "link":
        os.symlink(val[1], full)
    elif isinstance(val, tuple) and val[0] == "gitlink":
        os.makedirs(full, exist_ok=True)  # an uninitialised submodule is an empty directory
    else:
        with open(full, "wb") as fh:
            fh.write(val)


def commit_all(d, msg):
    git(d, "add", "-A")
    git(d, "commit", "-qm", msg)
    return git(d, "rev-parse", "HEAD").stdout.decode().strip()


def make(name, extra, prereg, post=None):
    """Return (dir, base_sha, freeze_sha, tip_sha, prereg_bytes)."""
    d = os.path.join(FX, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    git(d, "init", "-q", "-b", "main")
    top = git(d, "rev-parse", "--show-toplevel").stdout.decode().strip()
    assert os.path.realpath(top) == os.path.realpath(d), (top, d)
    put(d, "README", b"base\n")
    B = commit_all(d, "base")
    files = {"census/c1.py": COUNTER, "census/pop.tsv": POP, "census/control.txt": CTL_RED}
    files.update(extra or {})
    text = prereg(B)
    files["prereg.txt"] = text
    for rel, val in files.items():
        put(d, rel, val)
    git(d, "add", "-A")
    for rel, val in files.items():
        if isinstance(val, tuple) and val[0] == "gitlink":
            git(d, "update-index", "--add", "--cacheinfo", "160000,%s,%s" % (VENDOR_OID, rel))
    git(d, "commit", "-qm", "freeze")
    F = git(d, "rev-parse", "HEAD").stdout.decode().strip()
    if post:
        post(d)
    T = git(d, "rev-parse", "HEAD").stdout.decode().strip()
    return d, B, F, T, text


def std(B, **kw):
    c = {"Base": B, "Counter": "census/c1.py sha256=" + H(COUNTER),
         "Population": "census/pop.tsv sha256=" + H(POP), "Control": "census/control.txt",
         "Target": "items=2 corrected=2", "Kill": "any uncorrected"}
    for k, v in kw.items():
        c[k] = v
    return {k: v for k, v in c.items() if v is not None}


def doc(*claims):
    parts = ["# prereg", "Round: 41", ""]
    for i, c in enumerate(claims, 1):
        parts.append("## C%d — claim %d" % (i, i))
        for key in ("Base", "Counter", "Population", "Control", "Target", "Kill"):
            if key in c:
                parts.append("%s: %s" % (key, c[key]))
        parts.append("")
    return ("\n".join(parts) + "\n").encode("utf-8")


# post-freeze actions (worktree-only or post-freeze commits)
def post_fifo(d):
    os.remove(os.path.join(d, "census/pop.tsv"))
    os.mkfifo(os.path.join(d, "census/pop.tsv"))


def post_devzero(d):
    os.remove(os.path.join(d, "census/pop.tsv"))
    os.symlink("/dev/zero", os.path.join(d, "census/pop.tsv"))


def post_outside_c1(d):
    os.remove(os.path.join(d, "census/c1.py"))
    os.symlink(S_ABS, os.path.join(d, "census/c1.py"))


def post_tamper(d):
    with open(os.path.join(d, "census/pop.tsv"), "wb") as fh:
        fh.write(b"tampered in worktree only\n")


def post_dispatch_after_link(d):
    os.makedirs(os.path.join(d, ".ufo/waves/round-41"), exist_ok=True)
    os.symlink(S_ABS, os.path.join(d, ".ufo/waves/round-41/w1-dispatch.json"))
    commit_all(d, "dispatch after freeze (symlink)")


def post_dispatch_after_regular(d):
    os.makedirs(os.path.join(d, ".ufo/waves/round-41"), exist_ok=True)
    with open(os.path.join(d, ".ufo/waves/round-41/w1-dispatch.json"), "wb") as fh:
        fh.write(b"{}\n")
    commit_all(d, "dispatch after freeze")


CLEAN = [(0, frozenset())]
REFUSE = [(2, frozenset())]
ANY = "ANY"


def F(rc, *classes):
    return (rc, frozenset(classes))


def build_cases():
    cases = []

    def case(name, desc, accept, prereg, extra=None, post=None, arg="prereg.txt"):
        cases.append({"name": name, "desc": desc, "accept": accept, "prereg": prereg,
                      "extra": extra or {}, "post": post, "arg": arg})

    # --- path traversal in Counter / Population / Control
    case("clean", "standard lane shape, control", CLEAN, lambda B: doc(std(B)))
    case("trav-counter-rel", "Counter ../ escapes repo to sentinel", [F(1, "C1 COUNTER-MISSING")],
         lambda B: doc(std(B, Counter="../OUTSIDE-SECRET.txt sha256=" + H(OUT))))
    case("trav-counter-deep", "Counter census/../../ escapes repo", [F(1, "C1 COUNTER-MISSING")],
         lambda B: doc(std(B, Counter="census/../../OUTSIDE-SECRET.txt sha256=" + H(OUT))))
    case("trav-counter-abs", "Counter absolute path outside repo", [F(1, "C1 COUNTER-MISSING")],
         lambda B: doc(std(B, Counter=S_ABS + " sha256=" + H(OUT))))
    case("trav-counter-dotslash", "Counter ./../ escape", [F(1, "C1 COUNTER-MISSING")],
         lambda B: doc(std(B, Counter="./../OUTSIDE-SECRET.txt sha256=" + H(OUT))))
    case("trav-pop-rel", "Population ../ escapes repo", [F(1, "C1 POPULATION-MISSING")],
         lambda B: doc(std(B, Population="../OUTSIDE-SECRET.txt sha256=" + H(OUT))))
    case("trav-control-rel", "Control ../ escapes repo (sentinel ends EXIT=1)", [F(1, "C1 CONTROL-MISSING")],
         lambda B: doc(std(B, Control="../OUTSIDE-SECRET.txt")))
    case("trav-control-abs", "Control absolute path outside repo", [F(1, "C1 CONTROL-MISSING")],
         lambda B: doc(std(B, Control=S_ABS)))

    # --- symlink blobs (committed at FREEZE-REV) pointing outside the repo
    case("sym-counter-outside", "census/link-counter.py is a symlink blob -> sentinel",
         [F(1, "C1 COUNTER-MISSING"), F(1, "C1 COUNTER-DIGEST")],
         lambda B: doc(std(B, Counter="census/link-counter.py sha256=" + H(OUT))),
         extra={"census/link-counter.py": ("link", S_ABS)})
    case("sym-pop-outside", "census/link-pop.tsv is a symlink blob -> sentinel",
         [F(1, "C1 POPULATION-MISSING"), F(1, "C1 POPULATION-DIGEST"), F(1, "C1 POPULATION-DIGEST", "C1 POPULATION-EMPTY")],
         lambda B: doc(std(B, Population="census/link-pop.tsv sha256=" + H(OUT))),
         extra={"census/link-pop.tsv": ("link", S_ABS)})
    case("sym-control-outside", "census/link-ctl.txt is a symlink blob -> sentinel (EXIT=1)",
         [F(1, "C1 CONTROL-MISSING"), F(1, "C1 CONTROL-NOT-RED")],
         lambda B: doc(std(B, Control="census/link-ctl.txt")),
         extra={"census/link-ctl.txt": ("link", S_ABS)})
    case("sym-prereg-outside", "--prereg names a symlink blob -> outside prereg text",
         [F(1, "C0 NO-CLAIMS"), (2, frozenset())],
         lambda B: doc(std(B)), extra={"census/prereg-link.txt": ("link", S_PRE_ABS)},
         arg="census/prereg-link.txt")

    # --- --prereg itself
    case("prereg-abs-outside", "--prereg absolute path to a valid prereg outside the repo",
         REFUSE, lambda B: doc(std(B)), arg=S_PRE_ABS)
    case("prereg-trav", "--prereg ../ to a valid prereg outside the repo",
         REFUSE, lambda B: doc(std(B)), arg="../OUTSIDE-PREREG.txt")
    case("prereg-dash", "--prereg -x (option-looking value)", REFUSE, lambda B: doc(std(B)), arg="-x")

    # --- path starting with '-' (git option injection)
    case("dash-counter", "Counter --output=ABS: git log --output would write outside",
         [F(1, "C1 COUNTER-MISSING")],
         lambda B: doc(std(B, Counter="--output=%s sha256=%s" % (PWN_C, H(COUNTER)))))
    case("dash-pop", "Population --output=ABS", [F(1, "C1 POPULATION-MISSING")],
         lambda B: doc(std(B, Population="--output=%s sha256=%s" % (PWN_P, H(POP)))))
    case("dash-control", "Control --output=ABS", [F(1, "C1 CONTROL-MISSING")],
         lambda B: doc(std(B, Control="--output=" + PWN_T)))
    case("dash-base", "Base --output=ABS (not full40)", [F(1, "C1 BASE-UNRESOLVED")],
         lambda B: doc(std(B, Base="--output=" + PWN_B)))

    # --- Base shapes
    case("base-main", "Base: main (resolves, not full40)", [F(1, "C1 BASE-UNRESOLVED")],
         lambda B: doc(std(B, Base="main")))
    case("base-head", "Base: HEAD~0 (resolves, not full40)", [F(1, "C1 BASE-UNRESOLVED")],
         lambda B: doc(std(B, Base="HEAD~0")))
    case("base-short", "Base: 12-char prefix of a real commit", [F(1, "C1 BASE-UNRESOLVED")],
         lambda B: doc(std(B, Base=B[:12])))
    case("base-upper", "Base: uppercase full40 (spec says full40; ambiguous)",
         [F(1, "C1 BASE-UNRESOLVED"), (0, frozenset())], lambda B: doc(std(B, Base=B.upper())))

    # --- glob / directory / submodule / overlong names
    case("glob-counter", "Counter census/*.py (pathspec glob, no literal blob)",
         [F(1, "C1 COUNTER-MISSING")],
         lambda B: doc(std(B, Counter="census/*.py sha256=" + H(COUNTER))))
    case("glob-pop", "Population census/*.tsv (glob)", [F(1, "C1 POPULATION-MISSING")],
         lambda B: doc(std(B, Population="census/*.tsv sha256=" + H(POP))))
    case("dir-counter", "Counter names a tree (directory), not a blob",
         [F(1, "C1 COUNTER-MISSING")], lambda B: doc(std(B, Counter="census sha256=" + H(COUNTER))))
    case("submodule-counter", "Counter names a gitlink (160000) with an empty worktree dir",
         [F(1, "C1 COUNTER-MISSING")],
         lambda B: doc(std(B, Counter="vendor/sub sha256=" + H(COUNTER))),
         extra={"vendor/sub": ("gitlink", VENDOR_OID)})
    case("submodule-pop", "Population names a gitlink", [F(1, "C1 POPULATION-MISSING")],
         lambda B: doc(std(B, Population="vendor/sub sha256=" + H(POP))),
         extra={"vendor/sub": ("gitlink", VENDOR_OID)})
    case("name-too-long", "Counter path component 300 bytes (ENAMETOOLONG on open)",
         [F(1, "C1 COUNTER-MISSING")],
         lambda B: doc(std(B, Counter="census/" + "a" * 300 + ".py sha256=" + H(COUNTER))))
    case("dotgit-counter", "Counter .git/config (repository internals, not a tree path)",
         [F(1, "C1 COUNTER-MISSING")],
         lambda B: doc(std(B, Counter=".git/config sha256=" + H(COUNTER))))
    case("counter-trailing-slash", "Counter census/c1.py/ (file used as directory)",
         [F(1, "C1 COUNTER-MISSING")],
         lambda B: doc(std(B, Counter="census/c1.py/ sha256=" + H(COUNTER))))

    # --- shell metacharacters and odd-but-legal names; must be read as data
    case("shell-meta-names", "names with $(), ;, backticks (no spaces: ${IFS} stands in): must be data",
         CLEAN,
         lambda B: doc(std(B, Counter="census/$(touch${IFS}PWNED-EXEC).py sha256=" + H(COUNTER),
                           Population="census/a;touch${IFS}PWNED-SEMI.tsv sha256=" + H(POP),
                           Control="census/x`touch${IFS}PWNED-BT`.txt")),
         extra={"census/$(touch${IFS}PWNED-EXEC).py": COUNTER, "census/a;touch${IFS}PWNED-SEMI.tsv": POP,
                "census/x`touch${IFS}PWNED-BT`.txt": CTL_RED})
    case("space-path", "Counter path containing a space (legal repo path)", CLEAN,
         lambda B: doc(std(B, Counter="census/my counter.py sha256=" + H(COUNTER))),
         extra={"census/my counter.py": COUNTER})
    case("unicode-path", "Counter path non-ASCII (quotePath)", CLEAN,
         lambda B: doc(std(B, Counter="census/\u00fcn\u00ef.py sha256=" + H(COUNTER))),
         extra={"census/\u00fcn\u00ef.py": COUNTER})

    # --- huge input
    case("long-value", "Counter value preceded by 200000 spaces", CLEAN,
         lambda B: doc(std(B, Counter=" " * 200000 + "census/c1.py sha256=" + H(COUNTER))))
    case("huge-claims", "2000 valid claim blocks in one prereg", CLEAN,
         lambda B: doc(*[std(B) for _ in range(2000)]))
    case("huge-population", "50 MiB Population blob", CLEAN,
         lambda B: doc(std(B, Population="census/pop-big.tsv sha256=" + H(BIG))),
         extra={"census/pop-big.tsv": BIG})

    # --- worktree-only traps: verdicts must come from the blob at --rev only
    case("wt-fifo-pop", "worktree census/pop.tsv replaced by a FIFO (blob regular)", CLEAN,
         lambda B: doc(std(B)), post=post_fifo)
    case("wt-devzero-pop", "worktree census/pop.tsv -> /dev/zero (blob regular)", CLEAN,
         lambda B: doc(std(B)), post=post_devzero)
    case("wt-outside-c1", "worktree census/c1.py -> sentinel (blob regular)", CLEAN,
         lambda B: doc(std(B)), post=post_outside_c1)
    case("wt-tamper-pop", "worktree census/pop.tsv edited, uncommitted", CLEAN,
         lambda B: doc(std(B)), post=post_tamper)

    # --- prereg grammar edges
    case("dup-counter-key", "two Counter lines in one claim; second escapes", ANY,
         lambda B: ("# prereg\nRound: 41\n\n## C1 — claim 1\nBase: %s\nCounter: census/c1.py sha256=%s\n"
                    "Counter: ../OUTSIDE-SECRET.txt sha256=%s\nPopulation: census/pop.tsv sha256=%s\n"
                    "Control: census/control.txt\nTarget: t\nKill: k\n" % (B, H(COUNTER), H(OUT), H(POP))
                    ).encode("utf-8"))
    case("second-claim-bad", "claim 1 clean, claim 2 escapes", [F(1, "C2 COUNTER-MISSING")],
         lambda B: doc(std(B), std(B, Counter="../OUTSIDE-SECRET.txt sha256=" + H(OUT))))
    case("round-traversal", "Round: 41/../../x with a post-freeze dispatch file", ANY,
         lambda B: doc(std(B)).replace(b"Round: 41", b"Round: 41/../../x"),
         post=post_dispatch_after_regular)
    case("no-round-line", "prereg without a Round line, dispatch file before freeze", ANY,
         lambda B: doc(std(B)).replace(b"Round: 41\n", b""),
         extra={".ufo/waves/round-41/w1-dispatch.json": b"{}\n"})
    case("nonutf8-prereg", "invalid UTF-8 bytes in a comment line", ANY,
         lambda B: b"# prereg\nRound: 41\n# \xff\xfe junk\n\n" + doc(std(B))[len(b"# prereg\nRound: 41\n\n"):])
    case("crlf-prereg", "CRLF line endings throughout", ANY,
         lambda B: doc(std(B)).replace(b"\n", b"\r\n"))
    case("control-exit-zero", "Control last line EXIT=0 (zero is not nonzero)",
         [F(1, "C1 CONTROL-NOT-RED")], lambda B: doc(std(B, Control="census/ctl-green.txt")),
         extra={"census/ctl-green.txt": CTL_GREEN})
    case("control-exit-00", "Control last line EXIT=00", [F(1, "C1 CONTROL-NOT-RED")],
         lambda B: doc(std(B, Control="census/ctl-00.txt")), extra={"census/ctl-00.txt": CTL_00})
    case("control-exit-bignum", "Control EXIT= 32-digit nonzero integer", CLEAN,
         lambda B: doc(std(B, Control="census/ctl-big.txt")), extra={"census/ctl-big.txt": CTL_BIG})

    # --- dispatch / tree walk
    case("dispatch-after-symlink-outside", "post-freeze w1-dispatch.json is a symlink -> sentinel",
         CLEAN, lambda B: doc(std(B)), post=post_dispatch_after_link)
    case("dispatch-before-symlink-outside", "pre-freeze w1-dispatch.json is a symlink -> sentinel",
         [F(1, "C0 DISPATCH-BEFORE-FREEZE")], lambda B: doc(std(B)),
         extra={".ufo/waves/round-41/w1-dispatch.json": ("link", S_ABS)})
    case("dispatch-before-regular", "pre-freeze w1-dispatch.json regular file",
         [F(1, "C0 DISPATCH-BEFORE-FREEZE")], lambda B: doc(std(B)),
         extra={".ufo/waves/round-41/w1-dispatch.json": b"{}\n"})
    case("loop-symlink-in-waves", "symlink loop .ufo/waves/round-41/loop -> ..", CLEAN,
         lambda B: doc(std(B)), extra={".ufo/waves/round-41/loop": ("link", "..")})

    return cases


def fixtures(cases):
    os.makedirs(FX, exist_ok=True)
    # the outside sentinels live in FX, outside every fixture repository
    with open(S_ABS, "wb") as fh:
        fh.write(OUT)
    built = {}
    for c in cases:
        d, B, F_, T, text = make(c["name"], c["extra"], c["prereg"], c["post"])
        c["dir"], c["base"], c["freeze"], c["tip"] = d, B, F_, T
        built[c["name"]] = d
        if c["name"] == "clean":
            with open(S_PRE_ABS, "wb") as fh:
                fh.write(text)
    return built


def run_group(cmd, cwd, timeout):
    p = subprocess.Popen(cmd, cwd=cwd, env=GIT_ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         start_new_session=True)
    try:
        out, err = p.communicate(timeout=timeout)
        return p.returncode, out, err, False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = p.communicate()
        return None, out, err, True


OPEN_RE = re.compile(r'openat\([^,]*, "((?:[^"\\]|\\.)*)"')
EXEC_RE = re.compile(r'execve\("((?:[^"\\]|\\.)*)"')
FINDING_RE = re.compile(r"^FINDING (\S+) (\S+)", re.M)


def markers():
    found = []
    for base in (RUNS, FX):
        if os.path.isdir(base):
            for f in os.listdir(base):
                if f.startswith("PWN"):
                    found.append(os.path.join(base, f))
    for dp, dn, fn in os.walk(FX):
        if os.path.basename(dp) in (".git",):
            dn[:] = []
            continue
        for f in fn:
            if f.startswith("PWN"):
                found.append(os.path.join(dp, f))
        dn[:] = [x for x in dn if x != ".git"]
    return found


def clear_markers():
    for m in markers():
        try:
            os.remove(m)
        except OSError:
            pass


def judge(acc, rc, classes):
    if acc == ANY:
        return True
    return any(rc == arc and classes == acls for arc, acls in acc)


def run_candidate(name, cand, c, tag):
    trace = os.path.join(RUNS, "%s.%s.%s.trace" % (name, c["name"], tag))
    cmd = ["strace", "-f", "-qq", "-e", "trace=openat,execve", "-o", trace,
           "python3", "-B", cand, "--root", c["dir"], "--prereg", c["arg"], "--rev", c["tip"]]
    t0 = time.time()
    clear_markers()
    rc, out, err, hung = run_group(cmd, RUNS, TIMEOUT)
    dt = time.time() - t0
    stdout = out.decode("utf-8", "replace")
    stderr = err.decode("utf-8", "replace")
    opens, execs = [], []
    if os.path.exists(trace):
        with open(trace, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = OPEN_RE.search(line)
                if m:
                    opens.append(m.group(1))
                m = EXEC_RE.search(line)
                if m:
                    execs.append(m.group(1))
        os.remove(trace)
    d_real = os.path.realpath(c["dir"])
    escape = sorted({p for p in opens if "OUTSIDE-" in p or "PWN-" in p or p in ("/dev/zero", "/dev/random", "/dev/urandom", "/dev/full")})
    wt = sorted({p for p in opens if (p.startswith(c["dir"] + "/") or p.startswith(d_real + "/"))
                 and "/.git" not in p[len(c["dir"]):len(c["dir"]) + 6]})
    shell = sorted({e for e in execs if e.endswith(("/sh", "/bash", "/dash"))})
    classes = frozenset("%s %s" % (a, b) for a, b in FINDING_RE.findall(stdout))
    mk = markers()
    tb = "Traceback (most recent call last)" in stderr
    ok_acc = judge(c["accept"], rc, classes)
    fail_reasons = []
    if hung:
        fail_reasons.append("HANG(timeout %ds)" % TIMEOUT)
    if tb:
        fail_reasons.append("TRACEBACK")
    if escape:
        fail_reasons.append("READ-OUTSIDE/DEVICE")
    if shell:
        fail_reasons.append("EXEC-SHELL")
    if mk:
        fail_reasons.append("MARKER-WRITTEN")
    if not ok_acc:
        fail_reasons.append("OUTCOME")
    return {
        "candidate": name, "case": c["name"], "rc": rc, "hung": hung, "secs": round(dt, 3),
        "classes": sorted(classes), "traceback": tb, "escape_opens": escape,
        "worktree_opens": wt[:20], "shell_execs": shell, "markers": mk,
        "outcome_ok": ok_acc, "verdict": "PASS" if not fail_reasons else "FAIL " + ",".join(fail_reasons),
        "stdout_head": stdout[:400], "stderr_tail": stderr[-400:],
    }


def naive_probe(c):
    """What a straightforward implementation does with the same path strings."""
    text = c["prereg_text"]
    rev = c["tip"]
    d = c["dir"]
    res = {"paths": {}}
    seen = set()
    for key in ("Base", "Counter", "Population", "Control"):
        for m in re.finditer(r"^%s:[ \t]*(.*)$" % key, text, re.M):
            val = m.group(1).strip()
            path = val if key == "Base" else val.split(" sha256=")[0]
            if len(path) > 2000 or (key, path) in seen:
                continue
            seen.add((key, path))
            row = {}
            py = ("import os,sys,hashlib\n"
                  "p=os.path.join(sys.argv[1],sys.argv[2])\n"
                  "try:\n"
                  " f=open(p,'rb'); data=f.read(4<<20)\n"
                  " print('WT-READ bytes=%d%s sha=%s real=%s' % (len(data), ' (4MiB cap reached: unbounded)' if len(data)==(4<<20) else '', hashlib.sha256(data).hexdigest()[:12], os.path.realpath(p)))\n"
                  "except Exception as e:\n"
                  " print('WT-EXC %s: %s' % (type(e).__name__, e))\n")
            clear_markers()
            rc, out, err, hung = run_group(["python3", "-c", py, d, path], RUNS, 5)
            row["worktree_open"] = "HANG(5s, blocked in open or read)" if hung else out.decode("utf-8", "replace").strip()[:200]
            p2 = subprocess.run(["git", "-C", d, "cat-file", "-t", "%s:%s" % (rev, path)], env=GIT_ENV,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=RUNS, check=False)
            row["git_cat_file_t"] = "rc=%d %s" % (p2.returncode, (p2.stdout + p2.stderr).decode("utf-8", "replace").strip()[:120])
            p3 = subprocess.run(["git", "-C", d, "log", "--diff-filter=A", "--format=%H", "--", path],
                                env=GIT_ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=RUNS, check=False)
            row["git_log_pathspec"] = "rc=%d lines=%d %s" % (p3.returncode, len(p3.stdout.split()),
                                                              p3.stderr.decode("utf-8", "replace").strip()[:120])
            p4 = subprocess.run(["git", "-C", d, "log", "--diff-filter=A", "--format=%H", path],
                                env=GIT_ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=RUNS, check=False)
            row["git_log_no_dashdash"] = "rc=%d lines=%d %s" % (p4.returncode, len(p4.stdout.split()),
                                                                 p4.stderr.decode("utf-8", "replace").strip()[:120])
            clear_markers()
            p5 = subprocess.run("git -C %s cat-file -t %s:%s" % (d, rev, path), shell=True, env=GIT_ENV,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=RUNS, check=False)
            row["naive_shell_cat_file"] = "rc=%d" % p5.returncode
            row["naive_shell_markers"] = [m for m in markers()]
            row["post_run_markers_after_no_dashdash_and_shell"] = markers()
            res["paths"].setdefault(key, []).append({"path": path[:160], **row})
            clear_markers()
    return res


def main():
    os.makedirs(RUNS, exist_ok=True)
    os.makedirs(RECEIPTS, exist_ok=True)
    cases = build_cases()
    fixtures(cases)
    for c in cases:
        c["prereg_text"] = open(os.path.join(c["dir"], "prereg.txt"), "rb").read().decode("utf-8", "replace")
    cands = {n: os.path.join(LANE, ".ufo/waves/round-41/w1/R41%s/souji-freeze-check.py" % n) for n in CANDS}
    sha = {n: H(open(p, "rb").read()) for n, p in cands.items()}
    results = []
    for c in cases:
        for n in CANDS:
            results.append(run_candidate(n, cands[n], c, "cand"))
    prim = []
    for c in cases:
        c_prim = {"case": c["name"]}
        c_prim.update(naive_probe(c))
        prim.append(c_prim)
    meta = {
        "candidates": {n: {"path": cands[n], "sha256": sha[n]} for n in CANDS},
        "cases": [{"name": c["name"], "desc": c["desc"], "dir": c["dir"], "base": c["base"],
                   "freeze": c["freeze"], "tip": c["tip"], "prereg_arg": c["arg"],
                   "accept": c["accept"] if c["accept"] == ANY else [[a, sorted(b)] for a, b in c["accept"]]}
                  for c in cases],
        "git": subprocess.run(["git", "--version"], stdout=subprocess.PIPE, text=True).stdout.strip(),
    }
    with open(os.path.join(RECEIPTS, "candidates.json"), "w", encoding="utf-8") as fh:
        json.dump({"meta": meta, "results": results}, fh, indent=1, ensure_ascii=False)
    with open(os.path.join(RECEIPTS, "naive-primitives.json"), "w", encoding="utf-8") as fh:
        json.dump(prim, fh, indent=1, ensure_ascii=False)
    lines = []
    for c in cases:
        row = [r for r in results if r["case"] == c["name"]]
        lines.append("%-28s " % c["name"] + " | ".join("%s:%s" % (r["candidate"][-2:], "PASS" if r["verdict"] == "PASS" else "FAIL") for r in row))
    with open(os.path.join(RECEIPTS, "matrix.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("cases=%d candidates=%d runs=%d fails=%d" % (len(cases), len(CANDS), len(results),
                                                       sum(1 for r in results if r["verdict"] != "PASS")))


if __name__ == "__main__":
    sys.exit(main())
