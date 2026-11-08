#!/usr/bin/env python3
"""R91ReviewerC1 derivation driver (reviewer seat, NOT a round instrument).

Copies the frozen r91 harness into the seat dir with ONE change: a population file whose sha256 is
not in POP_PINS is accepted when it is one of this driver's leave-one-out derivations (the row count
is read from the file itself). Everything else -- fixture build, row judge, forge construction,
summary line -- is byte-identical to census/round-91/c1-false-row-harness.py.

Purpose: (a) dump, for each of the six new mutants on the FULL r91 population, exactly which rows go
red (the killing-row set); (b) delete each of the five new rows in turn and show that the mutant(s)
it binds survive (the leave-one-out loss).
"""
import concurrent.futures as cf
import hashlib
import json
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = os.path.join(LANE, ".ufo/waves/round-91/w1/R91ReviewerC1")
SCRATCH = "/fast/scratch/hyaku/souji-r91/R91ReviewerC1/derive"
FROZEN_HARNESS = os.path.join(LANE, "census/round-91/c1-false-row-harness.py")
FROZEN_COUNTER = os.path.join(LANE, "census/round-87/c1-pointer-counter.py")
FROZEN_POP = os.path.join(LANE, "census/round-91/c1-false-rows.tsv")
MUTANTS = os.path.join(LANE, "census/round-91/c1-mutants.json")
NEW = ("ld1c-class-keyed", "ld1d-conflict-keyed", "nf6i2-last-occurrence", "nf6j-pathch-narrow",
       "s1-exact-width", "s3-equal-two")
NEW_ROWS = ("LD1c", "LD3", "LD4", "NF6i2", "NF6j")
PIN_BLOCK = """    if not os.path.isfile(pop) or sha(pop) not in POP_PINS:
        print(f"C1-HARNESS-FATAL: population sha256 {sha(pop) if os.path.isfile(pop) else '-'} is not a pinned "
              f"population ({', '.join(sorted(POP_PINS))})", file=sys.stderr)
        return 2
    nrows = POP_PINS[sha(pop)]
"""
PIN_BLOCK_NEW = """    if not os.path.isfile(pop):
        print("C1-HARNESS-FATAL: population missing", file=sys.stderr)
        return 2
    if sha(pop) in POP_PINS:
        nrows = POP_PINS[sha(pop)]
    elif os.environ.get("R91REVIEW_DERIVED"):
        with open(pop, encoding="utf-8") as _f:
            nrows = sum(1 for _l in _f if _l.strip() and not _l.startswith("#"))
    else:
        print(f"C1-HARNESS-FATAL: population sha256 {sha(pop)} is not a pinned population", file=sys.stderr)
        return 2
"""


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    os.makedirs(SEAT + "/receipts", exist_ok=True)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH)
    der = os.path.join(SEAT, "derived-harness.py")
    src = open(FROZEN_HARNESS, encoding="utf-8").read()
    assert src.count(PIN_BLOCK) == 1, "pin block not found once"
    with open(der, "w", encoding="utf-8") as f:
        f.write(src.replace(PIN_BLOCK, PIN_BLOCK_NEW))
    print(f"derived harness {der} sha256={sha(der)}")
    print(f"frozen  harness {FROZEN_HARNESS} sha256={sha(FROZEN_HARNESS)}")

    # mutant copies
    msrc = open(FROZEN_COUNTER, encoding="utf-8").read()
    members = {m["id"]: m for m in json.load(open(MUTANTS))["members"]}
    mutdir = os.path.join(SCRATCH, "mut")
    os.makedirs(mutdir)
    paths = {}
    for mid in NEW:
        m = members[mid]
        assert msrc.count(m["old"]) == 1, mid
        p = os.path.join(mutdir, mid + ".py")
        with open(p, "w", encoding="utf-8") as f:
            f.write(msrc.replace(m["old"], m["new"]))
        paths[mid] = p
    pristine = os.path.join(mutdir, "pristine.py")
    with open(pristine, "w", encoding="utf-8") as f:
        f.write(msrc)
    paths["pristine"] = pristine

    # derived populations: leave-one-out of each new row
    poplines = open(FROZEN_POP, encoding="utf-8").read().split("\n")
    pops = {"full": FROZEN_POP}
    for rid in NEW_ROWS:
        keep = [l for l in poplines if not l.startswith(rid + "\t")]
        assert len(keep) == len(poplines) - 1, rid
        p = os.path.join(SCRATCH, f"pop-minus-{rid}.tsv")
        with open(p, "w", encoding="utf-8") as f:
            f.write("\n".join(keep))
        pops["minus-" + rid] = p

    def run_one(args):
        pop_label, pop, label, counter = args
        w = os.path.join(SCRATCH, "work", f"{pop_label}--{label}")
        shutil.rmtree(w, ignore_errors=True)
        os.makedirs(w)
        env = dict(os.environ)
        env["R91REVIEW_DERIVED"] = "1"
        env.pop("GIT_DIR", None)
        p = subprocess.run([sys.executable, "-B", der, "--counter", counter, "--lane", LANE,
                            "--fleet-root", "/home/vgpnk/Projects/shokunin", "--work", w,
                            "--population", pop],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=LANE, env=env, timeout=600)
        out, err = p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")
        shutil.rmtree(w, ignore_errors=True)  # keep the peak footprint one fixture
        return (pop_label, label, p.returncode, out, err)

    jobs = []
    for pop_label, pop in pops.items():
        for label in ("pristine",) + NEW:
            jobs.append((pop_label, pop, label, paths[label]))
    results = {}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for r in ex.map(run_one, jobs):
            results[(r[0], r[1])] = r
    outdir = os.path.join(SEAT, "receipts", "derive")
    os.makedirs(outdir, exist_ok=True)
    table = []
    for pop_label in pops:
        for label in ("pristine",) + NEW:
            pop_label_, lab, rc, out, err = results[(pop_label, label)]
            with open(os.path.join(outdir, f"{pop_label}--{label}.txt"), "w", encoding="utf-8") as f:
                f.write(out)
                if err:
                    f.write("\nSTDERR:\n" + err)
            red = [l.split()[1] for l in out.splitlines() if l.startswith("ROW ") and "match=no" in l]
            bad = [l.split()[1] for l in out.splitlines() if l.startswith("ROW ") and "match=error" in l]
            summ = [l for l in out.splitlines() if l.startswith("SUMMARY")]
            table.append({"population": pop_label, "arm": label, "exit": rc,
                          "summary": summ[-1] if summ else "-", "red_rows": red,
                          "error_rows": bad, "killed": rc != 0 or bool(red) or bool(bad),
                          "stderr": err[:300]})
    with open(os.path.join(SEAT, "receipts", "derive-table.json"), "w", encoding="utf-8") as f:
        json.dump(table, f, indent=1)
    for row in table:
        print(f"{row['population']:<10} {row['arm']:<24} exit={row['exit']} killed={row['killed']} "
              f"red={row['red_rows']} err={row['error_rows']}")
        print(f"           {row['summary']}")
    shutil.rmtree(SCRATCH, ignore_errors=True)


if __name__ == "__main__":
    main()
