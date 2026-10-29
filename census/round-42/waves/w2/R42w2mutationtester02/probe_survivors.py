#!/usr/bin/env python3
"""R42w2mutationtester02 - probe the SURVIVING mutants against targeted scenarios the frozen
counter does not cover, to separate behaviour-equivalent mutants from real coverage gaps.

Every scenario builds a synthetic git repo under the scratch root and runs the pristine tool
and the named mutant over it; only the two tools' stdout/exit are compared.
"""
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
REV = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
SEAT = os.path.join(LANE, ".ufo/waves/round-42/w2/R42w2mutationtester02")
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester02/probe"
GIT_ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_AUTHOR_NAME": "fixture",
           "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
           "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}


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
    return p.returncode, p.stdout.strip().replace("\n", " | ")


def scenario(name, build, tools, rev=None, prereg="prereg.txt"):
    """build(d) -> None; returns (name, {tool: (rc, out)})"""
    d = os.path.join(SCRATCH, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    git(d, "init", "-q", "-b", "main", d)
    build(d)
    r = rev or git(d, "rev-parse", "HEAD")
    out = {}
    for label, path in tools.items():
        rc, so = run(path, d, r, prereg)
        out[label] = (rc, so)
    print("### %s" % name)
    for label, (rc, so) in out.items():
        print("  %-10s rc=%d  %s" % (label, rc, so))
    return out


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
        git(d, "add", "-A")
        git(d, "commit", "-qm", "seed")
        return git(d, "rev-parse", "HEAD")

    SHA_C = "a3a5e715f0cc574a73c3f9bebb6bc24f32ffd5b67b387244c2c909da779a1478"  # "c\n"
    SHA_P = "bc0405cffdbb957b8790ce8d5ced0091b4d0b2f32bee8f8a5ffc143032bda4f8"  # "h\nr\n"

    # --- A: duplicated Base whose FIRST occurrence is unresolvable, second is good.
    def a(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % ("0" * 40, b0, SHA_C, SHA_P))
        mk(d)
    scenario("A-dup-base-first-bogus", a, {"pristine": pristine, "M08": M("M08-dup-key-still-evaluated")})

    # --- B: Base is a symbolic name, not a full 40-hex id.
    def b(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: main\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (SHA_C, SHA_P))
        mk(d)
    scenario("B-base-not-hex", b, {"pristine": pristine, "M29": M("M29-base-commit-no-full40")})

    # --- C: Counter path is a regular file at FREEZE and a symlink at REV.
    def c(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C, SHA_P))
        mk(d)
        os.remove(os.path.join(d, "c.py"))
        os.symlink("p.tsv", os.path.join(d, "c.py"))
        mk(d)
    scenario("C-symlink-only-at-rev", c, {"pristine": pristine, "M12": M("M12-symlink-at-rev-not-freeze")})

    # --- D: a dispatch-named file added before the freeze, deleted, then re-added after it.
    def d_(d):
        b0 = base(d)
        write(d, ".ufo/waves/round-7/w1-spec.json", "{}\n")
        mk(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C, SHA_P))
        mk(d)
        os.remove(os.path.join(d, ".ufo/waves/round-7/w1-spec.json"))
        mk(d)
        write(d, ".ufo/waves/round-7/w1-spec.json", "{}\nagain\n")
        mk(d)
    scenario("D-dispatch-readded-after-freeze", d_,
             {"pristine": pristine, "M21": M("M21-dispatch-first-setdefault")})

    # --- E: a heading that starts with C but carries no digit.
    def e(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              "\n## Claim notes\n"
              % (b0, SHA_C, SHA_P))
        mk(d)
    scenario("E-heading-no-digit", e, {"pristine": pristine, "M03": M("M03-badhead-digit-optional")})

    # --- F: an indented key line.
    def f(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\n"
              "    Target: t\nKill: k\n" % (b0, SHA_C, SHA_P))
        mk(d)
    scenario("F-indented-key", f, {"pristine": pristine, "M05": M("M05-keyline-allow-indent")})

    # --- G: trailing whitespace after a key value.
    def g(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s   \n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C, SHA_P))
        mk(d)
    scenario("G-trailing-space-value", g, {"pristine": pristine, "M44": M("M44-keyline-trailing-space-kept")})

    # --- H: a population file with one content line and one blank line.
    def h(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\n\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        sha_p = "82a2d0dc5ad56ed79f1960f9eefc350cb63487e0642b7d2d88575927d9edd551"
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C, sha_p))
        mk(d)
    scenario("H-population-one-line-one-blank", h,
             {"pristine": pristine, "M45": M("M45-population-blank-counted")})

    # --- I: a preregistration with no Round line at all.
    def i(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C, SHA_P))
        mk(d)
    scenario("I-no-round-line", i, {"pristine": pristine, "M23": M("M23-dispatch-missing-round-silent")})

    # --- J: the control receipt is red at FREEZE and green at REV.
    def j(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C, SHA_P))
        mk(d)
        write(d, "ctl.txt", "x\nEXIT=0\n")
        mk(d)
    scenario("J-control-changed-after-freeze", j, {"pristine": pristine, "M36": M("M36-control-at-rev")})

    # --- K: a Counter path containing a space.
    def k(d):
        b0 = base(d)
        write(d, "my counter.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: my counter.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C, SHA_P))
        mk(d)
    scenario("K-counter-path-with-space", k, {"pristine": pristine, "M37": M("M37-path-sha-no-spaces")})

    # --- L: an uppercase sha256 in the preregistration.
    def l(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C.upper(), SHA_P))
        mk(d)
    scenario("L-uppercase-digest", l, {"pristine": pristine, "M38": M("M38-path-sha-uppercase-hex")})

    # --- M: a Counter value with no sha256= at all.
    def m_(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_P))
        mk(d)
    scenario("M-counter-without-sha256", m_, {"pristine": pristine, "M40": M("M40-no-sha256-not-reported")})

    # --- N: dispatch-named file in a directory whose NAME contains '-dispatch'.
    def n_(d):
        b0 = base(d)
        write(d, ".ufo/waves/round-7/-dispatch-dir/notes.md", "x\n")
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C, SHA_P))
        mk(d)
    scenario("N-dispatch-in-dirname", n_, {"pristine": pristine, "M18": M("M18-dispatch-name-is-full-path")})

    # --- O: two claims, the second one duplicated.
    def o(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        b1 = b0
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              "\n## C2\nBase: %s\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b1, SHA_C, SHA_P, b1, "0" * 40, SHA_C, SHA_P))
        mk(d)
    scenario("O-two-claims-second-dup", o,
             {"pristine": pristine, "M09": M("M09-dup-unsorted"), "M08": M("M08-dup-key-still-evaluated")})

    # --- P: the dispatch pathspec without a trailing slash still matches nested files.
    def p_(d):
        b0 = base(d)
        write(d, ".ufo/waves/round-7/deep/nested/w1-spec.json", "{}\n")
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C, SHA_P))
        mk(d)
    scenario("P-nested-dispatch", p_, {"pristine": pristine, "M22": M("M22-dispatch-tree-no-slash")})

    # --- Q: symlink mode prefix without the trailing space.
    def q(d):
        b0 = base(d)
        write(d, "real.py", "c\n")
        os.symlink("real.py", os.path.join(d, "c.py"))
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C, SHA_P))
        mk(d)
    scenario("Q-symlink-mode-prefix", q, {"pristine": pristine, "M10": M("M10-symlink-mode-no-space")})

    # --- R: the dispatch file IS the freeze commit itself.
    def r_(d):
        b0 = base(d)
        write(d, "c.py", "c\n")
        write(d, "p.tsv", "h\nr\n")
        write(d, "ctl.txt", "x\nEXIT=1\n")
        write(d, ".ufo/waves/round-7/w1-spec.json", "{}\n")
        write(d, "prereg.txt", "Round: 7\n## C1\nBase: %s\n"
              "Counter: c.py sha256=%s\nPopulation: p.tsv sha256=%s\nControl: ctl.txt\nTarget: t\nKill: k\n"
              % (b0, SHA_C, SHA_P))
        mk(d)
    scenario("R-dispatch-is-freeze-commit", r_,
             {"pristine": pristine, "M20": M("M20-dispatch-ancestor-only")})

    # --- S: the selftest exception and expectation mutants, observed on a broken selftest.
    for label, mut in (("M51", M("M51-selftest-exception-passes")),
                       ("M54", M("M54-selftest-expectation-ignored"))):
        for tool_label, tool in (("pristine", pristine), (label, mut)):
            p = subprocess.run(["python3", "-B", tool, "--selftest"], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, check=False, env=GIT_ENV, timeout=600)
            print("### S-selftest %s rc=%d out=%r" % (tool_label, p.returncode, p.stdout.strip()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
