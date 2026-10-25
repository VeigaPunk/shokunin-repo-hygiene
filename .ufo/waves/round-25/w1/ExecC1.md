# ExecC1 — C1 (calibration, kill-rule tool row) implementation report

Seat: L1Souji25.ExecC1-2 (executor, wave 1). Drafts written:
- `.ufo/waves/round-25/w1/souji-coverage-agreement.py` (tool, `--base-rev` arm)
- `.ufo/waves/round-25/w1/r25-coverage-agreement.py` (fixture, 16 cases incl. k7 veto-less control)

## Status
STATUS: PASS — green arm `cases=16 pass=16 control=FALSE-GREEN-REJECTED` rc 0; red arm
(old tool blob `a6d2d15:tools/souji-coverage-agreement.py`, sha256
`71b89eb3…b8f28897`) fails k1–k7 rc 1; r24 fixture 9/9 on the draft; byte-identity with the old
tool without `--base-rev` on 5 revisions; 8/8 semantic mutants killed; real-lane runs at base
and tip print `kill_tested=6 kill_violations=0`, rc 0.

## Evidence
All commands run from the lane root; scratch `/var/tmp/souji-r25-ExecC1` (removed at end).
Receipts (v1 grammar, `receipt=v1` header, stdout/stderr fences) in
`.ufo/waves/round-25/w1/ExecC1/c1-*.tsv`:
- `c1-green-arm.tsv` — `python3 -B .ufo/waves/round-25/w1/r25-coverage-agreement.py --tool .ufo/waves/round-25/w1/souji-coverage-agreement.py` → rc 0, last line `cases=16 pass=16 control=FALSE-GREEN-REJECTED`.
- `c1-red-arm.tsv` — same fixture with old tool (`git show a6d2d15:tools/souji-coverage-agreement.py` into scratch) → rc 1; k1–k7 all `FAIL` (`counts_lines=0 exit=2` — the old tool refuses `--base-rev`).
- `c1-r24-fixture-on-draft.tsv` — committed r24 fixture vs draft → rc 0, `cases=9 pass=9`.
- `c1-real-base-vs-base.tsv` — `--rev a6d2d15 --base-rev a6d2d15` → `grounded=6 mapped=6 dangling=0 mismatches=0 kill_tested=6 kill_violations=0`, rc 0.
- `c1-real-tip-vs-base.tsv` — `--rev 6e4737e --base-rev a6d2d15` → same line, rc 0.
- `c1-real-reverse-witness.tsv` — `--rev a65fac9 --base-rev a6d2d15` → rc 1; two KILL-RULE rows
  (`count-objects-linked-worktree-garbage.md` absent; `git-repo-structure-readonly.md` lost F2)
  + two MISSING-FROM-MAP rows: real, honest red witness.
- `c1-real-tip-no-base.tsv` — no `--base-rev`, r24 output unchanged.
- `c1-base-refusal.tsv` — `--base-rev not-hex` → rc 2, `refused: --base-rev must be a full 40-hex commit id`.
Byte-identity (stdout and stderr) old-vs-draft without `--base-rev` at a6d2d15, 6e4737e,
315422b, a65fac9, 778747e — `cmp=same`, same rc on all five.
Semantic mutants (8; each killed by >=1 frozen case): rev-vs-rev (k1/k2/k5), existence-only
(k2/k5), kill-in-mismatches (k1/k2/k5), exit-ignores-kill (k1/k2/k5), pairs-tested (k4/k5),
kill-keys-always (cases 1–8), wholefile-grounds (k2), ignore-base-rev (k1/k2/k5).
Fixture/case semantics: kill_tested = base-grounded entries; kill_violations = entries with
>=1 violation; `MISMATCH\tKILL-RULE\t...` one row per violated entry (detail lists base and
lost grounds); extra grounds allowed (k6); `--base-rev` refused like `--rev`.

## Findings
1. Amendment 1 (commit 1814de5) corrected the frozen after-target literal to
   `kill_tested=6 kill_violations=0`; the real runs match it exactly. The prereg base text
   `kill_tested=4` was a carried-over fact error (r24 base a65fac9 count), committed before any
   scoring; no predicate changed. (My earlier interject to L1 was preempted by this amendment.)
2. Amendment 3 (commit 6deb535) added k5 (partial-removal), k6 (extra-ground-allowed) and the
   k7 veto-less control; the fixture implements all three, and the target line
   `cases=16 pass=16 control=FALSE-GREEN-REJECTED` is reproduced. k7's own repo mirrors the
   k1/k2 shape; the veto-less wrapper (accepts `--base-rev`, prints
   `kill_tested=0 kill_violations=0`, exits 0) fails k1/k2 as required.
3. The red-arm discrimination is not only argparse rc 2: the k7 control makes a "veto-less"
   tool that *accepts* `--base-rev` fail k1/k2 via counts, and the reverse-witness receipt
   proves the kill rule fires on real data (a65fac9 vs a6d2d15).
4. Tool draft: `measure()` gains `kill_rule()`; the counts line gains ` kill_tested=N kill_violations=V` only with `--base-rev`; without it the output is byte-identical (verified). `--base-rev` uses the same full-40-hex/commit/durable checks as `--rev`.

## Attack log
- ATTACK (pre-adjudication, now moot): prereg C1 after-target `kill_tested=4` vs real count 6
  at base a6d2d15 — amendment 1 fixed the literal; tool implements the frozen rule (6). No
  tuning to 4 was done.
- Residual (disclosed, not fixed): the frozen semantics count violations per *entry*, so a
  per-*(line)* violation counter is not discriminated by any frozen case (all multi-ground
  cases only drop one ground at a time). Mutant `pairs-tested` is caught on k4/k5 instead;
  the per-line variant would still be caught by k5's row count only if it also counted
  wrongly. No case was added/re-specified after scoring.

## Integration notes (for L1)
- Drafts are standalone; L1 moves them into `tools/` and `tests/fixtures/` (I did not touch
  those dirs). Receipts reference the draft paths and current HEAD `de736c2`; regenerate with
  `souji-receipt-run.py` after commit if byte-pinning of the final tools is wanted (the
  include's `tool_sha256` are the draft bytes' hashes: tool `bb506469…`, fixture
  `2a65d8c…`).
- Scratch `/var/tmp/souji-r25-ExecC1` removed; no tool installed (git/python3/sha256sum/cmp
  all pre-existing bundled tools).
