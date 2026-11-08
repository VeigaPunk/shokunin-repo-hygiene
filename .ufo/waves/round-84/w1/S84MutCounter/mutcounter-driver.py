#!/usr/bin/env python3
"""souji r84 C1 extension driver (seat S84MutCounter): score ten single-edit mutants of the pointer counter on both
pinned false-row populations with census/round-84/c1-false-row-harness.py, and attribute each kill to the row(s).

Read-only on the lane. Writes only under --work (never /tmp) and --out (the seat dir). Stdlib only.

Rule for a cell: KILLED iff the harness exits non-zero (the battery's rule: rc != 0 => a row mismatch or an error).
The killer rows are the ROW ids whose match flips from yes (pristine) to no (mutant) or whose run reports an error.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

PINS = {
    "r83": ("c9a6d58c1cf84a40a02a85a7342df2f2bd37301ba02e8f61ac91eded624e02eb", 36),
    "r84": ("4795f009d6c873e733a2992bc86405d509dfb105b5f9950b3b9f82b2596e8f6f", 44),
}
ROW = re.compile(r"^ROW (\S+) where=(\S+) rev=(\S+) item=(\S+) class=(\S+) expect=(\S+)/(\S+) "
                 r"got=(\S+) rc=(-?\d+) match=(\w+)")
SUMM = re.compile(r"^SUMMARY rows=(\d+) mismatches=(\d+) accepted=(\d+) refused_true=(\d+) errors=(\d+)$", re.M)


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run_one(harness, counter, lane, fleet, workroot, logs, tag, poplabel, pop):
    work = os.path.join(workroot, f"{tag}-{poplabel}")
    if os.path.exists(work):
        raise SystemExit(f"DRIVER-FATAL: work dir {work} already exists")
    p = subprocess.run([sys.executable, "-B", harness, "--counter", counter, "--lane", lane,
                        "--fleet-root", fleet, "--work", work, "--population", pop],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=lane, timeout=1800)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    log = os.path.join(logs, f"{tag}-{poplabel}.log")
    with open(log, "w", encoding="utf-8") as f:
        f.write(out)
        if err:
            f.write("\n# STDERR\n" + err)
    # keep the fixture only as long as the run needs it
    shutil.rmtree(work, ignore_errors=True)
    rows = {}
    for line in out.splitlines():
        m = ROW.match(line)
        if m:
            rid, where, rev, item, cls, exp_got, exp_rc, got, rc, match = m.groups()
            rows[rid] = {"where": where, "rev": rev, "item": item, "class": cls,
                         "expect": f"{exp_got}/{exp_rc}", "got": got, "rc": int(rc), "match": match}
    s = SUMM.search(out)
    summary = ({"rows": int(s.group(1)), "mismatches": int(s.group(2)), "accepted": int(s.group(3)),
                "refused_true": int(s.group(4)), "errors": int(s.group(5))} if s else None)
    return {"tag": tag, "pop": poplabel, "exit": p.returncode, "summary": summary, "rows": rows,
            "log": log, "counter_sha256": sha(counter), "stderr_tail": err[-400:]}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness", required=True)
    ap.add_argument("--counter", required=True)
    ap.add_argument("--lane", required=True)
    ap.add_argument("--fleet-root", required=True)
    ap.add_argument("--work", required=True, help="scratch root (never /tmp); per-run dirs are created below it")
    ap.add_argument("--out", required=True, help="seat dir for results.json, mutants/ and logs/")
    ap.add_argument("--mutants", required=True)
    ap.add_argument("--jobs", type=int, default=4)
    ns = ap.parse_args(argv)
    lane, fleet, work = (os.path.abspath(x) for x in (ns.lane, ns.fleet_root, ns.work))
    out, counter = os.path.abspath(ns.out), os.path.abspath(ns.counter)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("DRIVER-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.realpath(out).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("DRIVER-FATAL: --out under /tmp", file=sys.stderr)
        return 2
    logs, mutdir = os.path.join(out, "receipts", "logs"), os.path.join(out, "mutants")
    os.makedirs(logs, exist_ok=True)
    os.makedirs(mutdir, exist_ok=True)
    os.makedirs(work, exist_ok=True)
    pops = {lbl: os.path.join(lane, "census", "round-84" if lbl == "r84" else "round-83", "c1-false-rows.tsv")
            for lbl in PINS}
    for lbl, (pin, n) in PINS.items():
        if not os.path.isfile(pops[lbl]) or sha(pops[lbl]) != pin:
            print(f"DRIVER-FATAL: {lbl} population is not the pin {pin}", file=sys.stderr)
            return 2
    doc = json.load(open(ns.mutants, encoding="utf-8"))
    src = open(counter, encoding="utf-8").read()
    members = doc["members"]
    for m in members:
        n = src.count(m["old"])
        if n != 1:
            print(f"DRIVER-FATAL: edit {m['id']} occurs {n} times, need exactly 1", file=sys.stderr)
            return 2
    for m in members:
        p = os.path.join(mutdir, m["id"] + ".py")
        with open(p, "w", encoding="utf-8") as f:
            f.write(src.replace(m["old"], m["new"]))
        m["_path"] = p
        m["_sha256"] = sha(p)

    tasks = [("pristine", counter, lbl) for lbl in sorted(PINS)]
    tasks += [(m["id"], m["_path"], lbl) for m in members for lbl in sorted(PINS)]
    results = {}
    with ThreadPoolExecutor(max_workers=ns.jobs) as ex:
        futs = {ex.submit(run_one, ns.harness, path, lane, fleet, work, logs, tag, lbl, pops[lbl]): (tag, lbl)
                for tag, path, lbl in tasks}
        for f in futs:
            r = f.result()
            results[(r["tag"], r["pop"])] = r
    pristine = {lbl: results[("pristine", lbl)] for lbl in PINS}
    bad = []
    for lbl in sorted(PINS):
        pr = pristine[lbl]
        red = [rid for rid, r in pr["rows"].items() if r["match"] != "yes"]
        print(f"PRISTINE pop={lbl} exit={pr['exit']} summary={pr['summary']} nonmatching={red or 'none'}")
        if pr["exit"] != 0 or pr["summary"] is None or red:
            bad.append(lbl)
    if bad:
        print(f"DRIVER-FATAL: the unmutated counter is not green on {bad}", file=sys.stderr)
        return 2
    report = {"counter": os.path.relpath(counter, lane), "counter_sha256": sha(counter),
              "harness": os.path.relpath(os.path.abspath(ns.harness), lane),
              "harness_sha256": sha(os.path.abspath(ns.harness)),
              "mutants_json": os.path.relpath(os.path.abspath(ns.mutants), lane),
              "mutants_json_sha256": sha(os.path.abspath(ns.mutants)),
              "populations": {lbl: {"path": os.path.relpath(pops[lbl], lane), "sha256": PINS[lbl][0],
                                    "rows": PINS[lbl][1]} for lbl in PINS},
              "pristine": {lbl: {"exit": pristine[lbl]["exit"], "summary": pristine[lbl]["summary"]}
                           for lbl in PINS},
              "members": [], "table": []}
    for m in members:
        entry = {"id": m["id"], "clause": m["clause"], "sha256": m["_sha256"], "pops": {}}
        cells = []
        for lbl in sorted(PINS):
            r = results[(m["id"], lbl)]
            pr = pristine[lbl]
            killers = []
            for rid, row in r["rows"].items():
                if row["match"] != "yes" and pr["rows"].get(rid, {}).get("match") == "yes":
                    killers.append(rid)
            for rid in pr["rows"]:
                if rid not in r["rows"]:
                    killers.append(rid + "(no ROW line)")
            killed = r["exit"] != 0 or (r["summary"] or {}).get("mismatches", 0) > 0 \
                or (r["summary"] or {}).get("errors", 0) > 0
            entry["pops"][lbl] = {"killed": bool(killed), "exit": r["exit"], "summary": r["summary"],
                                  "killers": sorted(killers)}
            cells.append(("yes" if killed else "no", ", ".join(sorted(killers)) or "-",
                          (r["summary"] or {}).get("mismatches")))
        print(f"MUTANT {m['id']} r83={cells[0]} | r84={cells[1]}")
        report["members"].append(entry)
        report["table"].append({"id": m["id"], "clause": m["clause"],
                                "r83": "yes" if entry["pops"]["r83"]["killed"] else "no",
                                "r84": "yes" if entry["pops"]["r84"]["killed"] else "no",
                                "r83_rows": entry["pops"]["r83"]["killers"],
                                "r84_rows": entry["pops"]["r84"]["killers"]})
    with open(os.path.join(out, "results.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    lines = ["| mutant | clause | killed r83 | killed r84 | row(s) that kill it |",
             "|---|---|---|---|---|"]
    for row in report["table"]:
        rows = sorted(set(row["r83_rows"]) | set(row["r84_rows"]))
        lines.append(f"| `{row['id']}` | {row['clause']} | {row['r83']} | {row['r84']} | "
                     f"{', '.join(rows) if rows else '— (survives both)'} |")
    with open(os.path.join(out, "mutcounter-table.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    killed = sum(1 for row in report["table"] if row["r84"] == "yes")
    print(f"SUMMARY mutants={len(members)} r83_killed={sum(1 for row in report['table'] if row['r83'] == 'yes')} "
          f"r84_killed={killed}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
