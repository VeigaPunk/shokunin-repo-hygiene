#!/usr/bin/env python3
"""ScoutSources (souji r100): re-open S075/S332/S368 and verify the field
claims used by the round-100 claims.

Claims under check:
  S075  /proc/<pid>/stat field 5  = pgrp     (process group ID)
  S075  /proc/<pid>/stat field 6  = session  (session ID)
  S075  /proc/<pid>/stat field 22 = starttime (start time after boot)
  S332  fs/proc/array.c do_task_stat() emits ppid, pgid, sid, ... start_time
        in exactly that order (so man field N == the Nth emitted scalar).
  S368  setsid(2) puts the caller in a new session and a new process group.

Usage:
  verify-source-fields.py --live-dir <dir> --capture-dir <lane> [--check-live]

Exits 0 only when every assertion holds. Prints one PASS/FAIL line per
assertion plus a summary line.
"""
import argparse
import hashlib
import html
import os
import re
import subprocess
import sys

SOURCES = {
    "S075": {
        "url": "https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html",
        "capture": "census/round-98/srcs/proc_pid_stat.5.html",
        "live_name": "live-s075.html",
    },
    "S332": {
        "url": "https://raw.githubusercontent.com/torvalds/linux/v6.17/fs/proc/array.c",
        "capture": "census/round-83/srcs/linux-array.c-v6.17",
        "live_name": "live-s332.html",
    },
    "S368": {
        "url": "https://man7.org/linux/man-pages/man2/setsid.2.html",
        "capture": "census/round-96/srcs/setsid.2.html",
        "live_name": "live-s368.html",
    },
}

FAILURES = []
CHECKS = 0


def check(ok, label, detail=""):
    global CHECKS
    CHECKS += 1
    if not ok:
        FAILURES.append(label)
    print("%-4s %s%s" % ("PASS" if ok else "FAIL", label,
                         ("  | " + detail) if detail else ""))


def flat_text(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    raw = re.sub(r"(?s)<script.*?</script>", "", raw)
    raw = re.sub(r"(?s)<style.*?</style>", "", raw)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    return re.sub(r"\s+", " ", raw)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def http_status(url):
    out = subprocess.run(
        ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
         "-A", "Mozilla/5.0 (souji-source-audit)", url],
        capture_output=True, text=True)
    return out.stdout.strip(), out.returncode


def do_task_stat_fields(src):
    """Return the ordered list of emitted field values inside do_task_stat().

    Field numbering follows /proc/<pid>/stat: 1=pid, 2=comm, 3=state, then the
    decimal scalars emitted by seq_put_decimal_ll/seq_put_decimal_ull in
    source order.  The kernel emits pid/comm/state first, so the Nth decimal
    scalar after 'state' is man field 4.
    """
    lines = src.splitlines()
    fn = next(i for i, l in enumerate(lines)
              if l.startswith("static int do_task_stat("))
    start = next(i for i in range(fn, len(lines))
                 if 'seq_put_decimal_ull(m, "", pid_nr_ns(pid, ns));' in lines[i])
    vals = []
    for l in lines[start:]:
        if "seq_putc(m, '\\n')" in l:
            break
        m = re.match(r'\s*seq_put_decimal_(?:ll|ull)\(m,\s*"[^"]*",\s*(.+)\);\s*$', l)
        if m:
            vals.append(m.group(1).strip())
    # man field 1 = pid (the first decimal emit), field 2 = comm and
    # field 3 = state are not decimal scalars, so the Nth decimal scalar
    # after the pid emit is man field N+3.
    fields = {}
    for i, v in enumerate(vals[1:]):
        fields[i + 4] = v
    return fields, vals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live-dir", required=True)
    ap.add_argument("--capture-dir", required=True)
    ap.add_argument("--check-live", action="store_true",
                    help="re-fetch the three URLs over HTTP and compare sha256")
    args = ap.parse_args()

    live = {}
    for key, spec in SOURCES.items():
        lp = os.path.join(args.live_dir, spec["live_name"])
        if not os.path.exists(lp):
            # accept the md5-named fetches too
            alt = [f for f in os.listdir(args.live_dir) if f.startswith("live-")]
            if alt:
                lp = os.path.join(args.live_dir, sorted(alt)[0])
            else:
                print("missing live copy for %s" % key)
                FAILURES.append("missing-live-%s" % key)
                continue
        live[key] = lp
        cp = os.path.join(args.capture_dir, spec["capture"])
        ls, cs = sha256(lp), sha256(cp)
        check(ls == cs, "%s live==capture sha256" % key,
              "live=%s capture=%s" % (ls[:16], cs[:16]))
        if args.check_live:
            st, rc = http_status(spec["url"])
            check(st == "200" and rc == 0, "%s HTTP status" % key,
                  "status=%s curl_rc=%d" % (st, rc))

    # ---- S075 ----
    if "S075" in live:
        t = flat_text(live["S075"])
        for fld, name, desc in (
            (5, "pgrp", "The process group ID of the process."),
            (6, "session", "The session ID of the process."),
            (22, "starttime", "The time the process started after system boot."),
            (4, "ppid", "The PID of the parent of this process."),
        ):
            q = "(%d) %s " % (fld, name)
            occ = t.count(q)
            check(occ == 1, "S075 field %d header unique (%s)" % (fld, name),
                  "occ=%d quote=%r" % (occ, q))
            check(t.count(desc) == 1,
                  "S075 field %d description unique (%s)" % (fld, name),
                  "occ=%d quote=%r" % (t.count(desc), desc))

    # ---- S332 ----
    if "S332" in live:
        src = open(live["S332"], encoding="utf-8", errors="replace").read()
        fields, allvals = do_task_stat_fields(src)
        check(fields.get(4) == "ppid", "S332 emission slot 4 == ppid",
              "got=%r" % fields.get(4))
        check(fields.get(5) == "pgid", "S332 emission slot 5 == pgid",
              "got=%r" % fields.get(5))
        check(fields.get(6) == "sid", "S332 emission slot 6 == sid",
              "got=%r" % fields.get(6))
        check(fields.get(22) == "start_time", "S332 emission slot 22 == start_time",
              "got=%r" % fields.get(22))
        check(src.count("sid = task_session_nr_ns(task, ns);") == 1,
              "S332 sid source unique",
              "occ=%d" % src.count("sid = task_session_nr_ns(task, ns);"))
        check(src.count("pgid = task_pgrp_nr_ns(task, ns);") == 1,
              "S332 pgid source unique",
              "occ=%d" % src.count("pgid = task_pgrp_nr_ns(task, ns);"))

    # ---- S368 ----
    if "S368" in live:
        t = flat_text(live["S368"])
        q1 = ("The calling process is the leader of the new session "
              "(i.e., its session ID is made the same as its process ID).")
        q2 = ("The calling process also becomes the process group leader of "
              "a new process group in the session")
        check(t.count(q1) == 1, "S368 new-session quote unique",
              "occ=%d" % t.count(q1))
        check(t.count(q2) == 1, "S368 new-process-group quote unique",
              "occ=%d" % t.count(q2))
        check("setsid () creates a new session if the calling process is not a "
              "process group leader." in t,
              "S368 creates a new session")

    print("SUMMARY checks=%d failures=%d" % (CHECKS, len(FAILURES)))
    if FAILURES:
        for f in FAILURES:
            print("FAILED: %s" % f)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
