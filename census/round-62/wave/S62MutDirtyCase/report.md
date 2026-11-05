# S62MutDirtyCase: does the r60 fixture kill realistic dirty-check mutants?

Verdict: `FIXTURE-KILL-POWER: gap-named`

Base: `tools/souji-receipt-write.py` at lane base 16fa821fdce00e709d6895ccfc7aaffa465af195
(sha256 367a0ca3bdea35714f1c1dba7bca407f05e8ec8d8f6e9c16f071d6e20e503d2c).
Fixture: `tests/fixtures/r60-receipt-write.py` read from the lane path (sha256 d5291501e8ce828e26aabaea69853fe3223297f2d5ac249aee62f73bb294c114).
Lane index at base: 17350 entries, all tag `H` (`git ls-files -v`). Lane worktree porcelain empty (exit 0). No tools installed or updated.

## Commands (exit codes observed)

- Fixture per tool: `python3 -B <lane>/tests/fixtures/r60-receipt-write.py --tool <MUT> --work $S/r60-<T>`; rc is the fixture's exit code.
- Mutants: M1 to M5 as specified; M6 is an extra probe (untracked-only check), added because M1 to M5 contain no tracked-blind mutant.
- Concealment and tracked probe: `bash conceal.sh <TOOL> <TAG>` (6 rows per tool, fresh fixture repos). Run twice; verdicts identical (`concealment/conceal-rows.log`, 35 rows).
- All mutants `ast.parse` OK. Each mutant differs from base only in the dirty block (`mutants/M*.diff`).

## Kill table (r60 fixture, 8 cases)

| Mutant | Change at base line 131 | fixture rc | SUMMARY line | Killed | Concealment D (skip-wt forged) | E (assume-unch forged) | F (skip-wt unmodified) |
|---|---|---|---|---|---|---|---|
| base (control) | none | 0 | `cases=8 pass=8 fail=0` | n/a | ACCEPT | ACCEPT | ACCEPT |
| M1 | dirty block removed | 1 | `pass=7 fail=1` (case 8: `tool rc=0 (want 2)`) | yes | ACCEPT | ACCEPT | ACCEPT |
| M2 | `--untracked-files=no` | 1 | `pass=7 fail=1` (case 8) | yes | ACCEPT | ACCEPT | ACCEPT |
| M3 | `git diff --quiet` (rc-based) | 1 | `pass=7 fail=1` (case 8) | yes | ACCEPT | ACCEPT | ACCEPT |
| M4 | `--ignore-submodules=all` | 0 | `pass=8 fail=0` | **no** | ACCEPT | ACCEPT | ACCEPT |
| M5 | `git diff-index --quiet HEAD --` (rc-based) | 1 | `pass=7 fail=1` (case 8) | yes | ACCEPT | ACCEPT | ACCEPT |
| M6 (extra) | `git ls-files --others --exclude-standard` | 0 | `pass=8 fail=0` | **no** | ACCEPT | ACCEPT | ACCEPT |

Concealment column is the forgery verdict: ACCEPT = forgery passes (a gap). Base also ACCEPTs D, E, F. No mutant refuses any of D, E, F, so no mutant is "killed" by concealment.

Supplementary row TP (visible tracked edit to `notes.md`, no `--allow-dirty`; not in the r60 fixture):

| Mutant | TP verdict |
|---|---|
| base | REFUSE (`lane worktree is dirty (git status --porcelain non-empty)`), rc 2 |
| M1 | ACCEPT (rc 0) |
| M2 | REFUSE |
| M3 | REFUSE |
| M4 | REFUSE |
| M5 | REFUSE |
| M6 | ACCEPT (rc 0) |

## What the fixture covers

- The only dirty case is case 8: a single untracked file (`stray-untracked.txt`). It kills any mutant that stops seeing untracked files (M1, M2, M3, M5).
- The fixture has no tracked-modification row. Any mutant that checks untracked files alone passes all 8 cases (M6).
- The fixture has no index-flag row (`skip-worktree`, `assume-unchanged`). The r60 fixture cannot detect concealment.

## Survivors

1. **M6, untracked-only dirty check (highest realism).** A reviewer can plausibly write "dirty = untracked files present" and miss tracked edits. The fixture accepts it; the TP row shows the tracked edit accepted with rc 0. This is a real gap in dirty-check coverage.
2. **M4, `--ignore-submodules=all`.** Survives the fixture, but on this lane it is equivalent: lane HEAD has 0 gitlink entries (`git ls-files -s`, mode 160000 count 0). It is an unkilled mutant, not a lane risk.
3. **Concealment rows D, E, F (not a mutant survivor; a coverage absence).** All six mutants and the base accept the forged skip-worktree and assume-unchanged rows. No existing fixture covers these rows. The candidate's RECEIPT-INDEX-FLAG-CONCEALED refusal is the only thing that can refuse them, so its verification needs new rows.

## Verdict basis

`gap-named`: the r60 fixture kills the untracked-blind mutants (M1, M2, M3, M5), but it lets through a tracked-blind mutant (M6) and any index-flag concealment (D, E, F for every mutant). Dirty-detection coverage is therefore not sufficient on its own.

## Limits

- Single run per fixture invocation. Cases 3 and 4 are timing-based; base passed all 8 and no flakiness was seen, but the kill table is one run per mutant.
- Six hand-authored mutants. The set is not exhaustive.
- M6 and the TP row are extra probes beyond the assigned M1 to M5.
- Concealment rows use one minimal repo shape (instrument plus counter plus notes); the forged bytes are a one-line `print("FORGED")`.
- The lane was read only. The fixture ran from the lane path and wrote only under scratch `r60-<T>` and `conc/<T>`.
- The report path in the seat spec (`.ufo/waves/round-62/w1/S62MutDirtyCase.md`) sits outside the seat's hard write scope. This report is at `.ufo/waves/round-62/w1/S62MutDirtyCase/report.md` instead; the L1 may copy it if it wants the trailer path.

## Delivered files (this directory)

- `report.md` (this file)
- `mutants/M0-base.py`, `mutants/M1.py` to `M6.py`, `mutants/M*.diff`, `mutants/r60-fixture-copy-of-lane.py`
- `fixture-logs/fixture-{base,M1..M6}.log`
- `concealment/conceal.sh`, `concealment/conceal-rows.log`
- `SHA256SUMS.txt`
