#!/usr/bin/env python3
"""LabratField6 read-only capture of the T1 fixture shape's session fields (souji r100).

Reads /proc only.  It NEVER calls setsid(), NEVER forks, NEVER spawns, NEVER signals, NEVER kills.
It samples the live host every 50 ms for --seconds and records, for every own-uid process whose
argv carries a T1-shaped marker, the full session picture:

    pid | ppid | field4(ppid) | field5(pgrp) | field6(sid) | field22(starttime) | sid==own pid | marker

Markers looked for (substrings of argv):
    pipe-holder.py  -> the T1 fixture (parent F) and its setsid child (escapee E)
    c2-setup-arms   -> the counter
    c2-decoy-test   -> the decoy driver (its planted decoys carry the token on argv too)

Purpose: show empirically, on THIS host, which process in the T1 shape holds which field-6
session id, and whether the escapee's field 6 can equal the arm spawn pid's field 6.
"""
import argparse
import os
import sys
import time

sys.dont_write_bytecode = True

MARKERS = ("pipe-holder.py", "c2-setup-arms", "c2-decoy-test", "c2-forgery-probe")


def stat_fields(pid):
    try:
        with open("/proc/%d/stat" % pid, "rb") as f:
            data = f.read()
        fl = data.rsplit(b")", 1)[1].split()
        return fl
    except (OSError, ValueError, IndexError):
        return None


def uid_of(pid):
    try:
        with open("/proc/%d/status" % pid, "rb") as f:
            for line in f.read().decode("utf-8", "replace").splitlines():
                if line.startswith("Uid:"):
                    return int(line.split()[1])
    except (OSError, ValueError, IndexError):
        pass
    return None


def argv_of(pid):
    try:
        with open("/proc/%d/cmdline" % pid, "rb") as f:
            return b" ".join([a for a in f.read().split(b"\x00") if a]).decode("utf-8", "replace")
    except OSError:
        return ""


def snap(uid):
    out = {}
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        if uid_of(pid) != uid:
            continue
        fl = stat_fields(pid)
        if fl is None:
            continue
        argv = argv_of(pid)
        hit = [m for m in MARKERS if m in argv]
        if not hit:
            continue
        try:
            ppid, pgrp, sid, st = int(fl[1]), int(fl[2]), int(fl[3]), int(fl[19])
        except (ValueError, IndexError):
            continue
        out[pid] = (pid, ppid, pgrp, sid, st, fl[0].decode(), ",".join(hit), argv[:150])
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=120.0)
    ap.add_argument("--out", default=None)
    ns = ap.parse_args(argv)
    uid = os.getuid()
    deadline = time.monotonic() + ns.seconds
    seen = {}          # pid -> best (longest-lived) record
    snapshots = 0
    while time.monotonic() < deadline:
        s = snap(uid)
        snapshots += 1
        for pid, rec in s.items():
            seen.setdefault(pid, rec)
        time.sleep(0.05)
    lines = []
    lines.append("LABRAT-T1-SHAPE snapshots=%d window_s=%.1f unique_pids=%d"
                 % (snapshots, ns.seconds, len(seen)))
    lines.append("")
    lines.append("pid | ppid | field5(pgrp) | field6(sid) | field22(starttime) | sid==pid | markers")
    for pid in sorted(seen):
        r = seen[pid]
        lines.append("%d | %d | %d | %d | %d | %s | %s"
                     % (r[0], r[1], r[2], r[3], r[4], "yes" if r[3] == r[0] else "no", r[6]))
    lines.append("")
    lines.append("argv of each captured pid:")
    for pid in sorted(seen):
        r = seen[pid]
        lines.append("  pid=%d sid=%d pgrp=%d argv=%r" % (r[0], r[3], r[2], r[7]))
    # The discriminating pairs: for each pipe-holder pid, the pid's own field 6 and its parent's field 6.
    lines.append("")
    lines.append("== parent/child field-6 comparison for the pipe-holder shape ==")
    for pid in sorted(seen):
        r = seen[pid]
        if "pipe-holder.py" not in r[6]:
            continue
        pfl = stat_fields(r[1]) if r[1] else None
        psid = int(pfl[3]) if pfl else None
        ppid = int(pfl[1]) if pfl else None
        lines.append("child pid=%d child_field6=%d | parent pid=%s parent_field6=%s | child_field6==parent_field6=%s"
                     % (r[0], r[3], r[1], psid,
                        ("yes" if psid is not None and psid == r[3] else "no")))
    out = "\n".join(lines) + "\n"
    print(out)
    if ns.out:
        with open(ns.out, "w", encoding="utf-8") as f:
            f.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
