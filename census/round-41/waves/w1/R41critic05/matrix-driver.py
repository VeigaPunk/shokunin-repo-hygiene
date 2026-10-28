import importlib.util, os, shutil, sys, tempfile

FROZEN = "/fast/scratch/hyaku/souji-r41/R41critic05/frozen"
SCR = "/fast/scratch/hyaku/souji-r41/R41critic05"
PROBE = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41critic05/r41-drift-record-order.probe.py"

spec = importlib.util.spec_from_file_location("r1c", os.path.join(FROZEN, "census/round-41/r1-counter.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

source = open(os.path.join(FROZEN, "tools/souji-worktree-drift.py"), encoding="utf-8").read()
scratch = tempfile.mkdtemp(prefix="matrix.", dir=SCR)
try:
    pristine = os.path.join(scratch, "pristine.py")
    m.write(pristine, source, 0o755)
    fx = {}
    for name, path in (("r39", "tests/fixtures/r39-drift-record-rules.py"),
                       ("r40", "tests/fixtures/r40-drift-record-branches.py"),
                       ("probe", PROBE)):
        src = path if os.path.isabs(path) else os.path.join(FROZEN, path)
        dst = os.path.join(scratch, "fx-" + os.path.basename(src))
        shutil.copy(src, dst)
        fx[name] = dst
    for mid, old, new, owner in m.MUTANTS:
        print("ANCHOR %s count=%d owner=%s" % (mid, source.count(old), os.path.basename(owner)))
    print("PRISTINE")
    for name in ("r39", "r40", "probe"):
        r = m.run(fx[name], pristine, scratch)
        print("  %s rc=%s cases=%s pass=%s fail=%s crash=%s failing=%s clean=%s" % (
            name, r[0], r[1], r[2], r[3], r[4], ",".join(r[5]) or "-", m.clean(r)))
    for mid, old, new, owner in m.MUTANTS:
        mpath = os.path.join(scratch, mid + ".py")
        m.write(mpath, source.replace(old, new), 0o755)
        row = []
        for name in ("r39", "r40", "probe"):
            r = m.run(fx[name], mpath, scratch)
            row.append("%s:killed=%s(rc=%s,failing=%s)" % (name, m.killed(r), r[0], ",".join(r[5]) or "-"))
        print("MUTANT %s owner=%s  %s" % (mid, os.path.basename(owner), "  ".join(row)))
finally:
    shutil.rmtree(scratch, ignore_errors=True)
