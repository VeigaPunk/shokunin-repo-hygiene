# P-flake probe: runs the frozen prior fixture r36 against one frozen mutant N times, serially, with the
# counter's own run() invocation shape (argv, env from the counter's env()). Read-only over the tip blobs.
import importlib.util, os, subprocess, sys, tempfile, shutil, time
lane, rev, scratch, mid, n = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
spec = importlib.util.spec_from_file_location("c3c", os.path.join(lane, "census/round-42/c3-counter.py"))
c3c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c3c)
src = subprocess.run(["git", "-C", lane, "show", "%s:tools/souji-worktree-drift.py" % rev], capture_output=True).stdout.decode("utf-8")
fx = subprocess.run(["git", "-C", lane, "show", "%s:tests/fixtures/r36-worktree-drift.py" % rev], capture_output=True).stdout
d = tempfile.mkdtemp(prefix="flake.", dir=scratch)
try:
    fxp = os.path.join(d, "fx-r36.py"); open(fxp, "wb").write(fx)
    row = [m for m in c3c.MUTANTS + c3c.EQUIV if m[0] == mid][0]
    assert src.count(row[2]) == 1
    mp = os.path.join(d, "mut-%s.py" % mid); open(mp, "w", encoding="utf-8").write(src.replace(row[2], row[3]))
    counts = {}
    for i in range(n):
        res = c3c.run(fxp, mp, d, "f%d" % i)
        key = (res[0], res[1], res[3], res[4])
        counts[key] = counts.get(key, 0) + 1
        print("run %d rc=%s cases=%s failed=%s crash=%s" % (i, res[0], res[1], res[3], res[4]))
    print("tally (rc, cases, failed, crash) -> count:", counts)
    print("killed-by-r36 in", sum(v for k, v in counts.items() if k[0] == 1 and k[2] and k[2] > 0 and not k[3]), "of", n, "runs")
finally:
    shutil.rmtree(d, ignore_errors=True)
