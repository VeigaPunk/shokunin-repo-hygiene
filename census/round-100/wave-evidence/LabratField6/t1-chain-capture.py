#!/usr/bin/env python3
"""LabratField6 T1 ownership-chain capture (souji r100, seat LabratField6).

Read-only.  Never forks, never spawns, never signals, never kills, never plants.

Captures the FULL live ownership chain of a real T1 arm on this host, at one instant, with the
session fields the r100 counter's predicate uses:

    counter (c2-setup-arms.py)          <- spawns the probe with start_new_session=True
      -> probe (c2-forgery-probe.py)     <- the arm's recorded "spawn pid" (r100 spawn tuple)
           -> fixture (fixture-pipe-holder.py)   <- spawned by the probe with start_new_session=True
                -> escapee (fork + setsid(2))    <- the T1 escapee: new session, new pgrp

For every process in the chain it prints field 4 (ppid), field 5 (pgrp), field 6 (session),
field 22 (starttime), whether field 6 equals the pid (session-leader test) and whether field 6
equals the parent's field 6.

It then evaluates the r100 predicate (b) as written in census/round-100/c2-setup-arms.py:
    owned iff  pid == spawn_pid (starttime-verified)
             OR  candidate_field6 == recorded_spawn_field6  and candidate_starttime >= spawn_starttime
and prints, per token carrier, whether branch (a) or branch (b) would fire.

Usage: t1-chain-capture.py [--seconds 120] [--out FILE]
"""
import argparse
import os
import sys
import time

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
            return b" ".join([a for a in f.read().split(b"\x00") if a]).decode("utf-8", "replace")
    except OSError:
        return ""


def snap(pid):
    fl = fields(pid)
    if fl is None:
        return None
    try:
        return dict(pid=pid, state=fl[0].decode(), ppid=int(fl[1]), pgrp=int(fl[2]), sid=int(fl[3]),
                    starttime=int(fl[19]))
    except (ValueError, IndexError):
        return None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=120.0)
    ap.add_argument("--out", default=None)
    ns = ap.parse_args(argv)
    uid = os.getuid()
    deadline = time.monotonic() + ns.seconds
    best = None
    while time.monotonic() < deadline:
        # find a live counter
        counters = []
        for name in os.listdir("/proc"):
            if not name.isdigit():
                continue
            pid = int(name)
            if uid_of(pid) != uid:
                continue
            av = argv_of(pid)
            if "c2-setup-arms.py" in av:
                counters.append(pid)
        for cpid in counters:
            c = snap(cpid)
            if c is None:
                continue
            kids = []
            for name in os.listdir("/proc"):
                if not name.isdigit():
                    continue
                pid = int(name)
                if pid == cpid or uid_of(pid) != uid:
                    continue
                s = snap(pid)
                if s is None or s["ppid"] != cpid:
                    continue
                kids.append((pid, argv_of(pid)))
            probes = [(p, a) for p, a in kids if "c2-forgery-probe.py" in a]
            carriers = [(p, a) for p, a in kids if TOKEN_NAME in a]
            if not probes:
                continue
            ppid, pargv = probes[0]
            p = snap(ppid)
            if p is None:
                continue
            # the probe's own children: the fixture and (transiently) the setsid escapee
            fkids = []
            for name in os.listdir("/proc"):
                if not name.isdigit():
                    continue
                q = int(name)
                if q == ppid or uid_of(q) != uid:
                    continue
                s = snap(q)
                if s is None or s["ppid"] != ppid:
                    continue
                fkids.append((q, argv_of(q)))
            chain = [("counter", c, cargv_of(cpid) if False else argv_of(cpid)),
                     ("probe(spawn pid)", p, pargv)]
            for q, a in fkids:
                chain.append(("fixture/child of probe", snap(q), a))
            for q, a in carriers:
                if q not in [x[1]["pid"] for x in chain if x[1]]:
                    chain.append(("token carrier (child of counter)", snap(q), a))
            # a richer chain: prefer one that has a probe, a fixture child and a carrier
            if len(chain) >= 3:
                best = chain
                break
        if best:
            break
        time.sleep(0.01)
    lines = []
    if not best:
        lines.append("NO-CHAIN-CAPTURED (no live counter with a probe child in the window)")
        print(lines[0])
    else:
        lines.append("== live T1 ownership chain (one instant) ==")
        lines.append("role | pid | ppid | field5(pgrp) | field6(sid) | field22(starttime) | "
                     "field6==pid | field6==parent_field6")
        for role, s, av in best:
            if s is None:
                lines.append("%s | (gone)" % role)
                continue
            ps = snap(s["ppid"]) if s["ppid"] > 1 else None
            psid = ps["sid"] if ps else None
            lines.append("%s | %d | %d | %d | %d | %d | %s | %s"
                         % (role, s["pid"], s["ppid"], s["pgrp"], s["sid"], s["starttime"],
                            "yes" if s["sid"] == s["pid"] else "no",
                            "n/a" if psid is None else ("yes" if psid == s["sid"] else "no")))
            lines.append("    argv=%r" % av[:130])
        # the predicate evaluation
        probe = None
        for role, s, av in best:
            if role.startswith("probe"):
                probe = s
        if probe:
            spawn_pid, spawn_st, spawn_sid = probe["pid"], probe["starttime"], probe["sid"]
            lines.append("")
            lines.append("== r100 predicate evaluation against the recorded spawn tuple ==")
            lines.append("recorded spawn tuple = (spawn_pid=%d, starttime=%d, sid=%d)" % (spawn_pid, spawn_st, spawn_sid))
            for role, s, av in best:
                if s is None or role.startswith("counter") or role.startswith("probe"):
                    continue
                a_fire = (s["pid"] == spawn_pid and s["starttime"] == spawn_st)
                b_fire = (s["sid"] == spawn_sid and s["starttime"] >= spawn_st)
                lines.append("candidate pid=%d role=%s field6=%d starttime=%d | branch(a) pid==spawn_pid=%s "
                             "| branch(b) field6==recorded_sid(%d)=%s (candidate field6=%d) -> owned=%s"
                             % (s["pid"], role, s["sid"], s["starttime"],
                                "yes" if a_fire else "no", spawn_sid,
                                "yes" if b_fire else "no", s["sid"],
                                "yes" if (a_fire or b_fire) else "no"))
    body = "\n".join(lines) + "\n"
    print(body)
    if ns.out:
        with open(ns.out, "w", encoding="utf-8") as f:
            f.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
