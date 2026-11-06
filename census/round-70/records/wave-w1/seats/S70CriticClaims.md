# S70CriticClaims — C1/C2 falsification (post-landing wave, round 70)

Both claims were re-derived from committed bytes. Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Every instrument blob below is identical at `93a051b2`..`152b46c3` (writer `0e54c056`, counter `527a32cb`, matrix `a7f41327`, harness
`049abde1`, prereg `221413da`, receipts `9ceae58f`/`bd0253ec`, probe `383c7274`), so every run is valid
at the final tip. The lane advanced four times while this review ran (`9167e02d` → `20c117ce` →
`63ceb475` → `152b46c3`); I re-checked the blobs at each step.

## Verdicts

- **C1 — STANDS on its frozen predicate; QUALIFIED in scope.** The frozen SUMMARY/EXIT reproduce
  byte-for-byte at the candidate and at the assigned landing tip. The predicate does **not** witness
  the fourth variable (GIT_NOGLOB_PATHSPECS) and does not witness the scrub *mechanism* at all.
- **C2 — STANDS on its frozen predicate; QUALIFIED, with a HIGH qualification.** Both arms reproduce,
  but `positive_battery=PASS` is a single-member (D01) positive: the same counter over the full frozen
  r69 battery is red (8/26 class mismatches, `EXIT=1`) where the r69 counter was green. The claim is
  also not calibration under `AXES.md:15`, and its kill set is disjoint from the code path C1 runs.

## C1 evidence (reproduced, not trusted)

- Candidate `93a051b2`: `SUMMARY matrix=59 base_forgeries=4 base_honest=13 new_forgeries=0
  new_honest=15 class_mismatches=0 new_echo=0 errors=0 regress=PASS` / `EXIT=0` — identical to
  `census/round-70/records/c1-after.txt`; all 59 `CASE` lines diff-identical (`c1-rerun.txt`).
- Assigned tip `feb283ee`: same SUMMARY, `EXIT=0`, `# candidate new=feb283ee…:tools/souji-receipt-write.py`
  (`c1tip.txt`). Writer blob `0e54c056` is identical at `93a051b2`, `e84f691b`, `feb283ee`, `9167e02`.
- Do-nothing control reproduced: `new_forgeries=4 new_honest=13 class_mismatches=5`, `EXIT=1` (`dn.txt`).
- GA/ICA are real over-refusals, not fixture artefacts: in a fixture at `/fast/scratch/.../tmp.*`,
  `GIT_GLOB_PATHSPECS=1 git ls-tree HEAD -- tools/instr.sh` → `fatal: tools/instr.sh: pathspec magic
  not supported by this command: 'glob'`, rc=128; same for `icase`. `GIT_NOGLOB_PATHSPECS=1` → rc=0
  (no error), so NGA/NGD cannot discriminate the NOGLOB scrub.
- LITERAL forgery mechanism confirmed: `GIT_LITERAL_PATHSPECS=1 git ls-files -v -z ':(top)'` prints
  nothing (0 records) vs `H tools/instr.sh` plain — a vacuous index-flag read.
- Cheaper alternatives tested (all fail): F1 refuse-on-presence 11/8 EXIT=1; F2 literal-only 13/0
  EXIT=1; global `--literal-pathspecs` in `git()` → `new_forgeries=10 class_mismatches=14`, EXIT=1
  (and under GLOB git rejects the flag: `fatal: global 'literal' pathspec setting is incompatible
  with all other global pathspec settings`).

## C2 evidence

- After: `SUMMARY label=c2-after-r70 positive_selftest=PASS positive_battery=PASS mutants=4 killed=4
  survived=0 tamper=detected score=0` / `EXIT=0` — byte-identical to `records/c2-after.txt` (`c2-rerun.txt`).
  CM1 26/29, CM2/CM3/CM4 28/29 selftest cases; T1 `fatal=C1-COUNTER-FATAL: battery members unverified`.
- Before: `killed=0 survived=4 tamper=undetected score=5` / `EXIT=1` (`c2before.txt`).
- Writer selftest 38/38; counter selftest 29/29; instrument hashes in both receipts match the blobs
  (counter `3f684c3e…`, harness `38c30eff…`, base writer `b811ee2a…`, candidate `118597e0…`).
- Mutant-to-code map (`census/round-70/c2-harness.py:48-56`): CM1 `classify_outcome`, CM2/CM4
  `battery_verdict`, CM3 `echo_violation` — all **battery/selftest-path** code. C1's frozen run passes
  no `--battery-*` argument and never executes any of it.

## Findings

- **HIGH — C2's `positive_battery=PASS` is a single-member positive over a red battery.** The harness
  runs its positive battery arm as `--only D01` (`census/round-70/c2-harness.py:137`). The same
  frozen counter over the **full** frozen r69 battery (no `--only`) is red:
  `BATTERY mutants=26 kills=26 label_only=0 over_refusal=0 echo_violation=0 survived=0 error=0
  all_match=false` / `EXIT=1` (`census/round-70/probes/battery-r69-members-r70-counter.txt`), with 8
  members whose observed class ≠ manifest expectation (M-CD-NCABS, M-CD-NCRAW, K1, M-CD-ROOTREL, D02,
  D03, D04, D30 — all `outcome=forgery`). Cause: the r70 matrix adds four base-writer forgery rows
  (LD LN4 LG1 LA9), and Q131 precedence makes `forgery` outrank the r69 `label-only`/`over-refusal`/
  `echo-violation` class. The r69 counter over the same battery is `kills=18 … EXIT=0` with 0
  mismatches (`census/round-69/records/c1-after-battery.txt`). So the round's C1 matrix extension makes
  the only existing battery instrument red under the round's own counter, and the C2 harness cannot see
  it because its positive control picks the one member (D01, expected `forgery`) that survives the
  precedence shift. The limit appears only in a **post-freeze** probe (commit `63ceb475`, 16:11:30,
  after the 15:49:38 freeze and the 15:54:09 after-arm); the frozen prereg's named limits do not
  disclose it, and the frozen C2 predicate was not changed (correctly). I reproduced the probe
  independently (`batt.txt`): `BATTERY mutants=26 … all_match=false`, `EXIT=1`, the same eight
  mismatched members, instrument sha256 `3f684c3e…`.
- **MEDIUM — the frozen C1 predicate does not witness the fourth variable.** Dropping
  `GIT_NOGLOB_PATHSPECS` from `PATHSPEC_ENV` (`tools/souji-receipt-write.py:105`) still prints the
  frozen SUMMARY and `EXIT=0` (`c1v3.txt`; `variant-3var.diff`). No matrix row's verdict depends on
  it (NGA accept / NGD refuse are identical with and without the scrub). The landing text "scrubs the
  four pathspec variables" is code-true but measurement-false for one of the four; the prereg's named
  limits (`preregistration.txt:93-101`) do not name this gap.
- **MEDIUM — the C1 predicate is mechanism-agnostic.** A rewrite that drops every pathspec
  (`ls-files -s -z`, `ls-files -v -z`, `ls-tree -r -z <rev>`) and keeps **no env scrub** also prints
  the frozen SUMMARY/`EXIT=0` (`c1psf.txt`; `variant-pathspec-free.diff`). "The fix is a scrub inside
  git()" is a design statement, not something the predicate measures.
- **MEDIUM — C2 is not a calibration claim under the lane's own definition.** `AXES.md:15`:
  calibration = "SHONEN.md/SCORECARD entries match observed repo state". C2 counts selftest exit
  codes of synthetic mutants in a scratch copy; it never compares a lane self-assessment to repo
  state. It is an instrument self-test (meta-coverage of four named defect classes), and the mutants
  exercise a path C1 never runs — so C2 cannot underwrite C1's numbers either.
- **MEDIUM — SCORECARD overreach.** `SCORECARD.md:236` says the selftest kills "the four r69-found
  instrument blind spots". `S69MutTester.md` recorded **six** survivors (a, b, c, d, e2, e4). The
  r70 selftest closes a/b/d + a survived-gate; e2/e4 (weakening the selftest's own assertion) still
  survive: my e2 mutant (`len(emitted) >= 3`) prints `SELFTEST cases=29 pass=29 fail=0` / `EXIT=0`
  (`st-e2.txt`). This is structural (a selftest cannot detect weakening of its own assertion) and
  must be a named limit, not silently counted as closed.
- **MEDIUM — C2's after-arm was determined at freeze time.** CF1/CF2, committed in the freeze, already
  print `killed=4 survived=0 tamper=detected` (`controls/c2-CF1-*.txt`, `c2-CF2-*.txt`; prereg
  disclosure (ii)). The mutant *classes* are externally sourced (S69MutTester a/b/d, r69 lesson:44
  routed item c) but the regexes and the killing tests were authored in the same commit; the after-arm
  adds only "the regexes still match the final bytes". An honest C2 needs non-author mutants, mutants
  on the matrix/summary path, and a real mismatch count against repo state.
- **LOW — "at the landing tip" is loose.** `preregistration.txt:65-66` says the counter runs with
  `--rev <landing tip>`; the receipt records `rev=93a051b2`. Blobs are identical at every later tip and
  I reproduced the SUMMARY at `feb283ee`, so the substance holds; the receipt's `rev=` is not the tip.
  The lane advanced three times during the review (`9167e02d` 16:01:12 → `20c117ce` 16:01:49 →
  `63ceb475` 16:11:30); no instrument blob changed at any step.
- **LOW — author dates are unusable in this lane.** `.jj` is present; the freeze `0243af04` has author
  date `2026-11-05 17:34:21` (= the base commit's time) and committer date `2026-11-06 15:49:38`.
  Committer order is authoritative and shows no post-data target change: freeze 15:49:38 → candidate
  15:50:28 → after-arms 15:54:09 → evidence 15:54:29/15:56:41 → 16:01:12 → 16:01:49 → 16:11:30;
  `git log -- census/round-70/{preregistration.txt,c1-counter.py,c1-matrix.tsv,c2-harness.py}` shows
  those instruments touched only at the freeze. The post-freeze probe (`63ceb475`) adds a scope
  disclosure after the data but does not change a frozen predicate.

## Separability

C1 and C2 are separable at invocation level (C1 passes no battery/harness argument; C2 never reads
the writer) but **not mutually supporting**: C2's kill set is battery-path code, C1's run is matrix-path
code, and both trust the same counter blob `527a32cb`. A matrix-path counter defect would pass both.

## Other landed changes checked

- r69 wave mirror (`0d8ce29a`): `diff -rq .ufo/waves/round-69/w1 census/round-69/records/wave-w1/seats`
  → rc 0, 66 files each; byte-identical as claimed.
- Sources (`feb283ee`): `census/round-70/srcs/git-manual.html` sha256 `534c674f…` (identical to r69's
  capture), `gitglossary.html` `216bc0df…` — match the lesson and the prereg.
- Post-tip commits changed no r70 instrument: `9167e02` (`tools/souji-pointer-check.py`,
  `records/pointer-check-r69.txt`), `20c117ce` (`:line` suffix stripping, r69 receipt regenerated),
  `63ceb475` (SCORECARD rows, `records/pointer-check-r70.txt`, the battery probe). The r69 pointer
  receipt reports 5 missing r69 prereg pointers, EXIT=1; the r70 one reports 0 missing, EXIT=0.

## Files written (all under the lane)

`.ufo/waves/round-70/w1/S70CriticClaims.md`, and in `.ufo/waves/round-70/w1/S70CriticClaims/`:
`c1-rerun.txt`, `c1tip.txt`, `dn.txt`, `c1v3.txt`, `c1vlit.txt`, `c1psf.txt`, `c2-rerun.txt`,
`c2before.txt`, `batt.txt`, `st-e2.txt`, `wst.txt`, `variant-3var.diff`, `variant-literal-flag.diff`,
`variant-pathspec-free.diff`, `mutant-e2.diff`. Scratch `/fast/scratch/hyaku/souji-r70/S70CriticClaims`
removed. No tool installs; no pacman. No tracked lane file was written by this seat: every write is
under the gitignored `.ufo/waves/` tree (`.gitignore:1`).

## Commands

```
python3 -B census/round-70/c1-counter.py --root $L --matrix census/round-70/c1-matrix.tsv \
  --base-rev e063a2fc… --rev 93a051b2… --tool tools/souji-receipt-write.py --work $S/c1
  # same with --rev feb283ee… --work $S/c1tip ; same shape with --new-tool $S/variants/{v3,vlit,vpsfree}.py
python3 -B census/round-70/c1-counter.py … --new-tool census/round-70/controls/base-writer-e063a2fc.py --work $S/dn
python3 -B census/round-70/c2-harness.py --label c2-after-r70 … --work $S/c2
python3 -B census/round-70/c2-harness.py --label c2-before-r69 --counter census/round-69/c1-counter.py \
  --matrix census/round-69/c1-matrix.tsv --base-rev 3639087917ea… … --work $S/c2before
TMPDIR=$S/wst python3 -B tools/souji-receipt-write.py --selftest --work $S/wst
python3 -B $S/variants/counter-e2.py --selftest … --work $S/st-e2
```
