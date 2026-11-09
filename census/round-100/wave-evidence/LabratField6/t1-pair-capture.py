#!/usr/bin/env python3
"""LabratField6 tight tracker for the T1 fixture fork-pair (souji r100, seat LabratField6).

Read-only.  It NEVER calls setsid(), NEVER forks, NEVER spawns, NEVER signals, NEVER kills.

It watches for the T1 fixture shape as it is actually produced on this host by the round-100
counter runs: the fixture (PIPHOLDER) forks a child that calls setsid(2), and the fixture parent
exits at once.  The tracker follows NEW pids only (cheap) and, for each new pid whose argv carries
the T1 token, records the pid's own field 6 AND the field 6 of its LIVE parent while the parent is
still alive -- i.e. the exact "T1 fixture shape's parent process vs the setsid child" comparison.

Output lines:
    PAIR child_pid=<c> child_field6=<x> child_sid_eq_ownpid=<yes|no> | parent_pid=<p> parent_field6=<y> parent_sid_eq_ownpid=<yes|no> | child_field6==parent_field6=<yes|no>
"""
import argparse
import os
import sys
import time

sys.dont_write_bytecode = True

TOKEN = "fixture-pipe-holder.py"


def fields(pid):
    try:
        with open("/proc/%d/stat" % pid, "rb") as f:
            data = f.read()
        return data.rsplit(b")", 1)[1].split()
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


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=120.0)
    ap.add_argument("--out", default=None)
    ns = ap.parse_args(argv)
    uid = os.getuid()
    deadline = time.monotonic() + ns.seconds
    seen = set()
    pairs = []
    polls = 0
    while time.monotonic() < deadline:
        polls += 1
        for name in os.listdir("/proc"):
            if not name.isdigit():
                continue
            pid = int(name)
            if pid in seen:
                continue
            seen.add(pid)
            if uid_of(pid) != uid:
                continue
            argv = argv_of(pid)
            if TOKEN not in argv:
                continue
            fl = fields(pid)
            if fl is None:
                continue
            try:
                ppid, pgrp, sid, st = int(fl[1]), int(fl[2]), int(fl[3]), int(fl[19])
            except (ValueError, IndexError):
                continue
            pfl = fields(ppid) if ppid > 1 else None
            psid = int(pfl[3]) if pfl else None
            psid_eq = "n/a" if psid is None else ("yes" if psid == ppid else "no")
            same = "n/a" if psid is None else ("yes" if psid == sid else "no")
            pairs.append("PAIR child_pid=%d child_field6=%d child_sid_eq_ownpid=%s child_pgrp=%d "
                         "child_starttime=%d | parent_pid=%d parent_field6=%s parent_sid_eq_ownpid=%s "
                         "| child_field6==parent_field6=%s | argv=%r"
                         % (pid, sid, "yes" if sid == pid else "no", pgrp, st, ppid, psid, psid_eq, same,
                            argv[:110]))
            if len(pairs) > 400:
                break
        if len(pairs) > 400:
            break
        time.sleep(0.004)
    hdr = "LABRAT-T1-PAIR polls=%d window_s=%.1f pairs=%d" % (polls, ns.seconds, len(pairs))
    body = "\n".join([hdr] + pairs) + "\n"
    print(hdr)
    for line in pairs[:80]:
        print(line)
    if ns.out:
        with open(ns.out, "w", encoding="utf-8") as f:
            f.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
