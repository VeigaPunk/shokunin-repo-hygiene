#!/usr/bin/env python3
"""Scratch driver (R40w2simplifier03): leave-one-case-out kill matrix for the landed C3 fixture.

Reads the landed bytes extracted from 128e412b into $S/landed (read-only use), imports the fixture
and counter as modules, and runs the fixture's own run_cases with optional case filtering.
Writes only under $S.
"""
import importlib.util
import os
import sys

sys.dont_write_bytecode = True
S = "/fast/scratch/hyaku/souji-r40/w2/R40w2simplifier03"
L = S + "/landed"
WORK = S + "/work"
os.makedirs(WORK, exist_ok=True)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fx = load("fx", L + "/tests/fixtures/r40-drift-record-branches.py")
c3 = load("c3", L + "/census/round-40/c3-counter.py")
src = open(L + "/tools/souji-worktree-drift.py", encoding="utf-8").read()

mutants = {}
for mid, old, new in c3.MUTANTS:
    assert src.count(old) == 1, mid
    mutants[mid] = src.replace(old, new)


def sub(mid, old, new):
    assert src.count(old) == 1, mid
    mutants[mid] = src.replace(old, new)


# Undeclared probes: each models one behaviour the fixture's docstring claims to cover.
sub("P1-inverted-skip", c3.SKIP_GUARD, "    if args.skip_unrecorded:")
sub("P2-strict-decode", c3.DECODE, c3.DECODE.replace('"replace"', '"strict"'))
sub("P3-refuse-any-second-total", c3.TOTAL_ASSIGN,
    '            if total is not None:\n'
    '                raise Refusal("RECORD-MALFORMED: second TOTAL")\n' + c3.TOTAL_ASSIGN)
sub("P6-never-scan", c3.SKIP_GUARD, "    if False:")
mutants["P7-tool-always-raises"] = "raise RuntimeError('probe')\n" + src

CASES = ["good", "total-duplicate-identical", "total-conflicting-second", "total-repos-disagrees",
         "skip-unrecorded-suppresses", "unrecorded-without-flag", "invalid-utf8-in-repo-name",
         "invalid-utf8-in-comment"]


def run(label, text, skip=()):
    path = os.path.join(WORK, "tool-" + label + ".py")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    os.chmod(path, 0o755)
    orig = fx.run_record

    def filt(tool, root, path_, body, name, want_rc, want_tokens, results, binary=False,
             extra=None):
        if name in skip:
            return None
        return orig(tool, root, path_, body, name, want_rc, want_tokens, results,
                    binary=binary, extra=extra)

    fx.run_record = filt
    try:
        res = fx.run_cases(path, WORK)
    except Exception as exc:  # fixture itself raised: not a scored kill
        return "EXC(%s)" % type(exc).__name__, ["<exception>"]
    finally:
        fx.run_record = orig
    failing = [name for name, ok, _ in res if not ok]
    return ("KILLED" if failing else "SURVIVED"), failing


print("CASES_IN_FULL_FIXTURE=%d names=%s" % (len(CASES), ",".join(CASES)))
print("== full fixture, pristine tool")
status, failing = run("pristine", src)
print("pristine: %s failing=%s" % (status, failing))

print("== full fixture, every mutant")
full = {}
for mid in sorted(mutants):
    status, failing = run(mid, mutants[mid])
    full[mid] = (status, tuple(failing))
    print("%-28s %-9s failing=%s" % (mid, status, ",".join(failing) or "-"))

print("== leave-one-case-out: kill status per mutant (CHANGED marks a difference from full)")
for case in CASES:
    p_status, p_fail = run("pristine-loo", src, skip=(case,))
    row = []
    changed = []
    for mid in sorted(mutants):
        status, failing = run("loo-" + mid, mutants[mid], skip=(case,))
        row.append("%s=%s" % (mid, "K" if status == "KILLED" else ("S" if status == "SURVIVED" else status)))
        if status != full[mid][0]:
            changed.append("%s:%s->%s" % (mid, full[mid][0], status))
    print("drop %-28s pristine=%s pristine_fail=%s" % (case, p_status, ",".join(p_fail) or "-"))
    print("    kills: %s" % " ".join(row))
    print("    kill-status changes vs full: %s" % (", ".join(changed) or "none"))
