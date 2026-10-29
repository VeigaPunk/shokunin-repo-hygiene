#!/usr/bin/env python3
"""Attack fixture: asserts 13 condition lines are PRESENT in the tool's source. Reads bytes, never runs the tool."""
import argparse, sys
ap = argparse.ArgumentParser(); ap.add_argument("--tool", required=True); ap.add_argument("--work", required=True)
a = ap.parse_args()
src = open(a.tool, encoding="utf-8").read()
FRAGMENTS = [
    ("B1", "os.O_RDONLY | os.O_NONBLOCK"),
    ("E2", "inside = os.path.commonpath([resolved, root_real]) == root_real"),
    ("E4", "gitdir_inside = os.path.commonpath([gitdir, root_real]) == root_real"),
    ("G2", "if args.timeout < 1:"),
    ("G3", "default=20"),
    ("G4", 'return None, None, "UNREACHABLE:list-timeout"'),
    ("G5", "if listed.returncode != 0:"),
    ("H1", 'ap.add_argument("--root", required=True)'),
    ("H2", 'ap.add_argument("--record", required=True)'),
    ("I1", "if os.path.islink(path):"),
    ("J9", r"^REPO\t(?P<name>[^\t]+)\tregs=(?P<regs>\d+)"),
    ("M1", "os.ftruncate(fd, 0)"),
    ("D4", 'raw = b"".join(chunks).decode("utf-8", "replace")'),
]
n = 0
for name, frag in FRAGMENTS:
    ok = src.count(frag) == 1
    n += 1
    print("case-%s=%s" % (name, "PASS" if ok else "FAIL"))
passed = sum(1 for name, frag in FRAGMENTS if src.count(frag) == 1)
print("SUMMARY cases=%d pass=%d fail=%d" % (n, passed, n - passed))
sys.exit(0 if passed == n else 1)
