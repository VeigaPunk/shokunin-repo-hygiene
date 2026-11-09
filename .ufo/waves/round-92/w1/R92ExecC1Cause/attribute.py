#!/usr/bin/env python3
"""Attribute C1 kills: for each sampled target, run r92 harness, record failing rows.
ITEM-diff via direct counter runs on r77 base ledger (no fixture needed for ledger-resolve rows;
forge-row mutants diffed by rerunning the counter in the harness-population shape is approximated by
checking whether the mutant's changed line is in the forge path (judge) vs main tally/return).
Classification by source-line semantics (read off the pristine counter):
 - exit-polarity: line is in main's tally/ok/return block (539-574) or directly flips resolved count
 - resolution: line is in judge/_whole/_capture_ok/_regular/_ledger and kills by making an r77 item
   resolve differently (UNRESOLVED/REFUSED/MISMATCH/ERROR) so the forge/base run is not all-resolved.
Field check is from the actual harness ROW lines + direct counter ITEM diffs below.
"""
import json, os, re, shutil, subprocess, sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
COUNTER = os.path.join(LANE, "census/round-87/c1-pointer-counter.py")
HARNESS = os.path.join(LANE, "census/round-92/c1-false-row-harness.py")
POP_R92 = os.path.join(LANE, "census/round-92/c1-false-rows.tsv")
TARGETS = os.path.join(LANE, "census/round-92/c1-targets.json")
SEAT = "/fast/scratch/hyaku/souji-r92/R92ExecC1Cause"
FLEET = "/home/vgpnk/Projects/shokunin"

# sample: 7 required + 7 spread across lines
SAMPLE = ["a214c12-==-to-!=", "a287c38-==-to-!=", "a294c33-not-to-drop", "a323c41-==-to-!=",
          "a344c15-!=-to-==", "a396c41-==-to-!=", "a468c44-not-to-drop", "a539c13-0-to-1",
          "a541c27-0-to-1", "a545c43-1-to-0", "a552c28-==-to-!=", "a574c11-0-to-1",
          "h-exit-always-1", "a239c28-1-to-0"]

def build_mutant(entry, outdir):
    with open(COUNTER, "rb") as f:
        src = f.read().decode()
    if src.count(entry["old"]) != 1:
        print(f"{entry['id']}: AMBIGUOUS count={src.count(entry['old'])}", file=sys.stderr)
        sys.exit(2)
    mut = src.replace(entry["old"], entry["new"], 1)
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, "counter.py")
    with open(p, "w") as f:
        f.write(mut)
    # compile check
    r = subprocess.run([sys.executable, "-B", "-m", "py_compile", p], capture_output=True)
    if r.returncode != 0:
        print(f"{entry['id']}: UNCOMPILED {r.stderr.decode()[:200]}", file=sys.stderr)
        sys.exit(2)
    return p

def run_harness(mutant_path, tid):
    work = os.path.join(SEAT, "hwork", tid)
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(work)
    p = subprocess.run([sys.executable, "-B", HARNESS, "--counter", mutant_path, "--lane", LANE,
                        "--fleet-root", FLEET, "--work", work, "--population", POP_R92],
                       capture_output=True, text=True, cwd=LANE)
    return p.returncode, p.stdout

def counter_items(counter_path, pop, ledger):
    p = subprocess.run([sys.executable, "-B", counter_path, "--root", LANE,
                        "--rev", "e65538e73c7f1a8f7570bc24a2215da8a90043f3",
                        "--fleet-root", FLEET, "--population", pop, "--ledger", ledger],
                       capture_output=True, text=True, cwd=LANE)
    return p.returncode, p.stdout

def main():
    t = {e["id"]: e for e in json.load(open(TARGETS))}
    os.makedirs(os.path.join(SEAT, "hwork"), exist_ok=True)
    # pristine r77 base-run ITEM map
    _, base_out = counter_items(COUNTER, os.path.join(LANE, "census/round-77/c2-population.tsv"),
                                os.path.join(LANE, "census/round-77/c2-pointer-ledger.tsv"))
    base_items = {m.group(1): m.group(0).strip() for m in re.finditer(r"^ITEM (\S+) .*$", base_out, re.M)}
    results = {}
    for tid in SAMPLE:
        e = t[tid]
        mdir = os.path.join(SEAT, "mutants", tid)
        mp = build_mutant(e, mdir)
        rc, out = run_harness(mp, tid)
        rows = re.findall(r"^ROW (\S+).*?rc=(\S+).*?match=(\S+)", out, re.M)
        failing = [r[0] for r in rows if r[1] != "yes"]
        # ITEM diffs on r77 base
        rc2, out2 = counter_items(mp, os.path.join(LANE, "census/round-77/c2-population.tsv"),
                                  os.path.join(LANE, "census/round-77/c2-pointer-ledger.tsv"))
        mitems = {m.group(1): m.group(0).strip() for m in re.finditer(r"^ITEM (\S+) .*$", out2, re.M)}
        changed = {k: (base_items.get(k), mitems.get(k)) for k in sorted(set(base_items) | set(mitems))
                   if base_items.get(k) != mitems.get(k)}
        # also forge-shape: rerun each forge-kind row's class? cheaper: record LD4/ledger rows handled below
        # summary line
        summ = [l for l in out.splitlines() if l.startswith("SUMMARY")]
        print(f"### {tid} line={e['line']} harness_rc={rc} {summ[0] if summ else '?'}")
        print(f"  failing_rows={[r for r in rows if r[1]!='yes']}")
        print(f"  item_changes_r77base={changed if changed else '{}'} base_rc={rc2}")
        results[tid] = {"line": e["line"], "clause": e["clause"], "harness_rc": rc,
                        "rows": [{"row": r[0], "match": r[1], "rc": r[2]} for r in rows],
                        "failing": failing, "item_changes": changed, "base_counter_rc": rc2,
                        "summary": summ[0] if summ else None}
        # delete harness work tree now (keep mutant source + receipt)
        shutil.rmtree(os.path.join(SEAT, "hwork", tid), ignore_errors=True)
    with open(os.path.join(SEAT, "results.json"), "w") as f:
        json.dump(results, f, indent=1)

if __name__ == "__main__":
    main()
