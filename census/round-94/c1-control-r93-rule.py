#!/usr/bin/env python3
"""souji r94 C1 do-nothing control: the FROZEN r93 search (census/round-93/c1-survivor-search.py, its own verdict(),
score() and main(), no crash sentinel) run unchanged except that its HAND tuple is extended with the two r94 crash hand
edits, read from census/round-94/c1-survivor-search.py (byte-identical tuples), so `--ids` can name them. Every other
argument passes through. This is what the r93 kill rule says about the r94 targets."""
import importlib.util
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


r93 = load("r93search", os.path.join(HERE, "..", "round-93", "c1-survivor-search.py"))
r94 = load("r94search", os.path.join(HERE, "c1-survivor-search.py"))
extra = tuple(h for h in r94.HAND if h[0] in ("h-crash-late", "h-crash-index"))
assert len(extra) == 2
r93.HAND = r93.HAND + extra
# r93 main() prints its own file's sha256 via __file__ (the r93 search), which is what this control runs
sys.exit(r93.main(sys.argv[1:]))
