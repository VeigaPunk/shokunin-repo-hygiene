#!/usr/bin/env python3
"""R41w2critic02 probe: git-plumbing attacks on the pinned tools/souji-freeze-check.py.

Builds synthetic git fixtures under --scratch (every git call names -C <dir>, toplevel asserted,
author identity only via GIT_AUTHOR_*/GIT_COMMITTER_* env), runs the pinned tool (--tool, a file
extracted from the lane's committed blob) and records rc, FINDING lines, SUMMARY, the freeze
commit the tool's freeze_rev() selects (observed via import), and the expected (documented) result.
Read-only on the lane: the lane is only read via the tool's own git calls.
"""
import argparse
import hashlib
import importlib.util
import os
import subprocess
import sys

GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0",
           "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
           "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}
ARGS = None
MOD = None
RESULTS = []

C0 = b"# counter v0\nprint('c0')\n"
C1 = b"# counter v1\nprint('c1')\n"
POP = b"id\tname\n1\talpha\n2\tbeta\n"
CTL_RED = b"SUMMARY items=2 corrected=0\nEXIT=1\n"
CTL_GREEN = b"SUMMARY items=2 corrected=2\nEXIT=0\n"
ZERO = "0" * 64
PREREG = "prereg.txt"
DISP = ".ufo/waves/round-41/w1-dispatch.json"
DISP_UNI = ".ufo/waves/round-41/w\u00e9-dispatch.json"


def setup_env(scratch):
    os.environ.update(GIT_ENV)
    os.environ["TMPDIR"] = scratch


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git(d, *args, check=True):
    p = subprocess.run(["git", "-C", d] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       check=False)
    if check and p.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), p.stderr.decode("utf-8", "replace")))
    return p.stdout.decode("utf-8", "replace").strip()


def put(d, rel, data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    full = os.path.join(d, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as h:
        h.write(data)


def commit(d, msg, add=True):
    if add:
        git(d, "add", "-A")
    git(d, "commit", "-q", "--allow-empty", "-m", msg)
    return git(d, "rev-parse", "HEAD")


def subj(d, c):
    return git(d, "log", "-1", "--format=%s", c)


def repo(name):
    d = os.path.join(ARGS.scratch, name)
    os.makedirs(d)
    git(d, "init", "-q", "-b", "main")
    top = git(d, "rev-parse", "--show-toplevel")
    if os.path.realpath(top) != os.path.realpath(d):
        raise RuntimeError("toplevel mismatch: %s" % top)
    put(d, "README", "base\n")
    return d, commit(d, "%s base" % name)


def prereg_text(base, counter=("census/c.py", sha(C0)), pop=("census/pop.tsv", sha(POP)),
                ctl="census/ctl.txt", target="items=2", round_line="Round: 41", crlf=False):
    lines = ["# prereg"] + ([round_line] if round_line else [])
    lines += ["", "## C1 - probe", "Base: %s" % base, "Counter: %s sha256=%s" % counter,
              "Population: %s sha256=%s" % pop, "Control: %s" % ctl, "Target: %s" % target,
              "Kill: any", ""]
    text = "\n".join(lines) + "\n"
    return text.replace("\n", "\r\n") if crlf else text


def std_files(d):
    put(d, "census/c.py", C0)
    put(d, "census/pop.tsv", POP)
    put(d, "census/ctl.txt", CTL_RED)


def std_freeze(d, name, base, path=PREREG, extra=(), **kw):
    std_files(d)
    for rel, data in extra:
        put(d, rel, data)
    put(d, path, prereg_text(base, **kw))
    return commit(d, "%s freeze" % name)


def record(case, doc, expect, d, rev, path=PREREG):
    p = subprocess.run(["python3", "-B", ARGS.tool, "--root", d, "--prereg", path, "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    lines = p.stdout.decode("utf-8", "replace").splitlines()
    findings = [x for x in lines if x.startswith("FINDING ")]
    summ = [x for x in lines if x.startswith("SUMMARY ")]
    r = MOD.Repo(d)
    c = r.commit(rev)
    fz = MOD.freeze_rev(r, c, path) if c else None
    flabel = subj(d, fz) if fz else "None"
    RESULTS.append({"case": case, "doc": doc, "expect": expect, "rc": p.returncode,
                    "findings": findings, "summary": summ, "freeze": flabel,
                    "stderr": p.stderr.decode("utf-8", "replace").strip()})


def dup_prereg(base, counters):
    lines = ["# prereg", "Round: 41", "", "## C1 - probe", "Base: %s" % base]
    lines += ["Counter: %s sha256=%s" % c for c in counters]
    lines += ["Population: census/pop.tsv sha256=%s" % sha(POP), "Control: census/ctl.txt",
              "Target: items=2", "Kill: any", ""]
    return "\n".join(lines) + "\n"


def case_A():
    d, c0 = repo("A")
    F = std_freeze(d, "A", c0)
    put(d, "README", "x\n")
    X = commit(d, "A post")
    record("A1-clean-linear", "freeze = oldest add of PATH; clean", "rc0 findings0 freeze=A freeze", d, X)
    record("A2-rev-equals-freeze", "rev=freeze is allowed", "rc0 findings0", d, F)
    record("A3-rev-before-freeze", "PATH absent at rev -> refusal", "rc2 REFUSAL absent", d, c0)


def case_B():
    d, c0 = repo("B")
    F = std_freeze(d, "B", c0)
    put(d, PREREG, prereg_text(F))
    X = commit(d, "B base set to freeze")
    record("B1-base-equals-freeze", "Base must be STRICT ancestor of freeze", "BASE-NOT-ANCESTOR", d, X)


def case_C():
    d, c0 = repo("C")
    put(d, "README", "mid\n")
    M = commit(d, "C mid")
    std_freeze(d, "C", c0)
    put(d, PREREG, prereg_text(M))
    X = commit(d, "C base edited post-freeze")
    record("C1-base-edited-post-freeze", "prereg text not frozen; only Counter/Population blobs checked",
           "clean (undetected Base edit)", d, X)


def case_D():
    d, c0 = repo("D")
    std_freeze(d, "D", c0)
    put(d, PREREG, prereg_text(c0, target="items=99"))
    X = commit(d, "D target edited post-freeze")
    record("D1-target-edited-post-freeze", "Target not in FROZEN-EDITED scope", "clean (undetected)", d, X)


def case_E():
    d, c0 = repo("E")
    std_freeze(d, "E", c0)
    put(d, "census/ctl.txt", CTL_GREEN)
    X = commit(d, "E control turned green post-freeze")
    record("E1-control-edited-post-freeze", "Control checked only at FREEZE blob", "clean (undetected)", d, X)


def case_F():
    # F1: first Counter line is an untouched file, second Counter line is the edited counter.
    d, c0 = repo("F1")
    put(d, "census/keep.py", C0)
    std_files(d)
    put(d, PREREG, dup_prereg(c0, [("census/keep.py", sha(C0)), ("census/c.py", sha(C0))]))
    put(d, PREREG, dup_prereg(c0, [("census/keep.py", sha(C0)), ("census/c.py", sha(C0))]))
    F = commit(d, "F1 freeze dup-key")
    put(d, "census/c.py", C1)
    put(d, PREREG, dup_prereg(c0, [("census/keep.py", sha(C0)), ("census/c.py", sha(C1))]))
    X = commit(d, "F1 counter edited, second Counter line restamped")
    record("F1-duplicate-counter-key-hides-edit", "grammar silent on duplicate keys; first wins",
           "clean (second Counter line ignored)", d, X)
    # F2: same edit, single Counter line -> control.
    d, c0 = repo("F2")
    std_freeze(d, "F2", c0)
    put(d, "census/c.py", C1)
    put(d, PREREG, prereg_text(c0, counter=("census/c.py", sha(C1))))
    X = commit(d, "F2 counter edited, single line restamped")
    record("F2-single-counter-line-control", "FROZEN-EDITED expected", "FROZEN-EDITED + COUNTER-DIGEST", d, X)


def case_G():
    d, c0 = repo("G1")
    git(d, "checkout", "-q", "-b", "side")
    std_freeze(d, "G1", c0)
    S = git(d, "rev-parse", "HEAD")
    git(d, "checkout", "-q", "main")
    put(d, "README", "main\n")
    commit(d, "G1 main")
    git(d, "merge", "-q", "--no-ff", "-m", "G1 merge", "side")
    MG = git(d, "rev-parse", "HEAD")
    record("G1-added-on-branch-then-merged", "freeze = branch add commit; clean", "rc0 freeze=G1 freeze",
           d, MG)
    d, c0 = repo("G2")
    git(d, "checkout", "-q", "-b", "side")
    std_freeze(d, "G2", c0)
    put(d, "census/c.py", C1)
    commit(d, "G2 side counter edit after freeze")
    git(d, "checkout", "-q", "main")
    put(d, "README", "main\n")
    commit(d, "G2 main")
    git(d, "merge", "-q", "--no-ff", "-m", "G2 merge", "side")
    MG = git(d, "rev-parse", "HEAD")
    record("G2-branch-counter-edit-merged", "FROZEN-EDITED against branch freeze", "FROZEN-EDITED", d, MG)


def case_I():
    d, c0 = repo("I")
    std_freeze(d, "I", c0)
    put(d, "census/c.py", C1)
    X = commit(d, "I counter edited, prereg untouched")
    record("I1-counter-edited-honest", "FROZEN-EDITED at original path", "FROZEN-EDITED", d, X)
    git(d, "mv", "prereg.txt", "prereg-v2.txt")
    put(d, "prereg-v2.txt", prereg_text(c0, counter=("census/c.py", sha(C1))))
    R = commit(d, "I git mv prereg + restamp Counter digest")
    record("I2-renamed-then-restamped", "--no-renames: new PATH's first add is the freeze",
           "clean; freeze = rename commit", d, R, path="prereg-v2.txt")
    record("I3-old-path-after-rename", "PATH absent at rev -> refusal", "rc2 absent", d, R, path=PREREG)


def case_J():
    d, c0 = repo("J")
    std_freeze(d, "J", c0)
    git(d, "rm", "-q", "prereg.txt")
    commit(d, "J delete prereg")
    put(d, PREREG, prereg_text(c0, target="items=99"))
    R = commit(d, "J re-add prereg, Target changed")
    record("J1-deleted-readded-target-changed", "freeze = oldest add; prereg text not compared",
           "clean; freeze = J freeze", d, R)


def case_K():
    d, c0 = repo("K")
    std_freeze(d, "K", c0)
    git(d, "rm", "-q", "prereg.txt")
    commit(d, "K delete prereg")
    put(d, "census/c.py", C1)
    put(d, PREREG, prereg_text(c0, counter=("census/c.py", sha(C1))))
    R = commit(d, "K re-add with counter edited and restamped")
    record("K1-deleted-readded-counter-edited", "digest checked against FIRST add's blob", "COUNTER-DIGEST + FROZEN-EDITED",
           d, R)


def case_L():
    d, c0 = repo("L")
    std_freeze(d, "L", c0)
    put(d, "README", "2\n")
    commit(d, "L 2")
    put(d, "census/c.py", C1)
    put(d, PREREG, prereg_text(c0, counter=("census/c.py", sha(C1))))
    commit(d, "L counter edited and restamped")
    put(d, "README", "4\n")
    c4 = commit(d, "L 4")
    record("L1-full-history", "reference: full history", "COUNTER-DIGEST + FROZEN-EDITED freeze=L freeze", d, c4)
    for n in (1, 2, 3, 4):
        tgt = os.path.join(ARGS.scratch, "L-depth%d" % n)
        subprocess.run(["git", "clone", "-q", "--depth", str(n), "file://" + d, tgt], check=True)
        head = git(tgt, "rev-parse", "HEAD")
        record("L-shallow-depth%d" % n, "shallow clone: freeze = boundary commit if add not visible",
               "documented: none (no shallow clause); observed freeze/findings differ", tgt, head)


def case_M():
    d, c0 = repo("M")
    put(d, "census/dir/a.txt", "x\n")
    put(d, "census/popdir/x.tsv", "id\n1\n")
    std_files(d)
    put(d, PREREG, prereg_text(c0, counter=("census/dir", ZERO), pop=("census/popdir", ZERO)))
    F = commit(d, "M freeze")
    record("M1-counter-and-population-are-directories", "tree blob -> cat-file fails",
           "COUNTER-MISSING + POPULATION-MISSING", d, F)


def case_N():
    d, c0 = repo("N1")
    put(d, "census/real.py", C0)
    os.symlink("real.py", os.path.join(d, "census/link.py"))
    std_files(d)
    put(d, PREREG, prereg_text(c0, counter=("census/link.py", sha(C0))))
    F = commit(d, "N1 freeze honest digest of target content")
    record("N1-symlink-honest-digest", "symlink blob = link text, not target content",
           "COUNTER-DIGEST (false positive: digest of real content)", d, F)
    d, c0 = repo("N2")
    put(d, "census/real.py", C0)
    os.symlink("real.py", os.path.join(d, "census/link.py"))
    std_files(d)
    put(d, PREREG, prereg_text(c0, counter=("census/link.py", sha(b"real.py"))))
    F = commit(d, "N2 freeze digest of link text")
    put(d, "census/real.py", C1)
    X = commit(d, "N2 executed target edited post-freeze")
    record("N2-symlink-link-text-digest-target-edited", "tool never follows the symlink",
           "clean (executed counter changed, undetected)", d, X)


def case_O():
    d, c0 = repo("O")
    put(d, "census/pop.tsv", POP)
    put(d, "census/ctl.txt", CTL_RED)
    put(d, PREREG, prereg_text(c0, counter=("census/sub", ZERO)))
    git(d, "add", "-A")
    git(d, "update-index", "--add", "--cacheinfo", "160000,%s,census/sub" % c0)
    F = commit(d, "O freeze with gitlink Counter", add=False)
    record("O1-counter-is-gitlink", "cat-file on tree/commit entry fails", "COUNTER-MISSING", d, F)


def case_P():
    d, c0 = repo("P")
    F = std_freeze(d, "P", c0, extra=[(DISP, "{}\n")])
    record("P1-dispatch-same-commit-as-prereg", "freeze itself counts (c == freeze)",
           "DISPATCH-BEFORE-FREEZE C0 first added at freeze", d, F)


def case_Q():
    d, c0 = repo("Q")
    git(d, "checkout", "-q", "-b", "side")
    put(d, DISP, "{}\n")
    commit(d, "Q side dispatch")
    git(d, "checkout", "-q", "main")
    std_freeze(d, "Q", c0)
    git(d, "merge", "-q", "--no-ff", "-m", "Q merge", "side")
    MG = git(d, "rev-parse", "HEAD")
    record("Q1-dispatch-on-side-branch-merged", "documented test is strict ancestry; side commit is not",
           "clean (ancestry-only test)", d, MG)


def case_R():
    d, c0 = repo("R")
    put(d, DISP, "{}\n")
    D = commit(d, "R dispatch before freeze")
    F = std_freeze(d, "R", c0)
    record("R1-dispatch-before-freeze-linear", "positive control", "DISPATCH-BEFORE-FREEZE", d, F)
    d, c0 = repo("R2")
    put(d, DISP_UNI, "{}\n")
    commit(d, "R2 non-ascii dispatch before freeze")
    F = std_freeze(d, "R2", c0)
    record("R2-dispatch-nonascii-name", "git quotes the path (core.quotePath); endswith fails",
           "clean (silent miss)", d, F)


def case_S():
    d, c0 = repo("S")
    put(d, DISP, "{}\n")
    commit(d, "S dispatch before freeze")
    F = std_freeze(d, "S", c0, round_line=None)
    record("S1-no-round-line", "dispatch check keyed on Round line; silently skipped",
           "clean (silent skip)", d, F)
    d, c0 = repo("S2")
    put(d, DISP, "{}\n")
    commit(d, "S2 dispatch before freeze")
    F = std_freeze(d, "S2", c0, crlf=True)
    record("S2-crlf-prereg", "ROUND regex needs $ before LF; CR breaks it", "clean (silent skip)", d, F)


def main(argv):
    global ARGS, MOD
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    ARGS = ap.parse_args(argv)
    setup_env(ARGS.scratch)
    spec = importlib.util.spec_from_file_location("sfc_probe", ARGS.tool)
    MOD = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(MOD)
    for fn in (case_A, case_B, case_C, case_D, case_E, case_F, case_G, case_I, case_J, case_K, case_L,
               case_M, case_N, case_O, case_P, case_Q, case_R, case_S):
        fn()
    out = []
    for r in RESULTS:
        out.append("CASE %s" % r["case"])
        out.append("  doc: %s" % r["doc"])
        out.append("  expect: %s" % r["expect"])
        out.append("  observed: rc=%d freeze=%s summary=%s" % (r["rc"], r["freeze"], r["summary"]))
        for f in r["findings"]:
            out.append("  %s" % f)
        if r["stderr"]:
            out.append("  stderr: %s" % r["stderr"])
    text = "\n".join(out) + "\n"
    with open(ARGS.out, "w", encoding="utf-8") as h:
        h.write(text)
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
