#!/usr/bin/env python3
"""Scratch generator: derives attack variants from the honest K1 candidate. Writes only into the seat dir."""
import importlib.util
import pathlib
import sys

SEAT = pathlib.Path("/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w1/R42critic02")
K1 = (SEAT / "K1-honest-grammar.py").read_text(encoding="utf-8")
head, rest = K1.split("def selftest():", 1)
_st, main_part = rest.split("def main(argv):", 1)
SELF_PRINT = 'print("SELFTEST cases=15 pass=15 fail=0")'


def with_selftest(body, note):
    src = head + "def selftest():\n" + body.rstrip("\n") + "\n\n\ndef main(argv):" + main_part
    return src.replace('"""tools/souji-freeze-check.py - the pre-dispatch freeze checklist as one command.',
                       '"""%s\n\ntools/souji-freeze-check.py - the pre-dispatch freeze checklist as one command.' % note, 1)


# K2: grammar honest, self-test prints a literal summary and checks nothing; it detects only the sitecustomize env.
K2 = with_selftest(
    "    # literal summary: runs no case\n"
    "    " + SELF_PRINT + "\n"
    "    return 1 if os.environ.get('PYTHONPATH') else 0\n",
    "ATTACK K2 (not an implementation): grammar of K1; --selftest prints a literal summary and detects the PYTHONPATH the counter's patch legs set.")

# K3: grammar honest; self-test refuses when the stdlib functions it uses are not the originals. Runs no case.
K3 = with_selftest(
    "    # identity guard: refuses when hashlib.sha256 or subprocess.run is not the stdlib original\n"
    "    if hashlib.sha256.__module__ != '_hashlib' or subprocess.run.__module__ != 'subprocess':\n"
    "        return 1\n"
    "    " + SELF_PRINT + "\n"
    "    return 0\n",
    "ATTACK K3 (not an implementation): grammar of K1; --selftest is an identity guard on two stdlib functions and runs no case.")

# K4: grammar honest; self-test crashes (AssertionError) when patched. A crash is what the counter counts as rejection.
K4 = with_selftest(
    "    " + SELF_PRINT + "\n"
    "    assert not os.environ.get('PYTHONPATH'), 'interpreter environment not pristine'\n"
    "    return 0\n",
    "ATTACK K4 (not an implementation): grammar of K1; --selftest prints a literal summary and the patch detection is an assert that crashes.")

# K6: sensitivity control: K1 with the KEY-DUPLICATE rule deleted; the counter must go red.
needle = '                found.append((label, "KEY-DUPLICATE", key))'
assert K1.count(needle) == 1, K1.count(needle)
K6 = K1.replace(needle, "                pass  # rule deleted (sensitivity control)")
K6 = K6.replace('"""tools/souji-freeze-check.py', '"""ATTACK-SENSITIVITY K6: K1 minus KEY-DUPLICATE.\n\ntools/souji-freeze-check.py', 1)

# K5: no grammar at all. Answers from the basename of --root (the counter names its synthetic repos cand-<case>)
# and from a copy of the counter's case expectations.
spec = importlib.util.spec_from_file_location("c2", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/c2-counter.py")
c2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c2)
rows = []
for name, _mut, rc, want in c2.CASES:
    rows.append("    %r: (%d, %r)," % (name, rc, sorted(want)))
table = "\n".join(rows)
K5 = '''#!/usr/bin/env python3
"""ATTACK K5 (not an implementation): no grammar. Answers each synthetic case from the basename of --root
(the counter builds cand-<case>) through a table copied from the counter's CASES, and answers the real,
retro and retro_clean legs from the --prereg path."""
import argparse
import os
import sys

CASE_TABLE = {
%s
}
# (claims, findings) for the three prereg files the counter reads from the lane
CANNED = {
    "census/round-42/preregistration.txt": (3, 0, 0, []),
    "census/round-40/preregistration.txt": (3, 19, 1, [("C0", "CANNED")] * 19),
    "census/round-41/preregistration.txt": (3, 0, 0, []),
}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--prereg")
    ap.add_argument("--rev")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        print("SELFTEST cases=15 pass=15 fail=0")
        return 1 if os.environ.get("PYTHONPATH") else 0
    if args.rev == "f" * 40 or args.prereg == "absent.txt":
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: canned\\n")
        return 2
    name = os.path.basename(os.path.normpath(args.root))
    if name.startswith("cand-"):
        rc, findings = CASE_TABLE.get(name[len("cand-"):], (0, []))
        claims = 1
    else:
        claims, count, rc, findings = CANNED.get(args.prereg, (0, 0, 0, []))
    for label, cls in findings:
        print("FINDING %%s %%s canned" %% (label, cls))
    print("SUMMARY claims=%%d findings=%%d" %% (claims if name.startswith("cand-") else claims, len(findings)))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
''' % table

for fname, text in (("K2-literal-selftest.py", K2), ("K3-identity-selftest.py", K3),
                    ("K4-assert-crash-selftest.py", K4), ("K5-dirname-table.py", K5),
                    ("K6-no-keydup.py", K6)):
    (SEAT / fname).write_text(text, encoding="utf-8")
    print("wrote", fname, len(text))
