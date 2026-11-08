#!/usr/bin/env python3
"""S88Simplifier: differential check of _one_line / _stderr_tail between the lane tool and the two dedupe variants."""
import importlib.util
import os
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-record-agreement.py"
HERE = os.path.dirname(os.path.abspath(__file__))
CASES = [
    "", " ", "  \t ", "\n", "\r\n", "\n\n", "  x  ", "x",
    "fatal: cannot read index\n",
    "Traceback (most recent call last):\n  File \"w\", line 1\nAttributeError: boom\n",
    "AttributeError: " + "x" * 380 + "\n",
    "fatal: \x01 \x85 \u2028 marker\n",
    "a" * 100, "a" * 199, "a" * 200, "a" * 201, "a" * 400,
    "\\n", "\\", "\\\\", "\u2028", "x\u2029y", "\x7f", "\x00",
    "  " + "b" * 300 + "  ",
]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    old = load(LANE, "old")
    both = load(HERE + "/tool-both-ends.py", "both")
    deleg = load(HERE + "/tool-delegate.py", "deleg")
    bad = 0
    for label, mod in (("both_ends", both), ("delegate", deleg)):
        for i, s in enumerate(CASES):
            a, b = old._one_line(s), mod._one_line(s)
            if a != b:
                bad += 1
                print(f"DIFF {label} case={i} in={s!r:.60} old={a!r:.120} new={b!r:.120}")
        for i, s in enumerate(CASES):
            a, b = old._stderr_tail(s), mod._stderr_tail(s)
            if a != b:
                bad += 1
                print(f"DIFF {label} stderr_tail case={i} in={s!r:.60} old={a!r:.120} new={b!r:.120}")
    # the bound itself: head-100 / ellipsis / tail-99 at 200
    for mod, name in ((old, "old"), (both, "both"), (deleg, "delegate")):
        s = "H" * 150 + "T" * 150
        out = mod._one_line(s)
        ok = len(out) == 200 and out[:100] == "H" * 100 and out[100] == "\u2026" and out[-99:] == "T" * 99
        print(f"BOUND {name} len={len(out)} head100={'yes' if out[:100] == 'H' * 100 else 'no'} "
              f"ellipsis={'yes' if out[100] == chr(0x2026) else 'no'} tail99={'yes' if out[-99:] == 'T' * 99 else 'no'} ok={ok}")
        if not ok:
            bad += 1
    print(f"DIFFS total={bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
