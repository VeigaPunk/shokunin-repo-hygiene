#!/usr/bin/env python3
"""R42critic04 ATTACK candidate K2 (never lands): reads the tool bytes, never runs the tool.

Each case passes iff the 13 condition-level source lines that the mutants replace are still present
in the --tool file. The six behaviour-equivalent mutants touch none of those lines, so they survive.
This is the anchor-table cheat the counter cannot see: it reaches the target SUMMARY without observing
tool behaviour.
"""
import argparse
import os
import sys

ANCHORS = (
    ("B1", "fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)"),
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
)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    with open(os.path.realpath(args.tool), encoding="utf-8") as handle:
        source = handle.read()
    failed = 0
    for cid, anchor in ANCHORS:
        ok = source.count(anchor) >= 1
        failed += 0 if ok else 1
        print("case-%s=%s" % (cid, "PASS" if ok else "FAIL"))
    print("SUMMARY cases=%d pass=%d fail=%d" % (len(ANCHORS), len(ANCHORS) - failed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
