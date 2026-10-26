# SwarmMutationTester28 — C1 counter mutation test (souji round 30, wave 1)

## Status
STATUS: PASS — all 9 assigned mutants killed (8 at SUMMARY level; M9 only at PTR-verdict level, SUMMARY-equivalent); no unconstrained survivor; lane tool bytes untouched (sha256 equal before/after); scratch removed.

## Evidence
Target: /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-capability-agreement.py, sha256
`af71db1e898f00575de1e13d80b73a2ac73fbc15cae9c74cdba9eff9e40be620` — identical bytes at prereg d4928ec86b667e3d1ed0adb07fb088e500cf1631 and lane tip df6afe817d096e4ad71ba2b9cc21a83f126eb658; **absent at base** 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b (the counter itself was added at the preregistration). Mutants are single-point edits of a copy under scratch; the lane file was never written.

Run form (every run): `python3 -B <variant>.py --root <repo> --rev <rev> --base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --list-rev d4928ec86b667e3d1ed0adb07fb088e500cf1631 --scratch /fast/scratch/hyaku/souji-r30/MutateC1Counter/counter-scratch [--only <ids>]`, where `<repo>` is the lane for fidelity runs and the scratch clone `/fast/scratch/hyaku/souji-r30/MutateC1Counter/c` (origin removed, toplevel verified) for state runs. Full raw outputs of all 34 runs: receipts file below.

Fidelity — pristine reproduces the committed controls exactly:
- base, full: `SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10 rev=9420341d9a814cb6089c25fb03a4cc9b23dc0d1b` = controls.tsv `C1-do-nothing(base)` (rc=1, 31.5 s).
- base, `--only R05,R10`: `SUMMARY k1=2 k2=0 mismatches=2 rows=2 pointers=10 partial=1` = the preregistration's disclosed L1 sanity run (both MISMATCH).
- Rebuilt junk states mirror controls.tsv: J1 k1=2 (junk1), J2 k1=1 (junk2), J3 k1=1 (junk3).

Kill map (pristine vs mutant, same state, same args; state revs are commits in the scratch clone):

| mut | single-point change (pristine line) | killing state | pristine | mutant | level |
|---|---|---|---|---|---|
| M1 | correction accepted ignoring observed — drop `cobs == rs` from line 183 `if crc == rrc and cobs == rs:` | J1 `4b3f77610105` = controls.tsv junk1 rebuilt (controls.sh:25 appends `R30-CORRECTION SCORECARD.md:158 R05 rc=0 observed=SELFTEST pass=18 fail=0` — real rc 0, invented observed) | k1=2 | k1=0, both rows CORRECTED | SUMMARY |
| M2 | correction accepted ignoring rc — drop `crc == rrc` (line 183) | J4 `b982bf2520ec` (scratch): real observed `SELFTEST pass=65 fail=0`, wrong rc=1 | k1=1 | k1=0, CORRECTED | SUMMARY |
| M3 | append-only check dropped (fail-open at lines 123–124, 170, 212) | J2 `e3a017683369` = controls.tsv junk2 rebuilt (in-place stated edit, controls.sh:28) with `--only R01` (R01 matches at base) | k1=1 `MISMATCH(append-only-violated) kind=shape` | k1=0 `MATCH` | SUMMARY; on R05 same state only the ROW verdict string changes (`MISMATCH(append-only-violated) kind=value` → `MISMATCH kind=value`, k1=1 both) |
| M4 | rows read from `--rev` instead of `--list-rev` (line 106 `rows_tsv = blob(root, a.list_rev, "census/round-30/c1-rows.tsv")`) | (a) do-nothing base control — rows file absent at base → `COULD-NOT-EVALUATE census/round-30/c1-rows.tsv absent at --list-rev`, exit 2; (b) J8 `ce094becf3bd` (scratch): rows file at --rev shrunk to R01 | (a) SUMMARY k1=13 rows=18; (b) k1=13 rows=18 | (a) COULD-NOT-EVALUATE exit 2; (b) k1=0 rows=1 | SUMMARY (both) |
| M5 | `cmd=` script-identity check dropped (line 178 → `if False:`) | J3 `c5d2f16c5e6e` = controls.tsv junk3 rebuilt (controls.sh:40 appends `R30-CORRECTION SCORECARD.md:158 R05 cmd=echo 18/18 rc=0 observed=18/18`) | k1=1 | k1=0, observed becomes `18/18` via `echo`, CORRECTED | SUMMARY |
| M6 | `clean -fdxq` dropped (line 148) | J11 `d6312b439667` (scratch, purpose-built rows file: litterer row MX then sensor row MY) | k1=0 (MY `observed=sensor=0 litter-absent`) | k1=1 (MY `observed=sensor=1 litter-present`) | SUMMARY — but survivor on every state built from the frozen 18 rows (see Finding 5) |
| M7 | whole output compared instead of last digit-bearing line (line 162 `return rc, summary_line(normalize(out, work))`) | base (do-nothing state), row R18 | k1=13 | k1=12 (R18 → MATCH) | SUMMARY |
| M8 | missing SHONEN path counts as resolving (line 211 → `ok = True`) | J6 `3974f01e4795` (scratch): `.ufo/waves/round-21/w1/ConnSiblingOverlap.md` deleted | k2=1, `PTR … ConnSiblingOverlap.md MISMATCH` | k2=0, `PTR … RESOLVES` | SUMMARY |
| M9 | WITHDRAWN accepted for a resolving token (line 213 gate `if verdict == "MISMATCH":` → `or ok`) | J7 `9098cd1c84f3` (scratch): `R30-CORRECTION SHONEN.md:12 PROVINCE.md -> WITHDRAWN` appended while PROVINCE.md still resolves | `PTR SHONEN.md:12 PROVINCE.md RESOLVES`, k2=0 | `PTR SHONEN.md:12 PROVINCE.md CORRECTED`, k2=0 | PTR-verdict only; SUMMARY identical |

Survivors: none. Two near-survivors are called out as Findings 5 and 7.

## Findings
1. **The committed junk controls cannot be re-run.** Revs b148bf9b109179adacc5c2aa4601a2272add01e7, 00673117a2265470dabf82b9e4060889caabb30d, 84def39da96c6b089a9f11f28ddafbb0aaf130f4 are bad objects in the lane (`git cat-file -t` → `fatal: bad object …`) and absent from the fleet object store; only the TSV receipts remain. I rebuilt byte-equivalent states from the committed builder census/round-30/controls.sh:23–42 and reproduced the recorded k1 values (2/1/1) before scoring mutants. Location: census/round-30/records/controls.tsv:6–8.
2. **The rc half of the correction match has no committed control.** junk1's corrections carry the real rc (0) with an invented observed (controls.sh:25), so a mutant that drops only the rc check survives every committed control; killed by scratch state J4 (real observed, rc=1): k1 1→0. A stricter-only amendment could add a junk state with real observed + wrong rc. Location: tools/souji-capability-agreement.py:183.
3. **The append-only fail-closed is SUMMARY-load-bearing only for rows that would otherwise match.** On junk2's own row (R05, still value-mismatching) dropping the check changes only the ROW verdict string; the SUMMARY-level kill needs a matching row (R01) under the same in-place edit. Location: tools/souji-capability-agreement.py:123,170,212.
4. **The `--list-rev` guard is doubly load-bearing**: at base the rows file is absent (mutant exits 2 COULD-NOT-EVALUATE) and a shrunk rows file at `--rev` is defeated (rows 18→1, k1 13→0). Location: tools/souji-capability-agreement.py:106; census/round-30/c1-rows.tsv absent at 9420341d.
5. **M6 (clean drop) is invisible to every state built from the frozen 18 rows.** Full A/Bs at base (0/30 lines differ), at tip df6afe81 (0/30), the two-row junk1 state (0), and two litter states — broad J9 `b82fe0d31c0b` and targeted J10 `382173be2f67` (litter dropped into census/, census/round-30/, tools/, tests/, corpus/, corpus/knowledge/, .ufo/waves/round-30/w1/ by a patched R01 fixture) — all 0 differing lines: no frozen row command senses untracked work-tree files (the fixtures build private worlds under temp dirs). Killed only by the purpose-built J11 rows file. Coverage finding, not a contract change: the `clean -fdxq` is defense-in-depth for future row commands that write untracked files. Location: tools/souji-capability-agreement.py:148.
6. **The last-digit-line rule is load-bearing (M7).** R18's stated literal `cases=15 pass=15` occurs in the capture fixture's whole output (`…case-15: PASS …` region) but its last digit-bearing line is `Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]`; comparing the whole output flips R18 to MATCH (k1 13→12; KINDS value 7→5, shape 5→6 — R05 also shifts value→shape). Location: census/round-30/c1-rows.tsv (R18 row); tools/souji-capability-agreement.py:162.
7. **M9 is SUMMARY-invisible.** A WITHDRAWN correction on a still-resolving token (PROVINCE.md at SHONEN.md:12) changes only the PTR verdict line (RESOLVES→CORRECTED); k2=0 either way. A scoring that reads only the SUMMARY line cannot see this mutant class — the per-item PTR lines are the only detector. Location: tools/souji-capability-agreement.py:212–213.
8. **`--only` masks the `rows=` field** (line 226: `rows={len(rows) if not only else len(only)}`), so `--only` runs cannot detect rows-file shrinkage — the M4 shrink kill required full runs on both sides. Location: tools/souji-capability-agreement.py:226.

## Attack log
Item is an attack: mutation test of the frozen C1 counter, run entirely in scratch `/fast/scratch/hyaku/souji-r30/MutateC1Counter/` (clone `c` with origin removed and toplevel verified; throwaway identity `mut` set only inside the clone; TMPDIR exported under the scratch dir; counter's own clones under `counter-scratch/`). No lane write, no git/jj mutation outside the scratch clone, no signals, no subagent dispatch (leaf member). No tools installed (operator directive 2026-10-19 record: none). Restoration: the lane tool's sha256 is identical before and after all runs (`af71db1e898f00575de1e13d80b73a2ac73fbc15cae9c74cdba9eff9e40be620`); the scratch tree was removed after the receipts were copied (verified absent).

## Deliveries
- .ufo/waves/round-30/w1/SwarmMutationTester28.md (this report)
- .ufo/waves/round-30/w1/SwarmMutationTester28-runs.txt (all 34 raw run receipts, consolidated)

Report: .ufo/waves/round-30/w1/SwarmMutationTester28.md
