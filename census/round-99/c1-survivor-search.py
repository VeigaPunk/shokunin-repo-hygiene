"""souji r98 C1 survivor search: the r96 search (census/round-97/c1-survivor-search.py) with a RERAISE-aware
eligibility latch on the SystemExit leg (plans/round-96.md A1 trade) and the two r96 crash-path limits repaired
(plans/round-96.md A2/A3; r96 spot-check §7 routed item 1).

1. Wider crash sentinel (r94 closure routed defects 1 and 2; R94ScoutSources FW1, R94Sentinel F1/F2). The r94
   `sitecustomize.py` only replaced `sys.excepthook`, which never sees SystemExit (S359), an exception raised in an
   atexit callback or a finalizer (routed to `sys.unraisablehook`), an exception in a thread (`threading.excepthook`,
   S361) or `os._exit` (S362). The sentinel ends the process with exit 70 (S358) on each of these channels:
     - an uncaught exception other than SystemExit                       (`sys.excepthook`, as r94)
     - an exception reported to `sys.unraisablehook` (atexit callbacks, `__del__`)
     - an exception escaping a thread's run(), SystemExit included          (`threading.excepthook`)
     - any call of `os._exit` from Python code                             (`os._exit` replaced)
     - a SystemExit that reaches the main module's top level after being first raised inside a function DEFINED IN
       THE MAIN SCRIPT and is still terminating (seen with a `sys.monitoring` RAISE callback, S360, cleared by an
       `EXCEPTION_HANDLED` callback, S365, when the same exception is handled at the top level (a `finally`
       does not stop the exception terminating, so its `EXCEPTION_HANDLED` does not clear); checked by an
       atexit callback registered first, so it runs after every callback the program registers). The counter's declared exit path is
       the top-level `sys.exit(main(...))`; a SystemExit first raised in another module (argparse's usage error), at
       the top level itself, or one that is caught, is declared and keeps its status.
2. Kill rule: a mutant is ERRORED when the harness exits 70 or below 0, or any `ROW` line reads `rc=70` or a
   negative `rc` (the counter was killed by a signal, S363); otherwise KILLED only on a harness exit 1 with at least
   one `ROW ... match=no` line; a harness exit 0 is a survivor; anything else is errored.
3. r98 (four legs, one instrument file, one commit):
   (a) Exception-object-keyed latch (successor to the r97 A1 trade, S372: sys.monitoring.events.RERAISE, "An
       exception is re-raised, for example at the end of a finally block."). The r97 hook kept a GLOBAL
       pending/foreign flag: _souji_handled recorded one pending key and _souji_atexit flushed whatever
       pending candidate remained, clearing a live foreign mark it did not belong to. Round-97 spot-check A9
       falsified it twice (q1q: object 1 caught, object 2 terminating -> flushed as declared, hooked 1 want 70,
       an r96 regression; q1o: bare raise-saved fires RAISE but not RERAISE -> pending never cancelled,
       hooked 1 want 70). The r98 hook stamps the exception object ITSELF (attribute _souji98_last; a
       WeakKeyDictionary was measured unavailable: SystemExit is not weak-referenceable on CPython 3.14.8)
       with RAISE/EH/RR at every sys.monitoring callback, and declares at atexit iff the LIVE foreign
       object own last stamp is EH. Per-object event orders at <module> on CPython 3.14.8 (scratch trace):
       t1 RAISE,EH->EH; t4 RAISE,EH,RAISE,EH->EH; q1i RAISE,EH,RR,EH,RR,EH->EH (finally-unwind caught by outer
       except); x1/x2 RAISE,EH,RR,EH,RR->RR; q1o RAISE,EH,RAISE->RAISE; q1q obj1 RAISE,EH / obj2 RAISE->RAISE.
       Predicted: t1/t4/q1i declared, x1/x2/q1o/q1q errored (70), v3/w1/w2/a3b errored - a 17-shape table
       (r97 14 + q1i/q1o/q1q), mismatched=0.
   (b) Crash-path order (A2 carried): _souji_crash writes the marker on the raw fd first (non-blocking,
       best-effort) so a full undrained pipe cannot hold the exit hostage; the CHECK still asserts the reason.
   (c) Traceback print (A11 routed): r97 removed sys.__excepthook__/threading.__excepthook__ from the
       excepthook/thread channels so those channels print no Traceback. The r98 _souji_crash prints the
       traceback (best-effort) AFTER the marker write inside _souji_crash before os._exit.
   (d) No-free-tool-id fallback (A3, r97 path): restores fd 2 blocking mode (os.set_blocking(2, True))
       instead of leaving it permanently non-blocking for children.
   (e) Do-nothing control: the frozen r95 hook on the same 17 scripts and the r97 hook score mismatched>0
       (r97 hook: q1o/q1q declared wrongly; q1i measured hooked 70 vs plain 0).
   (The search search own --counter/--ids reads refuse non-UTF-8 inputs with exit 2.)
4. The five r95 hand edits, unchanged (see HAND).
   Hand edits: the r95 five (`h-sysexit`, `h-atexit`, `h-thread`, `h-osexit`, `h-sigkill` — one per channel the
   r94 sentinel misses, see HAND). A terminating helper-raised SystemExit stays `errored` (h-sysexit); the
   caught-at-`__main__` shape is covered by the declared-shape table (Q172), which the r95-rule control fails at
   mismatched=4 (r97: 14 shapes) while the r96 hook drops to mismatched=2 (x1/x2 wrongly declared; A1 below), the r97 hook reaches mismatched=0 on its 14 shapes but regresses q1q and escapes q1o (A9 above), and the r98 hook reaches mismatched=0 on all 17 shapes. No counter HAND edit can express `<module>`-level catching on the frozen
   counter's one-line-replace generator. The "r94-rule mismatched=6" label of r96 was the r95 receipt (A9).

Inherited from r94 and r93: SIGINT/SIGTERM stop the search, kill every live harness process group and delete every
per-mutant work tree before exit (exit 130); the bare-/tmp guard covers --work and --emit; the precondition now runs a
check script per channel plus two declared exits (status 1 and argparse's 2) before scoring.

Generates single-token operator mutants of the frozen r87 counter (census/round-87/c1-pointer-counter.py) with
`tokenize` (comparison flips, boolean-operator swaps, `not` deletion, True/False swaps, integer 0/1 swaps), plus
named hand edits, applies each EXACTLY ONCE to a scratch copy, and scores it with a pinned harness on a pinned
population. A mutant whose source line occurs more than once is skipped (`ambiguous`); one that does not compile is
skipped (`uncompiled`); one whose harness run exceeds --timeout seconds is stopped (its whole process group is
killed) and counted `hung`. Each per-mutant harness work tree (a lane clone) is deleted once scored; harness.out
stays.

Output: one `SEARCH <id> line=<n> killed=<yes|no|errored> rc=<n>` line per scored mutant, printed as it is scored,
and `SEARCH-SUMMARY generated=<G> ambiguous=<A> uncompiled=<U> hung=<H> scored=<S> errored=<E> killed=<K>
survived=<V>` (S = E + K + V); `--emit` writes the survivors' {id, clause, old, new} records as JSON. `--ids`
restricts the run to named generated ids. Scratch only under --work (never /tmp); exit 0 when the search ran, 2 on
setup error, 130 when interrupted.
"""
import argparse
import concurrent.futures as cf
import hashlib
import io
import json
import os
import re
import signal
import shutil
import subprocess
import sys
import tokenize

sys.dont_write_bytecode = True

SWAP = {"==": "!=", "!=": "==", "<": "<=", "<=": "<", ">": ">=", ">=": ">",
        "and": "or", "or": "and", "True": "False", "False": "True"}
HAND = (
    ("h-exit-always-1", "    return 0 if ok else 1\n", "    return 1  # h-exit-always-1\n"),
    ("h-exit-always-0", "    return 0 if ok else 1\n", "    return 0  # h-exit-always-0\n"),
    ("h-ok-admits-one", '    ok = counts["resolved"] == len(pop) and not unknown\n',
     '    ok = counts["resolved"] >= len(pop) - 1 and not unknown  # h-ok-admits-one\n'),
    ("h-crash-late", "    return 0 if ok else 1\n", '    raise RuntimeError("h-crash-late")  # h-crash-late\n'),
    ("h-crash-index", "            ledger[r[0]] = (r[1], r[2])\n",
     "            ledger[r[0]] = (r[1], r[2], r[3])[:2]  # h-crash-index\n"),
    ("h-sysexit", "    ledger, bad_ledger = _ledger(ns.ledger) if ns.ledger else ({}, [])\n",
     '    raise SystemExit("h-sysexit")  # h-sysexit\n'),
    ("h-atexit", "    return 0 if ok else 1\n",
     '    __import__("atexit").register(lambda: 1 / 0)  # h-atexit\n    return 0 if ok else 1\n'),
    ("h-thread", "    return 0 if ok else 1\n",
     '    t = __import__("threading").Thread(target=lambda: 1 / 0); t.start(); t.join()  # h-thread\n'
     "    return 0 if ok else 1\n"),
    ("h-osexit", "    ledger, bad_ledger = _ledger(ns.ledger) if ns.ledger else ({}, [])\n",
     "    os._exit(1)  # h-osexit\n"),
    ("h-sigkill", "    ledger, bad_ledger = _ledger(ns.ledger) if ns.ledger else ({}, [])\n",
     "    os.kill(os.getpid(), 9)  # h-sigkill\n"),
)
CRASH_RC = 70  # sysexits(3) EX_SOFTWARE: "An internal software error has been detected."
HOOK = '''# souji r98 crash sentinel (census/round-98/c1-survivor-search.py): every crash channel below exits @RC@
import atexit, os, sys, threading, traceback

_SOUJI_EXIT = os._exit
_SOUJI_SEEN = {}
_SOUJI_STATE = {"foreign": None, "foreign_exc": None}
_SOUJI_LAST = {}


def _souji_stamp(exc, event):
    # r98 (C1 successor latch): state keyed to the exception object ITSELF via an attribute stamp
    # (SystemExit is not weak-referenceable on CPython 3.14.8, so WeakKeyDictionary is unavailable;
    # the stamp is decided at RAISE/EXCEPTION_HANDLED/RERAISE callbacks from sys.monitoring, S372).
    # Each event for THIS object overwrites its own slot; only this stamp decides declared.
    # for the declared decision. A mirror dict keyed by id() (holding a strong ref) lets the atexit
    # leg read the stamp of the live foreign object.
    try:
        st = getattr(exc, "_souji98_last", None)
        if st is None or not isinstance(st, list):
            st = []
            try:
                exc._souji98_last = st
            except Exception:
                pass
        st.append(event)
    except Exception:
        pass
    try:
        _SOUJI_LAST[id(exc)] = (exc, event)
    except Exception:
        pass


def _souji_last_event(exc):
    try:
        st = getattr(exc, "_souji98_last", None)
        if st:
            return st[-1]
    except Exception:
        pass
    try:
        ent = _SOUJI_LAST.get(id(exc))
        if ent is not None and ent[0] is exc:
            return ent[1]
    except Exception:
        pass
    return None


def _souji_crash(why, exc=None):
    # Signal-safe and non-blocking (r96): a raw os.write bypasses the TextIOWrapper lock a signal handler would
    # deadlock on, and a momentarily non-blocking fd 2 keeps a full undrained pipe from blocking the crash path.
    # The marker is best-effort; the exit code is the verdict. A11 (r98): after the marker write, print the
    # traceback (best-effort) before os._exit, restoring the diagnostic the r97 hook removed when it dropped
    # sys.__excepthook__ from the excepthook/thread channels. Marker stays first (A2) so a full undrained
    # pipe cannot hold the exit hostage; the traceback print is also best-effort.
    try:
        try:
            os.set_blocking(2, False)
        except Exception:
            pass
        try:
            os.write(2, ("SOUJI-R98-CRASH " + why + "\\n").encode("utf-8", "surrogateescape"))
        except Exception:
            pass
        try:
            if exc is not None:
                traceback.print_exception(exc)
            else:
                exc_info = sys.exc_info()
                if exc_info[0] is not None:
                    traceback.print_exception(exc_info[1], exc_info[2])
        except Exception:
            pass
    except Exception:
        pass
    _SOUJI_EXIT(@RC@)


def _souji_excepthook(t, v, tb):
    # r98 (A2+A11): marker write first inside _souji_crash, traceback print second (best-effort), then exit.
    _souji_crash("uncaught " + getattr(t, "__name__", "?"), v)


def _souji_unraisable(u):
    try:
        u.print_exception()
    except Exception:
        pass
    _souji_crash("unraisable " + getattr(u.exc_type, "__name__", "?"), getattr(u, "exc_value", None))


def _souji_thread(a):
    # r98 (A2+A11): same order as _souji_excepthook above.
    _souji_crash("thread " + getattr(a.exc_type, "__name__", "?"), getattr(a, "exc_value", None))


def _souji_os_exit(n):
    _souji_crash("os._exit(%r)" % (n,))


def _souji_raise(code, _offset, exc):
    # r98 (C1): latch the foreign mark at RAISE-<module> (the unfold point). The object's own stamp is
    # updated for THIS exception at every RAISE/EXCEPTION_HANDLED/RERAISE. The EH/RR legs only stamp; they
    # never clear a global flag. The declared decision at atexit reads THIS object's last stamp.
    if not isinstance(exc, SystemExit):
        return
    main = getattr(sys.modules.get("__main__"), "__file__", None)
    seen = _SOUJI_SEEN.get(id(exc))
    if seen is None or seen[0] is not exc:
        seen = _SOUJI_SEEN[id(exc)] = (exc, code.co_filename, code.co_name)
    if main is not None and code.co_filename == main and code.co_name == "<module>":
        _souji_stamp(exc, "RAISE")
        _SOUJI_STATE["foreign"] = seen[2] if (seen[1] == main and seen[2] != "<module>") else None
        _SOUJI_STATE["foreign_exc"] = exc if _SOUJI_STATE["foreign"] is not None else None


def _souji_handled(code, _offset, exc):
    # r98 (C1): stamp EH on THIS object only. q1i (finally-unwind caught by outer except): EH,RR,EH,RR,EH ->
    # last stamp EH -> declared. x1/x2 (EH,RR,EH,RR): last stamp RR -> crash.
    if not isinstance(exc, SystemExit):
        return
    if code.co_name != "<module>":
        return
    _souji_stamp(exc, "EH")


def _souji_reraise(code, _offset, exc):
    # r98 (C1): stamp RR on THIS object only. A bare `raise saved` outside the except fires RAISE but not RR
    # (q1o), so its stamp ends RAISE -> crash; the finally/explicit-reraise leg ends RR -> crash (S372: "An
    # exception is re-raised, for example at the end of a finally block.").
    if not isinstance(exc, SystemExit):
        return
    if code.co_name != "<module>":
        return
    _souji_stamp(exc, "RR")


def _souji_atexit():
    # r98 (C1): declare iff the LIVE foreign object's own last stamp is EH (a catch that never re-raised).
    # q1q: object 1 was caught (EH) but object 2 (the live foreign mark) ends RAISE -> crash (no stale clear).
    # q1o: the live object was EH-then-RAISE by bare raise -> last RAISE -> crash.
    foreign = _SOUJI_STATE.get("foreign")
    if foreign is not None:
        exc = _SOUJI_STATE.get("foreign_exc")
        if exc is not None and _souji_last_event(exc) == "EH":
            return
        _souji_crash("SystemExit first raised in " + foreign + "() of the main script", exc)



atexit.register(_souji_atexit)
sys.excepthook = _souji_excepthook
sys.unraisablehook = _souji_unraisable
threading.excepthook = _souji_thread
os._exit = _souji_os_exit
for _souji_id in range(3, 6):
    try:
        sys.monitoring.use_tool_id(_souji_id, "souji-r98-sentinel")
    except ValueError:
        continue
    sys.monitoring.register_callback(_souji_id, sys.monitoring.events.RAISE, _souji_raise)
    sys.monitoring.register_callback(_souji_id, sys.monitoring.events.EXCEPTION_HANDLED, _souji_handled)
    sys.monitoring.register_callback(_souji_id, sys.monitoring.events.RERAISE, _souji_reraise)
    sys.monitoring.set_events(_souji_id, sys.monitoring.events.RAISE | sys.monitoring.events.EXCEPTION_HANDLED
                              | sys.monitoring.events.RERAISE)
    break
else:
    try:
        os.set_blocking(2, True)  # r98 (A3, r97 path): restore blocking mode; the r96 fallback left fd 2 non-blocking
        os.write(2, b"SOUJI-R98-SENTINEL no free sys.monitoring tool id\\n")
    except Exception:
        pass
'''.replace("@RC@", str(CRASH_RC))
CHECK = '''import argparse, atexit, os, sys, threading


def main(mode):
    if mode == "excepthook":
        raise RuntimeError("souji-r98-sentinel-check")
    if mode == "sysexit":
        raise SystemExit("souji-r98-sentinel-check")
    if mode == "atexit":
        atexit.register(lambda: 1 / 0)
    if mode == "thread":
        t = threading.Thread(target=lambda: 1 / 0)
        t.start()
        t.join()
    if mode == "osexit":
        os._exit(1)
    if mode == "argparse":
        argparse.ArgumentParser().parse_args(["--souji-r98-unknown"])
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
'''
CHECKS = (("excepthook", CRASH_RC, "SOUJI-R98-CRASH uncaught"), ("sysexit", CRASH_RC, "SOUJI-R98-CRASH SystemExit"),
          ("atexit", CRASH_RC, "SOUJI-R98-CRASH unraisable"), ("thread", CRASH_RC, "SOUJI-R98-CRASH thread"),
          ("osexit", CRASH_RC, "SOUJI-R98-CRASH os._exit"), ("declared", 1, None), ("argparse", 2, None))
LIVE = set()


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def gen(src):
    lines = src.splitlines(keepends=True)
    out, seen = [], set()
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        rep = None
        if tok.type == tokenize.OP and tok.string in SWAP:
            rep = SWAP[tok.string]
        elif tok.type == tokenize.NAME and tok.string in SWAP:
            rep = SWAP[tok.string]
        elif tok.type == tokenize.NAME and tok.string == "not":
            rep = ""
        elif tok.type == tokenize.NUMBER and tok.string in ("0", "1"):
            rep = "1" if tok.string == "0" else "0"
        if rep is None or tok.start[0] != tok.end[0]:
            continue
        ln, c0, c1 = tok.start[0], tok.start[1], tok.end[1]
        old = lines[ln - 1]
        new = old[:c0] + rep + (old[c1:].lstrip(" ") if rep == "" else old[c1:])
        if old.lstrip().startswith("#") or (old, new) in seen:
            continue
        seen.add((old, new))
        out.append({"id": f"a{ln}c{c0}-{tok.string}-to-{rep or 'drop'}", "line": ln,
                    "clause": f"line {ln}: `{tok.string}` -> `{rep or '(deleted)'}`", "old": old, "new": new})
    for hid, old, new in HAND:
        ln = lines.index(old) + 1 if old in lines else 0
        out.append({"id": hid, "line": ln, "clause": f"hand edit: {hid}", "old": old, "new": new})
    return out


def verdict(rc, out):
    """The r95 kill rule (unchanged): a crash (harness exit 70 or below 0, or any ROW `rc=70` or negative `rc`)
    is errored; otherwise killed only on a harness exit 1 with at least one asserted row mismatch (`match=no`);
    exit 0 survives; anything else is errored."""
    rows = [l for l in out.decode("utf-8", "replace").splitlines() if l.startswith("ROW ")]
    rcs = [int(m.group(1)) for m in (re.search(r" rc=(-?\d+) match=", l) for l in rows) if m]
    if rc == CRASH_RC or rc < 0 or any(r == CRASH_RC or r < 0 for r in rcs):
        return "errored"
    if rc == 0:
        return "no"
    if rc == 1 and any(l.endswith(" match=no") for l in rows):
        return "yes"
    return "errored"


def score(m, src, counter_name, ns, idx):
    if src.count(m["old"]) != 1:
        return m, "ambiguous", None, None
    msrc = src.replace(m["old"], m["new"], 1)
    try:
        compile(msrc, counter_name, "exec")
    except SyntaxError:
        return m, "uncompiled", None, None
    d = os.path.join(ns.work, f"m{idx:04d}")
    os.makedirs(d)
    mc = os.path.join(d, counter_name)
    with open(mc, "w", encoding="utf-8") as f:
        f.write(msrc)
    env = dict(os.environ)
    env["PYTHONPATH"] = ns.hook + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    p = subprocess.Popen([sys.executable, "-B", ns.harness, "--counter", mc, "--lane", ns.lane,
                          "--fleet-root", ns.fleet_root, "--work", os.path.join(d, "w"),
                          "--population", ns.population], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         start_new_session=True, env=env)
    LIVE.add(p)
    try:
        try:
            out, err = p.communicate(timeout=ns.timeout)
            state = "scored"
        except subprocess.TimeoutExpired:
            # the harness and the counter it spawns share one session: kill the whole group (r92: a272c34 loops)
            os.killpg(p.pid, signal.SIGKILL)
            out, err = p.communicate()
            state = "hung"
        with open(os.path.join(d, "harness.out"), "wb") as f:
            f.write(out + b"\n--stderr--\n" + err
                    + (b"\n--hung: killed after --timeout--\n" if state == "hung" else b""))
    finally:
        LIVE.discard(p)
        # each harness work tree is a lane clone (~0.7 GB): drop it once scored, keep harness.out (fleet disk, r92)
        shutil.rmtree(os.path.join(d, "w"), ignore_errors=True)
    return m, state, (verdict(p.returncode, out) if state == "scored" else None), p.returncode


def _stop(signum, _frame):
    raise KeyboardInterrupt(f"signal {signum}")


def _reap(work):
    for p in list(LIVE):
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    for e in os.listdir(work):
        shutil.rmtree(os.path.join(work, e, "w"), ignore_errors=True)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True)
    ap.add_argument("--harness", required=True)
    ap.add_argument("--population", required=True)
    ap.add_argument("--lane", required=True)
    ap.add_argument("--fleet-root", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=300, help="seconds per harness run before the mutant is `hung`")
    ap.add_argument("--emit", default=None)
    ap.add_argument("--ids", default=None,
                    help="JSON list of mutant ids (or of objects with an `id`) to score; every id must be generated")
    ns = ap.parse_args(argv)
    ns.work = os.path.abspath(ns.work)
    for k in ("counter", "harness", "population", "lane", "fleet_root"):
        setattr(ns, k, os.path.abspath(getattr(ns, k)))
    for k in ("work", "emit"):
        v = getattr(ns, k)
        if v and os.path.realpath(os.path.abspath(v)).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
            print(f"C1-SEARCH-FATAL: --{k} under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
            return 2
    if os.path.exists(ns.work) and os.listdir(ns.work):
        print(f"C1-SEARCH-FATAL: --work {ns.work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(ns.work, exist_ok=True)
    ns.hook = os.path.join(ns.work, "hook")
    os.makedirs(ns.hook)
    with open(os.path.join(ns.hook, "sitecustomize.py"), "w", encoding="utf-8") as f:
        f.write(HOOK)
    # precondition: every sentinel channel must fire, and both declared exits keep their status, in a child started
    # the way the harness starts the counter (`python -B <script>`, the hook on PYTHONPATH)
    env = dict(os.environ, PYTHONPATH=ns.hook + (os.pathsep + os.environ["PYTHONPATH"]
                                                 if os.environ.get("PYTHONPATH") else ""))
    chk_dir = os.path.join(ns.work, "check")
    os.makedirs(chk_dir)
    chk_py = os.path.join(chk_dir, "souji_r98_check.py")
    with open(chk_py, "w", encoding="utf-8") as f:
        f.write(CHECK)
    got = []
    for mode, want_rc, want_reason in CHECKS:
        chk = subprocess.run([sys.executable, "-B", chk_py, mode], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env, timeout=60)
        got.append(f"{mode}={chk.returncode}")
        if chk.returncode != want_rc:
            print(f"C1-SEARCH-FATAL: crash sentinel check {mode}: child exit {chk.returncode}, want {want_rc}",
                  file=sys.stderr)
            return 2
        if want_reason is not None and want_reason not in chk.stderr.decode("utf-8", "replace"):
            print(f"C1-SEARCH-FATAL: crash sentinel check {mode}: missing reason {want_reason!r}", file=sys.stderr)
            return 2
    print(f"# crash-sentinel rc={CRASH_RC} check=pass {' '.join(got)}")
    try:
        with open(ns.counter, encoding="utf-8") as f:
            src = f.read()
    except (UnicodeDecodeError, OSError) as exc:
        print(f"C1-SEARCH-FATAL: --counter {ns.counter} unreadable ({exc})", file=sys.stderr)
        return 2
    for k in ("counter", "harness", "population"):
        print(f"# {k} path={getattr(ns, k)} sha256={sha(getattr(ns, k))}")
    print(f"# search sha256={sha(os.path.abspath(__file__))}")
    muts = gen(src)
    if ns.ids:
        try:
            with open(ns.ids, encoding="utf-8") as f:
                want = [x["id"] if isinstance(x, dict) else x for x in json.load(f)]
        except (UnicodeDecodeError, OSError, ValueError) as exc:
            print(f"C1-SEARCH-FATAL: --ids {ns.ids} unreadable ({exc})", file=sys.stderr)
            return 2
        known = {m["id"] for m in muts}
        if not want or any(w not in known for w in want) or len(set(want)) != len(want):
            print(f"C1-SEARCH-FATAL: --ids names an empty, duplicate or ungenerated id", file=sys.stderr)
            return 2
        muts = [m for m in muts if m["id"] in set(want)]
        print(f"# ids path={os.path.abspath(ns.ids)} sha256={sha(os.path.abspath(ns.ids))} n={len(muts)}")
    name = os.path.basename(ns.counter)
    res = []
    signal.signal(signal.SIGTERM, _stop)
    ex = cf.ThreadPoolExecutor(max_workers=ns.jobs)
    try:
        futs = [ex.submit(score, m, src, name, ns, i) for i, m in enumerate(muts)]
        for fu in futs:
            m, s, v, rc = fu.result()
            res.append((m, s, v))
            if s == "scored":
                print(f"SEARCH {m['id']} line={m['line']} killed={v} rc={rc}", flush=True)
            else:
                print(f"SKIP {m['id']} line={m['line']} state={s}", flush=True)
    except KeyboardInterrupt as exc:
        ex.shutdown(wait=False, cancel_futures=True)
        _reap(ns.work)
        ex.shutdown(wait=True)
        _reap(ns.work)
        print(f"C1-SEARCH-INTERRUPTED: {exc}; live harness groups killed, work trees deleted", file=sys.stderr)
        return 130
    ex.shutdown(wait=True)
    amb = sum(1 for _m, s, _v in res if s == "ambiguous")
    unc = sum(1 for _m, s, _v in res if s == "uncompiled")
    hung = sum(1 for _m, s, _v in res if s == "hung")
    scored = [(m, v) for m, s, v in res if s == "scored"]
    errd = sum(1 for _m, v in scored if v == "errored")
    kill = sum(1 for _m, v in scored if v == "yes")
    surv = [m for m, v in scored if v == "no"]
    print(f"SEARCH-SUMMARY generated={len(muts)} ambiguous={amb} uncompiled={unc} hung={hung} scored={len(scored)} "
          f"errored={errd} killed={kill} survived={len(surv)}")
    if ns.emit:
        with open(ns.emit, "w", encoding="utf-8") as f:
            json.dump([{k: m[k] for k in ("id", "clause", "old", "new")} for m in surv], f, indent=1)
            f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
