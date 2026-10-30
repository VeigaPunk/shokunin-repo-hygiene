#!/usr/bin/env python3
"""r43 C1 discrimination fixture: the r42 and r43 correction counters over synthetic repos.

For each frozen case the fixture makes TWO disposable shared clones (never the lane):

  r42 clone at R42_TIP — corpus/lessons/round-42.md is stripped of its existing CORRECTION-DE
      lines and the case's r42 lines are appended; census/round-42/c1-register.tsv may take the
      case's extra rows; SCORECARD.md may take the case's append. Then the r42 counter runs at
      that clone commit.
  r43 clone at the lane's current master tip (must already carry census/round-43/c1-required.tsv)
      — corpus/lessons/round-43.md is created with the case's r43 lines; census/round-43/
      c1-required.tsv may take the case's extra rows; SCORECARD.md the same append. Then the r43
      counter runs at that clone commit.

Each case freezes, per counter, an expectation: the exit code plus a predicate over the counter's
SUMMARY fields. `expect42` documents the measured r42 defect signature (the before state this
round fixes); `expect43` is the r43 grammar. Usage:

  python3 -B tests/fixtures/r43-correction-prose.py --work DIR [--lane-root LANE] \
      [--rev42 FULL40] [--rev43 FULL40|master] [--counter42 PATH] [--counter43 PATH]

Prints `case-<name>-r42=<PASS|FAIL>` / `case-<name>-r43=<PASS|FAIL>` plus the observed SUMMARY of
every FAIL, then `SUMMARY42 cases=N pass=.. fail=..` and `SUMMARY43 cases=N pass=.. fail=..`.
Exit 0 iff the r43 column is all-pass AND the r42 column matches its frozen defect signatures.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

R42_TIP = "34343a39ffab8029b06e8e6c9ac699ebcbd65f8a"
R43_SUMMARY = re.compile(
    r"^SUMMARY required=(\d+) registered=(\d+) missing=(\d+) junk=(\d+) fenced=(\d+) duplicate=(\d+) "
    r"retracted=(\d+) rederived=(\d+) rederive_failed=(\d+) new_mismatches=(-?\d+)", re.M)
R42_SUMMARY = re.compile(
    r"^SUMMARY items=(\d+) population=(\w+) registered=(\d+) class_ok=(\d+) unresolved=(\d+) "
    r"corrected=(\d+) junk=(\d+) rewritten=(\d+) new_mismatches=(-?\d+)", re.M)
R42_KEYS = ("items", "population", "registered", "class_ok", "unresolved", "corrected", "junk",
            "rewritten", "new_mismatches")
R43_KEYS = ("required", "registered", "missing", "junk", "fenced", "duplicate", "retracted",
            "rederived", "rederive_failed", "new_mismatches")

D1 = ("CORRECTION-R39 id=R43-D1 file=census/round-39/records/census-after.txt field=rows "
      "stale=173 derived=rows=174 rev=0242085909fb6a4ee041c5443d76316ac6d59d4b")
D2 = ("CORRECTION-R39 id=R43-D2 file=census/round-39/records/census-after.txt field=W04 "
      "stale=47 derived=W04=48 rev=0242085909fb6a4ee041c5443d76316ac6d59d4b")
D3 = ("CORRECTION-R39 id=R43-D3 file=census/round-39/records/final-tip-measure.txt field=header-rev "
      "stale=0242085909fb6a4ee041c5443d76316ac6d59d4b derived=544104503a3ad70687ba399fcafd12bd30648169 "
      "rev=0242085909fb6a4ee041c5443d76316ac6d59d4b")
GOOD43 = D1 + "\n" + D2 + "\n" + D3
# the five honest r42 corrections (verbatim from corpus/lessons/round-42.md at the r42 tip)
HONEST42 = [
    "CORRECTION-DE line=14 token=65817d0d derived=rev-unresolved rev=bf618f6c5c09d302994871c94903abbea2deb60d",
    "CORRECTION-DE line=68 token=42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44 derived=sha256=bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f rev=bf618f6c5c09d302994871c94903abbea2deb60d",
    "CORRECTION-DE line=68 token=71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897 derived=sha256=bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f rev=bf618f6c5c09d302994871c94903abbea2deb60d",
    "CORRECTION-DE line=92 token=09bb8e0d derived=rev-unresolved rev=bf618f6c5c09d302994871c94903abbea2deb60d",
    "CORRECTION-DE line=175 token=c2-after.tsv derived=path-absent rev=bf618f6c5c09d302994871c94903abbea2deb60d",
]


def g42(cid, rc, **fields):
    return (cid, "r42", rc, fields)


def g43(cid, rc, **fields):
    return (cid, "r43", rc, fields)


# (case name, r43 lesson lines, r42 lesson lines, r43 register extra rows, r42 register extra rows,
#  scorecard append, [expectations])
CASES = (
    ("honest-corrections", GOOD43, "\n".join(HONEST42), "", "", "",
     [g43("honest", 0, required=3, registered=3, missing=0, junk=0, fenced=0, duplicate=0,
          retracted=0, rederived=3, rederive_failed=0, new_mismatches=0),
      g42("honest", 0, junk=0, rewritten=0, corrected=5, new_mismatches=0)]),
    ("tilde-fenced", "~~~\n" + D1 + "\n~~~\n" + D2 + "\n" + D3,
     "~~~\n" + HONEST42[0] + "\n~~~\n" + "\n".join(HONEST42[1:]), "", "", "",
     [g43("tilde", 1, fenced=1, registered=2, missing=1),
      g42("tilde", 0, junk=0, corrected=5)]),
    ("fourbt-fenced", "````\n" + D1 + "\n````\n" + D2 + "\n" + D3,
     "````\n" + HONEST42[0] + "\n````\n" + "\n".join(HONEST42[1:]), "", "", "",
     [g43("fourbt", 1, fenced=1, registered=2, missing=1),
      g42("fourbt", 1, junk=1, corrected=4)]),
    ("retracted", GOOD43 + "\nRETRACT-CORRECTION id=R43-D1",
     "\n".join(HONEST42) + "\nThe line=14 correction above is retracted.", "", "", "",
     [g43("retracted", 1, retracted=1),
      g42("retracted", 0, junk=0)]),
    ("duplicated", GOOD43 + "\n" + D1,
     HONEST42[0] + "\n" + HONEST42[0] + "\n" + "\n".join(HONEST42[1:]), "", "", "",
     [g43("dup", 1, duplicate=1),
      g42("dup", 1, junk=1)]),
    ("malformed", GOOD43 + "\nCORRECTION-R39 id=R43-D9 file=x field=y stale=z derived=w",
     "\n".join(HONEST42) + "\nCORRECTION-DE line=999 token=zzz derived=x rev=bf618f6c5c09d302994871c94903abbea2deb60d",
     "", "", "",
     [g43("malformed", 1, junk=1),
      g42("malformed", 1, junk=1)]),
    ("extra-required-row", GOOD43,
     "\n".join(HONEST42),
     "R43-EX\tcensus/round-43/nowhere.txt\tfield\tstale\tderived=1\t0242085909fb6a4ee041c5443d76316ac6d59d4b\tcensus-rows\n",
     "999\tdefinitely-not-a-token\tunresolved\t-\n",
     "",
     [g43("extra", 1, required=4, registered=3, missing=1),
      g42("extra", 0, corrected=5, junk=0)]),
    ("blankless-good-append", GOOD43, "\n".join(HONEST42), "", "",
     "see `tools/souji-verify.sh` for the verdict tool.\n",
     [g43("blankless", 0, new_mismatches=0),
      g42("blankless", 1, rewritten=1, new_mismatches=0)],
     "34e33a662cd0d6931e5aa006bd90364e7852c0d5"),
    ("boundary-mismatch", GOOD43, "\n".join(HONEST42), "", "",
     "see `census/round-43/definitely-absent-receipt.txt` for the count.\n",
     [g43("boundary", 1, new_mismatches=1),
      g42("boundary", 1, rewritten=1, new_mismatches=0)],
     "34e33a662cd0d6931e5aa006bd90364e7852c0d5"),
    ("crlf-register", GOOD43, "\n".join(HONEST42), "CRLF", "", "",
     [g43("crlf", 0, required=3, registered=3, missing=0, junk=0, rederived=3),
      g42("crlf", 0, class_ok=70, junk=0)]),
)


def clone(lane, rev, work, name):
    d = os.path.join(work, name)
    p = subprocess.run(["git", "clone", "-q", "--shared", lane, d], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    if p.returncode != 0:
        return None
    subprocess.run(["git", "-C", d, "checkout", "-q", rev])
    got = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"],
                         stdout=subprocess.PIPE).stdout.decode().strip()
    return d if got == os.path.realpath(d) else None


def commit_clone(d, msg):
    env = dict(os.environ)
    env.update({"GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"})
    subprocess.run(["git", "-C", d, "add", "-A"], env=env, check=True)
    subprocess.run(["git", "-C", d, "commit", "-qm", msg], env=env, check=True)
    return subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], env=env,
                          stdout=subprocess.PIPE).stdout.decode().strip()


def run_counter(path, d, rev, scratchdir):
    os.makedirs(scratchdir, exist_ok=True)
    try:
        p = subprocess.run([sys.executable, "-B", path, "--root", d, "--rev", rev,
                            "--scratch", scratchdir], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=1200)
        return p
    except (subprocess.TimeoutExpired, OSError):
        return None


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--lane-root", default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    ap.add_argument("--rev43", default="master")
    ap.add_argument("--rev42", default=R42_TIP)
    ap.add_argument("--counter42", default=None)
    ap.add_argument("--counter43", default=None)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    os.makedirs(work, exist_ok=True)
    lane = os.path.abspath(ns.lane_root)
    c42 = ns.counter42 or os.path.join(lane, "census/round-42/c1-counter.py")
    c43 = ns.counter43 or os.path.join(lane, "census/round-43/c1-counter.py")
    if ns.rev43 == "master":
        ns.rev43 = subprocess.run(["git", "-C", lane, "rev-parse", "refs/heads/master"],
                                  stdout=subprocess.PIPE).stdout.decode().strip()
    p43n = p43p = p42n = p42p = 0
    for case_row in CASES:
        (name, lesson43, lesson42, reg43, reg42, sc_append, expects) = case_row[:7]
        rev42_case = case_row[7] if len(case_row) > 7 else None
        outs = {}
        for tag, rev, lesson_path, lesson_text, reg_path, reg_text in (
                ("r42", rev42_case or ns.rev42, "corpus/lessons/round-42.md", lesson42,
                 "census/round-42/c1-register.tsv", reg42),
                ("r43", ns.rev43, "corpus/lessons/round-43.md", lesson43,
                 "census/round-43/c1-required.tsv", reg43)):
            d = clone(lane, rev, work, "c_%s_%s" % (name, tag))
            if d is None:
                outs[tag] = None
                continue
            lp = os.path.join(d, lesson_path)
            if tag == "r42":
                text = open(lp, encoding="utf-8").read()
                kept = "\n".join(l for l in text.splitlines()
                                 if not l.startswith("CORRECTION-DE") and not l.startswith("CORRECTION-"))
                open(lp, "w", encoding="utf-8").write(kept + "\n\n## Fixture corrections\n\n" + lesson_text + "\n")
            else:
                os.makedirs(os.path.dirname(lp), exist_ok=True)
                open(lp, "w", encoding="utf-8").write(
                    "# Round 43 — lesson (fixture)\n\n## Corrections\n\n" + lesson_text + "\n")
            if reg_text == "CRLF":
                rp = os.path.join(d, reg_path)
                blob = open(rp, "rb").read().replace(b"\n", b"\r\n")
                open(rp, "wb").write(blob)
            elif reg_text:
                rp = os.path.join(d, reg_path)
                with open(rp, "a", encoding="utf-8") as fh:
                    fh.write(reg_text)
            if sc_append:
                with open(os.path.join(d, "SCORECARD.md"), "a", encoding="utf-8") as fh:
                    fh.write(sc_append)
            rev_case = commit_clone(d, "fixture %s %s" % (name, tag))
            p = run_counter(c42 if tag == "r42" else c43, d, rev_case,
                            os.path.join(work, "s_%s_%s" % (name, tag)))
            if p is None:
                outs[tag] = None
                continue
            out = p.stdout.decode("utf-8", "replace")
            m = (R42_SUMMARY if tag == "r42" else R43_SUMMARY).search(out)
            if not m:
                outs[tag] = None
                continue
            keys = R42_KEYS if tag == "r42" else R43_KEYS
            pairs = [(k, (x if k == "population" else int(x))) for k, x in zip(keys, m.groups())]
            fields = dict(pairs)
            outs[tag] = (p.returncode, fields, out)
        for (cid, tag, rc, want) in expects:
            got = outs.get(tag)
            ok = got is not None and got[0] == rc and all(got[1].get(k) == v for k, v in want.items())
            print("case-%s-%s=%s" % (name, tag, "PASS" if ok else "FAIL"))
            if not ok:
                print("#   want rc=%d %s" % (rc, want))
                print("#   got  %s" % ("no-output" if got is None else
                                       "rc=%d %s" % (got[0], {k: got[1][k] for k in want})))
            if tag == "r42":
                p42n += 1
                p42p += 1 if ok else 0
            else:
                p43n += 1
                p43p += 1 if ok else 0
    print("SUMMARY43 cases=%d pass=%d fail=%d" % (p43n, p43p, p43n - p43p))
    print("SUMMARY42 cases=%d pass=%d fail=%d" % (p42n, p42p, p42n - p42p))
    shutil.rmtree(work, ignore_errors=True)
    return 0 if (p43p == p43n and p42p == p42n) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
