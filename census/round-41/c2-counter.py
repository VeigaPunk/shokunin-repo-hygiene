#!/usr/bin/env python3
"""census/round-41/c2-counter.py — r41 C2 (operability): the pre-dispatch freeze checklist, runnable.

Claim: `tools/souji-freeze-check.py` turns the "freeze before data" rule (addendum §9; r40 M40-3,
M40-4, M40-5) from prose into one command. The candidate TOOL speaks this protocol:

  python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40
  stdout  `FINDING <claim> <CLASS> <detail>` per finding, sorted, then
          `SUMMARY claims=<n> findings=<m>`;  exit 0 findings=0, 1 findings, 2 could-not-evaluate
          (`--rev` unresolved, or PATH absent at --rev; message `REFUSAL COULD-NOT-EVALUATE: ...`)

Preregistration grammar (read from the blob at --rev). A claim block starts at a line `## C<digits>`
and runs to the next `## ` line. Inside a block, a key line is `Key: value` at column 0:

  Base: <full40>                          the revision the claim is measured against
  Counter: <repo path> sha256=<64 hex>    the frozen counter
  Population: <repo path> sha256=<64 hex> the frozen population (items, sites, mutants, ...)
  Control: <repo path>                    a committed do-nothing control receipt
  Target: <text>                          non-empty
  Kill: <text>                            non-empty

FREEZE-REV is the oldest commit reachable from --rev that adds PATH (`git log --diff-filter=A`). Finding
classes (exactly these):

  NO-CLAIMS            the prereg holds no `## C<digits>` block
  FIELD-MISSING        a key line is absent from a block         (detail: the key)
  FIELD-EMPTY          Target or Kill is present but blank       (detail: the key)
  BASE-UNRESOLVED      Base is not a full40 that resolves to a commit
  BASE-NOT-ANCESTOR    Base resolves but is not a strict ancestor of FREEZE-REV
  COUNTER-MISSING      the Counter path has no blob at FREEZE-REV
  COUNTER-DIGEST       the blob at FREEZE-REV hashes to something other than the stated sha256
  POPULATION-MISSING   the Population path has no blob at FREEZE-REV
  POPULATION-DIGEST    the blob at FREEZE-REV hashes to something other than the stated sha256
  POPULATION-EMPTY     the Population blob has fewer than 2 non-blank lines (header + one item)
  CONTROL-MISSING      the Control path has no blob at FREEZE-REV
  CONTROL-NOT-RED      the Control blob's last non-blank line is not `EXIT=<n>` with n a nonzero integer
  FROZEN-EDITED        the Counter or Population blob at --rev differs from its blob at FREEZE-REV
  DISPATCH-BEFORE-FREEZE  a `*-dispatch.json` or `*.ready` file under the prereg's own directory tree
                       `.ufo/waves/round-<N>/` (N = the digits in a `Round: <N>` line of the prereg) was first
                       added by FREEZE-REV or an ancestor of it (strict-ancestor test: the freeze must come first)

The counter never trusts the tool. It builds synthetic git repositories under the scratch root (every
git call names `-C <dir>`; the author identity is passed through the environment, never through a
config or a global), runs the candidate over each, and requires the exact (exit code, finding class
multiset) the case declares. Two built-in controls must be REJECTED by the same cases: a stub that
always prints `SUMMARY claims=1 findings=0` and exits 0 (`control_clean`), and a stub that always
prints one `FINDING C1 NO-CLAIMS x` and exits 1 (`control_findings`).

Real legs (run over the committed bytes at --rev in the lane itself):
  real   the tool over `census/round-41/preregistration.txt` at --rev: exit 0, findings=0, claims=3
  retro  the tool over `census/round-40/preregistration.txt` at --rev (written before this grammar
         existed): exit 1 with at least 3 findings; the claim label of a prereg-wide finding (NO-CLAIMS, DISPATCH-BEFORE-FREEZE) is `C0`

CLI:
  python3 -B census/round-41/c2-counter.py --root LANE --rev FULL40 [--tool PATH-IN-REV] [--scratch DIR]
Exit: 0 target met; 1 target unmet (absent tool included); 2 could-not-evaluate.
Target: `SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red`.
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
PREREG_PATH = "census/round-41/preregistration.txt"
RETRO_PATH = "census/round-40/preregistration.txt"


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


def prereg_text(claims, round_no="41"):
    out = ["# prereg", "Round: %s" % round_no, ""]
    for n, c in enumerate(claims, 1):
        out.append("## C%d — claim %d" % (n, n))
        for key in ("Base", "Counter", "Population", "Control", "Target", "Kill"):
            if key in c and c[key] is not None:
                out.append("%s: %s" % (key, c[key]))
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
        write(".ufo/waves/round-41/w1-dispatch.json", "{}\n")
        commit("early dispatch")
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
    claims = [claim]
    if mut.get("two_claims"):
        bad = dict(claim)
        bad.pop("Kill")
        claims = [claim, bad]
    if not mut.get("counter_missing"):
        write("census/c1.py", counter)
    if not mut.get("population_missing"):
        write("census/pop.tsv", population)
    if not mut.get("control_missing"):
        write("census/control.txt", control)
    if mut.get("no_claims"):
        write("prereg.txt", "# prereg\nRound: 41\nno claims here\n")
    else:
        write("prereg.txt", prereg_text(claims))
    freeze = commit("freeze")
    if mut.get("dispatch_after"):
        write(".ufo/waves/round-41/w1-dispatch.json", "{}\n")
        commit("dispatch after freeze")
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
    ok = (rc == want_rc and got == sorted(want) and not crash and summ is not None
          and summ[1] == len(want))
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
    scratch = tempfile.mkdtemp(prefix="souji-r41-c2.", dir=scratch_root)
    try:
        blob = subprocess.run(["git", "-C", args.root, "show", "%s:%s" % (args.rev, args.tool)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env(scratch_root),
                              check=False)
        total = len(CASES) + 2
        if blob.returncode != 0:
            print("PRISTINE FAIL TOOL-ABSENT %s at %s" % (args.tool, args.rev))
            print("SUMMARY cases=%d pass=0 fail=%d control_clean=n/a control_findings=n/a real=FAIL "
                  "retro=FAIL tool_sha=absent" % (total, total))
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
        print("real %s rc=%d findings=%d summary=%r" % (real, r_rc, len(r_find), r_summ))
        print("retro %s rc=%d findings=%d summary=%r" % (retro, t_rc, len(t_find), t_summ))
        print("SUMMARY cases=%d pass=%d fail=%d control_clean=%s control_findings=%s real=%s retro=%s "
              "tool_sha=%s" % (n, passed, n - passed, stubs["control_clean"], stubs["control_findings"],
                               real, retro, hashlib.sha256(blob.stdout).hexdigest()[:12]))
        met = (n == 21 and passed == n and stubs["control_clean"] == "REJECTED"
               and stubs["control_findings"] == "REJECTED" and real == "ok" and retro == "red")
        return 0 if met else 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
