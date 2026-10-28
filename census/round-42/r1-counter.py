#!/usr/bin/env python3
"""census/round-42/r1-counter.py — r42 R1 (residual, not a claim): R41-D-LG-DANGLING.

The r41 closure ran `tools/souji-landing-gate.py --round 41` at the r41 tip WITHOUT `--fleet-root` and read three
`LG-DANGLING-PTR` findings (`corpus/README.md:217` twice, `corpus/knowledge/jj-colocation-receipts.md:148`): pointers into the
fleet repo's `.ufo/waves/hyaku/jj-w1/reports/`, which the lane tree does not carry. The same run WITH `--fleet-root`
reads findings=0, so the r41 lesson's N18 text ("raised for ... an untracked round-40 file and ...") and the closure
disagreed about which mode was the measurement. R1 settles it append-only: `corpus/pointer-exemptions.tsv` gains one row per
dangling pointer (path<TAB>reason), no existing line of any file changes.

Target: `SUMMARY findings=0 deleted=0 rows_added=3 stale=0` (exit 0) where
  findings   the gate's own `findings=` at REV, run as `--root LANE --rev REV --round 41` (NO --fleet-root)
  deleted    deleted lines between BASE and REV in corpus/README.md, the jj-colocation entry and pointer-exemptions.tsv
  rows_added data rows appended to corpus/pointer-exemptions.tsv between BASE and REV
  stale      `LG-DANGLING-PTR-EXEMPT-STALE` findings printed by the same run
CLI: python3 -B census/round-42/r1-counter.py --root LANE --rev FULL40 [--base FULL40] [--scratch DIR]
Exit: 0 met; 1 unmet; 2 could-not-evaluate.
"""
import argparse, os, re, subprocess, sys

REV = re.compile(r"^[0-9a-f]{40}$")
BASE = "bf618f6c5c09d302994871c94903abbea2deb60d"
GATE = "tools/souji-landing-gate.py"
FILES = ("corpus/README.md", "corpus/knowledge/jj-colocation-receipts.md", "corpus/pointer-exemptions.tsv")
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}


def env(scratch):
    e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": scratch}
    e.update(GIT_ENV)
    return e


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--scratch")
    a = ap.parse_args(argv)
    scratch = a.scratch or os.environ.get("TMPDIR")
    if not scratch or not os.path.isdir(scratch):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --scratch (or TMPDIR) must name a directory\n")
        return 2
    for rev in (a.rev, a.base):
        if not REV.match(rev) or subprocess.run(["git", "-C", a.root, "cat-file", "-e", rev + "^{commit}"],
                                                 env=env(scratch), stdout=subprocess.DEVNULL,
                                                 stderr=subprocess.DEVNULL).returncode != 0:
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: bad revision %s\n" % rev)
            return 2
    # the gate runs from the committed bytes at REV (an exported tree), never the working tree
    import tempfile, shutil
    work = tempfile.mkdtemp(prefix="souji-r42-r1.", dir=scratch)
    try:
        tar = subprocess.run(["git", "-C", a.root, "archive", "--format=tar", a.rev, "tools", "corpus"],
                             stdout=subprocess.PIPE, env=env(scratch), check=False)
        if tar.returncode != 0:
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: git archive failed\n")
            return 2
        subprocess.run(["tar", "-x", "-C", work], input=tar.stdout, check=True)
        gate = subprocess.run(["python3", "-B", os.path.join(work, GATE), "--root", a.root, "--rev", a.rev,
                               "--round", "41"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                              env=env(scratch), check=False, timeout=600)
        m = re.search(r"^SUMMARY\tfindings=(\d+)", gate.stdout, re.M)
        findings = int(m.group(1)) if m else -1
        stale = gate.stdout.count("LG-DANGLING-PTR-EXEMPT-STALE")
        deleted = 0
        for f in FILES:
            ns = subprocess.run(["git", "-C", a.root, "diff", "--numstat", a.base, a.rev, "--", f],
                                stdout=subprocess.PIPE, text=True, env=env(scratch), check=False).stdout.split()
            if len(ns) >= 2 and ns[1].isdigit():
                deleted += int(ns[1])
        pe = subprocess.run(["git", "-C", a.root, "diff", "--numstat", a.base, a.rev, "--",
                             "corpus/pointer-exemptions.tsv"], stdout=subprocess.PIPE, text=True,
                            env=env(scratch), check=False).stdout.split()
        added = int(pe[0]) if pe and pe[0].isdigit() else 0
        print("SUMMARY findings=%d deleted=%d rows_added=%d stale=%d" % (findings, deleted, added, stale))
        return 0 if (findings == 0 and deleted == 0 and added == 3 and stale == 0) else 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
