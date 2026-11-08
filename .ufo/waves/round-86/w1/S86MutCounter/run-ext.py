#!/usr/bin/env python3
"""souji r86 S86MutCounter driver: score the frozen eight and my eight new single-edit mutants on both pinned
populations with the FILED detector census/round-86/c1-false-row-harness.py, and split a kill into mismatches vs
errors (a row the harness could not judge at all is not the same kill as a row that came back wrong).

Writes only --work (never /tmp) and --out (this seat's receipts). Reads the lane. No git/jj mutation: the harness's
own `git clone --shared` and `git init` in a scratch clone are the harness's, and every one of its git calls is
`git -C <fixture>` with an absolute path asserted inside the harness.
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
COUNTER = os.path.join(LANE, "census/round-86/c1-pointer-counter.py")
HARNESS = os.path.join(LANE, "census/round-86/c1-false-row-harness.py")
POPS = {"r85": (os.path.join(LANE, "census/round-85/c1-false-rows.tsv"),
                "1468236cfc3c8f65e7fa9bb07884324ee8ae8b7f62d6d5ca984b9dfa04698d42", 47),
        "r86": (os.path.join(LANE, "census/round-86/c1-false-rows.tsv"),
                "79db70f6740de41a326dc4193bf80c5394fe126d636cc98d4e26e4b5e140f561", 49)}
SUMM = re.compile(r"^SUMMARY rows=(\d+) mismatches=(\d+) accepted=(\d+) refused_true=(\d+) errors=(\d+)$", re.M)


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def one(counter, pop, work, receipts):
    path, pin, nrows = POPS[pop]
    assert sha(path) == pin, f"population pin drift {pop}"
    d = os.path.join(work, f"run-{os.path.basename(counter)[:-3]}-{pop}")
    if os.path.exists(d) and os.listdir(d):
        raise SystemExit(f"work dir not empty: {d}")
    p = subprocess.run([sys.executable, "-B", HARNESS, "--counter", counter, "--lane", LANE,
                        "--fleet-root", FLEET, "--work", d, "--population", path],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=LANE)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    tag = f"{os.path.basename(counter)[:-3]}__{pop}"
    with open(os.path.join(receipts, tag + ".txt"), "w", encoding="utf-8") as f:
        f.write(f"# counter {counter} sha256={sha(counter)}\n# population {path} sha256={pin} rows={nrows}\n")
        f.write(f"# harness {HARNESS} sha256={sha(HARNESS)}\n# exit {p.returncode}\n")
        f.write(out)
        if err:
            f.write("\n# STDERR\n" + err)
    m = SUMM.search(out)
    if not m:
        return {"id": tag, "rows": 0, "mism": -1, "errs": -1, "rc": p.returncode, "red": [],
                "judge_err": [f"NO SUMMARY: {err.strip()[:160]}"]}
    rows, mism, acc, reft, errs = (int(x) for x in m.groups())
    red = [l for l in out.splitlines() if l.startswith("ROW ") and "match=no" in l]
    jerr = [l for l in out.splitlines() if l.startswith("ROW ") and "match=error" in l]
    return {"id": tag, "rows": rows, "mism": mism, "errs": errs, "rc": p.returncode, "red": red,
            "judge_err": jerr, "acc": acc, "reft": reft}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--receipts", required=True)
    ap.add_argument("--jobs", type=int, default=12)
    ns = ap.parse_args(argv)
    work, receipts = os.path.abspath(ns.work), os.path.abspath(ns.receipts)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("DRIVER-FATAL: --work under /tmp", file=sys.stderr)
        return 2
    os.makedirs(os.path.join(work, "mut"), exist_ok=True)
    os.makedirs(receipts, exist_ok=True)
    print(f"# counter {COUNTER} sha256={sha(COUNTER)}")
    print(f"# harness {HARNESS} sha256={sha(HARNESS)}")
    src = open(COUNTER, encoding="utf-8").read()
    frozen = json.load(open(os.path.join(LANE, "census/round-86/c1-mutants.json"), encoding="utf-8"))
    ext = json.load(open(os.path.join(LANE, ".ufo/waves/round-86/w1/S86MutCounter/mutants-ext.json"),
                        encoding="utf-8"))
    print(f"# c1-mutants.json sha256={sha(os.path.join(LANE, 'census/round-86/c1-mutants.json'))} "
          f"members={len(frozen['members'])}")
    print(f"# mutants-ext.json sha256={sha(os.path.join(LANE, '.ufo/waves/round-86/w1/S86MutCounter/mutants-ext.json'))} "
          f"members={len(ext['members'])}")
    copies = []
    for m in frozen["members"] + ext["members"]:
        n = src.count(m["old"])
        if n != 1:
            print(f"DRIVER-FATAL: {m['id']} old occurs {n} times, need exactly 1", file=sys.stderr)
            return 2
        out = os.path.join(work, "mut", m["id"] + ".py")
        with open(out, "w", encoding="utf-8") as f:
            f.write(src.replace(m["old"], m["new"]))
        copies.append((m["id"], out, "frozen" if m in frozen["members"] else "ext", m.get("clause", "")))
    counters = [("pristine", COUNTER, "pristine", "the filed counter, unchanged")] + copies
    jobs = [(cid, path, pop) for cid, path, _s, _c in counters for pop in ("r85", "r86")]
    res = {}
    with cf.ThreadPoolExecutor(max_workers=ns.jobs) as ex:
        futs = {ex.submit(one, path, pop, work, receipts): (cid, pop) for cid, path, pop in jobs}
        for f in cf.as_completed(futs):
            cid, pop = futs[f]
            res[(cid, pop)] = f.result()
    # summary receipt
    lines = [f"# counter sha256={sha(COUNTER)}", f"# harness sha256={sha(HARNESS)}",
             "# columns: id kind clause pop rows mismatches errors exit killed red_rows"]
    for cid, path, kind, clause in counters:
        for pop in ("r85", "r86"):
            r = res[(cid, pop)]
            killed = r["rc"] != 0 or r["mism"] > 0 or r["errs"] > 0
            lines.append(f"{cid}\t{kind}\t{clause}\t{pop}\t{r['rows']}\t{r['mism']}\t{r['errs']}\t{r['rc']}\t"
                         f"{'yes' if killed else 'no'}\t{len(r['red'])}")
            for l in r["red"]:
                lines.append(f"  RED {l}")
            for l in r["judge_err"]:
                lines.append(f"  ERR {l}")
    text = "\n".join(lines) + "\n"
    with open(os.path.join(receipts, "ext-summary.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    # console table
    print("TABLE id | pop=r85 | pop=r86")
    for cid, _p, kind, _c in counters:
        cells = []
        for pop in ("r85", "r86"):
            r = res[(cid, pop)]
            k = r["rc"] != 0 or r["mism"] > 0 or r["errs"] > 0
            cells.append(f"killed={'yes' if k else 'no'} m={r['mism']} e={r['errs']} rc={r['rc']} "
                         f"red={len(r['red'])}")
        print(f"{cid} [{kind}] | {cells[0]} | {cells[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
