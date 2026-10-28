#!/usr/bin/env python3
"""Witness probes for R41w2mutationtester01.

For each probe, build one synthetic git repository under $TMPDIR (scratch only), then run the committed
tool (mutants/baseline.py) and, where given, one surviving mutant on the same inputs and print both.
Writes nothing outside $TMPDIR. Every git call names -C; identity only through GIT_*_ environment.

  TMPDIR=<scratch> python3 -B probe.py
"""
import hashlib
import os
import subprocess
import sys

SEAT = os.path.dirname(os.path.abspath(__file__))
SCR = os.environ["TMPDIR"]
BASE = os.path.join(SEAT, "mutants", "baseline.py")


def MUT(mid):
    return os.path.join(SEAT, "mutants", mid + ".py")


GENV = dict(os.environ, LC_ALL="C", GIT_AUTHOR_NAME="fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
            GIT_COMMITTER_NAME="fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")
COUNTER = "# counter\nprint('counter')\n"
COUNTER2 = "# counter v2\nprint('counter2')\n"
POP = "id\tname\n1\talpha\n2\tbeta\n"
POP_TWO = "id\tname\n1\talpha\n"
POP_BLANK = "id\tname\n\n\n"
POP_ONE = "id\tname\n"
CTRL = "SUMMARY items=2 corrected=0\nEXIT=1\n"
DJ = ".ufo/waves/round-41/w1-dispatch.json"
README = {"README": "base\n"}


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git(d, *args):
    p = subprocess.run(["git", "-C", d] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=GENV, text=True, check=False)
    if p.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(args), p.stderr))
    return p.stdout.strip()


def prereg(base, counter=None, pop=None, control="census/control.txt", target="items=2 corrected=2",
           kill="any uncorrected", header="## C1 — witness", round_="41", extra=()):
    counter = "census/c1.py sha256=%s" % sha(COUNTER) if counter is None else counter
    pop = "census/pop.tsv sha256=%s" % sha(POP) if pop is None else pop
    lines = ["# prereg", "Round: %s" % round_, "", header, "Base: %s" % base, "Counter: %s" % counter,
             "Population: %s" % pop, "Control: %s" % control, "Target: %s" % target, "Kill: %s" % kill]
    lines += list(extra)
    return "\n".join(lines) + "\n"


def prereg_at(i, ctext=COUNTER, ptext=POP, **kw):
    return lambda s: prereg(s[i], counter="census/c1.py sha256=%s" % sha(ctext),
                            pop="census/pop.tsv sha256=%s" % sha(ptext), **kw)


def census(c=COUNTER, p=POP, ctl=CTRL):
    return {"census/c1.py": c, "census/pop.tsv": p, "census/control.txt": ctl}


def freeze(i=0, c=COUNTER, p=POP, ctl=CTRL, **kw):
    files = census(c, p, ctl)
    files["prereg.txt"] = prereg_at(i, c, p, **kw)
    return files


def make(wid, steps):
    d = os.path.join(SCR, "probe-" + wid)
    os.makedirs(d)
    subprocess.run(["git", "-C", d, "init", "-q", "-b", "main"], env=GENV, check=True)
    if os.path.realpath(git(d, "rev-parse", "--show-toplevel")) != os.path.realpath(d):
        raise SystemExit("fixture toplevel mismatch: %s" % d)
    shas = []
    for files in steps:
        for rel, val in files.items():
            full = os.path.join(d, rel)
            if val is None:
                os.remove(full)
                continue
            text = val(shas) if callable(val) else val
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as handle:
                handle.write(text)
        git(d, "add", "-A")
        git(d, "commit", "-q", "--allow-empty", "-m", "step %d" % len(shas))
        shas.append(git(d, "rev-parse", "HEAD"))
    return d, shas


def run(tool, root, rev, prereg_path):
    p = subprocess.run(["python3", "-B", tool, "--root", root, "--prereg", prereg_path, "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=os.environ, check=False)
    rows = [x for x in p.stdout.splitlines() if x.startswith(("FINDING", "SUMMARY"))]
    err = p.stderr.strip().splitlines()
    return "rc=%d | %s | stderr: %s" % (p.returncode, " ; ".join(rows) or "-", err[-1] if err else "-")


def show(wid, mid, steps, rev="last", root=None, prereg_path="prereg.txt"):
    d, s = make(wid, steps)
    rv = s[-1] if rev == "last" else rev
    rt = d if root is None else root
    out = ["W %s (mutant %s)" % (wid, mid or "-"), "  baseline: " + run(BASE, rt, rv, prereg_path)]
    if mid:
        out.append("  %-8s: %s" % (mid, run(MUT(mid), rt, rv, prereg_path)))
    print("\n".join(out))


def main():
    show("w-clean", None, [README, freeze()])
    show("w-m06", "M06", [README, freeze(kill="")])
    show("w-m10", "M10", [README, {**census(), "prereg.txt": lambda s: prereg("HEAD~1")}])
    show("w-m11", "M11", [README, freeze(), {"prereg.txt": prereg_at(1)}])
    show("w-m20", "M20", [README, {**census(), "prereg.txt": lambda s: prereg(s[0], counter="census/c1.py")}])
    show("w-m21", "M21", [README, {**census(), "prereg.txt": lambda s: prereg(s[0], counter="census/c1.py")}])
    show("w-m24", "M24", [README, freeze(p=POP_TWO)])
    show("w-m27", "M27", [README, freeze(p=POP_BLANK)])
    show("w-m28", "M28", [README, freeze(p=POP_ONE), {"census/pop.tsv": POP}])
    show("w-m34", "M34", [README, freeze(ctl=CTRL + "\n")])
    show("w-m36", "M36", [README, {DJ: "{}\n", **freeze()}])
    show("w-m43", "M43", [README, {".ufo/waves/round-41/w1.ready": "ready\n"}, freeze()])
    show("w-m45", "M45", [README, {DJ: "{}\n"}, {DJ: None}, freeze(), {DJ: "{}\n"}])
    show("w-m47", "M47", [README, freeze(), {"prereg.txt": None},
                          {"census/c1.py": COUNTER2, "prereg.txt": prereg_at(0, COUNTER)}])
    show("w-m51", "M51", [README, freeze()], rev="HEAD")
    show("w-m52", "M52", [README, freeze()], root="/nonexistent-root-r41")
    show("w-m53", "M53", [README, freeze()], prereg_path="absent.txt")
    show("w-m54", "M54", [README, freeze()], rev="f" * 40)
    show("w-m58", "M58", [README, freeze(extra=("Base: " + "0" * 40,))])
    show("w-m59", "M59", [README, freeze(header="## C1x — witness")])
    show("p-blank-base", None, [README, {**census(), "prereg.txt": lambda s: prereg("")}])
    show("p-blank-counter", None, [README, {**census(), "prereg.txt": lambda s: prereg(s[0], counter="")}])
    show("p-blank-pop", None, [README, {**census(), "prereg.txt": lambda s: prereg(s[0], pop="")}])
    show("p-blank-control", None, [README, {**census(), "prereg.txt": lambda s: prereg(s[0], control="")}])
    show("p-edit-after-freeze", None, [README, freeze(), {"prereg.txt": prereg_at(0, target="items=2 corrected=9")}])
    show("p-dispatch-no-round", None, [README, {DJ: "{}\n"}, freeze(round_="x")])
    return 0


if __name__ == "__main__":
    sys.exit(main())
