#!/usr/bin/env python3
"""R40w2simplifier01 reproduction: YAGNI review of the landed C1 counter (read-only w.r.t. the lane).

Every write goes under --work (an explicit scratch directory). The lane is only read via `git show`
and by running the lane's own fixture file from a scratch copy.

Usage:
  python3 -B .ufo/waves/round-40/w2/R40w2simplifier01-repro.py --lane /home/vgpnk/Projects/shokunin/souji-shokunin \
      --work /fast/scratch/hyaku/souji-r40/w2/<seat>/repro

Pinned revisions (verified by the seat): landed instrument 128e412b0ced3c243dc27c3dd3332054a611bc2e;
measured tip 549d9ec53a1f5932337ff14438fcd22b0621828d; later HEAD 994de3b (path-binding commit).
"""
import argparse
import importlib.util
import os
import shutil
import subprocess
import sys

LANDED = "128e412b0ced3c243dc27c3dd3332054a611bc2e"
TIP = "549d9ec53a1f5932337ff14438fcd22b0621828d"
LATER = "994de3b"
ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "GIT_AUTHOR_NAME": "fixture",
       "GIT_AUTHOR_EMAIL": "fixture@example.invalid", "GIT_COMMITTER_NAME": "fixture",
       "GIT_COMMITTER_EMAIL": "fixture@example.invalid", "LC_ALL": "C"}


def show_bytes(lane, rev, path):
    return subprocess.run(["git", "-C", lane, "show", "%s:%s" % (rev, path)], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=True, env=ENV).stdout


def gitc(root, *args):
    return subprocess.run(["git", "-C", root] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, check=True, env=ENV).stdout.strip()


def delete_lines(src_bytes, first, last, expect_prefix):
    lines = src_bytes.decode("utf-8").split("\n")
    if not lines[first - 1].startswith(expect_prefix):
        raise SystemExit("refusing: line %d is %r, expected prefix %r" % (first, lines[first - 1], expect_prefix))
    del lines[first - 1:last]
    return "\n".join(lines).encode("utf-8")


def run_counter(counter, root, rev, items, register, register_rev, forged=None, floors=("1", "1"), scratch=None):
    cmd = ["python3", "-B", counter, "--root", root, "--rev", rev, "--items", items, "--register", register,
           "--register-rev", register_rev, "--min-cells", floors[0], "--min-commit-rows", floors[1],
           "--scratch", scratch]
    if forged:
        cmd += ["--forged", forged]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, env=ENV)
    return proc.returncode, proc.stdout, proc.stderr


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    lane = os.path.abspath(args.lane)
    work = os.path.abspath(args.work)
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(work)
    print("ROOTS lane=%s work=%s landed=%s tip=%s later=%s" % (lane, work, LANDED, TIP, LATER))

    # Scratch copies of the instrument bytes.
    counters = {}
    landed_src = show_bytes(lane, LANDED, "census/round-40/c1-counter.py")
    head_src = show_bytes(lane, LATER, "census/round-40/c1-counter.py")
    cdir = os.path.join(work, "counters")
    os.makedirs(cdir)
    counters["landed"] = os.path.join(cdir, "landed.py")
    counters["later-HEAD"] = os.path.join(cdir, "later.py")
    with open(counters["landed"], "wb") as h:
        h.write(landed_src)
    with open(counters["later-HEAD"], "wb") as h:
        h.write(head_src)
    # Single-arm deletions of the landed bytes (line numbers are 1-based in census/round-40/c1-counter.py@128e412).
    variants = {
        "no-L221-equal": (221, 224, "        if commit == receipt_rev:"),
        "no-L229-notancestor": (229, 231, "        if not is_ancestor(root, commit, rev):"),
        "no-L252-evidence-resolve": (252, 253, "    if not git_resolves(root, evidence_rev):"),
        "no-L217-register-resolve": (217, 220, "        if not REV.match(commit) or not git_resolves(root, commit):"),
    }
    for name, (first, last, prefix) in variants.items():
        path = os.path.join(cdir, name + ".py")
        with open(path, "wb") as h:
            h.write(delete_lines(landed_src, first, last, prefix))
        counters[name] = path

    # Fixture: the landed (128e412) fixture and reconciler, extracted into a scratch lane tree.
    tree = os.path.join(work, "lane-tree")
    os.makedirs(os.path.join(tree, "tests", "fixtures"))
    os.makedirs(os.path.join(tree, "tools"))
    fixture_path = os.path.join(tree, "tests", "fixtures", "r40-c1-evidence.py")
    with open(fixture_path, "wb") as h:
        h.write(show_bytes(lane, LANDED, "tests/fixtures/r40-c1-evidence.py"))
    with open(os.path.join(tree, "tools", "souji-citation-reconcile.py"), "wb") as h:
        h.write(show_bytes(lane, LANDED, "tools/souji-citation-reconcile.py"))
    base_counter = os.path.join(lane, "census", "round-39", "c1-counter.py")

    print("\n##### 1. landed fixture (128e412, 8 cases) x each counter")
    for name, counter in counters.items():
        proc = subprocess.run(["python3", "-B", fixture_path, "--counter", counter, "--base-counter", base_counter,
                               "--work", os.path.join(work, "fixture-work-" + name)], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True, check=False, env=ENV) if os.makedirs(
            os.path.join(work, "fixture-work-" + name)) is None else None
        fails = [l for l in proc.stdout.splitlines() if "FAIL" in l]
        summ = [l for l in proc.stdout.splitlines() if l.startswith("SUMMARY")]
        print("%-26s rc=%d %s %s" % (name, proc.returncode, summ[0] if summ else "-", fails[0][:120] if fails else ""))

    # Lane's own measured command (tip 549d9ec items, register read at the tip).
    print("\n##### 2. real L1 command at measured tip %s (items/forged/register read from the tip)" % TIP)
    items = os.path.join(work, "c1-items.tsv")
    forged = os.path.join(work, "c1-forged.tsv")
    with open(items, "wb") as h:
        h.write(show_bytes(lane, TIP, "census/round-40/c1-items.tsv"))
    with open(forged, "wb") as h:
        h.write(show_bytes(lane, TIP, "census/round-40/c1-forged.tsv"))
    for name in ("landed", "later-HEAD"):
        rc, out, err = run_counter(counters[name], lane, TIP, items, "census/round-40/cells.tsv", TIP,
                                   forged=forged, floors=("3", "3"), scratch=work)
        print("-- %s rc=%d" % (name, rc))
        print(out.rstrip())

    # Scratch fixture repository for the probes (the lane's own build_repo).
    spec = importlib.util.spec_from_file_location("fx", fixture_path)
    fx = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fx)
    pdir = os.path.join(work, "probe")
    os.makedirs(pdir)
    root, c0, c1, c2, side = fx.build_repo(pdir, tree)
    assert gitc(root, "rev-parse", "--show-toplevel") == root
    print("\n##### 3. probe fixture repo: c0=%s c1=%s c2=%s side=%s" % (c0, c1, c2, side))

    def commit(name, text, msg):
        with open(os.path.join(root, name), "w", encoding="utf-8") as h:
            h.write(text)
        gitc(root, "add", "-A")
        gitc(root, "commit", "-qm", msg)
        return gitc(root, "rev-parse", "HEAD")

    HDR = "id\tfile\tanchor\texpected\tstale\treceipt\treceipt_rev\tcommit\n"
    IHDR = "id\tfile\tanchor\tmust\tmustnot\tevidence\n"

    def items_file(name, rows):
        path = os.path.join(work, name)
        with open(path, "w", encoding="utf-8") as h:
            h.write(IHDR + "".join("\t".join(r) + "\n" for r in rows))
        return path

    eqA = commit("claims-eq.md", "EQ-CLAIM cases=7 receipt `receipts/r0.txt` at %s\n" % c0, "probe eq anchor")
    eqB = commit("reg-eq.tsv", HDR + "ROW-EQ\tclaims-eq.md\tEQ-CLAIM\tcases=7\tcases=99\treceipts/r0.txt\t%s\t%s\n" % (c0, c0), "probe eq register")
    bkA = commit("claims-bk.md", "BK-CLAIM cases=7 receipt `receipts/r0.txt` at %s\n" % c0, "probe bk anchor")
    bkB = commit("reg-bk.tsv", HDR + "ROW-BK\tclaims-bk.md\tBK-CLAIM\tcases=7\tcases=99\treceipts/r0.txt\t%s\t%s\n" % (c1, c0), "probe bk register")
    sideB = commit("reg-side.tsv", HDR + "ROW-SIDE\tclaims.md\tBOUND-CLAIM\tcases=7\tcases=99\treceipts/r0.txt\t%s\t%s\n" % (c0, side), "probe side register")
    zeroB = commit("reg-zero.tsv", HDR + "ROW-ZERO\tclaims.md\tBOUND-CLAIM\tcases=7\tcases=99\treceipts/r0.txt\t%s\t%s\n" % (c0, "0" * 40), "probe zero register")
    nofileB = commit("reg-nofile.tsv", HDR + "ROW-NOFILE\tno-such.md\tBOUND-CLAIM\tcases=7\tcases=99\treceipts/r0.txt\t%s\t%s\n" % (c0, side), "probe nofile register")
    # Abbreviated receipt_rev naming the same commit as the row's commit.
    abbrB = commit("reg-abbr.tsv", HDR + "ROW-ABBR\tclaims.md\tBOUND-CLAIM\tcases=7\tcases=99\treceipts/r0.txt\t%s\t%s\n" % (c0[:12], c0), "probe abbr register")

    a = items_file("a.tsv", [("BOUND-1", "claims.md", "BOUND-CLAIM", "cases=7", "-", "receipts/r0.txt@" + c1)])
    p1 = items_file("p1-eq.tsv", [("BOUND-EQ", "claims-eq.md", "EQ-CLAIM", "cases=7", "-", "receipts/r0.txt@" + c0)])
    p2 = items_file("p2-bk.tsv", [("BOUND-BK", "claims-bk.md", "BK-CLAIM", "cases=7", "-", "receipts/r0.txt@" + c0)])
    d = items_file("d-path-uncited.tsv", [("PATH-UNCITED", "claims.md", "BOUND-CLAIM", "cases=7", "-", "receipts/r1b.txt@" + c1)])
    typo = items_file("f-typo.tsv", [("FORGE-TYPO", "claims-typo.md", "FORGED-CLAIM", "cases=7", "-", "receipts/r0.txt@" + c0)])
    tokenonly = items_file("f-token.tsv", [("FORGE-TOKEN", "claims.md", "FORGED-CLAIM", "cases=7", "-", "receipts/r0.txt@" + c0)])
    head_rev = gitc(root, "rev-parse", "HEAD")

    def probe(label, counter, items_p, reg, reg_rev, rev, forged_p=None, floors=("1", "1")):
        rc, out, err = run_counter(counter, root, rev, items_p, reg, reg_rev, forged=forged_p, floors=floors, scratch=pdir)
        lines = [l for l in out.splitlines() if l.startswith(("ITEM", "FORGED", "REGISTER ", "SUMMARY"))]
        extra = err.strip().splitlines()[-1] if err.strip() else ""
        print("%-48s rc=%d" % (label, rc))
        for l in lines:
            print("      " + l)
        if extra:
            print("      stderr: " + extra)

    print("\n##### 4. probes against the landed counter")
    probe("A valid bound item, no --forged", counters["landed"], a, "cells-clean.tsv", c2, c2)
    probe("B forged row with misspelt path (--forged)", counters["landed"], a, "cells-clean.tsv", c2, c2, forged_p=typo)
    probe("D evidence path not cited on the line", counters["landed"], d, "cells-clean.tsv", c2, c2)
    probe("C abbreviated receipt_rev, equal commit", counters["landed"], a, "reg-abbr.tsv", head_rev, c2)
    probe("S1 equal commit, anchor names it", counters["landed"], p1, "reg-eq.tsv", head_rev, eqA)
    probe("S2 commit older than receipt_rev, anchor names it", counters["landed"], p2, "reg-bk.tsv", head_rev, bkA)
    probe("S3 commit not ancestor of rev", counters["landed"], a, "reg-side.tsv", head_rev, c2)
    probe("S4 unresolvable 40-zero commit", counters["landed"], a, "reg-zero.tsv", head_rev, c2)
    probe("N  absent anchored file, commit not ancestor", counters["landed"], a, "reg-nofile.tsv", head_rev, c2)
    probe("H  register absent, zero floors", counters["landed"], a, "no-such.tsv", c2, c2, floors=("0", "0"))

    print("\n##### 5. the same probes against single-arm deletions and the later HEAD counter")
    for name in ("no-L221-equal", "no-L229-notancestor", "no-L217-register-resolve", "later-HEAD"):
        print("== %s" % name)
        ctr = counters[name]
        probe("S1 equal commit", ctr, p1, "reg-eq.tsv", head_rev, eqA)
        probe("S2 backwards commit", ctr, p2, "reg-bk.tsv", head_rev, bkA)
        probe("S3 commit not ancestor of rev", ctr, a, "reg-side.tsv", head_rev, c2)
        probe("S4 unresolvable 40-zero commit", ctr, a, "reg-zero.tsv", head_rev, c2)
        probe("D  evidence path not cited on the line", ctr, d, "cells-clean.tsv", c2, c2)
        probe("K  forged token-only line (must stay OPEN)", ctr, a, "cells-clean.tsv", c2, c2, forged_p=tokenonly)

    print("\n##### 6. has_token boundary (landed module, direct call)")
    spec2 = importlib.util.spec_from_file_location("landed_counter", counters["landed"])
    mod = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(mod)
    for text, token, want in (("rows=178", "rows=17", False), ("cases=79", "cases=7", False),
                              ("cases=7,", "cases=7", True), ("records=79", "records=", True),
                              ("subcases=21", "cases=21", False)):
        got = mod.has_token(text, token)
        print("has_token(%r,%r)=%s want=%s %s" % (text, token, got, want, "ok" if got == want else "MISMATCH"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
