# S72CriticClaims — r72 claim falsification (C1 self-check/base slot, C2 filter-witness rows, WM7)

Seat scope: attack the two frozen claims as claims, re-derive every number from committed bytes,
build neighbouring defects outside the frozen mutant set, judge chronology/separability and the
committed text. No lane file was edited; all runs are read-only over the lane and scratch-only.

## Verdicts

| claim | verdict | exact qualification |
|---|---|---|
| C1(i) calibration (harness score 0) | **QUALIFIED** | Predicate reproduces byte-for-byte, and each of the six Y/Z mutants is killed by a defect-specific check (FAIL lines below). But the harness kill test is only `selftest rc!=0 and fail>=1`; a counter with section 9 deleted and one generic source-digest check scores 0 (`SUMMARY … score=0`, `EXIT=0`, reproduced). Neighbouring defects survive 44/44 (D1, D2, D3). The prereg names the mutant-set limit, not the metric-gaming limit. |
| C1(ii) base-slot binding | **STANDS, qualified** | Reproduced exactly: `base_mismatches=10`, `base_forgeries=2`, `new_*` clean, `EXIT=1`. The predicate `N>0 and EXIT=1` is one-sided: any base-slot disagreement (including a miswired base slot or a base build error, which `evaluate` counts in `base_mismatches`) satisfies it; the receipt's other fields disambiguate this run. Rows with `base_expect=refuse` (44/75) are bound only at the accept/refuse bit, never the refusal class. The metric-probe counter (no section 9) passes C1(ii) with the same numbers, so C1(i)∧C1(ii) does not require the six checks. |
| C2(i) coverage battery | **STANDS** | Reproduced exactly: `kills=5 survived=0 all_match=true EXIT=0`; each mutant accepted exactly one row and each row was accepted by exactly one mutant (FWr→WM3, FWi→WM4, FWp→WM5, FWs→WM6, FWw→WM8). Before control reproduced: `kills=0 survived=5 EXIT=1`. |
| C2(ii) honest writer | **STANDS** | Reproduced exactly: `new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS EXIT=0`; `new_honest=19` = the 19 accept rows of the matrix. |
| axis labels | **STANDS** | C1 = calibration and C2 = coverage are the labels the r70/r71 and r69 closure rulings already accepted for the same shapes (r70 lesson: same-round mutants accepted as calibration, qualified; r71 lesson: "specific to this mutant set"; r69 C3: declared writer protections with a battery row = coverage). C2 names its surface and its before-arm, as the prompt rule requires. |
| chronology / separability | **STANDS** | Counter, matrix and `mk-counter.py` absent at the freeze (`git cat-file -e 23372f36:census/round-72/c1-counter.py` → exit 128); mutants/battery/probe/controls present. Candidate is byte-reproducible from `mk-counter.py` (diff identical). Probe 17:35:27 < freeze 17:46:24 < candidate 17:49:06 < after-arms 17:59:21. Probe peek is declared in the prereg and measured writers, not the counter. |
| WM7 reachability | **named limit STANDS** | Eight shapes probed; `git check-attr` returned rc 0 in all. `GIT_ATTR_SOURCE="<id> "` (trailing space) does fail rc 128, but the writer scrubs `GIT_ATTR_SOURCE`, so the route is closed by the scrub. |

## Evidence (commands and observed lines)

All runs from `/home/vgpnk/Projects/shokunin/souji-shokunin`; scratch
`/fast/scratch/hyaku/souji-r72/S72CriticClaims` (removed before yield). Base rev
`8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0`.

- **C1(i) candidate harness** — `python3 -B census/round-71/c2-harness.py --label c1-after-r72 --counter census/round-72/c1-counter.py --matrix census/round-72/c1-matrix.tsv --root . --base-rev 8b9345b1… --mutants census/round-72/c1-mutants.json --work <S>/h`:
  `SUMMARY label=c1-after-r72 positive_selftest=PASS x_mutants=11 x_killed=11 x_survived=0 cm_mutants=4 cm_killed=4 cm_survived=0 score=0` / `EXIT=0` (byte-identical to `records/c1-after.txt`).
- **C1(i) before control** — same harness, `--label c1-before-r71 --counter census/round-71/c1-counter.py --matrix census/round-71/c1-matrix.tsv`:
  `SUMMARY label=c1-before-r71 positive_selftest=PASS x_mutants=11 x_killed=5 x_survived=6 cm_mutants=4 cm_killed=4 cm_survived=0 score=6` / `EXIT=1`; survivors Y1 Y4 Y6 Y9 Y10 Z1, exactly the control (a) set.
- **C1(ii)** — `python3 -B <S>/mut/Y6.py --root . --matrix census/round-72/c1-matrix.tsv --base-rev 8b9345b1… --rev 0bf098dde7e6eafb62a9ce62b7c16a6291ee1e8e --tool tools/souji-receipt-write.py --work <S>/mainY6b`:
  `SUMMARY matrix=75 base_forgeries=2 base_honest=19 base_mismatches=10 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS`
  `EXIT=1` (byte-identical to `records/c1-Y6-main-arm.txt`). Y6 file sha256 `45f3afdb…c1b846` = the committed variant.
- **C2(i)** — `python3 -B census/round-72/c1-counter.py --root . --matrix census/round-72/c1-matrix.tsv --base-rev 8b9345b1… --work <S>/bat --battery-manifest census/round-72/battery-manifest.tsv --battery-dir census/round-72/battery`:
  `BATTERY mutants=5 kills=5 label_only=0 over_refusal=0 echo_violation=0 survived=0 error=0 all_match=true` / `EXIT=0`; each `MUTANT WMn outcome=forgery … forgeries=1 … base_mismatches=0`.
- **C2(i) before** — same with `census/round-71/c1-counter.py` and `census/round-71/c1-matrix.tsv`:
  `BATTERY mutants=5 kills=0 … survived=5 … all_match=false` / `EXIT=1`; 350 CASE lines, every mutant `forgeries=0`.
- **C2(ii)** — `python3 -B census/round-72/c1-counter.py --root . --matrix … --base-rev 8b9345b1… --rev 0bf098dd… --tool tools/souji-receipt-write.py --work <S>/main`:
  `SUMMARY matrix=75 base_forgeries=12 base_honest=19 base_mismatches=0 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` / `EXIT=0`.
- **Baseline selftest** — `python3 -B census/round-72/c1-counter.py --selftest …`: `SELFTEST cases=44 pass=44 fail=0` / `EXIT=0`.
- **Killing check per mutant** — each mutant selftest, `grep '^selftest FAIL'`:
  - Y1: `member binding: a member name with a path separator is refused as not plain | member sub/M1.py is not listed in SHA256SUMS`
  - Y4: `base witness … | rows=7 mismatches=['AS1:refuse!=accept', 'AS2:refuse!=accept']`
  - Y6: `base witness … | rows=7 mismatches=['AS1:refuse!=accept','AS2:refuse!=accept','FC1:refuse!=accept','FC2:refuse!=accept','FC3:refuse!=accept']`
  - Y9: `member binding: a SHA256SUMS line naming a dot-file is refused as non-plain`
  - Y10: `base witness … | rows=7 mismatches=[AS1, AS2, FC1, FC2, FC3]`
  - Z1: `clean_env: every scrub-tuple name is removed from the ambient environment | kept=['GIT_DIR']`
- **Neighbouring defects (not in the frozen set), selftest rc**:
  - D1 `clean_env` GIT_TRACE prefix → exact two names: `SELFTEST cases=44 pass=44 fail=0` / `EXIT=0`; `GIT_TRACE2_PERF` survives in `clean_env()` (probe: present `'/nonexistent-r72-trace2perf'`).
  - D2 remove `e["GIT_CONFIG_GLOBAL"]=os.devnull` and `e["GIT_CONFIG_NOSYSTEM"]="1"`: `44/44` / `EXIT=0`. (Latent: with HOME/XDG scrubbed and no `/etc/gitconfig` on this host, no observable effect here; a host with a system config would be steered.)
  - D3 `WITNESS_ROWS=("FM1",)`: `44/44` / `EXIT=0`; `selftest ok: base witness … | rows=1 mismatches=[]`.
  - D3+Y6 (witness narrowed + the frozen Y6 edit): `44/44` / `EXIT=0` — **Y6 survives the selftest** when the witness population is narrowed.
  - V1 `verify_members` symlink check resolved away: `44/43 fail=1` — caught by 8e. V2 AS env `GIT_ATTR_SOURCE` + "0": `44/44` but inert (git truncates a 41-char id; 40/41/39-char ids all resolve, only a trailing space fails rc 128).
- **Metric probe (P-selfdigest)** — candidate with section 9 deleted and one generic check
  `sha256(file minus '# SELFDIGEST ' line) == digest`: selftest `SELFTEST cases=40 pass=40 fail=0`;
  harness `SUMMARY label=c1-metric-probe positive_selftest=PASS x_mutants=11 x_killed=11
  x_survived=0 cm_mutants=4 cm_killed=4 cm_survived=0 score=0` / `EXIT=0`. The same counter with
  the Y6 edit on the main arm prints `base_forgeries=2 base_honest=19 base_mismatches=10
  new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` / `EXIT=1` —
  i.e. it satisfies both C1 predicates while its selftest contains none of the six defect checks.
- **Chronology** — `git cat-file -e 23372f36:census/round-72/{c1-counter.py,c1-matrix.tsv,mk-counter.py}` → exit 128 each; `c1-mutants.json`, `battery-manifest.tsv`, `probes/fw-shapes-probe.txt`, `controls/c1-before-r71.txt` present at the freeze. `python3 -B <patched mk-counter.py>` → `diff` against the committed counter and matrix: identical (counter sha256 `7578447d…a912`, matrix `cd8490b4…33b8`).
- **Receipt bindings** — `records/c1-after.txt` `counter_sha256=7578447d…`; `c2-after-battery.txt`/`c2-honest-writer.txt` `instrument_sha256=7578447d…`, `matrix-sha256=cd8490b4…`; harness `6c7bf41d…75fb`. All equal the committed bytes.
- **base_expect provenance** — all 70 carried rows equal the r71 receipt's `base=` field (0 diffs); FW rows `accept`; 31 accept-base, 44 refuse-base.
- **WM7 probes** — worktree `.gitattributes` as directory / chmod 000 / dangling symlink; `core.attributesFile` directory; `info/attributes` directory; `GIT_ATTR_SOURCE` naming a blob / a missing object; `attr.tree` valid / missing: `check-attr` rc 0 every time (missing `attr.tree` silently yields `unspecified`). `GIT_ATTR_SOURCE="<id> "` → `fatal: bad --attr-source or GIT_ATTR_SOURCE`, rc 128 — closed by the writer's scrub.

## Findings

- **HIGH (claim meaning).** C1(i)'s frozen predicate is satisfiable without detecting any of the six
  defects: the harness kills a mutant on any selftest failure, and the metric probe (section 9
  removed, one generic source-digest check) scores 0 with `P-SELFTEST PASS` (reproduced:
  `score=0`, `EXIT=0`) and also passes C1(ii) (`base_mismatches=10`, `EXIT=1`). The candidate's own
  kills are defect-specific (FAIL lines above), so the number is true; the inference "the instrument
  detects the six defects" is not what the metric establishes. The prereg's named limits omit this.
- **MEDIUM (self-referential check).** 9a asserts `len(wrows) == len(WITNESS_ROWS)` against the same
  constant it filters by; D3 narrows the population to one chmod row and the selftest stays 44/44,
  and D3+Y6 shows the Y6 kill disappears. The base-witness kill power is a mutable constant no check
  pins.
- **MEDIUM (neighbouring defects).** D1 (GIT_TRACE2_PERF leaks) and D2 (hermeticity pins removed)
  pass 44/44. Both are in `clean_env`, the function the r71 Z1 defect was about; the r72 section 9
  covers the tuple names, not the prefix clauses or the pins.
- **LOW–MEDIUM (C1(ii) predicate).** `base_mismatches>0` also counts a base build error
  (`evaluate` increments it on `CaseError`) and any base-slot disagreement, so the predicate alone
  does not establish the base slot is the declared weak base; the receipt's `base_forgeries=2` vs
  `12` on the honest run is what disambiguates. Refusal classes on the 44 refuse-base rows are never
  bound.
- **LOW (false provenance).** `records/counter-selftest.txt` header says
  `command=… --work <scratch>` — a literal placeholder, and the counter's `--selftest` path returns
  before any receipt code (`census/round-72/c1-counter.py:1852-1853`), so the header was composed,
  not emitted. The numbers are true (44/44 reproduced); the recorded command is not runnable.
- **LOW (text).** No overstatement found in the README frontier, knowledge r72 section or SKILL rows
  for the C2 sentences I checked ("each forges the base writer and exactly one mutant", "0 of 5 →
  5 of 5", "refuses all five with RECEIPT-FILTER-DRIVER-SET", "WM7 not covered"). The knowledge
  size-0 sentence is S72CriticDiscern's MEDIUM; not duplicated here.

## Files written

- `.ufo/waves/round-72/w1/S72CriticClaims.md` (this file)
- `.ufo/waves/round-72/w1/S72CriticClaims/` — `neighbour-defects.txt` (the D1/D2/D3/V1/V2 edit
  recipes and results), `metric-probe.txt` (P-selfdigest construction and harness output),
  `wm7-probes.txt` (the eight check-attr shapes and rc values), `raw-results.txt` (the exact
  SUMMARY/BATTERY/SELFTEST/FAIL lines from every run).
