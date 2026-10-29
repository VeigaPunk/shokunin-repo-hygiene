#!/usr/bin/env python3
"""R42mutationtester03 input builder: scratch clones of the lane tip, each carrying one synthetic
candidate or prior-fixture variant, plus the rev each input is scored at. Writes inputs.json into the
scratch root only. Never writes the lane; clones are created with `git clone --shared` (read of the lane).
"""
import json
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42mutationtester03"
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42mutationtester03"
TIP = "afe17f416eec04dcf3f480b580a8f928de61d19d"
CAND = "tests/fixtures/r42-drift-conditions.py"
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0",
           "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
           "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
           "PATH": os.environ.get("PATH", "/usr/bin:/bin")}
CTRL = os.path.join(LANE, "census/round-42/controls")
FROZEN_COUNTER = os.path.join(LANE, "census/round-42/c3-counter.py")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fixtures as F  # noqa: E402


def git(c, *args):
    p = subprocess.run(["git", "-C", c] + list(args), env=GIT_ENV, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True, check=False)
    if p.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), p.stderr))
    return p.stdout.strip()


def make(name, files=None, removals=(), edits=None):
    """Clone the lane tip into SCRATCH/clones/<name>, apply files (dest -> bytes), removals and
    in-place edits (dest -> function(bytes)->bytes), commit in the clone, return (path, rev)."""
    d = os.path.join(SCRATCH, "clones", name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    subprocess.run(["git", "clone", "-q", "--shared", LANE, d], env=GIT_ENV, check=True)
    if git(d, "rev-parse", "--show-toplevel") != d:
        raise SystemExit("toplevel mismatch for " + d)
    for dest, data in (files or {}).items():
        p = os.path.join(d, dest)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as h:
            h.write(data)
    for dest in removals:
        git(d, "rm", "-q", dest)
    for dest, fn in (edits or {}).items():
        p = os.path.join(d, dest)
        with open(p, "rb") as h:
            data = h.read()
        with open(p, "wb") as h:
            h.write(fn(data))
    git(d, "add", "-A")
    git(d, "commit", "-q", "--allow-empty", "-m", "r42 mutationtester03 input " + name)
    return d, git(d, "rev-parse", "HEAD")


def main():
    if os.geteuid() == 0:
        raise SystemExit("refusing to run as root")
    with open(os.path.join(CTRL, "c3-stub-allpass.py"), "rb") as h:
        allpass = h.read()
    with open(os.path.join(CTRL, "c3-stub-sniff.py"), "rb") as h:
        sniff = h.read()
    inputs = {}

    # IN01: the lane tip with no candidate (control A, the absent-fixture input).
    d, rev = make("IN01-ABSENT")
    inputs["IN01-ABSENT"] = {"clone": d, "rev": rev}
    # IN02/IN03: the two committed stubs (control B, control C).
    for name, body in (("IN02-ALLPASS", allpass), ("IN03-SNIFF", sniff)):
        d, rev = make(name, {CAND: body})
        inputs[name] = {"clone": d, "rev": rev}
    # Variant candidates (each a synthetic input that exercises one counter branch).
    variants = {
        "IN04-PARTIAL": F.partial(),
        "IN05-RC2": F.rc2(),
        "IN06-TB": F.tb_fail(),
        "IN07-NOSUM": F.nosum(),
        "IN08-FAIL0": F.fail0_rc1(),
        "IN09-TWELVE": F.cases_n(12),
        "IN10-INCONS": F.inconsistent(),
        "IN11-TWO": F.two_summaries(),
        "IN12-SLOW": F.slow(),
        "IN13-TBCLEAN": F.tb_clean(),
        "IN20-SYNTHMET": F.synth_met(),
        "IN22-FAILRC0": F.fail_rc0(),
    }
    for name, body in variants.items():
        d, rev = make(name, {CAND: body})
        inputs[name] = {"clone": d, "rev": rev}
    # Prior-fixture variants (tests/fixtures/r36-worktree-drift.py is one of the eight PRIOR fixtures).
    R36 = "tests/fixtures/r36-worktree-drift.py"
    d, rev = make("IN14-PRIORKILL", {CAND: allpass, R36: F.partial()})
    inputs["IN14-PRIORKILL"] = {"clone": d, "rev": rev}
    d, rev = make("IN15-PRIORFAIL", {CAND: allpass, R36: F.always_fail()})
    inputs["IN15-PRIORFAIL"] = {"clone": d, "rev": rev}
    d, rev = make("IN16-PRIORGONE", {CAND: allpass}, removals=[R36])
    inputs["IN16-PRIORGONE"] = {"clone": d, "rev": rev}
    # Population digest variant: every id kept, first digest zeroed.
    POP = "census/round-42/c3-mutants.tsv"

    def zero_first_digest(data):
        lines = data.decode("utf-8").split("\n")
        f = lines[1].split("\t")
        f[2] = "0" * 64
        lines[1] = "\t".join(f)
        return "\n".join(lines).encode("utf-8")
    d, rev = make("IN17-ANCHORDIG", {CAND: allpass}, edits={POP: zero_first_digest})
    inputs["IN17-ANCHORDIG"] = {"clone": d, "rev": rev}
    # Tool sha variant: one appended comment byte in the pinned tool.
    d, rev = make("IN18-TOOLDIFF", {CAND: allpass},
                  edits={"tools/souji-worktree-drift.py": lambda b: b + b"\n# r42 mutation probe\n"})
    inputs["IN18-TOOLDIFF"] = {"clone": d, "rev": rev}
    # Rev variants on the sniff clone and the absent clone.
    inputs["IN19-SHORTREV"] = {"clone": inputs["IN03-SNIFF"]["clone"], "rev": inputs["IN03-SNIFF"]["rev"][:39]}
    inputs["IN21-BADREV"] = {"clone": inputs["IN01-ABSENT"]["clone"], "rev": "0" * 40}
    with open(os.path.join(SCRATCH, "inputs.json"), "w") as h:
        json.dump(inputs, h, indent=1, sort_keys=True)
    print(json.dumps({k: v["rev"] for k, v in sorted(inputs.items())}, indent=1))


if __name__ == "__main__":
    main()
