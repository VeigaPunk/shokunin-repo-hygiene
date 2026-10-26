# SwarmConnector44 — r33 w1 separability check (C1-CURRENCY × C2-SCRATCH)

## Status

STATUS: PASS — separability confirmed from base bytes: exactly one live C2→C1 coupling (K07 via
`tools/souji-census.sh`), doubly guarded by C1's no-slash TMPDIR environment and C2's own slash-equality +
G6 rails; K08/K03 reach O5 only via `--selftest` paths their fixtures never execute; C1→C2 coupling is null
(no G-guard, O tool, or `c2-counter.py` reads SCORECARD.md). Deliverable:
`.ufo/waves/round-33/w1/deliver-cross-claim.md`.

## Evidence

All reads at base `6017a482e7068d5afb7617640198fbb0fe743357` in a scratch clone
(`/fast/scratch/hyaku/souji-r33/SwarmConnector44/c`, origin removed); counters/guards at frozen list-rev
`2d9bca55a9f042a2c9ed60a797a8069e74c41f46` via read-only `git show`.

- C2 repair sites: `tools/souji-census.sh:1990` (`st_worker_tmpdir` case pattern);
  `tools/souji-round9-selftest.sh:7` (mktemp under `${TMPDIR:-/var/tmp}`); literal `/var/tmp` at
  `tools/souji-evidence-cache.py:1295`, `tests/fixtures/r15-census-config.py:1545`,
  `tests/fixtures/r15-preservation-frozen/regenerate.py:138`.
- round9 reach: exactly one `round9` ref per tool, selftest-only — `tools/souji-verify.sh:1485`
  (`:1505 --selftest` dispatch), `tools/souji-vault-verify.sh:1720`, `tools/souji-quarantine.sh:1868`.
- C1 execution paths: `r17-jj-receipts.sh` invokes verify/vault/quarantine normal CLIs only (never
  `--selftest`), exports `TMPDIR="$T/tmp"` (`:183`); `r13-quarantine-bounds.sh` invokes
  `bash "$TOOL" --hold 0` (`:143`); `r17-census-hygiene.py` drives the census with `"TMPDIR": "/var/tmp"`
  (`:349`); `r16-landing-gate.py` names `tools/souji-census.sh`/r15 pin in literals and replays fixed rev
  `b410186`, "never runs tools/souji-census.sh" (`:52`); landing-gate selftest is fully synthetic
  (`souji-landing-gate.py:1900-2059`).
- C1 counter env: `TMPDIR=<mkdtemp>/tmp` — no trailing slash (`c1-counter.py:150-164` at list-rev).
- r15 pin at base covers `r14-census-boundary.py`, `r15-census-config.py`, `tools/souji-census.sh` — not
  `souji-round9-selftest.sh` (`tests/fixtures/r15-preservation-frozen/expected.json`).
- SCORECARD reach: `grep SCORECARD` over all 7 G-guard scripts, all 8 O-relevant tools,
  and `c2-counter.py` at list-rev → 0 matches (rc=1 each; only `c1-counter.py` references it).

## Findings

1. Live C2→C1 coupling: K07 alone. Its fixture executes `tools/souji-census.sh` bytes that O4 rewrites;
   C1 runs it only with no-slash TMPDIR, so a Q71-only repair cannot move `total=29 failed=0`; a non-Q71
   move fails C2 first (O4 slash-equality, G6 harm). Location: `census/round-33/c1-items.tsv` (K07 row),
   `tools/souji-census.sh:1986-1994`.
2. Dead couplings: K08 and K03 reach `souji-round9-selftest.sh` only through the tools' `--selftest`
   branches, which `r17-jj-receipts.sh` / `r13-quarantine-bounds.sh` never enter. Any Q71 O5 repair is
   invisible to them; no C2 leg observes their output. Location: `tools/souji-verify.sh:1485,1505`,
   `tools/souji-quarantine.sh:1868`, fixture invocation lines above.
3. Nominal-only: K06 names `tools/souji-census.sh`/r15 pin in expectation literals and historical replay at
   `b410186`; immutable history cannot move. K05/K06/K11/K21/K23 selftests run synthetic repos. Location:
   `tests/fixtures/r16-landing-gate.py:31-33,52,232-234`.
4. No reach: O1/O2/O3 files (`souji-evidence-cache.py`, `r15-census-config.py`, `regenerate.py`) are
   executed by no C1 item; the other 20 items intersect C2's reachable set nowhere. Location:
   `census/round-33/c1-items.tsv` files column.
5. C1→C2 is null: a restatement row touches only SCORECARD.md, and no G-guard, O tool, or the C2 counter
   reads SCORECARD.md (byte-verified, 0 matches each). The frozen `== Separability` design is accurate and
   slightly conservative (names K08 coupled; executable coupling is narrower). No amendment, no ATTACK.

## Attack log

None. The frozen separability clause reproduces at byte level; no predicate/target/counter defect observed.

## Deliveries

- `.ufo/waves/round-33/w1/deliver-cross-claim.md` (cross-claim separability analysis; full per-item
  predictions and counter manifestation).
- `.ufo/waves/round-33/w1/SwarmConnector44.md` (this report).

Scratch removed: `/fast/scratch/hyaku/souji-r33/SwarmConnector44` (clone + tmp, `rm -rf` after receipts
copied into the delivery file). No lane git/jj mutation; no tools installed this seat.
