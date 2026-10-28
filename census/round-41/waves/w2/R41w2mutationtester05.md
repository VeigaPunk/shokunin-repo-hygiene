# R41w2mutationtester05 — mutation test of the frozen C1 counter

Seat: R41w2mutationtester05 (role mutation-tester, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Subject: `census/round-41/c1-counter.py` (frozen, sha256 `8860dc7af55848db3d67d11aec69cd8ee1f5a413964dd32ac7baddcebe49ab63`).
Judged on: calibration. Milestone: r41 falsify landed claims.

## Verdict

**PARTIAL — the landed C1 target survives this probe; the frozen controls do not discriminate most of the counter's legs.**

- The pristine counter reproduces the landed state and both frozen controls exactly (exit code and SUMMARY, asserted by the harness).
- 11 of 60 single-point mutants change the landed verdict (exit 0 → 1 or 2). Each is a real break.
- Frozen controls change exit code under exactly those 11. Seven more mutants keep every exit code but change the pinned control SUMMARY text (the do-nothing `corrected=0` and junk `junk=3` expectations).
- 28 mutants are invisible to all three frozen inputs at the exit-code level but flip the verdict on crafted inputs (22) or change evidence only (6). Crafted inputs are my own scratch constructions, not frozen evidence.
- 14 mutants are invisible to every input I constructed: 11 are equivalent on the pinned history or digest, 3 are dead under the pinned digest (see F5).
- Named limits for the round lesson (no edit to any frozen file): F2 (the junk and rewritten legs have no verdict-level frozen test), F3 (control text is not machine-compared), F4 (a crash and a red verdict share exit 1), F5 (every derivation reads an immutable commit), F6 (the I1 mismatch predicate hard-codes the filed numeral), F8 (sourced leg is double-redundant).

## Scope and bounds

- Read-only in the lane. The only lane accesses were `git clone --shared` (source only), `git show`, `git cat-file`, `git rev-parse`, `git ls-tree`, and `sha256sum` on the working-tree counter and items table. No mutating git. No candidate under `tests/`, `tools/`, `census/`, `corpus/`, or any tracked file.
- Mutants and inputs lived under `/fast/scratch/hyaku/souji-r41/R41w2mutationtester05/` (clone, mutant sources, run log). Receipts copied to the seat directory; the scratch directory is deleted before yield.
- No tool was installed or upgraded.

## Pinned bytes checked

Commands:

```
sha256sum census/round-41/c1-counter.py census/round-41/c1-items.tsv
git show 31e4d3e758bb903808a9270018d7e5be99ce38a4:census/round-41/c1-counter.py | sha256sum
```

Output:

```
8860dc7af55848db3d67d11aec69cd8ee1f5a413964dd32ac7baddcebe49ab63  census/round-41/c1-counter.py
2d2a548e253b7863cd9679ebe9f1f851a10223e47d3456e33345279b79a036cf  census/round-41/c1-items.tsv
8860dc7af55848db3d67d11aec69cd8ee1f5a413964dd32ac7baddcebe49ab63  -
```

Both match `census/round-41/preregistration.txt` (C1 Counter and Population digests). The harness re-asserts both digests at BASE (`31e4d3e`) before mutating.

## Method

`harness.py` (seat dir copy) does the following:

1. Takes the committed counter blob at `31e4d3e` and applies 60 text substitutions. Each substitution's pattern is asserted to occur exactly once. Each mutant is `compile()`d.
2. Builds 50 inputs in a scratch `git clone --shared` of the lane. Every commit is a child of `31e4d3e`, except the do-nothing rev `6682b98`.
   - **Frozen (3):** `landed` = `31e4d3e` (target: exit 0, `SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1`); `nothing` = `6682b98` (exit 1, `corrected=0 uncorrected=3 junk=0 rewritten=0 sourced=0`); `junk` = the frozen junk control `census/round-41/controls/c1-junk-round-41.md` committed as the lesson (exit 1, `corrected=0 uncorrected=3 junk=3 rewritten=0 sourced=0`).
   - **Crafted (47, not frozen):** 24 single-field wrong CORRECTION lines (additive `A-*` and replacing `R-*`, for I1/I3/I4 × file/filed/derived/rev); `X01` unknown id; `X02` trailing text on I1's line; `Z-drop-I4`, `Z-drop-I1`; `R-I1-source-S999`; round-40 prefix edit, anchor removal, after-anchor edit, append (harmless), deletion; SCORECARD and LOG head edits; items-table header edit (`T-a`); seven S258 registry edits (tier, status, date, all-cell v2.56.0 removal, all-cell worktree.c removal, ten-cell row, cell-1-only v2.56.0 removal); rev inputs `rev-abbrev`, `rev-HEAD`, `rev-zero`.
3. Runs every mutant (and the pristine reference) against all 50 inputs: 3050 runs, 8 parallel workers.
4. Scores exit code and full stdout against pristine on each input.

Commands run (in order):

```
cd /fast/scratch/hyaku/souji-r41/R41w2mutationtester05 && timeout 1500 python3 -B harness.py > run.log 2>&1; echo rc=$?
```

Two earlier runs failed at harness-assertion time (G3 and M4 pattern anchoring, both in my patterns, not the counter). Both were fixed. The classifier was then split (exit-code change vs control-text drift) and one crafted input (X02) was added. The final run:

```
rc=0
inputs: 50 (frozen 3, crafted 47)
runs: 3050
pristine reproduces all three frozen controls
Wall time: 107.22 seconds
```

Harness self-check (pristine, verbatim from `table.md` / `results.json`):

```
landed   rc=0 SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1
nothing  rc=1 SUMMARY items=3 mismatched=3 corrected=0 uncorrected=3 junk=0 rewritten=0 sourced=0
junk     rc=1 SUMMARY items=3 mismatched=3 corrected=0 uncorrected=3 junk=3 rewritten=0 sourced=0
```

These match `census/round-41/controls/c1-control.txt` and `census/round-41/records/c1-after.txt`.

## Results by class (60 mutants; per-row detail in `summary.tsv`, full matrix in `table.md`)

| class | n | members |
|---|---|---|
| CHANGES EXIT CODE on frozen (landed and/or controls) | 11 | D2, D4, A6, V1, V2, V5, V7, V8, V10, V12, S1 |
| exit code unchanged on frozen; pinned control SUMMARY text drift | 7 | G1, G6, G7, J2, J5, J7, S9 |
| invisible to frozen; exit flip on a crafted input | 22 | D1, R1, R2, R4, A4, A7, J1, J3, J4, J6, J8, S2, S3, S4, S5, S6, S7, S8, S12, M3, M4, M5 |
| invisible to frozen verdict; evidence-only on a crafted input | 6 | A5, G2, G3, G4, G5, S10 |
| invisible to every input | 14 | D3, D5, R3, A1, A2, A3, V3, V4, V6, V9, V11, M1, M2, S11 |

Mutant descriptions are in `summary.tsv` column 3. Representative exact outputs follow.

### Mutants that change the landed verdict

```
D2  (digest check inverted)        landed rc=2 REFUSAL COULD-NOT-EVALUATE: items table absent or differs from the pinned digest
D4  (header row not skipped)       landed rc=1 uncaught ValueError: derive (no SUMMARY)
A6  (rewritten sign inverted)      landed rc=1 SUMMARY items=3 mismatched=3 corrected=3 uncorrected=0 junk=0 rewritten=3 sourced=1
V1  (I1 predicate inverted)        landed rc=1 SUMMARY items=3 mismatched=2 corrected=3 uncorrected=0 junk=0 rewritten=0 sourced=1
V12 (MEASURED moved to 7eebc18)    landed rc=1 SUMMARY items=3 mismatched=3 corrected=0 uncorrected=3 junk=3 rewritten=0 sourced=0
S1  (I1-only source gate removed)  landed rc=1 SUMMARY items=3 mismatched=3 corrected=1 uncorrected=2 junk=0 rewritten=0 sourced=1
```

### Mutants that keep exit codes but drift the pinned control text

```
J7 (junk loop disabled)       junk    rc=1 SUMMARY ... corrected=0 uncorrected=3 junk=0      (pinned: junk=3)
J2 (spec mismatch not junk)   junk    rc=1 SUMMARY ... corrected=0 uncorrected=3 junk=0      (pinned: junk=3)
J5 (junk derived check drop)  junk    rc=1 SUMMARY ... corrected=0 uncorrected=3 junk=1      (pinned: junk=3)
S9 (sourced counted always)   nothing rc=1 SUMMARY ... corrected=0 uncorrected=3 sourced=1   (pinned: sourced=0)
G1 (fine forced True)         nothing rc=1 SUMMARY ... corrected=2 uncorrected=1 sourced=0   (pinned: corrected=0)
G6 (corrected counts every)   nothing rc=1 SUMMARY ... corrected=3 uncorrected=0 sourced=0   (pinned: corrected=0)
G7 (I1 source any -> all)     nothing rc=1 SUMMARY ... corrected=0 uncorrected=3 sourced=1   (pinned: sourced=0)
```

These seven pass a verdict-only gate against the controls.

### Crafted-only kills (verbatim from `results.json`)

```
J8  (LINE regex trailing-field tolerance)  X02-trailing-text-I1  pristine rc=1 corrected=2 uncorrected=1   mutant rc=0 corrected=3
A4  (prefix check removed)                 W-a-prefix-edit-r40   pristine rc=1 rewritten=1                 mutant rc=0 rewritten=0
M3  (junk==0 clause removed)               X01-unknown-id        pristine rc=1 junk=1                       mutant rc=0 junk=1
S12 (sourced leg fully removed)            S-a-tier-B            pristine rc=1 sourced=0                    mutant rc=0 corrected=3 sourced=0
R1  (full-hex REV regex removed)           rev-abbrev            pristine rc=2 REFUSAL --rev does not resolve  mutant rc=0 corrected=3
D1  (digest check deleted)                 T-a-items-header      pristine rc=2 REFUSAL digest               mutant rc=0 corrected=3
S7  (blob reads cell 1 only)               S-h-cell1-no-v2.56.0  pristine rc=0 corrected=3                  mutant rc=1 corrected=2 sourced=0
```

`S7` is a crafted-input difference on purpose: the pristine rule accepts S-h (v2.56.0 remains in the anchor cell), the mutant narrows the blob to cell 1 and turns red. That is a real difference, not a harness artifact.

## Findings (named limits for the round lesson; no frozen file edited)

**F1. The landed verdict is sensitive to the derivations and the refusal path.** 11 of 60 mutants flip exit at landed: the I1, I3, I4 predicates (V1, V2, V5, V7, V8, V10), the MEASURED constant (V12), the items digest inversion (D2), the header skip (D4), the rewritten sign (A6), and the I1 source gate (S1). Each is a real break; none is harmless.

**F2. The frozen controls have no verdict-level test of the junk and rewritten legs.** The do-nothing and junk controls are both red because `corrected=0`, regardless of whether the junk clause, the junk count, or the rewritten clause work. Consequently:
- junk-check mutants (J1, J3, J4, J6, J8), the junk verdict clause (M3), the rewritten count (A7), and the prefix check (A4) are invisible to frozen exit codes;
- the only frozen-visible effect of junk counting is the printed `junk=` number (J2, J5, J7);
- the only input that flips M3/J1/J7 on exit is a lesson with a valid correction for every item *and* an extra junk line (`X01`), which no frozen input is.
Named limit: the next round needs a frozen "valid corrections + one junk line" control and a frozen "rewritten item file" control if these legs are meant to be verdict-tested.

**F3. Control expectations are text only.** The do-nothing and junk targets live in `census/round-41/controls/c1-control.txt` as prose; the counter itself does not compare its output to them. Seven mutants (G1, G6, G7, J2, J5, J7, S9) keep every exit code equal to the control's exit code and change the control SUMMARY. A gate on exit codes would pass them. Named limit.

**F4. Exit code 1 is shared by a red verdict and an uncaught traceback.** D4 (landed) and A5 (deleted round-40, mutant `TypeError` at `tip` None) both exit 1 with no SUMMARY line. The counter's red verdict and a crash are indistinguishable by exit code; only the presence of a `SUMMARY` line separates them. Named limit.

**F5. Every derivation reads an immutable commit.** `derive()` and the base-side checks (`present`, `mismatched`) read `MEASURED = bffcc0f`, not `--rev`. No `--rev` can change a derived value or an anchor's presence; only the lesson, the S258 registry row, and the byte-prefix of the three item files at `--rev` are rev-controlled. Consequences:
- V3 (pipe-led row filter), V4 (I1 threshold 9→3), V6 (I3 fallback), V9 (I4 prefix widened), V11 (I4 empty-path guard): invisible to every input.
- A1 (base anchor presence deleted), A2 (forced true), M2 (`mismatched==3` clause removed): dead under the pinned digest; reachable only if the items table or MEASURED changes.

Equivalence checks against the pinned history (read-only):

```
git show bffcc0f660ff36eb8add3f61582748a7af019a5b:corpus/SOURCES.md | grep -c '^|.*worktree\.c'            -> 2
git show bffcc0f660ff36eb8add3f61582748a7af019a5b:corpus/SOURCES.md | grep -cE '^\| S[0-9]+ .*worktree\.c' -> 2   (V3 equivalent)
git ls-tree -r --name-only bffcc0f660ff36eb8add3f61582748a7af019a5b census/round-40/ | while read f; do git show bffcc0f660ff36eb8add3f61582748a7af019a5b:"$f" | grep -q 'flagged as potentially' && echo "$f"; done   -> (no output; V9 equivalent)
git show bffcc0f660ff36eb8add3f61582748a7af019a5b:census/round-40/records/c1-before.txt | grep -o 'register_cells=[0-9]*'  -> register_cells=6
git show bffcc0f660ff36eb8add3f61582748a7af019a5b:census/round-40/records/c1-after-h.txt | grep -o 'register_cells=[0-9]*' -> register_cells=3   (V6 dead branch)
git show bffcc0f660ff36eb8add3f61582748a7af019a5b:corpus/lessons/round-40.md | grep -c 'appears in 9 rows'  -> 1   (A1, A2 dead)
```

Equivalent on any input: D3 (absent table digested as `b''` still refuses), A3 (anchor clause redundant given `startswith`), S11 (`sourced_n` is 0 or 1 and equals `src_ok`; the `fine and src_ok` leg already enforces it), R3 (MEASURED always resolves in the lane history), V4 (count 2 is the only reachable value; any constant ≠2 gives True), V11 (`show(root, MEASURED, "")` returns the root tree listing, which contains no phrase). Equivalent on the pinned digest or history: D5 (no blank lines in the table), M1 (three items), V3, V6, V9 (the pinned checks above).

**F6. The I1 mismatch predicate hard-codes the filed numeral.** `derive` for I1 returns `count != 9`; the filed token `9-rows` is never parsed from the items table. The predicate would not notice a change of the filed token, only of the derived count (V4 confirms any constant ≠2 is indistinguishable). The derived value still reaches the verdict through the CORRECTION match, which is why the landed exit is not fooled. Named limit.

**F7. Rev gate and digest gate are only exercised by crafted inputs.** The frozen inputs use full 40-hex revs and the pinned table. R1, R2, R4 are caught only by `rev-abbrev`/`rev-HEAD`; D1 only by `T-a-items-header` (exit 2→0). R3 is equivalent for this lane.

**F8. Sourced leg is double-redundant.** S10 (`fine and src_ok` dropped) and S11 (`sourced_n == 1` clause dropped) each leave the verdict unchanged on their own; removing both (S12) lets the S258 edits that break a source check turn green: `R-I1-source-S999`, the tier edit (S-a), status (S-b), date (S-c), all-cell v2.56.0 removal (S-d), all-cell worktree.c removal (S-e), and the ten-cell row (S-f). The cell-1-only edit (S-h) is accepted by the pristine rule and by S12, so it is not a S12 kill. Only the crafted S-edits expose the double redundancy.

**F9. Junk and rewritten clauses are not exercised by the landed state.** At landed both are 0, so a mutant that makes them always 0 (M3, M4, A7) is indistinguishable from the pristine on the landed input. Only crafted inputs (X01, W-a..W-g) separate them.

## Commands run and receipts

- `sha256sum census/round-41/c1-counter.py census/round-41/c1-items.tsv` and the `git show 31e4d3e…:census/round-41/c1-counter.py | sha256sum` check (output above).
- `git clone -q --shared <lane> <scratch>/clone` (inside the harness, once); the harness runs `python3 -B harness.py` (output above and in `run.log`).
- Equivalence checks listed under F5 (read-only `git show`, `git ls-tree`, `grep`).
- Per-run value checks listed under the result sections were read from `results.json` with a read-only Python query.
- No mutating git in the lane, no write into any tracked path.

Receipts in the seat directory `.ufo/waves/round-41/w2/R41w2mutationtester05/`:

- `harness.py` — the mutation harness (reproducible; commit hashes change per run, outcomes do not).
- `mutants/P00.py` … `mutants/M5.py` — the 61 mutated counters (P00 is the pristine reference).
- `table.md` — full matrix with every input's pristine rc and SUMMARY.
- `summary.tsv` — one row per mutant: landed exit, do-nothing and junk match, frozen exit flips, frozen text drift, crafted kill counts, tracebacks, class.
- `results.json` — every run's rc, stdout, stderr keyed `mutant|input`.
- `run.log` — harness stdout of the final run.

## What this does not establish

- It does not prove the counter is correct; it measures which single-point edits the frozen inputs can and cannot tell apart.
- Crafted inputs are my constructions; they are evidence about the counter's blind spots, not frozen verification of the claim.
- Mutants are single-point text substitutions; compound mutations are not exhaustively covered (S12 is the one deliberate compound).
- No candidate counter was produced. Findings F2–F8 are named limits for the round lesson; none is a reason to edit a frozen file.
