#!/usr/bin/env python3
"""souji r80 C2 counter: what tools/souji-quarantine.sh does when its caller signals it while a bounded child it
started is blocked, under --dry-run (the tool's default operating mode).

Successor of the r79 C1 instrument (census/round-79/c1-signal-counter.py, frozen and unchanged), carrying the r79
lesson's fixes M1-M3 and the r79 spot-check's routed defects 1 and 3:
  * every receipt starts with a column-0 `# launch` line: the counter's own inherited signal dispositions
    (SigIgn/SigBlk), process group, session, whether stdin is a tty, and the terminal's foreground group when
    there is one;
  * every tool child starts with SIGINT, SIGQUIT, SIGTERM and SIGHUP reset to SIG_DFL and unblocked (preexec), and
    the row prints the tool's SigIgn read from /proc at the moment of delivery; a row whose signal is ignored at
    delivery is an ERROR (an instrument condition), never a verdict about the tool;
  * the hang point is asserted: each shim writes a mark naming the program, its argv, its working directory and
    the comm of its parent and grandparent; the row is an ERROR unless the mark is the labelled call (M1: the r79
    shim matched its pattern anywhere in argv, including a row directory name);
  * every row has a wall-clock bound (ROW_BOUND), and cleanup kills every process carrying the row nonce,
    whatever its process group or session.

Rows (frozen in census/round-80/c2-population.tsv, which must equal ROUTES):
  point engine      the receipt engine (SOUJI_VERIFY_BIN = a stub that marks then sleeps), file target
  point file-digest the stage-1 file digest `sha256sum -- <target>` (shim on the exact last argument), file target
  point dir-scan    the stage-1 special-file pre-flight `find <target> ... -quit` (shim on argv[1] and -quit)
  point dir-digest  the directory digest pipeline's `sort -z` (shim on cwd == target), directory target
  p1/p2/p3          no signal (file / directory / directory with the SAFE stub): the dry-run verdict and exit code
                    equal the frozen `<verdict>/<rc>` expectation (the base tool's own), no SIGNAL line, nothing left
                    running, nothing left in TMPDIR (positive controls: a tool that refuses everything fails them).
A signal row matches iff the tool exits within SETTLE seconds of the signal with status 128 + the signal
number, prints the line `SIGNAL<TAB>SIG<name><TAB>RECEIPT-QUARANTINE-SIGNALED`, no process carrying the row
nonce is alive SETTLE seconds after the signal, and the row's private TMPDIR is empty.
Output: one `ROW ...` line per row, then `SUMMARY rows=<N> mismatches=<M> errors=<E> orphans=<O>`.
Exit 0 iff M == 0 and E == 0; 1 otherwise; 2 usage/fatal.

Run it in the foreground or not: dispositions are reset per child. A SIGKILL to the tool is not a row (cannot be
trapped); a descendant that leaves the tool's session itself (setsid, double fork into another session) is a
stated limit, not a row.
"""
import argparse
import hashlib
import os
import secrets
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SETTLE = 5.0
MARK_TIMEOUT = 60.0
ROW_BOUND = 90.0
CLASS = "RECEIPT-QUARANTINE-SIGNALED"
SIGS = {"TERM": signal.SIGTERM, "INT": signal.SIGINT, "HUP": signal.SIGHUP, "-": None}
RESET = (signal.SIGINT, signal.SIGQUIT, signal.SIGTERM, signal.SIGHUP)
IDENT = {"GIT_AUTHOR_NAME": "r80 fixture", "GIT_AUTHOR_EMAIL": "fixture@r80.invalid",
         "GIT_COMMITTER_NAME": "r80 fixture", "GIT_COMMITTER_EMAIL": "fixture@r80.invalid",
         "GIT_AUTHOR_DATE": "2026-11-07T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-07T00:00:00Z"}

# id, signal, point, target kind, engine (real = the measured souji-verify.sh; hang = a stub that marks and
# blocks; safe = a stub printing one SAFE(stale) verdict record, so a directory reaches its stage-1 digest), expected
ROUTES = [
    ("q1-term-engine", "TERM", "engine", "file", "hang", "SIGNALED"),
    ("q2-int-engine", "INT", "engine", "file", "hang", "SIGNALED"),
    ("q3-hup-engine", "HUP", "engine", "file", "hang", "SIGNALED"),
    ("q4-term-file-digest", "TERM", "file-digest", "file", "real", "SIGNALED"),
    ("q5-int-file-digest", "INT", "file-digest", "file", "real", "SIGNALED"),
    ("q6-hup-file-digest", "HUP", "file-digest", "file", "real", "SIGNALED"),
    ("q7-term-dir-scan", "TERM", "dir-scan", "dir", "real", "SIGNALED"),
    ("q8-int-dir-scan", "INT", "dir-scan", "dir", "real", "SIGNALED"),
    ("q9-hup-dir-scan", "HUP", "dir-scan", "dir", "real", "SIGNALED"),
    ("q10-term-dir-digest", "TERM", "dir-digest", "dir", "safe", "SIGNALED"),
    ("q11-int-dir-digest", "INT", "dir-digest", "dir", "safe", "SIGNALED"),
    ("q12-hup-dir-digest", "HUP", "dir-digest", "dir", "safe", "SIGNALED"),
    ("p1-file-no-signal", "-", "-", "file", "real", "DRY-RUN-PASS/0"),
    ("p2-dir-no-signal", "-", "-", "dir", "real", "DRY-RUN-BLOCKED/3"),
    ("p3-dir-safe-no-signal", "-", "-", "dir", "safe", "DRY-RUN-PASS/0"),
]
# point -> (program that must have written the mark, the parent comm chain it must show)
MARKS = {"engine": ("engine", ("timeout",)), "file-digest": ("sha256sum", ("timeout",)),
         "dir-scan": ("find", ("timeout",)), "dir-digest": ("sort", ("bash", "timeout"))}

MARK_FN = r'''r80_mark() {  # $1 program name, rest = argv
  local name=$1 pc gc gp; shift
  pc=$(cat /proc/$PPID/comm 2>/dev/null); gp=$(awk '{print $4}' /proc/$PPID/stat 2>/dev/null)
  gc=$(cat /proc/$gp/comm 2>/dev/null)
  { printf 'prog=%s\n' "$name"; printf 'parent=%s\n' "$pc"; printf 'grandparent=%s\n' "$gc"
    printf 'cwd=%s\n' "$PWD"; printf 'argv=%s\n' "$*"; } > "$SOUJI_R80_MARK.tmp"
  mv -f "$SOUJI_R80_MARK.tmp" "$SOUJI_R80_MARK"
}
'''
SHIMS = {
    # the stage-1 file digest: `sha256sum -- <target>`, exact last argument
    "sha256sum": r'''last=; for last in "$@"; do :; done
if [[ ${SOUJI_R80_POINT:-} == file-digest && $last == "$SOUJI_R80_TARGET" ]]; then r80_mark sha256sum "$@"; exec sleep 600; fi
''',
    # the pre-flight scan: `find <target> ... -quit`
    "find": r'''if [[ ${SOUJI_R80_POINT:-} == dir-scan && ${1:-} == "$SOUJI_R80_TARGET" && " $* " == *" -quit "* ]]; then r80_mark find "$@"; exec sleep 600; fi
''',
    # the directory digest pipeline runs in the target directory: `sort -z`
    "sort": r'''if [[ ${SOUJI_R80_POINT:-} == dir-digest && $PWD == "$SOUJI_R80_TARGET" && " $* " == *" -z "* ]]; then r80_mark sort "$@"; exec sleep 600; fi
''',
}
ENGINE_STUB = r'''#!/bin/bash
# r80 hanging receipt-engine stub: marks, then blocks
''' + MARK_FN + r'''r80_mark engine "$@"
exec sleep 600
'''
SAFE_STUB = r'''#!/bin/bash
# r80 receipt-engine stub: one SAFE(stale) verdict record for the last argument (the target)
last=; for last in "$@"; do :; done
printf 'VERDICT\t%s\tSAFE\tstale\tr80-safe-stub\n' "$last"
'''


class FixtureError(Exception):
    pass


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def which(name):
    for d in os.environ.get("PATH", "").split(os.pathsep):
        p = os.path.join(d, name)
        if d and os.path.isfile(p) and os.access(p, os.X_OK):
            return os.path.realpath(p)
    raise FixtureError(f"{name} not on PATH")


def proc_status(pid, *keys):
    out = {}
    try:
        with open(f"/proc/{pid}/status", encoding="ascii", errors="replace") as f:
            for l in f:
                k, _, v = l.partition(":")
                if k in keys:
                    out[k] = v.strip()
    except OSError:
        pass
    return out


def launch_line():
    st = proc_status(os.getpid(), "SigIgn", "SigBlk")
    try:
        tty = os.isatty(0)
        fg = os.tcgetpgrp(0) if tty else "-"
    except OSError:
        tty, fg = False, "-"
    return (f"# launch pid={os.getpid()} pgid={os.getpgrp()} sid={os.getsid(0)} stdin_tty={'y' if tty else 'n'} "
            f"tty_fg_pgid={fg} sigign={st.get('SigIgn', '?')} sigblk={st.get('SigBlk', '?')}")


def make_shims(shimdir):
    os.makedirs(shimdir)
    for name, body in SHIMS.items():
        p = os.path.join(shimdir, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write("#!/bin/bash\n" + MARK_FN + body + f"exec {which(name)} \"$@\"\n")
        os.chmod(p, 0o755)
    stubs = {}
    for kind, body in (("hang", ENGINE_STUB), ("safe", SAFE_STUB)):
        stubs[kind] = os.path.join(shimdir, f"engine-{kind}.sh")
        with open(stubs[kind], "w", encoding="utf-8") as f:
            f.write(body)
        os.chmod(stubs[kind], 0o755)
    return stubs


def git(repo, *args):
    if not repo or not os.path.isabs(repo):
        raise FixtureError(f"refusing git -C with {repo!r}")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(IDENT, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, LC_ALL="C")
    p = subprocess.run(["git", "-C", repo, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if p.returncode != 0:
        raise FixtureError(f"git {' '.join(args)} rc={p.returncode}: {p.stderr.decode()[:200]}")
    return p.stdout.decode().strip()


def aged(path):
    t = time.time() - 3 * 86400
    os.utime(path, (t, t), follow_symlinks=False)


def build(rowdir, kind):
    fleet = os.path.join(rowdir, "fleet")
    repo = os.path.join(fleet, "repo")
    os.makedirs(repo)
    git(fleet, "init", "-q", "--initial-branch=master", repo)
    if os.path.realpath(git(repo, "rev-parse", "--show-toplevel")) != os.path.realpath(repo):
        raise FixtureError("fixture toplevel is not the fixture repo")
    ledger = os.path.join(rowdir, "ledger.tsv")
    with open(ledger, "w", encoding="utf-8") as f:
        f.write("source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n")
    os.makedirs(os.path.join(repo, ".scratch"))
    if kind == "file":
        target = os.path.join(repo, ".scratch", "aged.dat")
        with open(target, "w", encoding="utf-8") as f:
            f.write("r80 C2 aged file payload\n")
        aged(target)
    else:
        target = os.path.join(repo, ".scratch", "ageddir")
        os.makedirs(target)
        for n in ("a.dat", "b.dat"):
            with open(os.path.join(target, n), "w", encoding="utf-8") as f:
                f.write(f"r80 C2 aged dir payload {n}\n")
            aged(os.path.join(target, n))
        aged(target)
    aged(os.path.join(repo, ".scratch"))
    return fleet, repo, ledger, target


def nonce_pids(nonce):
    key = f"SOUJI_R80_NONCE={nonce}".encode()
    found = []
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            with open(f"/proc/{d}/environ", "rb") as f:
                env = f.read().split(b"\0")
            with open(f"/proc/{d}/stat", "rb") as f:
                state = f.read().rsplit(b")", 1)[1].split()[0]
        except OSError:
            continue
        if key in env and state != b"Z":
            found.append(int(d))
    return found


def reap(nonce):
    for _ in range(5):
        pids = nonce_pids(nonce)
        if not pids:
            return
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        time.sleep(0.1)


def _preexec():
    for s in RESET:
        signal.signal(s, signal.SIG_DFL)
    signal.pthread_sigmask(signal.SIG_UNBLOCK, RESET)


def read_mark(mark):
    out = {}
    with open(mark, encoding="utf-8", errors="replace") as f:
        for l in f:
            k, _, v = l.rstrip("\n").partition("=")
            out[k] = v
    return out


def run_row(tool, engine, stubs, rowdir, rid, sig, point, kind, ekind, expect, shimdir):
    fleet, repo, ledger, target = build(rowdir, kind)
    tmpdir = os.path.join(rowdir, "tmp")
    os.makedirs(tmpdir)
    nonce = secrets.token_hex(8)
    mark = os.path.join(rowdir, "hang.mark")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SOUJI_"))}
    env.update({"PATH": shimdir + os.pathsep + os.environ.get("PATH", ""), "TMPDIR": tmpdir, "LC_ALL": "C",
                "SOUJI_R80_NONCE": nonce, "SOUJI_R80_MARK": mark, "SOUJI_R80_TARGET": target,
                "SOUJI_VERIFY_BIN": engine if ekind == "real" else stubs[ekind],
                "SOUJI_Q_SHOKUNIN_ROOT": fleet, "SOUJI_Q_LEDGER": ledger,
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    if point != "-":
        env["SOUJI_R80_POINT"] = point
    argv = ["bash", tool, "--dry-run", repo, target]
    outp, errp = os.path.join(rowdir, "tool.out"), os.path.join(rowdir, "tool.err")
    t0 = time.monotonic()
    with open(outp, "wb") as fo, open(errp, "wb") as fe:
        p = subprocess.Popen(argv, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL, env=env,
                             start_new_session=True, cwd=rowdir, preexec_fn=_preexec)
    exited, secs, ign, where = False, 0.0, "-", "-"
    try:
        if SIGS[sig] is None:
            try:
                p.wait(timeout=MARK_TIMEOUT)
                exited = True
            except subprocess.TimeoutExpired:
                pass
            secs = time.monotonic() - t0
            if os.path.exists(mark):
                raise FixtureError("a shim marked on a no-signal row")
        else:
            while not os.path.exists(mark) and p.poll() is None and time.monotonic() - t0 < MARK_TIMEOUT:
                time.sleep(0.05)
            if not os.path.exists(mark):
                raise FixtureError("hang point never reached (tool exited or mark timeout)")
            m = read_mark(mark)
            prog, chain = MARKS[point]
            got_chain = (m.get("parent", ""),) if len(chain) == 1 else (m.get("parent", ""), m.get("grandparent", ""))
            where = f"{m.get('prog')}<{'<'.join(got_chain)}"
            if m.get("prog") != prog or got_chain != chain:
                raise FixtureError(f"blocked at {where} argv={m.get('argv', '')[:120]!r}, not the labelled "
                                   f"{prog}<{'<'.join(chain)}")
            time.sleep(0.3)
            ign = proc_status(p.pid, "SigIgn").get("SigIgn", "?")
            try:
                if int(ign, 16) & (1 << (int(SIGS[sig]) - 1)):
                    raise FixtureError(f"SIG{sig} ignored by the tool at delivery (SigIgn={ign})")
            except ValueError:
                raise FixtureError(f"tool SigIgn unreadable at delivery ({ign})")
            t1 = time.monotonic()
            os.kill(p.pid, SIGS[sig])
            try:
                p.wait(timeout=SETTLE)
                exited = True
            except subprocess.TimeoutExpired:
                pass
            secs = time.monotonic() - t1
            if exited:
                time.sleep(max(0.0, SETTLE - secs))
        if time.monotonic() - t0 > ROW_BOUND:
            raise FixtureError(f"row exceeded its {ROW_BOUND:.0f}s bound")
        surv = nonce_pids(nonce)
    finally:
        reap(nonce)
        if p.poll() is None:
            p.kill()
        p.wait()
    with open(outp, "rb") as f:
        out = f.read().decode("utf-8", "replace")
    with open(errp, "rb") as f:
        err = f.read().decode("utf-8", "replace")
    left = []
    for dp, dns, fns in os.walk(tmpdir):
        left += dns + fns
    rc = p.returncode if exited else None
    lines = out.splitlines()
    sigline = f"SIGNAL\tSIG{sig}\t{CLASS}" in lines
    anysig = any(l.startswith("SIGNAL\t") for l in lines)
    verdict = "-"
    for l in lines:
        f = l.split("\t")
        if len(f) >= 3 and f[0] == "RESULT" and f[1] == target:
            verdict = f[2]
    if SIGS[sig] is None:
        want_v, want_rc = expect.split("/")
        ok = exited and rc == int(want_rc) and verdict == want_v and not anysig and not surv and not left
    else:
        ok = exited and rc == 128 + int(SIGS[sig]) and sigline and not surv and not left
    return ok, exited, rc, sigline, verdict, len(surv), len(left), secs, ign, where, out + err


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool-dir", required=True, help="directory holding souji-quarantine.sh and souji-verify.sh")
    ap.add_argument("--work", required=True, help="empty scratch directory (never under /tmp)")
    ns = ap.parse_args(argv)
    tool_dir = os.path.abspath(ns.tool_dir)
    tool = os.path.join(tool_dir, "souji-quarantine.sh")
    engine = os.path.join(tool_dir, "souji-verify.sh")
    work = os.path.abspath(ns.work)
    if not (os.path.isfile(tool) and os.path.isfile(engine)):
        print(f"C2-COUNTER-FATAL: tool dir incomplete: {tool_dir}", file=sys.stderr)
        return 2
    pop = os.path.join(HERE, "c2-population.tsv")
    with open(pop, encoding="utf-8") as f:
        rows = [l.rstrip("\n").split("\t") for l in f if l.strip() and not l.startswith("#")]
    if [tuple(r) for r in rows] != ROUTES:
        print("C2-COUNTER-FATAL: c2-population.tsv and the ROUTES table disagree", file=sys.stderr)
        return 2
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("C2-COUNTER-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"C2-COUNTER-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    print(launch_line())
    try:
        stubs = make_shims(os.path.join(work, "shim"))
    except (FixtureError, OSError) as exc:
        print(f"C2-COUNTER-FATAL: shims: {exc}", file=sys.stderr)
        return 2
    print(f"# tool path={tool} sha256={sha(tool)}")
    print(f"# engine path={engine} sha256={sha(engine)}")
    print(f"# population path={pop} sha256={sha(pop)}")
    print(f"# counter sha256={sha(os.path.abspath(__file__))} settle={SETTLE}s mark_timeout={MARK_TIMEOUT}s "
          f"row_bound={ROW_BOUND}s reset=INT,QUIT,TERM,HUP")
    mism = errs = orphans = 0
    for rid, sig, point, kind, ekind, ev in ROUTES:
        rowdir = os.path.join(work, rid)
        try:
            ok, exited, rc, sigline, verdict, ns_, nl, secs, ign, where, text = run_row(
                tool, engine, stubs, rowdir, rid, sig, point, kind, ekind, ev, os.path.join(work, "shim"))
        except (FixtureError, OSError, subprocess.SubprocessError) as exc:
            errs += 1
            print(f"ROW {rid} sig={sig} point={point} engine={ekind} expect={ev} exited=- rc=- signal_line=- verdict=- "
                  f"survivors=- tmpleft=- secs=- ign=- at=- match=error detail={type(exc).__name__}: "
                  f"{str(exc)[:200]}")
            continue
        orphans += ns_ > 0
        mism += 0 if ok else 1
        print(f"ROW {rid} sig={sig} point={point} engine={ekind} expect={ev} exited={'y' if exited else 'n'} rc={rc} "
              f"signal_line={'y' if sigline else 'n'} verdict={verdict} survivors={ns_} tmpleft={nl} "
              f"secs={secs:.1f} ign={ign} at={where} match={'yes' if ok else 'no'}")
        if not ok:
            brief = " | ".join(l for l in text.splitlines() if l.startswith(("RESULT", "SIGNAL", "souji-")))
            print(f"#  {rid} {brief[:300]}")
    print(f"SUMMARY rows={len(ROUTES)} mismatches={mism} errors={errs} orphans={orphans}")
    return 0 if mism == 0 and errs == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
