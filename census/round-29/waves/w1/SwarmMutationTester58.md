# SwarmMutationTester58 — mutation-test probe, base capture tool vs its r28 fixture

## Status

STATUS: PASS — 12 mutants of `tools/souji-wave-evidence-capture.sh` run through the 6-case fixture
`tests/fixtures/r28-wave-evidence-capture.sh` in scratch; 8 survivors found (5 real coverage gaps +
3 equivalent); required-case set for the v2 fixture delivered; lane bytes untouched (hash-verified).

## Evidence

- Revision: lane HEAD `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (preregistration commit), branch master.
- Scratch: `/var/tmp/souji-r29-MutateCaptureFixtureBase/` (tool + fixture copied; fixture only ever run there).
- Baseline (pristine): `bash .../tests/fixtures/r28-wave-evidence-capture.sh` -> rc 0,
  `cases=6 pass=6 control=TAMPER-REJECTED`.
- Battery: 12 mutants, one mutation each (m02 needed a 2-line coherent form); full outputs in
  `## Attack log`. Survivor summary line for each: `cases=6 pass=6 control=TAMPER-REJECTED`, rc 0.
- Kill-case probes (`killcases.sh` in scratch) — pristine passes all five:
  `RC1_verify_payload_tamper=4 RC2_cap=0/file=0 RC3_cap=0/targets=0 RC4_source_summary=4 RC5_bad_round=1`;
  each survivor fails exactly its own case (m02 RC1=0, m07 RC4=0, m10 RC5=2, m11 RC2 cap=4/file=1, m12 RC3 targets=1).
- Restoration: scratch tool restored from pristine (`cmp` IDENTICAL); post-restore fixture run rc 0
  `cases=6 pass=6`; lane file sha256 before = after:
  `c70655e0fdd1abbc2eac5527f27836eaae798795fd1ad59bcbd996c9749c6849` (tool),
  `caad4ab4001d6a7ed8aa5fc33d484b058735f5f43d71613d9d667f55c379ab1a` (fixture);
  `git status --porcelain` on both paths empty. Scratch removed at finish.
- Tooling installs: none (bash/coreutils/python3 only; operator 2026-10-19 record: nothing installed).

Paths below are relative to `/home/vgpnk/Projects/shokunin/souji-shokunin`.

## Findings

1. **The r28 failure models all survive the base fixture.** The three r28-modeling mutants — verify the
   disk copy (m02), ignore git's ignore rules (m11), drop symlink accounting (m12) — each pass
   `cases=6 pass=6 control=TAMPER-REJECTED`. Location: tools/souji-wave-evidence-capture.sh:172-193 (verify
   block), :100 (copy). The fixture has no payload-tamper `--verify` case, no ignored-name case, and no
   link-target fidelity check.
2. **`--verify` never checks the receipt's payload bytes against tampering.** Its only tamper case flips
   `manifest.sha256` itself. Mutant m02 keeps case 3 green (rc 4) while hashing the live source instead of
   the receipt — `--verify` on a corrupted receipt copy returns 0. Kill: RC1 (payload byte-flip then
   `--verify` -> rc 4). Location: tools/souji-wave-evidence-capture.sh:172-193;
   tests/fixtures/r28-wave-evidence-capture.sh:77-98. Quote (tool:176): `printf '%s\0' "${files[@]}"`,
   context: the recompute compares receipt bytes to the stored manifest — m02 skips exactly that compare.
3. **Source-provided `summary.tsv` / `manifest.sha256` are silently swallowed unless the hash-set
   comparison guards.** Base refuses rc 4 because the generated file overwrites the copied one and the
   value sets diverge; m07 (comparison dropped) returns 0 with source bytes replaced. Kill: RC4.
   Location: tools/souji-wave-evidence-capture.sh:192 `if [[ $src_hashes != "$dst_hashes" ]]; then`.
4. **Ignored names are untested; the safe property is refuse-or-copy, never silent drop.** Base has no
   gitignore logic and captures `__pycache__/` byte-exact; m11's silent drop trips the hash-set identity
   (rc 4) — the v2 gitignore handling must keep an explicit account so that property stays observable.
   Kill: RC2. Location: tools/souji-wave-evidence-capture.sh:100 `if ! cp -a -- "$src/." "$dst/"; then`.
5. **Symlink target fidelity is never verified.** Manifest and both hash sets cover regular files only;
   the supplementary check asserts links exist and stay out of the manifest but never compares targets.
   m12 rewrote every receipt link target to its basename and passed all six cases; only the absolute /
   nested-relative `readlink` equality of RC3 kills it. Locations: tools/souji-wave-evidence-capture.sh:157,
   :189; tests/fixtures/r28-wave-evidence-capture.sh:126-147. Quote (fixture:126): `supplementary (not a
   case): symlink entries are preserved verbatim, never`.
6. **Non-numeric round is untested** (m10 survived; RC5 kills). Location: tools/souji-wave-evidence-capture.sh:53
   `case $round in`.
7. **Three equivalent mutants — no black-box case can kill them.** m01 (generation-site self-exclusion,
   tool:157 — the find cannot observe `manifest.sha256` on a fresh receipt); m05 (inline `LC_ALL=C` is
   redundant under the global `export LC_ALL=C`, tool:35); m06 (nested src/dst lexical refusal,
   tool:90-95 — dead branch: both paths derive from one validated absolute lane, neither prefix can
   match). m06 is a tool-owner simplification candidate, not a fixture gap.
8. **Keep the existing guards.** Case 3 killed m08 (verification-always-passes), case 4 killed m03
   (special-file refusal dropped, rc 0 vs 3), case 5 killed m09 (traversal check dropped, rc 2 vs 1), the
   supplementary check killed m04 (`cp -a` -> `cp -rL`). Promote the supplementary symlink check to a
   numbered case in v2 (it gates the exit code but sits outside `cases=6`,
   tests/fixtures/r28-wave-evidence-capture.sh:149 `printf 'cases=6 pass=%s control=TAMPER-REJECTED\n'`).
9. Abandoned mutant note: an unscoped m02 (verification hashed the source in both modes) was KILLED
   shallowly — case 1 rc 4 — because the manifest covers receipt-only `summary.tsv`, so source hashes can
   never match it. Replaced by the scoped verify-only form actually reported above (final sha256
   `8c4182055a29ea1ce68adbe857ed287d4cbad1d0985652d4987e3728cba963c6`).

## Attack log

All runs: `bash /var/tmp/souji-r29-MutateCaptureFixtureBase/tests/fixtures/r28-wave-evidence-capture.sh`
with the mutant installed at scratch `tools/souji-wave-evidence-capture.sh`. Expected detector: fixture
exit 1 (some `case-N: FAIL` or `supplementary: FAIL`, or control not set); fixture exit 0 with
`cases=6 pass=6` = survivor.

| mutant | site (tool line) | mutation | fixture rc | verdict | observed |
|--------|------------------|----------|-----------|---------|----------|
| m01 | 157 | drop `! -name manifest.sha256` at generation | 0 | SURVIVED (equivalent) | all 6 pass; site unreachable |
| m02 | 172-193 | `--verify` compares manifest against live source; receipt payload never hashed | 0 | SURVIVED | all 6 pass + control set; killed by RC1 (rc 0 vs 4) |
| m03 | 82 | drop `if [[ ! -f $p && ! -d $p && ! -L $p ]]; then bad=1; fi` | 1 | KILLED | case-4 FAIL rc=0 want=3 |
| m04 | 100 | `cp -a` -> `cp -rL` | 1 | KILLED | supplementary FAIL (symlink capture) |
| m05 | 157 | inline `LC_ALL=C` dropped from manifest sort | 0 | SURVIVED (equivalent) | all 6 pass; global export pins sort |
| m06 | 90-95 | nested src/dst refusal removed | 0 | SURVIVED (equivalent) | all 6 pass; dead lexical branch |
| m07 | 192-195 | source-vs-receipt value comparison dropped | 0 | SURVIVED | all 6 pass; killed by RC4 (rc 0 vs 4) |
| m08 | 180,194 | `verify_ok=0` -> `verify_ok=1` (both sites) | 1 | KILLED | case-3 FAIL rc=0 want=4, control unset |
| m09 | 57-59 | lane `..` traversal check removed | 1 | KILLED | case-5 FAIL rc=2 want=1 |
| m10 | 53-55 | numeric-round validation removed | 0 | SURVIVED | all 6 pass; killed by RC5 (rc 2 vs 1) |
| m11 | 104-105 | silent `__pycache__` drop after copy | 0 | SURVIVED | all 6 pass; killed by RC2 (cap rc 4, file absent) |
| m12 | 104-105 | receipt link targets rewritten to basename | 0 | SURVIVED | all 6 pass; killed by RC3 (target mismatch) |

Mutant sha256 (final bytes): m01 `14d1ee9a…`, m02 `8c418205…`, m03 `dae32c76…`, m04 `eed5dea8…`,
m05 `f1b46f1b…`, m06 `d1f36048…`, m07 `9ef0c2cd…`, m08 `1bf3998a…`, m09 `11cd09ac…`, m10 `d374a023…`,
m11 `e48acee3…`, m12 `5aff0f43…` (full values reproducible from the mutation table; scratch removed).

No counter, target, case set or predicate of the frozen preregistration is challenged by this seat; the
survivors above are coverage findings that define what the v2 fixture must kill.

## Deliveries

- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/deliver-required-fixture-cases.md
  (required case set RC1-RC5 + retain/promote list + verdict table)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/SwarmMutationTester58.md (this report)
