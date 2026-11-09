#!/usr/bin/env python3
"""R92MutC1 probe driver: hand-edited alternative mutants scored with the frozen r92 harness.
Sequential, at most one work tree at a time (harness deletes its own fixture after each run;
we delete w/ after each scored mutant). Each result appended to results.json."""
import json, os, shutil, subprocess, sys, hashlib

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = os.path.join(LANE, ".ufo/waves/round-92/w1/R92MutC1")
S = "/fast/scratch/hyaku/souji-r92/R92MutC1"
HARNESS = os.path.join(LANE, "census/round-92/c1-false-row-harness.py")
POP_R92 = os.path.join(LANE, "census/round-92/c1-false-rows.tsv")
POP_R91 = os.path.join(LANE, "census/round-91/c1-false-rows.tsv")
SRC = open(os.path.join(LANE, "census/round-87/c1-pointer-counter.py"), encoding="utf-8").read()

def sha(b):
    return hashlib.sha256(b.encode()).hexdigest()[:12]

def apply(old, new):
    n = SRC.count(old)
    assert n == 1, f"old line occurs {n} times: {old!r}"
    return SRC.replace(old, new, 1)

# (id, old, new, description)
EDITS = [
    ("E1-ok-relaxed",
     "    ok = counts[\"resolved\"] == len(pop) and not unknown\n",
     "    ok = counts[\"resolved\"] >= len(pop) - 1 and not unknown\n",
     "line 552: == len(pop) -> >= len(pop)-1 (admits one unresolved)"),
    ("E2-return-0-if-ok-or-forged",
     "    return 0 if ok else 1\n",
     "    return 0 if ok or forged else 1\n",
     "line 574: return polarities swapped with forged escape (forge path unbound)"),
    ("E3-unresolved-noop",
     "        counts[key.get(st, \"resolved\")] += 1\n",
     "        counts[\"unresolved\"] += 0\n",
     "line 545: tally writes to wrong key with 0 (resolved tally broken differently)"),
    ("E4-ok-drop-unknown",
     "    ok = counts[\"resolved\"] == len(pop) and not unknown\n",
     "    ok = counts[\"resolved\"] == len(pop)\n",
     "line 552: drop `and not unknown` (unknown-id ledger never fails the run)"),
    ("E5-return-and-ok",
     "    return 0 if ok else 1\n",
     "    return 0 if (ok and True) else 1\n",
     "line 574: logically equivalent tautology (coverage probe)"),
    ("E6-summary-text",
     "    print(f\"SUMMARY items={len(pop)} resolved={counts['resolved']} unresolved={counts['unresolved']} \"\n"
     "          f\"refused={counts['refused']} mismatched={counts['mismatched']} errors={counts['errors']}\")\n",
     "    print(f\"SUMMARY items={len(pop)} resolved={counts['resolved']} unresolved={counts['unresolved']} \"\n"
     "          f\"refused={counts['refused']} mismatched={counts['mismatched']} errors={counts['errors']} EXTRA=1\")\n",
     "line 550-551: SUMMARY gains a field (output-only mutation)"),
    ("E7-forge-tally-noop",
     "                forged += 1\n",
     "                forged += 0\n",
     "line 566: forged counter never increments (forge path)"),
    ("E8-errors-no-op",
     "        counts[\"refused\"] += 1\n",
     "        counts[\"refused\"] += 0\n",
     "line 548: unknown-ledger-id tally no-op"),
]
# E6 old spans two source lines; line 550-551 in the file are:
# 550:    print(f"SUMMARY items=...
# 551:          f"refused=...
L550 = '    print(f"SUMMARY items={len(pop)} resolved={counts[\'resolved\']} unresolved={counts[\'unresolved\']} "\n'
L551 = '          f"refused={counts[\'refused\']} mismatched={counts[\'mismatched\']} errors={counts[\'errors\']}")\n'
EDITS[5] = ("E6-summary-text", L550 + L551,
            L550 + '          f"refused={counts[\'refused\']} mismatched={counts[\'mismatched\']} errors={counts[\'errors\']} EXTRA=1")\n',
            "line 550-551: SUMMARY gains a field (output-only mutation)")

results = []
for mid, old, new, desc in EDITS:
    msrc = apply(old, new)
    compile(msrc, mid, "exec")
    cpath = os.path.join(S, f"mut-{mid}.py")
    with open(cpath, "w", encoding="utf-8") as f:
        f.write(msrc)
    rec = {"id": mid, "desc": desc, "old": old, "new": new, "counter_sha": sha(msrc)}
    for popname, pop in (("r92", POP_R92), ("r91", POP_R91)):
        w = os.path.join(S, f"w-{mid}-{popname}")
        shutil.rmtree(w, ignore_errors=True)
        os.makedirs(w)
        p = subprocess.run([sys.executable, "-B", HARNESS, "--counter", cpath, "--lane", LANE,
                            "--fleet-root", "/home/vgpnk/Projects/shokunin", "--work", w,
                            "--population", pop],
                           capture_output=True, text=True, timeout=300)
        out = p.stdout
        ld4r = next((l for l in out.splitlines() if l.startswith("ROW LD4r")), None)
        summ = next((l for l in out.splitlines() if l.startswith("SUMMARY")), None)
        rec[popname] = {"harness_rc": p.returncode, "summary": summ, "ld4r": ld4r}
        with open(os.path.join(SEAT, f"harness-{mid}-{popname}.txt"), "w") as f:
            f.write(out + "\n--stderr--\n" + p.stderr)
        shutil.rmtree(w, ignore_errors=True)
    rec["killed_r92"] = rec["r92"]["harness_rc"] != 0
    print(mid, "r92:", rec["r92"]["harness_rc"], rec["r92"]["summary"],
          "| r91:", rec["r91"]["harness_rc"], rec["r91"]["summary"], flush=True)
    results.append(rec)
    with open(os.path.join(SEAT, "results.json"), "w") as f:
        json.dump(results, f, indent=1)
print("ALL DONE")
