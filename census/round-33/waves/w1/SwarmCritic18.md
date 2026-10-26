# SwarmCritic18 — falsify C1 item K20 (SCORECARD.md:314)

## Status

STATUS: PASS — K20 not falsified. Verdict **HOLDS** (not lax, not strict, not nondeterministic): the frozen argv reproduces `cases=15 pass=15 control=TAMPER-REJECTED` with rc 0 in three prereg runs (two fresh TMPDIR, one TMPDIR unset) and at base; the frozen predicate is the row's stated outcome text verbatim; both out-of-set residuals in the same cell re-derive exactly. Two limits are reported as ATTACKs below (a fixture oracle gap on `.gitattributes`, and a `SOUJI_*` env path the counter does not scrub) — neither makes K20's frozen (exit, predicate) unfaithful today, and neither may be amended by a seat.

## Evidence

Clone (per contract): `git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /fast/scratch/hyaku/souji-r33/AuditK20/c`, origin removed, detached at `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`; `git -C … rev-parse --show-toplevel` → the clone; `git -C … rev-parse HEAD` → `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`. Second clone `cbase` detached at `6017a482e7068d5afb7617640198fbb0fe743357`.

Row cell read (`git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 6017a482…:SCORECARD.md | sed -n 314p`), evidence column verbatim:
```
`bash tests/fixtures/r28-wave-evidence-capture.sh` `cases=15 pass=15 control=TAMPER-REJECTED` (base tool 8/15); `census/round-26/waves` `records=1381 failed=0 uncovered=0`
```

Item files are byte-identical base → prereg (`git diff --stat 6017a48 2d9bca55 -- tests/fixtures/r28-wave-evidence-capture.sh tools/souji-wave-evidence-capture.sh SCORECARD.md` → empty).

### (1) Determinism — three runs at prereg rev, fresh TMPDIR each, plus one TMPDIR-unset

`cd <clone> && TMPDIR=<fresh>/runN.XXXXXX bash tests/fixtures/r28-wave-evidence-capture.sh`:

| run | TMPDIR | rc | summary line |
|---|---|---|---|
| 1 | fresh `/fast/scratch/…/tmp/run1.RR1Qlt` | 0 | `cases=15 pass=15 control=TAMPER-REJECTED` |
| 2 | fresh `/fast/scratch/…/tmp/run2.AjJ5iJ` | 0 | `cases=15 pass=15 control=TAMPER-REJECTED` |
| 3 | unset (`env -u TMPDIR`) | 0 | `cases=15 pass=15 control=TAMPER-REJECTED` |
| base clone 6017a48 | fresh | 0 | `cases=15 pass=15 control=TAMPER-REJECTED` |

Run 1/2 tail (`/fast/scratch/…/run1.out` lines 42-47): `case-14: PASS (bad round usage rc=1 rc=1)`; `records=3 renames=0 excluded=0 symlinks=2`; `case-15: PASS (symlinks verbatim and committed-bytes verify rc=0 rc=0)`; summary. Only the fixture's own scratch commit id varies (`verify-rev rev=4e7a2dc0…` vs `rev=2d288f7a…` vs `rev=64947f64…`): it is a fresh `git init` per run. No predicate token reads it → **deterministic on the frozen predicate**.

Run 3 stderr also carries `warning: lane is not a git work tree; ignore rules not evaluated`, which runs 1/2 show at the same fixture-internal `lane-2` path; both are fixture-internal, verdict unchanged.

### (4) Counter, as assigned

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-33/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --scratch /fast/scratch/hyaku/souji-r33/AuditK20/cnt --only K20
ITEM	K20	AGREE	original	rc=0 expect_exit=0 predicate holds last=Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
counter rc=0
```

### Mutations (my clone, `SOUJI_CAPTURE_TOOL=<mutant>`; run from the pristine clone root)

| mutant | change | rc | summary |
|---|---|---|---|
| A | `tools/souji-wave-evidence-capture.sh:146` `RENAME_NAMES = ('.gitignore', '.gitattributes')` → `('.gitignore',)` | **0** | `cases=15 pass=15 control=TAMPER-REJECTED` |
| B | `tools/souji-wave-evidence-capture.sh:589` `return 0 if (failed == 0 and uncovered == 0) else 4` → `return 0` | 1 | `case-11: FAIL (tampered committed blob rejected rc=4 rc=0 want=4)` / `cases=15 pass=14 control=TAMPER-REJECTED` |

### (3) Out-of-set residuals re-derived

* `(base tool 8/15)` — `git -C <clone> show 765fe8b:tools/souji-wave-evidence-capture.sh > basetool/tool-r28.sh` (the pre-r29 tool; `git log --diff-filter=M -- tools/souji-wave-evidence-capture.sh` names only `b862007 round-29: C2 capture tool v2`), then `SOUJI_CAPTURE_TOOL=basetool/tool-r28.sh bash tests/fixtures/r28-wave-evidence-capture.sh` → rc 1, cases 1-6 PASS, 7-12/15 FAIL, `cases=15 pass=8 control=TAMPER-REJECTED`. **Reproduces.**
* `census/round-26/waves records=1381 failed=0 uncovered=0` — `bash tools/souji-wave-evidence-capture.sh <clone> 26 --verify --rev <rev>` at both `6017a482e7068d5afb7617640198fbb0fe743357` and `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`:
  `verify-rev rev=… records=1381 failed=0 uncovered=0` rc=0 (both). **Reproduces.** Accounting is exact: 1381 = `manifest.sha256` entries; the 1384 `find -type f` count adds `manifest.sha256` itself plus the two newline-named records stored GNU-escaped (`first\nsecond.md`, `old\nname.log`); 17 symlinks live in `symlinks.tsv`, not the manifest.

## Findings

1. **Predicate is the row's own text, and two of its tokens are inert constants.** `tests/fixtures/r28-wave-evidence-capture.sh:537` is `printf 'cases=15 pass=%s control=TAMPER-REJECTED\n' "$pass"` — `cases=15` and `control=TAMPER-REJECTED` are hardcoded; only `pass` is computed. The control guarantee comes from the exit path, not the token: `:538` `if [[ $fail -eq 0 && $control_tamper -eq 1 ]]; then exit 0`, with `control_tamper=1` set only by case 3 (`:271` `[[ $rc -eq 4 ]] && control_tamper=1`). Because K20's frozen exit is 0, the frozen (exit, predicate) still implies `fail==0 && control_tamper==1 && pass==15`. Not lax overall; the `control=` conjunct alone carries no information.
2. **Mutation B shows teeth.** Accepting a tampered committed blob (`:589` → `return 0`) is caught: case-11 FAIL, rc 1, `pass=14` → predicate fails → MISMATCH. The row's stated outcome cannot regress silently in the direction it names.
3. **ATTACK — fixture oracle gap on `.gitattributes` (reproduced, mutation A).** The row's own prose states “`nested .gitignore/.gitattributes/.git stored as .captured`”, but no fixture case exercises `.gitattributes`: `grep -n gitattributes tests/fixtures/r28-wave-evidence-capture.sh` → no hits (only `tools/souji-wave-evidence-capture.sh:24,146,220` mention it). Removing it from `RENAME_NAMES` keeps `cases=15 pass=15 control=TAMPER-REJECTED` rc 0, so the frozen predicate would still print AGREE while a capability named in the same cell is broken. This is a coverage gap in the frozen *item's oracle*, not lax wording in its predicate: K20's predicate is the cell's stated output, and the output is the fixture's own line. Smallest safe correction: a future stricter-only round adds a fixture case that commits a `.gitattributes` in `.ufo/waves/round-26/` and asserts `<name>.captured` + renames row + clean `--verify --rev`. A seat may not amend K20 this round.
4. **ATTACK — env path the counter does not scrub.** The fixture substitutes its tool from `SOUJI_CAPTURE_TOOL` (`tests/fixtures/r28-wave-evidence-capture.sh:33`, plus scratch root `SOUJI_R29_C2FIXTURE_BASE` at `:51`). `census/round-33/c1-counter.py:164` runs items with `env = dict(os.environ, TMPDIR=tmp, GIT_CONFIG_NOSYSTEM="1")` and pops only `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE` (`:165`). A stale `SOUJI_CAPTURE_TOOL` in the caller's environment would make K20 green without executing `tools/souji-wave-evidence-capture.sh` at all — my mutations A and B are exactly this reproduction. Today's hazard is nil only because no `SOUJI_*` var is set in this session (`env | grep -iE 'SOUJI|C2FIXTURE'` → nothing). Smallest safe correction: run the counter under `env -u SOUJI_CAPTURE_TOOL -u SOUJI_R29_C2FIXTURE_BASE`, or let the L1 record the harness env in the landing receipt. Counter-side amendment is stricter-only and the L1's alone.
5. **`TMPDIR` fallback.** `tests/fixtures/r28-wave-evidence-capture.sh:51` is `${SOUJI_R29_C2FIXTURE_BASE:-${TMPDIR:-/tmp}/souji-r29-wave-capture-fixture}`: with `TMPDIR` unset the fixture silently uses `/tmp` (run 3 left `/tmp/souji-r29-wave-capture-fixture`). Verdict unaffected, and the fixture is not a C2 O1-O5 leg or a G1-G6 guard — reported for the L1's Q71 sweep, not as a C1 defect.
6. **Not stale.** Both out-of-set residuals in the same cell hold as written (`pass=8` for the r28 tool; `records=1381 failed=0 uncovered=0` at base and prereg). No residual to report.

## Attack log

* **Attack 1 — nondeterminism.** Hypothesis: the fixture's fresh per-run git repos or `/tmp` fallback move the summary. Reproduced state: 3 prereg runs (fresh TMPDIR ×2, unset ×1) + 1 base run, all rc 0 with the same summary; the only varying token is the fixture-internal `verify-rev rev=…` sha, which no predicate conjunct reads. **Failed** → not NONDETERMINISTIC.
* **Attack 2 — lax predicate.** Hypothesis: a regressed tool still passes the frozen (exit, predicate). Reproduced state: mutation A (`.gitattributes` neutralisation removed) → `cases=15 pass=15 control=TAMPER-REJECTED` rc 0, i.e. the predicate agrees. **Partially succeeds**, but against the fixture's coverage, not the predicate's wording: the cell states this exact output, and removing the stated capabilities that *are* covered is caught (mutation B → `pass=14`, rc 1). Recorded as ATTACK 3 above; verdict remains HOLDS for the frozen item.
* **Attack 3 — strict predicate.** Hypothesis: the predicate demands more than the cell states. The cell states `cases=15 pass=15 control=TAMPER-REJECTED`; the predicate is that string with no anchor and no extra conjunct, and the frozen exit 0 is the fixture's documented condition (`:15-16`, `:538`). **Failed** → not STRICT.
* **Attack 4 — out-of-set staleness.** Hypothesis: the cell's other two counts drifted. Reproduced state: `pass=8` and `records=1381 failed=0 uncovered=0` both re-derived at their own revisions. **Failed** → no residual.

## Deliveries

* `.ufo/waves/round-33/w1/SwarmCritic18.md` (this report).

Scratch `/fast/scratch/hyaku/souji-r33/AuditK20/` removed after copying these receipts. Lane untouched: read-only `git -C` only, no worktree/index/jj mutation, no `git add/commit/push`. No tool installed or upgraded this run.
