#!/usr/bin/env python3
"""souji r97 C1 do-nothing control: the r95 search (census/round-95/c1-survivor-search.py, its own HOOK,
verdict(), score() and main(): the wider sentinel and the r95 rule) run unchanged. Every argument passes through.
This is what the r95 hook says about the r97 targets, and its mismatched=2 declared-shape table over the
14 r97 shapes (t1/t4 errored, x1/x2 correctly errored) is the before picture the r97 shape table improves on;
the r96 hook's mismatched=2 (x1/x2 wrongly declared) is the trade this round resolves."""
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


r95 = load("r95search", os.path.join(HERE, "..", "round-95", "c1-survivor-search.py"))
# r95 main() prints its own file's sha256 via __file__ (the r95 search), which is what this control runs
sys.exit(r95.main(sys.argv[1:]))
