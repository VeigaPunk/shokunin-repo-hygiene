# S90Connector — souji r90 connector: overlap table, sibling ownership, bounded r91 data-walk, dedup

Seat S90Connector (connector, leaf; no subagents, no peer messages). Lane `souji-shokunin`
(`/home/vgpnk/Projects/shokunin/souji-shokunin`, id `souji`). Lane base
`bd760432df2cc3ba6c5f1ccc540b050fe2ac09e2` (r89 closed, spot-check `corpus/lessons/round-89-verifier-spotcheck.md`);
lane HEAD at measurement `fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f` (F, the preregistration alone).
Measured 2026-11-08 11:44–11:56 -03, Python 3.14.8 / git 2.56.0. No installs, no upgrades, no pacman, no
host service, no sysctl. Only read-only git (`log`, `show`, `cat-file`, `ls-files`, `status`, `diff`,
`check-ignore`, `rev-parse`, `merge-base`, `grep` at revisions). Nothing in the lane was written except this
report and this seat's directory.

Assignment: prior-art/overlap scan for the round's two claim rules, sibling-lane ownership, the bounded r91
planning data-walk (the spot-check's routed defects 1–11 and the r89 C1 carry list), and dedup against the
wave's other seats. One bounded proposal, no dispatch, no integration.

## 0. What was read (and what "recorded" means here)

Lane: `census/round-90/preregistration.txt` (150 lines); `corpus/lessons/round-89-verifier-spotcheck.md`;
`plans/round-88.md`, `plans/round-89.md`, `plans/round-90.md` (uncommitted); `SCORECARD.md` r85–r90 blocks;
`corpus/QUALITY.md` Q159/Q161/Q163/Q164; `corpus/knowledge/{nel-byte-character-pair,decode-escape-order,
one-escaped-diagnostic-line,splitlines-line-model,machine-parsed-path-spelling,own-tree-pointer-binding}.md`;
`corpus/SOURCES.md` S278/S348/S351/S353 and the uncommitted S353 row; `census/round-{77,87,88,89,90}`
instruments, populations, ledgers, controls and records; `census/round-90/w1-spec.json`;
`.ufo/reports/round-89/souji.md` (fleet repo, read-only).
Wave: every `.ufo/waves/round-90/w1/*.md` present at 11:50–11:56 and the seat artifacts under
`S90ExecC2/`, `S90ExecC3/`, `S90Labrat/`, `S90MutCounter/`, `S90ScoutSources/`.
Siblings (read-only, under `/home/vgpnk/Projects/shokunin/`): each `*-shokunin/corpus/QUALITY.md` and
`corpus/SOURCES.md` (grep) plus the knowledge entries they name; full corpora and gate code not read.

"First recorded" below means the earliest *committed lane artifact* (code, corpus entry, plan/lesson,
SCORECARD/LOG) that states the rule. Instrument bytes cited are committed at HEAD unless marked uncommitted.
All eight prereg-pinned instruments hash equal to the prereg (table §8.1), and `head -n 59` of the r90
population is byte-identical to the r89 population (`PREFIX-57-ROWS-BYTE-IDENTICAL`), so the overlap scan is
over the same bytes the round is being judged on.

## 1. Overlap table A — the NEL/0x85 (raw byte vs character) spelling rule

| # | round | first record (path / commit) | what that record actually states | delta vs r90 C2 | does r90 evidence change its disposition? |
|---|---|---|---|---|---|
| A1 | r55 | `corpus/knowledge/splitlines-line-model.md` + S278 (2026-11-03) | `str.splitlines()` breaks on `\x85` (NEL) among VT/FF/FS/GS/RS/U+2028/U+2029; a NEL-named deletion is uncounted under a repository-local `core.quotePath=false` | character-as-line-boundary only; the byte/character spelling pair is never mentioned | no — r55 is about counter line numbering, and r90's rule is about a record cell's spelling; both can hold |
| A2 | r87 | `f36fcf55` (`tools/souji-record-agreement.py`) + `corpus/knowledge/machine-parsed-path-spelling.md` | the escape branch `elif o < 0x20 or o == 0x7F or o == 0x85: \xNN` is written, and U+2028/U+2029 take `\uNNNN` (S87Sentinel F4). This is the branch where the character U+0085 and the surrogate U+DC85 later collide once `surrogateescape` lands | creates the collision's origin; the r87 prose records the `\uNNNN` precedent, not the 0x85 pair | yes, but only the *code* disposition: r90 splits the branch (character → `\uNNNN`, surrogate → `\xNN`); the r87 record itself is neither falsified nor widened |
| A3 | r88 | `corpus/knowledge/one-escaped-diagnostic-line.md` + Q163 (QUALITY:404) | a diagnostic cell is ONE escaped line; escape the documented `str.splitlines()` set "not only the two characters the transport happens to produce", naming NEL; head/tail bound | first states NEL must be *escaped*; it does not distinguish the character from the byte, and its "injective spelling" reading is what r89 falsifies | yes, partially: the escape-set rule stands; the entry's implicit injectivity claim is narrowed by r90's `nel-byte-character-pair.md` (its "Boundary" section) |
| A4 | r89 | `plans/round-89.md` A2; SCORECARD r89; Q164 (QUALITY:410) | first *measured* record of the collision: raw `0x85` and the UTF-8 NEL both render `\x85`; routed to r90. Q164 still states, unqualified, "the decode must be injective on the bytes" | first records the defect, not the rule | yes: r90 lands the fix; but Q164's unqualified clause is still in the committed QUALITY file at 11:56 (Q165 does not exist yet — `grep '^| Q165'` rc 1). This is an open disposition item, not a claim issue |
| A5 | r90 | prereg C2; `4cb3a06f`; uncommitted `corpus/knowledge/nel-byte-character-pair.md` (4,272 B at 11:47); uncommitted S353 row | the rule: raw byte 0x85 keeps `\x85`; the CHARACTER U+0085 takes `\u0085`; KFF9/KFF10; `_one_line` deleted | this *is* the claim | n/a — no artifact seen widens the wording; the labrat's exhaustive sweep (below) is bounded support, and the elided-middle identity is the prereg's own stated limit |

Verdict A: the *defect* is first recorded at r89 (A4); the *rule as an obligation* is first recorded at r90
(A5); the material that makes the rule non-arbitrary (NEL is a line boundary; `\uNNNN` is already the branch's
spelling for LS/PS; `surrogateescape` maps the byte to a lone surrogate) is r55/r87/r88/r89 in that order.
r90's evidence changes the disposition of A2's code (repaired) and narrows A3/A4's injectivity sentence; it
does not change A1 and does not widen anything.

## 2. Overlap table B — the `_ledger` malformed-row guard (`len(r) < 3`)

| # | round | first record | what it states | delta vs r90 C1 | disposition change |
|---|---|---|---|---|---|
| B1 | r77 | `43822328`, `census/round-77/c2-pointer-counter.py` (the only file at that commit containing `len(r) < 3`; guard inherited unchanged through r79/r85/r86/r87 counters, each `grep -c` = 1) | the guard exists in code; no prose record in the r77 lesson (`grep '_ledger\|malformed\|len(r)' corpus/lessons/round-77.md` empty) | the clause r90 binds; unrecorded for 11 rounds | none for r77 itself |
| B2 | r88 | `plans/round-88.md` A8 (F3/F4); `corpus/lessons/round-88.md:78` (carried list) | first prose record: "the `_ledger` malformed-row guard (`len(r) < 3`, `m17c`) … unrowed"; `LD2` (2-column row) is its measured design; carried to r89 | first names the clause and the candidate mutant; the r88 filed set has 12 members and no `m17c` (member list at `e60ea25f`), so the mutant text is first *filed* at r89 | r90's LD2b is the r88 design finally landed; B2's "unrowed" is what r90 falsifies (if the predicate holds) |
| B3 | r89 | `plans/round-89.md` A1; `S89MutCounter` F1; `S89Sentinel` §3.4; SCORECARD r89 | first measurement: `LD2` appends `P02\tABSENT`, but `P02` is already in the frozen r77 ledger, so pristine and `m17c` both refuse on the duplicate leg; the reachable shape is `ZZ9\tABSENT` (absent id); `LD2b` is carried, not filed | first measurement of reachability and the first LD2b design; first recorded *falsification* of a binding | yes: r90 changes it from "measured, not landed" to "landed" iff C1's predicate holds |
| B4 | r90 | prereg C1; `census/round-90/c1-false-rows.tsv` (`d64d7695…`, 60 lines = 2 comments + 58 rows); LD2b = line 60 | the row is filed and the battery target is 31 kills | the claim | in flight: `records/c1-after.txt` had no `SUMMARY` at 11:56 (26 lines, ends at `m8`, sha `eacf0b63…`; live pids `l1-after`/`l1-both`); see §6 |

Verdict B: the *clause* is first recorded in code at r77 (B1), first recorded as a target at r88 (B2), first
*measured* reachable at r89 (B3), first *landed* at r90 (B4). r90's evidence changes the disposition from
"measured, not landed" to "landed" — which is exactly the r89 spot-check's routed defect 3 and the claim
itself; no sentence widens. A corroborating fact for B4's premise (independent of the seats' batteries):
`census/round-77/c2-pointer-ledger.tsv` has 32 lines, `P02` at line 3, and no `ZZ9` (`grep -n '^ZZ9'` rc 1).

## 3. Sibling-ownership verdict

Read: each sibling `*-shokunin/corpus/QUALITY.md` and `corpus/SOURCES.md` (grep for NEL/U+0085/0x85/
surrogateescape/splitlines/one-physical-line/malformed-ledger) and the knowledge entries those hits name.

**NEL/0x85 rule — no sibling lane owns it; one boundary must be stated.**
- `kumitate-shokunin` owns the *complementary* NEL rule, for registry row readers, not record cells:
  `corpus/knowledge/row-id-reader-class.md:148-150` — "**NEL (U+0085) is not JS white space.** A NEL pad or
  NEL-prefixed row is invisible to both JS readers while the census reads `E02`/not-a-row; … Do not 'fix' NEL
  into the pad class." Its `sources-check-cell-trim-class.md:47` table also records `NEL | U+0085 | 1 | — | — | strips`
  for the census trim. This is the pad/indent/record axis of `SOURCES.md` row parsing.
- souji's r90 rule is the *writer* side of a delegated-stderr cell: how to *spell* the character so it
  cannot collide with a raw byte. Same character, different instrument, opposite decision (kumitate: a reader
  must not strip it; souji: a writer must escape it). **Route:** a future souji move about NEL as a pad,
  whitespace class or `SOURCES.md` row boundary goes to kumitate, not souji; a kumitate move about escaping a
  NEL inside a one-line record belongs to whichever lane writes that record, not to its reader class.
- Adjacent but not contested: `kotodama-shokunin/corpus/QUALITY.md` criterion 22 requires a *Gate record* to be
  "one physical line" (record shape, no escaping grammar); `kengaku-shokunin/corpus/knowledge/tb2-password-recovery-grader.md:228`
  counts NEL among "non-newline separators" in a grader file (an observation, not a rule); `mado-shokunin`,
  `chousa-shokunin`, `kake-shokunin`, `tsukuroi-shokunin` have no NEL/escaping rule in QUALITY/SOURCES (the
  grep hits are unrelated uses of "escape"/`surrogateescape`). No sibling holds a `splitlines`/one-line
  diagnostic-cell criterion (grep for `splitlines|one physical line|physical line` over all sibling
  QUALITY/SOURCES: only souji's Q91/Q159/Q163/Q164 and the unrelated kotodama criterion 22).
- **Verdict:** no contested scope. The r90 knowledge entry / lesson should carry one explicit boundary
  sentence: the rule is about the escape spelling in a delegated-stderr cell, **not** about NEL's whitespace or
  pad class in registry readers (kumitate's rule), and not about newline *conventions* (UAX #13, which the
  scout rejects for exactly that reason).

**Ledger-malformed rule — no sibling lane owns it.**
- `kagi-shokunin/corpus/knowledge/claim-ledger.md` is a revision-stamp ledger (`path<TAB>sha256<TAB>lines<TAB>bytes`)
  with claim/citation classes; no `_ledger` tuple reader and no 2-column row guard.
- `lore-shokunin/corpus/knowledge/2026-10-12-malformed-error-patterns.md` is a JSON-bible malformed-input
  census (fixtures), not a ledger guard. `revenger-shokunin` owns RE evidence-ledger *discipline* (Evidence IDs,
  observation/inference/unknown), not a parser. `kumitate-shokunin/corpus/knowledge/row-id-reader-class.md` is
  the `SOURCES.md` row-id class, not souji's ledger.
- `tameshi-shokunin` owns the reusable *method* (mutation testing, fail-closed arms, verdict-line discipline)
  and explicitly "never edits a sibling's gate code"; the concrete guard and its population are souji's. If the
  lane ever wants the general rule ("a row binds a clause only when the clause-dropping mutant survives every
  already-pinned population" — Q162) generalized across lanes, that is tameshi's, by evidence from two lanes.
- **Verdict:** no contested scope; no routing needed beyond naming tameshi as the method owner if Q162 is ever
  claimed general.

## 4. Bounded r91 candidate list (no plan beyond r91)

Status at 2026-11-08 11:59. "Cheapest next measurement" is the least run that answers the candidate; cost is
the frozen instruments' cost (the r89 spot-check measured the 16-mutant × 2-set battery at 1,695.8 s; the r90
harness single-arm run measured 76 s by S90ExecC3).

### 4a. The r89 spot-check's routed defects 1–11

| # | candidate | status at 11:57 | cheapest next measurement |
|---|---|---|---|
| 1 | Commit the wave evidence (major) | **OPEN.** `.ufo/waves/` is still ignored (`.gitignore:1`); `git ls-files .ufo/waves/round-90` = 1 (`build-spec.py`); `git status --porcelain --ignored .ufo/waves/round-90` shows 6 `!!` entries (w1-dispatch, w1-run.err, w1-spec, w1.ready, w1.ready.dispatched, `w1/`). r89's own w1 reports are still absent: `git ls-files .ufo/waves/round-89` = 7 structural files, none under `w1/`. `plans/round-90.md` A0.6 promises `jj file track --include-ignored` at landing | one command after landing: `git ls-tree -r <r90 tip> -- .ufo/waves/round-90 \| wc -l` must equal the seat-file count, and `git check-ignore -v .ufo/waves/round-90/w1/S90Connector.md` must not resolve inside the tree |
| 2 | File the report after the ledger is final | **OPEN/pending.** `census/round-90/claims.json` does not exist (`ls census/round-90`); the pre-file gate needs it | `python3 /home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py --lane souji --round 90` immediately before filing; quote `findings=0` |
| 3 | C1: bind `m17c` with `LD2b` | **TARGET RE-DERIVED by a non-L1 seat; the filed receipt was still being rewritten at 11:59.** `records/prefreeze-c1-both.txt` completed at 11:55:50 with `SUMMARY mutants=16 sets=r89,r90 pristine_r89=ok pristine_r90=ok killed_r89=15 killed_r90=16 killed_total=31` (feasibility, not after-data); S90Reviewer's report §2.1 states the same target cell-for-cell with EXIT 0 and its control `killed_r89=15`, `m17c` alive, EXIT 0 (its cited `c1-after-official.txt` was **not yet in its seat dir at 11:57** — a receipt to confirm before filing); ExecC1/ExecC3/MutCounter's harness runs show LD2b is the sole row red under `m17c` (57/57 r89 rows green). The L1's `records/c1-after.txt` was 41 lines with no `SUMMARY` at 11:59 (rewritten in place by a later run) | re-check `grep -c SUMMARY census/round-90/records/c1-after.txt` = 1 and its sha before filing; the frozen command costs ~28 min under the 11+ live batteries, but a non-L1 seat has already measured it |
| 4 | C2: U+0085 spelling + dead `_one_line` | **ATTACKED and corroborated.** `records/c2-after.txt` (847 B, mtime 11:46) reads `SUMMARY cases=12 tool_pass=12 before_pass=10`; S90ExecC2 independently re-ran after/control/K4 (12/12 EXIT 0; 10/12 EXIT 1; `rows=12 mismatches=0 errors=0`); S90Reviewer reproduced 12/12 and the control and built two one-edit variants that fail EXACTLY KFF9 and EXACTLY KFF10 (so the pair check does not collapse them); S90Labrat's exhaustive sweep shows exactly one spelling change and zero residual pipeline collisions over its domain | none for the claim; residual r91 work is the r89-fixture arm artifact (row 22) and Q164's clause (row 23) |
| 5 | `corpus/README.md` coverage map/frontier | **IN FLIGHT (uncommitted).** Working-tree `corpus/README.md` +8 lines adds a "Frontier (r87–r90…)" section with r87, r88, r89, r90 entries (4 `r90\|round-90` hits); it is ` M` at 11:56, not committed | `git show <r90 tip>:corpus/README.md \| grep -c "nel-byte-character-pair"` after landing |
| 6 | Capability table: malformed-row row is "measured, not landed" | **OPEN.** `SCORECARD.md:2139` still reads "a malformed-row binding whose id is absent from the ledger (measured, not landed) … r89 (design)" | after C1's verdict: if it lands, replace with a landed row citing the battery/counter; if it fails, move it to planned. One grep verifies |
| 7 | Role split: 3 executors + planner seat (or record the waiver) | **SATISFIED in r90, waiver recorded in the prereg, not the plan.** `w1-spec.json` items = 3 executors + mutation-tester + 2 reviewers + critic + sentinel + revenger + scout + scribe + connector = 12; the prereg ROUND SHAPE says "The L1 holds the canonical planner seat (the validator rejects `planner`)" | none; r91 plan can copy the waiver sentence |
| 8 | Trend token exactly one of `improved\|harmed\|unchanged\|unprovable-but-better` | **OPEN historically.** The committed fleet `round-89/souji.md:176` still reads "discernment: mixed → improved by the honest stop" (not editable now). The r90 report does not exist yet (`.ufo/reports/round-90/` has 11 files, none `souji.md`) | grep the r90 report for `mixed`/`→` before filing; one line |
| 9 | Landed-changes LOG column for `claims.json` | **PENDING.** No r90 report/claims yet | grep the r90 report's landed-changes row for the round-90 LOG entry |
| 10 | S351 title version (3.14 vs the 3.15.2 capture) | **OPEN, not attacked.** Committed `corpus/SOURCES.md:292` S351 still opens "Python 3.14 `codecs`…" while its capture names the 3.15.2 book (the spot-check's defect 10). The r90 S353 row is correct (Unicode 18.0.0 rev 57, page date 2026-09-01) | an appended correction row (SOURCES rows are append-only) or a recorded acceptance; one row |
| 11 | SCORECARD order (r90 planned block above r89) | **FIXED in the working tree (uncommitted).** At 11:56: `### Planned (r89)` line 2142, `### Planned (r90, as filed in r89 — historical)` line 2153; at r89 close (`git show bd760432:SCORECARD.md`) the order was `Planned (r90)` 2142 then `Planned (r89)` 2153 | one heading grep after landing. Residual: the r89 planned block now sits *after* the r89 measurements/capability rows, unlike r85–r88; r91 close should put `Planned (r91)` before its measurements |

### 4b. The r89 C1 carry list (SCORECARD "Planned (r90)" → still open)

| # | candidate | status at 11:57 | cheapest next measurement |
|---|---|---|---|
| 12 | `LD1c` (same-class duplicate) and `LD1d` (identical duplicate) bind the class-conflict readers | **PRE-SCORED, not filed.** S90MutCounter `q162-probes.json` (922 B) holds exactly `ld1c-class-keyed`, `ld1d-conflict-keyed`, plus `nf6i2-last-occurrence`, `nf6j-pathch-narrow` | score the pre-filed mutant on r89+r90 with the existing battery; if it survives both, add the row type + row and re-run for the kill. ~28 min per 2-set battery |
| 13 | `NF6i2` (other occurrence order) | same receipt, pre-filed | same path |
| 14 | `NF6j` (six remaining PATHCH predecessors) | same receipt, `nf6j-pathch-narrow` | same path; note r88 F7 says the `,`/`;`/`:` punctuation members are dead (only `.` in PATHCH), so a punctuation-predecessor row cannot bind anything |
| 15 | p2 basename granularity, p3 punctuation lookahead, p7 `_regular` symlink leg, p8 `token_ok` hyphen marker, `fleet:` symlink leg | **UNATTACKED in r90** (no seat artifact names them); each is a single-spelling survivor from r85–r89 | one candidate mutant per clause scored on the pinned sets first (Q162), then a row; the r88 A8 F5/F7 designs are the starting text |
| 16 | battery `--only`/`--expect-killed` stale defaults | **OPEN.** `census/round-90/c1-clause-battery.py:114` `--only` default is `"r85,r86"`; `:116` `--expect-killed` default `None`; `:171-173` returns 0 when no target is given. A bare invocation therefore scores the wrong pinned populations and exits 0 | one bare `--work <empty>` run (prints `sets=r85,r86`, exit 0) to demonstrate; the fix is to default to the current round's pins or refuse when either is omitted |
| 17 | C2 carries: forged-`CLEAN` fail-open (S88Sentinel F3); pid-reuse row, parent-before-child, termign-fork/p5-late-term, strace-robust settle (r85/r86); `_regular` pathspec framing; quarantine intro-blob digest row; r79 gate re-measurement; check-4 300 s backstop; r76 K03/K04; r17 240 s runners; inherited K3 tally row (r86 A4) | **UNATTACKED in r90** (the round spends both claims on LD2b and the 0x85 pair) | re-run each round's own frozen counter/fixture from the round that designed it; cost as then. Start with S88Sentinel F3's reproducer, the only one with a one-command receipt |

### 4c. Candidates the round's own stated limits leave open (r90 → r91)

| # | candidate | status at 11:57 | cheapest next measurement |
|---|---|---|---|
| 18 | 4+-column ledger row (C1 limit ii) | **NOT BINDABLE (close it).** S90MutCounter's measured matrix (`spellings.json` + probe) shows the frozen reader accepts ≥3 columns (the frozen r77 ledger's own rows are 4 columns; pristine and `m17`/`m17b` accept a 4-column `ZZ9` row and refuse it only on the id); the only `!=3` spelling (`s1-exact-width`) refuses the frozen 31 rows as well (`+31 frozen`), so it is killed by the existing population, not by a new 4-column row. There is no clause to drop: the guard is a minimum-width guard | none for r91; record the shape as a named limit of the population (limit ii) instead of a row. One battery run would only re-confirm s1's death |
| 19 | 1-column ledger row (C1 limit ii) | **VIABLE, MUTANT PRE-FILED.** The matrix shows pristine/`m17`/`m17b`/`s2` refuse a 1-column `ZZ9` row by the same length leg; `s3-equal-two` (`== 2`) CRASHES on it (IndexError, no marker) while staying green on the frozen 3-/4-column rows — so s3 is a clause-dropping spelling that only a 1-column row can kill | score `s3-equal-two` on r89+r90 first (Q162 — it should survive, because no pinned population has a 1-column row); if it survives, add a 1-column row type to the harness and re-run. ~28 min per 2-set battery |
| 20 | CRLF-wrapped, header, blank-line-only ledger rows (C1 limit ii) | **NOT BINDABLE (close them).** S90MutCounter's matrix: a blank line and a `# header` line are *skipped* (rc 0) by pristine and by every surviving spelling — they never reach the length guard; `s1` refuses them only because it refuses everything 4-column. No measured branch strips `\r`, so a CRLF row only changes the last field's text, not a clause | none; record the three shapes as named limits (limit ii), not rows. A CR-strip mutant would have to be invented and would be a different clause |
| 21 | The line-binding (`which leg refused`) question | **ATTACKED and measured three ways.** S90MutCounter's counter-level sole-killer table (pristine/`m17`/`m17b` keep the marker; `m17c` raises IndexError with no marker under LD2b, and still refuses LD2's `P02` on the duplicate leg), S90ExecC3's harness run (only LD2b red, 57 r89 rows green) and S90ExecC1's four-run harness matrix (pristine 0 mismatches; `m17` 2 = LD1+LD1b; `m17b` 1 = LD1b; `m17c` 1 = LD2b) agree | no new run; record the single-row attribution in the lesson |
| 22 | The r89 fixture's no-delta guard firing when the r89 bytes are BOTH arms | **NEW and arm-dependent — do not record it as "the r89 fixture fails on the r90 tool".** S90ExecC2 passed the r89 bytes as `--before` to `tests/fixtures/r89-k4-flagfail.py`, whose `--before` contract is the r87 tool bytes; both arms then read 10/10 and the fixture's own "no measured delta" guard exits 1 (`receipt-r89fixture.txt`). S90Reviewer ran the same fixture with its intended before arm and read `SUMMARY cases=10 tool_pass=10 before_pass=8`, EXIT 0 — every r89 case passes on the r90 bytes. So the exit-1 is a mis-armed control, not a tool defect | already measured twice; the lesson should say "the r89 fixture is superseded by the 12-case r90 fixture; its exit code depends on the `--before` arm" and must not cite its exit 1 as a verdict |
| 23 | Q164's unqualified "the decode must be injective on the bytes" (QUALITY:410) | **OPEN.** Q165 absent (`grep '^| Q165'` rc 1); the uncommitted `nel-byte-character-pair.md` "Boundary" section narrows it, but the committed QUALITY row still states it unqualified | land Q165 (or amend the entry's boundary) naming the enumerated pair, the elided-middle limit and the 202-byte window; one row |
| 24 | S353 quote locator ("tag-stripped offset 82360") | **NEW, measured by S90ScoutSources** (`receipts/verify.out` §4): full 18-word quote begins at byte 82357 under `drop tags, '\n\t'→' '`; 82360 is the same sentence *minus its leading "The"*. Present in the frozen prereg line 128, the uncommitted S353 row (`SOURCES.md:292`) and the uncommitted knowledge entry (lines 8, 51). Also the tr13 tombstone quote is counted "(24 words)" in the knowledge entry while `wc -w` gives 25 | correct the uncommitted knowledge entry and SOURCES cell (editable pre-commit) to 82357 or "sentence minus 'The'", and record the frozen-prereg locator as a plan amendment (a locator slip, not a predicate falsification); `wc -w` is the word-count check |
| 25 | `census/round-90/srcs/tr13.html` untracked but cited by the uncommitted knowledge entry | **NEW, S90ScoutSources §6**: capture is byte-identical to live (`bfa7f97b…`) and cited at knowledge lines 55–56, but `git ls-files census/round-90/srcs/` lists only `LineBreak.txt` and `tr14.html` | land it with the knowledge entry, or drop the capture citation; `git ls-files` check |
| 26 | `_escape_text` on arbitrary `str` still collides for a lone surrogate U+DC85 | **NEW, S90Labrat §2.3**: `_escape_text("\udc85")` = `\x85` on BOTH arms; no feeder passes lone surrogates (the FLAGFAIL path feeds `_decode_record`; the other two call sites at tool lines 396 and 411 receive writer stdout decoded with `backslashreplace` at tool lines 372-373, `grep -n` verified), so the pipeline is not falsified — but injectivity is a pipeline property, not a function property | one static claim + the three call sites (already read); a r91 candidate only if a new feeder can pass text without `_decode_record`/`backslashreplace` |
| 27 | Wave-evidence durability at landing (A0.6) | **PROMISED, UNVERIFIED** (see row 1) | one `git ls-tree` after landing |
| 28 | README draft asserts C1 numbers before the after receipt is final | **NEW (this seat), still live at 11:57.** `corpus/README.md` (working tree) states `killed_r89=15 → killed_r90=16, killed_total=31` and points at `census/round-90/records/c1-after.txt`. The pre-freeze `prefreeze-c1-both.txt` completed at 11:55:50 with that exact `SUMMARY` (so the numbers are grounded as feasibility), but the filed `c1-after.txt` was 34 lines with no `SUMMARY` at 11:57 and is being rewritten in place (`> file` truncation) by a later run; S90Reviewer compares its own run to that path and its §2.6 notes the file "was being written when first read" | re-check `grep -c SUMMARY census/round-90/records/c1-after.txt` = 1 and record the filed sha immediately before commit; if the run restarts again, cite the reviewer's stable receipt instead or re-run once and freeze it |

## 5. Dedup — visible wave findings vs prior rounds, and loci the round does not attack

Reports present at 11:57 (sizes/mtimes): `S90ExecC3.md` 24,542 B 11:54; `S90Reviewer.md` 21,636 B 11:55; `S90Labrat.md` 18,030 B 11:53; `S90ScoutSources.md` 17,210 B 11:54; `S90ExecC1.md` 6,401 B 11:56; `S90MutCounter.md` 5,475 B 11:54; `S90ExecC2.md` 13,500 B 11:50. Skeletons only (64–157 B, 11:47): `S90Critic`, `S90Reviewer2`, `S90Sentinel`, `S90Scribe`. `S90MutCounter`'s §§1, 3, 4, 5 were still placeholders at 11:57 (its artifacts carry the measurements).

**Duplicates of prior-round findings (confirmation, not new findings):**
1. `S90ExecC2` §"Hand-driven pair" and §Arm A/B reproduce the r89 collision and the r89 control numbers —
   duplicates `plans/round-89.md` A2 and `S89ExecC2` §6 (prior round). Expected of a verifier; not counted as
   a new finding.
2. `S90ExecC2`'s, `S90ExecC3`'s, `S90ExecC1`'s, `S90Reviewer`'s and `S90Labrat`'s re-checks of the eight
   instrument hashes, the ten-r89-case byte-identity and the `_one_line` zero-caller proof duplicate the
   prereg's pre-freeze receipts and each other (five-way). `S90Reviewer` §2.6's line-by-line comparison to the
   L1 receipt duplicates the same numbers a third time. The new parts are listed below.
3. `S90Labrat` §4 "elided middle" (p1==p2 on both arms) duplicates the prereg's own stated limit (ii) — the
   labrat labels it so; it must not be filed as a defect.
4. `S90ScoutSources` §5 census (rows 275, E=0, W04=89) duplicates the committed pre-freeze receipt
   `census/round-90/records/sources-census-before.txt` (the scout says the output is byte-identical) — the
   duplicate is the point of a stability check, not a finding.
5. `S90ScoutSources` §4's UAX #13 reject duplicates the uncommitted knowledge entry's own reject (same URL,
   same tombstone) — confirmation; its archived-content reading and word-count correction are new.

**New wave findings (not prior-round duplicates):**
- S90ScoutSources: (a) the 82357/82360 locator slip in the prereg + S353 row + knowledge entry; (b) the tr13
  tombstone quote counted 24 words but `wc -w` = 25; (c) `tr13.html` untracked while cited; (d) the S353
  "capture lines 2873-2879" range is loose (row 2873–2876, quote 2878–2879).
- S90ExecC3: (a) the battery's r89 PINS entry *relocation* (`HERE` → explicit `census/round-89/` path) is a
  second changed file beyond "population and harness only" — the prereg's C1 stated limit (i) sentence is
  narrower than the file set (population + harness + battery pin/docstring + mutants note), an
  Amendment-59 narrowing candidate that does not touch the predicate; (b) the LD2b single-row harness
  attribution (only LD2b red under `m17c`, 57 r89 rows green).
- S90ExecC2: the r89 fixture's no-delta guard exit 1 is **arm-dependent** (r89 bytes as both arms); with the
  fixture's intended `--before` the reviewer reads 10/10/8 EXIT 0 — see §4c row 22. The arm artifact is new;
  the phrasing "the r89 fixture fails on the r90 tool" is not supported.
- S90Reviewer: (a) two one-edit tool variants fail EXACTLY KFF9 and EXACTLY KFF10 — new evidence that the pair
  check does not collapse the two cases; (b) an INFO scope note: `_escape_text` is shared by three cells
  (FLAGFAIL, receipt-writer-refused exit line, FORGED/REFUSED payload), and U+0085 in the other two also changes
  spelling from `\x85` to `\u0085`; no committed fixture asserts the old spelling, and both spellings are one
  line, so no verdict changes — this should be a lesson sentence (the claim's limit (i) says "covers
  `_escape_text`", which is accurate and must not be read as "FLAGFAIL only"); (c) an offset LOW finding that
  independently reproduces the scout's 82357/82360 disambiguation (two-seat agreement, so it is not a duplicate
  of a prior round).
- S90MutCounter: the six-spelling × seven-shape matrix of the `_ledger` guard (1-column, 2-column, 3-column,
  4-column, duplicate-id, blank, `# header`) with the counter-level sole-killer table — new; it closes the
  4+-column and blank/header candidates (§4c rows 18, 20) and makes the 1-column candidate viable (row 19).
  Its sole-killer table duplicates ExecC1/ExecC3's harness attribution (three-way confirmation, listed above).
- S90ExecC1: the four-run harness matrix (pristine/m17/m17b/m17c → 0/2/1/1 mismatches, the single m17c row
  being LD2b) — new single-row attribution; its precision notes (the mutants FILE is not byte-identical, only
  the members; the battery/harness diff classes) duplicate S90ExecC3's inventory and my own §8.3 observation.
- S90Labrat: exhaustive 128×128 spelling map (after 0 cross pairs, before 1), full 1,112,064-code-point ×
  256-byte cross-check (after 0, before 1), 2-token composition (after 0, before 509 outputs / 514 pairs),
  prefix-freeness 0 violations (so unique decodability for every concatenation over the swept alphabet), and
  the lone-surrogate residual of `_escape_text` as a function.
- S90Connector (this seat): README draft asserts the C1 after numbers while `c1-after.txt` is mid-run (§4c
  row 28); the r89 wave evidence is still untracked; Q164's unqualified clause; the S351 title still 3.14.

**Loci the round does not attack (no seat, no claim reaches them):**
1. Wave-evidence durability at landing (spot-check defect 1). No seat verifies the `jj file track`; A0.6 is a
   promise. (The connector measured only the pre-landing state.)
2. `--expect-killed`'s `None` default (no target → exit 0) and `--only`'s `r85,r86` default. No seat; the
   claim's command always passes both.
3. The S351 title version (defect 10) and the new S353 locator/word-count/untracked-capture items (§4c rows
   24–25). The scout measured them; no seat owns the SOURCES/knowledge edits.
4. Q164's unqualified injectivity clause (row 23). The scribe's Q165 is planned but absent; no seat owns the
   correction.
5. The forged-`CLEAN` fail-open (S88Sentinel F3) and the r85/r86 C2 carry list (row 17). Both are carried,
   not attacked, by design.
6. `_one_line`'s runtime-dispatch limit (prereg C2 limit iv): static grep + import only; no dynamic probe in
   any seat (labrat states the same limit).
7. The r89 fixture's exit-1-on-new-tool artifact (row 22): observed by one seat; no owner for the lesson note.
8. The C1 carried clauses (LD1c/LD1d/NF6i2/NF6j, p2/p3/p7/p8, `fleet:` symlink) are pre-scored by
   S90MutCounter's artifacts but not attacked in r90 and not planned beyond r91 here.

## 6. Evidence durability and chronology observations (measured at 11:57)

- HEAD `fd25bfc5`; base `bd760432` is an ancestor; working tree 9 entries (3 ` M`: SCORECARD, README,
  SOURCES; 6 `??`): `census/round-90/records/{c1-after.txt,c2-after.txt,prefreeze-c1-both.txt}`,
  `census/round-90/srcs/tr13.html`, `corpus/knowledge/nel-byte-character-pair.md`, `plans/round-90.md`.
  None of the six is gitignored (`git check-ignore` rc 1), so they can land normally; only `.ufo/waves/`
  needs the force-add A0.6 promises.
- `records/c2-after.txt` is complete: 847 B, mtime 11:46, `SUMMARY cases=12 tool_pass=12 before_pass=10`;
  its three header paths/hashes are the prereg's tool (`d095b52f…`), before-tool (`f6fce6d1…`) and fixture
  (`d4417213…`).
- `records/prefreeze-c1-both.txt` **completed** at 11:55:50 (62 lines): `SUMMARY mutants=16 sets=r89,r90
  pristine_r89=ok pristine_r90=ok killed_r89=15 killed_r90=16 killed_total=31` — the pre-freeze feasibility
  arm (disclosed as such by plans/round-90.md A0.3), not after-data.
- `records/c1-after.txt` is **not a stable filed receipt** at 11:57: 34 lines, no `SUMMARY`, ends inside the
  mutant table, mtime 11:56:27 (it has been rewritten in place since 11:53 by a later run; `>` truncation).
  Live processes at 11:51–11:52 included `l1-after` (pid 2241197) and `l1-both` (pid 760429), plus nine seat
  batteries — 11+ concurrent C1 battery runs. S90Reviewer's report states the same target cell-for-cell
  (its cited seat receipt was not yet in its dir at 11:57), and its §2.6 notes the L1 path "was being written
  when first read". **The L1 must freeze one complete run with a `SUMMARY` before citing it.**
- The three modified files and `plans/round-90.md` are the scribe/L1's in-flight integration; their content
  (README r90 frontier paragraph, S353 row, SCORECARD order fix, A0.6/Q165 plans) is uncommitted and
  therefore not yet evidence. The r90 wave dir is ignore-matched and untracked except `build-spec.py`; r89's
  twelve seat reports remain untracked (7 structural files tracked).
- Source integrity (scout receipt, re-read here): tr14 capture == live (`296df533…`, 226,166 B, HTTP 200,
  Unicode 18.0.0 rev 57, 2026-09-01); LineBreak.txt == live (`ae8cf197…`, 266,206 B); tr13 tombstone == live
  (`bfa7f97b…`, 6,348 B). Sources census `validate EXIT 0`, 90 output lines, 0 E-codes, 89 W04, rows 275
  (274 committed + the uncommitted S353 row), identical to the pre-freeze receipt.

## 7. What I could NOT check

- The C1 after data as a *filed* receipt: `census/round-90/records/c1-after.txt` was incomplete at 11:57 and
  being rewritten; a non-L1 seat's official run (S90Reviewer) and the completed pre-freeze feasibility arm
  both read `killed_total=31`. I did not start or re-run a battery — that is the seats'/L1's scope.
- The r90 wave reports still skeletons at 11:57 (`S90Critic`, `S90Reviewer2`, `S90Sentinel`, `S90Scribe`) and
  S90MutCounter's placeholders (§§1, 3, 4, 5); the dedup section is bounded to the seven substantive reports
  and the artifacts present at that time.
- S353's offset under the lane's own tag-stripper (the scout's receipt disambiguates 82357/82360; I did not
  re-implement the stripper). The frozen prereg itself was not edited.
- Sibling lanes' full corpora and gate code (only their `corpus/QUALITY.md`, `corpus/SOURCES.md` and the
  knowledge entries those hits name were searched; a rule that lives only in a sibling's tool code was not
  swept).
- The fleet-root r90 report (absent at 11:20; `.ufo/reports/round-90/` has 11 lane reports, none `souji.md`).
- Universal injectivity beyond S90Labrat's swept domain (it swept all 1,112,064 non-surrogate code points
  against the 256 byte spellings, plus 2-token composition; longer compositions are covered only by
  prefix-freeness + length-2 unique decodability over the 256-token alphabet).
- No credential/secret material was read; no sibling lane file was written.

## 8. Commands and exact tails

### 8.1 Instrument pins (all match the prereg verbatim)

```
$ sha256sum census/round-90/c1-false-rows.tsv census/round-87/c1-pointer-counter.py \
    census/round-90/c1-clause-battery.py census/round-90/c1-false-row-harness.py \
    census/round-90/c1-mutants.json tests/fixtures/r90-k4-flagfail.py \
    tools/souji-record-agreement.py census/round-90/controls/c2-before-tool.py
d64d76954daea7da5d36e6f5eda96ae343bdd37db5071ea50bd55b30a1844b45  census/round-90/c1-false-rows.tsv
fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b  census/round-87/c1-pointer-counter.py
e7265335e4458e68d2277dd0ad4f36e68999a7ba70363d60dc2155bd9cfa2d39  census/round-90/c1-clause-battery.py
c3664747ffe712fde8f61c34562df2f0e92f2a0378b151bd0b4d74e91d629cbe  census/round-90/c1-false-row-harness.py
392522489bc6f22a9747f64d311dbde7528dd0e8b481159db15d3eb038066dd5  census/round-90/c1-mutants.json
d44172132f0a0c707d47e9522df8502f8d84859eb3e82d13e09809450c94aeaa  tests/fixtures/r90-k4-flagfail.py
d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561  tools/souji-record-agreement.py
f6fce6d147165d1baf3d8d0343f46c1ab913b23947f3edaa28b61cdd6caa18dd  census/round-90/controls/c2-before-tool.py
```

### 8.2 Population prefix and LD2b premise

```
$ head -n 59 census/round-90/c1-false-rows.tsv | diff - census/round-89/c1-false-rows.tsv
PREFIX59_IDENTICAL=yes           # no diff output; r90 = r89's 59 lines + LD2b at line 60

$ grep -n "^ZZ9\|^P02" census/round-77/c2-pointer-ledger.tsv
3:P02	ABSENT	-	sentence names a deliberately absent scratch path (r33 control example)
                                 # 32 lines; ZZ9 absent (grep rc 1)

$ tail -2 census/round-90/c1-false-rows.tsv | cut -c1-130
LD2	ledger	BASE	r77	P02	-	-	LEDGER-REFUSED	1	r89 C1: the `_ledger` malformed-row guard `len(r) < 3` (S88MutCounter F3 kills m17c).
LD2b	ledger	BASE	r77	ZZ9	-	-	LEDGER-REFUSED	1	r90 C1: the SAME malformed-row guard reached under an id ABSENT from the frozen r77 
```

### 8.3 First-record provenance

```
$ git log --reverse -S'0x85' -- tools/souji-record-agreement.py
f36fcf55 round-87: C2 sentinel repairs … U+2028/U+2029 cannot tear a detail …
4cb3a06f round-90: C2 repair — U+0085 takes the \u0085 spelling and the dead escape-first _one_line is deleted

$ git log --reverse -S'len(r) < 3' -- .
43822328 round-77: P — C1 non-regular-source counter + population …

$ git log --reverse -S'm17c' -- .
ac61ca1e round-88: wave evidence (10 seat reports and receipts), plan amendments A1-A9 …
c9329534 round-89: instruments and controls (P)
…
fd25bfc5 round-90: preregistration (F) …

$ git grep -l 'len(r) < 3' 43822328
43822328:census/round-77/c2-pointer-counter.py
```

### 8.4 Durability / order / state

```
$ git ls-files .ufo/waves/round-90
.ufo/waves/round-90/build-spec.py                        # 1 file
$ git status --porcelain --ignored .ufo/waves/round-90
!! .ufo/waves/round-90/w1-dispatch.json
!! .ufo/waves/round-90/w1-run.err
!! .ufo/waves/round-90/w1-spec.json
!! .ufo/waves/round-90/w1.ready
!! .ufo/waves/round-90/w1.ready.dispatched
!! .ufo/waves/round-90/w1/
$ git ls-files .ufo/waves/round-89 | wc -l
7                                                        # structural files; none under w1/

$ grep -n "^### " SCORECARD.md | tail -6
2096:### Round 88 measurements …
2110:### Round 88 capability rows
2117:### Round 89 measurements …
2135:### Round 89 capability rows
2142:### Planned (r89)
2153:### Planned (r90, as filed in r89 — historical)
$ git show bd760432:SCORECARD.md | grep -n "^### " | tail -3
2135:### Round 89 capability rows
2142:### Planned (r90)
2153:### Planned (r89)                                        # inversion fixed in the working tree

$ ls census/round-90/records/ ; wc -l census/round-90/records/c1-after.txt
c1-after.txt c2-after.txt prefreeze-c1-both.txt prefreeze-c1-control.txt
prefreeze-c2-after.txt prefreeze-c2-control.txt prefreeze-c2-k4-regression.txt sources-census-before.txt
26 census/round-90/records/c1-after.txt     # 11:56: no SUMMARY; ends m8
34 census/round-90/records/c1-after.txt     # 11:57: still no SUMMARY; rewritten in place (mtime 11:56:27)
$ tail -1 census/round-90/records/c1-after.txt   # 11:56 observation
MUTANT-PAIR m8-w-only-shapes pop=r89 killed=yes mismatches=2 errors=0 exit=1 | pop=r90 killed=yes …
$ grep "SUMMARY" census/round-90/records/prefreeze-c1-both.txt
SUMMARY mutants=16 sets=r89,r90 pristine_r89=ok pristine_r90=ok killed_r89=15 killed_r90=16 killed_total=31
$ grep "SUMMARY" census/round-90/records/prefreeze-c1-control.txt
SUMMARY mutants=16 sets=r89 pristine_r89=ok killed_r89=15 killed_total=15
$ cat census/round-90/records/c2-after.txt | tail -1
SUMMARY cases=12 tool_pass=12 before_pass=10
$ ps -eo pid,etimes,cmd | grep -E "c1-clause-battery" | grep -v grep   # 11+ lines at 11:52, incl.
760429 846 python3 -B census/round-90/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
  --work /fast/scratch/hyaku/souji-r90/l1-both --only r89,r90 --expect-killed 31
2241197 288 … --work /fast/scratch/hyaku/souji-r90/l1-after --only r89,r90 --expect-killed 31
```

### 8.5 Battery defaults (the carried stale-default item)

```
$ sed -n '114,116p;171,173p' census/round-90/c1-clause-battery.py
    ap.add_argument("--only", default="r85,r86", …)
    ap.add_argument("--expect-killed", type=int, default=None, …)
    if ns.expect_killed is not None:
        return 0 if tot == ns.expect_killed else 1
    return 0
```

### 8.6 Sibling-ownership greps

```
$ for d in *-shokunin; do … corpus/QUALITY.md Q-count / corpus/SOURCES.md S-count …; done
# souji 164/275; kumitate 0/219; tameshi 0/183; kagi 0/158; lore 13/32; revenger 17/509; …
$ grep -n "NEL (U+0085)" kumitate-shokunin/corpus/knowledge/row-id-reader-class.md
148:- **NEL (U+0085) is not JS white space.** A NEL pad or NEL-prefixed row is invisible to both JS
150:  different mechanism. Do not "fix" NEL into the pad class.
$ grep -n "splitlines\|one physical line\|physical line" */corpus/QUALITY.md */corpus/SOURCES.md
# souji Q91/Q159/Q163/Q164 (the lane's own rule); kotodama criterion 22 (Gate record shape, unrelated);
# no sibling holds a splitlines/one-line diagnostic-cell criterion
$ grep -l "malformed.*ledger\|ledger.*malformed\|len(r) < 3" */corpus/QUALITY.md */corpus/SOURCES.md */corpus/knowledge/
# kagi claim-ledger.md, lore 2026-10-12-malformed-error-patterns.md, kumitate row-id-reader-class.md,
# revenger … — none is souji's _ledger 2-column guard
```

### 8.7 Source locators (scout receipt, re-read)

```
$ cat .ufo/waves/round-90/w1/S90ScoutSources/receipts/verify.out   (excerpt)
tag-stripped (drop tags, '\n\t'->' ') char offset: 82199
  byte offset of the quoted sentence 'The NL class ...': 82357
  byte offset of the same sentence MINUS its first word ('The'), leading space kept: 82360
occurrence count in tag-stripped text: 1
word count (whitespace split): 18
95:0085           ; NL # Cc         <control-0085>
tr13 supersession-notice quote count: 1 words: 25
validate EXIT=0 ; E-code lines: 0 ; souji rows 275
```

### 8.8 The uncommitted knowledge entry's slips (11:47 version, 4,272 B)

```
$ grep -n "82360\|24 words\|tr13" corpus/knowledge/nel-byte-character-pair.md
8:bytes; the quote verified once at tag-stripped offset 82360).
51:  character)." — § NL: Next Line, tag-stripped offset 82360, occurrence count 1; …
55:  Guidelines — https://www.unicode.org/reports/tr13/ opened 2026-11-08 (HTTP 200, 6348 bytes, sha256
56:  `bfa7f97b…a667c78`, capture census/round-90/srcs/tr13.html): the URL now serves a supersession notice, not the
58:  Core Specification of the Unicode Standard, starting with Version 4.0" (24 words). REJECT: …
```

## 9. Scratch and side effects

- No scratch was needed; `/fast/scratch/hyaku/souji-r90/S90Connector` was created empty at seat start and
  removed (`rmdir`) before yield. Nothing left behind under `/fast/scratch/hyaku/`, `/tmp`, or elsewhere.
- Tooling: none installed or upgraded; no pacman; no host service, sysctl, credential or secret access.
- Git: read-only only (`log`, `show`, `cat-file`, `ls-files`, `status`, `diff`, `check-ignore`, `rev-parse`,
  `merge-base`, `grep` at revisions). No add/commit/push/checkout/reset/stash, no jj write, no fixture repo.
- Writes: this report and `.ufo/waves/round-90/w1/S90Connector/` (receipts). No lane file edited; no
  MANIFEST.json, `.ufo/state/*`, `.scratch/*`, `.ufo/watchdog.log`, or sibling-lane file touched.


## 10. State at yield (2026-11-08 12:00 -03)

- `census/round-90/records/c1-after.txt`: 41 lines at 11:59:40, still no `SUMMARY`, mtime 11:59:33, sha256
  `62601ed5…` (prefix) — still a run in progress, rewritten in place. The completed pre-freeze feasibility arm
  (`prefreeze-c1-both.txt`, 11:55:50) and S90Reviewer's report (§2.1) both read `killed_total=31`; the L1's
  filed after receipt was not yet stable at this seat's yield.
- Seat reports at 11:59: `S90ExecC3` 24,542 B; `S90Reviewer` 21,636 B; `S90Labrat` 18,030 B; `S90ScoutSources`
  17,210 B; `S90ExecC1` 6,401 B; `S90MutCounter` 5,475 B (placeholders in §§1/3/4/5); `S90ExecC2` 13,500 B;
  `S90Connector` this file; skeletons: `S90Critic` 64 B, `S90Reviewer2` 110 B, `S90Sentinel` 157 B,
  `S90Scribe` 88 B.
- S90Reviewer's seat dir at 11:57 held 7 files (`c2-after-mine.txt`, `c2-control-mine2.txt`,
  `k4-regression-mine.txt`, four `probe-*.txt`) and **not** the `c1-after-official.txt` its §2.1 cites; the
  seat was still running, so this is a "confirm at yield" item, not a defect.
- Nothing else in this seat's §1–§9 changed: the C1 target numbers, the C2 numbers, the overlap table, the
  sibling verdict and the r91 candidate list stand as written; the only status that moved between 11:44 and
  12:00 is the C1 receipt stability (row 3) and the seat-report inventory (§5, §10).

Report: .ufo/waves/round-90/w1/S90Connector.md
