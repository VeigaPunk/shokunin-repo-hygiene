#!/usr/bin/env python3
"""census/round-41/c3-counter.py — r41 C3 (coverage): refusal-site probe battery, scored by site mutation.

Claim (coverage): every refusal site of `tools/souji-worktree-drift.py` that the module
docstring's refusal classes name is reached by a runnable, class-asserting probe. The population is
frozen in `census/round-41/c3-sites.tsv` (19 sites in source order, 10 classes, 21 probe ids); its
sha256 is pinned below. The tool bytes are pinned too (`PRISTINE_SHA256`): no tool edit is part of
this claim.

The candidate is a FIXTURE (`tests/fixtures/r41-refusal-sites.py`) speaking one protocol:

  python3 -B <fixture> --tool PATH --work DIR
  stdout: one `probe-<ID>=PASS|FAIL [detail]` line per probe id, then
          `SUMMARY probes=<n> pass=<p> fail=<f>`; exit 0 iff fail=0, 1 otherwise.

The counter never trusts the fixture's PASS lines. It scores the fixture by SITE MUTATION: for each
source-order site n it rewrites that one site's class label to `ZZ-MUTANT` in the pristine tool
bytes and runs the fixture on the mutant. A site is KILLED only when the set of FAIL probe ids equals
exactly the probe ids the frozen table maps to that site (so a fixture that prints PASS without
probing, one that checks only the exit code, or one whose probe reaches a different site, leaves
the site SURVIVED or MISATTRIBUTED).

Privilege: the EACCES probes (P02a, P18) change class under a privileged runner. The counter refuses
to score as uid 0 (exit 2, could-not-evaluate); it never skips a probe.

CLI:
  python3 -B census/round-41/c3-counter.py --root LANE --rev FULL40 [--fixture PATH-IN-REV]
      [--scratch DIR] [--sites PATH-IN-REV] [--pristine-sha SHA]
  python3 -B census/round-41/c3-counter.py --selftest [--scratch DIR]

Exit: 0 target met; 1 target unmet (pristine failure, survivor, misattribution, probe-set mismatch,
absent fixture); 2 could-not-evaluate (bad rev, uid 0, scratch unavailable, pinned bytes differ).
Target: `SUMMARY sites=19 probes=21 pristine=ok killed=19 survived=0 misattributed=0 docclasses=10`.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

REV = re.compile(r"^[0-9a-f]{40}$")
TOOL_PATH = "tools/souji-worktree-drift.py"
FIXTURE_PATH = "tests/fixtures/r41-refusal-sites.py"
SITES_PATH = "census/round-41/c3-sites.tsv"
SITES_SHA256 = "be363c0de5d332dc4223bdf6ccf5f2035e6e38af9cc30735463b07b5d2e764ea"
PRISTINE_SHA256 = "b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6"
SITE_RE = re.compile(r'(?:Refusal\(\s*"|"REFUSAL )([A-Z]+(?:-[A-Z]+)*):')
DOC_CLASS_RE = re.compile(r"^  ([A-Z]+(?:-[A-Z]+)*) {2,}\S", re.M)
PROBE_RE = re.compile(r"^probe-([A-Za-z0-9]+)=(PASS|FAIL)\b", re.M)
SUMMARY_RE = re.compile(r"^SUMMARY probes=(\d+) pass=(\d+) fail=(\d+)\s*$", re.M)
GIT_ENV = {
    "LC_ALL": "C",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_TERMINAL_PROMPT": "0",
}


def child_env(scratch):
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": scratch}
    env.update(GIT_ENV)
    return env


def git_show(root, rev, path, scratch):
    proc = subprocess.run(["git", "-C", root, "show", "%s:%s" % (rev, path)],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          env=child_env(scratch), check=False)
    return proc.stdout if proc.returncode == 0 else None


def resolves(root, rev, scratch):
    return subprocess.run(["git", "-C", root, "cat-file", "-e", rev + "^{commit}"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                          env=child_env(scratch), check=False).returncode == 0


def parse_sites(text):
    sites = []
    for line in text.splitlines()[1:]:
        if line.strip():
            sid, cls, probes, _trigger = line.split("\t", 3)
            sites.append((sid, cls, tuple(probes.split(","))))
    return sites


def run_fixture(fixture, tool, scratch):
    proc = subprocess.run(["python3", "-B", fixture, "--tool", tool, "--work", scratch],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                          check=False, env=child_env(scratch), timeout=900)
    probes = {m.group(1): m.group(2) for m in PROBE_RE.finditer(proc.stdout)}
    dup = len(PROBE_RE.findall(proc.stdout)) != len(probes)
    summ = SUMMARY_RE.findall(proc.stdout)
    crash = "Traceback (most recent call last)" in proc.stderr
    return proc.returncode, probes, dup, (tuple(int(x) for x in summ[-1]) if summ else None), crash


def mutate(source, n, label):
    matches = list(SITE_RE.finditer(source))
    m = matches[n]
    return source[:m.start(1)] + "ZZ-MUTANT" + source[m.end(1):]


def score(tool_src, fixture_src, sites, scratch, label):
    """Return (lines, ok-dict). Pure over bytes so the selftest can drive it."""
    out = []
    expected_ids = sorted({p for _s, _c, ps in sites for p in ps})
    tool = os.path.join(scratch, "pristine.py")
    with open(tool, "w", encoding="utf-8") as handle:
        handle.write(tool_src)
    os.chmod(tool, 0o755)
    fixture = os.path.join(scratch, "fixture.py")
    with open(fixture, "w", encoding="utf-8") as handle:
        handle.write(fixture_src)
    found = SITE_RE.findall(tool_src)
    site_ok = [c for _s, c, _p in sites] == found
    docstring = tool_src.split('"""', 2)[1] if tool_src.count('"""') >= 2 else ""
    docclasses = sorted(set(DOC_CLASS_RE.findall(docstring)))
    frozen_classes = sorted({c for _s, c, _p in sites})
    rc, probes, dup, summ, crash = run_fixture(fixture, tool, scratch)
    pristine = (rc == 0 and not crash and not dup and summ is not None
                and sorted(probes) == expected_ids
                and all(v == "PASS" for v in probes.values())
                and summ == (len(expected_ids), len(expected_ids), 0))
    out.append("PRISTINE %s rc=%d probes=%d crash=%s dup=%s summary=%s" % (
        "ok" if pristine else "FAIL", rc, len(probes), crash, dup, summ))
    killed = survived = misattributed = 0
    if pristine and site_ok:
        for n, (sid, cls, mapped) in enumerate(sites):
            mpath = os.path.join(scratch, "mut-%s.py" % sid)
            with open(mpath, "w", encoding="utf-8") as handle:
                handle.write(mutate(tool_src, n, label))
            os.chmod(mpath, 0o755)
            mrc, mprobes, mdup, msumm, mcrash = run_fixture(fixture, mpath, scratch)
            failing = sorted(k for k, v in mprobes.items() if v == "FAIL")
            if failing == sorted(mapped) and not mcrash and not mdup and mrc == 1:
                verdict = "killed"
                killed += 1
            elif not failing:
                verdict = "survived"
                survived += 1
            else:
                verdict = "misattributed"
                misattributed += 1
            out.append("SITE %s %s %s failing=%s mapped=%s rc=%d" % (
                sid, cls, verdict, ",".join(failing) or "-", ",".join(mapped), mrc))
    else:
        survived = len(sites)
    return out, {
        "sites": len(sites), "site_regex_ok": site_ok, "probes": len(expected_ids),
        "pristine": pristine, "killed": killed, "survived": survived,
        "misattributed": misattributed, "docclasses": len(docclasses),
        "docclasses_ok": docclasses == frozen_classes,
    }


def summary_line(r, tool_sha, fixture_sha):
    return ("SUMMARY sites=%d probes=%d pristine=%s killed=%d survived=%d misattributed=%d "
            "docclasses=%d site_regex=%s docclasses_match=%s tool_sha=%s fixture_sha=%s" % (
                r["sites"], r["probes"], "ok" if r["pristine"] else "FAIL", r["killed"],
                r["survived"], r["misattributed"], r["docclasses"],
                "ok" if r["site_regex_ok"] else "FAIL", "ok" if r["docclasses_ok"] else "FAIL",
                tool_sha, fixture_sha))


def target_met(r):
    return (r["pristine"] and r["site_regex_ok"] and r["docclasses_ok"] and r["survived"] == 0
            and r["misattributed"] == 0 and r["killed"] == r["sites"] == 19 and r["probes"] == 21)


def selftest(scratch_root):
    """Three synthetic cases over a 3-site tool: perfect, stub, wrong-attribution."""
    tool = ('"""t\n\n  AAA-ONE  first\n  BBB-TWO  second\n  CCC-THREE  third\n"""\n'
            'import sys\n'
            'def main(a):\n'
            '    if a == ["1"]:\n        sys.stderr.write("REFUSAL AAA-ONE: x\\n"); return 2\n'
            '    if a == ["2"]:\n        sys.stderr.write("REFUSAL BBB-TWO: x\\n"); return 2\n'
            '    if a == ["3"]:\n        sys.stderr.write("REFUSAL CCC-THREE: x\\n"); return 2\n'
            '    return 0\n'
            'sys.exit(main(sys.argv[1:]))\n')
    sites = [("S1", "AAA-ONE", ("Pa",)), ("S2", "BBB-TWO", ("Pb",)), ("S3", "CCC-THREE", ("Pc",))]
    head = ("import argparse,subprocess,sys\nap=argparse.ArgumentParser();ap.add_argument('--tool');"
            "ap.add_argument('--work');a=ap.parse_args()\n"
            "def run(x):\n    return subprocess.run(['python3','-B',a.tool,x],capture_output=True,text=True)\n")
    good = head + (
        "res=[('Pa',run('1')),('Pb',run('2')),('Pc',run('3'))]\n"
        "want={'Pa':'AAA-ONE','Pb':'BBB-TWO','Pc':'CCC-THREE'}\n"
        "f=0\nfor k,p in res:\n"
        "    ok=p.returncode==2 and 'REFUSAL '+want[k]+':' in p.stderr\n    f+=0 if ok else 1\n"
        "    print('probe-%s=%s'%(k,'PASS' if ok else 'FAIL'))\n"
        "print('SUMMARY probes=3 pass=%d fail=%d'%(3-f,f));sys.exit(1 if f else 0)\n")
    stub = head + ("print('probe-Pa=PASS');print('probe-Pb=PASS');print('probe-Pc=PASS');"
                   "print('SUMMARY probes=3 pass=3 fail=0')\n")
    rc_only = good.replace("and 'REFUSAL '+want[k]+':' in p.stderr", "")
    cases = (("perfect", good, 3, 0, 0), ("stub", stub, 0, 3, 0), ("rc-only", rc_only, 0, 3, 0))
    failures = 0
    for name, fixture_src, want_k, want_s, want_m in cases:
        scratch = tempfile.mkdtemp(prefix="c3-selftest.", dir=scratch_root)
        try:
            _out, r = score(tool, fixture_src, sites, scratch, name)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
        ok = (r["killed"], r["survived"], r["misattributed"]) == (want_k, want_s, want_m) \
            and r["pristine"] and r["docclasses_ok"]
        print("selftest %s killed=%d survived=%d misattributed=%d %s" % (
            name, r["killed"], r["survived"], r["misattributed"], "ok" if ok else "FAIL"))
        failures += 0 if ok else 1
    print("SELFTEST cases=3 fail=%d" % failures)
    return 0 if failures == 0 else 1


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root")
    ap.add_argument("--rev")
    ap.add_argument("--fixture", default=FIXTURE_PATH)
    ap.add_argument("--sites", default=SITES_PATH)
    ap.add_argument("--pristine-sha", default=PRISTINE_SHA256)
    ap.add_argument("--scratch")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    scratch_root = args.scratch or os.environ.get("TMPDIR")
    if not scratch_root or not os.path.isdir(scratch_root):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --scratch (or TMPDIR) must name a directory\n")
        return 2
    if args.selftest:
        return selftest(scratch_root)
    if os.geteuid() == 0:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: uid 0 changes the EACCES probes' class (P02a, P18)\n")
        return 2
    if not args.root or not args.rev or not REV.match(args.rev) or not resolves(args.root, args.rev, scratch_root):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --root/--rev must name a resolvable full40 commit\n")
        return 2
    tool_b = git_show(args.root, args.rev, TOOL_PATH, scratch_root)
    sites_b = git_show(args.root, args.rev, args.sites, scratch_root)
    if tool_b is None or sites_b is None:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: tool or sites table absent at %s\n" % args.rev)
        return 2
    if hashlib.sha256(sites_b).hexdigest() != SITES_SHA256:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: sites table sha256 differs from the pinned %s\n" % SITES_SHA256)
        return 2
    tool_sha = hashlib.sha256(tool_b).hexdigest()
    if tool_sha != args.pristine_sha:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: tool sha256 %s differs from the pinned %s\n" % (tool_sha, args.pristine_sha))
        return 2
    sites = parse_sites(sites_b.decode("utf-8"))
    fixture_b = git_show(args.root, args.rev, args.fixture, scratch_root)
    scratch = tempfile.mkdtemp(prefix="souji-r41-c3.", dir=scratch_root)
    try:
        if fixture_b is None:
            print("PRISTINE FAIL FIXTURE-ABSENT %s at %s" % (args.fixture, args.rev))
            r = {"sites": len(sites), "site_regex_ok": False, "probes": 0, "pristine": False,
                 "killed": 0, "survived": len(sites), "misattributed": 0, "docclasses": 0,
                 "docclasses_ok": False}
            print(summary_line(r, tool_sha[:12], "absent"))
            return 1
        out, r = score(tool_b.decode("utf-8"), fixture_b.decode("utf-8"), sites, scratch, "c2")
        for line in out:
            print(line)
        print(summary_line(r, tool_sha[:12], hashlib.sha256(fixture_b).hexdigest()[:12]))
        return 0 if target_met(r) else 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
