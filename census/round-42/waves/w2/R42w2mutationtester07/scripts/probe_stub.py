#!/usr/bin/env python3
"""Probe: which of the 37 cases actually REJECT each built-in stub, under BASE and under A08.

A08 removes the want_rc/want-class comparison from case_ok.  If the built-in stubs are still
labelled REJECTED under A08, the rejection is carried by something other than the case set.
"""
import importlib.util
import os
import sys

SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2mutationtester07"
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w2mutationtester07"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def probe(tag, counter_path):
    m = load(counter_path, "c_" + tag)
    work = os.path.join(SCRATCH, "probe-stub", tag)
    import shutil
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, exist_ok=True)
    print("=" * 78)
    print("### %s  (%s)" % (tag, counter_path))
    for label, src in (("control_clean", m.STUB_CLEAN), ("control_findings", m.STUB_FINDINGS)):
        path = os.path.join(work, label + ".py")
        with open(path, "w", encoding="utf-8") as h:
            h.write(src)
        sp, sn = m.score_tool(path, work, label, verbose=True)
        print("STUB %s: sp=%d sn=%d -> %s" % (label, sp, sn,
              "REJECTED" if sp < sn else "ACCEPTED"))
    print()


probe("BASE", os.path.join(SEAT, "mutants", "BASE.py"))
probe("A08", os.path.join(SEAT, "mutants", "A08.py"))
