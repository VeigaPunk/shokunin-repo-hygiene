#!/usr/bin/env python3
"""census/round-43/c2-counter.py — r43 C2 (operability): the freeze check closes its named holes.

Claim. Round 42's freeze check reads 37/37 but its wave-2 attacks named holes it does not close
(r42 lesson E-6, N-C2c; spotcheck section 6 item 4): a duplicated key is reported and then NEITHER
value is evaluated (first-wins lost), keys after a malformed heading are silently dropped, a
zero-padded or fullwidth `Round:` line scans a nonexistent tree and reads clean, a Control file
that is a symlink whose link text is `EXIT=1` passes the red-control read, FROZEN-EDITED covers
neither the Control file nor the preregistration itself, the selftest crashes when TMPDIR names a
missing directory, and the "hidden-case audit" stayed informational instead of becoming a frozen
leg. The r43 grammar the candidate `tools/souji-freeze-check.py` must speak (normative):

  KEY-DUPLICATE      first-wins: the first occurrence's value is evaluated; every further
                     occurrence is one KEY-DUPLICATE finding.
  UNATTACHED-KEY     (new) a key line after a malformed `##` heading and before the next valid
                     `## C<digits>` heading is reported: `FINDING C0 UNATTACHED-KEY line=<n>`;
                     it is never silently dropped and never attached to a claim.
  ROUND-MALFORMED    (new) a `Round:` line present but not strict ASCII `[1-9][0-9]*`:
                     `FINDING C0 ROUND-MALFORMED detail=<text>`; no dispatch scan runs.
  CONTROL-SYMLINK    (new) the Control path is a symlink (git mode 120000) at FREEZE: one finding,
                     and the red-control read is refused (a link text is not a control file).
  FROZEN-EDITED      extended: the Control blob and the preregistration text itself are compared
                     between FREEZE and REV; a difference is one FROZEN-EDITED finding (C0 for the
                     preregistration, C1 for the Control).
  --selftest         still exits 0 with every case passing when TMPDIR is unset or names a
                     missing directory (fallback to the system temp directory).

The counter never trusts the tool. It builds synthetic git repositories under the scratch root
(every git call names `-C`; the author identity travels through the environment), runs the
candidate over each, and requires the exact (exit code, finding-class multiset) that the frozen
table `census/round-43/c2-cases.tsv` declares. Every candidate invocation runs under a timeout; a
candidate that hangs is a refusal (CANDIDATE-TIMEOUT), never a hang. Two built-in stubs must be
REJECTED by the same table: `control_clean` (always SUMMARY findings=0, exit 0) and
`control_findings` (always one NO-CLAIMS finding, exit 1); a `memorizer` stub answers the nine
visible cases from their preregistration bytes and must FAIL the hidden audit.

Legs over the lane's committed bytes at --rev:
  newtable     the nine frozen cases on the candidate (all pass required)
  r42table     census/round-42/c2-counter.py over a clone of the lane at the r42 freeze revision
               (frozen constant R42_FREEZE) with the candidate swapped in: 37/37 and every leg the
               r42 counter declares must still read green (behaviour retention)
  hidden       census/round-43/c2-hidden-audit.py over the candidate: all held-out scenarios pass
  hidden_ctrl  the memorizer stub must FAIL the hidden audit
  real         the candidate over census/round-43/preregistration.txt: exit 0, findings=0
  selftest     --selftest exits 0 and prints SELFTEST cases=<n> pass=<n> fail=0 with n >= 31
  tmpdir       --selftest with TMPDIR naming a missing directory still exits 0

CLI:
  python3 -B census/round-43/c2-counter.py --root LANE --rev FULL40 [--scratch DIR]
Exit: 0 target met; 1 target unmet (absent tool included); 2 could-not-evaluate.
Target: `SUMMARY newtable=9/9 r42table=ok hidden=ok hidden_ctrl=REJECTED real=ok selftest=ok
tmpdir=ok control_clean=REJECTED control_findings=REJECTED`.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

REV_RE = re.compile(r"^[0-9a-f]{40}$")
TOOL_PATH = "tools/souji-freeze-check.py"
TABLE = "census/round-43/c2-cases.tsv"
HIDDEN_AUDIT = "census/round-43/c2-hidden-audit.py"
PREREG_PATH = "census/round-43/preregistration.txt"
R42_COUNTER = "census/round-42/c2-counter.py"
R42_FREEZE = "afe17f416eec04dcf3f480b580a8f928de61d19d"
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0",
           "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
           "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}
TOOL_TIMEOUT = 180
STUB_CLEAN = "import sys\nprint('SUMMARY claims=1 findings=0')\nsys.exit(0)\n"
STUB_FINDINGS = ("import sys\nprint('FINDING C1 NO-CLAIMS x')\nprint('SUMMARY claims=0 findings=1')\n"
                 "sys.exit(1)\n")
COUNTER = "# counter\nprint('counter')\n"
POPULATION = "id\tname\n1\talpha\n2\tbeta\n"
CONTROL_RED = "SUMMARY items=2 corrected=0\nEXIT=1\n"
GOOD_PREREG_CLAIM = {"Target": "items=2 corrected=2", "Kill": "any uncorrected"}


def env(scratch):
    e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": scratch}
    e.update(GIT_ENV)
    return e


def git(d, scratch, *args, check=True):
    p = subprocess.run(["git", "-C", d] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=env(scratch), check=False, text=True)
    if check and p.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), p.stderr))
    return p.stdout.strip()


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def prereg_text(round_line, claims, tail=""):
    out = ["# prereg", round_line, ""]
    for n, c in enumerate(claims, 1):
        out.append("## C%d — claim %d" % (n, n))
        for key in ("Base", "Counter", "Population", "Control", "Target", "Kill"):
            if key in c and c[key] is not None:
                out.append("%s: %s" % (key, c[key]))
        for key, value in c.get("__extra", []):
            out.append("%s: %s" % (key, value))
        out.append("")
    return "\n".join(out) + "\n" + tail


def build(scratch, name, mut=None):
    """Build one synthetic repo. Returns (dir, tip, prereg text)."""
    mut = mut or {}
    d = os.path.join(scratch, name)
    os.makedirs(d)
    git(d, scratch, "init", "-q", "-b", "main", d)
    if os.path.realpath(git(d, scratch, "rev-parse", "--show-toplevel")) != os.path.realpath(d):
        raise RuntimeError("fixture repo root mismatch")

    def write(rel, text):
        full = os.path.join(d, rel)
        os.makedirs(os.path.dirname(full) or d, exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def commit(msg):
        git(d, scratch, "add", "-A")
        git(d, scratch, "commit", "-qm", msg)
        return git(d, scratch, "rev-parse", "HEAD")

    write("README", "base\n")
    base = commit("base")
    claim = {"Base": base, "Counter": "census/c1.py sha256=%s" % sha(COUNTER),
             "Population": "census/pop.tsv sha256=%s" % sha(POPULATION),
             "Control": "census/control.txt", "Target": "items=2 corrected=2", "Kill": "any uncorrected"}
    claims = [claim]
    tail = ""
    round_line = "Round: 42"
    if mut.get("dispatch_before"):
        write(".ufo/waves/round-42/w1-dispatch.json", "{}\n")
        commit("early dispatch")
    if mut.get("dup_first_bad"):
        claim["__extra"] = [("Base", base)]
        claim["Base"] = "0" * 40
    if mut.get("dup_first_good"):
        claim["__extra"] = [("Base", "0" * 40)]
    if mut.get("heading_unattached"):
        tail = "##C2 malformed\nPopulation: census/pop.tsv sha256=%s\n" % sha(POPULATION)
    if mut.get("round_zero"):
        round_line = "Round: 042"
    if mut.get("round_fullwidth"):
        round_line = "Round: ４２"
    if mut.get("round_missing"):
        round_line = "no round line here"
    write("census/c1.py", COUNTER)
    write("census/pop.tsv", POPULATION)
    if mut.get("control_symlink"):
        os.symlink("EXIT=1", os.path.join(d, "census/control.txt"))
    else:
        write("census/control.txt", CONTROL_RED)
    ptext = prereg_text(round_line, claims, tail)
    write("prereg.txt", ptext)
    freeze = commit("freeze")
    if mut.get("edit_control"):
        write("census/control.txt", CONTROL_RED + "\n")
        commit("edit control after freeze")
    if mut.get("edit_prereg"):
        write("prereg.txt", prereg_text(round_line, claims, tail) + "# edited\n")
        commit("edit prereg after freeze")
    return d, git(d, scratch, "rev-parse", "HEAD"), ptext


CASE_BUILDERS = {
    "dup-key-first-bad": {"dup_first_bad": True},
    "dup-key-first-good": {"dup_first_good": True},
    "heading-unattached-key": {"heading_unattached": True},
    "round-zero-padded": {"round_zero": True, "dispatch_before": True},
    "round-fullwidth": {"round_fullwidth": True},
    "round-missing": {"round_missing": True},
    "control-symlink-text": {"control_symlink": True},
    "frozen-edit-control": {"edit_control": True},
    "frozen-edit-prereg": {"edit_prereg": True},
}


def run_tool(tool_path, args, cwd, scratch, timeout=TOOL_TIMEOUT):
    try:
        p = subprocess.run(["python3", "-B", tool_path] + args, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, cwd=cwd, env=env(scratch), timeout=timeout)
        return p, False
    except subprocess.TimeoutExpired:
        return None, True


def run_script(argv, cwd, scratch, timeout):
    try:
        p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           cwd=cwd, env=env(scratch), timeout=timeout)
        return p, False
    except subprocess.TimeoutExpired:
        return None, True


def findings_of(p):
    classes = []
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        f = line.split()
        if len(f) >= 3 and f[0] == "FINDING":
            classes.append("%s:%s" % (f[1], f[2]))
    return sorted(classes)


def read_table(blob):
    rows = []
    for line in blob.decode("utf-8", "replace").splitlines():
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) != 3:
            return None
        want = []
        for item in filter(None, cols[2].split(",")):
            if "*" in item:
                cls, n = item.split("*")
                want.extend([cls] * int(n))
            else:
                want.append(item)
        rows.append((cols[0], int(cols[1]), sorted(want)))
    return rows


def clone_at(root, rev, scratch, name):
    d = os.path.join(scratch, name)
    p = subprocess.run(["git", "clone", "-q", "--shared", root, d], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, env=env(scratch))
    if p.returncode != 0:
        return None
    subprocess.run(["git", "-C", d, "checkout", "-q", rev], env=env(scratch), check=False)
    return d


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--scratch", required=True)
    ns = ap.parse_args(argv)
    root, rev, scratch = os.path.abspath(ns.root), ns.rev, os.path.abspath(ns.scratch)
    if not REV_RE.match(rev) or subprocess.run(["git", "-C", root, "cat-file", "-e", rev + "^{commit}"],
                                               env=env(scratch)).returncode != 0:
        sys.stderr.write("REFUSAL REV-UNRESOLVED: %s\n" % rev)
        return 2
    if os.getuid() == 0:
        sys.stderr.write("REFUSAL UID0\n")
        return 2
    os.makedirs(scratch, exist_ok=True)
    tool_b = subprocess.run(["git", "-C", root, "show", "%s:%s" % (rev, TOOL_PATH)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env(scratch)).stdout
    table_b = subprocess.run(["git", "-C", root, "show", "%s:%s" % (rev, TABLE)],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env(scratch)).stdout
    if not tool_b or not table_b:
        sys.stderr.write("REFUSAL MISSING-INPUT tool=%s table=%s\n" % (bool(tool_b), bool(table_b)))
        return 2
    rows = read_table(table_b)
    if rows is None or not rows:
        sys.stderr.write("REFUSAL TABLE-MALFORMED\n")
        return 2
    work = tempfile.mkdtemp(prefix="r43c2-", dir=scratch)
    tool = os.path.join(work, "candidate.py")
    with open(tool, "wb") as fh:
        fh.write(tool_b)
    total = len(rows)

    def score(tool_bytes, table, label):
        tpath = os.path.join(work, "score_%s.py" % label)
        with open(tpath, "wb") as fh:
            fh.write(tool_bytes)
        passed = 0
        details = []
        answers = {}
        for cid, want_exit, want_classes in table:
            if cid not in CASE_BUILDERS:
                details.append("%s:no-builder" % cid)
                continue
            d, tip, ptext = build(work, "case_%s_%s" % (label, cid), CASE_BUILDERS[cid])
            answers[hashlib.sha256(ptext.encode("utf-8")).hexdigest()] = (
                want_exit, ["FINDING %s memorized" % c.replace(":", " ", 1) for c in want_classes])
            p, to = run_tool(tpath, ["--root", d, "--prereg", "prereg.txt", "--rev", tip], work, work)
            if to or p is None:
                details.append("%s:timeout" % cid)
                continue
            got = findings_of(p)
            if p.returncode == want_exit and got == want_classes:
                passed += 1
            else:
                details.append("%s:got rc=%d %s" % (cid, p.returncode, ",".join(got) or "-"))
        return passed, details, answers

    cand_pass, cand_details, answers = score(tool_b, rows, "cand")
    clean_b = STUB_CLEAN.encode()
    find_b = STUB_FINDINGS.encode()
    clean_pass, _cd, _ = score(clean_b, rows, "clean")
    find_pass, _fd, _ = score(find_b, rows, "find")
    # memorizer stub: answers every VISIBLE case from the frozen want, prints clean elsewhere
    mem_lines = ["import hashlib, sys", "ANSWERS = {"]
    for key, (code, lines) in sorted(answers.items()):
        mem_lines.append("    %r: (%r, %r)," % (key, code, lines))
    mem_lines += [
        "}",
        "args = sys.argv[1:]",
        "path = args[args.index('--prereg') + 1] if '--prereg' in args else (args[-1] if args else None)",
        "key = hashlib.sha256(open(path, 'rb').read()).hexdigest() if path and os.path.exists(path) else 'none'",
        "if key in ANSWERS:",
        "    code, lines = ANSWERS[key]",
        "    for l in lines:",
        "        print(l)",
        "    print('SUMMARY claims=1 findings=%d' % len(lines))",
        "    sys.exit(code)",
        "print('SUMMARY claims=1 findings=0')",
        "sys.exit(0)",
    ]
    mem_b = ("\n".join(mem_lines) + "\n").encode()
    with open(os.path.join(work, "memorizer.py"), "wb") as fh:
        fh.write(mem_b)
    # hidden audit (candidate must pass; memorizer must fail)
    hidden_b = subprocess.run(["git", "-C", root, "show", "%s:%s" % (rev, HIDDEN_AUDIT)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env(scratch)).stdout
    hidden_ok = hidden_ctrl_rejected = False
    hidden_detail = "audit-absent"
    if hidden_b:
        hap = os.path.join(work, "hidden_audit.py")
        with open(hap, "wb") as fh:
            fh.write(hidden_b)
        p1, to1 = run_script([sys.executable, "-B", hap, "--tool", tool, "--work", os.path.join(work, "h1")],
                             work, work, 900)
        p2, to2 = run_script([sys.executable, "-B", hap, "--tool", os.path.join(work, "memorizer.py"),
                              "--work", os.path.join(work, "h2")], work, work, 900)
        if not to1 and p1 is not None:
            m = re.search(r"^SUMMARY scenarios=(\d+) pass=(\d+) fail=(\d+)", p1.stdout.decode("utf-8", "replace"), re.M)
            if m and p1.returncode == 0 and int(m.group(1)) >= 8:
                hidden_ok = True
            else:
                hidden_detail = (p1.stdout.decode("utf-8", "replace") + "|" + p1.stderr.decode("utf-8", "replace"))[:300]
        if not to2 and p2 is not None and p2.returncode != 0:
            hidden_ctrl_rejected = True
    # r42 table leg
    r42_ok = False
    r42_detail = "clone-failed"
    clone = clone_at(root, R42_FREEZE, work, "r42freeze")
    if clone:
        dest = os.path.join(clone, TOOL_PATH)
        if not os.path.islink(dest):
            with open(dest, "wb") as fh:
                fh.write(tool_b)
            git(clone, work, "add", "-A")
            git(clone, work, "commit", "-qm", "candidate tool")
            ctip = git(clone, work, "rev-parse", "HEAD")
            p, to = run_script([sys.executable, "-B", os.path.join(clone, R42_COUNTER),
                                "--root", clone, "--rev", ctip,
                                "--scratch", os.path.join(work, "r42scratch")],
                               work, work, 1800)
            if not to and p is not None:
                out = p.stdout.decode("utf-8", "replace")
                r42_detail = out.strip().splitlines()[-1] if out.strip() else "empty"
                r42_ok = p.returncode == 0 and "cases=37 pass=37 fail=0" in out and "patches=3/3" in out
    # real, selftest, tmpdir legs
    prereg_b = subprocess.run(["git", "-C", root, "show", "%s:%s" % (rev, PREREG_PATH)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env(scratch)).stdout
    real_ok = False
    if prereg_b:
        p, to = run_tool(tool, ["--root", root, "--prereg", PREREG_PATH, "--rev", rev], work, work)
        real_ok = (not to) and p is not None and p.returncode == 0 and "findings=0" in p.stdout.decode("utf-8", "replace")
    st_ok = tmp_ok = False
    p, to = run_tool(tool, ["--selftest"], work, work, timeout=900)
    if not to and p is not None and p.returncode == 0:
        m = re.search(r"^SELFTEST cases=(\d+) pass=(\d+) fail=(\d+)", p.stdout.decode("utf-8", "replace"), re.M)
        st_ok = bool(m and int(m.group(1)) >= 31 and m.group(1) == m.group(2) and m.group(3) == "0")
    e2 = env(work)
    e2["TMPDIR"] = os.path.join(work, "does-not-exist")
    try:
        p = subprocess.run(["python3", "-B", tool, "--selftest"], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, cwd=work, env=e2, timeout=900)
        tmp_ok = p.returncode == 0 and "fail=0" in p.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        tmp_ok = False
    print("SUMMARY newtable=%d/%d r42table=%s hidden=%s hidden_ctrl=%s real=%s selftest=%s tmpdir=%s "
          "control_clean=%s control_findings=%s%s r42detail=%s hiddendetail=%s"
          % (cand_pass, total, "ok" if r42_ok else "RED", "ok" if hidden_ok else "RED",
             "REJECTED" if hidden_ctrl_rejected else "ACCEPTED", "ok" if real_ok else "RED",
             "ok" if st_ok else "RED", "ok" if tmp_ok else "RED",
             "REJECTED" if clean_pass < total else "ACCEPTED",
             "REJECTED" if find_pass < total else "ACCEPTED",
             ("" if cand_pass == total else " failed=[" + ";".join(cand_details) + "]"),
             r42_detail[:120] if not r42_ok else "-", hidden_detail if not hidden_ok else "-"))
    shutil.rmtree(work, ignore_errors=True)
    target = (cand_pass == total and r42_ok and hidden_ok and hidden_ctrl_rejected and real_ok
              and st_ok and tmp_ok and clean_pass < total and find_pass < total)
    return 0 if target else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
