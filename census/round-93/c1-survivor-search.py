#!/usr/bin/env python3
"""souji r93 C1 survivor search: the r92 search (census/round-92/c1-survivor-search.py) with three changes.

1. Kill rule (r92 A3: the r92 rule scored ANY non-zero harness exit, so a crashing counter counted as killed): a
   mutant is KILLED only when the harness exits 1 AND prints at least one `ROW ... match=no` line (a row's asserted
   verdict or exit code differs). A harness exit 2, or an exit 1 whose only failing rows are `match=error` (the
   counter crashed, rc 2), is `errored` -- neither killed nor survived.
2. One more hand edit, `h-ok-admits-one` (R92MutC1 E1): the success test `resolved == len(pop)` slackened to
   `resolved >= len(pop) - 1`, which survived the r91 and r92 populations.
3. Robustness (R92Sentinel M1/L1): SIGINT/SIGTERM stop the search, kill every live harness process group and delete
   every per-mutant work tree before exit (exit 130); the bare-/tmp guard covers --work and --emit.

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
)
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
    """r93 kill rule: killed only on a harness exit 1 with at least one asserted row mismatch (`match=no`)."""
    if rc == 0:
        return "no"
    if rc == 1 and any(l.startswith("ROW ") and l.endswith(" match=no") for l in out.decode("utf-8", "replace")
                       .splitlines()):
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
    p = subprocess.Popen([sys.executable, "-B", ns.harness, "--counter", mc, "--lane", ns.lane,
                          "--fleet-root", ns.fleet_root, "--work", os.path.join(d, "w"),
                          "--population", ns.population], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         start_new_session=True)
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
