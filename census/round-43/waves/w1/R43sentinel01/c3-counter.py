#!/usr/bin/env python3
"""census/round-43/c3-counter.py — r43 C3 (coverage): kill the 16 deterministic condition-level
survivors, refuse a leaf-symlink --json target, and keep every prior drift fixture green.

Claim. Round 42's battery killed its frozen 13 but left 16 deterministic non-equivalent survivors
of all nine committed drift fixtures (census/round-42/waves/w2/R42w2critic04.md section 4; S42 is
race-only and stays a NAMED LIMIT, never scored), and the tool still resolves a leaf symlink named
by --json through realpath before the O_NOFOLLOW walk, so the write follows the link (N10,
R41sentinel01 F1). This round's candidate fixture `tests/fixtures/r43-drift-survivors.py` must kill
every mutant in the frozen population `census/round-43/c3-survivors.tsv` without killing any EQUIV
mutant (no observable behaviour), and the candidate TOOL must refuse a leaf-symlink --json target
with `REFUSAL JSON-TARGET-SYMLINK:` while keeping the nine committed drift fixtures clean.

Fixture protocol: `python3 -B <fixture> --tool PATH --work DIR` prints `case-<name>=PASS|FAIL`
lines and `SUMMARY cases=<n> pass=<p> fail=<f>`; exit 0 iff fail=0. A KILL is: the fixture exits 1,
its own SUMMARY shows fail>0, and no Python traceback in its stderr has a frame whose code file is
the fixture itself (N-C3b fix: tool stderr forwarded through the fixture never blocks a kill; a
traceback that names the fixture is a battery defect, counted in `crashed`, never a kill). A
per-fixture-run timeout is NOT a kill: it is counted in `timed_out` and the target requires 0.

Scoring (every number printed):
  mutants      len(POPULATION rows)            frozen: 16
  killed/survived/crashed/timed_out        candidate fixture over the mutants
  equiv        len(EQUIV) (frozen: 6); equiv_killed must be 0
  old_killed   population mutants killed by any of the 8 pre-r42 PRIOR fixtures applied to the rev
               tool bytes (must be 0: the population is the survivor set of the nine fixtures)
  prior        how many of the 9 committed drift fixtures run clean on the rev tool (must be 9/9)
  cases/pass/fail   the candidate fixture on the rev tool; cases >= 17 and fail=0 required
  n10_before   with the PINNED (unfixed) tool bytes the fixture must fail exactly the frozen case
               `case-json-symlink-leaf` — proved at the base receipt; at a rev whose tool differs
               it prints `base-receipt` (the arm is history, not re-run)
  n10_after    a direct probe run: the rev tool refuses a leaf-symlink --json target with
               `REFUSAL JSON-TARGET-SYMLINK:` exit 2
  sniff_eq_killed   an embedded byte-sniffing control fixture (FAIL iff an old anchor is absent)
               must kill EQUIV mutants (it reads bytes, not behaviour) — requires >= 1
  shim         the fixture run through a logging wrapper must invoke the tool at least once per
               passing case (execution-count shim, Q100)
  stderr_discrimination   embedded N-C3b pair: a forwarded-tool-traceback kill is a KILL, a
               fixture-own traceback is a battery defect
  anchors      every old string (MUTANTS and EQUIV) occurs exactly once in the rev tool and the
               population file lists exactly the MUTANTS ids with their anchor sha256s
  load         load1 at scoring time (recorded, never a verdict)

CLI:
  python3 -B census/round-43/c3-counter.py --root LANE --rev FULL40 [--scratch DIR]
Exit: 0 target met; 1 target unmet (absent fixture included); 2 could-not-evaluate.
Target: `SUMMARY mutants=16 killed=16 survived=0 crashed=0 timed_out=0 equiv=6 equiv_killed=0
old_killed=0 prior=9/9 cases>=17 fail=0 n10_before=base-receipt n10_after=ok sniff_eq_killed>=1
shim=ok stderr_discrimination=ok anchors=ok population=ok` -> exit 0.
"""
import argparse
import concurrent.futures
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

REV_RE = re.compile(r"^[0-9a-f]{40}$")
TOOL = "tools/souji-worktree-drift.py"
FIXTURE = "tests/fixtures/r43-drift-survivors.py"
POPULATION = "census/round-43/c3-survivors.tsv"
BASE_TOOL_SHA256 = "b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6"
N10_CASE = "case-json-symlink-leaf"
PRIOR = ("tests/fixtures/r36-worktree-drift.py", "tests/fixtures/r37-drift-discrimination.py",
         "tests/fixtures/r38-drift-record.py", "tests/fixtures/r38-drift-write-envelope.py",
         "tests/fixtures/r39-drift-record-rules.py", "tests/fixtures/r40-drift-record-branches.py",
         "tests/fixtures/r41-drift-record-order.py", "tests/fixtures/r41-refusal-sites.py",
         "tests/fixtures/r42-drift-conditions.py")
PRE42 = PRIOR[:-1]
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}
SUMMARY_RE = re.compile(r"^SUMMARY (?:cases|probes)=(\d+) pass=(\d+) fail=(\d+)", re.M)
TRACEBACK_FILE = re.compile(r"^  File \"([^\"]+)\", line", re.M)

MUTANTS = (
    ("S03", "            chunk = os.read(fd, 65536)\n            if not chunk:\n                break\n            chunks.append(chunk)",
     "            chunk = os.read(fd, 65536)\n            chunks.append(chunk)\n            break"),
    ("S11", 'TOTAL = re.compile(r"^TOTAL\\trepos=(?P<repos>\\d+)\\tregs=(?P<regs>\\d+)\\tprunable=(?P<prunable>\\d+)$")',
     'TOTAL = re.compile(r"^TOTAL\\trepos=(?P<repos>\\d+)\\tregs=(?P<regs>\\d+)\\tprunable=(?P<prunable>\\d+)")'),
    ("S12", 'ROW = re.compile(r"^REPO\\t(?P<name>[^\\t]+)\\tregs=',
     'ROW = re.compile(r"^REPO\\t(?P<name>[^ \\t]+)\\tregs='),
    ("S13", '(?P<name>[^\\t]+)\\tregs=(?P<regs>\\d+)\\tprunable=',
     '(?P<name>[^\\t]+)\\tregs=(?P<regs>\\d*)\\tprunable='),
    ("S17", 'if total["prunable"] != sum(r["prunable"] for r in rows):',
     'if total["prunable"] > sum(r["prunable"] for r in rows):'),
    ("S22", 'if name == os.path.basename(root.rstrip("/")) and os.path.isdir(os.path.join(root, ".git")):',
     'if name == os.path.basename(root.rstrip("/")):'),
    ("S25", "except OSError:\n        return names",
     "except OSError:\n        raise"),
    ("S33", "root_real = os.path.realpath(root)",
     "root_real = root"),
    ("S34", "root = os.path.abspath(args.root)",
     "root = args.root"),
    ("S35", 'got = git(["rev-parse", "--absolute-git-dir"], resolved, args.timeout)',
     'got = git(["rev-parse", "--absolute-git-dir"], resolved, 20)'),
    ("S43", 'if regs != row["regs"]:',
     'if regs < row["regs"]:'),
    ("S44", 'if prunable != row["prunable"]:',
     'if prunable > row["prunable"]:'),
    ("S53", "inside = os.path.commonpath([json_target, base]) == base",
     "inside = os.path.commonprefix([json_target, base]) == base"),
    ("S58", "os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK,\n                0o644,",
     "os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK,\n                0o600,"),
    ("S63", "json_target = None\n    if args.json:",
     "json_target = None\n    if args.json is not None:"),
    ("S73", 'ap.add_argument("--timeout", type=int, default=20)',
     'ap.add_argument("--timeout", type=float, default=20)'),
)
EQUIV = (
    ("B3", "os.set_blocking(fd, True)\n        chunks = []", "chunks = []"),
    ("B4", "os.set_blocking(fd, True)\n        return fd", "return fd"),
    ("E5", "for base in measured:", "for base in [root_real]:"),
    ("E7", "measured.append(gitdir)", "pass"),
    ("E9", "measured.append(resolved)", "pass"),
    ("H4", 'ap.add_argument("--json")', 'ap.add_argument("--json", default="")'),
)
SNIFF = (
    "import sys\n"
    "tool = open(sys.argv[sys.argv.index('--tool') + 1], 'rb').read().decode('utf-8', 'replace')\n"
    "olds = %r\n"
    "n = 0\n"
    "for i, old in enumerate(olds):\n"
    "    ok = old in tool\n"
    "    print('case-sniff-%%d=%%s' %% (i, 'PASS' if ok else 'FAIL'))\n"
    "    n += 0 if ok else 1\n"
    "print('SUMMARY cases=%%d pass=%%d fail=%%d' %% (len(olds), len(olds) - n, n))\n"
    "sys.exit(1 if n else 0)\n"
) % (tuple(m[1] for m in MUTANTS),)
WRAPPER = (
    "import os, sys\n"
    "args = sys.argv[1:]\n"
    "with open(os.environ['SHIM_LOG'], 'a') as fh:\n"
    "    fh.write('invoke %%s\\n' %% ' '.join(args))\n"
    "os.execv(sys.executable, [sys.executable, '-B'] + args)\n"
)


def env(scratch):
    e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": scratch}
    e.update(GIT_ENV)
    return e


def git(root, scratch, *args):
    return subprocess.run(["git", "-C", root] + list(args), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, env=env(scratch), check=False)


def show(root, rev, path, scratch):
    p = git(root, scratch, "show", "%s:%s" % (rev, path))
    return p.stdout if p.returncode == 0 else None


def kill_reading(rc, out, err, fixture_path):
    """r43 kill rule: exit 1 + SUMMARY fail>0 + no traceback framed in the fixture's own file.

    A traceback framed inside the fixture itself is a battery defect and reads
    `fixture-traceback` before the SUMMARY check, so a fixture that crashes without a SUMMARY is
    never scored as a kill and never silently as `no-summary`.
    """
    if rc != 1:
        return "no-rc"
    for frame in TRACEBACK_FILE.findall(err.decode("utf-8", "replace")):
        try:
            same = os.path.realpath(frame) == os.path.realpath(fixture_path)
        except OSError:
            same = frame == fixture_path
        if same:
            return "fixture-traceback"
    m = SUMMARY_RE.search(out.decode("utf-8", "replace"))
    if not m or int(m.group(3)) <= 0:
        return "no-summary"
    return "KILL"


def write_fixture(dirpath, fixture_bytes):
    os.makedirs(dirpath, exist_ok=True)
    fx = os.path.join(dirpath, "_fixture.py")
    with open(fx, "wb") as fh:
        fh.write(fixture_bytes)
    return fx


def run_fixture(fixture_bytes, tool_path, workdir, scratch, timeout=300):
    fx = write_fixture(workdir, fixture_bytes)
    t0 = time.monotonic()
    try:
        p = subprocess.run(["python3", "-B", fx, "--tool", tool_path, "--work", workdir],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           cwd=scratch, env=env(scratch), timeout=timeout)
        return p, time.monotonic() - t0, False, fx
    except subprocess.TimeoutExpired:
        return None, time.monotonic() - t0, True, fx


def parse_population(blob, tool_text):
    ids = {}
    for line in blob.decode("utf-8", "replace").splitlines():
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) != 5:
            return False, ["row-cols %r" % cols[:1]]
        ids[cols[0]] = (cols[1], cols[2], cols[3])
    want = {mid: (hashlib.sha256(o.encode()).hexdigest(), hashlib.sha256(n.encode()).hexdigest())
            for mid, o, n in MUTANTS}
    if set(ids) != set(want):
        return False, ["id-set %s" % sorted(set(ids) ^ set(want))[:4]]
    for mid, (osh, nsh) in want.items():
        if ids[mid][0] != osh or ids[mid][1] != nsh:
            return False, ["anchor-sha %s" % mid]
    for _, o, _n in MUTANTS + EQUIV:
        if tool_text.count(o) != 1:
            return False, ["anchor-once"]
    return True, []


def direct_n10_probe(tool_path, work, scratch):
    os.makedirs(work + "/root/r", exist_ok=True)
    rec = os.path.join(work, "rec")
    outside = os.path.join(work, "outside")
    os.makedirs(outside, exist_ok=True)
    with open(rec, "w") as fh:
        fh.write("REPO\tr\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n")
    target = os.path.join(outside, "victim.json")
    with open(target, "w") as fh:
        fh.write("{}")
    link = os.path.join(work, "out.json")
    if not os.path.islink(link):
        os.symlink(target, link)
    try:
        p = subprocess.run(["python3", "-B", tool_path, "--root", os.path.join(work, "root"),
                            "--record", rec, "--json", link, "--skip-unrecorded"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           cwd=work, env=env(scratch), timeout=60)
    except subprocess.TimeoutExpired:
        return "timeout"
    err = p.stderr.decode("utf-8", "replace")
    if "REFUSAL JSON-TARGET-SYMLINK:" in err and p.returncode == 2:
        return "ok"
    return "no-refusal rc=%d" % p.returncode


def stderr_discrimination_selftest():
    tmp = tempfile.mkdtemp(prefix="r43c3disc-")
    fx = os.path.join(tmp, "fixture.py")
    tool = os.path.join(tmp, "tool.py")
    try:
        with open(fx, "w") as fh:
            fh.write("import subprocess, sys\n"
                     "p = subprocess.run([sys.executable, '-B', sys.argv[1]],\n"
                     "                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)\n"
                     "sys.stderr.write(p.stdout.decode())\n"
                     "print('SUMMARY cases=1 pass=0 fail=1')\n"
                     "sys.exit(1)\n")
        with open(tool, "w") as fh:
            fh.write("raise ValueError('tool crash')\n")
        p = subprocess.run([sys.executable, "-B", fx, tool], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=60)
        fwd = kill_reading(p.returncode, p.stdout, p.stderr, fx)
        with open(fx, "w") as fh:
            fh.write("raise ValueError('fixture crash')\n")
        p = subprocess.run([sys.executable, "-B", fx, tool], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=60)
        own = kill_reading(p.returncode, p.stdout, p.stderr, fx)
        return fwd == "KILL" and own == "fixture-traceback"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--scratch", required=True)
    ns = ap.parse_args(argv)
    root, rev, scratch = os.path.abspath(ns.root), ns.rev, os.path.abspath(ns.scratch)
    if not REV_RE.match(rev) or git(root, scratch, "cat-file", "-e", rev + "^{commit}").returncode != 0:
        sys.stderr.write("REFUSAL REV-UNRESOLVED: %s\n" % rev)
        return 2
    if os.getuid() == 0:
        sys.stderr.write("REFUSAL UID0\n")
        return 2
    os.makedirs(scratch, exist_ok=True)
    tool_bytes = show(root, rev, TOOL, scratch)
    fixture_bytes = show(root, rev, FIXTURE, scratch)
    pop_bytes = show(root, rev, POPULATION, scratch)
    if tool_bytes is None or pop_bytes is None:
        sys.stderr.write("REFUSAL MISSING-INPUT tool=%s population=%s\n"
                         % (tool_bytes is not None, pop_bytes is not None))
        return 2
    tool_text = tool_bytes.decode("utf-8")
    tool_sha = hashlib.sha256(tool_bytes).hexdigest()
    pinned = tool_sha == BASE_TOOL_SHA256
    pop_ok, problems = parse_population(pop_bytes, tool_text)
    if not pop_ok:
        sys.stderr.write("REFUSAL ANCHORS: %s\n" % ";".join(problems))
        return 2
    work = tempfile.mkdtemp(prefix="r43c3-", dir=scratch)
    tool_rev = os.path.join(work, "tool_rev.py")
    with open(tool_rev, "wb") as fh:
        fh.write(tool_bytes)

    def mutated(mid, old, new):
        path = os.path.join(work, "mut_%s.py" % mid)
        with open(path, "w") as fh:
            fh.write(tool_text.replace(old, new))
        return path

    def score_pair(fixture_b, arg):
        mid, old, new = arg
        mp = mutated(mid, old, new)
        p, _t, to, fx = run_fixture(fixture_b, mp, "%s/%s" % (work, mid), scratch)
        if to or p is None:
            return mid, "timed-out"
        return mid, kill_reading(p.returncode, p.stdout, p.stderr, fx)

    # ---- n10_before (only meaningful at a rev whose tool is still the pinned bytes) ----
    n10_before = "base-receipt" if not pinned else "no-fixture"
    if pinned and fixture_bytes is not None:
        p, _t, to, _fx = run_fixture(fixture_bytes, tool_rev, work + "/nb", scratch)
        if to or p is None:
            n10_before = "run-error"
        else:
            fails = sorted(l.split("=")[0].strip() for l in p.stdout.decode("utf-8", "replace").splitlines() if "=FAIL" in l)
            n10_before = "ok" if fails == [N10_CASE] else "wrong-fails"

    killed = crashed = timed_out = equiv_killed = old_killed = sniff_eq = 0
    prior_clean = 0
    cases = passed = failed = 0
    fail_names = []
    shim_invocations = -1
    if fixture_bytes is None:
        pass
    else:
        p, _t, to, _fx = run_fixture(fixture_bytes, tool_rev, work + "/pc", scratch)
        if to or p is None:
            timed_out += 1
        else:
            m = SUMMARY_RE.search(p.stdout.decode("utf-8", "replace"))
            txt = p.stdout.decode("utf-8", "replace")
            if m:
                cases, passed, failed = int(m.group(1)), int(m.group(2)), int(m.group(3))
                fail_names = sorted(l.split("=")[0].strip() for l in txt.splitlines() if "=FAIL" in l)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            results = list(ex.map(lambda a: score_pair(fixture_bytes, a), MUTANTS))
        killed = sum(1 for _m, r in results if r == "KILL")
        crashed = sum(1 for _m, r in results if r == "fixture-traceback")
        timed_out += sum(1 for _m, r in results if r == "timed-out")
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            eresults = list(ex.map(lambda a: score_pair(fixture_bytes, a), EQUIV))
        equiv_killed = sum(1 for _m, r in eresults if r == "KILL")
        # prior fixtures on the rev tool + old_killed over the 8 pre-r42 fixtures
        for fx_path in PRIOR:
            fxb = show(root, rev, fx_path, scratch)
            if fxb is None:
                continue
            tag = os.path.basename(fx_path)[:-3]
            p, _t, to, _fx = run_fixture(fxb, tool_rev, "%s/prior_%s" % (work, tag), scratch)
            if not to and p is not None and p.returncode == 0:
                prior_clean += 1
            if fx_path == FIXTURE:
                continue

            def oldscore(arg, fxb=fxb, tag=tag):
                mid, old, new = arg
                mp = mutated(mid, old, new)
                q, _t, to2, fx2 = run_fixture(fxb, mp, "%s/old_%s_%s" % (work, tag, mid), scratch)
                if to2 or q is None:
                    return "timed-out"
                return kill_reading(q.returncode, q.stdout, q.stderr, fx2)

            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
                oresults = list(ex.map(oldscore, MUTANTS))
            old_killed += sum(1 for r in oresults if r == "KILL")
        # sniff control over EQUIV
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
            sres = list(ex.map(lambda a: score_pair(SNIFF.encode(), a), EQUIV))
        sniff_eq = sum(1 for _m, r in sres if r == "KILL")
        # execution-count shim over the fixture's passing cases
        shim_path = os.path.join(work, "shim_wrapper.py")
        with open(shim_path, "w") as fh:
            fh.write(WRAPPER)
        shim_dir = os.path.join(work, "shim")
        fx2 = write_fixture(shim_dir, fixture_bytes)
        e2 = env(shim_dir)
        e2["SHIM_LOG"] = os.path.join(shim_dir, "shim.log")
        try:
            subprocess.run(["python3", "-B", fx2, "--tool", shim_path, "--work", shim_dir],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           cwd=scratch, env=e2, timeout=600)
            with open(e2["SHIM_LOG"]) as fh:
                shim_invocations = sum(1 for _ in fh)
        except (subprocess.TimeoutExpired, OSError):
            shim_invocations = 0
    shim_ok = shim_invocations >= passed and passed > 0
    stderr_disc = stderr_discrimination_selftest()
    n10_after = direct_n10_probe(tool_rev, work + "/n10", scratch)
    try:
        with open("/proc/loadavg") as fh:
            load1 = fh.read().split()[0]
    except OSError:
        load1 = "?"
    target = (killed == len(MUTANTS) and equiv_killed == 0 and old_killed == 0
              and prior_clean == len(PRIOR) and failed == 0 and cases >= 17 and timed_out == 0
              and crashed == 0 and n10_after == "ok" and sniff_eq >= 1 and shim_ok and stderr_disc)
    print("SUMMARY mutants=%d killed=%d survived=%d crashed=%d timed_out=%d equiv=%d equiv_killed=%d "
          "old_killed=%d prior=%d/%d cases=%d pass=%d fail=%d fails=%s n10_before=%s n10_after=%s "
          "sniff_eq_killed=%d shim=%s stderr_discrimination=%s anchors=%s population=%s tool_sha=%s load=%s"
          % (len(MUTANTS), killed, len(MUTANTS) - killed, crashed, timed_out, len(EQUIV), equiv_killed,
             old_killed, prior_clean, len(PRIOR), cases, passed, failed,
             ",".join(fail_names) or "-", n10_before, n10_after, sniff_eq,
             "ok" if shim_ok else "FAIL invocations=%d" % shim_invocations,
             "ok" if stderr_disc else "FAIL", "ok" if pop_ok else "bad",
             "ok" if pop_ok else "bad", tool_sha[:12], load1))
    shutil.rmtree(work, ignore_errors=True)
    return 0 if target else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
