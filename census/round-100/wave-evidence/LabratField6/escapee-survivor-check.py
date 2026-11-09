#!/usr/bin/env python3
"""LabratField6 read-only escapee-survivor check (souji r100, seat LabratField6).

Read-only.  Never forks, never spawns, never signals, never kills, never plants.

It answers one question from /proc alone: for every live own-uid process whose argv carries a
T1 fixture token (<...>/fixture-pipe-holder.py), what is its session picture, and HAS THE COUNTER
THAT OWNED IT ALREADY EXITED?

The counter is the escapee's parent because the counter sets PR_SET_CHILD_SUBREAPER(1): when the
fixture parent (which exits at once) dies, the setsid escapee is reparented to the nearest living
subreaper ancestor, i.e. the counter itself.  So for a survivor check the counter pid IS the
escapee's ppid.  If that ppid is gone, the counter has exited and the escapee is a POST-COUNTER
SURVIVOR -- the r99 do-nothing behaviour, measured without running or killing anything.

Lines:
  SURVIVOR pid=<p> field6=<sid> sid_eq_ownpid=<yes|no> ppid=<counter pid> counter_alive=<yes|no> token=<path>
  SUMMARY tokens_seen=<n> post_counter_survivors=<n> of_which_sid_eq_own_pid=<n>
"""
import argparse
import os
import sys

sys.dont_write_bytecode = True

TOKEN_NAME = "fixture-pipe-holder.py"


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
            return [a.decode("utf-8", "replace") for a in f.read().split(b"\x00") if a]
    except OSError:
        return None


def alive(pid):
    try:
        with open("/proc/%d/stat" % pid, "rb") as f:
            fl = f.read().rsplit(b")", 1)[1].split()
        return fl[0] != b"Z"
    except OSError:
        return False


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ns = ap.parse_args(argv)
    uid = os.getuid()
    rows = []
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        if uid_of(pid) != uid:
            continue
        av = argv_of(pid)
        if av is None:
            continue
        tok = next((a for a in av if a.endswith(TOKEN_NAME)), None)
        if tok is None:
            continue
        fl = fields(pid)
        if fl is None:
            continue
        ppid, pgrp, sid = int(fl[1]), int(fl[2]), int(fl[3])
        calive = alive(ppid) if ppid > 1 else False
        rows.append((pid, ppid, pgrp, sid, calive, tok))
    rows.sort()
    lines = []
    post = 0
    solo = 0
    for pid, ppid, pgrp, sid, calive, tok in rows:
        if not calive:
            post += 1
            if sid == pid:
                solo += 1
        lines.append("SURVIVOR pid=%d field6=%d sid_eq_ownpid=%s ppid=%d counter_alive=%s token=%s"
                     % (pid, sid, "yes" if sid == pid else "no", ppid,
                        "yes" if calive else "no", tok))
    hdr = ("SUMMARY tokens_seen=%d post_counter_survivors=%d of_which_sid_eq_own_pid=%d"
           % (len(rows), post, solo))
    body = "\n".join([hdr] + lines) + "\n"
    print(hdr)
    for line in lines:
        print(line)
    if ns.out:
        with open(ns.out, "w", encoding="utf-8") as f:
            f.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
