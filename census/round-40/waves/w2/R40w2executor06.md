# R40w2executor06 — every committed fixture at the landed revision

Verdict: **SAFE** on the harm question (no fixture/consumer regressed at 128e412b0ced vs the r39 base 0242085909fb). Four pre-existing reds reproduce byte-for-byte at the r39 base and are therefore not r40 harm (listed in §3). One landed-bytes defect in the C3 counter (§4), already repaired by a later commit.

## 0. Setup (all scratch, no lane writes)
Scratch root `S=/fast/scratch/hyaku/souji-r40/w2/R40w2executor06`.
```
git clone -q --no-hardlinks /home/vgpnk/Projects/shokunin/souji-shokunin $S/lane   && git -C $S/lane checkout -q --detach 128e412b0ced3c243dc27c3dd3332054a611bc2e
git clone -q --no-hardlinks /home/vgpnk/Projects/shokunin/souji-shokunin $S/lane39 && git -C $S/lane39 checkout -q --detach 0242085909fb6a4ee041c5443d76316ac6d59d4b
git -C $S/lane branch -f master 128e412...; git -C $S/lane39 branch -f master 0242085...   # r34/r35 junk fixtures clone `master` (r34-sandbox-junk.py:67 `rev-parse master`)
```
Every run: `cd $S/lane` (or lane39), `TMPDIR=$S/tmp/<name>`, `--work $S/w/<name>` where the CLI has it. Registry commands taken from SKILL.md rows (`grep tests/fixtures SKILL.md`); historical base blobs for `--base-tool/--base` via `git show 6ff3413:tools/souji-seat-audit.py`, `6ff3413:tools/souji-proc-census.sh`, `8513d6ac`/`522dcd76:census/round-21/run-acceptance.py`, `12516f7d:tools/souji-seat-audit.py`, `007ab53:tools/souji-worktree-drift.py` (r36 blob) into `$S/base/`.

Structural fact that bounds the harm question: `git diff --stat 0242085909fb..128e412b0ced -- tools tests census/round-3* census/round-2* SKILL.md` shows ONLY three added files: `tests/fixtures/r40-c1-evidence.py` (+235), `r40-docstring-joined.py` (+126), `r40-drift-record-branches.py` (+150). No tool, no existing fixture and no earlier counter changed, so no r12–r39 consumer can regress by tool bytes. (SCORECARD.md/LOG.md/corpus changed; only the r34-c1-junk fixture reads SCORECARD.md — §3.)

## 1. r36–r40 families (the named ask) — SUMMARY line, exit code
| fixture (tests/fixtures/…) | command (after `cd $S/lane`) | SUMMARY | rc |
|---|---|---|---|
| r36-report-gate.py | `python3 -B tests/fixtures/r36-report-gate.py --work W` | `SUMMARY cases=21 pass=21 fail=0 control=STUB-REJECTED` | 0 |
| r36-worktree-drift.py | `… --work W` | `SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED` | 0 |
| r37-citation-reconcile.py | `… --work W` | `SUMMARY cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED` | 0 |
| r37-drift-discrimination.py | `… --work W` | `SUMMARY cases=6 pass=6 fail=0` | 0 |
| r37-drift-escapes.py | `… --base-tool $S/base/drift-r36.py --work W` | `SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED` | 0 |
| r37-drift-escapes.py (no base, registry says control-free exits 1) | `… --work W` | `SUMMARY cases=12 pass=12 fail=0 base_fail=0 control=NO-BASE-TOOL` | 1 (documented) |
| r37-drift-mutants.py | `… --fixture tests/fixtures/r37-drift-discrimination.py --work W` | `SUMMARY mutants=6 killed=6 survived=0` | 0 |
| r38-citation-commit.py | `… --work W` | `SUMMARY cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED` | 0 |
| r38-counter-arms.py | `… --work W` | `SUMMARY cases=6 pass=6 fail=0 control=FALSE-GREEN-REJECTED` | 0 |
| r38-drift-mutants.py | `… --fixture tests/fixtures/r38-drift-record.py --base-fixture tests/fixtures/r37-drift-discrimination.py --work W` | `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0` | 0 |
| r38-drift-record.py | `… --work W` | `SUMMARY cases=10 pass=10 fail=0` | 0 |
| r38-drift-write-envelope.py | `… --work W` (and with `--base-tool $S/base/drift-r36.py`) | `SUMMARY cases=12 pass=12 fail=0` / `… base_cases=12 base_fail=8 behavioral_fail=3` | 0 / 0 |
| r39-citation-rev.py | `… --work W` | `SUMMARY cases=8 pass=8 fail=0` | 0 |
| r39-drift-record-rules.py | `… --work W` | `SUMMARY cases=7 pass=7 fail=0` | 0 |
| r40-c1-evidence.py | `… --work W` (and `--base-counter census/round-39/c1-counter.py`) | `SUMMARY cases=8 pass=8 fail=0` (both) | 0 / 0 |
| r40-docstring-joined.py | `python3 -B tests/fixtures/r40-docstring-joined.py` | `SUMMARY cases=9 pass=9 fail=0` | 0 |
| r40-docstring-joined.py (`--one-line`, the r39 analyser arm) | `… --one-line` | `SUMMARY cases=9 pass=6 fail=3` (fails: case-synthetic-primary-has-trigger, case-frozen-pairs-present missing=['RECORD-OUTSIDE-ROOT(--root)'], case-outside-root-trigger-primary) | 1 (intended red arm; matches census/round-40/records/fixtures-after.txt) |
| r40-drift-record-branches.py | `… --work W` | `SUMMARY cases=8 pass=8 fail=0` | 0 |

## 2. r12–r35 families (all committed fixtures; every `.py`/`.sh` under tests/fixtures/)
| fixture | command | final/summary line | rc |
|---|---|---|---|
| r12-maintenance-guard.sh | `bash tests/fixtures/r12-maintenance-guard.sh` | `id=SOUJI-R12-MAINT-maintenance-auto … verdict=PASS` (all PASS) | 0 |
| r13-cert-evidence.py | default | `fixture: 5/5 checks passed` | 0 |
| r13-quarantine-bounds.sh | default | `SUMMARY total=5 failed=0 hung=0` | 0 |
| r13-repo-structure.sh | `--selftest --probe tools/souji-repo-structure.sh` | `selftest=PASS ids=7/7` | 0 |
| r14-census-boundary.py | default | `SUMMARY total=12 failed=0` | 0 |
| r14-evidence-cache.py | default | `fixture: 22/22 checks passed` | 0 |
| r15-census-config.py | default | `SUMMARY total=20 failed=0` | 0 |
| r15-preservation-evidence.py | default | `fixture: 8/8 checks passed` | 0 |
| r16-landing-gate.py | default | `SUMMARY total=15 failed=0` | 0 |
| r17-census-hygiene.py | default | `SUMMARY total=29 failed=0` | 0 |
| r17-jj-receipts.sh | default / `--tool-dir tools` | `SUMMARY total=35 failed=0 skipped=2` | 0 |
| r18-census-bounded.py | default | `SUMMARY total=12 failed=0` | 0 |
| r18-landing-pointers.py | default | `SUMMARY total=11 failed=0` | 0 |
| r18-proc-census.sh | default (parallel AND serial) | `SUMMARY total=19 failed=1` (P7 `traced census failed (rc=124 timed_out=True …)`) | 1 — pre-existing, §3 |
| r19-carry-wrap.py | default | `SUMMARY total=4 failed=0 base_discriminating=2` | 0 |
| r19-rev-pin.py | default | `SUMMARY total=13 failed=0 base_discriminating=6` | 0 |
| r19-seat-audit-shapes.py | default | `SUMMARY total=17 failed=0 base_discriminating=12` | 0 |
| r20-audit-contract.py | default / `--base-tool $S/base/audit-12516f7d.py` | `SUMMARY total=66 pass=66 fail=0 base_discriminating=0` / `total=78 pass=78 fail=0 base_discriminating=11` | 0 / 0 |
| r20-input-binding.py | default / `--baseline 12516f7d…` | `total=45 pass=45 … baseline_mismatches=not-requested` / `total=52 pass=52 fail=0 … baseline_mismatches=37` | 0 / 0 |
| r21-read-render-edges.py | `--tool tools/souji-seat-audit.py` | `SUMMARY total=4 pass=4 fail=0` | 0 |
| r21-read-root.py | `--tool tools/souji-seat-audit.py --base-tool $S/base/audit-6ff3413.py` | `SUMMARY total=32 pass=32 fail=0 base_discriminating=14` | 0 |
| r21-reason-canary.sh | `--tool tools/souji-proc-census.sh --base $S/base/proc-6ff3413.sh` | `SUMMARY total=27 pass=27 fail=0 leaks=0 base_leaks=19 max_reason_bytes=160` | 0 |
| r21-replay-boundaries.py | `--tool census/round-21/run-acceptance.py --base-tool $S/base/runner-8513d6ac.py` | `SUMMARY total=8 pass=8 fail=0 base_discriminating=4` | 0 |
| r21-source-head.py | `--tool census/round-21/run-acceptance.py --base-tool $S/base/runner-522dcd76.py` | `SUMMARY total=3 pass=3 fail=0 base_discriminating=1` | 0 |
| r21-source-refs.py | `--runner census/round-21/run-acceptance.py --root $S/lane --rev 128e412… --work <fresh>` | `CASE FAIL refs/remotes/synthetic/main runner_exit=1 matched=16` / `SUMMARY total=1 pass=0 fail=1` | 1 — pre-existing, §3 |
| r22-result-oracle.py | `--runner census/round-21/run-acceptance.py` | JSON `"pass": 258, "fail": 0` | 0 |
| r23-locator-heading.py | registered 2-entry cmd (`repo-size-census-readonly.md count-objects-garbage-readings-r25.md`) | `entries=2 locators=11 locators_bad=0` | 0 |
| r23-locator-heading.py (mutant `tests/fixtures/q54-mutant-entry.md`) | `--entries tests/fixtures/q54-mutant-entry.md …` | `entries=1 locators=1 locators_bad=1` (must be nonzero) | 1 (intended) |
| r23-receipt-run.py | default | `selftest=8/8` | 0 |
| r23-record-agreement.py | default | `selftest=15/15`, `control=FALSE-GREEN-REJECTED` | 0 |
| r24-coverage-agreement.py | `--tool tools/souji-coverage-agreement.py` | `cases=9 pass=9 control=FALSE-GREEN-REJECTED` | 0 |
| r24-receipt-verify.py | `--tool tools/souji-receipt-run.py` | `cases=8 pass=8 refusals=2/2 regress=5/5` | 0 |
| r24-size-census.py | `--tool tools/souji-size-census.py` | `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` | 0 |
| r25-coverage-agreement.py | `--tool tools/souji-coverage-agreement.py` | `cases=16 pass=16 control=FALSE-GREEN-REJECTED` | 0 |
| r25-q57-check.sh | `. census/round-24/records/slice-verdicts.tsv … corpus/lessons/round-25.md $(cat census/round-28/q57-sites.txt)` | `q57=PASS` | 0 |
| r25-receipt-stderr.py | `--rev 128e412…` | `cases=1 pass=1` | 0 |
| r25-slice-mapping.py | default | `rows=8/8 status=PASS` | 0 |
| r26-axis-check.py | `--tool tools/souji-axis-check.py` | `cases=12 pass=12 control=FALSE-GREEN-REJECTED` | 0 |
| r27-pre-report-gate.sh | default | `cases=4 pass=4 control=FALSE-GREEN-REJECTED` | 0 |
| r28-wave-evidence-capture.sh | default | `cases=15 pass=15 control=TAMPER-REJECTED` | 0 |
| r29-registry-agreement.py | default | `cases=20 pass=20 control=FALSE-GREEN-REJECTED` | 0 |
| r30-jj-keep-expiry.sh | default | 8 `RESULT step=… ` lines, last `step=8-control-expire-now keep_refs=6 object_present=yes` | 0 |
| r30-landing-gate-discovery.py | default | `cases=7 pass=7 control=FALSE-GREEN-REJECTED` | 0 |
| r31-jj-object-clock.sh | default | RESULT lines, last `arm=reflog-only step=reflog-expire-then-prune … object_present=no` | 0 |
| r31-landing-gate-precision.py | default | `cases=10 pass=10 control=FALSE-GREEN-REJECTED` | 0 |
| r32-jj-mtime-clock.sh | default | RESULT lines, last `arm=nocruft step=gc-cruft-disabled obj=C mtime=recent where=loose object_present=yes` | 0 |
| r34-c1-junk.py | `--counter census/round-34/c1-counter.py --scratch W` (master pinned to 128e412) | `cases=3 pass=0 control=STUB-REJECTED` (all 3 `BAD-ROW(duplicate restatement)`) | 1 — pre-existing, §3 |
| r34-sandbox-junk.py | `--counter census/round-34/c2-counter.py --scratch W` | `subprocess.TimeoutExpired … after 900 seconds` | 1 — pre-existing, §3 |
| r35-sandbox-junk.py | `--counter census/round-35/c2-counter.py --scratch W` | `cases=5 pass=5 control=STUB-REJECTED checked=W1;W2;W3;W4;N3` | 0 |
`tests/fixtures/case-F*`, `r13-cert-frozen/`, `r14-cache-frozen/`, `r15-preservation-frozen/`: data dirs consumed by the fixtures above (not executables).

## 3. Reds, and why they are not r40 harm (same command, r39 base lane39 @ 0242085909fb)
- r18-proc-census P7 (`rc=124 timed_out=True`, strace-traced census): `SUMMARY total=19 failed=1`, rc 1 at BOTH 0242085 and 128e412, also serial → host-environment/pre-existing.
- r21-source-refs: `CASE FAIL refs/remotes/synthetic/main runner_exit=1 matched=16`, `SUMMARY total=1 pass=0 fail=1`, rc 1 at BOTH revs (`--root $S/lane39 --rev 0242085…` and landed) → pre-existing.
- r34-c1-junk: `cases=3 pass=0 control=STUB-REJECTED`, rc 1 at BOTH revs with `master` pinned to the measured rev (it reads SCORECARD.md:71 / PROBE E18, frozen at r34) → pre-existing, r40's SCORECARD edit changes nothing.
- r34-sandbox-junk: 900 s inner timeout at BOTH revs; SKILL.md already records "timed out at 900 s, not a pass".
- r23-locator-heading with `--entries corpus/knowledge/*.md` reports `locators_bad=17`; that is out of the Q54 registered scope (Gate-without-snapshot entries and an r29 `CONSTANTS` locator). The registered 2-entry call is clean (§2). No r40 entry adds a bad locator in my run (the three r40 knowledge entries print `UNSCOPED … predates Q54`).

## 4. Attack finding on the landed C3 bytes (not a regression, a landed-bytes defect)
`python3 -B census/round-40/c3-counter.py --root $S/lane --rev 128e412… --base-rev 0242085… --scratch $S/w/c3` at the landed commit:
```
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- …
MUTANT M16 killed=yes … fails=4 … failing=- …
MUTANT M17 killed=yes … fails=1 … failing=- …
MUTANT M18 killed=yes … fails=1 … failing=- …
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e   (rc 0)
```
Kills and pristine/base verdicts hold (C3 predicate satisfied). But every `failing=` is `-`: c3-counter.py (landed) filtered `l.endswith("FAIL")`, yet the fixture prints `case-X=FAIL <detail>` so the filter never matched; the docstring promises "prints the failing case names, so a kill is attributable". Commit 8a5fbdb changed the filter to `"=FAIL" in l.split(" ",1)[0]` (`git diff 128e412..HEAD -- census/round-40/c3-counter.py`). So at 128e412 the kill-attribution claim was false; repaired later. Verdict on the claim as landed: kill counts true, attribution FALSIFIED-at-128e412.

## 5. Verdict
- Harm from r40 to any existing consumer: **SAFE** (zero tool/fixture/counter bytes of r12–r39 changed; every fixture result equals the r39 base result; the four reds are identical at base).
- r40 fixtures themselves: 8/8, 9/9 (6/9 on the intended `--one-line` base arm), 8/8 at the landed bytes.
- Flag: §4 C3 attribution defect at landed bytes (repaired in 8a5fbdb).

## 6. Scratch / installs
No installs. Scratch dir `/fast/scratch/hyaku/souji-r40/w2/R40w2executor06` removed after writing this report (see final line check below). Nothing in the lane or fleet written except this file.
