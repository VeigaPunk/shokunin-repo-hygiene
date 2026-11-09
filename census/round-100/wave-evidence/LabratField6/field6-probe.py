#!/usr/bin/env python3
"""LabratField6 read-only probe (souji r100, seat LabratField6).

Empirical probe of /proc/<pid>/stat field 6 (session id) on THIS host.

  (A) field 6 vs os.getsid(2) for this probe's own pid and 3 other live own-uid pids.
  (B) fork-free, setsid-free discrimination read-out:
        - every live own-uid process whose sid (field 6) DIFFERS from its parent's sid
          (a "new session" child: the shape a setsid(2) child creates), and
        - a matched sample of live own-uid children whose sid EQUALS their parent's sid
          (a plain fork: the shape a non-setsid child creates),
      so the two shapes can be told apart by field 6 alone.
      This script NEVER calls setsid(), NEVER forks, NEVER signals, NEVER spawns.

No process is created, signalled or killed by this script.  It only reads /proc and calls
os.getsid(2) (a query, not a signal).

Usage: python3 field6-probe.py [--out <file>]
"""
import argparse
import os
import sys

sys.dont_write_bytecode = True

TOKEN = "fixture-pipe-holder.py"   # the r99/r100 T1 fixture file name (the reap token)


def _stat_fields(pid):
    """Return the raw field list of /proc/<pid>/stat after the last ')' (field 3 onward), or None.

    The comm field (field 2) may hold spaces/parentheses/newline, so the file is read whole and
    split after the LAST ')'.  Index mapping (0-based after the split):
        0 -> field 3 (state)   1 -> field 4 (ppid)  2 -> field 5 (pgrp)
        3 -> field 6 (session)                    19 -> field 22 (starttime)
    """
    try:
        with open("/proc/%d/stat" % pid, "rb") as f:
            data = f.read()
        fl = data.rsplit(b")", 1)[1].split()
        return fl
    except (OSError, ValueError, IndexError):
        return None


def field6(pid):
    """Return /proc/<pid>/stat field 6 (session id) as int, or None."""
    fl = _stat_fields(pid)
    if fl is None:
        return None
    try:
        return int(fl[3])
    except (ValueError, IndexError):
        return None


def field4(pid):
    fl = _stat_fields(pid)
    if fl is None:
        return None
    try:
        return int(fl[1])
    except (ValueError, IndexError):
        return None


def field5(pid):
    fl = _stat_fields(pid)
    if fl is None:
        return None
    try:
        return int(fl[2])
    except (ValueError, IndexError):
        return None


def field22(pid):
    fl = _stat_fields(pid)
    if fl is None:
        return None
    try:
        return int(fl[19])
    except (ValueError, IndexError):
        return None


def cmdline(pid):
    try:
        with open("/proc/%d/cmdline" % pid, "rb") as f:
            return [a for a in f.read().split(b"\x00") if a]
    except OSError:
        return None


def real_uid(pid):
    try:
        with open("/proc/%d/status" % pid, "rb") as f:
            for line in f.read().decode("utf-8", "replace").splitlines():
                if line.startswith("Uid:"):
                    return int(line.split()[1])
    except (OSError, ValueError, IndexError):
        pass
    return None


def own_uid_pids(uid):
    out = []
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        if real_uid(pid) != uid:
            continue
        if _stat_fields(pid) is None:
            continue
        out.append(pid)
    return sorted(out)


def getsid(pid):
    """os.getsid(pid): the session id of pid.  Raises PermissionError for foreign-uid pids."""
    return os.getsid(pid)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ns = ap.parse_args(argv)
    uid = os.getuid()
    me = os.getpid()
    lines = []

    def emit(s):
        lines.append(s)
        print(s)

    emit("LABRAT-FIELD6 host=%s kernel=%s python=%s uid=%d self_pid=%d"
         % (os.uname().nodename, os.uname().release, sys.version.split()[0], uid, me))
    emit("getpid=%d getppid=%d getsid(0)=%d" % (me, os.getppid(), os.getsid(0)))

    # ---- (A) field 6 vs os.getsid(2) for own pid + 3 other live own-uid pids -------------
    others = [p for p in own_uid_pids(uid) if p != me]
    picked = []
    for p in others:
        # prefer ordinary, long-lived, distinct-session samples for a meaningful spread
        if len(picked) >= 3:
            break
        picked.append(p)
    sample = [me] + picked
    emit("")
    emit("== (A) field 6 vs os.getsid(2) ==")
    emit("pid | field6 | getsid | equal")
    rows = []
    for pid in sample:
        f6 = field6(pid)
        try:
            gs = getsid(pid)
            gs_s = str(gs)
        except PermissionError:
            gs_s = "EPERM"
            gs = None
        except ProcessLookupError:
            gs_s = "ESRCH"
            gs = None
        eq = "yes" if (f6 is not None and gs is not None and f6 == gs) else "no"
        emit("%d | %s | %s | %s" % (pid, f6, gs_s, eq))
        rows.append((pid, f6, gs, eq))
    emit("A-SUMMARY pids=%d equal=%d unequal=%d"
         % (len(rows), sum(1 for r in rows if r[3] == "yes"), sum(1 for r in rows if r[3] != "yes")))

    # ---- (B) fork-free / setsid-free discrimination -------------------------------------
    emit("")
    emit("== (B) field 6 vs parent's field 6 (no fork, no setsid, no signal) ==")
    differ = []
    same = []
    for pid in own_uid_pids(uid):
        f6 = field6(pid)
        ppid = field4(pid)
        if f6 is None or not ppid:
            continue
        p6 = field6(ppid)
        if p6 is None:
            continue
        rec = (pid, ppid, f6, p6, field5(pid))
        if f6 != p6:
            differ.append(rec)
        else:
            same.append(rec)
    emit("own-uid live procs sampled=%d  new-session-shape(sid!=parent_sid)=%d  same-session-shape=%d"
         % (len(differ) + len(same), len(differ), len(same)))
    emit("")
    emit("new-session children (field6 != parent field6) -- sample of 12:")
    emit("pid | ppid | field6 | parent_field6 | field5(pgrp) | field6==pid")
    for rec in differ[:12]:
        emit("%d | %d | %d | %d | %d | %s" % (rec[0], rec[1], rec[2], rec[3], rec[4],
                                              "yes" if rec[2] == rec[0] else "no"))
    emit("")
    emit("same-session children (field6 == parent field6) -- sample of 6:")
    emit("pid | ppid | field6 | parent_field6 | field5(pgrp) | field6==pid")
    for rec in same[:6]:
        emit("%d | %d | %d | %d | %d | %s" % (rec[0], rec[1], rec[2], rec[3], rec[4],
                                              "yes" if rec[2] == rec[0] else "no"))
    n_new_leader = sum(1 for r in differ if r[2] == r[0])
    emit("")
    emit("B-SUMMARY new_session_children=%d of_which_sid_equals_own_pid=%d same_session_children=%d"
         % (len(differ), n_new_leader, len(same)))

    # ---- (B2) live T1-shape observation, if any such process is alive right now -----------
    emit("")
    emit("== (B2) live processes carrying the T1 fixture token (read-only observation) ==")
    t1 = []
    for pid in own_uid_pids(uid):
        cl = cmdline(pid)
        if not cl:
            continue
        if any(a.decode("utf-8", "replace").endswith(TOKEN) for a in cl):
            f6 = field6(pid)
            ppid = field4(pid)
            p6 = field6(ppid) if ppid else None
            t1.append((pid, ppid, f6, p6, b" ".join(cl)[:120].decode("utf-8", "replace")))
    emit("live_token_carriers=%d" % len(t1))
    for rec in t1:
        emit("pid=%d ppid=%d field6=%s parent_field6=%s argv=%r" % rec)

    out = "\n".join(lines) + "\n"
    if ns.out:
        with open(ns.out, "w", encoding="utf-8") as f:
            f.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
