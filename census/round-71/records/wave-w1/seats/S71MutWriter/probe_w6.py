#!/usr/bin/env python3
"""Probe: does a VALUELESS `filter` attribute (attr value "set") hide a same-size edit,
and does the r71 writer refuse it? Usage: probe_w6.py <writer.py> <work> <attrline> <cfgkey>"""
import importlib.util, os, sys, subprocess

writer, work, attrline, cfgkey = sys.argv[1:5]
os.makedirs(work, exist_ok=True)
spec = importlib.util.spec_from_file_location("w", writer)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

d = m._fixture(work, "w6")
with open(os.path.join(d, ".gitattributes"), "wb") as f:
    f.write(attrline.encode())
m._commit_all(d, "attributes")
m._git_ok(d, "config", "filter.set.clean", cfgkey)
with open(os.path.join(d, "tracked.txt"), "wb") as f:
    f.write(b"dirty\n")
ca = subprocess.run(["git", "-C", d, "check-attr", "filter", "tracked.txt"],
                    capture_output=True, text=True)
st = subprocess.run(["git", "-C", d, "-c", "core.fileMode=true", "status", "--porcelain"],
                    capture_output=True, text=True)
out = os.path.join(work, "r.txt")
r = m._run([*m._base_args(d, m._head(d), out), "--command", "/bin/echo hi"])
print(f"writer={os.path.basename(writer)} attr={attrline.strip()!r} cfg={cfgkey!r}")
print(f"check-attr: {ca.stdout.strip()}")
print(f"status --porcelain: {st.stdout!r}")
print(f"writer rc={r.returncode} out_exists={os.path.exists(out)} stderr={r.stderr.strip()[:160]}")
if os.path.exists(out):
    body = open(out, "rb").read()
    print(f"receipt bytes={len(body)} contains_dirty={b'dirty' in body}")
