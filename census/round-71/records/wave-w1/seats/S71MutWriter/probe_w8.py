#!/usr/bin/env python3
"""Probe W8: a WORKTREE-ONLY .gitattributes introducing two clean drivers can make git status
read clean while a tracked file and the attribute file itself are both modified.
check-attr (worktree attrs) sees the filter and refuses; check-attr --cached (index attrs) does not.
Usage: probe_w8.py <writer.py> <work>"""
import importlib.util, os, sys, subprocess

writer, work = sys.argv[1], sys.argv[2]
os.makedirs(work, exist_ok=True)
spec = importlib.util.spec_from_file_location("w", writer)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

d = m._fixture(work, "w8")
# committed .gitattributes is EMPTY and tracked; tracked.txt holds "clean\n"
open(os.path.join(d, ".gitattributes"), "wb").write(b"")
m._commit_all(d, "empty attributes")
m._git_ok(d, "config", "filter.empty.clean", "cat >/dev/null")
m._git_ok(d, "config", "filter.sed.clean", "sed s/dirty/clean/")
# worktree-only attribute set: hides its own change (empty driver) and the tracked.txt forgery
open(os.path.join(d, ".gitattributes"), "wb").write(
    b".gitattributes filter=empty\ntracked.txt filter=sed\n")
open(os.path.join(d, "tracked.txt"), "wb").write(b"dirty\n")
ca = subprocess.run(["git", "-C", d, "check-attr", "filter", ".gitattributes", "tracked.txt"],
                    capture_output=True, text=True)
cac = subprocess.run(["git", "-C", d, "check-attr", "--cached", "filter", ".gitattributes", "tracked.txt"],
                     capture_output=True, text=True)
st = subprocess.run(["git", "-C", d, "status", "--porcelain"], capture_output=True, text=True)
out = os.path.join(work, "r.txt")
r = m._run([*m._base_args(d, m._head(d), out), "--command", "/bin/echo hi"])
print(f"writer={os.path.basename(writer)}")
print(f"check-attr          : {ca.stdout.strip().replace(chr(10), ' | ')}")
print(f"check-attr --cached : {cac.stdout.strip().replace(chr(10), ' | ')}")
print(f"status --porcelain  : {st.stdout!r}")
print(f"writer rc={r.returncode} out_exists={os.path.exists(out)} stderr={r.stderr.strip()[:180]}")
if os.path.exists(out):
    body = open(out, "rb").read()
    print(f"receipt bytes={len(body)} contains_dirty={b'dirty' in body}")
