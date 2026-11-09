#!/usr/bin/env python3
"""souji r95 C1 do-nothing control: the FROZEN r94 search (census/round-94/c1-survivor-search.py, its own HOOK,
verdict(), score() and main(): the excepthook-only sentinel and the r94 rule) run unchanged except that its HAND tuple
is extended with the five r95 hand edits, read from census/round-95/c1-survivor-search.py (byte-identical tuples), so
`--ids` can name them. Every other argument passes through. This is what the r94 kill rule says about the r95
targets."""
import importlib.util
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
NEW = ("h-sysexit", "h-atexit", "h-thread", "h-osexit", "h-sigkill")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


r94 = load("r94search", os.path.join(HERE, "..", "round-94", "c1-survivor-search.py"))
r95 = load("r95search", os.path.join(HERE, "c1-survivor-search.py"))
extra = tuple(h for h in r95.HAND if h[0] in NEW)
assert len(extra) == len(NEW)
r94.HAND = r94.HAND + extra
# r94 main() prints its own file's sha256 via __file__ (the r94 search), which is what this control runs
sys.exit(r94.main(sys.argv[1:]))
