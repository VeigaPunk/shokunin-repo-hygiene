# SwarmScribe27 — round 32 wave 1 — QUALITY Q70-Q72 and matching gate rows (draft)

## Status

STATUS: PASS — both paste-ready blocks are drafted at the delivery path below and every predicate, target and item count in them is read from the frozen r32 contract and its committed red receipts; the three green targets and the `r32-jj-mtime-clock` probe row are drafting targets, not observed runs, and the delivery says so in place. Read-only seat: I wrote two files (this report and the delivery) and nothing else; no scratch directory was needed, so none was created or removed.

## Evidence

Lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`; preregistration `3ec84fc81b3243429c834a051880b0bcde06291c`; controls/amendment `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1` (`git rev-parse HEAD`). `git status --short` prints only `?? census/round-32/measure.sh` (another seat's, untouched).

Frozen inputs are byte-identical at `3ec84fc` and at HEAD (`git rev-parse <rev>:<path>` compared for `census/round-32/c1-counter.py`, `c2-counter.py`, `c3-counter.py`, `c3-contract.txt`, `m1-r31-contract.txt`, `c1-items.tsv`, `c2-items.tsv`, `tools/souji-record-contract.py`: all `same`). All reads below are therefore the frozen bytes.

Frozen contract read in full: `census/round-32/records/preregistration.txt` (lines 1-32, including the raw long lines 3-6), which fixes C1 `unbound=0 mismatches=0 withdrawn<=8`, C2 `fail=0`, C3 `legs=14 fail=0 f1_entries=5`, and M1.

Enumeration sizes, from the committed TSVs:

```
awk -F'\t' '$1 ~ /^T[0-9]+$/' census/round-32/c2-items.tsv | wc -l   -> 27
awk -F'\t' '$1 ~ /^N[0-9]+$/ || $1=="L29"' census/round-32/c1-items.tsv | wc -l -> 44
```

Counter and tool predicates, read at those exact lines:

- `census/round-32/c1-counter.py:62` `WITHDRAW_MAX = 8`; `:341` `ok = counts["mm"] == 0 and counts["unbound"] == 0 and counts["withdrawn"] <= WITHDRAW_MAX`; `:186-187` fixes the append-only tail and `:190` scans rows only inside it; `:268` withdrawn needs `len(target.split()) >= 8`.
- `census/round-32/c2-counter.py:154-155` the sandbox argv `bwrap --dev-bind / / --ro-bind <empty> /tmp --ro-bind <empty> /var/tmp --ro-bind <empty> /dev/shm`; `:58-64` normalisation (`<TMP>`, `<HEX>`, `<DUR>`) and `:67-72` last digit-bearing line; `:174-175` the two clauses (`rc1 == rc0 and s1 == s0 and s0 != "NONE"`; `w1 * 2 >= w0`).
- `census/round-32/c3-counter.py:83-104` `contract_bad` and `:271-274` L14 (`c_list == c_rev`, i.e. the contract unchanged between `--list-rev` and `--rev`).
- `tools/souji-record-contract.py:56` the wildcard test `v in allowed or ("*" in allowed and v) or ("#" in allowed and v.isdigit())`; `:78` `return 0 if n >= 1 and not bad else 1`.

Committed red receipts read this run (not re-executed):

```
census/round-32/records/controls.tsv
  C1-do-nothing  SUMMARY items=44 ... unbound=44 mismatches=44 rev=3ec84fc...
  C1-junk1(withdraw all)  ... withdrawn=44 unbound=0 mismatches=0
  C1-junk2(mechanical record binder, 43 rows)  ... bound_record=39 unbound=1 mismatches=5
  C2-do-nothing  SUMMARY items=27 pass=1 fail=26 rev=3ec84fc...
  C2-junk(stub selftests printing the anchor, T01+T05)  SUMMARY items=2 pass=0 fail=2 partial=1
  C3-do-nothing  SUMMARY legs=14 fail=13 f1_entries=4
  C3-junk(sourceless entry + typed record + cat fixture)  SUMMARY legs=14 fail=6 f1_entries=5
census/round-32/records/controls-a0.tsv
  C1-junk2 ... bound_record=5 ... mismatches=39
  C1-junk3(cited-record mechanical binder, 22 rows) ... bound_record=13 ... mismatches=31
census/round-32/records/m1-red-before.txt
  BAD 16..19 arm=reflog-only ... lines=17 bad=4 / exit=1
```

Routed-defect anchors used in the motivating-evidence cells, read raw: `corpus/lessons/round-31-verifier-spotcheck.md:31` (the disclosed D1), `:128` (defect 1, L29), `:133` (defect 3, D1 recurrence guard), `:135-137` (defect 5, the C1 enumeration gap and file-granular record rule), `:145` (`/var/tmp` snapshots, prompt §7 item 4). Layout source for the rows: `corpus/QUALITY.md:163-169:raw` (Round 31 header `| id | criterion | applies to | check | motivating evidence |`); registry layout: `SKILL.md:180-236`.

Not run, and not claimed: any of the three counters at a landing revision (none exists at HEAD), and the r32 fixture `tests/fixtures/r32-jj-mtime-clock.sh` (not committed at HEAD). No tool install or upgrade was needed, so none was performed.

## Findings

1. **C3's L14 and the M1 tool disagree on two contract tokens.** `census/round-32/c3-counter.py:102` tests only `v not in allowed`, while `tools/souji-record-contract.py:56` also honours `*` (any non-empty) and `#` (any non-negative integer). A contract that used either token would pass the tool and fail L14. No effect on `census/round-32/c3-contract.txt`, which uses neither; this makes L14 stricter, not looser, and therefore is not an ATTACK — it is stated as a limit in the Q72 row's criterion.
2. **None of the three r32 counters refuses a `--scratch` that resolves inside the lane or the fleet root**, which Q66's clause requires. `census/round-32/c2-counter.py:110-112` refuses only `/tmp`, `/var/tmp` and `/dev/shm`; `census/round-32/c1-counter.py` and `c3-counter.py` validate `--scratch` not at all (they mkdtemp under the caller's value at `c1:208-209`, `c3:139-140`). The frozen C2 item set covers r20-r31 files only, so no target is affected; this is a residual for the r32 instruments, routed without an amendment proposal.
3. **The binding row's reason cell is enforced only for its word count** (`census/round-32/c1-counter.py:268`), so "the reason names the cell occurrence it measures" is a prose duty, not a mechanical one. The Q70 row states this in the criterion rather than implying the counter checks it.
4. **The withdrawal cap is load-bearing.** The cheapest-skip arm `C1-junk1` reaches `unbound=0 mismatches=0` with `withdrawn=44` (`census/round-32/records/controls.tsv`), and only the `withdrawn <= 8` clause at `c1-counter.py:341` refuses it. The Q70 row therefore keeps the cap inside the printed target rather than treating it as a secondary note.
5. **No round-32 lesson exists yet**, so the Q70-Q72 motivating-evidence cells cite the r31 closure spot-check and the r32 frozen records (`corpus/lessons/round-31-verifier-spotcheck.md`, `census/round-32/records/amendments.txt`). Re-pointing those cells at a later `corpus/lessons/round-32.md` is an evidence-cell edit and must not touch a predicate or target.
6. **The `r32-jj-mtime-clock` probe row is drafted ahead of its fixture**: `tests/fixtures/r32-jj-mtime-clock.sh` is absent at HEAD, so its verdict map is the C3 counter's L8/L9/L12/L13 contract, and the row says "no run of it is claimed here". It must be re-read against the landed fixture before integration.
7. **Both drafted blocks avoid a literal pipe inside every cell** (checked by counting separators: 6 per QUALITY row, 9 per registry row), so the rows paste into the existing tables without breaking them; `arm=<solo\|descendant>`-style spellings are paraphrased instead of quoted.

## Deliveries

- `.ufo/waves/round-32/w1/deliver-quality-q70-q72.md` — `## Round 32 criteria` (Q70, Q71, Q72 in the Round 31 layout) and five `## Gate registry` rows (`r32-c1-counter`, `r32-c2-counter`, `r32-c3-counter`, `r32-jj-mtime-clock`, `souji-record-contract`), paste-ready for the L1.
