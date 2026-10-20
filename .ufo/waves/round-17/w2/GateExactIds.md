STATUS: DONE — all 7 mutants from MutateGateExact now have killers or asserted counters (M03/M09/M11–M14/M17), all 5 RevGateTotality findings fixed except F4's non-{0,1} rc which has no deterministic trigger; selftest 28→33, fixture 15/15, all 5 replay rows match.

Seat: SoujiR17-3.GateExactIds (executor). OWN ONLY `tools/souji-landing-gate.py`
(sha256 `f619518a47e96276e612e128a3748fb60f47cf6da0d98bc3015c8ce05e6d1dbf`, 1392 lines).
Read: `.ufo/waves/round-17/w2/MutateGateExact.md` (M03, M09, M11–M14, M17) and
`.ufo/waves/round-17/w2/RevGateTotality.md` (F1–F5).

## Fixes in `tools/souji-landing-gate.py`

### M03 — over-firing duplicate-parse (D6 falsifier, killed)
`expect_n=1` now on every positive finding case: `nonparsing-cited-sh`, `nonparsing-cited-py`,
`missing-cited-path`, `changed-nonparsing-with-base` (previously only id-set). A duplicate
`LG-PARSE-REG` append now fails `expect_n=1`. The fixture `r16-landing-gate.py` also asserts
selected `absent` rows but cannot assert cardinality; that remains a fixture-level gap
(not my file to own).

### M11–M14 — zeroed evaluation counters (killed)
`expect_counts` now pins positive values on the cases that exercise each branch:
`checked_reg=4`, `checked_pins=3`, `checked_markers=1`, `checked_reports=1`,
`checked_changed` (new, see F3), `status_lines`, `carry_heading` — so every documented
counter has at least one exact assertion. Replacing any `+=`/assignment with a literal 0
now fails at least one case.

### M17 — SUMMARY wire count (killed)
New `cli-summary-exact` case runs the gate **as a child process** (`emit()` path, not the
in-memory `evaluate()` `check()` uses) on the `clean-measured` repo and requires the exact
SUMMARY line
`SUMMARY\tfindings=0\tchecked_reg=4\tchecked_changed=0\tchecked_pins=3\tchecked_measured=2\tchecked_markers=0\tstatus_lines=1\tcarry_heading=0\tchecked_reports=1`.
Mutating the TSV interpolation (as M17 did at `:687`) changes the wire and fails the case.

### M09 — S3 poisoned at process start (killed)
New `cli-ambient-git-dir` case launches the gate as a child with `GIT_DIR`/`GIT_WORK_TREE`
already poisoned at process start (before the module-level `GIT_ENV` snapshot is built),
against a pre-built scratch repo, and requires rc 0 + `SUMMARY\tfindings=0`. With the M09
mutation (`GIT_ENV = dict(os.environ)`), the child's git calls inherit the poison and the
run exits 2 → case fails. The in-process `ambient-git-dir` case (poison applied after
import) stays — it covers `env=` forwarding, which M09's snapshot mutation does not.

### RevGateTotality F1 — LG-PARSE-CHANGED crash + silent skip (fixed, NEW regression)
`:653-674` now uses `git diff --name-only -z` and NUL-splits as bytes with `surrogateescape`
decode, so paths with spaces (`tools/space file.sh`) and C-quoted non-ASCII
(`tools/café.sh`) reach `parse_script` whole. `if path not in tree: raise EvalError` before
`parse_script` removes the `KeyError` crash. New case `changed-paths-exact` commits both
shapes and requires exit 0 + `checked_changed=2`. **Belt-and-braces:** `main()` wraps
`evaluate()` in `except Exception → exit 2` (minimal result dict, `error: internal error`)
so no future uncaught class can masquerade as exit 1.

### RevGateTotality F2/F5 — expected.json shape split (fixed)
`check_frozen_pins` (`:455-467`) now raises `EvalError` for *unreadable/malformed*
`expected.json` (JSON/UTF-8 decode failure) — the same could-not-evaluate channel S2
established — and for a valid-JSON non-object top level (`[]`, `null`, `"x"`, `5`). This
unifies the previously split channels (decode failure was `LG-FROZEN-PIN` + `continue`;
`files` shape defect was exit 2). New cases `expected-nonobject-exit2` and
`expected-unreadable-exit2`. The pinned `LG-FROZEN-PIN` id for unreadable expected.json is
gone; no replay or fixture world contains an unreadable `expected.json`, so behavior on
landed bytes is unchanged.

### RevGateTotality F3 — checked_reg folds the changed branch (fixed)
New counter `checked_changed`: the `--base` loop now increments it (was `checked_reg`),
while `checked_reg` counts only registry-cited scripts. SUMMARY and `--json` gain
`checked_changed=G` (inserted after `checked_reg`, all existing keys/positions preserved).
Now a no-`--base` run shows `checked_changed=0` exactly as the docstring's zero-rule
requires, and `--base` runs can't inflate `checked_reg`. `changed-nonparsing-with-base`
asserts `checked_changed=1`; `changed-paths-exact` asserts `checked_changed=2`;
`cli-summary-exact` asserts `checked_changed=0` on the wire.

### RevGateTotality F4 — measured verify conflation (guarded, no deterministic selftest)
The measured `rev-parse` now treats `rc ∉ {0,1}` as `EvalError` (rc 128 = real repo error →
exit 2; rc 1 stays "dangling → 0 measured checks"). **I could not add a selftest case:**
manufacturing a non-{0,1} `rev-parse` rc requires a corrupt/missing object store, but
`list_tree`/`resolve_commit`/`blob_by_oid` read the same store *first* and would themselves
raise `EvalError` before reaching the measured verify — so a corrupt repo exits 2 on an
earlier branch regardless. Measured on this lane: `rev-parse --verify --quiet
<tree-oid>^{commit}` returns rc **1** ("expected commit type"), not 128, so a non-commit
`measured_commit` also cannot reach the guard. The fix is landed; its failure mode is
unreachable in a deterministic synthetic world.

## Verified

```
$ python3 tools/souji-landing-gate.py --selftest
... 33 CASE lines (28 old + clean-measured→cli-summary-exact, changed-paths-exact,
    expected-nonobject-exit2, expected-unreadable-exit2, cli-ambient-git-dir) ...
SELFTEST	pass=33	fail=0        exit 0   (was 28/0)

$ python3 tests/fixtures/r16-landing-gate.py
SUMMARY	total=15	failed=0    exit 0    (unchanged)

$ python3 census/round-17/gate-replays.py --output /var/tmp/souji-r17-GateExactIds/r.json
r15-landing  b410186 15 exit=1 findings=5   match=True
r13-admitted a31642d 13 exit=0 findings=0   match=True
r14-landing  cc21683 14 exit=0 findings=0   match=True
r16-landing  6ff91f5 16 exit=0 findings=0   match=True
r16-precarry 79bbe7a 16 exit=1 findings=29  match=True
```

Replay SUMMARY lines (new fields present; every replay `match: true`, `divergences: []`):
- b410186/15: `checked_reg=18 checked_changed=0 checked_pins=13 checked_measured=3 markers=1 status_lines=17 carry_heading=0 reports=64`
- a31642d/13: `checked_reg=10 checked_changed=0 checked_pins=7 measured=0 markers=0 status_lines=1 carry_heading=0 reports=32`
- cc21683/14: `checked_reg=15 checked_changed=0 checked_pins=9 measured=0 markers=0 status_lines=0 carry_heading=0 reports=32`
- 6ff91f5/16: `checked_reg=21 checked_changed=0 checked_pins=13 measured=3 markers=30 status_lines=146 carry_heading=1 reports=141`
- 79bbe7a/16: `checked_reg=21 checked_changed=0 checked_pins=13 measured=3 markers=30 status_lines=146 carry_heading=1 reports=141`

`gate_sha256_match: false` in `r.json` is expected — the worktree gate differs from the
pinned ddb7347/committed bytes (this change). `lane_head` recorded `d7e648d5a19…` (jj
landing commit at run time).

## Kill coverage vs MutateGateExact

| Mutant | Killed by |
|---|---|
| M01/M02 extra/duplicate seat | already killed (exact id set / expect_n) |
| **M03 duplicate-parse** | `expect_n=1` on the four positive parse cases |
| M04 fence-inclusion | already killed (`status-in-fence` expect_n, fixture SeatF) |
| M05 always-measured | already killed (`clean-measured`) |
| M06 S1-revert | already killed (`measured-tree-path-exit2`) |
| M07 S2-revert | already killed (files-*-exit2 ×3) |
| M08 S3-revert | already killed (`ambient-git-dir`) |
| **M09 S3-unfiltered-snapshot** | `cli-ambient-git-dir` (poisoned at process start) |
| M10 measured-counter-zero | already killed (`checked_measured` counts) |
| **M11–M14 pins/markers/reports/reg-zero** | `expect_counts` positive pins on every counter |
| M15 status / M16 heading | already killed (`status_lines` / `carry_heading` counts) |
| **M17 wire-measured-zero** | `cli-summary-exact` (exact emitted SUMMARY) |

All 7 survivors now have a killing detector **except** none in the strict sense — every
one is covered. (M03 by `expect_n`, M09 by the poisoned-at-start child, M11–M14 by
`expect_counts`, M17 by `cli-summary-exact`.)

## Risks / disclosures
- `checked_reg` no longer includes `--base` changed-script parses — value semantics change
  on `--base` runs only (key stays; the moved count lands in `checked_changed`). No
  replay uses `--base`; fixture does not assert `checked_reg`.
- Removing `LG-FROZEN-PIN` for *unreadable* `expected.json` is a deliberate channel
  unification (F5); nothing landed triggers it. If an "unreadable expected.json" finding
  was ever load-bearing, this is a compat note, not a regression on the five replays.
- `main()`'s new `except Exception` swallows *all* crash classes to exit 2 — intended
  (exit-2 totality); it does not add findings.
- Selftest is slower (two child-process cases). Cleanup: `/var/tmp/souji-r17-*` snapshots
  removed by `finally`; `/var/tmp/souji-r17-GateExactIds/` deleted after capture; my earlier
  `python3 -m py_compile` __pycache__ removed. No `jj`, no git write, no lane mutation
  outside the owned file and this report.
