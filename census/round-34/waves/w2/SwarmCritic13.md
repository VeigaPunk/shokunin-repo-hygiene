# SwarmCritic13 — r34 w2 seat report (AttackE14a)

## Status

Assignment complete: adversarial falsification of W1's C1 E14a finding. Result: **W1
CONFIRMED with sharpened root cause** — E14a's frozen argv pins a malformed 41-hex object
name (transcription defect in the frozen list), the mismatch is permanent at every
revision, no honest do-nothing route exists, and the only Q76-conforming repair is an
argv-correction restatement of one specific shape (cause `315422ba…`, restated exit 128,
restated statement binding the "exists on disk, but not in" wording). Full detail in
`AttackE14a.md`.

## Evidence

- Frozen row verified at list rev `2b0171e2…` (`c1-items.tsv:54`): hash
  `a65fac98964b445758e94c8057280c9a19d302ff8` measured at **41 chars**; working tree ==
  list rev (defect genuinely frozen).
- W1's three committed readings agree byte-for-byte (`controls-c1-do-nothing.txt`,
  `deliver-c1-do-nothing-check.txt:43`, `deliver-q76-honoring.txt:47`): `rc=128
  expect_exit=128 predicate fails last=fatal: invalid object name …`.
- Executed read-only probes in the lane repo:
  - 41-hex hash absent even from the main object store; 40-hex
    `a65fac98964b445758e94c805728c9a19d302ff8` exists (commit "a65fac9 round-23 verifier
    spot-check") and is an ancestor of both base `9c76c72…` and list rev `2b0171e2…`.
  - `git cat-file -e <true>:tests/fixtures/r24-size-census.py` → `fatal: path … exists on
    disk, but not in 'a65fac…c9a1…'`, rc 128 — does NOT match frozen statement
    `path .* does not exist`; fixture confirmed TRACKED-AT-BASE.
  - `SCORECARD.md:63` heading carries the correct 40-hex hash; `:67` cell documents the
    intended probe. Zero prior `SCORECARD.md:67` correction pointers at base.
- Executed bounded synthetic probe (counter's exact clone mechanics, git 2.56.0,
  `/fast/scratch/hyaku/souji-r34/E14a/`, removed after): both message forms reproduced
  byte-for-byte; 77 MB lane `.git` precluded a full-lane clone under the 50 MB ceiling.
- Cause-candidate verification for the conforming restatement: `315422ba9970f03c27f8a9184446783b7fcdf0a7`
  is an ancestor of the list rev, has parent `d3666c3ef291c0c6c7827ffcfb58471c4b8d54f7`,
  and the exact bound line is PRESENT at the cause / ABSENT at the parent.

## Findings

1. W1's E14a mismatch is real and not a measurement artifact (exit agrees 128==128;
   predicate fails on "invalid object name"; load-independent).
2. Root cause is stronger than W1's "missing/unresolvable pinned revision" label: a 41-hex
   malformed name in the frozen argv (extra `0` after `5728` vs the true commit documented
   in the bound cell's own heading). It fails identically at every revision; no repo state
   can ever make the frozen argv resolve.
3. The "obvious" hash repair alone is insufficient: with the true hash the run prints
   "exists on disk, but not in" (fixture tracked at base → on disk in the counter's
   checkout), which never matches the frozen statement — same trap as sibling E09a.
4. Honest-route audit under the frozen judge (`c1-counter.py:237-312`, preregistration
   lines 48-57): value-drift restatement provably impossible (original predicate never
   holds at any commit); exactly one argv-correction restatement shape conforms (details
   in AttackE14a.md); RESULTS/ANYLINE/COUNT alternatives unavailable; ref-gaming and
   fixture-deletion escapes fail other frozen clauses (E14c, exit/statement match).
5. W1's blockage claim stands; my seat adds the root-cause precision, the impossibility
   proof for value-drift, the hash-repair trap, and the exact conforming restatement shape.
   Corroborating overlap: sibling E15c shares the same corrupted 41-hex hash (different
   cell/statement/exit; its own seat's target — not claimed here).

## Attack log

Read-only lane inspection only; no frozen artifact, ref, or working-tree file modified;
nothing committed/pushed. One small synthetic probe in item scratch (created and removed).
No subagents dispatched (leaf seat). No tools installed. Lane `.git` size (77 MB) noted as
the reason the full-lane clone probe was replaced by the synthetic equivalent.

## Deliveries

- `.ufo/waves/round-34/w2/AttackE14a.md` — full attack report (Status / Evidence /
  Findings / Attack log / Deliveries).
- `.ufo/waves/round-34/w2/SwarmCritic13.md` — this seat summary.
