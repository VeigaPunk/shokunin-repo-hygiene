#!/usr/bin/env python3
"""L1 pre-freeze survey (r42): which of the eight committed drift fixtures kill each mutant of the r41 wave-2 survivor list.
Reads the pinned tool and fixtures from the working tree of the lane at --rev's checkout; prints one line per mutant.
  python3 -B census/round-42/records/survey-prior.py --lane LANE --scratch DIR
"""
import argparse, concurrent.futures, importlib.util, os, shutil, sys, tempfile
a = argparse.ArgumentParser(); a.add_argument("--lane", required=True); a.add_argument("--scratch", required=True); a = a.parse_args()
spec = importlib.util.spec_from_file_location("c3", os.path.join(a.lane, "census/round-42/c3-counter.py")); c3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c3)
EXTRA = (("D3", "if st.st_nlink > 1:", "if st.st_nlink >= 1:"),
         ("F2", "alias = (rec_st.st_dev, rec_st.st_ino) == (out_st.st_dev, out_st.st_ino)", "alias = False"),
         ("H3", 'action="store_true"', 'action="store_false"'),
         ("J5", "totals.append(total)", "totals[:] = [total]"),
         ("N1", "return 0 if not drift else 1", "return 0"),
         ("T2", 'if total["repos"] != len(rows):', 'if total["repos"] > len(rows):'),
         ("F1", "alias = record_abs == json_target", "alias = False"))
tool = open(os.path.join(a.lane, c3.TOOL), encoding="utf-8").read()
d = tempfile.mkdtemp(prefix="survey.", dir=a.scratch)
try:
    pristine = os.path.join(d, "pristine.py"); c3.write(pristine, tool, 0o755)
    fx = {p: os.path.join(a.lane, p) for p in c3.PRIOR}
    jobs = {}
    for mid, old, new in EXTRA:
        assert tool.count(old) == 1, mid
        mp = os.path.join(d, "mut-%s.py" % mid); c3.write(mp, tool.replace(old, new), 0o755); jobs[mid] = mp
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futs = {(m, p): pool.submit(c3.run, fx[p], jobs[m], d, m) for m in jobs for p in fx}
        res = {k: v.result() for k, v in futs.items()}
    for m in jobs:
        by = [os.path.basename(p) for p in c3.PRIOR if c3.killed(res[(m, p)])]
        print("MUTANT %s killed-by-prior-fixtures=%s" % (m, ",".join(by) or "-"))
finally:
    shutil.rmtree(d, ignore_errors=True)
