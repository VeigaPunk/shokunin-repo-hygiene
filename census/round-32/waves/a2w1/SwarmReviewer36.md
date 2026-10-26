# SwarmReviewer36 — verify the five attempt-1 salvage records (4e56c48b)

## Status

STATUS: PASS — all five salvage records verified: counters frozen, header revs correct, and every record I was assigned to re-execute reproduces byte-for-byte (mod the `$ ...` header line); c2-after-v1 structurally consistent.

Lane tip during verification: master = 4e56c48b8fc828f9aba2746e324dc46aa538bdbf (the salvage commit itself is the tip; confirmed ancestor of master).

## Evidence

Freeze checks (all `git -C /home/vgpnk/Projects/shokunin/souji-shokunin`):

- `log --format='%H %s' -- census/round-32/<counter>`: c1-counter.py, c2-counter.py, c3-counter.py each last touched at 3ec84fc81b3243429c834a051880b0bcde06291c (prereg); c1-counter-v2.py at 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1 (controls); c3-counter-v2.py at a92e1aae91dbf46c2d7eff713932cfc820186970 (C3+A1 commit). `c2-counter-v2.py` does not exist at master (`ls-tree master census/round-32/` lists exactly five counters) and no record claims it.
- `diff 3ec84fc..master -- census/round-32/c1-counter.py census/round-32/c2-counter.py census/round-32/c3-counter.py` → empty, rc=0. Same empty result for `7a6667cd..master -- c1-counter-v2.py c2-counter-v2.py` and `a92e1aae..master -- c3-counter-v2.py`.
- `show --stat 4e56c48b`: exactly the five record files, 156 insertions, nothing else — the salvage commit itself touches no counter.

Re-executions (`--root /home/vgpnk/Projects/shokunin/souji-shokunin`, `--base 85b61a15...`, `--list-rev 3ec84fc...`, `--scratch /fast/scratch/hyaku/souji-r32/VerifySalvage/<n>`, `python3 -B`):

- c1-after-v1.txt — header `$ ... --rev 9e8982b7a6ac57dffa415f9db43cf7cd6e829c93 ... c1-counter.py`; rerun `diff` vs record: only `1d0` (the header line). All 44 ITEM + SUMMARY `items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6 rev=9e8982b7...` byte-identical. rc=1 (counter signals target miss, as the record's content states).
- c1-after-v2.txt — same header rev, `c1-counter-v2.py`; rerun diff: only `1d0` (header). Byte-identical, same SUMMARY.
- c3-after-v1.txt — header `--rev a92e1aae... c3-counter.py`; rerun rc=0, diff: only `1d0` (header). All 14 legs + `SUMMARY legs=14 fail=0 f1_entries=5 rev=a92e1aae...` byte-identical.
- c3-after-v2.txt — header `--rev a92e1aae... c3-counter-v2.py`; first rerun (executed concurrently with the v1 rerun) differed at L12: record `git_calls=366` vs rerun `git_calls=369`. Serial rerun (scratch `VerifySalvage/5`): rc=0, diff vs record: only `1d0` (header), `git_calls=366` reproduced, all 17 legs + SUMMARY byte-identical.
- c2-after-v1.txt — per assignment, re-execution not attempted (RemeasureC2 re-runs it). Checked instead: header rev = 98e5203d45b4e419a9e72801733d93303acc7ebd ✓; `awk -F'\t' '$1=="ITEM"{...}'` → `items=27 pass=26 fail=1`, agreeing with `SUMMARY items=27 pass=26 fail=1 rev=98e5203d...`; the single FAIL is T18 (`baseline_mismatches` base 26 vs sbox 31, tagged `regress`), matching the amendment's "26/27 -> MISSED on T18".

Cross-check against census/round-32/records/amendments.txt readings: C1 unbound=6 withdrawn=17 (v1 and v2) → MISSED ✓; C2 26/27 → MISSED ✓; C3 v1 and v2 met at a92e1aae ✓.

## Findings

1. `census/round-32/c3-counter-v2.py:53` — L12's informational call counts are contention-sensitive under concurrent counter execution. Quote (line 53): "run once more with PATH led by a shim dir whose `jj`, `git` and `touch` log their argv". Running the v1 and v2 counters simultaneously perturbed the shim-logged `git` count once (366 → 369, one observation at `--rev a92e1aae...`); a serial rerun reproduces the record's 366 exactly. The leg verdict `ok12` (line 316: `src == 0 and bool(rl) and slines == rl and all(need.values())`) does not read the counts, so no contract field moves — but two C3 counters must never be run in parallel when their outputs are compared byte-for-byte.
2. `census/round-32/records/c1-after-v1.txt:47` and `c1-after-v2.txt:47` — SUMMARY prints `mismatches=6` while every ITEM line shows only MATCH/WITHDRAWN/UNBOUND; the mismatches are the counter's own derivation over the (still unbound) r31 rows, not per-item MISMATCH lines. Cosmetic opacity, not an inconsistency: rerun reproduces both records byte-for-byte, and `unbound=6 mismatches=6` is what the frozen counter prints.
3. No gaming found: counter blobs are frozen at their stated freeze commits with empty diffs to master, and no salvage-record line depends on anything the salvage commit introduced.

## Attack log

Item is a verification attack on attempt-1's salvaged after-records; re-derivation was the attack. Tried: (a) counter post-freeze tampering — none (empty freeze diffs); (b) header-rev laundering — all five header revs are the true landing commits of their claims (9e8982b7 C1 rows, 98e5203d C2, a92e1aae C3+A1); (c) reproduction — 4/4 assigned counters re-executed; all reproduce byte-for-byte mod the header line; (d) SUMMARY/ITEM agreement in the un-rerun c2 record — holds (27/26/1). One observation recorded as Finding 1; it does not touch any frozen predicate, target or pass condition, so no amendment proposed.

## Deliveries

- `.ufo/waves/round-32/a2w1/SwarmReviewer36.md` (this report)

Scratch `/fast/scratch/hyaku/souji-r32/VerifySalvage/` removed after writing; no lane mutation performed (read-only seat).
