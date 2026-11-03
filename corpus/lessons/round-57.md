# Round 57 — the inline-comment class (v6) and the receipt revision-binding gate

Fresh-start reading: not applicable (no streak block). The r56 non-author closure
(`corpus/lessons/round-56-verifier-spotcheck.md`, verdict ok / **rejected-harmed**) routed six defects;
r57 takes the two that carry its claims (4: B4/C4 hidden-inline over-acceptance → C1; 1: Q109 receipt
revision naming → C2) and dispositions the rest in `## Routed-item disposition` below.

Claims (frozen in `census/round-57/preregistration.txt`, freeze commit
`d749f7ee081ec1b382b2f92577eb22bfba1c7761`, base `b4ef0bc84ada3fb3aefd6a0b1a841a6517b84acd`):

- **C1 calibration 7** — the correction-filing counter v6 (`census/round-57/c1-counter.py`) adds the
  `inline` hidden class: a `<!--` on a visible line that does not start the line opens a comment that
  ends at the first `-->` after it, including one on a later line, so B4-INLINE-NBSP-OPENER and
  C4-INLINE-CLOSED-COMMENT are refused where v5 filed them; F29 and the new C6-INLINE-SAME-LINE stay
  visible; the finding detail carries `hidden_by=fence|block|inline`; the selftest asserts the FULL
  ordered finding list (the r56 routed M1).
- **C2 operability 8** — a new receipt revision-binding gate (`census/round-57/c2-counter.py`) plus a
  recorder (`census/round-57/record-receipt.sh`): a receipt must name a durable full40 `rev=`, an
  `EXIT=` line and an `instrument_sha256=` equal to the instrument's committed blob at that revision.
  This is the Q109 repair.
- No exploratory claim. **Assimilation: none** — no `considerthese/` directory in this lane;
  shokuknow's `merge/souji/` stays held by the open r46 L0 question on mass id drift.

## Gate

### New rows opened this round (S279, S280 admitted; S281 rejected)

- **S279** WHATWG HTML Living Standard, §13.1.6 Comments —
  https://html.spec.whatwg.org/multipage/syntax.html — opened 2026-11-03, `curl -sSL -o <scratch>
  -w '%{http_code} %{url_effective}\n'` → `200 https://html.spec.whatwg.org/multipage/syntax.html`
  (no redirect), 89196 bytes, sha256
  `ad4bdaca53226b0c6f5962786f309fea3ca4e59bec86b026cb3fc5d641b25ff1`; capture
  `census/round-57/sources/s279-whatwg-html-syntax.html`.
  Located quotes (normalized: tag-stripped, entity-decoded, whitespace-collapsed; each asserted a
  verbatim substring): 11 words — "Comments must have the following format: The string " <!-- "." and
  19 words (the receipt and the registry cell say 17 — see ERRATUM-R57-3) — "the text must not start
  with the string " > ", nor start with the string " -> "".
  `teaches`: the authoring restriction constrains the comment TEXT, not where a renderer opens a
  comment. Tier A (spec, official).
- **S280** CommonMark 0.31.2, §6.6 Raw HTML — https://spec.commonmark.org/0.31.2/ — opened 2026-11-03,
  `200` (no redirect), 514698 bytes, sha256
  `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d` (equal to the digest S277 already
  recorded — same page, different scope: §6.6 inline raw HTML, not §4.5/§4.6 blocks); capture
  `census/round-57/sources/s280-commonmark-0.31.2.html`.
  Located quote (24 words): "An HTML comment consists of <!--> , <!---> , or <!-- , a string of
  characters not including the string --> , and -->". `teaches`: an inline comment needs only a later
  closer, so a mid-line opener hides its span — the r56 B4/C4 harm. Tier A (spec, authoritative for
  the renderer grammar the counter implements).
- **S281 REJECTED** MDN, Using HTML comments —
  https://developer.mozilla.org/en-US/docs/Web/HTML/Comments — opened 2026-11-03, `200`, effective
  URL `/en-US/docs/Web/HTML/Guides/Comments`, 175824 bytes, sha256
  `2bca88c20599aa7f3c1bc12dc4d041f156b526ed7dee68c0b08b9fc1ca60d9ba`; capture
  `census/round-57/sources/s281-mdn-comments.html`. Located quote (25 words): "This text cannot start
  with the string > or -> , cannot contain the strings --> or --!> , nor end with the string <!-".
  Reason: restates the HTML **authoring** restriction only, silent on the markdown inline grammar this
  counter reads, and the A-tier S279 already holds that rule. Flip: a markdown-renderer statement, or
  a scope change to raw HTML authoring. Kept as a rejected row (taste evidence) — and it is the round's
  reject sample the r56 spot-check asked for.
- Registry change: 202 → 205 rows at the sources commit, then 207 after the two superseding rows
  below. `used-by` for S279/S280 = `corpus/knowledge/inline-html-comment-visibility-r57.md`; S281
  `used-by` = `—`, `status` = `rejected`. Search log entry added at the top of `## Search log`. No
  existing row's immutable cells changed.
- **Superseding rows filed the same round (CORPUS.md rule 2), after `S57scribe01` re-opened the page
  and checked the cells against it:** `S282` supersedes `S279` (S279's `teaches` cell rendered the
  page's double quotes as single quotes; the verbatim form is `The string " <!-- ".`) and `S283`
  supersedes `S280` (S280's `teaches` cell carried a quote containing both `<!--` and `-->` in a bare
  table cell, which a Markdown renderer swallows — the row renders as `An HTML comment consists of , ,
  or , and -->`; in a code span it reads verbatim). Both superseding rows are `mined`, `used-by`
  `corpus/lessons/round-57.md`, and the originals stay as filed. Scribe also observed that `S281`'s
  `used-by` is `—` (a rejected row is not cited by an admission) although the seat task's draft said
  otherwise: the row is right, the task text was sloppy, disclosed.

### Candidates considered

- Admitted: S279, S280 (above). Rejected: S281 (above). No other page was opened.
- Discernment sample: one admit pair and one reject are on record; the non-author closure decides
  whether it agrees (`## Wave findings` records the seats' verdicts, not the closure's).

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| a frozen target's parenthetical miscounted the rows it described (T3 said "the 33 carried rows minus F17/F18/F19/F29" while the operative condition is "every row other than B4/C4 is identical", which is 34 rows including C6) | `census/round-57/records/c1-targets.txt` `carry_identical 34`, `changed_rows B4,C4`; the prereg's T3 wording at `census/round-57/preregistration.txt` | none — the freeze was read against the matrix only after the commit; the dry-run matrix was already in hand, so a one-line check before freezing would have caught it | ERRATUM-R57-1 (below); the claim is scored on the operative condition, which holds 34/34, and the prose is not edited |
| the "before" source-census receipt was first recorded with `--file` over a corpus-only snapshot, which produced two false E11 rows for `SKILL.md` and then two for `tools/*.py` (used-by paths resolve against a tree that was not extracted) | `census/round-57/records/sources-census-before.txt` (final form carries the full snapshot list); the earlier attempts printed `E11 S225 missing used-by SKILL.md` and `E11 S120 missing used-by tools/souji-size-census.py` | none — a file-mode census over a partial tree cannot be distinguished from a real defect by its exit code (both 1), so the receipt's own command line had to name every extracted path | the receipt now names every extracted path (`corpus SKILL.md SCORECARD.md PROVINCE.md tools/`) and its exit is 0 with 61 W04; rule for r58: a before-receipt over a snapshot states the snapshot's exact path list in the receipt |
| the standing-suite recorder was asked to run at the freeze revision and refused with `COULD-NOT-EVALUATE dirty worktree at run time: 6 unexpected rows` (rc 2) because the lane tree carried the round's own uncommitted evidence | seat S57executor02's receipt (preserved as EXIT=2) and the L1's identical refusal in the same minute | the recorder's own dirty-tree guard (the r46 counter) | the standing receipt is produced after the content commit and recorded against that clean revision; the EXIT=2 receipt is kept as the guard's evidence, never as a pass |

## Errata to frozen prose (no frozen file changed)

- **ERRATUM-R57-1** — `census/round-57/preregistration.txt` C1 target T3's parenthetical ("the 33
  carried rows minus F17/F18/F19/F29") is a miscount: the operands are 36 fixtures, 2 changed (B4, C4),
  34 identical, of which C6 is new and F17/F18/F19/F29 are in fact identical. The operative condition
  ("every row other than B4/C4 identical in exit and full finding list") holds 34/34.
- **ERRATUM-R57-3** — the S279 quote-2 word count is **19**, not 17: `records/source-quotes.txt` and
  the S279 registry row's `anchor` cell both say 17. The quote is verbatim, inside §13.1.6, and ≤25
  words (the criterion that matters), so the row stands; the two counts are left as filed (a records
  receipt and an immutable registry cell are never rewritten) and the correction is this entry plus the
  report. `S57scribe01` re-derived 19 with its own normalizer; the L1 confirms 19 by `split()` on the
  quote text. r58 may file a superseding row if a precise count is wanted.
- **ERRATUM-R57-2** — the C1 docstring's `fence` class note keeps the r55 sentence that a fence-closer
  line is rstripped; v6 rstrips whitespace rather than only spaces, so a closer followed by a vertical
  tab or form feed still closes. Inherited from v5, disclosed, not a r57 change.

## Named limits carried into r58

- The comment class is line-level: a line only partially covered by an inline span is marked hidden
  whole, and a `<!--` on a line with four or more leading spaces is treated as indented code (a lazy
  paragraph continuation is not modelled). Other HTML block types (CDATA, processing instructions,
  declarations) are not modelled.
- Comment validity beyond "a closer exists" is not judged. WHATWG S279 restricts the text; CommonMark
  S280 does not; the counter follows the renderer. A future round that grades raw HTML authoring would
  need the opposite rule, and this entry says so.
- `<!-->` / `<!--->` are special-cased for the inline class only; the block class does not treat them
  differently from any other opener.
- The receipt gate binds the receipt's revision and the instrument's committed bytes, **not
  execution**: a forger who names a real revision and a real instrument digest still passes
  (reviewer02's no-execution forgery case). Annotated tag OBJECT ids are accepted — git peels them to
  the same tree — although the docstring promises `RECEIPT-REV-ABSENT` for a full40 token naming no
  commit object (reviewer02 MEDIUM, `records/probe-rev-shapes.txt`): a contract/behaviour mismatch, not
  a durability hole, routed to r58.
- Manifest receipt paths are not confined to `--root`: an absolute path or a `../escape` is read and
  can exit 0 (reviewer02 MEDIUM). The gate's docstring calls them root-relative; no confinement check
  exists in the frozen bytes.
- The gate's durability test walks `refs/heads`, `refs/tags`, `refs/remotes`; a commit reachable only
  from `refs/stash` or `refs/original` reads as absent, which is stricter than the r17 receipt rule and
  is disclosed rather than fixed in frozen bytes.
- The r56 sentinel MEDIUM/LOW items (quadratic correction-line lookup at `c1-counter.py`'s site loop,
  raw control bytes in diagnostics, symlink scratch roots) remain **OPEN**: r57 does not edit them.
- The capture counter's row-set meta-test (r56 routed N3) remains **OPEN**: this round does not touch
  `census/round-56/c2-counter.py`.

## Routed-item disposition (r56 → r57)

| r56 routed item | what r57 did | verdict |
|---|---|---|
| 1 standing-suite receipts name no measured revision (Q109) | `record-receipt.sh` + `c2-counter.py`; the standing receipt is re-produced at the round's final content revision; the r56 receipt is the red arm. `S57revenger01` scores it **NARROWED**, not closed: the recorder accepts a dirty tree (it binds the clean blob's digest while capturing whatever the command prints) and silently overwrites an existing OUT file | NARROWED (r57's own receipts; historical r53/r54 receipts and the dirty-tree/overwrite gaps routed to r58) |
| 2 wave composition (2 executors vs 3) | three executor seats fielded in w1 | CLOSED |
| 3 ignored `__pycache__` artifact left behind | `census/round-56/__pycache__` removed; `git ls-files census/round-56/__pycache__` prints nothing | CLOSED |
| 4 B4/C4 hidden-inline over-acceptance | C1's v6 inline class; both shapes refuse with `hidden_by=inline` | CLOSED |
| 5 selftest kill-power (M1, N3) | the all-findings assertion kills the M1 mutant (`records/m1-red-before.txt`) and the C1 selftest also asserts `rc`; the C2 selftest asserts the finding list but **not** `rc`, compares ids only, and ignores a ghost expected row (`S57mutation01` G1–G8, `S57revenger01` rowset-ghost); N3 (capture row-set) untouched | M1 CLOSED, C2 harness gaps + N3 OPEN |
| 6 sentinel MEDIUM/LOW items | disclosed only | OPEN (carried to r58 planned) |

## Wave findings (one v1 wave, 12 seats)

Shape: scout 1, connector 1, executor 3, scribe 1, reviewer 2, critic 1, mutation-tester 1, sentinel 1,
revenger 1 — attack roles 4 of 12 (33%), one connector; the L1 holds the planner seat. Evidence
committed at `census/round-57/wave/w1/`.

### Seats and verdicts

- **S57scout01 (scout, read-only recon)** — pins 13/13 MATCH; all 52 built fixtures deterministic in
  every column but `dir`; both matrix arms reproduce the committed dry-runs byte for byte; v5 exit-0
  10/36, v6 8/36; C2 at base refuses the r56 receipt with exactly `RECEIPT-REV-MISSING`; the stub is
  false-green; sources census rc 0 (205 rows, 62 W04). Its nine OPEN items are dispositioned in
  `## Wave findings` below and in the report.
- **S57connector01 (connector)** — no sibling owns the inline-span rule (`hidden_lines` is lane-local;
  `tameshi` has an `in_fence` helper with a different purpose); several sibling auditors model line
  boundaries but none distinguishes block from inline comments; receipt revision binding exists in
  other lanes (`tool_sha256`, `is-ancestor`) but none binds the instrument's committed blob at the
  receipt's revision — LANE-FIRST on C2's digest binding, SHARED on the general idea. No sibling file
  edited or executed.
- **S57executor01 (executor)** — AGREE on every step: both arms reproduced per fixture, matrices
  byte-identical to the dry-runs, T3/T4 numbers re-derived (34 identical rows, v5 10, v6 8), selftest
  36/36, real lane exit 0 with `unfiled=0 … fenced=0`.
- **S57executor02 (executor)** — AGREE on C2: selftest 8/8 with `control=FALSE-GREEN-REJECTED`; the
  before manifest refused (rc 1); the three recorder receipts carry `instrument=`,
  `instrument_sha256=`, `rev=<40>`, `EXIT=`; the standing suite refused with `COULD-NOT-EVALUATE dirty
  worktree at run time: 6 unexpected rows` (rc 2) — preserved as a dirty-tree refusal, never a pass.
- **S57executor03 (executor)** — M1/M2/M3 killed by the expected fixtures; **M4 (closer line not
  hidden) and M5 (`<!-->`/`<!--->` special case removed) SURVIVED** — coverage gaps. Independently
  reproduced the routed M1 pair: the secondary-emission mutant survives a first-finding-only
  comparison and dies under the frozen all-findings one.
- **S57mutation01 (mutation-tester)** — 21 C2 mutants: 9 killed (EXIT check, short rev, absent/keep-only
  durability, pin presence, committed-blob digest, symbolic rev, missing rev, mirror always-refuse),
  **12 survived**, and the survivors expose real harness gaps: **G4 the selftest never asserts `rc`
  (`passed = (got == want)` only)**, G6 the comparison drops path and detail so a receipt-name-keyed
  fake gate passes, G7 an expected row whose case is not built is silently ignored (`SELFTEST pass
  cases=7`), plus missing cases for symlink, manifest shape, tag/remote reachability and token
  boundaries.
- **S57reviewer01 (reviewer, C1 attack)** — ATTACK-FOUND. **HIGH: a second comment opener on the
  closer's suffix is never opened** (two inline openers, two block openers and the empty-comment
  variants), so v6 files corrections that an independent markdown-it render hides. **HIGH (disclosed):
  a four-space-indented opener inside a lazy paragraph continuation** hides filings that v6 files.
  **MEDIUM over-hide:** an opener inside an inline code span, after a backslash escape, or in a link
  destination is refused though it renders visible; **MEDIUM:** `<!-->`/`<!--->` and `--!>` in the
  block branch over-hide to EOF. The L1 reproduced the HIGH second-opener harm independently
  (`census/round-57/records/probe-second-opener-harm.txt`: v6 `filed=2 fenced=0` exit 0 while both
  correction lines sit inside the second comment).
- **S57reviewer02 (reviewer, C2 attack)** — ATTACK-FOUND. **MEDIUM:** an annotated tag OBJECT id is
  accepted although the gate's docstring says a full40 token naming no commit object is
  `RECEIPT-REV-ABSENT` (contract/behaviour mismatch; the tag peels to the same tree). **MEDIUM:**
  manifest receipt paths are not confined to `--root` — an absolute path or `../escape` reads outside
  it and exits 0. **LOW:** duplicate `rev=` precedence is unspecified (`good; bad` passes, `bad; good`
  refuses). Confirmations: symlink refusal, missing-EXIT refusal, digest mismatch, tag-only commit,
  CRLF, `rev = <hex>` refusal all AGREE; and the residual limit — the gate binds bytes, not execution,
  so a receipt written without running the instrument passes.

- **S57sentinel01 (sentinel)** — write-scope and scratch proof: `strace -f -y` shows every write
  under `--work`, no hardcoded `/tmp`, the FIFO/symlink receipt cases refused before `open` (no hang),
  and the frozen pins intact. **ATTACK-FOUND, one HIGH:** the inline scan is purely textual, so a
  backticked `` `<!--` `` opens a phantom span that **suppresses an unrelated LOG.md overstatement**
  (`log-codespan`: v6 `logunfiled=0` exit 0 where v5 refuses `UNFILED-SOURCES-ANNOTATION`) — a v6
  regression in the *silent* direction, in addition to the over-hide direction. MEDIUM: raw terminal
  control bytes echoed in finding details (M2, the r56 F2 class), a BEL after a correction's line
  number drops the correction unjudged (M3, also in v5). LOW: 1 MiB tokens echoed whole (L4, output
  amplification), plus scratch/symlink/`.pyc` notes.

### Admission / no-harm verdict

- **C1:** the frozen targets T1–T7 hold (B4/C4 refused with `hidden_by=inline`, C6/F29/F17/F18/F19
  visible, 34 identical carry-over rows, exit-0 8 vs 10, selftest 36/36, real lane exit 0). **But
  calibration is harmed**: (a) the frozen grammar's own rule ("a `<!--` that does not start the line
  opens a comment ending at the first `-->` after it") is not implemented after the first closer on a
  line, so a second comment hides filings v6 counts as filed (HIGH, reproduced by the L1); (b) a
  code span makes the scan open a phantom span that hides an unrelated LOG/README overstatement
  (HIGH, sentinel H1 — the silent direction, and a v6 regression where v5 refused); (c) four over-hide
  classes newly refuse visible filings (code span, escape, link destination, tab indent; MEDIUM).
  Predicate holds; the claim is **not admitted**.
- **C2:** the frozen targets T1/T2/T4/T5/T6 hold (before refused, after clean, receipts bound), and
  the gate's core checks are mutation-guarded (M1–M6, M10, M11, M21 killed). **But calibration is
  harmed**: the documented `RECEIPT-REV-ABSENT` contract does not hold for an annotated tag object,
  the manifest path confinement the docstring implies is absent, and the selftest's own claim is
  weaker than a reader would infer (no `rc` assertion, id-only comparison, silently skipped expected
  rows, four missing case families). Operability improved on the declared surface; the claim is **not
  admitted**.
- **Whole round: rejected-harmed, honest stop.** No operator ruling is assumed and no continuation
  round is started here. This is the third consecutive rejected closure for this lane (r55, r56, r57);
  the next dispatched round should read the three closures first (fresh-start posture) even if the
  driver does not block.

## Routed to r58 (each item names the violation it repairs)

0. **Inline scan must model inline code spans (HIGH, C1; sentinel H1).** A backticked `` `<!--` ``
   currently opens a phantom span: in the pair scan that suppresses an unrelated overstatement
   (v6 exit 0, v5 refuses), in SCORECARD it refuses a visible filing. Track backtick runs before the
   inline class; add the `log-codespan` and `sc-codespan` fixtures. This subsumes part of item 2.
1. **Inline class, second opener (HIGH, C1).** `hidden_lines` must resume tokenization immediately
   after every closer — on its suffix and on a block's closing line — and process every opener on a
   line. Fixtures: two inline openers (`04`), two block openers (`05`), empty-comment then block (`30`),
   second opener on the closer line (`31`). Evidence: `S57reviewer01/04-two-inline-openers`,
   `records/probe-second-opener-harm.txt`.
2. **Inline class, over-hide (MEDIUM, C1).** The opener search must respect inline code spans,
   backslash escapes, link destinations and TAB indentation (CommonMark expands a tab to four columns,
   so a tab-indented opener is indented code) before it opens a comment; a block branch must handle
   `<!-->`, `<!--->` and (if browser visibility is the contract) `--!>`. Fixtures: reviewer01 `22`,
   `23`, `24`, `32`, `08`, `09`, `19`; L1 `records/probe-code-span-overhide.txt`,
   `records/probe-tab-indent-overhide.txt`; revenger D2/D3.
3. **Lazy paragraph continuation (HIGH, disclosed, C1).** Indented-code eligibility needs paragraph
   state, not a leading-space count: reviewer01 `14`.
4. **Selftest coverage (MEDIUM, C2).** Assert `rc` as well as the finding list; assert full finding
   detail (path/revision), not only the id; fail when an expected row's case is not built; add cases
   for symlink, manifest shape (wrong column count), tag/remote reachability, token boundaries, and
   multi-finding receipts. Evidence: `S57mutation01` G1–G8, M7/M8/M9/M12/M13/M14/M15/M16/M17/M18/M19/M20.
5. **C1 selftest coverage (coverage).** M4 (closer line not hidden) and M5 (`<!-->` special case)
   survived — add fixtures (`S57executor03`).
6. **Gate contract and confinement (MEDIUM, C2).** Decide and implement: an annotated tag OBJECT id is
   refused as `RECEIPT-REV-ABSENT` (as the docstring says today) or the docstring is corrected; and
   manifest receipt paths are confined to `--root` (absolute and `../` refused by name). Evidence:
   `S57reviewer02`, `records/probe-rev-shapes.txt`.
7. **Duplicate `rev=` precedence (LOW, C2).** State the rule: first token, all tokens must agree, or a
   single header only. Current behaviour is first-token-wins and is unspecified.
8. **Recorder and harness operability (LOW, C2).** The recorder must refuse or disclose a dirty
   tree (it currently binds the clean blob's digest while capturing whatever the command prints) and
   must not silently overwrite an existing OUT; the C2 selftest must be idempotent over an existing
   `--work` (a re-run fails in the fixture builder). Evidence: `S57revenger01` D4/D6.
9. **Scale (MEDIUM, C1).** The inline scan is quadratic in unclosed openers
   (`records/probe-scale-unclosed.txt`: 5k → 0.85 s, 20k → 11.17 s). Pre-compute closer offsets or
   bound the scan.
10. **r56 sentinel MEDIUM/LOW residuals still open:** the quadratic correction-line lookup in the site
   loop, raw control bytes in diagnostics, and a symlink selftest case for `RECEIPT-SYMLINK`.
11. **Capture counter row-set meta-test (r56 routed N3) still open.**
12. **r57 `.pyc` recurrence.** `census/round-57/__pycache__/*.pyc` reappeared from a non-`-B` run
   during the round (revenger D5); removed at close. The routed-3 class needs a code-level guard, not a
   command convention.
