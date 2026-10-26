# SwarmMutationTester33 — C2 counter mutation battery (souji r31, wave 1)

## Status
STATUS: PASS — 10 mutants of `census/round-31/c2-counter.py` probed in scratch; 9 killed (3 by the committed do-nothing row, 1 by the committed junk row, 5 by constructed scratch states), 1 survivor (m8) reported as a coverage finding. Lane bytes untouched: `sha256(census/round-31/c2-counter.py)` = `7f912cc6bae10c4a1ca739c5ce98ee2001cbb1f9ca71b51a5c1b048b066a1281` before and after the battery; `git status --porcelain` on the file empty. No tools installed (python3 + git sufficed).

## Evidence
- Detector (bounded): `python3 -B census/round-31/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <REV> --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --fleet-root /home/vgpnk/Projects/shokunin --scratch <dir>`; observable = (exit rc, `SUMMARY` line). Mutants are scratch copies; every run used a private `--scratch` under `/fast/scratch/hyaku/souji-r31/MutateC2Counter/` and `TMPDIR` set per the 2026-10-25 directive. The lane working tree was never read by the counter (it exports via `git clone --no-local`) and never written by me.
- Pristine baseline on the do-nothing state (rev `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`): rc=1, `SUMMARY fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same rev=1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525` — byte-reproduces the committed row `census/round-31/records/controls.tsv:3`. Detector validated.
- Do-nothing battery (all 10 mutants, same state): m2a `fp=15 real=0`, m3 `fp=0 real=0`, m4a `fp=15 real=0` → killed; m1, m2b, m4b, m5, m6, m7, m8 byte-identical to pristine (`diff` empty) → survive, pushed to constructed states.
- Constructed states (lane clones in scratch, origin removed, throwaway identity via `git -C <clone> -c`; base `9f17a1e…` unless noted):
  - S1 `8f4f5fe1a414d80f185b04c26eb4194c8666b297` — 30 `.ufo/waves/round-26/w1/*.md` deleted at REV.
  - S2 `d70a85537e3fb898b59b150a3061a24b44c8b07e` — fake `tests/fixtures/r31-landing-gate-precision.py` printing all G PASS + `control=FALSE-GREEN-ACCEPTED`.
  - S3v2 `a8ec7d47a27539fa0a6f3716a8b1981e857f4d35` — fake fixture whose `/base/` branch prints G1–G8 FAIL, G2 PASS, G9 FAIL, G10 PASS (RED all FAIL, GREEN broken only at G9); rev branch all PASS + `FALSE-GREEN-REJECTED`.
  - S4 `5a126a1423693a0a9a1fb5757a9af4986fe7ee6a` — `tests/fixtures/r19-carry-wrap.py` SUMMARY print gains ` mut=1` at REV; rc unchanged (0).
  - J `a21d57794f42fda0c40f9c16f414edacd94e0517` — junk replica: stub gate printing `checked_reports=495` and no findings + fake fixture all-PASS + `FALSE-GREEN-REJECTED`. J-true printed `fp=0 real=0 cne=0 r26=495 fixture=ok redarm=fail regress=differs` — exactly the committed junk row's shape (`controls.tsv:11`).
  - S5v2 `9f899432b7b25b56f587e376e7359c778c33687c` — base content edited so `corpus/lessons/round-23-verifier-spotcheck.md:28` cites `census/round-3/garbage-census.out:3–5` (en dash); run with `--rev == --base` so both counters read the edited content.
- Restoration: mutants and states live only in scratch; lane file hash unchanged (above). Scratch removed at end of seat.

## Attack log
| # | mutant (single edit to a scratch copy) | do-nothing state | junk row/replica | constructed state | verdict |
|---|---|---|---|---|---|
| 1 | m1-revcontent: LANE leg `--rev a.base` → `--rev a.rev` | identical | identical (stub ignores `--rev`) | S1: true `r26=466` vs mutant `r26=436` | KILLED (S1) |
| 2 | m2a-noreal: `if key in REAL:` → `if key in ():` | `fp=15 real=0` vs committed `fp=13 real=2` | — | — | KILLED (do-nothing row) |
| 3 | m2b-hardreal: `real = len(real_seen)` → `real = 2` | identical | committed row records `real=0`; replica: true `real=0` vs mutant `real=2` | — | KILLED (junk row) |
| 4 | m3-stderr: scan `err` instead of `out` for `LG-DANGLING-PTR` | `fp=0 real=0` | — | — | KILLED (do-nothing row) |
| 5 | m4a-stripsrc: strip the source, not the token | `fp=15 real=0` | — | — | KILLED (do-nothing row) |
| 6 | m4b-nostrip: use raw `f[1]`, no strip | identical | — | S5v2: true `fp=13 real=2` vs mutant `fp=14 real=1` | KILLED (S5v2) |
| 7 | m5-acceptfga: control accepted if `FALSE-GREEN-REJECTED` or `FALSE-GREEN-ACCEPTED` | identical (fixture absent) | — | S2: true `fixture=fail` vs mutant `fixture=ok` | KILLED (S2) |
| 8 | m6-nogreen: REDARM checks RED only, drops GREEN | identical | replica: `redarm=fail` both (inconclusive from the committed row alone) | S3v2: true `redarm=fail` vs mutant `redarm=ok` | KILLED (S3v2) |
| 9 | m7-rconly: REGRESS compares `(rc,)` only | identical | replica: `regress=differs` both (stub changes dependent fixtures' rc) | S4: true `regress=differs` vs mutant `regress=same` | KILLED (S4) |
| 10 | m8-drop-r26: `r26 == 495` removed from the exit condition | identical (rc=1 both) | identical (rc=1 both) | none buildable — see Finding 1 | **SURVIVOR** |

Survivors: m8 only.

## Findings
1. **m8 survivor — the r26 target is enforced only through the exit code** (`census/round-31/c2-counter.py:163`: "return 0 if fp == 0 and real == 2 and cnec == 0 and r26 == 495 and fok and rok and same else 1"). Dropping `r26 == 495` leaves (rc, SUMMARY) identical to pristine on every state in the battery (17 runs). `controls.tsv` records SUMMARY lines only, so no recorded evidence can ever distinguish this mutant; a state that would (fp=0, real=2, cne=0, fixture=ok, redarm=ok, regress=same, r26≠495) requires a near-complete C2 implementation with a miscounted r26, which exists at no revision and is not buildable from committed bytes. Coverage finding, not a contract change: the r26 leg's kill power lives entirely in an unrecorded channel.
2. **Junk-state revisions are absent from the lane repo.** `git cat-file -t 4320f030b6fec9d5befaa15507df37e23f96c773` fails in the lane and in the fleet repo, and none of the seven junk revs in `census/round-31/records/controls.tsv:6-13` resolve under `--all` — the junk rows are recorded outputs of scratch states not reproducible from committed bytes. Kills against them are therefore analytic (m2b: any state where the tool reports neither REAL pair yields `real=0`, and m2b prints 2 unconditionally) or replica-based (J, which reproduces the recorded row's shape exactly). Location: `census/round-31/records/controls.tsv:11`: "SUMMARY fp=0 real=0 cne=0 r26=495 fixture=ok redarm=fail regress=differs".
3. **The gate strips plain `:N` specs itself; the counter's strip is load-bearing for the en-dash/comma class.** In S5 (citation edited to `…garbage-census.out:5`) the gate printed the token bare and m4b stayed byte-identical; in S5v2 (`…:3–5`, en dash) the gate printed the spec and m4b flipped to `fp=14 real=1`. This matches the counter docstring, `census/round-31/c2-counter.py:17-18`: "token-path is the printed path with any `:<line-spec>` suffix removed". The do-nothing row's `real=2` therefore also depends on the gate never printing a plain-`:N` spec for the two REAL pairs — true at base content (verified in the round-23 probe: both REAL tokens print bare).
4. **m2b is caught only by the junk row.** On the do-nothing state the hard-coded `real=2` is byte-identical to pristine; the junk row's recorded `real=0` (`controls.tsv:11`) is the only committed observable that distinguishes a faked real count. This is the one kill in the battery that would be lost if junk rows were dropped from the controls.

## Deliveries
- `.ufo/waves/round-31/w1/SwarmMutationTester33.md` (this report)
