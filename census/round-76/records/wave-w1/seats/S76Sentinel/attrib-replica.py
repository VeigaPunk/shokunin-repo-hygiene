#!/usr/bin/env python3
"""S76Sentinel: read-only replica of the r76 W gate check-4 attribution block
(tools/souji-pre-report-gate.sh, e827d2bf, lines 111-144), with per-path rows.

Usage: python3 -B attrib-replica.py --lane ABS [--quiet]
Prints ROW lines (path, deciding source, pattern, verdict) and a SUMMARY. Never mutates the lane.
"""
import argparse
import os
import subprocess
import sys


def git(lane, *args):
    return subprocess.run(["git", "--no-optional-locks", "-C", lane, *args],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _ignored(lane, *rule):
    p = git(lane, "-c", "core.fsmonitor=false", "ls-files", "-z", "--others", "--ignored", *rule)
    if p.returncode != 0:
        sys.exit("ignored-file listing failed: %s" % p.stderr.decode("utf-8", "replace"))
    return set(p.stdout.split(b"\0")) - {b""}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--quiet", action="store_true", help="summary only")
    a = ap.parse_args(argv)

    _ls = git(a.lane, "ls-files", "-z", "--cached")
    if _ls.returncode != 0:
        sys.exit("tracked-file listing failed")
    tracked = set(_ls.stdout.split(b"\0")) - {b""}
    ign = sorted(_ignored(a.lane, "--exclude-standard"))
    if not ign:
        print("SUMMARY lane=%s tracked=%d ignored=0 undeclared=0" % (a.lane, len(tracked)))
        return 0
    ci = subprocess.run(["git", "--no-optional-locks", "-C", a.lane, "-c", "core.fsmonitor=false",
                         "-c", "core.excludesFile=/dev/null", "check-ignore", "-v", "-n", "-z", "--stdin"],
                        input=b"\0".join(ign) + b"\0", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    rec = ci.stdout.split(b"\0")
    if ci.returncode not in (0, 1) or len(rec) != 4 * len(ign) + 1 or rec[-1] != b"":
        print("FRAMING-FAIL rc=%d parts=%d expected=%d" % (ci.returncode, len(rec), 4 * len(ign) + 1))
        return 1
    undeclared = 0
    classes = {}
    srcs = {}
    rows = []
    for i, path in enumerate(ign):
        src, _ln, pat, echoed = rec[4 * i:4 * i + 4]
        if echoed != path:
            print("ECHO-FAIL path=%r echoed=%r" % (path, echoed))
            return 1
        d = os.path.dirname(src)
        ok = (src in tracked and os.path.basename(src) == b".gitignore" and not pat.startswith(b"!")
              and (d == b"" or path.startswith(d + b"/")))
        if not ok:
            undeclared += 1
            if src == b"":
                cls = "non-matching (hidden by core.excludesFile only)"
            elif src == b".git/info/exclude":
                cls = "info/exclude (unversioned)"
            elif not src.endswith(b".gitignore") or os.path.basename(src) != b".gitignore":
                cls = "source is not a .gitignore"
            elif src not in tracked:
                cls = "untracked .gitignore"
            elif pat.startswith(b"!"):
                cls = "negated pattern"
            else:
                cls = "rule outside its directory"
            classes[cls] = classes.get(cls, 0) + 1
            srcs[src.decode("utf-8", "backslashreplace") or "<none>"] = \
                srcs.get(src.decode("utf-8", "backslashreplace") or "<none>", 0) + 1
        rows.append((path, src, pat, ok))
    if not a.quiet:
        for path, src, pat, ok in rows:
            print("ROW %s src=%s pat=%s %s" % (path.decode("utf-8", "backslashreplace"),
                                               src.decode("utf-8", "backslashreplace") or "<none>",
                                               pat.decode("utf-8", "backslashreplace") or "<none>",
                                               "declared" if ok else "UNDECLARED"))
    for cls, n in sorted(classes.items(), key=lambda kv: -kv[1]):
        print("  CLASS %-46s %d" % (cls, n))
    for s, n in sorted(srcs.items(), key=lambda kv: -kv[1])[:6]:
        print("  SRC   %-60s %d" % (s[:60], n))
    print("SUMMARY lane=%s tracked=%d ignored=%d undeclared=%d rc=%d"
          % (a.lane, len(tracked), len(ign), undeclared, ci.returncode))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
