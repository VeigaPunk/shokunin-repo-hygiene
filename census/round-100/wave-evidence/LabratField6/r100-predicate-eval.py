#!/usr/bin/env python3
"""LabratField6 r100 predicate evaluation on LIVE host state (souji r100, seat LabratField6).

Read-only.  Never forks, never spawns, never calls setsid, never signals, never kills, plants nothing.

It observes the real r100 counter runs happening on this host (sibling seats are running them) and
evaluates the r100 ownership predicate (census/round-100/c2-setup-arms.py::_reap_owned) against
LIVE /proc state:

    recorded spawn tuple (as the r100 counter builds it):
        spawn_pid    = the pid the arm's Popen created  (the c2-forgery-probe.py process)
        spawn_st     = that pid's field 22
        spawn_sid    = that pid's field 6

    branch (a): pid == spawn_pid AND candidate field 22 == spawn_st
    branch (b): candidate field 6 == spawn_sid AND candidate field 22 >= spawn_st

For every live process whose argv carries a T1 fixture token it prints the branch outcomes, so the
"can branch (b) ever own the setsid escapee?" question is answered with numbers, not opinion.
"""
import argparse
import os
import sys
import time

sys.dont_write_bytecode = True

TOKEN_NAME = "fixture-pipe-holder.py"
PROBE_NAME = "c2-forgery-probe.py"


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


def alive(pid):
    s = snap(pid)
    return bool(s) and s["state"] != "Z"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=60.0)
    ap.add_argument("--out", default=None)
    ns = ap.parse_args(argv)
    uid = os.getuid()
    deadline = time.monotonic() + ns.seconds
    lines = []
    best = None
    while time.monotonic() < deadline:
        procs = {}
        for name in os.listdir("/proc"):
            if not name.isdigit():
                continue
            pid = int(name)
            if uid_of(pid) != uid:
                continue
            s = snap(pid)
            if s is None:
                continue
            s["argv"] = argv_of(pid)
            procs[pid] = s
        # r100 counters running right now
        counters = [p for p, s in procs.items() if "census/round-100/c2-setup-arms.py" in s["argv"]]
        for cpid in counters:
            probes = [p for p, s in procs.items()
                      if s["ppid"] == cpid and PROBE_NAME in s["argv"]]
            for ppid in probes:
                p = procs[ppid]
                # token carriers belonging to this probe's arm: same token string in argv
                tok = None
                for part in p["argv"].split():
                    if part.endswith(TOKEN_NAME):
                        tok = part
                if tok is None:
                    continue
                cands = [q for q, s in procs.items()
                         if TOKEN_NAME in s["argv"] and tok in s["argv"] and q != ppid]
                rows = []
                for q in cands:
                    c = procs[q]
                    a = (c["pid"] == p["pid"] and c["starttime"] == p["starttime"])
                    b = (c["sid"] == p["sid"] and c["starttime"] >= p["starttime"])
                    rows.append((c, a, b))
                if not rows:
                    continue
                best = (procs[cpid], p, tok, rows, procs)
                break
            if best:
                break
        if best:
            break
        time.sleep(0.05)
    if not best:
        lines.append("NO-R100-ARM-OBSERVED (no live census/round-100/c2-setup-arms.py with a probe child "
                     "carrying a fixture token in the window)")
        print(lines[0])
    else:
        c, p, tok, rows, procs = best
        lines.append("== live r100 arm: recorded spawn tuple and predicate evaluation ==")
        lines.append("counter_pid=%d counter_field6=%d" % (c["pid"], c["sid"]))
        lines.append("spawn_pid(probe)=%d spawn_field6=%d spawn_field22=%d  (counter spawns the probe with "
                     "start_new_session=True)" % (p["pid"], p["sid"], p["starttime"]))
        lines.append("token=%s" % tok)
        lines.append("")
        lines.append("candidate pid | field6(sid) | field6==own pid | field22 | branch(a) | branch(b) | owned")
        n_a = n_b = n_owned = 0
        for c2, a, b in rows:
            owned = a or b
            n_a += bool(a)
            n_b += bool(b)
            n_owned += bool(owned)
            lines.append("%d | %d | %s | %d | %s | %s | %s"
                         % (c2["pid"], c2["sid"], "yes" if c2["sid"] == c2["pid"] else "no", c2["starttime"],
                            "FIRE" if a else "-", "FIRE" if b else "-", "yes" if owned else "no"))
        lines.append("")
        lines.append("PREDICATE-SUMMARY candidates=%d branch_a_fired=%d branch_b_fired=%d owned_total=%d "
                     "recorded_spawn_sid=%d" % (len(rows), n_a, n_b, n_owned, p["sid"]))
        # the escapee's session vs the recorded spawn session, side by side
        esc = [r for r in rows if r[0]["sid"] == r[0]["pid"]]
        if esc:
            lines.append("")
            lines.append("== session-leader candidates (a setsid escapee is one) ==")
            for c2, a, b in esc:
                lines.append("candidate pid=%d field6=%d (== own pid: yes) vs recorded spawn field6=%d -> "
                             "equal? %s ; ppid=%d parent_field6=%s"
                             % (c2["pid"], c2["sid"], p["sid"],
                                "yes" if c2["sid"] == p["sid"] else "no", c2["ppid"],
                                procs[c2["ppid"]]["sid"] if c2["ppid"] in procs else "gone"))
            lines.append("ESCAPEE-VERDICT %s"
                         % ("a session-leader candidate's field 6 equals the recorded spawn field 6"
                            if any(r[0]["sid"] == p["sid"] for r in esc)
                            else "NO session-leader candidate's field 6 equals the recorded spawn field 6 "
                                 "(each is its OWN pid): branch (b) cannot own a setsid escapee"))
    body = "\n".join(lines) + "\n"
    print(body)
    if ns.out:
        with open(ns.out, "w", encoding="utf-8") as f:
            f.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
