#!/usr/bin/env python3
"""souji r92 C1 alternative-edit survivor search (the r91 `### Planned (r92)` item R91MutCounter never ran).

Generates single-token operator mutants of the frozen r87 counter (census/round-87/c1-pointer-counter.py) with
`tokenize` (comparison flips, boolean-operator swaps, `not` deletion, True/False swaps, integer 0/1 swaps), plus
named hand edits, applies each EXACTLY ONCE to a scratch copy, and scores it with a pinned harness on a pinned
population. Kill rule (the battery's, unchanged): a kill is a non-zero harness exit on that population. A mutant
whose source line occurs more than once is skipped (`ambiguous`); one that does not compile is skipped
(`uncompiled`); one whose harness run exceeds --timeout seconds is stopped (its whole process group is killed) and
counted `hung` — none of the three is scored killed or survived. (r92: mutant a272c34 makes `line.find` loop
forever; without the timeout the census never finished.) Each per-mutant harness work tree (a lane clone) is deleted
once scored; harness.out stays.

Output: one `SEARCH <id> line=<n> killed=<yes|no> rc=<n>` line per scored mutant, printed as it is scored, and
`SEARCH-SUMMARY generated=<G> ambiguous=<A> uncompiled=<U> hung=<H> scored=<S> killed=<K> survived=<V>`; `--emit`
writes the survivors' {id, clause, old, new} records as JSON (`old` is the whole source line). `--ids` restricts
the run to named generated ids. Scratch only under --work (never /tmp); exit 0 when the search ran, 2 on setup
error.
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
)


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
        out.append({"id": hid, "line": ln, "clause": "hand edit: exit code", "old": old, "new": new})
    return out


def score(m, src, counter_name, ns, idx):
    if src.count(m["old"]) != 1:
        return m, "ambiguous", None
    msrc = src.replace(m["old"], m["new"], 1)
    try:
        compile(msrc, counter_name, "exec")
    except SyntaxError:
        return m, "uncompiled", None
    d = os.path.join(ns.work, f"m{idx:04d}")
    os.makedirs(d)
    mc = os.path.join(d, counter_name)
    with open(mc, "w", encoding="utf-8") as f:
        f.write(msrc)
    p = subprocess.Popen([sys.executable, "-B", ns.harness, "--counter", mc, "--lane", ns.lane,
                          "--fleet-root", ns.fleet_root, "--work", os.path.join(d, "w"),
                          "--population", ns.population], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         start_new_session=True)
    try:
        out, err = p.communicate(timeout=ns.timeout)
        state = "scored"
    except subprocess.TimeoutExpired:
        # the harness and the counter it spawns share one session: kill the whole group (r92: a272c34 loops)
        os.killpg(p.pid, signal.SIGKILL)
        out, err = p.communicate()
        state = "hung"
    with open(os.path.join(d, "harness.out"), "wb") as f:
        f.write(out + b"\n--stderr--\n" + err + (b"\n--hung: killed after --timeout--\n" if state == "hung" else b""))
    # each harness work tree is a lane clone (~0.7 GB): drop it once scored, keep harness.out (fleet disk, r92)
    shutil.rmtree(os.path.join(d, "w"), ignore_errors=True)
    return m, state, p.returncode


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
    if os.path.realpath(ns.work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("C1-SEARCH-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
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
    with cf.ThreadPoolExecutor(max_workers=ns.jobs) as ex:
        futs = [ex.submit(score, m, src, name, ns, i) for i, m in enumerate(muts)]
        for fu in futs:
            m, s, rc = fu.result()
            res.append((m, s, rc))
            if s == "scored":
                print(f"SEARCH {m['id']} line={m['line']} killed={'no' if rc == 0 else 'yes'} rc={rc}", flush=True)
            else:
                print(f"SKIP {m['id']} line={m['line']} state={s}", flush=True)
    amb = sum(1 for _m, s, _rc in res if s == "ambiguous")
    unc = sum(1 for _m, s, _rc in res if s == "uncompiled")
    hung = sum(1 for _m, s, _rc in res if s == "hung")
    scored = [(m, rc) for m, s, rc in res if s == "scored"]
    surv = [m for m, rc in scored if rc == 0]
    print(f"SEARCH-SUMMARY generated={len(muts)} ambiguous={amb} uncompiled={unc} hung={hung} scored={len(scored)} "
          f"killed={len(scored) - len(surv)} survived={len(surv)}")
    if ns.emit:
        with open(ns.emit, "w", encoding="utf-8") as f:
            json.dump([{k: m[k] for k in ("id", "clause", "old", "new")} for m in surv], f, indent=1)
            f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
