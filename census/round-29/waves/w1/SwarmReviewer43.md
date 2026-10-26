# SwarmReviewer43 — prereg audit against Q55–Q59 and claim sizing (r29, attempt 1)

## Status

STATUS: PARTIAL — the base literals for all three claims re-derive exactly and the axis
assignment is clean (`claims=3 flags=0`), but 11 findings are actionable before any scoring:
C3's gate literal is not base-derivable and its instrument reads the working tree, C2's target
is reachable by deleting evidence and its fixture growth is not a literal, C1's K2 clears
without content and its K1 used-by arm is substring-only, the control receipt binds neither
sha256 nor reachable junk revs, both SUMMARY shapes are misquoted, the "causally separable"
sentence is contradicted by C3's own target, one universal survives the R4 scan, the
round-start census count is unbound, and C1 binds no SHONEN claim.

## Evidence

Lane HEAD at audit time: `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (prereg commit; `git log --oneline -3` → b8cb4b3, 691dd29, fec846d). Base: `691dd29211c53d0ef94fa072394cb9c8a69fe92e`.

| # | command | output excerpt | rev |
|---|---|---|---|
| E1 | `python3 -B tools/souji-registry-agreement.py --root . --rev 691dd29… --list-rev b8cb4b3…` | `SUMMARY k1=6 k2=4 mismatches=10 rev=691dd29…`, rc 1; items: S215 used-by-no-cite, S075/S076 cited-not-in-used-by, S022/S024/S025 cited-not-in-used-by, `K2 uncorrected` ×4 | base |
| E2 | `python3 -B census/round-29/c2-counter.py --root . --rev 691dd29…` | `r26 records=1382 failed=152 uncovered=14 floor_violation=0`; r27 124/0/0; r28 75/0/0; `SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=…`, rc 1 | base |
| E3 | `git grep -lE '^ground: F3' 691dd29… -- corpus/knowledge/ \| wc -l`; `git show 691dd29…:corpus/SOURCES.md \| grep -cE '^[[:space:]]{0,3}\|…'`; `tools/souji-coverage-agreement.py --rev 691dd29…` | `0`; `139`; `grounded=13 mapped=13 dangling=0 mismatches=0`, rc 0 | base |
| E4 | `python3 -B tools/souji-axis-check.py --prereg census/round-29/records/preregistration.txt --scorecard SCORECARD.md` | `claims=3 flags=0`, rc 0 | HEAD |
| E5 | `git cat-file blob b8cb4b3…:<f> \| sha256sum` for the six files in `census/round-29/records/frozen-digests.txt` | all six equal `frozen-digests.txt` | prereg |
| E6 | `git cat-file -e <rev>^{commit}` for the six junk revs in `controls.tsv` | 6/6 UNREACHABLE | — |
| E7 | `tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries dupe-finders-detect-then-act.md --snapshot-dir census/round-29/sources --slice census/round-29/records/quarantine-slice --slice-verdicts census/round-29/records/slice-verdicts.tsv` | `FAIL slice slice-missing`; `entries=1 ok=0 slice_verdicts=0 slice_total=0 fail=2` (neither round-29 slice file exists at base) | base |
| E8 | `bash tests/fixtures/r28-wave-evidence-capture.sh` | `cases=6 pass=6 control=TAMPER-REJECTED`, rc 0 | HEAD |
| E9 | `tools/souji-declared-evidence.py --root . --rev 691dd29…` | `assertions=164 resolved=145 skipped=223 mismatches=19`, rc 1 | base |
| E10 | SHONEN arm probe: `git show 691dd29…:LOG.md \| sed -n '362p'`; row/claim presence of S100–S103; `git cat-file -e` for the 5 cited paths | all citations resolve at base; LOG.md:362 states the 96-artifact sweep | base |
| E11 | attack probes, scratch clone under `/var/tmp/souji-r29-SwarmReviewer43.*` (removed) | C2 deletion rev `6c4eb39…` → `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0`, rc 0; C1 marker-only rev `377acf0…` → `k1=6 k2=0 mismatches=6`; C1 comment-only S215 rev `49ebcd4…` → `k1=5` | scratch |

No tool install or upgrade was needed; nothing was written outside `census/…/w1/` and `/var/tmp`; no lane git/jj mutation.

## Findings

Each item names the frozen sentence and the judgment.

**F1 — wrong (Q58, claim sizing).** C3, `prereg:9`: "… `--slice census/round-29/records/quarantine-slice --slice-verdicts census/round-29/records/slice-verdicts.tsv` … -> `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`". Neither named file exists at the frozen base, so the frozen command prints `slice-missing` and `slice_verdicts=0 slice_total=0` (E7); the `8` is not derived at 691dd29. The identical tail `slice_verdicts=8 slice_total=8 fail=0` already sits in the round-28 row at `SCORECARD.md:22`, and `8` is exactly gate-check's default pair (`census/round-22/attempt2/{quarantine-slice,slice-verdicts.tsv}`, 8 ids / 8 rows). The junk receipt was produced without those two flags (`census/round-29/controls.sh:80`), so it scored the round-22 defaults, not the declared predicate (`controls.tsv` C3-junk line).

**F2 — wrong (claim sizing: "a target must be one a do-nothing control cannot reach").** C2, `prereg:7`: "After target: at the C2 landing commit `manifests=3 failed=0 uncovered=0 floor_violations=0`, rc 0". Reached with zero capture work at scratch rev `6c4eb39…`: drop the 152 non-verifying manifest lines and delete the 14 uncovered committed files → exact target literal, rc 0 (E11). The floor cannot fire: after the drop r26 holds 1230 records and `census/round-29/c2-counter.py:23` freezes exactly 1230 (`1382 − 152 = 1230`). The prereg's two junk controls ("drop the failing records only -> uncovered 14"; "empty manifests with files deleted -> floor_violations 3") miss the combined path.

**F3 — wrong (Q58 / Q55-shape).** C2, `prereg:7`: "its case count rises from 6". Not a concrete value and not a counter literal; the fixture's own shape is `cases=6 pass=6 control=TAMPER-REJECTED` (E8). No target and no machine-block enumerator names the fixture — the C2 enumerate line covers only "SUMMARY failed uncovered floor_violations" — so the operability surface (the instrument) is measured by nothing while the evidence is. The parenthetical in F2's sentence, "(round 29 captured by the improved tool)", is likewise unobservable by the counter (no tool-bytes/provenance binding).

**F4 — wrong (attack on gameability; Q55 record accuracy).** C1, `prereg:5`: "the same file must carry, after that line, a line starting `R29-CORRECTION ` naming `file:line`". The predicate is presence-only (`tools/souji-registry-agreement.py:96`), so four lines reading `R29-CORRECTION <file>:<line> marker only, no content` give `k2=0` (E11). That clears 4 of the 10 base mismatches — the entire set that corrects the false r26 statements — without writing a corrected fact. The prereg's own junk row admits `k2=0` under markers-only, but the claim text still reads as if `k2=0` means the records agree. Related: the kill rule's "phrase-moved-or-edited" is not a distinct flag — an edited phrase and an uncorrected one both count in `k2`.

**F5 — wrong (Q55).** C1, `prereg:5`: "Before: `k1=6 k2=4 mismatches=10` at base (`census/round-29/records/controls.tsv`)". The receipt binds the revision (`rev=`) but no sha256 of the bytes that produced it; `frozen-digests.txt` binds the sha256 (verified equal, E5) but is not cited, and `controls.tsv` itself carries no `tool_sha256=` line. The six junk rows are worse: their revs are unreachable (6/6, E6) because `controls.sh:81` deletes the scratch clone, so no junk-control count can be re-derived. The three do-nothing rows re-derive fine (E1–E3), so the defect is scoped to the junk rows and the missing digest binding.

**F6 — wrong (Q59 causal separability).** `prereg:13`: "each counter is evaluable at its own landing commit without the others". C3's target contradicts it: "`the C1 counter at the C3 landing commit still mismatches=0`" is C1's counter, so C3 is not evaluable at its own landing commit without C1 already landed; and C1's "again at the final tip" depends on C3's four rows keeping `k1=0`. The parenthetical "(C3's rows are counted by C1 only at the final tip, where used-by must agree)" is also inexact: K1 enumerates every SOURCES row at whatever rev it is run at. Either declare the landing order (C1 → C2 → C3) as part of the claim, or drop the cross-counter clause.

**F7 — wrong (Q58 output shape).** C1 `prereg:5` "prints `SUMMARY k1=<a> k2=<b> mismatches=<a+b>`" and C2 `prereg:7` "`SUMMARY manifests=<m> failed=<f> uncovered=<u> floor_violations=<v>`" both omit the trailing `rev=<40hex>` the tools actually emit (E1, E2). Targets are therefore substring checks, not the counters' own shapes. Separately, the C3 machine block's `enumerate:` is five near-bare commands ("grep grounded F3 entries; grep SOURCES rows; …; sources-census.sh validate") with no revision and no arguments, so the frozen enumerator for C3 is not runnable as frozen; `sources-census.sh` is not on `PATH` (only `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`).

**F8 — wrong (claim sizing: "over committed bytes").** C3, `prereg:9`: "python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25". The gate instrument reads the working tree — `os.path.isfile`/`open(path)` at `tools/souji-gate-check.py:68,70` and `144`–`152` — with no `--rev` arm, so `entries=2 ok=2` is re-derivable over the disk and equals the commit only if the tree is clean (unstated). An uncommitted entry or snapshot can pass the frozen target.

**F9 — minor (Q55).** `prereg:1`: "Census at round start: `census/round-29/records/census-start.txt` (rc 0, 35 W04, 0 errors)". The count is correct (37 lines, `grep -c W04` = 35, `exit=0`) but the receipt binds neither a revision nor a sha256.

**F10 — minor (Q59 instrument scope / universal clauses).** `prereg:9` "— misses every other counter." is a universal over the C3 counter set that the receipt never scores: coverage-agreement and sources-census are absent from the C3-junk row. `prereg:13` "each counter is evaluable at its own landing commit without the others." is false per F6. Both survive `flags=0` because `tools/souji-axis-check.py:19` scopes R4 to the machine block and passes any block that carries an `enumerate:` line, regardless of whether that line enumerates the set.

**F11 — wrong (calibration definition; judged honestly).** `prereg:5`: "Declared self-assessment records must agree with what committed bytes show." K1 (6 of the 10 mismatches) is SOURCES-registry↔entry internal consistency, not self-assessment vs observed state; of the four K2 statements exactly one is in `SCORECARD.md` (line 23) and **SHONEN.md is never named** (0 occurrences in the prereg, both counters and the stale list). So C1 is honest record agreement over two record families, but it is not the SCORECARD/SHONEN mismatch count the sizing rule demands at scale. Caveat for honesty: the lane's existing predicate instrument reports `mismatches=19` at base (E9) but much of that is its own over-read (class-A bare basenames such as `c1-after.tsv`, and a historical tool digest at `SCORECARD.md:68`), so "19" must not be presented as 19 false SCORECARD claims.

**F12 — fine.** Base literals in `prereg:5`, `prereg:7`, `prereg:9`: "Before: `k1=6 k2=4 mismatches=10`", "`manifests=3 failed=152 uncovered=14 floor_violations=0`", "base 139 -> target 143", "base 0 -> target 2", "`grounded=13 mapped=13 dangling=0 mismatches=0`" all re-derive exactly (E1–E3), including the six-item K1 breakdown.

**F13 — fine.** `prereg:13` axis assignment: "C1 changes records (bookkeeping, calibration); C2 changes a runnable instrument and fixture (operability); C3 changes the knowledge registry (coverage)." R2 accepts `bookkeeping-file` → calibration (`tools/souji-axis-check.py` SURFACE_AXIS) and C1 does edit SCORECARD/LOG/lessons under K2; `flags=0`, rc 0 (E4). The axes are distinct; only the separability sentence (F6) is wrong.

**F14 — fine.** Do-nothing reachability for C1 and C3: `prereg:5` "none reach 0" and `prereg:9` "Do-nothing control: 0 entries / 139 rows" hold — no control row reaches C1's 0 or C3's 2/143 (controls.tsv; E1/E3). The C3 junk control does reach the entry literal `2`, so the composite target is what carries the claim, not the entry count alone.

## Attack log

My item is a review, not an attack seat; these are executable attacks plus stricter-only proposals. No frozen predicate, target or case set was changed.

- **A1 (executed) C2 target reachable by evidence deletion.** Method: clone at base, delete the 152 absent records and the 14 uncovered files, commit. Result: exact target literal, rc 0 (rev `6c4eb39…`). The frozen floor is calibrated to the post-deletion count (1230). *Proposal (stricter-only):* add a floor or a "no committed path removed under `census/round-26/waves/`" arm, e.g. compare the r26 waves path set at base and at the measured commit and require base ⊆ measured; or raise no target until the deletion control is scored and committed.
- **A2 (executed) C1 K2 content-blind.** Method: four `R29-CORRECTION <file>:<line> marker only` lines on top of base. Result: `k2=0` (rev `377acf0…`). *Proposal:* require the correction line to carry `absent=<n> escaped=<n>` recomputed by the same counter from the committed r26 manifest (`152`, `2`), so markers alone keep `k2=4`; the frozen target `k2=0` is unchanged.
- **A3 (executed) C1 K1 used-by→file arm is substring-only.** Method: append `<!-- S215 -->` to `corpus/knowledge/git-auto-maintenance-trigger-set.md`. Result: `k1` 6→5 (rev `49ebcd4…`). *Proposal:* require the id in citation form (inside the entry's `source:` front-matter line or a bracketed marker), not anywhere in the blob.
- **A4 (proposed) SCORECARD/SHONEN binding, strictest cheap observable.** C1's frozen target stays `mismatches=0`; add one binding observable that C1's current counter does not cover: for the SCORECARD row this round appends, every `after` literal must be reproduced by the frozen counters at the claim's landing commit, and every `<path>:<line>` citation in that row must resolve at the final tip — `SUMMARY rows=1 literals=<n> mismatches=<m>`, target `m=0`. Its do-nothing control is non-zero (no r29 row exists at base). A SHONEN arm is cheap but **cannot** be a target: I verified all five SHONEN citations and the 96-artifact count resolve at base (E10), so a do-nothing control reaches 0; use it as a regression guard only. The whole-file `tools/souji-declared-evidence.py` arm is the strictest reading (base `mismatches=19`, E9) but needs its class-A bare-basename and historical-digest readings settled first, or it flags SCORECARD history rather than SCORECARD errors.

## Deliveries

- `.ufo/waves/round-29/w1/SwarmReviewer43.md`
