#!/usr/bin/env python3
"""R42w2mutationtester02 - behavioural probes for the surviving part-B mutants.

Each scenario builds a synthetic git repo under the scratch root and runs the pristine
tool and the named mutant over it, so that a survivor can be classified as
behaviour-equivalent or as a real coverage gap.
"""
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
REV = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
SEAT = os.path.join(LANE, ".ufo/waves/round-42/w2/R42w2mutationtester02")
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester02/probeB"
GIT_ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_AUTHOR_NAME": "fixture",
           "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
           "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}
SHA_C = "a3a5e715f0cc574a73c3f9bebb6bc24f32ffd5b67b387244c2c909da779a1478"
SHA_P = "bc0405cffdbb957b8790ce8d5ced0091b4d0b2f32bee8f8a5ffc143032bda4f8"


def git(d, *a):
    p = subprocess.run(["git", "-C", d] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=GIT_ENV, check=True, text=True)
    return p.stdout.strip()


def write(d, rel, text):
    full = os.path.join(d, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(text)


def run(tool, d, rev, prereg):
    p = subprocess.run(["python3", "-B", tool, "--root", d, "--prereg", prereg, "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
                       env=GIT_ENV, timeout=300)
    return p.returncode, p.stdout.strip().replace("\n", " | "), p.stderr.strip().replace("\n", " | ")


def scenario(name, build, tools, rev=None, prereg="prereg.txt"):
    d = os.path.join(SCRATCH, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    git(d, "init", "-q", "-b", "main", d)
    build(d)
    r = rev or git(d, "rev-parse", "HEAD")
    print("### %s" % name)
    for label, path in tools.items():
        rc, so, se = run(path, d, r, prereg)
        print("  %-10s rc=%d  out=%s%s" % (label, rc, so, ("  err=%s" % se) if se else ""))
    return d


def main():
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH)
    pristine = os.path.join(SCRATCH, "pristine.py")
    with open(pristine, "w", encoding="utf-8") as fh:
        fh.write(subprocess.run(["git", "-C", LANE, "show", "%s:tools/souji-freeze-check.py" % REV],
                                stdout=subprocess.PIPE, check=True).stdout.decode())
    M = lambda n: os.path.join(SEAT, "mutants", n + ".py")

    def mk(d):
        git(d, "add", "-A")
        git(d, "commit", "-qm", "c")

    def base(d):
        write(d, "seed.txt", "seed\n")
        mk(d)
        return git(d, "rev-parse", "HEAD")

    def std(d, prereg_extra="", **files):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C, SHA_P) + prereg_extra)
        mk(d)
        return b0

    # N02: an empty Kill value.
    def a(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill:\n"
              % (b0, SHA_C, SHA_P))
        mk(d)
    scenario("A-empty-Kill", a, {"pristine": pristine, "N02": M("N02-field-empty-skips-kill")})

    # N08: a population with 120 non-blank lines.
    def b(d):
        b0 = base(d)
        import hashlib
        pop = "".join("row%d\n" % i for i in range(120))
        write(d, "c.py", "c\n")
        write(d, "p.tsv", pop)
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C, hashlib.sha256(pop.encode()).hexdigest()))
        mk(d)
    scenario("B-population-120-lines", b, {"pristine": pristine, "N08": M("N08-population-empty-too-many-lines")})

    # N09: a control receipt whose last line is EXIT=-1.
    def c(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=-1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C, SHA_P))
        mk(d)
    scenario("C-control-exit-minus-one", c, {"pristine": pristine, "N09": M("N09-control-exit-gt-zero")})

    # N30: two findings whose sorted order differs from discovery order.
    def d_(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\n"
              "Target: t\nKill: k\n\n## C2\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C, SHA_P, b0, SHA_C, SHA_P))
        mk(d)
    scenario("D-two-claims-order", d_, {"pristine": pristine, "N30": M("N30-main-findings-unsorted")})

    # N33: a --rev that is not 40 hex.
    e = scenario("E-rev-not-hex", lambda d: std(d), {"pristine": pristine, "N33": M("N33-main-rev-format-not-checked")},
                 rev="deadbeef")

    # N19/N20: the --selftest of the mutants that dropped a case.
    for label, mut in (("N19", M("N19-selftest-case-counter-symlink-dropped")),
                       ("N20", M("N20-selftest-case-population-empty-dropped")),
                       ("pristine", pristine)):
        p = subprocess.run(["python3", "-B", mut, "--selftest"], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, check=False, env=GIT_ENV, timeout=600)
        print("### F-selftest %-9s rc=%d out=%r" % (label, p.returncode, p.stdout.strip()))

    # M51/M54: the selftest of the mutants that weaken the self-test itself.
    for label, mut in (("M51", M("M51-selftest-exception-passes")),
                       ("M54", M("M54-selftest-expectation-ignored")),
                       ("pristine", pristine)):
        p = subprocess.run(["python3", "-B", mut, "--selftest"], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, text=True, check=False, env=GIT_ENV, timeout=600)
        print("### G-selftest %-9s rc=%d out=%r" % (label, p.returncode, p.stdout.strip()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
