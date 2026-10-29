#!/usr/bin/env python3
"""Noise floor: run the PRISTINE counter copy N more times per artifact (same command as the matrix).

Replicate records are written under receipts/ as REP<k>__<artifact>.json; analyze.py ignores them,
noise.py reads them.
"""
import concurrent.futures
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import driver  # noqa: E402

REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 3


def main():
    jobs = []
    for k in range(1, REPS + 1):
        for aname, afix in driver.ARTIFACTS:
            jobs.append(("REP%d" % k, "replicate", driver.PRISTINE, aname, afix))
    recs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(jobs)) as ex:
        futs = [ex.submit(driver.run_job, *j) for j in jobs]
        for f in concurrent.futures.as_completed(futs):
            r = f.result()
            recs.append(r)
            print("%s %s rc=%s %s" % (r["mutant"], r["artifact"], r["rc"], r["summary"]), flush=True)
    print("DONE %d replicate records" % len(recs), flush=True)


if __name__ == "__main__":
    main()
