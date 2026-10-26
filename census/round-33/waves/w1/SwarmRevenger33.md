# SwarmRevenger33 — r32 C2 T08 mechanism (revenger seat, w1)

## Status

STATUS: PASS — the T08 mechanism is reconstructed from committed bytes and reproduced by execution: both registered
gates (G1 `r22-result-oracle`, G2 `r22-mutation-adequacy`) turn red on the r32 tool bytes alone, through one
conjunct that compares the live `tools/souji-evidence-cache.py` sha256 with the digest frozen in the r21 receipt;
revert restores both; under Q73 no committed regenerator exists for that pin, so revert is the only clean repair.

## Evidence

All runs executed by me in a scratch clone at `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`
(`/fast/scratch/hyaku/souji-r33/RevengeT08Revert/`, removed after the runs; `git -C <clone> rev-parse --show-toplevel`
printed the clone before any write). The six relevant files are byte-identical at base `6017a48` and at `2d9bca55`
(`git diff --stat 6017a48 2d9bca55 -- <paths>` empty).

| # | command (cwd = clone) | output |
|---|---|---|
| 1 | patch applied: `git -C <lane> diff 7a6667c 98e5203 -- tools/souji-evidence-cache.py \| git -C c apply` | worktree sha256 `6b826da2b65f9901f40b967fa296a164ef2bd0813aa474c0e8a5e760f65e7297` = r32 landing blob `1578e419` |
| 2 | `python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py` (r32 bytes) | **rc=1**, `total 258 pass 256 fail 2`, `R22-RESULT-CONTRACT`; failing `positive/clean-cache-demonstration`, `positive/cache-transient-path-and-time` |
| 3 | `python3 -B census/round-22/mutation-adequacy.py` (r32 bytes) | **rc=1**, `pristine {exit 1, pass 256, fail 2}`, `killed 59 survived 0`, 7 `disagreeing_with_expect` |
| 4 | same two commands at base bytes (before patch) | G1 rc=0 258/258; G2 rc=0 pristine fail 0, `killed 52 survived 7`, no disagreements |
| 5 | revert to base bytes, same two commands | G1 rc=0 258/258; G2 rc=0 pristine fail 0, 52/7 |
| 6 | r32 bytes + one-word docstring edit only (`under`→`beneath`, sha `d5a516b6…`) | G1 rc=1, same two vectors → the pin is over bytes, not behaviour |
| 7 | in-memory `payload["gate"]["sha256"] := live sha`, `summarize_result` | `as-pinned matched=False` → `replaced matched=True`; every other check already matched → `:522` is the sole failing conjunct |
| 8 | `python3 -B tests/fixtures/r14-evidence-cache.py` (r32 bytes, G3) | rc=0, `fixture: 22/22 checks passed` → G3 carries no byte pin |
| 9 | `run-acceptance.py:522` weakened to `and isinstance(gate, dict)`, then G2 | rc=2, `could-not-evaluate: anchor count 0: 'and isinstance(gate, dict) and gate.get'` |

Pin chain over committed bytes (revision `2d9bca55`), with pointers:
`census/round-14/cache-demonstration.py:229` records `sha256_file(gate)` into the demo's `gate.sha256` (wired from
`census/round-21/run-acceptance.py:338`); that stdout is frozen in `census/round-21/final-out-S1.json` (record
`:2515`, stdout `:3383`/`:3384`, gate `sha256` `:3155`, `sha256_after` `:3165`, `gate_sha256_after` `:3169`);
`tests/fixtures/r22-result-oracle.json:3-7` pins the receipt (`bc53a752…`) and inventory (`8b7b1cd8…`) bytes, checked
by `tests/fixtures/r22-result-oracle.py:31-35`; `:87-91` feeds the pinned stdout and the live `ROOT` into
`run-acceptance.py:503` `sha256_bytes(read_regular(root / "tools" / "souji-evidence-cache.py"))` and `:522`
`gate.get("sha256") == gate_sha`, folded at `:536`; `census/round-22/mutation-adequacy.py:266,276` grades the same
oracle in memory and requires `pristine['fail'] == 0`.

## Findings

1. **T08 red is one byte-equality, not a behaviour change.** `census/round-21/run-acceptance.py:503` reads the live
   worktree copy of `tools/souji-evidence-cache.py` (`read_regular`, `:217-220`), and `:522` requires its sha256 to
   equal the digest inside the frozen r21 cache-demo payload (`dd279ba9…39d6`, `census/round-21/final-out-S1.json:3155`).
   A one-word docstring edit reddens G1 identically (§Evidence 6), and substituting the live digest in memory makes
   the pinned vector match (§Evidence 7).
2. **G2 red is collateral, not independent.** `census/round-22/mutation-adequacy.py:276` requires a green pristine
   run; with the tool changed, `pristine fail=2` and the 7 `equivalent` mutants are falsely reported killed
   (`:270` `killing_vectors` now lists only the two broken positives). The gate is adequate — every one of its 59
   mutants remained killed-or-surviving consistently except through the broken pin — but its reading is not
   independent of G1's.
3. **Only three gate-time consumers read those bytes.** The Q73 sweep
   `git grep -l "souji-evidence-cache.py" 2d9bca55 -- tests/fixtures census` yields 85 files; the readers are
   `census/round-21/run-acceptance.py:503`, `tests/fixtures/r22-result-oracle.py:87-91`, and
   `census/round-22/mutation-adequacy.py:266`. `tests/fixtures/r14-evidence-cache.py` (G3) runs the CLI and asserts
   exits (`22/22` on the r32 bytes); `tests/fixtures/r20-input-binding.py` stubs `run_demonstration` (`:575`,`:682`);
   `tools/souji-landing-gate.py` has no reference. Every other `dd279ba9…` hit is a historical record no gate reads.
4. **Q73 repair paths: revert is the only clean one here.** Q73 (`corpus/QUALITY.md:178`) allows "regenerated with its
   own committed script at the candidate, or the tool edit is reverted". No committed script writes
   `tests/fixtures/r22-result-oracle.json` (`git grep -n "r22-result-oracle.json" -- '*.py' '*.sh'` → only
   `census/round-22/mutation-adequacy.py:12`, an input option); the sole committed regenerator is
   `tests/fixtures/r15-preservation-frozen/regenerate.py` (`:2`, re-pins `tools/souji-census.sh`);
   `census/round-21/run-acceptance.py` can only create a *new exclusive* receipt for the revision it replays, and its
   receipt bytes are themselves pinned by the oracle (`r22-result-oracle.py:31-35`). Revert is measured green
   (Evidence 5) and is what `9da5e9a` landed (blob back to `82de0e07`); its receipt states the cause at
   `census/round-32/records/a2-repairs.txt:30-38`.
5. **Weakening the consumer is structurally blocked.** Dropping `run-acceptance.py:522` makes G2 exit 2
   (`anchor count 0`, `census/round-22/mutation-adequacy.py:261-265`) because three mutants anchor on that text
   (`:100`,`:121`,`:190`). Measured (Evidence 9).
6. **Guard-rule precision.** G1's last digit-bearing line is identical green and red (`"total": 258`); only its exit
   code separates them, while G2 differs in both (`"survived": 7 → 0`). A reading that keys on the last line alone
   is inert for G1.
7. **C2 feasibility risk (reported, no amendment proposed).** O1's repair is the tool's bytes, so O1 PASS and
   G1/G2 green cannot coexist with the base pin; by Finding 4 no committed regenerator exists for the r22 pin at the
   prereg commit. [INFERENCE] a regenerator authored this round would not be "its own committed script". Reproduced
   states: O1 repair → G1 rc1 / G2 rc1 (Evidence 2-3); revert → both green, O1 at its base FAIL.

## Attack log

**ATTACK-T08-PIN-MOVABLE** (reproduced in scratch; frozen predicate untouched, no amendment proposed).
With the r32 tool bytes kept in place, I hand-edited the pin and both gates read as base:
(1) replace `dd279ba9…`→`6b826da2…` inside the `clean-cache-demonstration` record's stdout in
`census/round-21/final-out-S1.json` (new receipt sha `dc13b8d938ac0d08…`); (2) set
`tests/fixtures/r22-result-oracle.json`'s `source_receipt_sha256` to it; (3) replace the same digest in the three
fabricated case stdouts (`r22-result-oracle.json:4955,4962,4969`). Result: G1 `rc=0 258/258`,
G2 `rc=0 pristine fail 0, 52/7, disagreeing []` — indistinguishable from base while the tool's bytes changed.
The only trace is the receipt field `oracle_sha256` (`750946f4…` vs committed `970b7362…`), and no committed
instrument compares it: the sweep for `970b7362` hits only round-22 receipts that print it, one lesson, and the r26
assimilation `manifest.sha256` of an exported snapshot. Q73 forbids the edit in words; it is not detected
mechanically. Consequence for this round: `harm=0` is reachable without a real re-pin, so G1/G2 alone cannot certify
that a landed O1 repair kept the r21/r22 measurement meaning.

## Deliveries

- `.ufo/waves/round-33/w1/deliver-c2-t08-mechanism.md` — full mechanism, pin chain, reproduction receipts,
  Q73 path table, attack state.
