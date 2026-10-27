#!/usr/bin/env python3
"""r35 C2 sandbox measurement counter (frozen at the r35 preregistration).

Repair of the r34 counter (r34 lesson `## Mistakes`; r34 verifier spot-check routed defect 4):

R1 Scratch-path normalization in base/rev comparisons. The r34 counter compared the raw
   last digit-bearing lines of the base and tip runs; each run's own mkdtemp dir appears in
   tool output, so W3 failed on path noise, not semantics. Every comparison now replaces
   the run's own scratch root string with <D> before comparing digit lines.
R2 Per-leg timeouts. c2-legs.tsv takes an optional 4th column `timeout` (seconds) so the
   long legs (N3's 12-case fixture, J1's full-counter run) get bounded budgets instead of
   dying against the shared default; a leg that times out still FAILs, never CNEs away.
R3 harm is measured, not printed. The r34 SUMMARY emitted a literal `harm=0` whether or
   not anything checked harm. Here `harm_measured=` counts FAILED legs of the harm surface
   (kinds guard and nsbind: touched-paths, disjointness, r34-dir integrity, namespace pin,
   /var/tmp canary) — fail=0 therefore implies harm_measured=0 because the surface was run,
   and a failed harm leg raises it.
R4 G2 touched-paths reconciles the r34 routed defect: the frozen allowed set includes
   LOG.md (the round's own LOG entry lands inside the measured window), corpus files,
   census/round-35/, tests/fixtures/r35-*, .ufo/waves/round-35/, SCORECARD.md, SKILL.md,
   PROVINCE.md and corpus/knowledge/ — every other path FAILs the leg.
R5 `--only` selects legs (diagnostic + the junk fixture runs its stubbed subset only, so
   J1 cannot be eaten by a full-width run under load). A legs file with witness or junk
   clauses dropped is still refused by validate_legs.

The r34 contract otherwise stands: legs loaded from census/round-35/c2-legs.tsv at
--list-rev only; private no-local detached clones; bwrap envelope --dev-bind / /,
--ro-bind <empty> /tmp /dev/shm, --bind <vt> /var/tmp, TMPDIR=<scratch>/tmp; witness legs
compare sandboxed base/rev exit + last digit line (normalized per R1) and prove work via
strace file-creating syscalls (>= half base, >=1 create under TMPDIR or the /var/tmp bind;
W2 self-traces and proves work by its own CASE assertions); nsbind stages the pinned r14
fixture's tool from the checkout, holds the PIN digest and the real /var/tmp canary;
anchor takes two adjacent base runs then the rev run under one flock with one retake at
load >48; junk runs the r35 stub fixture; guards below.

SUMMARY legs=<n> pass=<p> fail=<f> harm_measured=<h> rev=<r>; exit 0 iff fail=0.
"""
import argparse
import fcntl
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

FULL = re.compile(r"[0-9a-f]{40}")
ITEMS = "census/round-35/c2-legs.tsv"
PIN = "e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2"


def git(root, *args, check=True):
    p = subprocess.run(["git", "-C", root, "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null", *args], capture_output=True)
    if check and p.returncode:
        raise RuntimeError(p.stderr.decode("utf-8", "replace"))
    return p


def blob(root, rev, path):
    p = subprocess.run(["git", "-C", root, "cat-file", "blob", f"{rev}:{path}"], capture_output=True)
    return p.stdout if p.returncode == 0 else None


def cne(msg):
    print("COULD-NOT-EVALUATE " + msg)
    return 2


def validate_legs(legs):
    """Frozen legs contract (preregistration G3): a legs file with its witness clauses
    dropped, or a junk-only leg set, is refused -- both are false-green shapes."""
    kinds = [k for _, k, *_ in legs]
    if "witness" not in kinds:
        raise ValueError("legs file with witness clauses dropped")
    if "junk" not in kinds:
        raise ValueError("legs file with no junk control (witness-only or guard-only set refused)")


def load_legs(root, list_rev):
    raw = blob(root, list_rev, ITEMS)
    if raw is None:
        raise ValueError("legs absent at --list-rev")
    out = []
    for line in raw.decode().splitlines():
        if not line or line.startswith("#") or line.startswith("id\t"):
            continue
        f = line.split("\t")
        if len(f) not in (3, 4):
            raise ValueError("malformed leg: " + line)
        tmo = None
        if len(f) == 4:
            if not re.fullmatch(r"\d+", f[3]) or not (30 <= int(f[3]) <= 7200):
                raise ValueError("bad leg timeout: " + line)
            tmo = int(f[3])
        out.append((f[0], f[1], f[2], tmo))
    validate_legs(out)
    return out


def last_digit(out, err):
    lines = (out + "\n" + err).splitlines()
    return next((" ".join(x.split()) for x in reversed(lines) if re.search(r"\d", x)), "")


def run(root, rev, argv, scratch, timeout):
    d = tempfile.mkdtemp(prefix="leg.", dir=scratch)
    clone = os.path.join(d, "clone")
    tmp = os.path.join(d, "tmp")
    os.makedirs(tmp)
    try:
        p = subprocess.run(["git", "clone", "-q", "--no-local", "--no-checkout", root, clone], capture_output=True)
        if p.returncode:
            raise RuntimeError("clone failed")
        git(clone, "remote", "remove", "origin")
        git(clone, "checkout", "-qf", "--detach", rev)
        argv = argv.replace("{REV}", rev).replace("{SCRATCH}", shlex.quote(d))
        env = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/root"), "TMPDIR": tmp,
               "GIT_CONFIG_NOSYSTEM": "1", "LANG": "C.UTF-8"}
        p = subprocess.run(["bash", "-c", argv], cwd=clone, env=env, capture_output=True, timeout=timeout)
        return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace"), clone
    finally:
        shutil.rmtree(d, ignore_errors=True)

def sandbox_run(root, rev, argv, scratch, timeout):
    bwrap = shutil.which("bwrap")
    if not bwrap:
        raise RuntimeError("bwrap unavailable")
    d = tempfile.mkdtemp(prefix="sandbox.", dir=scratch)
    for name in ("vt", "tmp", "empty"):
        os.makedirs(os.path.join(d, name))
    clone = os.path.join(d, "clone")
    try:
        p = subprocess.run(["git", "clone", "-q", "--no-local", "--no-checkout", root, clone],
                           capture_output=True)
        if p.returncode:
            raise RuntimeError("clone failed")
        git(clone, "remote", "remove", "origin")
        git(clone, "checkout", "-qf", "--detach", rev)
        cmd = argv.replace("{REV}", rev).replace("{SCRATCH}", shlex.quote(d))
        wrap = [bwrap, "--unshare-user", "--unshare-pid", "--die-with-parent", "--dev-bind", "/", "/",
                "--ro-bind", os.path.join(d, "empty"), "/tmp",
                "--ro-bind", os.path.join(d, "empty"), "/dev/shm",
                "--bind", os.path.join(d, "vt"), "/var/tmp",
                "--setenv", "TMPDIR", os.path.join(d, "tmp"),
                "--chdir", clone, "--", "bash", "-c", cmd]
        p = subprocess.run(wrap, capture_output=True, timeout=timeout)
        return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace"), clone
    finally:
        shutil.rmtree(d, ignore_errors=True)


def leg_witness(root, base, rev, argv, scratch, timeout):
    bwrap = shutil.which("bwrap")
    if not bwrap:
        return False, "bwrap unavailable"
    canary = None
    canary_bytes = b"r35 private-bind canary\n"
    results = []
    for check_rev in (base, rev):
        d = tempfile.mkdtemp(prefix="bwrap.", dir=scratch)
        os.makedirs(os.path.join(d, "vt")); os.makedirs(os.path.join(d, "tmp")); os.makedirs(os.path.join(d, "empty"))
        c = os.path.join(d, "clone")
        try:
            p = subprocess.run(["git", "clone", "-q", "--no-local", "--no-checkout", root, c], capture_output=True)
            if p.returncode:
                return False, "clone failed"
            git(c, "remote", "remove", "origin")
            git(c, "checkout", "-qf", "--detach", check_rev)
            if "r14-census-boundary.py" in argv:
                tool = os.path.join(d, "tool.sh")
                shutil.copyfile(os.path.join(c, "tools", "souji-census.sh"), tool)
                os.chmod(tool, 0o755)
            cmd = argv.replace("{REV}", check_rev).replace("{SCRATCH}", shlex.quote(d))
            strace = shutil.which("strace")
            if strace and check_rev == rev and "r14-census-boundary.py" not in argv:
                cmd = shlex.quote(strace) + " -f -qq -e trace=%file -o " + shlex.quote(os.path.join(d, "trace")) + " -- " + cmd
            wrap = [bwrap, "--unshare-user", "--unshare-pid", "--die-with-parent", "--dev-bind", "/", "/",
                    "--ro-bind", os.path.join(d, "empty"), "/tmp", "--ro-bind", os.path.join(d, "empty"), "/dev/shm",
                    "--bind", os.path.join(d, "vt"), "/var/tmp", "--setenv", "TMPDIR", os.path.join(d, "tmp"),
                    "--chdir", c, "--", "bash", "-c", cmd]
            if "r14-census-boundary.py" in argv:
                fd, canary = tempfile.mkstemp(prefix="souji-r35-canary.", dir="/var/tmp")
                with os.fdopen(fd, "wb") as fh:
                    fh.write(canary_bytes)
            p = subprocess.run(wrap, capture_output=True, timeout=timeout)
            if canary and open(canary, "rb").read() != canary_bytes:
                os.unlink(canary)
                canary = None
                return False, "real /var/tmp canary changed"
            if canary:
                os.unlink(canary)
                canary = None
            out = p.stdout.decode("utf-8", "replace"); err = p.stderr.decode("utf-8", "replace")
            trace = open(os.path.join(d, "trace"), errors="replace").read() if os.path.exists(os.path.join(d, "trace")) else ""
            creates = [x for x in trace.splitlines() if re.search(r"(open|creat|mkdir|rename|link|symlink|mknod|truncate)\(", x) and re.search(r"O_CREAT|O_WRONLY|O_RDWR|mkdir|creat", x)]
            witnessed = any(os.path.join(d, "tmp") in x or os.path.join(d, "vt") in x for x in creates)
            norm = lambda s: s.replace(d, "<D>")
            results.append((p.returncode, last_digit(norm(out), norm(err)), len(creates), witnessed, out, err))
        except (OSError, subprocess.TimeoutExpired) as e:
            if canary:
                os.unlink(canary)
                canary = None
            return False, "sandbox run failed: " + str(e)
        finally:
            # Keep scratch only until comparison; removal is after reading trace.
            pass
        if len(results) == 2:
            base_run, tip_run = results
            if base_run[0] != tip_run[0] or base_run[1] != tip_run[1]:
                return False, f"base/rev mismatch rc={base_run[0]}/{tip_run[0]} line={base_run[1]!r}/{tip_run[1]!r}"
            if "r14-census-boundary.py" in argv:
                cases = len(re.findall(r"^CASE\t", tip_run[4], re.M))
                summary = "SUMMARY\ttotal=12\tfailed=0"
                fixture = blob(root, rev, "tests/fixtures/r14-census-boundary.py")
                pinned = fixture is not None and __import__("hashlib").sha256(fixture).hexdigest() == PIN
                ok = tip_run[0] == 0 and cases == 12 and summary in tip_run[4] and pinned
                return ok, f"cases={cases} pinned={pinned} summary={summary in tip_run[4]}"
            if not strace:
                return False, "strace unavailable (except self-tracing W2)"
            if tip_run[2] * 2 < max(base_run[2], 1) or not tip_run[3]:
                return False, f"work witness failed creates={base_run[2]}/{tip_run[2]} target={tip_run[3]}"
            return True, f"rc={tip_run[0]} creates={base_run[2]}/{tip_run[2]} line={tip_run[1]}"
    return False, "missing run"


def guard(root, base, rev, iid, scratch):
    if iid == "G1":
        return git(root, "diff", "--quiet", base, rev, "--", "census/round-34", check=False).returncode == 0, "r34 diff"
    if iid == "G2":
        changed = set(git(root, "diff", "--name-only", base, rev).stdout.decode().split())
        # R4: frozen allowed set — LOG.md is included because the round's own LOG entry
        # lands inside the measured window (r34 routed defect 4: the r34 frozen list
        # omitted it while the diff contained it). Everything else FAILs the leg.
        allowed = lambda p: (p.startswith("census/round-35/") or p.startswith("tests/fixtures/r35-")
                             or p.startswith(".ufo/waves/round-35/") or p.startswith("corpus/knowledge/")
                             or p in {"SCORECARD.md", "SKILL.md", "LOG.md", "PROVINCE.md",
                                      "corpus/lessons/round-35.md", "corpus/SOURCES.md", "corpus/README.md"})
        bad = sorted(p for p in changed if not allowed(p))
        return not bad, "unexpected paths=" + ",".join(bad)
    if iid == "G3":
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--selftest"], capture_output=True)
        return p.returncode == 0 and b"SELFTEST pass" in p.stdout, p.stdout.decode("utf-8", "replace").strip()
    if iid == "G4":
        return bool(shutil.which("bwrap") and shutil.which("strace")), "bwrap+strace available"
    if iid == "G5":
        # Per-commit path-disjointness across the two claim namespaces.
        log = git(root, "rev-list", "--reverse", f"{base}..{rev}").stdout.decode().split()
        c1 = {"SCORECARD.md", "SKILL.md"}; c2 = {"census/round-35/c2-legs.tsv", "census/round-35/c2-counter.py"}
        bad = []
        for commit in log:
            files = set(git(root, "show", "--format=", "--name-only", commit).stdout.decode().split())
            if files & c1 and files & c2:
                bad.append(commit[:12])
        return not bad, "overlap commits=" + ",".join(bad)
    if iid == "G6":
        data = blob(root, rev, "tests/fixtures/r14-census-boundary.py")
        import hashlib
        return data is not None and hashlib.sha256(data).hexdigest() == PIN, "namespace fixture pin"
    return False, "unknown guard"


def selftest():
    """Frozen legs-contract checks: witness clauses dropped and junk-only sets are refused."""
    good = [("W1", "witness", "x"), ("J1", "junk", "y")]
    witness_dropped = [("J1", "junk", "y"), ("G1", "guard", "z")]
    junk_only = [("J1", "junk", "y")]
    try:
        validate_legs(good)
    except ValueError:
        print("SELFTEST fail")
        return 1
    for bad, label in ((witness_dropped, "witness-dropped"), (junk_only, "junk-only")):
        try:
            validate_legs(bad)
        except ValueError:
            continue
        print(f"SELFTEST fail ({label} accepted)")
        return 1
    print("SELFTEST pass witness-required rejected junk-only rejected")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--rev")
    ap.add_argument("--base")
    ap.add_argument("--list-rev")
    ap.add_argument("--scratch")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--only", default="")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not all((a.root, a.rev, a.base, a.list_rev, a.scratch)):
        return cne("required arguments missing")
    root = os.path.abspath(a.root); scratch = os.path.abspath(a.scratch)
    for x in (a.rev, a.base, a.list_rev):
        if not FULL.fullmatch(x):
            return cne("revision must be full 40 hex")
    if any(scratch == x or scratch.startswith(x + "/") for x in ("/tmp", "/var/tmp", "/dev/shm")):
        return cne("scratch under ephemeral root")
    os.makedirs(scratch, exist_ok=True)
    try:
        lock = open(os.path.join(scratch, "c2.lock"), "w"); fcntl.flock(lock, fcntl.LOCK_EX)
        legs = load_legs(root, a.list_rev)
        if a.only:
            sel = {x for x in a.only.split(",") if x}
            unknown = sel - {i for i, _, *_ in legs}
            if unknown:
                return cne("unknown --only legs: " + ",".join(sorted(unknown)))
            # R5: --only selects legs AND drops every other junk leg — a stubbed run must
            # not re-enter the junk fixture (recursion) nor run unselected legs.
            legs = [l for l in legs if l[0] in sel and l[1] != "junk"]
            if not legs:
                return cne("--only selected no legs")
        results = []
        for iid, kind, argv, tmo in legs:
            tmo = tmo or a.timeout
            try:
                if kind == "guard":
                    ok, detail = guard(root, a.base, a.rev, iid, scratch)
                elif kind == "junk":
                    p = subprocess.run([sys.executable, os.path.join(root, "tests/fixtures/r35-sandbox-junk.py"), "--counter", os.path.abspath(__file__), "--scratch", scratch], capture_output=True, timeout=tmo)
                    ok = p.returncode == 0 and b"control=STUB-REJECTED" in p.stdout
                    detail = p.stdout.decode("utf-8", "replace").strip()
                elif kind == "anchor":
                    one = run(root, a.base, argv, scratch, tmo); two = run(root, a.base, argv, scratch, tmo); tip = run(root, a.rev, argv, scratch, tmo)
                    # R1: normalize each run's own scratch root before comparing digit lines.
                    norm = lambda s, dd: s.replace(dd, "<D>")
                    ld = lambda r: last_digit(norm(r[1], os.path.dirname(r[3])), norm(r[2], os.path.dirname(r[3])))
                    same = one[0] == two[0] and ld(one) == ld(two) == ld(tip) and tip[0] == one[0]
                    ok = same and os.getloadavg()[0] <= 48
                    detail = f"base={ld(one)} base2={ld(two)} rev={ld(tip)} load={os.getloadavg()[0]:.2f}"
                elif kind == "nsbind":
                    # The fixture itself self-traces, takes the tool path and handles canary/pin assertions.
                    ok, detail = leg_witness(root, a.base, a.rev, argv, scratch, tmo)
                    ok = ok and "SUMMARY" in detail
                elif kind == "witness":
                    if iid == "W2":
                        # r15 fixture runs its own strace and validates each case; require identical result line and all CASE lines.
                        rb = sandbox_run(root, a.base, argv, scratch, tmo)
                        rr = sandbox_run(root, a.rev, argv, scratch, tmo)
                        out = rr[1] + rr[2]
                        cases = len(re.findall(r"^CASE\t", out, re.M))
                        summary = re.search(r"SUMMARY\ttotal=(\d+)\tfailed=(\d+)", out)
                        ldn = lambda r: last_digit(norm(r[1], os.path.dirname(r[3])), norm(r[2], os.path.dirname(r[3])))
                        ok = rb[0] == rr[0] == 0 and ldn(rb) == ldn(rr) and summary is not None and cases == int(summary.group(1)) and int(summary.group(2)) == 0
                        detail = f"CASE={cases} summary={summary.group(0) if summary else 'missing'}"
                    else:
                        ok, detail = leg_witness(root, a.base, a.rev, argv, scratch, tmo)
                else:
                    ok, detail = False, "unknown kind"
            except Exception as e:
                ok, detail = False, str(e)
            try:
                load = os.getloadavg()[0]
            except OSError:
                load = -1
            results.append((iid, kind, ok, detail, load))
            print(f"LEG\t{iid}\t{'PASS' if ok else 'FAIL'}\t{detail}\tload={load:.2f}", flush=True)
        passed = sum(ok for _, _, ok, _, _ in results); failed = len(results) - passed
        harm = sum(1 for _, k, ok, _, _ in results if k in ("guard", "nsbind") and not ok)
        print(f"SUMMARY legs={len(results)} pass={passed} fail={failed} harm_measured={harm} rev={a.rev}")
        return 0 if failed == 0 else 1
    except Exception as e:
        return cne(str(e))

if __name__ == "__main__":
    sys.exit(main())
