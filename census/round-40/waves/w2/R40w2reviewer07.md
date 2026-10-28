# R40w2reviewer07 — C3 battery attack report

Seat: `R40w2reviewer07` (reviewer, wave 2 falsify, souji round 40).
Target: `census/round-40/c3-counter.py`, `tests/fixtures/r40-drift-record-branches.py`,
`tests/fixtures/r39-drift-record-rules.py`, audited tool `tools/souji-worktree-drift.py`.
Attacked revision: `128e412b0ced3c243dc27c3dd3332054a611bc2e` (landed instrument commit);
base: `0242085909fb6a4ee041c5443d76316ac6d59d4b` (frozen preregistration base).
Scratch: `/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer07/` — **removed before yield** (see §7).
No installs; no lane writes outside this wave dir. Replay driver kept for the L1 at
`.ufo/waves/round-40/w2/R40w2reviewer07-driver.py`.

## 1. What I attacked

The three C3 prereg kill conditions (`census/round-40/preregistration.txt:11`): pristine fails,
any mutant survives, any base mutant is killed — plus the claim's implicit contract that the
fixture isolates the record-parser branches it names (multiple TOTAL rows, `--skip-unrecorded`,
invalid UTF-8). I did not take the counter's own `killed=` tokens at face value: I rebuilt every
mutant and the pristine from `git show <rev>:tools/souji-worktree-drift.py` and ran both fixtures
against each by hand.

## 2. Commands run and real output

### 2a. The counter itself at the landed revision

```
$ cd /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer07 && TMPDIR=$S \
  python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/c3-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e \
  --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S/c3work
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-conflicting-second base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=invalid-utf8-in-repo-name base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-repos-disagrees base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
COUNTER-RC=0
```

### 2b. Independent replay (my driver, not the counter's scoring)

`python3 -B .ufo/waves/round-40/w2/R40w2reviewer07-driver.py $S` — rebuilds M15–M18 plus three of
my own mutants from rev-bound tool bytes, then runs `r40-drift-record-branches.py` and
`r39-drift-record-rules.py` directly (`--work` under my scratch). Output (abridged to verdict
lines; every ANCHOR count was exactly 1):

```
VERDICT pristine fixture=r40 rc=0 crash=False summary='SUMMARY cases=8 pass=8 fail=0' failing=[]
VERDICT pristine fixture=r39 rc=0 crash=False summary='SUMMARY cases=7 pass=7 fail=0' failing=[]
VERDICT M15 fixture=r40 rc=1 summary='cases=8 pass=7 fail=1' failing=['case-total-conflicting-second']
VERDICT M15 fixture=r39 rc=0 summary='cases=7 pass=7 fail=0' failing=[]
VERDICT M16 fixture=r40 rc=1 summary='cases=8 pass=4 fail=4' failing=['case-good','case-total-duplicate-identical','case-skip-unrecorded-suppresses','case-invalid-utf8-in-comment']
VERDICT M16 fixture=r39 rc=0 summary='cases=7 pass=7 fail=0' failing=[]
VERDICT M17 fixture=r40 rc=1 summary='cases=8 pass=7 fail=1' failing=['case-invalid-utf8-in-repo-name']
VERDICT M17 fixture=r39 rc=0 summary='cases=7 pass=7 fail=0' failing=[]
VERDICT M18 fixture=r40 rc=1 summary='cases=8 pass=7 fail=1' failing=['case-total-repos-disagrees']
VERDICT M18 fixture=r39 rc=0 summary='cases=7 pass=7 fail=0' failing=[]
```

The counter's scoring matches independent observation. Each kill is attributable to a distinct
case (M15→total-conflicting-second, M16→skip arms, M17→invalid-utf8-in-repo-name,
M18→total-repos-disagrees), and every mutant survives the base fixture. The repaired crash probe
(`c3-counter.py:107` reads fixture **stderr** only) is correct: a Python traceback goes to
stderr, while the fixture echoes the *tool's* output into its own stdout detail strings.

### 2c. Fifth mutants planted (not among M15–M18)

Two single-defect mutants of `parse_record` in `tools/souji-worktree-drift.py`:

- **M19a** — disable the `regs` disagreement guard, `tools/souji-worktree-drift.py:172`
  `if total["regs"] != sum(r["regs"] for r in rows):` → `if False:`
- **M19b** — disable the `prunable` disagreement guard, `tools/souji-worktree-drift.py:174`
  `if total["prunable"] != sum(r["prunable"] for r in rows):` → `if False:`
- **MCTL** (contrast control) — disable the whole TOTAL block, `:169` `if total is not None:` →
  `if False:`

```
VERDICT M19a fixture=r40 rc=0 crash=False summary='SUMMARY cases=8 pass=8 fail=0' failing=[]   → SURVIVES
VERDICT M19a fixture=r39 rc=0 summary='cases=7 pass=7 fail=0'                                   → survives base too
VERDICT M19b fixture=r40 rc=0 summary='SUMMARY cases=8 pass=8 fail=0' failing=[]               → SURVIVES
VERDICT M19b fixture=r39 rc=0 summary='cases=7 pass=7 fail=0'                                   → survives base too
VERDICT MCTL fixture=r40 rc=1 summary='cases=8 pass=6 fail=2' failing=['case-total-conflicting-second','case-total-repos-disagrees']
```

### 2d. `--base-rev` no-op probe

```
$ python3 -B .../c3-counter.py --root .../souji-shokunin --rev 128e412... \
  --base-rev c2dcd6251260c5ff17965c47a99cec6592c3a597 --scratch $S/c3work
<output byte-identical to §2a, same tool_sha/fixture_sha, rc=0>
```

At `c3-counter.py:146` the base fixture is fetched with `git_show(args.root, args.rev,
args.base_fixture)` — `args.rev`, **not** `args.base_rev`. `--base-rev` is only rev-validated
(`:133`) and never bound to the comparison. Harmless today only because
`git diff 0242085...128e412 -- tests/fixtures/r39-drift-record-rules.py tools/souji-worktree-drift.py`
is empty (verified). The advertised "survives the r39 base fixture" gate actually means
"survives whatever `r39-drift-record-rules.py` contains at `--rev`" — a mutant that survives the
frozen base but trips a *later edit* of that file would be scored `base_killed`, and the flag
cannot express the frozen comparison it names.

### 2e. Refusal probe

```
$ python3 -B .../c3-counter.py --root .../souji-shokunin --rev 0242085... --base-rev 0242085... --scratch $S/c3work
REFUSAL COULD-NOT-EVALUATE: tool or fixture absent at 0242085909fb6a4ee041c5443d76316ac6d59d4b
COUNTER-BASE-REV-RC=2
```

### 2f. No-timeout probe

`c3-counter.py:103` (`score()`), `:163` (pristine run), and fixture `:82` all call
`subprocess.run` without `timeout`. Planted a hang mutant (`import time; time.sleep(120)` at
module top of the tool):

```
$ timeout 12 python3 -B .../r40-drift-record-branches.py --tool $S/hang/hang.py --work $S/hang
HANG-PROBE-RC=124        # killed by my outer timeout; the fixture itself waits forever
```

A hanging mutant produces no SURVIVED verdict and no SUMMARY at all — the battery blocks
unboundedly instead of reporting the mutant.

## 3. Findings

### F1 (moderate) — the TOTAL-disagreement coverage is 1/3 of the contract it names

`tests/fixtures/r40-drift-record-branches.py:103-109` has two TOTAL cases, both of which make the
`repos` field disagree (`total-conflicting-second` second TOTAL `repos=1`; `total-repos-disagrees`
`repos=1`). The `regs` (`tools/souji-worktree-drift.py:172`) and `prunable` (`:174`) disagreement
guards have **no isolating case**: M19a and M19b both pass all 8 cases. Demonstrated, not
inferred (§2c). The pristine's exit-2 path can still be tripped by these guards, but no mutant of
them can fail — i.e., those two guards are covered only by the pristine run, which is not a kill
condition. Related family: `corpus/lessons/round-40.md` M40-4 already records the
last-TOTAL-wins ordering gap and the docstring (`:47-48` "a TOTAL row that disagrees" is refused
vs. `:165-168` last-wins) contract disagreement; the sibling-guard hole here is a new, distinct
demonstration.

### F2 (minor) — `--base-rev` is dead weight; "survives the base fixture" is rev-relative, not frozen

`c3-counter.py:146` fetches `args.base_fixture` at `args.rev`; `args.base_rev` is validated and
discarded (§2d). The advertised contract ("all mutants survive the r39 base fixture" —
preregistration C3) is measured against the r39 fixture **at the after revision**, not the base
revision. Today the bytes are identical, so the verdict stands; the flag lies about what it pins.

### F3 (minor) — unbounded waits: a hanging mutant yields no verdict at all

`c3-counter.py:103,163` and `r40-drift-record-branches.py:82` lack `timeout=`; §2f shows the
fixture waits forever on a hanging tool. The tool's own child git calls are bounded (`--timeout`),
but the battery's calls are not. A hang scores nothing — neither killed nor survived — so a
mutant that loops escapes silently as a stalled counter, not a verdict.

## 4. Non-findings (checked, do not fire)

- **Scoring contract:** `score()` (`c3-counter.py:96-120`) requires fixture rc==1, `fail>0` from
  the last `SUMMARY cases=` line, and no `Traceback` on the fixture's **stderr** — a tool
  traceback laundered into the fixture's stdout diagnostic echo cannot mask a kill (r40 repair of
  r39's stdout+stderr union bug, `corpus/lessons/round-40.md` M40-1). Matches my replay in §2b.
- **Pristine gate:** `c3-counter.py:165-181` requires rc==0, `fail=0`, `pass==cases`, `cases>=8`
  before any mutant is scored; an empty or broken fixture exits 1, not 0. Pristine passed all 8
  cases in my independent run.
- **Anchor uniqueness:** every mutant anchor occurs exactly once in the rev-bound tool bytes
  (`ANCHOR ... count=1` for all seven mutants in §2b output).
- **Hermeticity:** counter and fixture pass a whitelisted git env (`GIT_CONFIG_*=/dev/null`,
  `GIT_TERMINAL_PROMPT=0`, no inherited `GIT_*`); scratch is `mkdtemp` under my `--scratch`, never
  a hardcoded `/tmp`. Records are created under `fleet-root` (outside `--root path`), so they do
  not pollute `discover()`.
- **Refusal arms:** missing fixture/tool at `--rev` → rc 2 COULD-NOT-EVALUATE (§2e); unresolvable
  `--rev`/`--base-rev` → rc 2 (validated at `:133`).

## 5. Verdict

**C3 battery as scored: SAFE on its frozen terms, coverage claim FALSIFIED beyond the declared four.**

- Frozen predicate (all four declared mutants killed, pristine passes, zero base kills): SAFE —
  command §2a rc=0, independently reproduced §2b.
- Fixture coverage of the record parser's declared branches: **FALSIFIED** — M19a/M19b are
  single-defect mutants of `parse_record`'s TOTAL validation that the r40 fixture cannot fail
  (§2c, rc=0 `fail=0` on both); two of the three disagreement guards it names are unisolated.
- Supporting defects: F2 (`--base-rev` never read), F3 (no timeouts → hang, not a verdict).
- The prereg's own kill conditions do not include "mutants other than the declared four", and
  `corpus/lessons/round-40.md` M40-4 already rules C3 **unprovable** for definitional reasons;
  this report agrees with that verdict and adds two demonstrated defects on top.

## 6. Re-run instructions for the L1

```
S=$(mktemp -d /fast/scratch/hyaku/souji-r40/w2/repro.XXXX)
python3 -B census/round-40/c3-counter.py --root . \
  --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e \
  --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch "$S/c3work"
python3 -B .ufo/waves/round-40/w2/R40w2reviewer07-driver.py "$S"
```

Second command prints `VERDICT M19a fixture=r40 rc=0 ... fail=0` and `M19b` likewise — that is
the falsifier. `rm -rf "$S"` after.

## 7. Scratch accounting

`/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer07/` — **removed** (`rm -rf`) after this report
was written; only `hang/hang.py`, `mutants/*.py`, `fixwork/` and `c3work/` temp dirs lived there.
The replay driver `.ufo/waves/round-40/w2/R40w2reviewer07-driver.py` remains as the named
scratch/report file of this seat. No pacman, no installs, no writes outside the wave dir and the
named scratch root.
