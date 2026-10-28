# R41w2reviewer07 — corrections sweep (reviewer, wave 2)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin · tip `1d41c13574db80fdd9a4bde490b712da7ce2a85f` · read-only; no tracked file, candidate, or git state changed.
Scope: find every standing mention of the superseded statements (`appears in 9 rows`, `last TOTAL`, `first-disagreeing`, TOTAL `overwrites` / `last-wins`, the pre-r41 TOTAL docstring wording) and classify each as now-true or now-false at the tip.

## 1. Commands actually run

```
sha256sum tools/souji-worktree-drift.py
  -> b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6  (matches the frozen digest in the assignment)
git log -1 --format=%H -- tools/souji-worktree-drift.py   -> e9dc38daa67f437fcf1518e4117d684a543ad32d (r41 TOTAL fix)
```

Grep sweeps (absolute paths, lane root; results read in full):

- `TOTAL` over SKILL.md, PROVINCE.md, corpus/README.md, corpus/QUALITY.md, corpus/knowledge/, corpus/SOURCES.md, SCORECARD.md, LOG.md, AGENTS.md, MINT.md, SHONEN.md, tools/souji-worktree-drift.py.
- `TOTAL|last-wins|last TOTAL|LAST TOTAL|overwrit|first-disagree|last-agree|appears in 9|9 rows|last row|assigns the|parser assigns` over tests/fixtures/, tools/, SKILL.md, PROVINCE.md, corpus/README.md, corpus/QUALITY.md, corpus/knowledge/, corpus/SOURCES.md, AGENTS.md, MINT.md, SHONEN.md.
- `appears in 9|last TOTAL|LAST TOTAL|first-disagree|last-agree|last-wins|last wins|overwrites its|TOTAL row it reads|assigns the LAST|only the last|LAST row` over census/round-41, census/round-40, corpus/knowledge, corpus/lessons/round-41.md, corpus/lessons/round-40.md, and the root files.
- `grep --exclude-dir=census ... -e "M40-4" -e "R40-D-TOTAL" -e "R40-D-PRUNE"` and `grep -e "TOTAL row that disagrees" -e "r40-drift" -e "r41-drift"` over the whole lane (excluding .git, .jj, .ufo, census).
- `grep -c 'worktree\.c' corpus/SOURCES.md` and `^| S[0-9]` registry-row filter.
- `grep -n "total" tools/souji-worktree-drift.py` (all uses).

Probes against the tip tool (scratch `/fast/scratch/hyaku/souji-r41/R41w2reviewer07/probe/`, root = a scratch dir with `alpha`, `beta`; record bytes printed by `printf`):

```
python3 -B tools/souji-worktree-drift.py --root <scratch>/probe/root --record <scratch>/probe/good-only.tsv --skip-unrecorded
  (REPO alpha regs=1, REPO beta regs=1, TOTAL repos=2 regs=2)   -> DRIFT ABSENT x2, SUMMARY record_repos=2 ... drift_rows=2, rc=1 (parsed; TOTAL accepted)
valid-then-conflicting (TOTAL 2/2/0, then TOTAL 1/1/0)          -> REFUSAL RECORD-MALFORMED: TOTAL repos=1 but 2 REPO rows, rc=2
conflicting-then-valid (TOTAL 1/1/0, then TOTAL 2/2/0)          -> REFUSAL RECORD-MALFORMED: TOTAL repos=1 but 2 REPO rows, rc=2
bad-regs-then-good (TOTAL 2/3/0, then TOTAL 2/2/0)              -> REFUSAL RECORD-MALFORMED: TOTAL regs=3 but REPO rows sum to 2, rc=2
```

Fixtures against the tip tool (`--work` = scratch):

```
python3 -B tests/fixtures/r40-drift-record-branches.py --tool <lane>/tools/souji-worktree-drift.py --work <scratch>/r40
  case-good..case-invalid-utf8-in-comment all PASS;  SUMMARY cases=8 pass=8 fail=0;  rc=0
python3 -B tests/fixtures/r41-drift-record-order.py  --tool <lane>/tools/souji-worktree-drift.py --work <scratch>/r41
  case-total-agreeing-pair ... case-other-basename-absent all PASS;  SUMMARY cases=12 pass=12 fail=0;  rc=0
```

Registry measurement at tip: `grep -c 'worktree\.c' corpus/SOURCES.md` → 5 lines; registry rows (`^| S[0-9]`) containing the literal `worktree.c` → **3** (S009, S033, S258); rows containing `v2.56.0/worktree.c` → **0**. Remaining lines are prose bullets (SOURCES.md:241, :290).

## 2. Tool state at tip (the superseded TOTAL wording is gone from the tool)

- `tools/souji-worktree-drift.py:47-49` (docstring): "a TOTAL row that disagrees (any TOTAL row, in any position: every one is checked against the REPO rows)". **Current and true** — confirmed by the four probes above (first-bad and middle-bad refused; agreeing pair accepted).
- `:167-170` (code comment): "r40 M40-4: the loop used to keep only the last row, accepting a first-disagreeing, last-agreeing pair". Correctly dated as history.
- Dead state left behind: `:166` still does `total = {...}` (last-wins overwrite), `:186` `return rows, total`, `:288` `rows, total = parse_record(args.record)`; `total` is never read again in `run()` (`grep -n "total"` shows no use after :288). The last-wins variable survives only as discarded state. Not a sibling-file correction; noted as residual cleanup.

## 3. Standing mentions — verdict at tip

### FALSE at tip (corrected fact or superseded behaviour still standing)

| # | path:line | standing text | tip state | verdict |
|---|---|---|---|---|
| F1 | `tests/fixtures/r40-drift-record-branches.py:8-9` | "multiple TOTAL rows — the parser assigns the LAST TOTAL row it reads, so a second, conflicting TOTAL is refused as a disagreement" | Literal `total =` overwrite still exists (tool :166), but validation iterates every TOTAL (`:171`, `:176-185`). The causal reading "the last row is the one validated" is false: valid-then-conflicting and conflicting-then-valid both return rc 2 (probes). The fixture's assertions still pass (8/8). | **FALSE as a description of the semantics** (assertions still correct). Fix: state that every TOTAL row is checked and a conflicting one is refused in any position. |
| F2 | `corpus/lessons/round-40.md:49` | "`worktree.c` appears in 9 rows of `corpus/SOURCES.md`" | Tip: 3 registry rows contain the literal (S009, S033, S258), 0 contain `v2.56.0/worktree.c`. The correction exists only as I1 in `corpus/lessons/round-41.md:43-47`; the round-40 file carries no pointer or appended correction. | **FALSE and uncorrected in its own file.** Corrected elsewhere, standing here. |
| F3 | `corpus/lessons/round-40.md:115` (M40-4 evidence pointer) | "`tools/souji-worktree-drift.py:162-178` overwrites each TOTAL row, so a mismatching TOTAL followed by a matching TOTAL is accepted although the docstring … says … malformed" | Present-tense "is accepted" is false at tip (conflicting-then-valid → rc 2). The cited line range no longer names that code (TOTAL match is now :164-171; validation :176-186). | **FALSE at tip; line pointers stale.** |
| F4 | `corpus/lessons/round-40.md:117` (M40-4 fix) | "the tool-contract discrepancy is routed for a separately frozen repair" | Repair landed at e9dc38d (r41 instruments commit, tool sha b2a603cf). No appended status line in round-40.md. `corpus/lessons/round-41.md:8` says R40-D-TOTAL is "answered … by a landed artifact", but the round-40 entry itself is not annotated. | **FALSE status (routed-pending, now landed); uncorrected.** |
| F5 | `corpus/knowledge/drift-record-invalid-utf8-r40.md:57` | "alternate non-fatal decoders can satisfy both invalid-byte cases; see `corpus/lessons/round-40.md` M40-4" | M40-4 (round-40.md:112) is the TOTAL / base-fixture entry. The decoder-mutant finding is M40-12 (round-40.md:168; routed forward at round-41.md:174). Wrong pointer. | **FALSE cross-reference.** Not a TOTAL statement, but a corrected-fact-class defect in a sibling file. |
| F6 | `corpus/lessons/round-40-verifier-spotcheck.md:72` and `:75` | :72 quotes "appears in 9 rows" and measures "3 lines … (1 row, S009 …)"; :75 "R40-D-TOTAL … tool defect awaiting a separately frozen repair" | Non-author dated record. The "9 rows" quotation is the claim being refuted (method and count differ from round-41 I1: spot-check at bffcc0f counted lines/rows that cite the file). :75 status is stale (repair landed). | **Historical record with stale status (:75).** Spot-checks are append-only; no correction present. Lower severity than F2–F4. |

### Frozen artifact, now misleading (cannot be edited in this round)

| # | path:line | standing text | verdict |
|---|---|---|---|
| X1 | `census/round-40/c3-counter.py:9-10` (M15) | "the parser assigns the LAST TOTAL row it reads; the mutant keeps the FIRST, so a second conflicting TOTAL row is accepted" | Describes the r40 base mutant; the mutant is still a valid mutant of the r40 base. As a description of tip behaviour it is false, but the counter is frozen; record only. |

### Dated/historical — true as of the date written; no present-tense claim

- `LOG.md:1906` (r40 C3 entry): "a pristine TOTAL ordering that contradicts the tool docstring (M40-4/M40-8/M40-12/M40-13)". Accurate as an r40 finding; append-only log, no correction expected here.
- `LOG.md:1903`, `corpus/lessons/round-40.md:117` mention of the r40 battery's blind spot: already covered in F4.
- Round-40 wave reports (`census/round-40/waves/w1/R40connector09.md:121-124, 355-359`; `R40connector21.md:294-297`; `R40connector33.md:266-268`; `R40connector57.md:93`; `R40executor27.md:112-124`; `R40revenger12.md:25, 74`; `R40revenger36.md:5`; `waves/w1-results.json`) all describe the r40 base's last-wins behaviour. These are immutable wave evidence; not standing claims.
- `corpus/lessons/round-41.md:31, 43-47` quote "appears in 9 rows" as the filed claim and state the measured correction. Correct.

### Current and correct (no action)

- `tools/souji-worktree-drift.py:25, 48-49` — TOTAL format and "any TOTAL row, in any position" wording (verified by probes).
- `tests/fixtures/r41-drift-record-order.py:2-10` — "every TOTAL row is checked … a first-disagreeing, last-agreeing pair is refused" (12/12 pass). Lines 4-5 describe the r40 battery in the past tense; accurate.
- `tests/fixtures/r40-drift-record-branches.py:45-47,102-106` — assertions (duplicate-identical accepted, conflicting-second refused) still match the tip.
- `tests/fixtures/r38-drift-record.py:4-17`, `tests/fixtures/r39-drift-record-rules.py:14-15` — "TOTAL-before-rows accepted" still holds (probe-consistent; fixture 7/7 not re-run here).
- `corpus/QUALITY.md:242` (Q94) — a requirement; both orderings named. Fine.
- `SCORECARD.md:682, 775, 779, 803` — dated round rows; accurate. `SCORECARD.md:807` — future-tense r41 plan; fine.
- `corpus/knowledge/fleet-prune-numerator-r35.md:12-13` — `TOTAL repos=26 regs=27 prunable=0` matches `census/round-35/records/prune-census.tsv` (grep `TOTAL` output).
- `corpus/README.md:788-790` — r40 round summary, past tense.
- No hit in SKILL.md, PROVINCE.md, corpus/README.md (beyond the above), SCORECARD.md (beyond the above), AGENTS.md, MINT.md, SHONEN.md for `last TOTAL`, `LAST TOTAL`, `overwrites`, `last-wins`, or the pre-r41 "a TOTAL row that disagrees" wording outside `tools/souji-worktree-drift.py:48`.

## 4. Adjacent observation (outside this item, not scored)

`grep -n "r40-\|r41-" SKILL.md` returns nothing: the gate registry has rows for r38/r39 fixtures (`SKILL.md:276-280`) but none for `r40-drift-record-branches.py` or `r41-drift-record-order.py`. Not a superseded-fact defect; flagged for the registry owner.

## 5. Verdict

**Corrections sweep: NOT CLEAN.** The tool itself is correct at tip (docstring wording and behaviour agree, verified by four probes plus two fixtures at 8/8 and 12/12). Standing defects are sibling-file statements that were true at r40 and are now false or unannotated:

- F2 `corpus/lessons/round-40.md:49` "appears in 9 rows" — false (3 registry rows); corrected only in round-41.md I1.
- F3/F4 `corpus/lessons/round-40.md:115, 117` — "is accepted" and "awaiting repair" — false at tip; no appended correction.
- F1 `tests/fixtures/r40-drift-record-branches.py:8-9` — "the parser assigns the LAST TOTAL row it reads" as the refusal mechanism — false as a description; assertions still pass.
- F5 `corpus/knowledge/drift-record-invalid-utf8-r40.md:57` — cites M40-4 for a finding that is M40-12.
- F6 `corpus/lessons/round-40-verifier-spotcheck.md:75` — "awaiting a separately frozen repair" — stale status.

Residual: `tools/souji-worktree-drift.py:166, 186, 288` keep a dead last-wins `total` binding (no behavioural effect; cleanup candidate).

Verification gaps: I did not run the committed R41 counters (C1/C2/C3/R1); this item is a text sweep plus tool probes. I did not re-derive the C1 I1 count with the committed counter (counted directly with grep). I did not read R41 wave-1 reports, since this item names none.

No candidate written; no tracked file, git state, or fleet file modified. Scratch dir removed after this report was written.
