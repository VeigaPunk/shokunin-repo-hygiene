#!/usr/bin/env python3
"""souji r98 C2 forgery probe: the r95 probe (census/round-95/c2-forgery-probe.py; same eight forgeries, same verdict,
same setup refusals) with the setup failures the r95 wave found still hanging the probe moved to exit 2 (r95 closure
A6; plans/round-95.md A6).

r98: identical to r97 (same eight forgeries, same verdict, same setup refusals, same --max-output cap
and --timeout behaviour; only the counter's ownership rule changed).

r96 additions, each exit 2 with one `C2-FORGERY-FATAL:` line on stderr: a fixture run that outlives --timeout
seconds (default 120): its process group is killed, the probe stops waiting on the pipes rather than blocking for
EOF, so a descendant that left the process group with the pipes held no longer hangs the probe past its own timeout;
and any other exception escaping main(). Exit 1 still means only "a forgery was not rejected or the positive control
failed".

r94 docstring follows (its "every setup failure exits 2" sentence was false for the cases above; A4).

r94 setup discipline: exit 1 means only "a forgery was not rejected or the positive control failed". Every setup
failure exits 2 with one `C2-FORGERY-FATAL:` line on stderr: --fixture/--tool/--before not a readable regular file;
--work under /tmp, an existing non-directory, or a non-empty directory (an EXISTING EMPTY directory is used as is —
r93 aborted on it with a FileExistsError traceback, exit 1); a fixture run that prints no `SUMMARY cases=...` line
(the fixture itself failed, for the positive control or for any forgery — r93 scored such a forgery `rejected=no`
and exited 1). Verdicts and output lines are otherwise the r93 ones.

r93 docstring follows. Does a fixture refuse tools that fake the r92 cut repair?

Each forgery is ONE text edit (applied exactly once) to a pinned tool's bytes, run through the fixture named by
--fixture as `--tool`, with the r91 tool as `--before`. A forgery is REJECTED iff the fixture exits 1 with
tool_pass < cases. The positive control is the filed tool, which must exit 0 at cases/cases; the negative control
is the unmodified r91 tool, which must be rejected too. Run against tests/fixtures/r92-k4-flagfail.py it is the r93
C2 do-nothing control (F5-F7 pass that fixture 20/20, R92MutC2); against tests/fixtures/r93-k4-flagfail.py it is
the C2 after arm.

  F1 ab-special   r91 tool + a special case that keeps the tail cut when an F0 lead is followed by 0x80 (fixes the
                  R91 repro pair, nothing else)
  F2 cont-only    r91 tool + the r91 A2 routed repair WITHOUT range checks: move the tail cut only when every
                  declared byte is a continuation and the sequence ends inside the payload
  F3 no-tail      filed tool with `_cut_tail` returning the cut unchanged
  F4 no-head      filed tool with `_cut_head` returning the cut unchanged
  N0 r91          the r91 tool bytes unchanged (do-nothing control)
  F5 surrpass     filed tool deciding a straddling sequence with the `surrogatepass` decoder (R92MutC2 C): an
                  ED A0..BF surrogate encoding, ill-formed per Table 3-7, is moved across as one sequence
  F6 multichar    filed tool accepting `len(...) >= 1` (R92MutC2 D): a span of several characters moves the cut
  F7 head-fwd     filed tool moving the head cut FORWARD to the straddling sequence's end (R92MutC2 E)

Output: `FORGERY <id> exit=<rc> tool_pass=<n>/<cases> rejected=<yes|no>` and
`FORGERY-SUMMARY forgeries=8 rejected=<k> positive=<pass|fail>`. Exit 0 iff all eight are rejected and the positive
control passes; 1 otherwise; 2 on setup error. Scratch only under --work (never /tmp).
"""
import argparse
import hashlib
import os
import re
import signal
import subprocess
import sys

sys.dont_write_bytecode = True


class Fatal(Exception):
    """A setup failure: printed as one `C2-FORGERY-FATAL:` line, exit 2."""

R91_TAIL_OLD = """        if need and end > t:
            return min(end, len(raw))
    return t
"""
FORGERIES = (
    ("F1", "before", "    if t <= 0 or t >= len(raw) or not 0x80 <= raw[t] <= 0xBF:\n        return t\n",
     "    if t <= 0 or t >= len(raw) or not 0x80 <= raw[t] <= 0xBF:\n        return t\n"
     "    if raw[t - 1] == 0xF0 and raw[t] == 0x80:  # F1 forgery: the repro pair only\n        return t\n"),
    ("F2", "before", R91_TAIL_OLD,
     "        if need and end > t and end <= len(raw) and all(0x80 <= b <= 0xBF for b in raw[i:end]):  # F2\n"
     "            return end\n    return t\n"),
    ("F3", "tool", "    seq = _straddling_sequence(raw, t)\n    return seq[1] if seq else t\n",
     "    return t  # F3 forgery\n"),
    ("F4", "tool", "    seq = _straddling_sequence(raw, h)\n    return seq[0] if seq else h\n",
     "    return h  # F4 forgery\n"),
    ("N0", "before", None, None),
    ("F5", "tool", '                if len(raw[start:end].decode("utf-8", "strict")) == 1:\n',
     '                if len(raw[start:end].decode("utf-8", "surrogatepass")) == 1:  # F5 forgery\n'),
    ("F6", "tool", '                if len(raw[start:end].decode("utf-8", "strict")) == 1:\n',
     '                if len(raw[start:end].decode("utf-8", "strict")) >= 1:  # F6 forgery\n'),
    ("F7", "tool", "    seq = _straddling_sequence(raw, h)\n    return seq[0] if seq else h\n",
     "    seq = _straddling_sequence(raw, h)\n    return seq[1] if seq else h  # F7 forgery\n"),
)


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _wait_output(p, timeout, max_output, label="the fixture run"):
    """Wait for the fixture's own stdout/stderr pipes, but stop waiting on pipe EOF once the process group is killed.

    A descendant that leaves the fixture's process group but keeps the pipes open would otherwise block
    communicate() forever even after killpg.  On timeout: kill the group, then wait only for the integer
    returncode (never for pipe EOF).

    r97 (A5): the pipes are drained with selectors; a fixture whose captured output exceeds max_output bytes is
    a setup failure (Fatal) — the probe refuses it within the run instead of exhausting its own memory (the
    r96 probe was driven to 27.3 GB RSS by an unbounded-rate fixture, plans/round-96.md A5)."""
    import selectors, time
    bufs = {id(p.stdout): [p.stdout, bytearray()], id(p.stderr): [p.stderr, bytearray()]}
    sel = selectors.DefaultSelector()
    for f, pair in bufs.values():
        os.set_blocking(f.fileno(), False)
        sel.register(f, selectors.EVENT_READ)
    deadline = time.monotonic() + timeout
    total = 0
    timed_out = False
    while sel.get_map():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            timed_out = True
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            break
        for key, _mask in sel.select(timeout=min(remaining, 0.25)):
            try:
                chunk = os.read(key.fileobj.fileno(), 65536)
            except BlockingIOError:
                continue
            if not chunk:
                sel.unregister(key.fileobj)
                continue
            bufs[id(key.fileobj)][1].extend(chunk)
            total += len(chunk)
            if total > max_output:
                sel.close()
                try:
                    os.killpg(p.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                raise Fatal(f"{label} exceeded --max-output {max_output} bytes; its process group was killed")
    sel.close()
    p.wait()
    if timed_out:
        return b"", p.returncode, True
    out = bytes(bufs[id(p.stdout)][1])
    return out, p.returncode, False


def run(fixture, tool, before, work, timeout, label, max_output=8388608):
    p = subprocess.Popen([sys.executable, "-B", fixture, "--tool", tool, "--before", before, "--work", work],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    so, rc, killed = _wait_output(p, timeout, max_output, label)
    if killed:
        raise Fatal(f"the fixture run for {label} exceeded --timeout {timeout}s; its process group was killed")
    out = so.decode("utf-8", "replace")
    m = re.search(r"^SUMMARY cases=(\d+) tool_pass=(\d+) before_pass=(\d+)$", out, re.M)
    return rc, (int(m.group(2)), int(m.group(1))) if m else None, out


def read_utf8(k, path):
    with open(path, "rb") as f:
        data = f.read()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Fatal(f"--{k} {path} is not UTF-8 ({exc.reason} at byte {exc.start})")


def write(path, text):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    except OSError as exc:
        raise Fatal(f"cannot write {path}: {exc.strerror or exc}")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--tool", required=True, help="the filed tool (positive control)")
    ap.add_argument("--before", required=True, help="the r91 tool bytes")
    ap.add_argument("--work", required=True)
    ap.add_argument("--timeout", type=int, default=120, help="seconds per fixture run before the probe gives up")
    ap.add_argument("--max-output", type=int, default=8388608, help="bytes of fixture output before the probe refuses")
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        raise Fatal("--work under /tmp, /var/tmp or /dev/shm")
    if os.path.lexists(work) and not os.path.isdir(work):
        raise Fatal(f"--work {work} exists and is not a directory")
    if os.path.isdir(work) and os.listdir(work):
        raise Fatal(f"--work {work} is not empty")
    if ns.timeout <= 0:
        raise Fatal("--timeout must be a positive number of seconds")
    fixture, tool, before = (os.path.abspath(x) for x in (ns.fixture, ns.tool, ns.before))
    for k, v in (("fixture", fixture), ("tool", tool), ("before", before)):
        if not os.path.isfile(v) or not os.access(v, os.R_OK):
            raise Fatal(f"--{k} {v} is not a readable regular file")
    src = {"tool": read_utf8("tool", tool), "before": read_utf8("before", before)}
    try:
        os.makedirs(work, exist_ok=True)
    except OSError as exc:
        raise Fatal(f"--work {work} cannot be created: {exc.strerror or exc}")
    for k, v in (("fixture", fixture), ("tool", tool), ("before", before), ("probe", os.path.abspath(__file__))):
        print(f"# {k} path={v} sha256={sha(v)}")
    rc, res, _out = run(fixture, tool, before, os.path.join(work, "positive"), ns.timeout, "the positive control", ns.max_output)
    if res is None:
        raise Fatal(f"the fixture printed no SUMMARY line for the positive control (exit {rc})")
    positive = rc == 0 and res is not None and res[0] == res[1]
    print(f"POSITIVE tool exit={rc} tool_pass={res[0] if res else '-'}/{res[1] if res else '-'} "
          f"{'pass' if positive else 'fail'}")
    rejected = 0
    for fid, base, old, new in FORGERIES:
        text = src[base]
        if old is not None:
            if text.count(old) != 1:
                raise Fatal(f"{fid} edit does not apply exactly once")
            text = text.replace(old, new, 1)
        path = os.path.join(work, f"{fid}-souji-record-agreement.py")
        write(path, text)
        rc, res, out = run(fixture, path, before, os.path.join(work, fid), ns.timeout, f"forgery {fid}", ns.max_output)
        write(os.path.join(work, f"{fid}.out"), out)
        if res is None:
            raise Fatal(f"the fixture printed no SUMMARY line for forgery {fid} (exit {rc}); its verdict is unknown")
        fails = [l.split()[1] for l in out.splitlines() if l.startswith("CASE ") and " tool=fail " in l]
        rej = rc == 1 and res is not None and res[0] < res[1]
        rejected += rej
        print(f"FORGERY {fid} sha256={sha(path)} exit={rc} tool_pass={res[0] if res else '-'}/{res[1] if res else '-'} "
              f"rejected={'yes' if rej else 'no'} failed={','.join(fails) or '-'}")
    print(f"FORGERY-SUMMARY forgeries={len(FORGERIES)} rejected={rejected} positive={'pass' if positive else 'fail'}")
    return 0 if positive and rejected == len(FORGERIES) else 1


def cli(argv):
    try:
        return main(argv)
    except Fatal as exc:
        print(f"C2-FORGERY-FATAL: {exc}", file=sys.stderr)
    except OSError as exc:
        print(f"C2-FORGERY-FATAL: I/O error: {exc}", file=sys.stderr)
    except Exception as exc:  # an internal error is not a verdict: never exit 1 for it
        print(f"C2-FORGERY-FATAL: internal error {type(exc).__name__}: {exc}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(cli(sys.argv[1:]))
