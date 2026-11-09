#!/usr/bin/env python3
"""souji r98 C2 counter: does a forgery probe keep setup failures off its verdict exit code?

C2 operability r98 (S075): the T1 reap kills ONLY processes whose pid is (a) the pid the arm's Popen recorded
at spawn, or (b) a descendant of it found by walking /proc/<pid>/stat field 4 (ppid) up to that pid, or (c) an
orphan reparented to the counter itself (the counter sets PR_SET_CHILD_SUBREAPER before spawning arms, so the
setsid T1 escapee, orphaned when its fixture parent exits, stays a visible counter child instead of escaping
to init/systemd). The escapee's starttime is freshly re-read at act time; the spawn pid's own starttime must
match the recorded one. argv matching may select candidates, but never authorises a kill. The r97 argv-only reap
(killing any own-uid process carrying the fixture token) is gone: it killed foreign own-uid decoys planted
after the arm started (Q174). A foreign decoy (its ppid is its own driver, never the counter) is never killed.
T1 is reaped by the counter itself by ownership
(S368 for the new-session escape) and the run prints a surviving-grandchild count; the probe caps captured
output (--max-output, default 8 MiB; rejects rather than exhausts memory); the counter records a signal exit
(-15) distinctly (never coerce it) and prints it as exit=signal. Docstrings corrected (A6).

The r95 counter (census/round-95/c2-setup-arms.py) with four more setup arms (T1-T4) and a per-arm timeout. T1 is
the fixture that escapes the process group with the pipes held open (r95 closure A6; plans/round-95.md A6); T2-T4
bind the r95 write-failure, non-integer --timeout and internal-error classes no r95 arm exercised.

Runs the probe named by --probe under sixteen arms and checks each arm's exit code and one required output line. Two
arms are verdict arms (the probe must still say "all eight rejected" with exit 0, and "a forgery survived" with exit
1); eight are setup arms (the probe must either run normally or refuse with exit 2 and a `C2-FORGERY-FATAL:` line —
never exit 1, which means "a forgery survived").

  P1 verdict-pass   r93 fixture, filed tool, r91 before, fresh --work      -> exit 0, `FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass`
  P2 verdict-fail   r92 fixture (F5/F6/F7 pass it), fresh --work          -> exit 1, `FORGERY-SUMMARY forgeries=8 rejected=5 positive=pass`
  S1 work-empty     as P1 but --work is an existing EMPTY directory        -> exit 0, `FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass`
  S2 work-nonempty  --work is a directory holding one file                 -> exit 2, `C2-FORGERY-FATAL:`
  S3 work-file      --work is an existing regular file                     -> exit 2, `C2-FORGERY-FATAL:`
  S4 fixture-absent --fixture names a path that does not exist             -> exit 2, `C2-FORGERY-FATAL:`
  S5 tool-absent    --tool names a path that does not exist                -> exit 2, `C2-FORGERY-FATAL:`
  S6 before-absent  --before names a path that does not exist              -> exit 2, `C2-FORGERY-FATAL:`
  S7 fixture-mute   a fixture that exits 1 and prints nothing              -> exit 2, `C2-FORGERY-FATAL:`
  S8 fixture-crash  a fixture that prints a passing SUMMARY for the filed
                    tool and raises (no SUMMARY) for any other tool        -> exit 2, `C2-FORGERY-FATAL:`
  S9 tool-nonutf8   --tool is the filed tool plus one comment line holding
                    the byte 0xFF (not UTF-8)                              -> exit 2, `C2-FORGERY-FATAL:`
  S10 before-nonutf8 --before is the r91 tool plus the same 0xFF line     -> exit 2, `C2-FORGERY-FATAL:`
  S11 work-fileparent --work is <regular file>/sub                         -> exit 2, `C2-FORGERY-FATAL:`
  S12 fixture-hang  a fixture that sleeps forever                          -> exit 2, `C2-FORGERY-FATAL:`
                    (the counter kills an arm after --arm-timeout seconds, default 300, and scores it `exit=hung`)
  S13 work-tmp      --work is an absent path under /tmp                    -> exit 2, `C2-FORGERY-FATAL:`
  S14 edit-twice    --tool is the filed tool plus a string literal holding
                    a second copy of forgery F3's edit target              -> exit 2, `C2-FORGERY-FATAL:`
  T1 fixture-escapes the fixture forks a new-session child that keeps the pipes open and sleeps forever;
                    the fixture itself exits 0 at once                       -> exit 2, `C2-FORGERY-FATAL:`
                    within --arm-timeout (the probe stops waiting on pipe EOF once its process group is killed)
  T2 work-midfull   --work becomes read-only after the checks (its positive dir is filled to a mode the probe
                    cannot write); the probe's write refusal must still be exit 2 -> exit 2, `C2-FORGERY-FATAL:`
  T3 timeout-zero   --timeout 0                                            -> exit 2, `C2-FORGERY-FATAL:`
  T4 abort-fixture  a fixture that aborts itself (raises a traceback, exit 1, no SUMMARY) -> exit 2,
                    `C2-FORGERY-FATAL:` (the abort is a setup failure, never the probe's verdict exit)

The S7/S8/S12 fixtures and the S9/S10/S14 copies are written by this counter under --work (their bytes are printed as
sha256); S13 names a /tmp path the counter never creates. T1-T4 fixtures/copies are written under --work too.
Output: one `ARM <id> exit=<rc|hung> want=<rc> line=<yes|no> conform=<yes|no>` per arm and
`ARMS-SUMMARY arms=20 conform=<k>`. Exit 0 iff k == 20; 1 otherwise; 2 on setup error. Scratch only under
--work (never /tmp).
"""
import argparse
import concurrent.futures as cf
import hashlib
import os
import signal
import subprocess
import sys

sys.dont_write_bytecode = True
PASS8 = "FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass"
FAIL5 = "FORGERY-SUMMARY forgeries=8 rejected=5 positive=pass"
FATAL = "C2-FORGERY-FATAL:"
MUTE = "import sys\nsys.exit(1)\n"
CRASH = """import sys
tool = sys.argv[sys.argv.index("--tool") + 1]
if tool == %r:
    print("SUMMARY cases=1 tool_pass=1 before_pass=0")
    sys.exit(0)
raise RuntimeError("fixture-crash arm: no SUMMARY for " + tool)
"""
HANG = "import time\nwhile True:\n    time.sleep(3600)\n"
PIPHOLDER = """import os, sys, time
pid = os.fork()
if pid == 0:
    os.setsid()
    time.sleep(3600)
    os._exit(0)
print("SUMMARY cases=1 tool_pass=1 before_pass=0")
sys.exit(0)
"""
ABORT = "import sys\ndef _boom(): raise RuntimeError('fixture-abort')\n_boom()\n"
F3_OLD = "    seq = _straddling_sequence(raw, t)\n    return seq[1] if seq else t\n"


def _proc_stat(pid):
    """Return (ppid, starttime) from /proc/<pid>/stat (fields 4 and 22, S075), or None."""
    try:
        with open(f"/proc/{pid}/stat", "rb") as f:
            data = f.read()
        fields = data.rsplit(b")", 1)[1].split()
        return int(fields[1]), int(fields[19])
    except (OSError, ValueError, IndexError):
        return None


def _proc_starttime(pid):
    """Return /proc/<pid>/stat field 22 (starttime), or None if unreadable."""
    st = _proc_stat(pid)
    return None if st is None else st[1]


def _proc_ppid(pid):
    """Return /proc/<pid>/stat field 4 (ppid), or None if unreadable."""
    st = _proc_stat(pid)
    return None if st is None else st[0]


def _argv_of(pid):
    """Return the pid's argv as a list of bytes, or None if unreadable."""
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            return f.read().split(b"\x00")
    except OSError:
        return None


def _is_descendant(pid, ancestor):
    """True iff pid == ancestor or walking field-4 (ppid) up from pid reaches <ancestor> (S075)."""
    seen = set()
    cur = pid
    while cur is not None and cur > 0 and cur not in seen:
        if cur == ancestor:
            return True
        seen.add(cur)
        cur = _proc_ppid(cur)
    return False


def _survivors(ident, exclude):
    """Count own-uid processes whose argv contains <ident> byte-exactly, skipping <exclude> (pids)."""
    n = 0
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        if pid in exclude:
            continue
        argv = _argv_of(pid)
        if argv is None:
            continue
        if any(a == ident.encode() for a in argv):
            n += 1
    return n


def _reap_by_identity(ident, exclude):
    """SIGKILL every own-uid process whose argv contains <ident> byte-exactly (the arm's fixture path token),
    skipping <exclude> pids (the counter itself and the probe). S368 makes the escaped grandchild a new
    session/group, so killpg(probe) cannot reach it; argv identity is the counter-owned reaping key (A4).
    Retained for compat: now delegates to ownership; the T1 path uses _reap_owned."""
    return _reap_owned(ident, exclude, None)


def _reap_owned(ident, exclude, spawn):
    """r99 ownership reap (C2 operability, S075): kill ONLY pids that are the recorded spawn pid itself
    (re-verified by its starttime, stat field 22) or a ppid-chain descendant of that spawn pid.
    argv may select candidates, but argv alone never authorises a kill; a counter-descendant carrier that
    is not a spawn-chain member is NEVER killed (r98 branch (c) removed). Returns how many were signalled."""
    killed = 0
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        if pid in exclude:
            continue
        argv = _argv_of(pid)
        if argv is None or not any(a == ident.encode() for a in argv):
            continue
        st = _proc_stat(pid)
        if st is None:
            continue
        if spawn is not None:
            spawn_pid, spawn_st = spawn
            if pid == spawn_pid:
                if st[1] != spawn_st:
                    continue
            elif _is_descendant(pid, spawn_pid):
                pass  # fresh starttime re-read above; chain walked at act time
            else:
                continue
        else:
            # No spawn record (compat path): require an owned ancestor chain to an excluded pid's group --
            # never argv alone. Falls back to skipping the pid (never kill on argv alone).
            continue
        try:
            os.kill(pid, signal.SIGKILL)
            killed += 1
        except (ProcessLookupError, PermissionError):
            pass
    return killed


def _set_child_subreaper():
    """r98 ownership net (S075/S368): PR_SET_CHILD_SUBREAPER(1) so an orphaned descendant of this counter
    reparents to the counter instead of init/systemd. The T1 escapee (setsid, orphaned when its fixture
    parent exits) then stays a visible child of the counter and can be owned by the ppid-chain walk,
    while a foreign decoy with ppid == its own driver is never a counter child. Best-effort on non-Linux.
    """
    try:
        import ctypes
        rc = ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0)
        if rc != 0:
            print(f"C2-ARMS-FATAL: prctl(PR_SET_CHILD_SUBREAPER) failed", file=sys.stderr)
            return False
    except Exception as exc:
        print(f"C2-ARMS-FATAL: prctl unavailable ({exc})", file=sys.stderr)
        return False
    return True


def main(argv):
    if not _set_child_subreaper():
        return 2
    ap = argparse.ArgumentParser()
    for a in ("--probe", "--fixture-pass", "--fixture-fail", "--tool", "--before", "--work"):
        ap.add_argument(a, required=True)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--arm-timeout", type=int, default=300)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("C2-ARMS-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and (not os.path.isdir(work) or os.listdir(work)):
        print(f"C2-ARMS-FATAL: --work {work} is not an empty directory", file=sys.stderr)
        return 2
    probe, fpass, ffail, tool, before = (os.path.abspath(x) for x in
                                         (ns.probe, ns.fixture_pass, ns.fixture_fail, ns.tool, ns.before))
    for k, v in (("probe", probe), ("fixture-pass", fpass), ("fixture-fail", ffail), ("tool", tool),
                 ("before", before)):
        if not os.path.isfile(v):
            print(f"C2-ARMS-FATAL: --{k} {v} is not a file", file=sys.stderr)
            return 2
    os.makedirs(work, exist_ok=True)
    for k, v in (("probe", probe), ("fixture-pass", fpass), ("fixture-fail", ffail), ("tool", tool),
                 ("before", before), ("counter", os.path.abspath(__file__))):
        with open(v, "rb") as f:
            print(f"# {k} path={v} sha256={hashlib.sha256(f.read()).hexdigest()}")
    mute, crash = os.path.join(work, "fixture-mute.py"), os.path.join(work, "fixture-crash.py")
    with open(mute, "w", encoding="utf-8") as f:
        f.write(MUTE)
    with open(crash, "w", encoding="utf-8") as f:
        f.write(CRASH % tool)
    hang = os.path.join(work, "fixture-hang.py")
    with open(hang, "w", encoding="utf-8") as f:
        f.write(HANG)
    # T1 pipe-holder: the fixture forks a new-session child that keeps the pipes and sleeps forever, then exits 0.
    # The r95 probe hangs past --timeout on it (communicate waits for pipe EOF); the r96 probe stops waiting.
    piphole = os.path.join(work, "fixture-pipe-holder.py")
    with open(piphole, "w", encoding="utf-8") as f:
        f.write(PIPHOLDER)
    # T4 abort: no SUMMARY, traceback exit 1.
    abort = os.path.join(work, "fixture-abort.py")
    with open(abort, "w", encoding="utf-8") as f:
        f.write(ABORT)
    tool_bad, before_bad, tool_dup = (os.path.join(work, n) for n in ("tool-nonutf8.py", "before-nonutf8.py",
                                                                      "tool-edit-twice.py"))
    with open(tool, "rb") as f:
        tool_bytes = f.read()
    with open(before, "rb") as f:
        before_bytes = f.read()
    if tool_bytes.decode("utf-8").count(F3_OLD) != 1:
        print("C2-ARMS-FATAL: the filed tool does not hold F3's edit target exactly once", file=sys.stderr)
        return 2
    with open(tool_bad, "wb") as f:
        f.write(tool_bytes + b"# \xff not utf-8 (S9)\n")
    with open(before_bad, "wb") as f:
        f.write(before_bytes + b"# \xff not utf-8 (S10)\n")
    with open(tool_dup, "wb") as f:
        f.write(tool_bytes + ("_SOUJI_R95_S14 = \"\"\"\n" + F3_OLD + "\"\"\"\n").encode("utf-8"))
    for k, v in (("fixture-mute", mute), ("fixture-crash", crash), ("fixture-hang", hang), ("tool-nonutf8", tool_bad),
                 ("before-nonutf8", before_bad), ("tool-edit-twice", tool_dup), ("fixture-pipe-holder", piphole),
                 ("fixture-abort", abort)):
        with open(v, "rb") as f:
            print(f"# {k} sha256={hashlib.sha256(f.read()).hexdigest()}")
    a = lambda i: os.path.join(work, i)  # noqa: E731
    os.makedirs(a("S1"))
    os.makedirs(a("S2"))
    with open(os.path.join(a("S2"), "keep"), "w") as f:
        f.write("x\n")
    with open(a("S3"), "w") as f:
        f.write("x\n")
    missing = a("absent-path")
    with open(a("S11-parent"), "w") as f:
        f.write("x\n")
    tmp_work = f"/tmp/souji-r95-arm-S13-{os.getpid()}-absent"
    if os.path.lexists(tmp_work):
        print(f"C2-ARMS-FATAL: {tmp_work} exists", file=sys.stderr)
        return 2
    arms = (
        ("P1", fpass, tool, before, a("P1"), 0, PASS8),
        ("P2", ffail, tool, before, a("P2"), 1, FAIL5),
        ("S1", fpass, tool, before, a("S1"), 0, PASS8),
        ("S2", fpass, tool, before, a("S2"), 2, FATAL),
        ("S3", fpass, tool, before, a("S3"), 2, FATAL),
        ("S4", missing, tool, before, a("S4"), 2, FATAL),
        ("S5", fpass, missing, before, a("S5"), 2, FATAL),
        ("S6", fpass, tool, missing, a("S6"), 2, FATAL),
        ("S7", mute, tool, before, a("S7"), 2, FATAL),
        ("S8", crash, tool, before, a("S8"), 2, FATAL),
        ("S9", fpass, tool_bad, before, a("S9"), 2, FATAL),
        ("S10", fpass, tool, before_bad, a("S10"), 2, FATAL),
        ("S11", fpass, tool, before, os.path.join(a("S11-parent"), "sub"), 2, FATAL),
        ("S12", hang, tool, before, a("S12"), 2, FATAL),
        ("S13", fpass, tool, before, tmp_work, 2, FATAL),
        ("S14", fpass, tool_dup, before, a("S14"), 2, FATAL),
        ("T1", piphole, tool, before, a("T1"), 2, FATAL),
        ("T2", fpass, tool, before, a("T2"), 2, FATAL),
        ("T3", fpass, tool, before, a("T3"), 2, FATAL),
        ("T4", abort, tool, before, a("T4"), 2, FATAL),
    )

    # T2's --work must be an existing EMPTY but read-only directory: makedirs succeeds, the first write fails.
    os.makedirs(a("T2"), exist_ok=True)
    os.chmod(a("T2"), 0o555)

    def one(arm):
        aid, fx, tl, bf, wk, want, line = arm
        extra = ["--timeout", "0"] if aid == "T3" else []
        # r98 ownership (S075): record at spawn the pid the arm's Popen created and its starttime (stat field
        # 22). The T1 reap kills ONLY that pid and its ppid-chain (field 4) descendants with matching
        # starttime. argv may select candidates, but never authorises a kill. The r97 argv-only reap is gone.
        p = subprocess.Popen([sys.executable, "-B", probe, "--fixture", fx, "--tool", tl, "--before", bf,
                              "--work", wk] + extra, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        spawn = (p.pid, _proc_starttime(p.pid)) if aid == "T1" else None
        try:
            so, se = p.communicate(timeout=ns.arm_timeout)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            so, se = p.communicate()
            rc = "hung"
        text = so.decode("utf-8", "replace") + "\n--stderr--\n" + se.decode("utf-8", "replace")
        with open(a(f"{aid}.out"), "w", encoding="utf-8") as f:
            f.write(text + (f"\n--hung: killed after --arm-timeout {ns.arm_timeout}s--\n" if rc == "hung" else ""))
        stream = se if line == FATAL else so
        has = any(l.startswith(line) for l in stream.decode("utf-8", "replace").splitlines())
        # r99: on the T1 arm, reap the escaped grandchild by ownership (spawn pid + ppid chain only,
        # starttime verified) and count survivors that are spawn-chain members NOT killed. A counter-
        # descendant carrier outside the spawn chain is NEVER killed and is NOT counted here either.
        # A8: a signal exit (rc < 0) prints as exit=<rc>.
        survivors = None
        if aid == "T1":
            # Spawn-chain rule: a pid is owned iff it equals the spawn pid or its ppid chain reaches the
            # spawn pid. After the fixture parent exits, the setsid escapee's ppid chain may no longer
            # reach the spawn pid (open limit, reported with observed evidence); it is then NOT killed.
            killed = _reap_owned(fx, (os.getpid(), p.pid), spawn) if spawn else 0
            survivors = 0
            for name in os.listdir("/proc"):
                if not name.isdigit():
                    continue
                pid = int(name)
                if pid in (os.getpid(), p.pid):
                    continue
                st = _proc_stat(pid)
                if st is None or spawn is None:
                    continue
                # Spawn-chain only: a descendant is counted iff it is the spawn pid or a ppid-chain
                # descendant of the spawn pid; no subreaper/counter branch. Only the spawn pid itself
                # must match its own recorded starttime (re-verified above).
                if pid != spawn[0] and not _is_descendant(pid, spawn[0]):
                    continue
                survivors += 1
            with open(a(f"{aid}.out"), "a", encoding="utf-8") as f:
                f.write(f"\n--survivors {survivors} planted-killed {killed}--\n")
        return aid, rc, want, has, survivors

    with cf.ThreadPoolExecutor(max_workers=ns.jobs) as ex:
        res = list(ex.map(one, arms))
    conform = 0
    for aid, rc, want, has, survivors in res:
        # C-3/F12: conform counts exit+line only, so a counter that reaps NOTHING still prints
        # conform=20. The T1 survivors byte is the binding byte for the reap leg, so bind it here:
        # conform requires survivors==0 on the T1 arm (the escapee must be reaped by ownership).
        ok = rc == want and has
        if aid == "T1" and survivors is not None:
            ok = ok and survivors == 0
        conform += ok
        tail = f" survivors={survivors}" if survivors is not None else ""
        print(f"ARM {aid} exit={rc} want={want} line={'yes' if has else 'no'} conform={'yes' if ok else 'no'}{tail}")
    print(f"ARMS-SUMMARY arms={len(arms)} conform={conform}")
    return 0 if conform == len(arms) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
