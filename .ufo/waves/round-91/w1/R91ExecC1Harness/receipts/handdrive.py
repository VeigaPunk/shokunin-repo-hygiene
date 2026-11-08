import hashlib, json, os, subprocess, sys
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
S = "/fast/scratch/hyaku/souji-r91/R91ExecC1Harness"
FX = os.path.join(S, "work-r91", "fixture")
R13 = "8a61ecf4e4f494cac85cfd80d8170c3666818766"
COUNTER = os.path.join(LANE, "census/round-87/c1-pointer-counter.py")
MUT = {m["id"]: m for m in json.load(open(os.path.join(LANE, "census/round-91/c1-mutants.json")))["members"]}
D = os.path.join(S, "drive"); os.makedirs(D, exist_ok=True)
src = open(COUNTER, encoding="utf-8").read()
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
def mutant_path(mid):
    m = MUT[mid]
    assert src.count(m["old"]) == 1, (mid, src.count(m["old"]))
    p = os.path.join(D, mid + ".py")
    open(p, "w", encoding="utf-8").write(src.replace(m["old"], m["new"]))
    return p
def run(label, counter, root, rev, pop, ledger, forge=None):
    cmd = [sys.executable, "-B", counter, "--root", root, "--rev", rev, "--fleet-root", FLEET,
           "--population", pop, "--ledger", ledger]
    if forge: cmd += ["--forge", forge]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=LANE)
    out = p.stdout.decode("utf-8", "replace"); err = p.stderr.decode("utf-8", "replace")
    print(f"### {label}  (counter={os.path.basename(counter)} sha256={sha(counter)[:16]}...)")
    keep = [l for l in out.splitlines() if l.startswith("FORGE ") or l.startswith("ITEM P04 ")
            or l.startswith("LEDGER-REFUSED") or l.startswith("SUMMARY")]
    for l in keep: print(l)
    print(f"EXIT={p.returncode}" + (f" STDERR={err.strip().splitlines()[-1]!r}" if err.strip() else ""))
    print()
    return p.returncode, out, err
r77pop = os.path.join(LANE, "census/round-77/c2-population.tsv")
r77led = os.path.join(LANE, "census/round-77/c2-pointer-ledger.tsv")
r78pop = os.path.join(LANE, "census/round-78/c2-population.tsv")
r78led = os.path.join(LANE, "census/round-78/c2-pointer-ledger.tsv")
base = open(r77led, "rb").read()
def mkledger(name, appended):
    p = os.path.join(D, name)
    open(p, "wb").write(base + (b"" if base.endswith(b"\n") else b"\n") + appended.encode())
    return p
ld1c_led = mkledger("ledger-LD1c.tsv", "P01\tFLEET\t-\tr91 LD1c identical duplicate (class and target equal)\n")
ld3_led = mkledger("ledger-LD3.tsv", "ZY8\n")
# --- NF6i2 / NF6j one-row forges at R13 ---
for rid, target in (("NF6i2", ".ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/last-stub"),
                    ("NF6j", ".ufo/quarantine/round-17/tests/vault/vadv54-run/p/p6repo/pathch-stub")):
    forge = os.path.join(D, f"forge-{rid}.tsv")
    open(forge, "w", encoding="utf-8").write(f"{rid}\tL06\tQUARANTINED\t{target}\tREFUSED\n")
    print(f"=== R13 forge {rid}: {open(forge).read().strip()} ===")
    for label, ctr in (("pristine", COUNTER), ("nf6i2-last-occurrence", mutant_path("nf6i2-last-occurrence")),
                       ("nf6j-pathch-narrow", mutant_path("nf6j-pathch-narrow"))):
        run(f"{rid} / {label}", ctr, FX, R13, r78pop, r78led, forge)
# --- LD1c / LD3 / LD4 ---
for rid, led, rev, root, pop in (("LD1c", ld1c_led, "e65538e73c7f1a8f7570bc24a2215da8a90043f3", LANE, r77pop), ("LD3", ld3_led, "e65538e73c7f1a8f7570bc24a2215da8a90043f3", LANE, r77pop),
                                 ("LD4", r77led, "e65538e73c7f1a8f7570bc24a2215da8a90043f3", LANE, r77pop)):
    print(f"=== ledger drive {rid} (ledger sha256={sha(led)[:16]}...) ===")
    for label, ctr in (("pristine", COUNTER), ("ld1c-class-keyed", mutant_path("ld1c-class-keyed")),
                       ("ld1d-conflict-keyed", mutant_path("ld1d-conflict-keyed")),
                       ("s3-equal-two", mutant_path("s3-equal-two")), ("s1-exact-width", mutant_path("s1-exact-width"))):
        run(f"{rid} / {label}", ctr, root, rev, pop, led)
