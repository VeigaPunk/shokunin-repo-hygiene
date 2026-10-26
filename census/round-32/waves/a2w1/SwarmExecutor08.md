# SwarmExecutor08 — r32 a2w1: C2 re-measure at its landing commit + T18 from bytes

Scratch `/fast/scratch/hyaku/souji-r32/RemeasureC2/` (clones `base`, `rev`, `mini`; all `--no-local`, `origin` removed, `rev-parse --show-toplevel` printed the clone path before any commit; `TMPDIR` under the same scratch). Read-only on the lane: no git/jj mutation, no files written in the lane except this report.

## Status

STATUS: PARTIAL — C2 at its landing commit `98e5203d45b4e419a9e72801733d93303acc7ebd` re-measures **25/27 PASS, T12 and T18 FAIL** in two independent full runs (the L1 amendment's reading was 26/27). T18 is explained from bytes: the anchor moved 26 → 31 because five C2-repaired files that the T18 fixture compares are in its measured closure; **no honest repair of the enumerated set can hold `baseline_mismatches=26`**, so C2's frozen `fail=0` was unsatisfiable at landing. T12's FAIL is instrument-induced (strace wrapper vs a 6000 ms bound) and flips between runs.

## Evidence

Counter (frozen v1, full set, no `--only`), revision `98e5203d45b4e419a9e72801733d93303acc7ebd`, base `85b61a151923986e7e6b48f7084b9122561b5f3d`, list-rev `3ec84fc81b3243429c834a051880b0bcde06291c`, second (quiet) run:

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 98e5203d45b4e419a9e72801733d93303acc7ebd --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --scratch /fast/scratch/hyaku/souji-r32/RemeasureC2/cnt2
```

```
ITEM	T01	PASS	base=rc0:W8306:SELFTEST pass=65 fail=0	sbox=rc0:W8312:SELFTEST pass=65 fail=0
ITEM	T02	PASS	base=rc0:W25:SUMMARY findings=0 checked_reg=65 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=18 status_lines=75 carry_heading=1 checked_reports=114	sbox=rc0:W26:SUMMARY findings=0 checked_reg=65 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=18 status_lines=75 carry_heading=1 checked_reports=114
ITEM	T03	PASS	base=rc1:W0:assertions=252 resolved=229 skipped=401 mismatches=23	sbox=rc1:W0:assertions=252 resolved=229 skipped=401 mismatches=23
ITEM	T04	PASS	base=rc0:W87:selftest=8/8	sbox=rc0:W88:selftest=8/8
ITEM	T05	PASS	base=rc0:W20:selftest=9/9	sbox=rc0:W21:selftest=9/9
ITEM	T06	PASS	base=rc0:W110:SUMMARY total=11 failed=0	sbox=rc0:W111:SUMMARY total=11 failed=0
ITEM	T07	PASS	base=rc0:W275:selftest: 36/36 passed	sbox=rc0:W276:selftest: 36/36 passed
ITEM	T08	PASS	base=rc0:W302:selftest: 48/48 passed	sbox=rc0:W303:selftest: 48/48 passed
ITEM	T09	PASS	base=rc0:W364:selftest: 47/47 passed	sbox=rc0:W365:selftest: 47/47 passed
ITEM	T10	PASS	base=rc0:W60:SELFTEST pass=118 fail=0	sbox=rc0:W61:SELFTEST pass=118 fail=0
ITEM	T11	PASS	base=rc0:W537:selftest=PASS ids=7/7	sbox=rc0:W544:selftest=PASS ids=7/7
ITEM	T12	FAIL	base=rc1:W4836:FAIL parent SIGTERM cleanup rc=-1 launcher=0 census= git= watchdog= tmp=	sbox=rc1:W5946:selftest: 69 checks, 2 failed	regress
ITEM	T15	PASS	base=rc0:W2544:selftest: 49 checks, 0 failed	sbox=rc0:W2542:selftest: 49 checks, 0 failed
ITEM	T16	PASS	base=rc0:W483:selftest=8/8	sbox=rc0:W488:selftest=8/8
ITEM	T17	PASS	base=rc0:W345:SUMMARY total=66 pass=66 fail=0 base_discriminating=0	sbox=rc0:W350:SUMMARY total=66 pass=66 fail=0 base_discriminating=0
ITEM	T18	FAIL	base=rc0:W4234:SUMMARY total=52 pass=52 fail=0 blocked=0 inventory=exact baseline_mismatches=26	sbox=rc0:W4220:SUMMARY total=52 pass=52 fail=0 blocked=0 inventory=exact baseline_mismatches=31	regress
ITEM	T19	PASS	base=rc0:W154:cases=8 pass=8 refusals=2/2 regress=5/5	sbox=rc0:W157:cases=8 pass=8 refusals=2/2 regress=5/5
ITEM	T20	PASS	base=rc0:W2436:selftest=15/15	sbox=rc0:W2437:selftest=15/15
ITEM	T21	PASS	base=rc0:W649:cases=9 pass=9 control=FALSE-GREEN-REJECTED	sbox=rc0:W650:cases=9 pass=9 control=FALSE-GREEN-REJECTED
ITEM	T22	PASS	base=rc0:W1372:cases=16 pass=16 control=FALSE-GREEN-REJECTED	sbox=rc0:W1373:cases=16 pass=16 control=FALSE-GREEN-REJECTED
ITEM	T23	PASS	base=rc0:W1218:cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED	sbox=rc0:W1217:cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED
ITEM	T24	PASS	base=rc0:W3:cases=1 pass=1	sbox=rc0:W4:cases=1 pass=1
ITEM	T25	PASS	base=rc0:W27:cases=12 pass=12 control=FALSE-GREEN-REJECTED	sbox=rc0:W28:cases=12 pass=12 control=FALSE-GREEN-REJECTED
ITEM	T26	PASS	base=rc0:W536:cases=4 pass=4 control=FALSE-GREEN-REJECTED	sbox=rc0:W535:cases=4 pass=4 control=FALSE-GREEN-REJECTED
ITEM	T27	PASS	base=rc0:W737:cases=15 pass=15 control=TAMPER-REJECTED	sbox=rc0:W737:cases=15 pass=15 control=TAMPER-REJECTED
ITEM	T29	PASS	base=rc0:W689:cases=7 pass=7 control=FALSE-GREEN-REJECTED	sbox=rc0:W697:cases=7 pass=7 control=FALSE-GREEN-REJECTED
ITEM	T30	PASS	base=rc0:W875:cases=10 pass=10 control=FALSE-GREEN-REJECTED	sbox=rc0:W885:cases=10 pass=10 control=FALSE-GREEN-REJECTED
SUMMARY items=27 pass=25 fail=2 rev=98e5203d45b4e419a9e72801733d93303acc7ebd
```

First full run (same argv, `--scratch .../cnt`, overlapping my other work) — same verdict, T12 flipped sides:

```
ITEM	T12	FAIL	base=rc0:W5323:selftest: 69 checks, 0 failed	sbox=rc1:W5952:selftest: 69 checks, 2 failed	regress
ITEM	T18	FAIL	base=rc0:W4231:SUMMARY total=52 pass=52 fail=0 blocked=0 inventory=exact baseline_mismatches=26	sbox=rc0:W4218:SUMMARY total=52 pass=52 fail=0 blocked=0 inventory=exact baseline_mismatches=31	regress
SUMMARY items=27 pass=25 fail=2 rev=98e5203d45b4e419a9e72801733d93303acc7ebd
```

T18 from bytes — fixture run in a clone at base and a clone at the landing commit (`python3 -B tests/fixtures/r20-input-binding.py --baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812`; base run contained by `bwrap --bind <scratch>/var /var/tmp` so nothing reached the host `/var/tmp`):

```
base 85b61a1…  rc=0  BASELINE_MISMATCH lines=26  SUMMARY	total=52	pass=52	fail=0	blocked=0	inventory=exact	baseline_mismatches=26
rev  98e5203…  rc=0  BASELINE_MISMATCH lines=31  SUMMARY	total=52	pass=52	fail=0	blocked=0	inventory=exact	baseline_mismatches=31
rev  98e5203…  under the counter's sandbox (ro /tmp,/var/tmp,/dev/shm) + TMPDIR scratch: rc=0, pass=52, baseline_mismatches=31
tip  4e56c48…  under the same sandbox: rc=0, pass=52, baseline_mismatches=32
C3 landing a92e1aa…: 32 | C1 landing 9e8982b…: 32
```

Path-set delta (`comm` on the `BASELINE_MISMATCH` path column, base vs 98e5203): 0 removed, 5 added —

```
tools/souji-census.sh
tools/souji-cert-evidence.py
tools/souji-evidence-cache.py
tools/souji-repo-structure.sh
tools/souji-round9-selftest.sh
```

Each of the five is changed by `98e5203` and by no other commit in `85b61a1..98e5203` (`git log --oneline 85b61a1..98e5203 -- <path>` returns one line each). `tools/souji-rev-pin.py` was also repaired at `98e5203` but is already one of the 26 base mismatches, so it added nothing: 26 + 5 = 31.

Minimal-repair experiment in a clone at base (`mini`), each step one sandboxed run of the same argv: apply only the T18 hunk (22 added lines at `tests/fixtures/r20-input-binding.py`) → rc=0, `pass=52`, `baseline_mismatches=26`; add only the T07 hunk (`tools/souji-cert-evidence.py`) → rc=0, `pass=52`, `baseline_mismatches=27` (single added path `tools/souji-cert-evidence.py`); add the T08, T11-probe and T12 hunks (`tools/souji-evidence-cache.py`, `tools/souji-repo-structure.sh`, `tools/souji-census.sh`) → rc=0, `pass=52`, `baseline_mismatches=30` (added paths exactly those four). The fifth path (`tools/souji-round9-selftest.sh`) is what takes the landing commit to 31.

T12 cause: isolated sandbox runs without the tracer, three consecutive, all `selftest: 69 checks, 0 failed`, `watchdog wall time` 4030/3970/3858 ms; the same command under the counter's `strace -f -e trace=mkdir,mkdirat,creat,open,openat,openat2` wrapper → `selftest: 69 checks, 1 failed` with `FAIL watchdog wall time 6025ms (want < 6000ms)`.

Location of the count: `tests/fixtures/r20-input-binding.py:1137-1165` (`compare_baseline`), `:89` prints `BASELINE_MISMATCH`, `:105-108` prints the `SUMMARY … baseline_mismatches=` field; the counter's predicate compares that whole line (`census/round-32/c2-counter.py`, `ok_a`). Item row: `census/round-32/c2-items.tsv` T18.

## Findings

1. **T18 fails at its landing commit on one field, not on behaviour.** `98e5203` prints `pass=52 fail=0` inside the sandbox (rc 0, W 4220 ≥ 4234/2), i.e. every case passes and the work-not-dropped test holds; the only disagreement with the base anchor is `baseline_mismatches=26` vs `=31`. Loc: `census/round-32/c2-items.tsv` T18; `tests/fixtures/r20-input-binding.py:1137-1165`, `:89`, `:105-108`.

2. **The five paths that moved the count are all C2 repairs, and four of them are the enumerated items' own files.** `tools/souji-cert-evidence.py` (T07 `files`), `tools/souji-evidence-cache.py` (T08), `tools/souji-repo-structure.sh` (T11, reached through `--probe`), `tools/souji-census.sh` (T12); `tools/souji-round9-selftest.sh` is outside the enumerated set but sits in the fixture's measured closure. All five are compared byte-for-byte by `compare_baseline` and all five matched the pinned `12516f7d…` blob at base, so each honest repair costs exactly +1. Loc: `census/round-32/c2-items.tsv`; `tests/fixtures/r20-input-binding.py:1137-1160`.

3. **No honest repair holds `baseline_mismatches=26`.** Measured: T18's own repair alone is count-neutral (26, pass=52 under the sandbox), one honest repair of one enumerated closure item (T07) moves it to 27, the four enumerated items' repairs together move it to 30, and `98e5203` lands at 31 with the out-of-set fifth. The only subtraction available is making a currently-mismatching closure file equal to its `12516f7d…` blob again — i.e. reverting `LOG.md`, `corpus/SOURCES.md`, 17 `corpus/knowledge/*` entries, `census/round-13/run-verification.py`, `census/round-14/{run-verification,run-targeted,cache-demonstration}.py`, `tests/fixtures/r13-repo-structure.sh` or `tools/souji-rev-pin.py` — or shrinking a pinned `MEASURED_PATHS` list (`census/round-13/run-verification.py:92`, `census/round-14/run-verification.py:32`, `census/round-14/cache-demonstration.py:80`). Both destroy other claims; neither is a scratch-discipline repair. So T18 and T07/T08/T11/T12 are mutually exclusive at any commit, and C2's frozen `fail=0` was unsatisfiable at landing. Answer to the question as posed: **no**.

4. **T12's verdict is not reproducible and is instrument-induced.** Two full counter runs give T12 FAIL on different sides (base `69 checks, 0 failed` in one, base `FAIL parent SIGTERM cleanup` in the other; sandbox `69 checks, 2 failed` in both); four isolated sandbox runs without the tracer pass 69/0 with the watchdog at 3.9–4.0 s, and the tracer alone produces `FAIL watchdog wall time 6025ms (want < 6000ms)`. Loc: `tools/souji-census.sh` `run_selftest` wall-time bound (6 000 ms); `census/round-32/c2-counter.py` (`strace -f` wraps both runs, the sandboxed one carrying an extra bwrap).

5. **The after-record's tip figure is one low.** `census/round-32/records/amendments.txt` A1/residual paragraph says `26 -> 31 at the integration commit`; measured, 31 is the C2 landing commit only (`98e5203`), and every commit that contains C3's entry reads 32 (`a92e1aa` 32, `9e8982b` 32, tip `4e56c48` 32 — the added path being `corpus/knowledge/jj-abandoned-object-mtime-clock.md`). No commit I measured with C3 landed yields 31.

6. No-harm by this seat: read-only on the lane, no axis touched; the C2 landing commit's functional behaviour is strictly better than the wave-1 best reading (`pass=52 fail=0` in the sandbox vs `pass=48 fail=4`).

## Attack log

A1 — **T18's anchor is a tree-drift counter, so the item is self-defeating for the claim it belongs to.** Reproduced at `98e5203`: base anchor `SUMMARY … baseline_mismatches=26`, sandbox at REV `…=31`, delta exactly the five closure files repaired by `98e5203` (four of them the `files` of T07/T08/T11/T12, one out-of-set). Minimal reproduction: base + T18 hunk only → 26 (`pass=52`); base + T18 hunk + T07 hunk → 27. Impacted axis: operability (C2's `fail=0`). No post-data change is proposed; the reproduced state is the report.

A2 — **T12's verdict is load/tracer dependent, so the counter's fail count is not an invariant.** Two full runs of the frozen counter at the same revision give `pass=25 fail=2` both times but with T12 failing on different sides; isolated sandbox runs pass 69/0; the tracer alone trips `FAIL watchdog wall time 6025ms (want < 6000ms)`. The L1 amendment's `26 of 27 PASS` is a third reading not reproduced here (this host, 2 full runs). Impacted axis: operability (the reading's stability, not the bytes).

A3 — **The after-record's `26 -> 31` is not the tip value.** Measured 31 at `98e5203`, 32 at `a92e1aa`, `9e8982b` and the tip `4e56c48`. Impacted axis: calibration of the lane's own records (disclosure accuracy), not a predicate.

## Deliveries

- `.ufo/waves/round-32/a2w1/SwarmExecutor08.md` (this report). No delivery files; no tool installs or upgrades were needed.
