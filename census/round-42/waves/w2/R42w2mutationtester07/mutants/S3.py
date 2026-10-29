#!/usr/bin/env python3
"""census/round-42/c2-counter.py — r42 C2 (operability): the freeze check, hardened and self-testing.

Claim. r41's `tools/souji-freeze-check.py` makes the "freeze before data" rule one command, but its
r41 wave-2 attacks (lesson N13) and the r41 closure (R41-D-C2-SELFTEST) left four holes and no
self-invocation mode. The r42 candidate TOOL speaks the r41 protocol (below, unchanged) plus:

  python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40
  stdout  `FINDING <claim> <CLASS> <detail>` per finding, sorted, then `SUMMARY claims=<n> findings=<m>`;
          exit 0 findings=0, 1 findings, 2 could-not-evaluate (`REFUSAL COULD-NOT-EVALUATE: ...`)
  python3 -B tools/souji-freeze-check.py --selftest
          builds its own synthetic repositories (under $TMPDIR), runs its own checks and prints
          `SELFTEST cases=<n> pass=<p> fail=<f>`; exit 0 iff fail=0 (n >= 12)

r41 grammar and classes are unchanged (NO-CLAIMS, FIELD-MISSING, FIELD-EMPTY, BASE-UNRESOLVED,
BASE-NOT-ANCESTOR, COUNTER-/POPULATION-MISSING/-DIGEST, POPULATION-EMPTY, CONTROL-MISSING,
CONTROL-NOT-RED, FROZEN-EDITED, DISPATCH-BEFORE-FREEZE; claim label of a prereg-wide finding is C0).
New in r42 (exactly these):

  KEY-DUPLICATE        a key line appears more than once in one claim block (identical value or not);
                       one finding per duplicated key (detail: the key). First-wins reading is gone.
  HEADING-MALFORMED    a line at column 0 that starts `##` (and not `###`), then optional spaces, then
                       `C` or `c`, optional spaces, a digit, and does not match `## C<digits>` followed by
                       a space or end of line (`##C1`, `## c1`, `## C 1`, `## C1x`). Claim label C0,
                       one finding per such line (detail: line=<n>); the line opens no claim.
  COUNTER-SYMLINK      the Counter path is a symlink (git mode 120000) at FREEZE-REV: this finding alone,
                       no digest comparison is made (the link text is not the counter)
  POPULATION-SYMLINK   the same for the Population path
  DISPATCH-BEFORE-FREEZE now covers every file under `.ufo/waves/round-<N>/` (any depth) whose basename
                       contains `-dispatch` or `.ready`, or ends `-spec.json` or `-results.json`, and was
                       first added by FREEZE-REV or an ancestor of it (`w1-dispatch-attempts.txt`,
                       `w1.ready.dispatched`, `w1-spec.json`, `w1-results.json` read red; `notes.md` clean)

The counter never trusts the tool. It builds synthetic git repositories under the scratch root (every
git call names `-C <dir>`; the author identity is passed through the environment), runs the candidate
over each, and requires the exact (exit code, finding class multiset) the case declares (37 cases:
the 21 r41 cases plus 16 new). Two built-in stubs must be REJECTED by the same cases (`control_clean`
always prints `SUMMARY claims=1 findings=0`, `control_findings` always prints one NO-CLAIMS finding).

Legs over the lane's committed bytes at --rev:
  real         the tool over `census/round-42/preregistration.txt`: exit 0, findings=0, claims=3
  retro        the tool over `census/round-40/preregistration.txt` (pre-grammar): exit 1, >= 3 findings
  retro_clean  the tool over `census/round-41/preregistration.txt` (written to the r41 grammar):
               exit 0, findings=0, claims=3 (the hardened tool must not turn real bytes red)
  selftest     `--selftest` exits 0 and prints `SELFTEST cases=<n> pass=<n> fail=0` with n >= 12
  patches      `--selftest` run with one of three runtime patches injected through a sitecustomize on
               PYTHONPATH (P1 sha256 digests reversed, P2 `git log --diff-filter` returns nothing,
               P3 `git merge-base` always fails) must exit non-zero under each (3/3): a self-test
               that does not exercise the tool's own digest, freeze-detection and ancestry logic
               passes under a patch and is rejected

CLI:
  python3 -B census/round-42/c2-counter.py --root LANE --rev FULL40 [--tool PATH-IN-REV] [--scratch DIR]
Exit: 0 target met; 1 target unmet (absent tool included); 2 could-not-evaluate.
Target: `SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red
retro_clean=ok selftest=ok patches=3/3`.
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
TOOL_PATH = "tools/souji-freeze-check.py"
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0",
           "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
           "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}
STUB_CLEAN = ("import sys\nprint('SUMMARY claims=1 findings=0')\nsys.exit(0)\n")
STUB_FINDINGS = ("import sys\nprint('FINDING C1 NO-CLAIMS x')\nprint('SUMMARY claims=0 findings=1')\n"
                 "sys.exit(1)\n")
PREREG_PATH = "census/round-42/preregistration.txt"
RETRO_PATH = "census/round-40/preregistration.txt"
CLEAN_RETRO_PATH = "census/round-41/preregistration.txt"


def env(scratch):
    e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": scratch}
    e.update(GIT_ENV)
    return e


def git(d, scratch, *args, check=True):
    p = subprocess.run(["git", "-C", d] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=env(scratch), check=False, text=True)
    if check and p.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), p.stderr))
    return p.stdout.strip()


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


COUNTER = "# counter\nprint('counter')\n"
POPULATION = "id\tname\n1\talpha\n2\tbeta\n"
CONTROL_RED = "SUMMARY items=2 corrected=0\nEXIT=1\n"
CONTROL_GREEN = "SUMMARY items=2 corrected=2\nEXIT=0\n"


def prereg_text(claims, round_no="42"):
    out = ["# prereg", "Round: %s" % round_no, ""]
    for n, c in enumerate(claims, 1):
        out.append("## C%d — claim %d" % (n, n))
        for key in ("Base", "Counter", "Population", "Control", "Target", "Kill"):
            if key in c and c[key] is not None:
                out.append("%s: %s" % (key, c[key]))
        for key, value in c.get("__extra", []):
            out.append("%s: %s" % (key, value))
        out.append("")
    return "\n".join(out) + "\n"


def build(scratch, name, mut=None):
    """Build one synthetic repo. Returns (dir, tip, prereg-relative-path, expected-classes)."""
    mut = mut or {}
    d = os.path.join(scratch, name)
    os.makedirs(d)
    git(d, scratch, "init", "-q", "-b", "main", d)
    if os.path.realpath(git(d, scratch, "rev-parse", "--show-toplevel")) != os.path.realpath(d):
        raise RuntimeError("fixture repo root mismatch")

    def write(rel, text):
        full = os.path.join(d, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def commit(msg):
        git(d, scratch, "add", "-A")
        git(d, scratch, "commit", "-qm", msg)
        return git(d, scratch, "rev-parse", "HEAD")

    write("README", "base\n")
    base = commit("base")
    if mut.get("base_side"):
        git(d, scratch, "checkout", "-q", "-b", "side")
        write("side.txt", "side\n")
        side = commit("side")
        git(d, scratch, "checkout", "-q", "main")
    if mut.get("dispatch_before"):
        write(".ufo/waves/round-42/w1-dispatch.json", "{}\n")
        commit("early dispatch")
    if mut.get("before_files"):
        for rel in mut["before_files"]:
            write(".ufo/waves/round-42/" + rel, "x\n")
        commit("early wave files")
    counter, population, control = COUNTER, POPULATION, mut.get("control", CONTROL_RED)
    if "population" in mut:
        population = mut["population"]
    claim = {"Base": base, "Counter": "census/c1.py sha256=%s" % sha(counter),
             "Population": "census/pop.tsv sha256=%s" % sha(population),
             "Control": "census/control.txt", "Target": "items=2 corrected=2", "Kill": "any uncorrected"}
    if mut.get("base_side"):
        claim["Base"] = side
    if mut.get("base_unresolved"):
        claim["Base"] = "0" * 40
    if "drop" in mut:
        claim.pop(mut["drop"])
    if "blank" in mut:
        claim[mut["blank"]] = ""
    if mut.get("counter_digest"):
        claim["Counter"] = "census/c1.py sha256=%s" % ("0" * 64)
    if mut.get("population_digest"):
        claim["Population"] = "census/pop.tsv sha256=%s" % ("1" * 64)
    if mut.get("dup"):
        key, value = mut["dup"]
        claim["__extra"] = [(key, claim["Counter"] if value == "CLAIMCOUNTER" else value)]
    claims = [claim]
    if mut.get("two_claims"):
        bad = dict(claim)
        bad.pop("Kill")
        claims = [claim, bad]
    if mut.get("counter_symlink"):
        write("census/real-c1.py", counter)
        os.symlink("real-c1.py", os.path.join(d, "census/c1.py"))
    elif not mut.get("counter_missing"):
        write("census/c1.py", counter)
    if mut.get("population_symlink"):
        write("census/real-pop.tsv", population)
        os.symlink("real-pop.tsv", os.path.join(d, "census/pop.tsv"))
    elif not mut.get("population_missing"):
        write("census/pop.tsv", population)
    if not mut.get("control_missing"):
        write("census/control.txt", control)
    if mut.get("no_claims"):
        write("prereg.txt", "# prereg\nRound: 42\nno claims here\n")
    else:
        write("prereg.txt", prereg_text(claims) + mut.get("tail", ""))
    freeze = commit("freeze")
    if mut.get("dispatch_after"):
        write(".ufo/waves/round-42/w1-dispatch.json", "{}\n")
        commit("dispatch after freeze")
    if mut.get("after_files"):
        for rel in mut["after_files"]:
            write(".ufo/waves/round-42/" + rel, "x\n")
        commit("wave files after freeze")
    if mut.get("edit_counter"):
        write("census/c1.py", counter + "# edited after freeze\n")
        commit("edit counter")
    if mut.get("edit_population"):
        write("census/pop.tsv", population + "3\tgamma\n")
        commit("edit population")
    return d, git(d, scratch, "rev-parse", "HEAD"), "prereg.txt", freeze


# (case name, mutation, expected exit, expected multiset of (claim, class)); None expected = skip classes
CASES = (
    ("clean", {}, 0, []),
    ("clean-dispatch-after", {"dispatch_after": True}, 0, []),
    ("no-claims", {"no_claims": True}, 1, [("C0", "NO-CLAIMS")]),
    ("field-missing-base", {"drop": "Base"}, 1, [("C1", "FIELD-MISSING")]),
    ("field-missing-counter", {"drop": "Counter"}, 1, [("C1", "FIELD-MISSING")]),
    ("field-empty-target", {"blank": "Target"}, 1, [("C1", "FIELD-EMPTY")]),
    ("base-unresolved", {"base_unresolved": True}, 1, [("C1", "BASE-UNRESOLVED")]),
    ("base-not-ancestor", {"base_side": True}, 1, [("C1", "BASE-NOT-ANCESTOR")]),
    ("counter-missing", {"counter_missing": True}, 1, [("C1", "COUNTER-MISSING")]),
    ("counter-digest", {"counter_digest": True}, 1, [("C1", "COUNTER-DIGEST")]),
    ("population-missing", {"population_missing": True}, 1, [("C1", "POPULATION-MISSING")]),
    ("population-digest", {"population_digest": True}, 1, [("C1", "POPULATION-DIGEST")]),
    ("population-empty", {"population": "id\tname\n"}, 1, [("C1", "POPULATION-EMPTY")]),
    ("control-missing", {"control_missing": True}, 1, [("C1", "CONTROL-MISSING")]),
    ("control-not-red", {"control": CONTROL_GREEN}, 1, [("C1", "CONTROL-NOT-RED")]),
    ("frozen-edited-counter", {"edit_counter": True}, 1, [("C1", "FROZEN-EDITED")]),
    ("frozen-edited-population", {"edit_population": True}, 1, [("C1", "FROZEN-EDITED")]),
    ("dispatch-before-freeze", {"dispatch_before": True}, 1, [("C0", "DISPATCH-BEFORE-FREEZE")]),
    ("two-claims-one-bad", {"two_claims": True}, 1, [("C2", "FIELD-MISSING")]),
    # --- r42 additions (16)
    ("dup-base-differs", {"dup": ("Base", "0" * 40)}, 1, [("C1", "KEY-DUPLICATE")]),
    ("dup-counter-identical", {"dup": ("Counter", "CLAIMCOUNTER")}, 1, [("C1", "KEY-DUPLICATE")]),
    ("dup-target", {"dup": ("Target", "something else")}, 1, [("C1", "KEY-DUPLICATE")]),
    ("heading-nospace", {"tail": "##C2 - second\n"}, 1, [("C0", "HEADING-MALFORMED")]),
    ("heading-lowercase", {"tail": "## c2 - second\n"}, 1, [("C0", "HEADING-MALFORMED")]),
    ("heading-spaced-digit", {"tail": "## C 2 - second\n"}, 1, [("C0", "HEADING-MALFORMED")]),
    ("heading-suffix", {"tail": "## C2x second\n"}, 1, [("C0", "HEADING-MALFORMED")]),
    ("heading-valid-tail", {"tail": "## C2 - empty second claim\n"}, 1,
     [("C2", "FIELD-MISSING")] * 6),
    ("dispatch-spec-before", {"before_files": ["w1-spec.json"]}, 1, [("C0", "DISPATCH-BEFORE-FREEZE")]),
    ("dispatch-attempts-before", {"before_files": ["w1-dispatch-attempts.txt"]}, 1,
     [("C0", "DISPATCH-BEFORE-FREEZE")]),
    ("dispatch-dispatched-before", {"before_files": ["w1.ready.dispatched"]}, 1,
     [("C0", "DISPATCH-BEFORE-FREEZE")]),
    ("dispatch-results-before", {"before_files": ["w1-results.json"]}, 1,
     [("C0", "DISPATCH-BEFORE-FREEZE")]),
    ("dispatch-names-after", {"after_files": ["w1-spec.json", "w1-dispatch-attempts.txt",
                                              "w1.ready.dispatched", "w1-results.json"]}, 0, []),
    ("dispatch-notes-before", {"before_files": ["notes.md", "w1/Seat01.md"]}, 0, []),
    ("counter-symlink", {"counter_symlink": True}, 1, [("C1", "COUNTER-SYMLINK")]),
    ("population-symlink", {"population_symlink": True}, 1, [("C1", "POPULATION-SYMLINK")]),
)


def run_tool(tool, d, rev, prereg, scratch):
    p = subprocess.run(["python3", "-B", tool, "--root", d, "--prereg", prereg, "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
                       env=env(scratch), timeout=300)
    findings = sorted((m.group(1), m.group(2)) for m in
                      re.finditer(r"^FINDING (\S+) (\S+)", p.stdout, re.M))
    summ = re.findall(r"^SUMMARY claims=(\d+) findings=(\d+)\s*$", p.stdout, re.M)
    crash = "Traceback (most recent call last)" in p.stderr
    return p.returncode, findings, (tuple(int(x) for x in summ[-1]) if summ else None), crash, p.stderr


def case_ok(tool, scratch, name, mut, want_rc, want):
    d, tip, prereg, _freeze = build(scratch, name, mut)
    rc, findings, summ, crash, _err = run_tool(tool, d, tip, prereg, scratch)
    got = sorted(findings)
    ok = (not crash and summ is not None)
    return ok, "rc=%d want=%d findings=%r want=%r summary=%r crash=%s" % (rc, want_rc, got, sorted(want), summ, crash)


def two_unresolved(tool, scratch, label):
    d, tip, prereg, _ = build(scratch, "%s-unres" % label, {})
    r1 = run_tool(tool, d, "f" * 40, prereg, scratch)
    r2 = run_tool(tool, d, tip, "absent.txt", scratch)
    return [r1[0] == 2 and "COULD-NOT-EVALUATE" in r1[4] and not r1[3],
            r2[0] == 2 and "COULD-NOT-EVALUATE" in r2[4] and not r2[3]]


def score_tool(tool, scratch, label, verbose=True):
    results = []
    for name, mut, rc, want in CASES:
        ok, detail = case_ok(tool, scratch, "%s-%s" % (label, name), mut, rc, want)
        results.append((name, ok, detail))
    for name, ok in zip(("unresolved-rev", "absent-prereg"), two_unresolved(tool, scratch, label)):
        results.append((name, ok, "rc/refusal check"))
    if verbose:
        for name, ok, detail in results:
            print("case-%s=%s%s" % (name, "PASS" if ok else "FAIL", "" if ok else " " + detail[:240]))
    return sum(1 for _n, ok, _d in results if ok), len(results)


SITECUSTOMIZE = (
    "import os, sys\n"
    "_p = os.environ.get('SOUJI_R42_PATCH', '')\n"
    "if _p == 'P1':\n"
    "    import hashlib\n"
    "    _orig = hashlib.sha256\n"
    "    class _Rev(object):\n"
    "        def __init__(self, *a, **k):\n"
    "            self._h = _orig(*a, **k)\n"
    "        def update(self, b):\n"
    "            self._h.update(b)\n"
    "        def hexdigest(self):\n"
    "            return self._h.hexdigest()[::-1]\n"
    "        def digest(self):\n"
    "            return self._h.digest()[::-1]\n"
    "    hashlib.sha256 = _Rev\n"
    "elif _p in ('P2', 'P3'):\n"
    "    import subprocess\n"
    "    _run = subprocess.run\n"
    "    def _patched(args, *a, **k):\n"
    "        try:\n"
    "            argv = [str(x) for x in args]\n"
    "        except TypeError:\n"
    "            argv = []\n"
    "        if _p == 'P2' and argv[:1] == ['git'] and '--diff-filter=A' in argv:\n"
    "            return subprocess.CompletedProcess(args, 0, b'', b'')\n"
    "        if _p == 'P3' and argv[:1] == ['git'] and 'merge-base' in argv:\n"
    "            return subprocess.CompletedProcess(args, 1, b'', b'')\n"
    "        return _run(args, *a, **k)\n"
    "    subprocess.run = _patched\n"
)
SELFTEST_RE = re.compile(r"^SELFTEST cases=(\d+) pass=(\d+) fail=(\d+)\s*$", re.M)


def run_selftest(tool, scratch, patch=None):
    e = env(scratch)
    if patch:
        pdir = os.path.join(scratch, "patch-" + patch)
        os.makedirs(pdir, exist_ok=True)
        with open(os.path.join(pdir, "sitecustomize.py"), "w", encoding="utf-8") as handle:
            handle.write(SITECUSTOMIZE)
        e["PYTHONPATH"] = pdir
        e["SOUJI_R42_PATCH"] = patch
    work = tempfile.mkdtemp(prefix="st.", dir=scratch)
    e["TMPDIR"] = work
    try:
        p = subprocess.run(["python3", "-B", tool, "--selftest"], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, check=False, env=e, timeout=300)
    except subprocess.TimeoutExpired:
        return 124, None, True
    finally:
        shutil.rmtree(work, ignore_errors=True)
    m = SELFTEST_RE.findall(p.stdout)
    crash = "Traceback (most recent call last)" in p.stderr
    return p.returncode, (tuple(int(x) for x in m[-1]) if m else None), crash


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--tool", default=TOOL_PATH)
    ap.add_argument("--scratch")
    args = ap.parse_args(argv)
    scratch_root = args.scratch or os.environ.get("TMPDIR")
    if not scratch_root or not os.path.isdir(scratch_root):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --scratch (or TMPDIR) must name a directory\n")
        return 2
    if not REV.match(args.rev) or subprocess.run(
            ["git", "-C", args.root, "cat-file", "-e", args.rev + "^{commit}"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env(scratch_root),
            check=False).returncode != 0:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --rev must name a resolvable full40 commit\n")
        return 2
    scratch = tempfile.mkdtemp(prefix="souji-r42-c2.", dir=scratch_root)
    try:
        blob = subprocess.run(["git", "-C", args.root, "show", "%s:%s" % (args.rev, args.tool)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env(scratch_root),
                              check=False)
        total = len(CASES) + 2
        if blob.returncode != 0:
            print("PRISTINE FAIL TOOL-ABSENT %s at %s" % (args.tool, args.rev))
            print("SUMMARY cases=%d pass=0 fail=%d control_clean=n/a control_findings=n/a real=FAIL "
                  "retro=FAIL retro_clean=FAIL selftest=FAIL patches=0/3 tool_sha=absent" % (total, total))
            return 1
        tool = os.path.join(scratch, "tool.py")
        with open(tool, "wb") as handle:
            handle.write(blob.stdout)
        passed, n = score_tool(tool, scratch, "cand")
        stubs = {}
        for label, src in (("control_clean", STUB_CLEAN), ("control_findings", STUB_FINDINGS)):
            path = os.path.join(scratch, label + ".py")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(src)
            sp, sn = score_tool(path, scratch, label, verbose=False)
            stubs[label] = "REJECTED" if sp < sn else "ACCEPTED"
        # real legs over the lane's own committed bytes
        real = retro = "FAIL"
        r_rc, r_find, r_summ, r_crash, _e = run_tool(tool, args.root, args.rev, PREREG_PATH, scratch)
        if r_rc == 0 and not r_find and r_summ == (3, 0) and not r_crash:
            real = "ok"
        t_rc, t_find, t_summ, t_crash, _e = run_tool(tool, args.root, args.rev, RETRO_PATH, scratch)
        if t_rc == 1 and len(t_find) >= 3 and not t_crash:
            retro = "red"
        c_rc, c_find, c_summ, c_crash, _e = run_tool(tool, args.root, args.rev, CLEAN_RETRO_PATH, scratch)
        retro_clean = "ok" if (c_rc == 0 and not c_find and c_summ == (3, 0) and not c_crash) else "FAIL"
        st_rc, st_sum, st_crash = run_selftest(tool, scratch)
        selftest = "ok" if (st_rc == 0 and st_sum and st_sum[0] >= 12 and st_sum[1] == st_sum[0]
                            and st_sum[2] == 0 and not st_crash) else "FAIL"
        patches = 0
        for patch in ("P1", "P2", "P3"):
            p_rc, _ps, p_crash = run_selftest(tool, scratch, patch)
            patches += 1 if (selftest == "ok" and p_rc not in (0, 124)) else 0
        print("real %s rc=%d findings=%d summary=%r" % (real, r_rc, len(r_find), r_summ))
        print("retro %s rc=%d findings=%d summary=%r" % (retro, t_rc, len(t_find), t_summ))
        print("retro_clean %s rc=%d findings=%d summary=%r" % (retro_clean, c_rc, len(c_find), c_summ))
        print("selftest %s rc=%d summary=%r" % (selftest, st_rc, st_sum))
        print("SUMMARY cases=%d pass=%d fail=%d control_clean=%s control_findings=%s real=%s retro=%s "
              "retro_clean=%s selftest=%s patches=%d/3 tool_sha=%s" % (
                  n, passed, n - passed, stubs["control_clean"], stubs["control_findings"], real, retro,
                  retro_clean, selftest, patches, hashlib.sha256(blob.stdout).hexdigest()[:12]))
        met = (n == 37 and passed == n and stubs["control_clean"] == "REJECTED"
               and stubs["control_findings"] == "REJECTED" and real == "ok" and retro == "red"
               and retro_clean == "ok" and selftest == "ok")
        return 0 if met else 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
