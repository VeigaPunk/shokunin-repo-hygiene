# S82ExecC1 — C1 falsification (reproduce from committed bytes)

## Verdicts

- **c1-after.txt (r82 counter, 32 rows): REPRODUCED yes.** All 32 ROW lines match byte-for-byte including
  full fixture line `F0=6436db6a… R1=f28736a9… R2=afc4ceb7… R3=bdea7114… R4=0440ea31… R5=d1ed98f4…`
  and `SUMMARY rows=32 mismatches=0 accepted=0 refused_true=0 errors=0`, EXIT=0. NF-F/NF-G/NF-H/NF-I REFUSED,
  PF-1 MOVED, TF3/TF4/TF5 MOVED — all match.
- **c1-K-a-r81-counter.txt: REPRODUCED yes.** `SUMMARY rows=32 mismatches=2 accepted=2 refused_true=0 errors=0`,
  EXIT=1; NF-F and NF-G both `expect=REFUSED/- got=MOVED … match=no`, all else yes. r81 counter accepts the
  own-tree decoys; the before-delta is exactly these 2.
- **c1-K-b-owntree-dropped.txt: REPRODUCED yes.** SHA `87a5e037…` matches bind line;
  `SUMMARY mismatches=2 accepted=2`, EXIT=1; NF-F/NF-G `got=MOVED match=no`, NF-H/NF-I REFUSED.
- **c1-K-c-suffix-last-component.txt: REPRODUCED yes.** SHA `8b3ade7f…` matches bind line;
  `SUMMARY mismatches=2 accepted=2`, EXIT=1; accepts exactly **NF12c** and **NF-I**
  (`NF12c … got=MOVED/… match=no`, `NF-I … got=MOVED/… match=no`), all other rows yes.
- **c1-regress-r78.txt (r82 counter): REPRODUCED yes.** `SUMMARY items=22 resolved=22 …`,
  `FORGE-SUMMARY forged=12 matched=12 accepted=0`, EXIT=0.
- **c1-regress-r77.txt (r82 counter): REPRODUCED yes.** `SUMMARY items=35 resolved=35 …`,
  `FORGE-SUMMARY forged=7 matched=7 accepted=0`, EXIT=0.
- **c1-regress-r79-harness.txt: REPRODUCED yes.** `SUMMARY rows=9 mismatches=0 accepted=0 errors=0`, EXIT=0.
- **c1-regress-r80-harness.txt: REPRODUCED yes.** `SUMMARY rows=18 mismatches=0 accepted=0 errors=0`, EXIT=0.
- **c1-regress-r81-harness.txt: REPRODUCED yes.** `SUMMARY rows=25 mismatches=0 accepted=0 refused_true=0
  errors=0`, EXIT=0.

Digest checks: harness `a45a9022…`, r82 counter `cbfdc07c…`, population `c7d4a1ef…`, r81 counter `ca97b984…`,
K-b variant `87a5e037…`, K-c variant `8b3ade7f…` — all match the `# bind` lines in the committed receipts.
Chronology: `records/freeze-check-at-P.txt` findings=3 (C0/C1/C2) disclose the M1 slip in-band; P(1cb7c7d1),
F(d302b4f3), W1(f5bc4197), W2(73110f6f), A(9881676a) all present in `git log` in order.

## ITEM-line diff (r81 counter vs r82 counter, same `--rev e65538e7…`)

r77 (35 ITEMs) and r78 (22 ITEMs): **zero verdict moves.** Every ITEM status is identical under both
counters (including all MOVED: P04/P05/P07/P25/P26/P29/P30/P31/P34/P35 and L11/L12/L15/L21). This is the
expected result: both ledgers' MOVED targets live under `census/round-<N>/`, never in the token's own tree,
so the new `_owntree_ok` gate (which only fires on own-tree prefixes) cannot change them.

## Per-token analysis for every MOVED ledger row (r82 `_capture_ok`/`_owntree_ok`, c1-pointer-counter.py:299-319)

`_capture_ok` = target-after-`round-<N>` matches `^(waves/|wave/|records/wave-<w>/)(.+)$` with the suffix a
whole-component suffix of the token's below-`round-<N>` tail; `_owntree_ok` = identical tail or `_capture_ok`.

| item | token → target | subtree | suffix check |
|---|---|---|---|
| P04 | `.ufo/waves/round-32/a2w1/SwarmExecutor08.md` → `census/round-32/waves/a2w1/SwarmExecutor08.md` | `waves/` | `a2w1/SwarmExecutor08.md` == token tail ✓, `_capture_ok=True` |
| P05 | `.ufo/waves/round-33/make-spec-w2.py` → `census/round-33/waves/make-spec-w2.py` | `waves/` | `make-spec-w2.py` == tail ✓, True |
| P07 | `.ufo/waves/round-61/w1/S61ExecRealRecord/erratum-evidence.txt` → `census/round-61/wave/w1/S61ExecRealRecord/erratum-evidence.txt` | `wave/` | `w1/S61ExecRealRecord/erratum-evidence.txt` == tail ✓, True |
| P25 | `…round-32/a2w1/SwarmExecutor16.md` → `census/round-32/waves/a2w1/SwarmExecutor16.md` | `waves/` | tail ✓, True |
| P26 | `…round-32/a2w1/SwarmReviewer13.md` → `…waves/a2w1/SwarmReviewer13.md` | `waves/` | tail ✓, True |
| P29/P34 | `…round-32/a2w1/SwarmCritic20.md` → `…waves/a2w1/SwarmCritic20.md` | `waves/` | tail ✓, True |
| P30/P35 | `…round-32/a2w1/SwarmReviewer27.md` → `…waves/a2w1/SwarmReviewer27.md` | `waves/` | tail ✓, True |
| P31 | `.ufo/waves/round-62/w1/S62ConnectorOverlap` → `census/round-62/wave/S62ConnectorOverlap` | `wave/` | `S62ConnectorOverlap` is a suffix of `w1/S62ConnectorOverlap` ✓ (partial suffix, True) |
| L11 | `.ufo/waves/round-42/w3` → `census/round-42/waves/w3` | `waves/` | `w3` == tail ✓, True |
| L12 | `.ufo/waves/round-44/w1-results.json` → `census/round-44/waves/w1-results.json` | `waves/` | tail ✓, True |
| L15 | `.ufo/waves/round-54/w1/S54critic01.md` → `census/round-54/wave/S54critic01.md` | `wave/` | `S54critic01.md` is a suffix of `w1/S54critic01.md` ✓ (partial, True) |
| L21 | `.ufo/waves/round-69/w1-results.json` → `census/round-69/records/wave-w1/w1-results.json` | `records/wave-w1/` | tail ✓, True |

For all 14 rows `_owntree_ok=True` via `_capture_ok` (none is own-tree: prefix is `census`, not `.ufo/waves`),
and the census-branch gate at `c1-pointer-counter.py:361-371` passes, so the MOVED verdict is retained. No row
flips under either check — consistent with the zero ITEM diff above.

## Findings

- HIGH: none. MEDIUM: none. LOW: none — every frozen predicate on C1 held under independent re-execution.
- Note (not a finding): this seat's first harness invocation via `setsid timeout …` swallowed ROW/SUMMARY
  stdout (only the `#` headers appeared); re-running without `setsid` reproduced everything. The frozen
  invocation in the spec does not use `setsid` on the harness itself, so this is a seat-side artifact, not a
  lane defect.

## Commands run

All from `/home/vgpnk/Projects/shokunin/souji-shokunin`, each under `timeout -k 5 120`, with a fresh empty
`--work` under `/fast/scratch/hyaku/souji-r82/S82ExecC1/<name>` and `2>&1; echo EXIT=$?`:

1. `python3 -B census/round-82/c1-false-row-harness.py --counter census/round-82/c1-pointer-counter.py --lane … --fleet-root … --work …/c1a`
2. `python3 -B census/round-82/c1-false-row-harness.py --counter census/round-81/c1-pointer-counter.py --lane … --fleet-root … --work …/c1b`
3. `python3 -B census/round-82/c1-false-row-harness.py --counter census/round-82/controls/variants/c1-K-b-owntree-dropped.py --lane … --fleet-root … --work …/kb`
4. `python3 -B census/round-82/c1-false-row-harness.py --counter census/round-82/controls/variants/c1-K-c-suffix-last-component.py --lane … --fleet-root … --work …/kc`
5. `python3 -B census/round-82/c1-pointer-counter.py --root … --rev e65538e7… --fleet-root … --population census/round-78/c2-population.tsv --ledger census/round-78/c2-pointer-ledger.tsv --forge census/round-78/c2-forge-r78.tsv`
6. Same with `census/round-77` population/ledger and `census/round-78/c2-forge-r77.tsv`.
7. Same as 5–6 with `census/round-81/c1-pointer-counter.py` (ITEM diff).
8. `python3 -B census/round-79/c2-false-row-harness.py --counter census/round-82/c1-pointer-counter.py --lane … --fleet-root … --work …/r79`
9. `python3 -B census/round-80/c1-false-row-harness.py --counter census/round-82/c1-pointer-counter.py --lane … --fleet-root … --work …/r80`
10. `python3 -B census/round-81/c1-false-row-harness.py --counter census/round-82/c1-pointer-counter.py --lane … --fleet-root … --work …/r81`
11. `sha256sum` on the 6 bound files; `git log --oneline` chronology; Python `_capture_ok`/`_owntree_ok` re-derivation with `ROUND = re.compile(r"(?:^|/)round-([0-9]+)(?:/|$)")` (c1-pointer-counter.py:106).

## Files written

- `.ufo/waves/round-82/w1/S82ExecC1.md` (this report).
- Scratch only under `/fast/scratch/hyaku/souji-r82/S82ExecC1/`.
- No tool installs (nothing was needed; system python3/git sufficed — no tool/version record required).
