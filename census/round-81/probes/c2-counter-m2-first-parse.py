#!/usr/bin/env python3
"""DIAGNOSIS COPY (lesson M2): the first pre-freeze parse of the souji r81 C2 counter, which read cli= from the
VERIFIED line. Not an instrument.
souji r81 C2 counter: what tools/souji-vault-verify.sh does when its caller signals it while the advisory
Obsidian CLI call it bounds with `timeout` (cli_claim, the tool's only `timeout` child) is blocked.

Successor in method of census/round-80/c2-signal-counter.py (frozen and unchanged; that instrument measures
tools/souji-quarantine.sh). It carries the same instrument rules:
  * a column-0 `# launch` line with the counter's own inherited dispositions, group, session and tty;
  * every tool child starts with SIGINT, SIGQUIT, SIGTERM and SIGHUP reset to SIG_DFL and unblocked, and a row whose
    signal is ignored by the tool at delivery (SigIgn read from /proc) is an ERROR, never a verdict;
  * the hang point is asserted: the CLI stub writes a mark naming itself and its parent's comm, and the row is an
    ERROR unless the mark says `prog=cli parent=timeout` (the stub was started by the tool's `timeout`);
  * every row has a wall-clock bound (ROW_BOUND); cleanup kills every process carrying the row nonce, whatever its
    process group or session.

Fixture per row (under --work only): one source file and its byte-equal vault copy, a one-row ledger naming both
digests (the four conjuncts hold, so the tool reaches its advisory CLI call), an empty fleet root, a private
TMPDIR, and SOUJI_CLI_BIN = one of these stubs:
  hang    marks, then `exec sleep 600`
  fork    marks, starts `sleep 600 &` (a grandchild of timeout), then `exec sleep 600`
  honest  prints {"sha256":"<sha256 of its last argument>"}
  stdin   reads one line from its stdin and prints the honest answer only when that line is `r81-stdin`
          (the tool is started with stdin = a file holding that line; base `$(timeout ...)` inherits it)
Rows (frozen in census/round-81/c2-population.tsv, which must equal ROUTES):
  delivery pid    the signal goes to the tool's pid only
  delivery group  the signal goes to the tool's process group (the counter starts the tool as a group leader);
                  `timeout` moved itself and the CLI into a group of their own (S326), so a group kill of the
                  caller's group does not reach them
A signal row matches iff the tool exits within SETTLE seconds of the signal with status 128 + the signal number,
writes a stderr line starting `souji-vault-verify: SIG<name>`, no process carrying the row nonce is alive SETTLE
seconds after the signal, and the row's private TMPDIR is empty.
A no-signal row (p*) matches iff the tool exits 0 within MARK_TIMEOUT, its stdout carries exactly one `VERDICT`
record, whose evidence field holds the token `cli=<expected state>`, and exactly one line
`VERIFIED(moved-to-obsidian)`, no `souji-vault-verify: SIG` line, nothing carrying the nonce is
left running and TMPDIR is empty (positive controls: a tool that stops calling the CLI, or calls it without the
caller's stdin, fails them).
Output: one `ROW ...` line per row, then `SUMMARY rows=<N> mismatches=<M> errors=<E> orphans=<O>`.
Exit 0 iff M == 0 and E == 0; 1 otherwise; 2 usage/fatal.

Stated limits: SIGKILL to the tool is not a row (cannot be trapped); a CLI descendant that leaves timeout's process
group itself (setsid, setpgid) is not a row; a SIGINT ignored by the caller before starting the tool (an `&`
launch without job control) cannot be trapped by bash (S325) and is not a row; signals while the tool runs
another (unbounded, short) child such as sha256sum or git are not rows.
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
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # diagnosis copy: the frozen population one level up
SETTLE = 5.0
MARK_TIMEOUT = 60.0
ROW_BOUND = 90.0
SIGS = {"TERM": signal.SIGTERM, "INT": signal.SIGINT, "HUP": signal.SIGHUP, "-": None}
RESET = (signal.SIGINT, signal.SIGQUIT, signal.SIGTERM, signal.SIGHUP)

# id, signal, delivery, cli stub, SOUJI_CLI_TIMEOUT, expected
ROUTES = [
    ("v1-term-pid", "TERM", "pid", "hang", "300", "SIGNALED"),
    ("v2-int-pid", "INT", "pid", "hang", "300", "SIGNALED"),
    ("v3-hup-pid", "HUP", "pid", "hang", "300", "SIGNALED"),
    ("v4-term-group", "TERM", "group", "hang", "300", "SIGNALED"),
    ("v5-int-group", "INT", "group", "hang", "300", "SIGNALED"),
    ("v6-hup-group", "HUP", "group", "hang", "300", "SIGNALED"),
    ("v7-term-pid-fork", "TERM", "pid", "fork", "300", "SIGNALED"),
    ("v8-hup-group-fork", "HUP", "group", "fork", "300", "SIGNALED"),
    ("p1-honest", "-", "-", "honest", "6", "cli=agree"),
    ("p2-hang-bounded", "-", "-", "hang", "2", "cli=timeout"),
    ("p3-stdin", "-", "-", "stdin", "6", "cli=agree"),
    ("p4-fallback", "-", "-", "honest", "6", "cli=skipped(fallback)"),
]

MARK_FN = r'''r81_mark() {
  local pc; pc=$(cat /proc/$PPID/comm 2>/dev/null)
  { printf 'prog=cli\n'; printf 'parent=%s\n' "$pc"; printf 'argv=%s\n' "$*"; } > "$SOUJI_R81_MARK.tmp"
  mv -f "$SOUJI_R81_MARK.tmp" "$SOUJI_R81_MARK"
}
'''
STUBS = {
    "hang": "#!/bin/bash\n" + MARK_FN + 'r81_mark "$@"\nexec sleep 600\n',
    "fork": "#!/bin/bash\n" + MARK_FN + 'sleep 600 &\nr81_mark "$@"\nexec sleep 600\n',
    "honest": "#!/bin/bash\nlast=; for last in \"$@\"; do :; done\n"
              "h=$(sha256sum -- \"$last\" | cut -d' ' -f1)\nprintf '{\"ok\":true,\"sha256\":\"%s\"}\\n' \"$h\"\n",
    "stdin": "#!/bin/bash\nlast=; for last in \"$@\"; do :; done\nIFS= read -r l || l=\n"
             "[ \"$l\" = r81-stdin ] || exit 0\n"
             "h=$(sha256sum -- \"$last\" | cut -d' ' -f1)\nprintf '{\"ok\":true,\"sha256\":\"%s\"}\\n' \"$h\"\n",
}


class FixtureError(Exception):
    pass


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


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


def make_stubs(d):
    os.makedirs(d)
    out = {}
    for name, body in STUBS.items():
        p = os.path.join(d, f"cli-{name}")
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
        os.chmod(p, 0o755)
        out[name] = p
    return out


def build(rowdir):
    src, vault, fleet = (os.path.join(rowdir, x) for x in ("src", "vault", "fleet"))
    for d in (src, vault, fleet):
        os.makedirs(d)
    s = os.path.join(src, "a-src.md")
    v = os.path.join(vault, "a-vlt.md")
    for p in (s, v):
        with open(p, "w", encoding="utf-8") as f:
            f.write("r81 C2 vault pair payload\n")
    h = sha(s)
    ledger = os.path.join(rowdir, "ledger.tsv")
    with open(ledger, "w", encoding="utf-8") as f:
        f.write("source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n")
        f.write(f"{s}\t{h}\t{v}\t{h}\t2026-11-07\tr81-c2\n")
    stdin = os.path.join(rowdir, "stdin.txt")
    with open(stdin, "w", encoding="utf-8") as f:
        f.write("r81-stdin\n")
    return s, fleet, ledger, stdin


def nonce_pids(nonce):
    key = f"SOUJI_R81_NONCE={nonce}".encode()
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


def run_row(tool, stubs, rowdir, rid, sig, delivery, stub, ctimeout, expect):
    target, fleet, ledger, stdin = build(rowdir)
    tmpdir = os.path.join(rowdir, "tmp")
    os.makedirs(tmpdir)
    nonce = secrets.token_hex(8)
    mark = os.path.join(rowdir, "cli.mark")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SOUJI_"))}
    env.update({"TMPDIR": tmpdir, "LC_ALL": "C", "SOUJI_R81_NONCE": nonce, "SOUJI_R81_MARK": mark,
                "SOUJI_CLI_BIN": stubs[stub], "SOUJI_CLI_TIMEOUT": ctimeout, "SOUJI_LEDGER": ledger,
                "SHOKUNIN_ROOT": fleet, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    argv = ["bash", tool] + (["--fallback"] if expect == "cli=skipped(fallback)" else []) + [target]
    outp, errp = os.path.join(rowdir, "tool.out"), os.path.join(rowdir, "tool.err")
    t0 = time.monotonic()
    with open(outp, "wb") as fo, open(errp, "wb") as fe, open(stdin, "rb") as fi:
        p = subprocess.Popen(argv, stdout=fo, stderr=fe, stdin=fi, env=env, start_new_session=True, cwd=rowdir,
                             preexec_fn=_preexec)
    exited, secs, ign, where = False, 0.0, "-", "-"
    try:
        if SIGS[sig] is None:
            try:
                p.wait(timeout=MARK_TIMEOUT)
                exited = True
            except subprocess.TimeoutExpired:
                pass
            secs = time.monotonic() - t0
        else:
            while not os.path.exists(mark) and p.poll() is None and time.monotonic() - t0 < MARK_TIMEOUT:
                time.sleep(0.05)
            if not os.path.exists(mark):
                raise FixtureError("hang point never reached (tool exited or mark timeout)")
            m = read_mark(mark)
            where = f"{m.get('prog')}<{m.get('parent')}"
            if m.get("prog") != "cli" or m.get("parent") != "timeout":
                raise FixtureError(f"blocked at {where}, not the labelled cli<timeout")
            time.sleep(0.3)
            ign = proc_status(p.pid, "SigIgn").get("SigIgn", "?")
            try:
                if int(ign, 16) & (1 << (int(SIGS[sig]) - 1)):
                    raise FixtureError(f"SIG{sig} ignored by the tool at delivery (SigIgn={ign})")
            except ValueError:
                raise FixtureError(f"tool SigIgn unreadable at delivery ({ign})")
            t1 = time.monotonic()
            if delivery == "group":
                os.killpg(p.pid, SIGS[sig])
            else:
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
    sigline = any(l.startswith(f"souji-vault-verify: SIG{sig}") for l in err.splitlines()) if SIGS[sig] else False
    anysig = any(l.startswith("souji-vault-verify: SIG") for l in err.splitlines())
    r4 = [l for l in out.splitlines() if l.startswith("VERIFIED(moved-to-obsidian)")]
    state = "-"
    for tok in (r4[0].split() if r4 else []):
        if tok.startswith("cli="):
            state = tok
    if SIGS[sig] is None:
        ok = exited and rc == 0 and len(r4) == 1 and state == expect and not anysig and not surv and not left
    else:
        ok = exited and rc == 128 + int(SIGS[sig]) and sigline and not surv and not left
    return ok, exited, rc, sigline, state, len(surv), len(left), secs, ign, where, out + err


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True, help="the souji-vault-verify.sh bytes under test")
    ap.add_argument("--work", required=True, help="empty scratch directory (never under /tmp)")
    ns = ap.parse_args(argv)
    tool = os.path.abspath(ns.tool)
    work = os.path.abspath(ns.work)
    if not os.path.isfile(tool):
        print(f"C2-COUNTER-FATAL: no tool at {tool}", file=sys.stderr)
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
    stubs = make_stubs(os.path.join(work, "stubs"))
    print(f"# tool path={tool} sha256={sha(tool)} mode={oct(os.stat(tool).st_mode & 0o777)}")
    print(f"# population path={pop} sha256={sha(pop)}")
    print(f"# counter sha256={sha(os.path.abspath(__file__))} settle={SETTLE}s mark_timeout={MARK_TIMEOUT}s "
          f"row_bound={ROW_BOUND}s reset=INT,QUIT,TERM,HUP")
    mism = errs = orphans = 0
    for rid, sig, delivery, stub, ct, ev in ROUTES:
        rowdir = os.path.join(work, rid)
        try:
            ok, exited, rc, sigline, state, ns_, nl, secs, ign, where, text = run_row(
                tool, stubs, rowdir, rid, sig, delivery, stub, ct, ev)
        except (FixtureError, OSError, subprocess.SubprocessError) as exc:
            errs += 1
            print(f"ROW {rid} sig={sig} delivery={delivery} cli={stub} expect={ev} exited=- rc=- sig_line=- state=- "
                  f"survivors=- tmpleft=- secs=- ign=- at=- match=error detail={type(exc).__name__}: "
                  f"{str(exc)[:200]}")
            continue
        orphans += ns_ > 0
        mism += 0 if ok else 1
        print(f"ROW {rid} sig={sig} delivery={delivery} cli={stub} expect={ev} exited={'y' if exited else 'n'} "
              f"rc={rc} sig_line={'y' if sigline else 'n'} state={state} survivors={ns_} tmpleft={nl} "
              f"secs={secs:.1f} ign={ign} at={where} match={'yes' if ok else 'no'}")
        if not ok:
            brief = " | ".join(l for l in text.splitlines() if l.startswith(("VERIFIED", "NOT-VERIFIED", "souji-")))
            print(f"#  {rid} {brief[:300]}")
    print(f"SUMMARY rows={len(ROUTES)} mismatches={mism} errors={errs} orphans={orphans}")
    return 0 if mism == 0 and errs == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
