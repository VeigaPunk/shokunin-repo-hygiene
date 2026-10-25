# MutC3Checks — mutation probes vs the C3 selftest harness

## Status
STATUS: PASS — all four assigned probes executed on the C3 harness bytes with a healthy baseline (rc 0, `cases=4 pass=4 control=FALSE-GREEN-REJECTED`); probe (b) killed, (d) deterministic, probe (a) SURVIVED (coverage/attack finding F1), probe (c) shows trap-only single-mechanism cleanup (finding F3). Lane bytes untouched.

## Evidence
- Revision: lane base e78ac7c4837b81b634db4a927605a751a7f006ba (branch master), confirmed via `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` this run.
- Bytes under test: delivery paths `tools/souji-pre-report-gate.sh` + `tests/fixtures/r27-pre-report-gate.sh` were absent from the lane worktree for the whole probe window (bounded watcher, 150 s, TIMEOUT; re-checked after probes: still absent). Tested the wave-dir drafts that L1 installs: `souji-shokunin/.ufo/waves/round-27/w1/souji-pre-report-gate.sh` sha256 `a0082bca1c926de12b5fad9326b17b83340b314cc05088acc1834c25a51cf04b` and `souji-shokunin/.ufo/waves/round-27/w1/r27-pre-report-gate.sh` sha256 `92c4be6ed0e1c46ef4869ab675a131954eee5ead79622a3dc536337bb79bc07e`. If L1's install differs from these bytes, results are `[INFERENCE]` for the installed copy only.
- Environment parameterization (documented, not a behavior mutation): every scratch copy differs from pristine ONLY in line 38 `WORLD_ROOT=/var/tmp/souji-r27-ExecFixtureC3Tests` → `/var/tmp/souji-r27-MutC3Checks/worlds`, because the frozen scratch root belongs to the builder seat and my bounds require scratch under `/var/tmp/souji-r27-MutC3Checks/`. Parameterized pristine copy sha256 `89ef34786e213df029cef830c8ebc5ac6571f2d3a5ec5a457b67c2b09021cbcf`.
- Detector (bounded, same for pristine/mutated): run `bash <fixture>`; record rc, last `cases=`/`FAIL` line, and residue under the worlds root (`find ... -mindepth 1 -maxdepth 1`).
- Baseline (pristine copy, run twice): rc=0, last line `cases=4 pass=4 control=FALSE-GREEN-REJECTED`, residue `[home]`; outputs byte-identical across the two runs (probe d).
- Restoration: mutants existed only in `/var/tmp/souji-r27-MutC3Checks/{mut-a,mut-b,mut-c1,mut-c2}`; lane drafts re-hashed after all probes — unchanged (`92c4be6e…`, `a0082bca…`, identical to pre-run). Scratch removed after the report was written. No installs/upgrades performed (none needed).

## Findings
1. F1 — (probe a, SURVIVED) Dropping case 2 (remote-mismatch) entirely leaves the harness green: rc 0 and it still prints `cases=4 pass=4 control=FALSE-GREEN-REJECTED`. Location: `souji-shokunin/.ufo/waves/round-27/w1/r27-pre-report-gate.sh:224` — quote: `printf 'cases=4 pass=4 control=FALSE-GREEN-REJECTED\n'`. The success line is a hardcoded literal; `assert_case` (:116) counts nothing, so any deleted case is invisible to the frozen counter. Expected per tasking: must NOT still print `cases=4` — observed: it does. Counter is gameable by case deletion (reported as ATTACK; no predicate change proposed).
2. F2 — (probe b, KILLED) Control is wired to the real tool: it first proves the control world red with the real gate (rc 1, `check-clean=FAIL`), then requires the stub to lie green-on-red; replacing the always-pass stub with a genuinely passing tool (exec of the real gate) yields `FAIL control stub-not-green rc=1`, harness rc 1, no success line. Location: control block `r27-pre-report-gate.sh:194-222`.
3. F3 — (probe c, hygiene) Cleanup is a single EXIT trap (:62 quote: `trap cleanup EXIT`, body :58-61 quote: `for w in $WORLDS; do rm -rf "$WORLD_ROOT/$w"; done`). Pristine runs do remove all five worlds ("trap still removes scratch" confirmed: residue `[home]` only). But both skip mutants — trap line removed (mut-c1) or body neutered (mut-c2) — leak `case1 case2 case3 case4 control` into the fixed scratch root while the harness still prints the success line and exits 0: hygiene regressions are invisible to the harness's own output and to the frozen counter. Also note: `$WORLD_ROOT/home` (:52) persists on every run, even pristine — cleanup never removes it.
4. F4 — (probe d, deterministic) Two consecutive pristine runs produced byte-identical stdout and rc 0; no commit SHAs, timestamps, or paths from the ephemeral worlds leak into the output.

## Attack log
| # | Mutation (smallest behavior-bearing point) | Expected | Observed | Verdict |
|---|---|---|---|---|
| a | Delete case-2 block (mkworld→assert_case, lines 163-173) | must NOT still print `cases=4` | rc 0; `cases=4 pass=4 control=FALSE-GREEN-REJECTED` still printed | SURVIVED (F1) |
| b | Stub heredoc → `printf '#!/usr/bin/env bash\nexec bash %q "$@"\n' "$TOOL"` (genuinely passing tool) | harness must fail | rc 1; `FAIL control stub-not-green rc=1`; no `cases=` line | KILLED |
| c1 | Remove `trap cleanup EXIT` | scratch still removed by trap | rc 0; worlds persist: `home case1 case2 case3 case4 control` | SURVIVED output contract; scratch leaks (F3) |
| c2 | Trap intact, rm loop neutered to no-op | trap still removes scratch | rc 0; same five worlds persist | SURVIVED output contract; scratch leaks (F3) |
| d | none (repeat run) | deterministic output | two runs byte-identical, rc 0 both | CONFIRMED |

Mutant fixture hashes (before → after): pristine `92c4be6ed0e1c46ef4869ab675a131954eee5ead79622a3dc536337bb79bc07e` → mut-a `2dbd62d43f3716c202d31863465e1fb60d8492d22354f79a3f7750d8b040e58b`, mut-b `b0ede246bf7d7cff10f588a068f1ea46bda8a5c5c2f011559f64304b40328629`, mut-c1 `619ecd92c9211a6c041d484e8e42a9d3aa60d0af2dd6fef7ec23d9ec90fcfc0e`, mut-c2 `d5083fe34cf6796f63222cf41b18b5c81b333dc872463ebfc40d551646f71752`. Lane bytes restored/unmodified (hashes above).

Commands (representative): `bash /var/tmp/souji-r27-MutC3Checks/pristine/tests/fixtures/r27-pre-report-gate.sh` (and per-mutant copies); detector excerpts above are verbatim from this run's captured outputs (`out-A.txt`, `out-B.txt`, `out-d1/d2.txt` in the now-removed scratch).
