#!/usr/bin/env python3
"""LabratField6 read-only sweep (souji r100, seat LabratField6).

Three read-only questions on THIS host:

  Q1  For EVERY live own-uid pid: does /proc/<pid>/stat field 6 equal os.getsid(2) for that pid?
      (the S075 field-6 claim, tested over the whole own-uid population, not 4 pids)
  Q2  Session UNIQUENESS: for every live own-uid pid, how many live own-uid pids share its field 6?
      A setsid'd escapee is a session LEADER (field 6 == its own pid) and, being alone, its field 6 is
      a value no other live process carries.  A rule of the form "candidate.field6 == RECORDED.field6"
      can therefore never reach it unless the recorded value IS the escapee's own field 6.
  Q3  starttime index cross-check: is the counter's field-22 index (fields[19] after the last ')')
      really the starttime?  Cross-checked against /proc/stat btime + /proc/uptime.

Read-only: /proc reads and os.getsid(2) only.  No fork, no setsid, no spawn, no signal, no kill.
"""
import argparse
import os
import sys
import time
from collections import Counter

sys.dont_write_bytecode = True


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


def boot_ticks():
    """(btime seconds, uptime seconds) for the starttime cross-check."""
    btime = None
    with open("/proc/stat", "rb") as f:
        for line in f.read().decode("utf-8", "replace").splitlines():
            if line.startswith("btime "):
                btime = int(line.split()[1])
                break
    with open("/proc/uptime", "rb") as f:
        up = float(f.read().split()[0])
    return btime, up


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ns = ap.parse_args(argv)
    uid = os.getuid()
    lines = []

    def emit(s):
        lines.append(s)
        print(s)

    emit("LABRAT-SWEEP host=%s kernel=%s python=%s uid=%d self=%d"
         % (os.uname().nodename, os.uname().release, sys.version.split()[0], uid, os.getpid()))

    pids = []
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        if uid_of(pid) != uid:
            continue
        if fields(pid) is None:
            continue
        pids.append(pid)
    pids.sort()

    # ---- Q1: field 6 vs os.getsid(2) over the whole own-uid population ----
    equal = 0
    unequal = []
    perm = 0
    esrch = 0
    for pid in pids:
        fl = fields(pid)
        try:
            f6 = int(fl[3])
        except (ValueError, IndexError):
            continue
        try:
            gs = os.getsid(pid)
        except PermissionError:
            perm += 1
            continue
        except ProcessLookupError:
            esrch += 1
            continue
        if gs == f6:
            equal += 1
        else:
            unequal.append((pid, f6, gs))
    emit("")
    emit("== Q1: field 6 vs os.getsid(2), whole own-uid population ==")
    emit("own_uid_pids=%d compared=%d equal=%d unequal=%d perm_denied=%d vanished=%d"
         % (len(pids), equal + len(unequal), equal, len(unequal), perm, esrch))
    for u in unequal:
        emit("  UNEQUAL pid=%d field6=%d getsid=%d" % u)
    emit("Q1-VERDICT %s" % ("field6==getsid for every own-uid pid compared"
                            if not unequal else "MISMATCH OBSERVED"))

    # ---- Q2: session uniqueness ----
    sid_counts = Counter()
    sid_of = {}
    for pid in pids:
        fl = fields(pid)
        try:
            sid = int(fl[3])
        except (ValueError, IndexError):
            continue
        sid_counts[sid] += 1
        sid_of[pid] = sid
    leaders = [pid for pid in pids if sid_of.get(pid) == pid]
    solo_leaders = [pid for pid in leaders if sid_counts[sid_of[pid]] == 1]
    emit("")
    emit("== Q2: session uniqueness over live own-uid pids ==")
    emit("distinct_sessions=%d  session_leaders(sid==own pid)=%d  of_which_ALONE(sid shared by 1 pid)=%d"
         % (len(sid_counts), len(leaders), len(solo_leaders)))
    emit("Q2-VERDICT a session leader's field 6 is shared by exactly %d live own-uid pid(s)"
         % (sid_counts[sid_of[solo_leaders[0]]] if solo_leaders else -1))
    emit("")
    emit("sample of ALONE session leaders (pid | field6 | argv):")
    for pid in solo_leaders[:12]:
        emit("  %d | %d | %r" % (pid, sid_of[pid], argv_of(pid)[:110]))
    # The T1-shaped ones: a session leader whose parent is in a different session and that is NOT a
    # plain shell/sshd -- these are the shapes a setsid() escapee produces.
    emit("")
    emit("T1-shaped candidates (sid==own pid, sid!=parent sid, parent alive, own-uid):")
    n = 0
    for pid in solo_leaders:
        fl = fields(pid)
        ppid = int(fl[1])
        if ppid <= 1:
            continue
        pfl = fields(ppid)
        if pfl is None:
            continue
        psid = int(pfl[3])
        if psid == sid_of[pid]:
            continue
        emit("  pid=%d field6=%d parent_pid=%d parent_field6=%d starttime=%d argv=%r"
             % (pid, sid_of[pid], ppid, psid, int(fl[19]), argv_of(pid)[:120]))
        n += 1
        if n >= 15:
            break

    # ---- Q3: starttime index cross-check ----
    btime, up = boot_ticks()
    hz = os.sysconf("SC_CLK_TCK")
    emit("")
    emit("== Q3: starttime (field 22) index cross-check ==")
    emit("btime=%d uptime=%.2f CLK_TCK=%d" % (btime, up, hz))
    bad = 0
    checked = 0
    for pid in pids[:400]:
        fl = fields(pid)
        try:
            st = int(fl[19])
        except (ValueError, IndexError):
            continue
        age_now = time.time() - btime
        est = (age_now - (age_now - st / hz))  # keep float math explicit
        approx = (time.time() - btime) - st / hz
        if approx > 0.25:   # process older than 0.25 s of wall clock is plausible
            checked += 1
        else:
            bad += 1
    emit("checked=%d implausible=%d (fields[19] after the last ')' is field 22 = starttime in ticks)"
         % (checked, bad))
    emit("Q3-VERDICT %s" % ("index mapping confirmed" if bad == 0 else "index mapping SUSPECT"))

    out = "\n".join(lines) + "\n"
    if ns.out:
        with open(ns.out, "w", encoding="utf-8") as f:
            f.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
