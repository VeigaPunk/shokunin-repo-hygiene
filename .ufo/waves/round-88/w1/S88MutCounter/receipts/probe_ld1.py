import subprocess, sys, os
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
BASE = "e65538e73c7f1a8f7570bc24a2215da8a90043f3"
COUNTER = os.path.join(LANE, "census/round-87/c1-pointer-counter.py")
POP = os.path.join(LANE, "census/round-77/c2-population.tsv")
HERE = os.path.dirname(os.path.abspath(__file__))
base = open(os.path.join(LANE, "census/round-77/c2-pointer-ledger.tsv"), "rb").read()
cases = {
    "dup_same_class_same_target": "P01\tFLEET\t-\tr88 probe: same class, same target",
    "dup_same_class_diff_target": "P01\tFLEET\tcensus/nowhere/r88\tprobe: same class, different target",
    "dup_diff_class_same_target": "P01\tABSENT\t-\tprobe: filed LD1 shape (diff class, same target)",
    "dup_diff_class_diff_target": "P01\tABSENT\tcensus/nowhere/r88\tprobe: diff class, diff target",
    "dup_row_2col": "P02\tABSENT",
    "newid_2col_malformed": "ZZ9\tABSENT",
    "newid_3col": "ZZ9\tABSENT\t-",
    "dup_3col": "P01\tABSENT\t-",
    "dup_3col_p02": "P02\tABSENT\t-",
    "dup_1col": "P09",
}
for name, row in cases.items():
    path = os.path.join(HERE, name + ".tsv")
    open(path, "wb").write(base + (b"" if base.endswith(b"\n") else b"\n") + row.encode() + b"\n")
    p = subprocess.run([sys.executable, "-B", COUNTER, "--root", LANE, "--rev", BASE, "--fleet-root", FLEET,
                        "--population", POP, "--ledger", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       cwd=LANE)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    marks = [l for l in out.splitlines() if l.startswith("LEDGER-REFUSED")]
    summ = [l for l in out.splitlines() if l.startswith("SUMMARY")]
    print(f"CASE {name:28s} cols={row.count(chr(9)) + 1} rc={p.returncode} markers={marks} "
          f"{summ[0] if summ else ''} stderr={err[:80]!r}")
