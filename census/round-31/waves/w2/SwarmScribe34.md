# SwarmScribe34 — round 31 wave 2 (scribe: round-report draft)

## Status

STATUS: PASS — the round-report draft is written in the round-30 section order with every after-value re-derived at `2c16d018e40db7c23420a2c3bb546b52957bcc25`; four contract-level findings are recorded below (C1's one-item miss, the absent per-commit gate receipt, a broken no-harm instrument, a placeholder sentence in the admitted entry).

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, branch `master`, base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, prereg `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`, draft tip `2c16d018e40db7c23420a2c3bb546b52957bcc25` (worktree clean). Frozen contract and amendments read first; amendments A0-A5 and their digests verified against the files at the tip.

- Commit range: `git log --format='%H %s' 9f17a1e..2c16d01` → 11 commits (the earliest, `1d45496`, is the preregistration itself).
- C1, v1 and current (A2+A4), both at the tip, run serially:
  - `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1 rev=2c16d018…`
  - `ITEM L29 SCORECARD.md:170 literal=18/18 base-cell binding=- UNBOUND`
- C2, v1 at the tip: `SUMMARY fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same rev=2c16d018…`.
- C2, v3 (A5) two runs, distinct `SHIFT-PROBES` lists printed on each run; both `SHIFT rc=1 dangling=[…] want=[…] ok` and `SUMMARY … shift=ok rev=2c16d018…`.
- C3 at the tip: v1 `legs=11 fail=0 f1_entries=4`; v2 `legs=12 fail=0 f1_entries=4` (`L12 PASS … jj_calls=26 git_calls=111 missing=[]`); v3 `legs=13 fail=0 f1_entries=4` (`L13 PASS M1… M2… no=0<4=True`).
- M1 receipts: base gate at the prereg content `findings=18` (r26), `29` (r27), `21` (r28, 19 uncarried + 2 dangling), `carry_heading=0`; at `c6108301…` base gate 0/0/2 (no uncarried), tip gate 0/0/0.
- No-harm: coverage `grounded=16 mapped=16` at base → `grounded=17 mapped=17 … kill_tested=16 kill_violations=0` at the tip; SOURCES census exit 0 with 36 W04 at both ends; SOURCES rows 145 → 146.
- Round-31 landing gate (tip gate) at the tip: `findings=7`, all `LG-SEAT-UNCARRIED`, no `LG-DANGLING-PTR`, `checked_reports=60`; at `24f343c8…` and `8024b54…` it prints `COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-31/ or census/round-31/waves/`.
- Instrument digests at the tip match amendments: `edf0933d…` (capability cells), `95540fad…` (c2 v2), `12593a3b…` (c2 v3), `72a946e3…` (c3 v2), `5553b6d8…` (c3 v3), `450984a3…` (preregistration).

## Findings

1. **C1 misses its frozen target at the landing commit and at the tip.** Location: `census/round-31/records/c1-after-v1.txt` / `c1-after-a4.txt`, item L29 — `unbound=1 mismatches=1` against the target `unbound=0 mismatches=0`. L29's named record states the count only as `"matched_command_count": 18`, so no honest `record:` binding exists. Axis: **calibration** (the claim is scored missed; the road was disclosed by A4 before landing, so it is a target miss, not a hidden defect).
2. **The prereg's routed defect-5 process receipt is absent at the tip.** Location: `census/round-31/records/landing-gate-per-commit.txt` is named by `preregistration.txt:3` but not committed (`git ls-tree HEAD census/round-31/records/` has no such file). Axis: **operability** (the round's process evidence, not a claim target).
3. **`tools/souji-registry-agreement.py` cannot evaluate a healthy pair.** Location: `tools/souji-registry-agreement.py:115` raises `COULD-NOT-EVALUATE derived facts are trivial` when the r29 counter's `r26` line reports `failed=0`, which is its normal state. Reproduced at the round-31 pair (`--rev 2c16d018… --list-rev 1d45496…`) and at the round-30 committed pair (`--rev 2726c3d8… --list-rev d4928ec8…`), while `tests/fixtures/r29-registry-agreement.py` still prints `cases=20 pass=20 control=FALSE-GREEN-REJECTED`. Axis: **operability/calibration** (the no-harm instrument the round-30 report leans on cannot produce its reading; pre-existing since `8aaacf5`, not caused by this round).
4. **The admitted entry still calls S222 a placeholder.** Location: `corpus/knowledge/jj-dropped-keep-object-lifetime.md:1` — `source: S222 — git-reflog(1) at tag v2.56.0 (placeholder id: the L1 renumbers by document)`; S222 is already the row id at `corpus/SOURCES.md:167`. Axis: **coverage/quality** (a stale self-description inside an admitted artifact).
5. **Seven wave-1 STATUS lines are uncarried at the draft tip.** Location: tip gate output (Critic29, Executor04, Executor06, Reviewer25, Reviewer26, Scribe23, Simplifier38); `corpus/lessons/round-31.md` does not exist yet. Axis: **operability/quality** — expected mid-round, but the carry must land with the lesson or the round closes with `findings=7`.
6. **C1's tail scan is last-row-wins.** Location: `tools/souji-capability-cells.py:70` (`ROW` matches any `| Lnn | SCORECARD.md:<n> | …` line) and `:183` (`sup[m.group(1)] = …` overwrites). Today the 40 binding rows are the last such rows in `SCORECARD.md`, so the reading is stable; any later `| Lnn |` measurement table appended to the tail silently re-binds an item. Axis: **calibration** (future integration hazard; verified in code, not reproduced as a false pass).

## Attack log

- **A1 — beat the C2 v3 random SHIFT by inspecting a static table.** No: two runs drew different probes and both flagged exactly the four real paths. Not an attack that landed; the leg holds for these draws.
- **A2 — find C1 drift between the landing commit and the tip** (A4/A5 changed only counters/records). No: v1 and A2+A4 both re-read `unbound=1 mismatches=1` at `2c16d01`.
- **A3 — reproduce the round-30 no-harm registry reading at round 31.** Failed to reproduce; the live tool returns could-not-evaluate at *both* pairs while its fixture is green. Filed as finding 3 (counter defect, reproduced state).
- **A4 — test the routed defect-5 process at the record-landing commits.** The gate could-not-evaluate at `24f343c8` and `8024b54` because no round-31 capture was committed then; the named receipt file is absent. Filed as finding 2.
- **A5 — check the frozen-instrument digests against the amendments.** All six match; no post-freeze edit went unlogged.

## Deliveries

- `.ufo/waves/round-31/w2/deliver-report-draft.md` — the round report draft, round-30 section order, `<final>` placeholders for the final lane hash and report commit.
- `.ufo/waves/round-31/w2/deliver-tip-measure.txt` — every counter run, probe list, gate output and census line produced by this seat.
- `.ufo/waves/round-31/w2/SwarmScribe34.md` — this report.

Scratch `/fast/scratch/hyaku/souji-r31/w2-SwarmScribe34` was removed after the deliveries were copied. No lane mutation, no `agent://all`, no tool installs.
