# SwarmConnector29 — cross-claim pattern finder (round-31 w2, read-only)

Lane tip: `2c16d018e40db7c23420a2c3bb546b52957bcc25` (branch master)
Lane base: `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc` · preregistration: `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`

## Status

`STATUS: PASS` — the four scoped pattern checks were completed at the lane tip; no landed-claim contradiction found (M1 carries are gate-clean, C1 supersession rows are unshadowed today and re-derive exactly `items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1`, C3 doc edits state no C1 literal), with hygiene findings listed below. No target relaxation proposed; nothing outside the lane was touched.

## Evidence

All commands ran read-only against the lane (or a scratch clone of it); scratch root `/fast/scratch/hyaku/souji-r31/w2-SwarmConnector29`, removed before finish. No tools installed (nothing needed).

### Q1 — M1 carries vs tip gate (rounds 26-28 at tip)

`python3 -B tools/souji-landing-gate.py --root <lane> --rev 2c16d01... --round N --base 9f17a1... --fleet-root /home/vgpnk/Projects/shokunin`

- round 26: `SUMMARY findings=0 checked_reg=63 checked_changed=21 checked_pins=13 checked_measured=3 checked_markers=26 status_lines=94 carry_heading=1 checked_reports=495`
- round 27: `SUMMARY findings=0 ... checked_markers=29 status_lines=79 carry_heading=1 checked_reports=94`
- round 28: `SUMMARY findings=0 ... checked_markers=19 status_lines=58 carry_heading=1 checked_reports=61`

- (carried unchanged through `1baf4da`, `6fdd696`, `24f343c`, `c610830`; `2c16d01` adds `amendments.txt:47` A5 and `census/round-31/records/a1-regex-receipt.txt:29,47` at the capture commit itself)

### Q2 — C1 supersession block vs later-table shadowing

ROW-shaped lines (`| Lnn | SCORECARD.md:<line> | ... | run:/record: ... |`) in the whole file at tip: exactly 40, all inside the `### Round 31 capability-cell supersessions` block (lines 367-406); ids L01-L41 except L29; the L41 row is the last line of the file (0 lines after it). Counter re-run at tip (serial, one instance):

`python3 -B tools/souji-capability-cells.py --root <lane> --rev 2c16d01... --base 9f17a1... --list-rev 1d45496...` → each of the 40 superseding rows `MATCH`; `ITEM L29 ... UNBOUND`; `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1 rev=2c16d018e40db7c23420a2c3bb546b52957bcc25` — identical to the L1 reading at 24f343c8ffc820c0f89b4252cbdc94ab9a673aab.

### Q3 — C3 SKILL/README/PROVINCE text vs C1 rows

The three doc deltas of commit `1baf4da02b71b012ee2426ea7c309496c0c3aca0` (PROVINCE.md +25, SKILL.md +3/-1, corpus/README.md +61): added lines contain zero count-shaped tokens (`\d+/\d+` or `word=N`) and none of the 40 C1 literal strings. Where SKILL.md / corpus/README.md restate C1-bound counts in pre-existing text (e.g. `cases=7 pass=7` / `cases=7 pass=3` at SKILL.md:232 vs L40/L41; `cases=20 pass=20` / `cases=20 pass=8` at SKILL.md:228 vs L36/L37; `cases=15 pass=15` / `cases=15 pass=8` at SKILL.md:229 vs L38/L39; `ids=7/7` at corpus/README.md:544 vs L05; `12/9`, `12/0`, `69/0` at SKILL.md:184,205 vs L13-L15; `36/36` at corpus/README.md:94 vs L02), the stated values agree with the C1 bindings. No contradiction.

### Q4 — commits citing `.ufo/waves/round-31/` before the capture existed

`git grep -n '.ufo/waves/round-31' 2c16d01... -- . ':!census/round-31/waves'` plus per-commit `git grep`. `.ufo/waves/round-31/` exists in no commit tree (zero paths in `git ls-tree -r` at tip; it is an ignored worktree-only artifact). Committed citations found:

- `census/round-31/records/preregistration.txt:26` — commit `1d45496` (the first round-31 commit): the policy sentence naming the wave delivery path.
- `census/round-31/apply-c3.py:3` — commit `26153a4`: `W = '/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1'` (committed one-shot apply helper).
- `census/round-31/records/amendments.txt:12` — commit `26153a4` (A1): cites `.ufo/waves/round-31/w1/SwarmCritic30.md`.
- `census/round-31/records/c2-fixture-red-before.txt:3,14,24` — commit `8024b54`: cites `.ufo/waves/round-31/w1/deliver-r31-landing-gate-precision.py` and fixture stdout lines containing `.ufo/waves/round-31/v/` paths.
- (carried unchanged through `1baf4da`, `6fdd696`, `24f343c`, `c610830`; `2c16d01` adds `amenments.txt:47` A5 and `census/round-31/records/a1-regex-receipt.txt:29,47` at the capture commit itself)
- Pre-round-31 committed records that already mention the path: `census/round-29/records/stray-r26-scribegatedraft.diff:10` (commit `8aaacf5`, round 29) documents that `.ufo/waves/round-31/wave1/` does not exist at HEAD `ba8b54b`; `census/round-30/waves/w1/SwarmExecutor02.md:57` (commit `aea0525`, round 30 capture) describes the base gate flagging `.ufo/waves/round-31/w1/X.md`.

All four cited target files (`deliver-r31-landing-gate-precision.py`, `deliver-a1-regress-full-check.py`, `SwarmCritic30.md`, `SwarmReviewer26.md`) now exist in the committed capture `census/round-31/waves/w1/`, so the C2 landed union/capture mapping would resolve them; the gate does not scan `census/round-31/records/`, hence no current red.

## Findings

1. **M1 carries are gate-clean at tip; no new pointers flagged.** Rounds 26/27/28 at `2c16d01`: `findings=0`, `carry_heading=1`, markers 26/29/19; base-gate per-round uncarried counts 18/29/19 reduce to 0 (m1-red-before.txt vs tip runs). All `resolved@` dispositions point at existing commits. Axis: none harmed (validates M1). Location: `corpus/lessons/round-2{6,7,8}.md`.
2. **Round-26 lesson carries a duplicated, empty `## Seat-reported failures` section.** Two consecutive headings (lines 98 and 105) with identical intro paragraphs; the first section is empty, the bullets sit only under the second. Origin: w1 delivery `deliver-m1-carry-r26.md` itself contains two headings and was integrated verbatim in `c610830`. Harmless to the gate (carry_heading=1) but duplicated dead bytes in an append-only carry area. Axis: calibration (bookkeeping hygiene). Location: `corpus/lessons/round-26.md:98-105`.
3. **C1 supersession rows are unshadowed today but last-row-wins by design.** The counter resolves each item from the LAST ROW-shaped line in the tail after base bytes (`sup[m.group(1)]` overwritten top-down); today the only matches are the 40 rows of the block, EOF-terminated, so nothing shadows them. Any future appended row reusing `| Lnn | SCORECARD.md:<same-line> |` (same id and base line) would silently replace this round's binding — that is the intended effective-statement mechanism, but the block has no sentinel and is not heading-anchored, so an accidental row-shaped line in a later table would be absorbed. Axis: calibration (forward fragility). Location: `SCORECARD.md:361-406`, `tools/souji-capability-cells.py:113,179-184`.
4. **C3 doc edits contradict no C1 row.** C3's added text contains no count literals at all; overlapping pre-existing doc statements agree with the C1-bound values (list in Evidence Q3). Axis: coverage/calibration — no conflict. Location: `PROVINCE.md` Round 31 boundary note, `SKILL.md` jj bullets, `corpus/README.md` Round 31 section.
5. **Committed pre-capture citations of `.ufo/waves/round-31/` exist (the round-30 C2 defect class).** Six commits in base..tip commit bytes referencing a path that never exists in git (list in Evidence Q4). Currently inert because (a) the C2 landing added the `.ufo`→`census/round-N/waves/` mapping and (b) no gate scans `census/round-31/records/`; the round-30 C2 died on exactly this shape (uncaptured wave path). Two hygiene sub-findings: `census/round-31/apply-c3.py` is a committed one-shot apply helper with an absolute machine-specific `W` path, and `census/round-31/records/a1-regex-receipt.txt` embeds absolute `/home/vgpnk/.../.ufo/waves/round-31/w1/...` invocation lines in a committed receipt (non-portable, machine-specific). Axis: operability (instrument/receipt portability), calibration (bookkeeping hygiene).

## Attack log

- Falsification attempt: tip gate for rounds 26-28 (lane root and fresh clone) → no flags (`findings=0`), target access. Attack failed: M1 carries hold.
- Falsification attempt: C1 block rows shadowed by any existing later table → exactly 40 ROW matches, all in-block, EOF-terminated; L29 absent → re-derived `unbound=1 mismatches=1` (C1 misses its frozen target by item L29, as the L1 disclosed). No new defect beyond the documented miss.
- Falsification attempt: C3 docs contradict C1 rows → no literal overlap in C3-added lines; matched pre-existing text agrees. Attack failed.
- Falsification attempt: pre-capture citations of the wave path → reproduced and listed (finding 5); none is currently gate-red, so it is a hygiene/forward-risk finding, not an attack on a landed claim.
- Verified all `resolved@` disposition commits exist; verified capture contains all cited target files; verified `.ufo/waves/round-31/` is absent from every commit tree.

## Deliveries

- This report: `.ufo/waves/round-31/w2/SwarmConnector29.md`.
- No other files written. Scratch `/fast/scratch/hyaku/souji-r31/w2-SwarmConnector29` removed. No tools installed or upgraded.
