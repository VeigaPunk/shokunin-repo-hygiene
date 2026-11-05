#!/usr/bin/env python3
"""S60ReviewerFreeze C1 falsification probes (reviewer-owned, scratch only).

  python3 -B build-probes.py --tool PATH --work DIR [--substance]

Builds ONE synthetic git fixture repo under --work (toplevel asserted before the first commit,
throwaway identity, all git calls name -C WORK), commits a freeze containing the Counter/Population
blobs and every attack receipt, then runs the freeze checker once per attack preregistration at the
freeze revision. Prints, per case: the attack id, the EXPECTED verdict for the substance arm, the
observed verdict and the raw FINDING lines. Read-only on the lane.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys

CBYTES = "COUNTER-BYTES-v1\n"          # the declared Counter, c.py
C2BYTES = "COUNTER-TWO-BYTES\n"        # a different instrument, c2.py
DECOYBYTES = "DECOY-COUNTER\n"         # a different instrument, decoy.py
PBYTES = "h\nr\n"                      # Population p.tsv


def sha(b):
    return hashlib.sha256(b.encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--substance", action="store_true")
    args = ap.parse_args()
    tool = os.path.abspath(args.tool)
    work = os.path.abspath(args.work)
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(work)
    env = dict(os.environ, GIT_AUTHOR_NAME="probe", GIT_AUTHOR_EMAIL="p@invalid",
               GIT_COMMITTER_NAME="probe", GIT_COMMITTER_EMAIL="p@invalid",
               GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)

    def g(*a):
        return subprocess.run(["git", "-C", work] + list(a), stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, check=True, env=env).stdout.decode().strip()

    g("init", "-q")
    top = g("rev-parse", "--show-toplevel")
    assert os.path.realpath(top) == os.path.realpath(work), "toplevel %r != fixture %r" % (top, work)

    def write_commit(files, msg):
        for rel, data in files.items():
            fp = os.path.join(work, rel)
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            with open(fp, "wb") as fh:  # binary: fixture digests are over LF bytes
                fh.write(data.encode() if isinstance(data, str) else data)
        g("add", "-A")
        g("commit", "-q", "-m", msg)
        return g("rev-parse", "HEAD")

    base = write_commit({"notes.txt": "base\n"}, "base")
    orphan = g("commit-tree", base + "^{tree}", "-m", "orphan")  # resolves, not an ancestor

    shaC, shaC2, shaD, shaP = sha(CBYTES), sha(C2BYTES), sha(DECOYBYTES), sha(PBYTES)

    def receipt(instr, digest, rev, command, extra=""):
        lines = []
        if instr is not None:
            lines.append("instrument=%s" % instr)
        if digest is not None:
            lines.append("instrument_sha256=%s" % digest)
        if rev is not None:
            lines.append("rev=%s" % rev)
        if command is not None:
            lines.append("command=%s" % command)
        return "\n".join(lines) + ("\n" if lines else "") + extra + "EXIT=1\n"

    def claim(ctl, counter="c.py sha256=" + shaC, extra=None, drop=()):
        k = {"Base": base, "Counter": counter, "Population": "p.tsv sha256=" + shaP,
             "Control": ctl, "Target": "t", "Kill": "k"}
        k.update(extra or {})
        for d in drop:
            k.pop(d, None)
        return k

    def block(head, keys, tail=""):
        out = head + "\n" + "".join("%s: %s\n" % (k, v) for k, v in keys.items())
        return out + tail

    files = {"c.py": CBYTES, "c2.py": C2BYTES, "copy_of_c.py": CBYTES,
             "decoy.py": DECOYBYTES, "xc.py": "XC-OTHER-TOOL\n", "p.tsv": PBYTES}
    # (attack id, expected substance verdict, expected finding class(es), receipts, claim blocks)
    cases = []

    def case(name, expect, classes, receipts, blocks):
        for rel, data in receipts.items():
            files[rel] = data
        cases.append((name, expect, classes, "pre-%s.txt" % name, blocks))

    # (a) kind-only: plausible labels, no instrument/digest/rev lines
    case("a-kindonly", "refuse", "CONTROL-INSTRUMENT-MISSING,CONTROL-REV-MISSING",
         {"ctl-a.txt": "kind=counter-red\nlabel-instrument=c.py\nnote=by-hand\nEXIT=1\n"},
         [block("## C1", claim("ctl-a.txt"))])

    # (b) cross-claim copy: C1's receipt is C2's instrument+digest; C1 Counter is c.py
    case("b-crossclaim", "refuse", "CONTROL-INSTRUMENT-MISMATCH",
         {"ctl-b1.txt": receipt("c2.py", shaC2, base, "python3 -B c2.py"),
          "ctl-b2.txt": receipt("c2.py", shaC2, base, "python3 -B c2.py")},
         [block("## C1", claim("ctl-b1.txt")),
          block("## C2", claim("ctl-b2.txt", counter="c2.py sha256=" + shaC2))])

    # (c) bytes-vs-execution: all lines present and bound, command text never ran the instrument
    case("c-never-executed", "accept-or-refuse-not-repaired", "none (contract says bytes only)",
         {"ctl-c.txt": receipt("c.py", shaC, base, "echo 'pretend: python3 -B c.py'")},
         [block("## C1", claim("ctl-c.txt"))])

    # (d) rename: digest matches byte-identical copy_of_c.py; instrument= names the copy
    case("d-rename-identical", "refuse", "CONTROL-INSTRUMENT-MISMATCH (path must equal Counter path)",
         {"ctl-d.txt": receipt("copy_of_c.py", shaC, base, "python3 -B copy_of_c.py")},
         [block("## C1", claim("ctl-d.txt"))])

    # (e1) fenced decoy AFTER the real Counter: duplicate key
    fence_after = "```sh\nCounter: decoy.py sha256=" + shaD + "\n```\n"
    case("e1-fence-decoy-after", "refuse", "KEY-DUPLICATE (base)",
         {"ctl-e1.txt": receipt("c.py", shaC, base, "python3 -B c.py")},
         [block("## C1", claim("ctl-e1.txt"), fence_after)])

    # (e2) fenced decoy BEFORE, and the real Counter key ABSENT: decoy binds, FIELD-MISSING hidden
    fence_before = "```sh\nCounter: decoy.py sha256=" + shaD + "\n```\n"
    case("e2-fence-decoy-only", "refuse", "FIELD-MISSING-hidden (decoy must not bind)",
         {"ctl-e2.txt": receipt("c.py", shaC, base, "python3 -B c.py")},
         [block("## C1", claim("ctl-e2.txt", drop=("Counter",)), fence_before)])

    # (e3) same as e2 but the receipt is matched to the DECOY instrument: passes substance if the
    #      decoy is bound (the attack that survives a substance arm that trusts the fenced key)
    case("e3-fence-decoy-matched", "refuse", "must refuse: decoy line is not a real key",
         {"ctl-e3.txt": receipt("decoy.py", shaD, base, "python3 -B decoy.py")},
         [block("## C1", claim("ctl-e3.txt", drop=("Counter",)), fence_before)])

    # (e4) indented decoy (column-1 grammar must ignore it): real Counter present
    case("e4-indent-decoy", "accept", "none",
         {"ctl-e4.txt": receipt("c.py", shaC, base, "python3 -B c.py")},
         [block("## C1", claim("ctl-e4.txt"), "    Counter: decoy.py sha256=" + shaD + "\n")])

    # (f) command substring: command names xc.py and merely CONTAINS c.py
    case("f-command-substring", "refuse-or-not-repaired", "CONTROL-COMMAND-MISMATCH only if exact-token",
         {"ctl-f.txt": receipt("c.py", shaC, base, "python3 -B xc.py --flag c.py-enabled")},
         [block("## C1", claim("ctl-f.txt"))])

    # (g) duplicate rev= lines in the receipt: orphan first, real base second
    case("g-duplicate-rev", "refuse", "CONTROL-REV-INVALID (any duplicate rev= refuses)",
         {"ctl-g.txt": receipt("c.py", shaC, orphan, "python3 -B c.py", extra="rev=%s\n" % base)},
         [block("## C1", claim("ctl-g.txt"))])

    # (h) orphan rev: resolves but is not a strict ancestor of freeze
    case("h-orphan-rev", "refuse", "CONTROL-REV-INVALID",
         {"ctl-h.txt": receipt("c.py", shaC, orphan, "python3 -B c.py")},
         [block("## C1", claim("ctl-h.txt"))])

    # (g2) conflicting SECOND rev= after a valid first rev= (first-wins hides the orphan second)
    case("g2-second-rev-conflict", "refuse", "CONTROL-REV-NOT-BEFORE-FREEZE (any conflicting duplicate refuses)",
         {"ctl-g2.txt": receipt("c.py", shaC, base, "python3 -B c.py", extra="rev=%s\n" % orphan)},
         [block("## C1", claim("ctl-g2.txt"))])

    # (g3) conflicting SECOND instrument= (decoy path) after the real first instrument=
    case("g3-second-instrument-conflict", "refuse", "CONTROL-INSTRUMENT-MISMATCH (any conflicting duplicate refuses)",
         {"ctl-g3.txt": receipt("c.py", shaC, base, "python3 -B c.py", extra="instrument=decoy.py\n")},
         [block("## C1", claim("ctl-g3.txt"))])

    # (g4) conflicting SECOND instrument_sha256= (decoy digest) after the real first digest
    case("g4-second-digest-conflict", "refuse", "CONTROL-INSTRUMENT-MISMATCH (any conflicting duplicate refuses)",
         {"ctl-g4.txt": receipt("c.py", shaC, base, "python3 -B c.py", extra="instrument_sha256=%s\n" % shaD)},
         [block("## C1", claim("ctl-g4.txt"))])

    # (i) short rev (39 hex)
    case("i-short-rev", "refuse", "CONTROL-REV-INVALID or MISSING",
         {"ctl-i.txt": receipt("c.py", shaC, "f" * 39, "python3 -B c.py")},
         [block("## C1", claim("ctl-i.txt"))])

    # (j) rev = freeze commit itself: created later, so not a strict ancestor (filled after freeze known)
    # handled below: needs the freeze id, so written after the first commit.

    # (k) honest: full binding, rev is the strict ancestor base
    case("k-honest", "accept", "none",
         {"ctl-k.txt": receipt("c.py", shaC, base, "python3 -B c.py --root . --rev " + base)},
         [block("## C1", claim("ctl-k.txt"))])

    freeze = write_commit(files, "freeze: probes")

    # (j) rev = the freeze commit itself: needs the freeze id, so it is committed afterwards
    # as part of the same freeze? no: a later commit would move FREEZE. Build it into the freeze
    # by pre-computing the freeze id is impossible; instead record it as a rev-at-freeze attack
    # by pointing rev= at the freeze commit in a *second* freeze case committed below.
    jrec = receipt("c.py", shaC, freeze, "python3 -B c.py")
    jblock = block("## C1", claim("ctl-j.txt"))
    files2 = {"ctl-j.txt": jrec, "pre-j.txt": "Round: 60\n\n" + jblock}
    freeze2 = write_commit(files2, "freeze two: rev-at-freeze probe")
    cases.append(("j-rev-at-freeze", "n/a-unconstructible", "CONTROL-REV-NOT-BEFORE-FREEZE (unreachable: a receipt cannot name the commit that contains it)", "pre-j.txt", None))

    argv = [sys.executable, "-B", tool, "--root", work] + (["--substance"] if args.substance else [])
    print("# tool=%s substance=%s base=%s freeze=%s freeze2=%s" % (
        tool, bool(args.substance), base, freeze, freeze2))
    print("# shaC=%s shaC2=%s shaD=%s shaP=%s" % (shaC, shaC2, shaD, shaP))
    rc_all = 0
    for name, expect, classes, path, blocks in cases:
        if blocks is None:
            # j: prereg written at freeze2 (already committed); check at freeze2
            rev = freeze2
        else:
            # per-case prereg committed alone so FREEZE is the commit that adds it
            with open(os.path.join(work, path), "wb") as fh:
                fh.write(("Round: 60\n\n" + "".join(blocks)).encode())
            g("add", "-A")
            g("commit", "-q", "-m", "prereg " + name)
            rev = g("rev-parse", "HEAD")
        p = subprocess.run(argv + ["--prereg", path, "--rev", rev], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, env=env)
        out = p.stdout.decode()
        ref = p.stderr.decode().strip()
        verdict = {0: "accept", 1: "refuse"}.get(p.returncode, "rc%d" % p.returncode)
        print("CASE %s expect=%s observed=%s rc=%d classes=[%s]" % (name, expect, verdict, p.returncode, classes))
        for line in out.splitlines():
            print("  " + line)
        if ref:
            print("  STDERR " + ref)
        if p.returncode not in (0, 1):
            rc_all = 2
    print("DONE rc=%d" % rc_all)
    return rc_all


if __name__ == "__main__":
    sys.exit(main())
