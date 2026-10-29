#!/usr/bin/env python3
"""R42w2mutationtester02 - part-B mutants (lines >= 188) of tools/souji-freeze-check.py.

Same contract as gen_mutants.py: one string replacement per mutant, occurrence count
asserted to be exactly 1, output under the seat's mutants/ dir.
"""
import os
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
REV = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mutants")

MUTANTS = [
    # ---- evaluate(): duplicate keys and field emptiness
    ("N01-dup-key-becomes-empty",
     "the duplicated key is blanked instead of deleted: the key is still evaluated (and now empty)",
     '        for key in dups:\n            del f[key]  # ambiguous: reported above, not evaluated\n',
     '        for key in dups:\n            f[key] = ""\n'),
    ("N02-field-empty-skips-kill",
     "the FIELD-EMPTY loop stops before the Kill key",
     '        for key in KEYS:\n            if key in f and not f[key]:',
     '        for key in KEYS[:5]:\n            if key in f and not f[key]:'),
    # ---- evaluate(): Base
    ("N03-base-unresolved-class",
     "the BASE-UNRESOLVED class is renamed",
     'found.append((label, "BASE-UNRESOLVED", base))',
     'found.append((label, "BASE-MISSING", base))'),
    ("N04-base-not-ancestor-class",
     "the BASE-NOT-ANCESTOR class is renamed",
     'found.append((label, "BASE-NOT-ANCESTOR", "%s is not a strict ancestor of freeze %s"',
     'found.append((label, "BASE-NOT-ANCESTOR-X", "%s is not a strict ancestor of freeze %s"'),
    ("N05-base-unresolved-detail",
     "the BASE-UNRESOLVED detail loses the offending value",
     'found.append((label, "BASE-UNRESOLVED", base))',
     'found.append((label, "BASE-UNRESOLVED", ""))'),
    ("N06-base-not-ancestor-detail",
     "the BASE-NOT-ANCESTOR detail loses the word 'strict'",
     '"%s is not a strict ancestor of freeze %s"',
     '"%s is not an ancestor of freeze %s"'),
    # ---- evaluate(): Population
    ("N07-population-never-read",
     "the Population path is never checked: POPULATION-* findings disappear",
     '            got = check_path_sha(repo, rev, freeze, label, "Population", f["Population"],\n'
     '                                 "POPULATION-MISSING", "POPULATION-DIGEST", found)\n',
     '            got = None\n'),
    ("N08-population-empty-too-many-lines",
     "a population with more than 100 lines is also reported empty",
     '                if len(lines) < 2:',
     '                if len(lines) < 2 or len(lines) > 100:'),
    # ---- evaluate(): Control
    ("N09-control-exit-gt-zero",
     "a control receipt with EXIT=-1 is no longer read as red",
     'if not (m and int(m.group(1)) != 0):',
     'if not (m and int(m.group(1)) > 0):'),
    ("N10-control-missing-detail",
     "the CONTROL-MISSING detail loses the path and revision",
     'found.append((label, "CONTROL-MISSING", "%s not present at freeze %s" % (path, freeze[:12])))',
     'found.append((label, "CONTROL-MISSING", "control missing"))'),
    # ---- evaluate(): dispatch leg and claim scan
    ("N11-dispatch-leg-no-round",
     "the dispatch leg is fed an empty text: a missing Round line is always reported",
     '    found.extend(dispatch_findings(repo, rev, freeze, text))',
     '    found.extend(dispatch_findings(repo, rev, freeze, ""))'),
    ("N12-heading-malformed-never",
     "the malformed-heading list is discarded: HEADING-MALFORMED disappears",
     '    claims, bad = parse_claims(text)',
     '    claims, bad = parse_claims(text), []'),
    ("N13-no-claims-never",
     "the NO-CLAIMS finding is never raised",
     '    if not claims:\n        found.append(("C0", "NO-CLAIMS", "no \'## C<digits>\' block in %s" % prereg))\n',
     '    if False:\n        found.append(("C0", "NO-CLAIMS", "no \'## C<digits>\' block in %s" % prereg))\n'),
    # ---- the --selftest fixtures and helpers
    ("N14-sha-p-literal-wrong",
     "the population fixture digest literal is wrong",
     'SHA_P = "bc0405cffdbb957b8790ce8d5ced0091b4d0b2f32bee8f8a5ffc143032bda4f8"  # "h\\nr\\n"',
     'SHA_P = "cc0405cffdbb957b8790ce8d5ced0091b4d0b2f32bee8f8a5ffc143032bda4f8"  # "h\\nr\\n"'),
    ("N15-sha-p1-literal-wrong",
     "the one-line population fixture digest literal is wrong",
     'SHA_P1 = "91ee5e9f42ba3d34e414443b36a27b797a56a47aad6bb1e4c1769e69c77ce0ca"  # "h\\n"',
     'SHA_P1 = "81ee5e9f42ba3d34e414443b36a27b797a56a47aad6bb1e4c1769e69c77ce0ca"  # "h\\n"'),
    ("N16-spec-path-wrong",
     "the self-test's dispatch marker path is wrong",
     'SPEC = ".ufo/waves/round-7/w1-spec.json"',
     'SPEC = ".ufo/waves/round-7/w1-spec.jsonx"'),
    ("N17-prereg-format-glues-keys",
     "the synthetic preregistration glues the key lines onto the heading line",
     'return "Round: 7\\n%s\\n%s%s" % (head,',
     'return "Round: 7\\n%s%s%s" % (head,'),
    ("N18-prereg-no-kill-key",
     "the synthetic preregistration has no Kill key",
     '             Control="ctl.txt", Target="t", Kill="k")',
     '             Control="ctl.txt", Target="t")'),
    # ---- the --selftest case table
    ("N19-selftest-case-counter-symlink-dropped",
     "the self-test drops its counter-symlink case (cases=30)",
     '    ("counter-symlink", 1, "C1:COUNTER-SYMLINK", prereg(), {"fz": {"c.py": ("x",)}}),\n',
     ''),
    ("N20-selftest-case-population-empty-dropped",
     "the self-test drops its population-empty case (cases=30)",
     '    ("population-empty", 1, "C1:POPULATION-EMPTY", prereg(Population="p.tsv sha256=" + SHA_P1),\n'
     '     {"fz": {"p.tsv": "h\\n"}}),\n',
     ''),
    # ---- selftest_case(): repository construction
    ("N21-selftest-no-committer-identity",
     "the self-test's git environment has no committer identity: every commit fails",
     '           "GIT_COMMITTER_NAME": "st", "GIT_COMMITTER_EMAIL": "st@example.invalid"}',
     '           "GIT_COMMITTER_EMAIL": "st@example.invalid"}'),
    ("N22-selftest-prereg-filename-wrong",
     "the self-test looks for a preregistration file name that is never committed",
     'def selftest_case(tmp, n, code, want, text, pre=None, fz=None, post=None, rev=None, path="pre.txt"):',
     'def selftest_case(tmp, n, code, want, text, pre=None, fz=None, post=None, rev=None, path="prereg.txt"):'),
    ("N23-selftest-rev-override-ignored",
     "the self-test ignores the per-case --rev override",
     'rev or git("rev-parse", "HEAD")',
     'git("rev-parse", "HEAD")'),
    ("N24-selftest-pre-files-not-committed",
     "the self-test does not commit the pre-freeze files",
     '    base = commit({"a": "a", **(pre or {})})',
     '    base = commit({"a": "a"})'),
    ("N25-selftest-symlink-not-created",
     "the self-test writes a symlink case as a regular file",
     '            if isinstance(c, tuple):\n                os.symlink(c[0], fp)\n',
     '            if isinstance(c, tuple):\n                with open(fp, "w") as fh:\n                    fh.write(c[0])\n'),
    # ---- selftest(): accounting and output
    ("N26-selftest-pass-count-always",
     "the self-test counts every case as a pass",
     '            passed += ok',
     '            passed += 1'),
    ("N27-selftest-pass-fail-swapped",
     "the self-test prints its pass and fail counts swapped",
     'print("SELFTEST cases=%d pass=%d fail=%d" % (len(CASES), passed, len(CASES) - passed))',
     'print("SELFTEST cases=%d pass=%d fail=%d" % (len(CASES), len(CASES) - passed, passed))'),
    ("N28-selftest-expectations-never-compared",
     "the self-test collects no findings, so its expectations are never compared",
     '    got = sorted("%s:%s" % tuple(x.split()[1:3]) for x in out.getvalue().splitlines() if x.startswith("FINDING "))\n',
     '    got = []\n'),
    # ---- main(): CLI, refusal contract, output
    ("N29-main-selftest-mode-short-circuits",
     "--selftest returns 0 without running the self-test",
     '    if args.selftest:\n        return selftest()\n',
     '    if args.selftest:\n        return 0\n'),
    ("N30-main-findings-unsorted",
     "the FINDING lines are printed in discovery order, not sorted",
     '    lines = sorted("FINDING %s %s %s" % f for f in found)',
     '    lines = ["FINDING %s %s %s" % f for f in found]'),
    ("N31-main-exit-only-when-two-findings",
     "the tool exits 0 when exactly one finding is reported",
     '    return 1 if lines else 0',
     '    return 1 if len(lines) > 1 else 0'),
    ("N32-main-refusal-detail-lost",
     "the refusal message loses the revision and root",
     'raise Refusal("--rev %s does not resolve to a commit in %s" % (args.rev, args.root))',
     'raise Refusal("--rev does not resolve")'),
    ("N33-main-rev-format-not-checked",
     "--rev is not checked for the full 40-hex form",
     '        if not FULL40.match(args.rev):\n            raise Refusal("--rev must be a full 40-hex commit id")\n',
     '        if False:\n            raise Refusal("--rev must be a full 40-hex commit id")\n'),
]


def main():
    src = subprocess.run(["git", "-C", LANE, "show", "%s:tools/souji-freeze-check.py" % REV],
                         stdout=subprocess.PIPE, check=True).stdout.decode("utf-8")
    os.makedirs(OUT, exist_ok=True)
    for name, desc, old, new in MUTANTS:
        n = src.count(old)
        if n != 1:
            sys.stderr.write("MUTANT %s: pattern occurs %d times, expected 1\n" % (name, n))
            return 2
        mutant = src.replace(old, new)
        path = os.path.join(OUT, name + ".py")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(mutant)
        try:
            compile(mutant, path, "exec")
        except SyntaxError as exc:
            sys.stderr.write("MUTANT %s: syntax error %s\n" % (name, exc))
            return 2
    with open(os.path.join(OUT, "INDEX-partB.tsv"), "w", encoding="utf-8") as fh:
        fh.write("name\tdescription\n")
        for name, desc, _o, _n in MUTANTS:
            fh.write("%s\t%s\n" % (name, desc))
    print("wrote %d part-B mutants into %s" % (len(MUTANTS), OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
