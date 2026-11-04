# S59ExecDomain — bounded domain trial of the r58 assessment comparator

Scope: execute the registered r58 assessment-comparator public command end-to-end over the
committed base and over isolated fixtures, independently recompute its matrix-derived numbers,
and deliver a reusable subprocess-only acceptance script. Substance evidence for the frozen
registry-kind correction `evidence → gate`; not a second claim, no score mapping, no production
edit.

Frozen references read first:

| item | ref / digest |
|---|---|
| base commit | `da5af55b5ea0a2a38edea05635a13416c698e6e7` |
| preregistration | `census/round-59/preregistration.txt` @ `19f44552378d333f401ff2f0864c4e8b9c59ab1f` |
| executed controls | `74455b7209e04a2375c2084738a7b6fea59bf6d5` |
| counter (frozen) | `census/round-58/c1-counter.py` sha256 `52ccdb1be66dd8379fb7bf81eae7e28965f156aa50e1e4573b82adb23bd0dea7` (byte-identical at base and HEAD) |
| matrices @ base | v5 `4cce7f59d97b453da6e85df090302772f3c1857afe5a939c5f4ec0aa28fb3d30`, v6 `27b8e7a2412d88a6ae731537cabae4ec6a36954f89544d210ecfa4bc7d3fe0ab` |
| SCORECARD @ base | sha256 `79e3caf321245b7cb1012f386c79c0d41887a28997839f0460832f8b233d44b6`, 1488 lines |
| registry row observed | `SKILL.md:776` @ base: `r58 assessment comparison | evidence` |

## Independent recomputation (no lane counter imported)

Own parser over the committed TSV bytes at base (header pinned to
`fixture counter rev base exit finding findings_all SUMMARY`, 8 fields/row, 36 rows/arm).
Result: **identical = 34**, **exit_zero = 10,8**; the two non-identical fixture pairs are
`B4-INLINE-NBSP-OPENER` and `C4-INLINE-CLOSED-COMMENT` (both exit `0` in v5, `1` in v6 with
divergent finding lists). The comparator’s `SUMMARY` line reports exactly these derived values.
No lane code was imported or copied for this count.

## End-to-end public CLI trial (actual command, actual rc)

Command: `python3 -B census/round-58/c1-counter.py --root LANE --rev FULL40`.

1. Committed base `da5af55b…` — **rc 0**, stderr empty:
   ```
   MATCH R58-CALIBRATION carry_identical=34 supersedes the r57 SCORECARD claim "all 33 carry-over rows".
   MATCH R58-CALIBRATION exit_zero=10,8 counted separately per matrix; the r57 two-file awk command emits the combined total 18, not the pair.
   SUMMARY assertions=2 mismatches=0 carry_identical=34 exit_zero=10,8
   ```
   stdout sha256 `93f200de25962da54c22d49dbc5ab225707eb30493003fc4fb8cd4e4321d49f0`.
2. Isolated fixture, one correction omitted — matrices + base SCORECARD committed in an
   independent Git repo (toplevel asserted), then the single line starting
   `R58-CALIBRATION exit_zero=` removed. Fixture revisions:
   `e30f311f8851c96bc3195a79c72edfb407dd1341` (honest copy), `72e7ec7139fab20932c1c202a8720b8c115396cb`
   (one omitted); omitted input sha256 `414d3b816de6cb82e2b6a22b75421b7a421c0eee1a09d32feec2af41b3cd1738`,
   1487 lines. **rc 1**, stderr empty:
   ```
   MATCH R58-CALIBRATION carry_identical=34 supersedes the r57 SCORECARD claim "all 33 carry-over rows".
   MISSING R58-CALIBRATION exit_zero=10,8 counted separately per matrix; the r57 two-file awk command emits the combined total 18, not the pair.
   SUMMARY assertions=2 mismatches=1 carry_identical=34 exit_zero=10,8
   ```
   stdout sha256 `9f7080184ad559b48d8f4007f4d61f9c0727a2cdb70bf8ed6ad635aab9503e75`.

Exact commands, input bytes and digests: `trial/receipt.json`, `trial/honest.stdout.txt`,
`trial/honest.SCORECARD.md`, `trial/one-correction-omitted.stdout.txt`,
`trial/one-correction-omitted.SCORECARD.md`.

## Reusable independent acceptance script

`acceptance.py` — arguments exactly `--tool PATH --work DIR --root LANE --rev REV`. It invokes
the public CLI with `subprocess` only (no helper import/call), rebuilds fixtures with
`git init` after asserting `rev-parse --show-toplevel` equals the fixture, and recomputes
`identical` / `exit_zero` from committed TSV bytes to derive its own expected `SUMMARY`.
Exit 0 iff every asserted case matches; 1 on mismatch; 2 on CLI/input failure.

| case | fixture input | expected |
|---|---|---|
| `committed-honest` | committed lane @ rev | rc 0, both MATCH, `mismatches=0 carry_identical=34 exit_zero=10,8` |
| `one-correction-omitted` | base SCORECARD minus `exit_zero` note (`414d3b81…`) | rc 1, carry MATCH / exit_zero MISSING, `mismatches=1` |
| `prose-wrong-count-forgery` | template-shaped notes carrying the superseded count `33` and combined `18` (`448fac34…`) | rc 1, both MISSING, `mismatches=2`, SUMMARY still reports true 34 / 10,8 |
| `both-missing` | neither note (`4042e10d…`) | rc 1, both MISSING, `mismatches=2` |
| `prose-contradiction-adjacent` (observation) | exact notes plus contradicting wrong-count prose (`22e5c86c…`) | rc 0 — presence predicate only; recorded scope, not execution authentication |

Run receipt: `acceptance-receipt.json`, `accepted=true`, 4/4 asserted cases, script sha256
`efbc59a5f798c9c3c51760b9b8091d9fae3f00982308b764631ba1d08446f358`, receipt sha256
`6b52c9c845dc0647934895bb4667d827ac6d5316a22586f4dc2da37003cd5615`. Fixture revisions in that
run: one-omitted `028ddba21771d655360cecedf54dcd9045c85c1e`, forgery
`2c793ffa760ff3646547edb6787af500a6e56976`, both-missing `a6fc401ae66b053d1b4288dc0501fadd8b5d5218`,
contradiction-adjacent `59b87d04bfca4646e624f2057c58ed97b8f5b6df`.

## Finding

Actual behavior matches the claimed classification: the r58 comparator derives two verdicts from
committed matrix bytes, self-invokes over a lane snapshot, and discriminates honestly (rc 0) from
one omitted correction (rc 1) and from prose-only or wrong-count note text (rc 1), with rc 2
reserved for row-shape/CLI failures. This supports the frozen `R58-KIND` registry migration to
`gate` for this one row only.

Retained limitations (not repaired here): the comparator checks exact note presence in
`SCORECARD.md`, so adjacent contradictory prose is not parsed and rc 0 does not authenticate
execution; matrix parsing is positional; `findings_all` is compared as one column. These are
bounds on the classification, not new debt claims.

## Inventory / cleanup

Delivered under `.ufo/waves/round-59/w1/S59ExecDomain/`: `acceptance.py`, `acceptance-receipt.json`,
`trial/{receipt.json,honest.stdout.txt,honest.SCORECARD.md,one-correction-omitted.stdout.txt,one-correction-omitted.SCORECARD.md}`.
Scratch root `/fast/scratch/hyaku/souji-r59/S59ExecDomain/` held only this seat’s children and was
cleaned before yield; receipts above are the durable copy. No production, fleet, sibling or
historical-gate file was modified; no commits, pushes or jj mutations were made. Sibling working-tree
changes in `corpus/` predate and were not touched.
