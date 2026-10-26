## Status
STATUS: PASS — audit executed end to end; K13 is **deterministic** and reproduces the cell's digits at base/list-rev/tip, but the frozen predicate is **LAX-PREDICATE**: two reproduced mutant states read `AGREE` while the same output contradicts the cell (`CASE FAIL` beside `SUMMARY total=13 failed=0`; `\b13/13\b` matched a foreign line over `SUMMARY total=13 failed=1`).

## Evidence

Contract read first: `census/round-33/preregistration.txt` (commit 2d9bca55), `census/round-33/c1-items.tsv` K13 row, counter predicate machinery `census/round-33/c1-counter.py:130-145` (`frozen_pred`: alternatives ` || ` are OR, each conjunct is `re.search` over whitespace-collapsed stdout+stderr, no line anchor).

Row at base 6017a482e7068d5afb7617640198fbb0fe743357 (`git show 6017a48:SCORECARD.md | sed -n 167p`, line sha256 `291d0d990c49285afdecf0872b48a4ddbbf8b660cefe5e951c92960099b99307`); SCORECARD.md byte-unchanged base→list-rev→tip (`git diff --name-only 6017a48 fef88f2 -- SCORECARD.md tests/fixtures/r19-rev-pin.py tools/souji-rev-pin.py` = empty):
```
| durable revision stamps (r19) | refuse HEAD/branch/short/keep-only/dirty-tree revisions before a record and verify tracked measured bytes | `tools/souji-rev-pin.py --selftest` 11/0; `tests/fixtures/r19-rev-pin.py` 13/0 | r19 |
```
Cell quotes (pipe-free): `refuse HEAD/branch/short/keep-only/dirty-tree revisions before a record and verify tracked measured bytes`; outcome span `tests/fixtures/r19-rev-pin.py` followed by `13/0`. Frozen K13: exit `0`, predicate `\btotal=13\b && \bfailed=0\b || \b13/13\b`.

**(1) Determinism** — clone `/fast/scratch/hyaku/souji-r33/AuditK13/c` (`git clone -q --no-local`, origin removed, `rev-parse --show-toplevel` printed the clone, detached at 2d9bca55, clean):
```
TMPDIR=<fresh t1> python3 -B tests/fixtures/r19-rev-pin.py -> rc=0
TMPDIR=<fresh t2> python3 -B tests/fixtures/r19-rev-pin.py -> rc=0
env -u TMPDIR      python3 -B tests/fixtures/r19-rev-pin.py -> rc=0
sha256(run1)=sha256(run2)=sha256(run3)=b966053127ecff7e867688308e7fd7a0d0dbe973357888c9644a42181aaee77c
13x "CASE pass", 6x "discriminates", last line each: SUMMARY total=13 failed=0 base_discriminating=6
```
No residue: `/var/tmp/souji-r19-rev-pin.*` count 0 before and after; the three caller TMPDIRs were empty after the runs. Runs are byte-identical, so the item is environment-stable, but the scratch root is the fixture's own pin, not the counter's: `strace -f -e trace=mkdir` on one run logged 13 `mkdir("/var/tmp/souji-r19-rev-pin.*")` calls and 0 under the caller TMPDIR (`tests/fixtures/r19-rev-pin.py:31` `TMPDIR="/var/tmp"`, `:143` `tempfile.mkdtemp(..., dir="/var/tmp")`, cleaned at `:224` `shutil.rmtree`). The counter's documented `TMPDIR=<fresh dir under --scratch>` (`c1-counter.py:167`) never reaches the fixture's children.

**(2) Predicate vs cell** — the cell states `13/0` (13 passed / 0 failed, the file's own `pass/fail` notation, e.g. `35/0`, `29/0`, `12/9 failed →12/0`). The healthy run prints exactly `SUMMARY total=13 failed=0` with rc 0, and `13 = 8 behavioral + 5 wiring` (`CASE pass` count 13). `grep -c "13/13"` on the healthy output = 0: the second alternative is never produced by the command.

**(3) Same cell's other digits/outcomes** — only `11/0` (enumerated as K12) and the round tag `r19`. No out-of-set count. The cell's prose "dirty-tree" is broader than behaviour, and was already broader at r19: independent probe in a scratch sandbox at 2d9bca55 (`tools/souji-rev-pin.py --root <sandbox> --rev <clean>`):
```
tracked file "unmeasured.txt" modified, --path tool.sh --path record.json -> printed db875b28..., rc_unmeasured_dirty=0
same repo, measured "tool.sh" modified                                -> "refused: measured inputs differ from ... changed=['tool.sh']", rc_measured_dirty=2
```
The r19 tool carried the same measured-path scope (`git show 005f3d3:tools/souji-rev-pin.py` line 139: `"tracked measured paths differ from %s (a record must not claim "`), so this is a base imprecision, **not a stale residual** — no cause commit exists at which it stopped being true.

**(4) Frozen counter, run as assigned** (twice; identical):
```
python3 -B …/census/round-33/c1-counter.py --root …/souji-shokunin --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
  --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch /fast/scratch/hyaku/souji-r33/AuditK13/cnt --only K13
ITEM	K13	AGREE	original	rc=0 expect_exit=0 predicate holds last=SUMMARY total=13 failed=0 base_discriminating=6
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
counter rc=0
```
Tip `fef88f2159f6380a4d1360f73365b3d595973a37`: same ITEM/SUMMARY lines, `agree=1 mismatches=0`, rc=0.

**Mutants** (scratch clone `/fast/scratch/hyaku/souji-r33/AuditK13/m`, origin removed, throwaway identity; committed mutants read with `--root <mutant clone> --rev <mutant> --list-rev 2d9bca55 --only K13`):

| id | state | change | argv output | counter |
|---|---|---|---|---|
| A | working tree, uncommitted | `tools/souji-rev-pin.py`: `if actual != expected:` → `if False:` | rc=1; `CASE FAIL dirty-tree-refuse exit=0 want=2`; `SUMMARY total=13 failed=1` | exit and `failed=0` both violated |
| B | working tree, uncommitted | append `revision = module.git("rev-parse", "HEAD")` to `census/round-14/run-targeted.py` | rc=1; `CASE FAIL wiring/census/round-14/run-targeted.py missing=False leftovers=[…]`; `total=13 failed=1` | ditto |
| C | working tree, uncommitted | `tools/souji-rev-pin.py`: `for relative in selected:` → `selected[:1]` | rc=1; `total=13 failed=1` (caught via `durable-clean-accept`) | ditto |
| D13 | `04086ecdd47938ab2d800a1b3f1765ed993a368c` | one `WIRING` entry removed from the fixture | rc=0; `SUMMARY total=12 failed=0` | K13 **MISMATCH** `predicate fails last=SUMMARY total=12 failed=0` |
| F13 | `e23a8a075aabd7124981d229c82a5a334c043eec` | helper tree check disabled **and** fixture counts a failed behavioral case as a pass (`failed += 1` → `passed += 1`) | rc=0; `CASE FAIL dirty-tree-refuse exit=0 want=2`; `SUMMARY total=13 failed=0 base_discriminating=6` | K13 **AGREE** `predicate holds last=SUMMARY total=13 failed=0` |
| E13 | `04d3811a1927ab6820625586289041c1a329141c` | helper tree check disabled, fixture prints `PROGRESS 13/13 cases planned`, `return 0` forced | rc=0; `CASE FAIL dirty-tree-refuse …`; `PROGRESS 13/13 cases planned`; `SUMMARY total=13 failed=1` | K13 **AGREE** `predicate holds last=SUMMARY total=13 failed=1` |

## Findings
1. **Deterministic.** Three runs (two fresh TMPDIRs, one unset) are byte-identical, rc 0, last line `SUMMARY total=13 failed=0 base_discriminating=6`; the counter reads AGREE at 2d9bca5 (twice) and at tip. Location: `tests/fixtures/r19-rev-pin.py:185-224`.
2. **First alternative is faithful and anchored.** `\btotal=13\b && \bfailed=0\b` is exactly the cell's `13/0` in the file's own notation and is the command's own summary rendering; count drift is rejected (D13 `total=12` → MISMATCH; an added 14th case would also MISMATCH under the same conjunct `[INFERENCE]`, which is currency-correct, not over-strict). Location: `census/round-33/c1-items.tsv` K13; `c1-counter.py:139-144`.
3. **Second alternative is unanchored (lax).** `\b13/13\b` never occurs in the healthy output, so it has no basis in the cell; it is matched anywhere in collapsed stdout+stderr and on its own satisfies the whole predicate. Reproduced: rev `04d3811` prints `SUMMARY total=13 failed=1` and is scored AGREE because a `PROGRESS 13/13 cases planned` line matched. Location: `c1-items.tsv` K13 predicate; `c1-counter.py:130-145`.
4. **The aggregate cannot see self-contradiction.** Rev `e23a8a0` prints `CASE FAIL dirty-tree-refuse` beside `SUMMARY total=13 failed=0`, rc 0 — the cell's capability (refuse a dirty measured path) is gone and the row still reads current. The predicate never inspects `CASE` lines. Location: `c1-counter.py:130-145`; `tests/fixtures/r19-rev-pin.py:212-224`.
5. **Not stricter.** The healthy run matches alternative 1 on exit 0; no conjunct fails a current run.
6. **No out-of-set residual count in this cell.** The only other digit group is `11/0`, which is enumerated as K12 and re-derived current by the same fixture run; `r19` is a round tag. The prose "dirty-tree" is imprecise at base (probe: unmeasured dirt accepted, measured dirt refused, rc 0 / rc 2) and was equally imprecise at r19, so it must **not** be restated — the restatement rule needs a cause commit where the outcome stopped holding, and none exists. Location: `SCORECARD.md:167`; `tools/souji-rev-pin.py:178-180`; `005f3d3:tools/souji-rev-pin.py:139`.
7. **Scratch isolation claim does not hold for this item (measurement fact, not a verdict defect).** The counter documents `TMPDIR=<fresh dir under --scratch>` for every run, but this fixture overwrites TMPDIR and mkdtemps under `/var/tmp` (13 `mkdir` verified by strace), so K13's runs escape `--scratch`; nothing is left behind (`:224`). `tests/fixtures/r19-rev-pin.py` has exactly one commit (`005f3d3`) and was not part of the r32 scratch sweep `98e5203`, which touched `tools/souji-rev-pin.py` but not its fixture. Location: `tests/fixtures/r19-rev-pin.py:31,143,224`; `c1-counter.py:167`; `git show --name-only 98e5203`.
8. **Residual risk for the L1.** Findings 3-4 mean a command that lies about its own failure can satisfy K13. They need a compound fault (capability loss **plus** fixture accounting/output change); the three single-fault regressions of the measured tool that were tested (A, B, C) are each caught.

## Attack log
- **Counterexample 1 (lax, alternative 2):** scratch rev `04d3811a1927ab6820625586289041c1a329141c`; output `CASE FAIL dirty-tree-refuse exit=0 want=2`, `PROGRESS 13/13 cases planned`, `SUMMARY total=13 failed=1`, rc 0 → `ITEM K13 AGREE`. A row whose tool no longer refuses a dirty measured path passes C1.
- **Counterexample 2 (lax, aggregate):** scratch rev `e23a8a075aabd7124981d229c82a5a334c043eec`; output carries `CASE FAIL` and `SUMMARY total=13 failed=0`, rc 0 → `ITEM K13 AGREE`.
- **Negative controls:** `04086ec` (`total=12`) → MISMATCH; working-tree mutants A (failed=1, rc 1), B (wiring leftovers), C (first-path-only verification) all break the exit/`failed=0` conjuncts. The predicate is not universally lax.
- **Impacted axis:** calibration (C1-CURRENCY) only; C2 untouched. K13 can certify a false capability row on self-contradicting output, same idiom as K12's `11/11`.
- **Smallest safe correction (L1's, NOT applied by this seat — compound with the fact that a wave seat has now scored):** match only the final `SUMMARY` line and drop the fraction alternative, e.g. `\bSUMMARY\ttotal=13\tfailed=0\b?$` or require `\btotal=13\b && \bfailed=0\b` with `&&` `!CASE\tFAIL`. Either keeps the healthy run green and rejects both reproduced states. Because the predicate is frozen and already scored, record this as a residual rather than amend.

## Deliveries
- `.ufo/waves/round-33/w1/SwarmCritic11.md` (this report; no other file written). Scratch `/fast/scratch/hyaku/souji-r33/AuditK13` removed after receipts were copied above; `/var/tmp/souji-r19-rev-pin.*` count 0; no tool installed or upgraded; no lane git/jj mutation.
