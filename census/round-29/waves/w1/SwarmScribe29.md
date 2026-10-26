## Status

STATUS: PASS — draft `## Mistakes` section written to the delivery path with the three required rows (a/b/c) plus three evidence-sourced extra rows; every pointer was opened and line-checked against committed bytes at `b8cb4b31ce80e2e3314b88e85d40ea9873180804`; no fix is claimed landed (all `<landed-hash: …>` left visibly unfilled).

## Evidence

Lane read-only start: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --short HEAD` → `b8cb4b3`; `git status --porcelain` → 1 line, ` M .ufo/waves/round-26/w1/ScribeGateDraft.md` (pre-existing, not mine, untouched).

Required pointers, all opened this run:

- `sed -n '1758p' LOG.md` → "`two newline-containing` …" (full: the C3 bullet ending "`sha256sum -c` on r26 warns that two newline-containing path rows are improperly formatted (rc 0); r27 verifies cleanly").
- `sed -n '23p' SCORECARD.md` → C3 row with "r26 `sha256sum -c` warns 2 malformed newline-path records (rc 0), r27 clean".
- `census/round-29/records/controls.tsv` (`nl -ba`): line 2 `C1-do-nothing(base) … SUMMARY k1=6 k2=4 mismatches=10 rev=691dd292…`; line 3 `C2-do-nothing(base) … failed=152 uncovered=14`; line 4 `C3-do-nothing(base) … F3_entries=0 rows=139`; lines 5,7 `C1-junk1 … mismatches=6`, `C1-junk3 … mismatches=68`; lines 8,9 `C2-junk1 … uncovered=14`, `C2-junk2 … floor_violations=3`; line 10 `C3-junk … F3_entries=2 rows=139`.
- `corpus/lessons/round-28-verifier-spotcheck.md`: `:69-79` §C3 (`ok=1228`, `152` records `FAILED open or read`, rc 1; the two escaped records are valid GNU escapes, uutils 0.8.0 limit); `:46-50` exclusion-clause ruling (138 non-S215 rows, "would make the claim fail by construction on its own ADMIT branch"); `:52-53` global `grounded=13 mapped=13`, "a Q58-class preregistration defect"; `:119-120` landing-gate carry "can never evaluate committed round reports"; `:121,123` routed defects 4 and 5.
- `git show b8cb4b31…:corpus/lessons/round-28.md` piped to `grep -n` → `21` carries "The frozen registry-row counter is 139 … the frozen target 138 is missed"; `22` and `40` carry the "improperly formatted" / "two malformed newline-path records" text.
- `census/round-28/records/preregistration.txt:7` → "S119 row, if appended, is not counted in this claim" (11 words) and "grounded/mapped=6/6 dangling=0 mismatches=0".
- `.ufo/waves/round-29/w1/deliver-q60-q62-red-before.tsv`: `:8` Q60 base `clauses=1 readings=0 unread=1 rc=1`; `:10` Q62 base k1 block naming S215 `used-by-no-cite` and S075/S076/S022/S024/S025 `cited-not-in-used-by`.
- `.ufo/waves/round-29/w1/SwarmExecutor18.md`: `:36` the r28 miss ruling quoted with a citation; `:42-45` Q60 base/repair/control/round-27 runs (`32c0fe6` `readings=1 unread=1` rc 1; round 27 `clauses=0` rc 2); `:105` Q62 both-direction failure at base.
- `.ufo/waves/round-29/w1/SwarmExecutor01.md:26-40` → committed-tool fixture `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, reverse check deleted `cases=12 pass=9` rc 1; base instrument `mismatches=10` rc 1.
- `.ufo/waves/round-29/w1/SwarmExecutor04.md:6,11-13` → extended fixture red on the base tool `cases=12 pass=6`, `EXIT=1`, case-11 two-sided tamper control.
- `.ufo/waves/round-29/w1/deliver-landing-checklist.md` §6 → base `SUMMARY … checked_reports=0` + `COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-29/`, rc 2; scratch clone with committed reports `carry_heading=1 checked_reports=1` rc 0.
- `corpus/lessons/round-26-verifier-spotcheck.md:47` → `disagree (qualified)`, recorded reason "version alignment unprovable" does not reproduce, "decision-time mirror state is unrecoverable"; `:61` routed.

Sweeps behind negative claims:

- `grep -n '^| Q5[6-9]' corpus/QUALITY.md` → Q56 `135`, Q57 `141`, Q58 `142`, Q59 `143`; no Q60/Q61/Q62 row exists at base.
- `grep -rln souji-landing-gate .ufo/waves/round-29/w1/` → 8 files, all reports/TSVs that reference the gate; the only `landing`-named delivery is `deliver-landing-checklist.md`, so no w1 delivery patches `tools/souji-landing-gate.py`.
- `awk -F'|' '/^\|/{print NR": fields="NF-2}'` on the delivery → all 8 table lines `fields=4` (no literal pipe inside a cell).

No scratch directory was created; no tool installed or upgraded; no `pacman` call; no git/jj mutation; no lane file written except this report and the delivery.

## Findings

1. All three required rows verify, with one correction inside row (a)'s chain of pointers: the number-drift chain is `LOG.md:1758` / `SCORECARD.md:23` / `corpus/lessons/round-28.md:22,40` versus `corpus/lessons/round-28-verifier-spotcheck.md:69-79` and `census/round-29/records/controls.tsv:3` (`failed=152`). Location: those five files at `b8cb4b31ce80e2e3314b88e85d40ea9873180804`.
2. Required row (b)'s "five other pairs" resolves to named rows, not a count alone: S075, S076, S022, S024, S025 `cited-not-in-used-by`, plus S215 `used-by-no-cite`. Location: `.ufo/waves/round-29/w1/deliver-q60-q62-red-before.tsv:10`; repairs in `deliver-c1-usedby-changes.tsv`.
3. Required row (c)'s evidence is the frozen clause `census/round-28/records/preregistration.txt:7` read against the self-ruling at `corpus/lessons/round-28.md:21`, not `:22`.
4. Peer receipt defect to fix before landing: `SwarmExecutor18.md:36` cites the r28 miss ruling at `corpus/lessons/round-28.md:22`; committed bytes at `b8cb4b3` put that sentence at `:21` (line 22 is the C3 bullet). The Q60 base run is unaffected (the checker reads whole files), but the motivating citation in the seat report is off by one line.
5. Q60 and Q62 are proposals, not criteria: no Q60/Q61/Q62 row exists in `corpus/QUALITY.md` at base (sweep above). The draft therefore says "proposed" and leaves the landed-hash placeholders unfilled for rows (b) and (c).
6. Row 4 (class `vacuous`, the landing gate's unevaluable carry check) has no in-wave fix; the sweep shows no seat patches `tools/souji-landing-gate.py`, so its `<landed-hash: …>` must stay unfilled unless the L1 lands a gate change. Its only working mechanism on record is the scratch-clone run in `deliver-landing-checklist.md` §6.
7. Extra rows added, all from the named sources and nothing else: row 4 and row 5 from `corpus/lessons/round-28-verifier-spotcheck.md` routed defects 3 and 4; row 6 from `corpus/lessons/round-26-verifier-spotcheck.md` discernment row S119 plus routed defect 2. Rows 5 and 6 carry no `fail-receipt:` label: row 5's fix is a derivation rule already exercised by this round's own target (`controls.tsv:4`), and row 6's premise decayed between rounds so no red-before run exists; the draft says both plainly instead of inventing a receipt.
8. Not folded into the table: `SwarmExecutor04.md:24` (finding 2, probe at `:18`) records a defect in the v2 capture tool's own first revision (manifest record kept the `./` prefix, so `--verify --rev` failed on every receipt and a one-sided tamper control would pass vacuously). It is in-round work, outside the r26-r28 lessons and spot-checks this seat was scoped to, so it is flagged here for the L1 rather than added as a lesson row.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-lesson-mistakes.md` — `## Mistakes` draft: 6 rows (`number-drift`, `reference-drift`, `attribution/stale-premise`, `vacuous`, `number-drift`, `stale-premise`), each with located evidence, captured-by and a `fail-receipt:` pointer; 4 `<landed-hash: …>` placeholders (rows 1-4); rows 5 and 6 need none (Q58 already exists at base; row 6's fix is a premise pin already exemplified on record and has no runnable red-before).
- `.ufo/waves/round-29/w1/SwarmScribe29.md` — this report.
