#!/usr/bin/env python3
"""souji r95 C1 survivor search: the r94 search (census/round-94/c1-survivor-search.py) with three changes.

1. Wider crash sentinel (r94 closure routed defects 1 and 2; R94ScoutSources FW1, R94Sentinel F1/F2). The r94
   `sitecustomize.py` only replaced `sys.excepthook`, which never sees SystemExit (S359), an exception raised in an
   atexit callback or a finalizer (routed to `sys.unraisablehook`), an exception in a thread (`threading.excepthook`,
   S361) or `os._exit` (S362). The r95 sentinel ends the process with exit 70 (S358) on each of these channels:
     - an uncaught exception other than SystemExit                       (`sys.excepthook`, as r94)
     - an exception reported to `sys.unraisablehook` (atexit callbacks, `__del__`)
     - an exception escaping a thread's run(), SystemExit included          (`threading.excepthook`)
     - any call of `os._exit` from Python code                             (`os._exit` replaced)
     - a SystemExit that reaches the main module's top level after being first raised inside a function DEFINED IN
       THE MAIN SCRIPT (seen with a `sys.monitoring` RAISE callback, S360; checked by an atexit callback registered
       first, so it runs after every callback the program registers). The counter's declared exit path is the
       top-level `sys.exit(main(...))`; a SystemExit first raised in another module (argparse's usage error) or at
       the top level itself is declared and keeps its status.
2. r95 kill rule: a mutant is ERRORED when the harness exits 70 or below 0, or any `ROW` line reads `rc=70` or a
   negative `rc` (the counter was killed by a signal, S363); otherwise KILLED only on a harness exit 1 with at least
   one `ROW ... match=no` line; a harness exit 0 is a survivor; anything else is errored.
3. Five hand edits, one per channel the r94 sentinel misses: `h-sysexit` (`raise SystemExit("h-sysexit")` in place of
   the ledger read), `h-atexit` (an atexit callback that divides by zero), `h-thread` (a joined thread that divides by
   zero), `h-osexit` (`os._exit(1)` in place of the ledger read), `h-sigkill` (`os.kill(os.getpid(), 9)` in place of
   the ledger read). The r94 search scores each of them killed or survived (census/round-95/controls).

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
HOOK = '''# souji r95 crash sentinel (census/round-95/c1-survivor-search.py): every crash channel below exits @RC@
import atexit, os, sys, threading

_SOUJI_EXIT = os._exit
_SOUJI_SEEN = {}
_SOUJI_STATE = {"foreign": None}


def _souji_crash(why):
    try:
        sys.stderr.write("SOUJI-R95-CRASH " + why + "\\n")
    except Exception:
        pass
    for s in (sys.stdout, sys.stderr):
        try:
            s.flush()
        except Exception:
            pass
    _SOUJI_EXIT(@RC@)


def _souji_excepthook(t, v, tb):
    sys.__excepthook__(t, v, tb)
    _souji_crash("uncaught " + getattr(t, "__name__", "?"))


def _souji_unraisable(u):
    sys.__unraisablehook__(u)
    _souji_crash("unraisable " + getattr(u.exc_type, "__name__", "?"))


def _souji_thread(a):
    threading.__excepthook__(a)
    _souji_crash("thread " + getattr(a.exc_type, "__name__", "?"))


def _souji_os_exit(n):
    _souji_crash("os._exit(%r)" % (n,))


def _souji_raise(code, _offset, exc):
    if not isinstance(exc, SystemExit):
        return
    main = getattr(sys.modules.get("__main__"), "__file__", None)
    seen = _SOUJI_SEEN.get(id(exc))
    if seen is None or seen[0] is not exc:
        seen = _SOUJI_SEEN[id(exc)] = (exc, code.co_filename, code.co_name)
    if main is not None and code.co_filename == main and code.co_name == "<module>":
        _SOUJI_STATE["foreign"] = seen[2] if (seen[1] == main and seen[2] != "<module>") else None


def _souji_atexit():
    if _SOUJI_STATE["foreign"] is not None:
        _souji_crash("SystemExit first raised in " + _SOUJI_STATE["foreign"] + "() of the main script")


atexit.register(_souji_atexit)
sys.excepthook = _souji_excepthook
sys.unraisablehook = _souji_unraisable
threading.excepthook = _souji_thread
os._exit = _souji_os_exit
for _souji_id in range(3, 6):
    try:
        sys.monitoring.use_tool_id(_souji_id, "souji-r95-sentinel")
    except ValueError:
        continue
    sys.monitoring.register_callback(_souji_id, sys.monitoring.events.RAISE, _souji_raise)
    sys.monitoring.set_events(_souji_id, sys.monitoring.events.RAISE)
    break
else:
    sys.stderr.write("SOUJI-R95-SENTINEL no free sys.monitoring tool id\\n")
'''.replace("@RC@", str(CRASH_RC))
CHECK = '''import argparse, atexit, os, sys, threading


def main(mode):
    if mode == "excepthook":
        raise RuntimeError("souji-r95-sentinel-check")
    if mode == "sysexit":
        raise SystemExit("souji-r95-sentinel-check")
    if mode == "atexit":
        atexit.register(lambda: 1 / 0)
    if mode == "thread":
        t = threading.Thread(target=lambda: 1 / 0)
        t.start()
        t.join()
    if mode == "osexit":
        os._exit(1)
    if mode == "argparse":
        argparse.ArgumentParser().parse_args(["--souji-r95-unknown"])
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
'''
CHECKS = (("excepthook", CRASH_RC), ("sysexit", CRASH_RC), ("atexit", CRASH_RC), ("thread", CRASH_RC),
          ("osexit", CRASH_RC), ("declared", 1), ("argparse", 2))
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
    """CRITIC cheap rule R1 (no sentinel): errored iff the harness printed no ROW line (counter died before
    judging), i.e. no ITEM line printed by any counter run. No 70, no negative-rc, no stderr test."""
    text = out.decode("utf-8", "replace")
    rows = [l for l in text.splitlines() if l.startswith("ROW ")]
    if not rows:
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
    chk_py = os.path.join(chk_dir, "souji_r95_check.py")
    with open(chk_py, "w", encoding="utf-8") as f:
        f.write(CHECK)
    got = []
    for mode, want_rc in CHECKS:
        chk = subprocess.run([sys.executable, "-B", chk_py, mode], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env, timeout=60)
        got.append(f"{mode}={chk.returncode}")
        if chk.returncode != want_rc:
            print(f"C1-SEARCH-FATAL: crash sentinel check {mode}: child exit {chk.returncode}, want {want_rc}",
                  file=sys.stderr)
            return 2
    print(f"# crash-sentinel rc={CRASH_RC} check=pass {' '.join(got)}")
    with open(ns.counter, encoding="utf-8") as f:
        src = f.read()
    for k in ("counter", "harness", "population"):
        print(f"# {k} path={getattr(ns, k)} sha256={sha(getattr(ns, k))}")
    print(f"# search sha256={sha(os.path.abspath(__file__))}")
    muts = gen(src)
    if ns.ids:
        with open(ns.ids, encoding="utf-8") as f:
            want = [x["id"] if isinstance(x, dict) else x for x in json.load(f)]
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
