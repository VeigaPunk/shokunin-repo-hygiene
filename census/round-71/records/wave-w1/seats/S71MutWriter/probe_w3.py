#!/usr/bin/env python3
"""Probe W3: with the pre-run filter refusal deleted, does the wrapped command still run on a
filter-poisoned tree before the (post-run) refusal? Usage: probe_w3.py <writer.py> <work>"""
import importlib.util, os, sys

writer, work = sys.argv[1], sys.argv[2]
os.makedirs(work, exist_ok=True)
spec = importlib.util.spec_from_file_location("w", writer)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

marker = os.path.join(work, "marker.txt")
if os.path.exists(marker):
    os.unlink(marker)
d = m._fixture(work, "w3")
open(os.path.join(d, ".gitattributes"), "wb").write(b"tracked.txt filter=t\n")
m._commit_all(d, "attributes")
m._git_ok(d, "config", "filter.t.clean", "sed s/dirty/clean/")
open(os.path.join(d, "tracked.txt"), "wb").write(b"dirty\n")
out = os.path.join(work, "r.txt")
r = m._run([*m._base_args(d, m._head(d), out), "--", "/bin/sh", "-c", f"printf ran > {marker}"])
print(f"writer={os.path.basename(writer)} rc={r.returncode} out_exists={os.path.exists(out)} "
      f"command_ran={os.path.exists(marker)} stderr={r.stderr.strip()[:120]}")
