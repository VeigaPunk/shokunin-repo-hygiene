# Round 55 — the annotation and capture counters amended (v4): the r54 routed surfaces instrumented

Fresh-start reading: not applicable (round 55 of a lane with no streak block). The r54 non-author
verifier spot-check (`corpus/lessons/round-54-verifier-spotcheck.md`, verdict ok/admitted) routed
§5.1 (an unreceipted measured-revision citation) and §5.2 (an unnamed counted kill row). Both are
answered below as QUALITY criteria Q109 and Q110, each shown able to fail on the r54 artifacts.
§5.3 (the fleet-side wave-results pointer) and §5.4 (the pre-existing W04 warnings) stay with the
integrator and the registry-cleanup queue; they are not claimed here.

Claims (frozen in `census/round-55/preregistration.txt`, freeze `e8f338674dea386c186aa7657ef2142cbb4b6d48`;
base `f056aaa031bb65de27e7fa5daa38b0d4a443aedc`):

- C1 calibration 7 (the lowest non-retired axis): the annotation-agreement counter is amended to
  v4 (`census/round-55/c1-counter.py`, sha256 `944feafa…`). It instruments the r54 surfaces: the
  HIGH sentinel S1 (one LF line model), reviewer R1–R6, sentinel S2, connector PTR, and committed
  fixtures for mutation M2/M7 and critic N5. 27 committed fixtures (13 carry-over + 14 new).
- C2 coverage 8: the capture counter is amended to v4 (`census/round-55/c2-counter.py`, sha256
  `e4eb34e6…`). It instruments reviewer02 NL-1, NL-3, NL-4, NL-5, the M11 pin branch (selftest arm
  FA9), and FB4 (named pin-shape refusal). 13 committed fixtures + 2 selftest-only arms.

No exploratory claim. No assimilation: shokuknow's `merge/souji/` stays held by the open r46 L0
question on mass id drift. `considerthese/` does not exist in this lane (re-checked at round start).

## Gate

- Admitted: **S278** — Python 3.12 library reference, `str.splitlines` (tier A, docs, scope: the
  line-boundary set). URL https://docs.python.org/3.12/library/stdtypes.html#str.splitlines; access
  date 2026-11-03; `curl -sSL -w '%{http_code} %{url_effective}'` → `200
  https://docs.python.org/3.12/library/stdtypes.html#str.splitlines` (no redirect), 648964 bytes,
  sha256 `0b10fb9e7e5b8db1d1283835b98b6a9c167871bf6475937aa5d0e1467956a352`. Capture
  `census/round-55/sources/s278-python-stdtypes.html`. Located quotes (in
  `census/round-55/sources/s278-located-quote.txt`, recipe: strip script/style, strip tags,
  `html.unescape`, collapse whitespace; all `substring=True`):
  - 18 words — "This method splits on the following line boundaries. In particular, the boundaries are a superset of universal newlines"
  - 15 words — "Line breaks are not included in the resulting list unless keepends is given and true."
  - 25 words — "\v or \x0b Line Tabulation \f or \x0c Form Feed \x1c File Separator \x1d Group Separator \x1e Record Separator \x85 Next Line (C1 Control Code)"
  - 13 words — "Changed in version 3.2: \v and \f added to list of line boundaries"
- Reuse: **S277** (CommonMark 0.31.2 §4.5/§4.6) and **S276** (gitignore PATTERN FORMAT) are cited
  by the r54 knowledge entries and unchanged this round. No status, recheck or used-by cell of an
  existing row changed. The S278 row's used-by is `corpus/knowledge/splitlines-line-model.md`.
- Search log: one bounded fetch (the `str.splitlines` section and the line-boundary table),
  identified 1, screened 1, included 1, excluded 0. Stop rationale: the S1 mechanism is the
  `splitlines()` boundary set, which the one page states exactly. Negative claim, scoped to the
  FILING surface (hidden set, correction line numbers, site lines, pair scan, record count): the
  v4 counter reads those with `str.split('\n')` only. The sweep is `grep -n "splitlines"
  census/round-55/c1-counter.py` → four hits: two in docstring or comment text (lines 14 and 149) and
  line 227 (the git numstat parser, which reads git's C-quoted path records; measured below in
  the knowledge entry) and line 478 (the selftest expected-TSV reader, not a filing surface).
- Knowledge entry admitted: `corpus/knowledge/splitlines-line-model.md` (source S278, provenance
  trio first). Rejected this round: none. The round opened exactly one new page, so there is no
  reject sample to report.
- Spot-check result: pending the round's non-author closure (LEARNING.md). The lane does not claim it.

## Claim evidence

C1 (calibration 7). The frozen predicate is verified on its own fixtures and on the real lane.

- Pinned selftest: `census/round-55/records/c1-selftest.txt` → `SELFTEST pass cases=27`, exit 0,
  builder and expected-TSV pins verified before exec.
- The v3-arm acceptance control (the frozen r54 counter over the same 27 rows, official run
  `census/round-55/records/c1-matrix-v3.tsv`, reproduced byte-identically by `run-matrix.sh`):
  the eight acceptance attacks exit 0 under v3 (F7-FF, F13, F14, F15, F16, F20, F21, F22), so the
  claimed work is not vacuous.
- v4 on the same eight (`census/round-55/records/c1-matrix-v4.tsv`): exit 1 on all eight, with the
  named findings ANCHOR-ALIAS-MISMATCH (F13), PAIR-FILING-INERT (F14), UNFILED-SOURCES-ANNOTATION
  (F15, F16, F22), BOGUS-RECOMPUTED (F20, F21) and CORRECTION-IN-FENCE (F7-FF; F21's wrapped
  corrections also fire it: its SUMMARY reads `fenced=2 bogus=2`).
- Over-hide repairs: F17, F18 and F19 (honest filings behind a 4-space fence, a backtick-info fence,
  and a fenced pair example) exit 1 under v3 and exit 0 under v4.
- Carry-over: the thirteen r54 rows keep identical exit codes and findings under v4 (diff of the
  two matrices, rows 1–13: no difference).
- Counting command: `awk -F'\t' 'NR>1 && $5==0{n++} END{print n+0}' census/round-55/records/c1-matrix-v{3,4}.tsv`
  → `11` then `6` (the 27-row matrix); `awk -F'\t' 'NR>1 && $5==1{n++} END{print n+0}' …` → `16` then `21`.
  The 21 under v4 include F8b-BT4-SHORT-RUN, F23-SOURCES-RECOMP and the carry-over kills; the
  acceptance-attack kills are the 8 rows named above.
- Real lane at the measured revision `4b10ddd1741a948c89d283358affd1da2ab3fd95`:
  `census/round-55/records/c1-tip.txt` → exit 0, `unfiled=0 record_sha=ok appended=ok multi=0
  inert=0 fenced=0 straddle=0 bogus=0 logunfiled=0 logrecomp=0 alias=0 pairinert=0 recomputed=79`.
  The base pre-flight (`records/c1-real-lane-base-preflight.txt`) prints the same field values at
  `f056aaa0`.

C2 (coverage 8). The frozen predicate is verified on its own fixtures and on the real lane.

- Pinned selftest: `census/round-55/records/c2-selftest.txt` → `SELFTEST pass cases=15`, exit 0,
  including FA9-WRONG-TOOL-PIN (rc 1, `TOOL-SHA-ARG-MISMATCH`) and FB4-PIN-SHAPE (rc 2,
  `TOOL-SHA-ARG-MALFORMED`).
- v3 arm over the new rows (`census/round-55/records/c2-matrix-v3.tsv`): FB1-TAB4-ROW, FB2-LOWER-KEY
  and FB3-NOSPACE-KEY all exit 0, so the claimed work is not vacuous.
- v4 arm (`census/round-55/records/c2-matrix-v4.tsv`): all three exit 1 with the named findings
  COMMENT-AMBIGUOUS-NAME (FB1) and RECEIPT-UNKNOWN-KEY (FB2, FB3).
- Carry-over: FH, FH2 and FA1–FA7 keep their exit codes under v4; FA8-SYMLINK-CLASS keeps exit 1 and
  its finding is named `CLASS-MISMATCH` (was the unnamed token `class`; §5.2).
- Counting command: `awk -F'\t' 'NR>1 && $5==0{n++} END{print n+0}' census/round-55/records/c2-matrix-v{3,4}.tsv`
  → `5` then `2` (the 13-row matrix).
- Real lane at the measured revision `4b10ddd1…`: `census/round-55/records/c2-tip.txt` → exit 0,
  `receipt=ok sorted=ok tool_pin=ok`; the same pin passes on the committed round-54 capture
  (`census/round-55/records/c2-r54-capture-preflight.txt`, exit 0), so no honest shape regressed.
- Wrong pin on the real lane (run by the L1 at `4b10ddd1`, not left to a seat):
  `FINDING TOOL-SHA-ARG-MISMATCH pinned=000000000000 observed=e7e79952f783`, `tool_pin=FAIL`, rc 1.

## Erratum (append-only; the frozen prereg and fixtures are not edited)

ERRATUM-R55-1 — `census/round-55/fixtures/build-fixtures.py`, fixture `F7-FF`, and the prereg clause
"two form-feed lines directly above the opening ~~~ fence". The committed bytes are two VERTICAL TAB
characters (`\x0b`), not form feeds (`\x0c`); the builder's comment says so. Both are S1-class
separators (S278 lists both as line boundaries), so the committed F7-FF is a true instance of the
class, and the frozen v4 kill (exit 1) on F7-FF stands. The exact r54 S1 shape (form feed) was not in
the frozen matrix, so I measured it in a single-commit scratch fixture (rev equal to base; scratch
removed after the receipt; NOT claim evidence, recorded here only as the erratum's evidence):

- form-feed shape, frozen v3 counter (`census/round-54/c1-counter.py`): exit 0,
  `SUMMARY sites=2 mismatches=2 filed=2 unfiled=0 … fenced=0 … recomputed=79`
  (the S1 defect reproduced in the clean single-commit shape);
- form-feed shape, v4 counter (`census/round-55/c1-counter.py`): exit 1,
  `FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:10 (site SCORECARD.md:5)`,
  `FINDING CORRECTION-IN-FENCE correction at SCORECARD.md:11 (site census/round-51/preregistration.txt:3)`,
  `SUMMARY … filed=0 unfiled=2 … fenced=2`;
- control, the unmodified vertical-tab F7-FF bytes under v4 in the same harness: the same two
  CORRECTION-IN-FENCE findings.

A form-feed fixture is not added to the frozen builder (that would edit a frozen file). It is routed
to r56 as a new fixture version with its own prereg.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| a fixture named for one separator carries another: `F7-FF` says "two form-feed lines" and its bytes are `\x0b` (vertical tab); the prereg and the builder comment disagree on which byte the S1 shape uses | `census/round-55/fixtures/build-fixtures.py` F7-FF branch (`'\x0b', '\x0b'`); `census/round-55/preregistration.txt` C1 F7-FF row; ERRATUM-R55-1 above | none — the prereg's kill rule names the fixture id only, so exit 1 on F7-FF passed while the named byte was never tested | ERRATUM-R55-1; the form-feed shape measured in a scratch probe (v3 exit 0, v4 exit 1); a form-feed fixture is routed to r56 as a new frozen version. Criterion: a fixture name that names a byte must be checked against the bytes it writes (routed, not yet a Q number) |
| the census-before receipt's `--out` inside the lane root returned rc 2 and the stderr was not printed, so the first attempt looked like a missing file rather than the tool's refusal | `census/round-55` first capture attempt (`$S/cb.log` never read); the receipt tool refuses in-root output by design (`RECEIPT-WRITTEN` only outside the root) | none — a nonzero exit with redirected stderr was not read | staged outside the root (`/fast/scratch/hyaku/souji-r55/L1/census-before-staged.txt`), verified (`VERIFY ok`), copied byte-exact (`cmp`). Rule for the L1: print stderr on any nonzero rc before the next step |
| the capture receipt's `ENTRIES` cell was empty: the staging step grepped lowercase `entries=` from the tool's `CENSUS ENTRIES=49` line, so no value was written | `census/round-55/records/fleet-root-census-run.txt` first commit (`# ENTRIES=` with no value); `c2-tip.txt` → `RECEIPT-MALFORMED` before the fix | the C2 counter's receipt grammar (`RECEIPT-MALFORMED`) — it refused the receipt, which is what it is for | the receipt now takes ENTRIES from the capture's own header (`# ENTRIES=49`); corrected receipt committed at `4b10ddd1`; `c2-tip.txt` → exit 0 |
| the F13/F20/F21 fixtures left the stale prereg site at `(78)` in base and tip, so each matrix row exited 1 with `mismatches=1` for a reason unrelated to its named surface | first dry-run matrix (`census/round-55/records/matrix-dryrun/` before the fix); the SUMMARY line `mismatches=1 filed=0 unfiled=1` | the dry-run inspection of SUMMARY lines before the freeze | the sites were made to read 79 in base and tip; the three rows re-run green on the surface they name, and the official matrix reproduces the dry-run byte-identically |
| the frozen wave spec's `milestone` exceeded the validator's 256-byte cap; the failure surfaced only at `plan` | `ufo-swarm-wave.mjs plan` → `invalid_spec: spec.milestone exceeds 256 bytes` (rc 1) | the validator itself (`plan` before `run`) | milestone shortened to 175 bytes; `plan` rc 0, `run` rc 0 (12 spawns, policy v1 band 8–16). Rule: check the validator's field caps before writing the spec |
| the dispatch context's first draft said the named commit was "the lane tip at dispatch" when the tip was a later commit (records and sources had landed after the measured revision) | the wave context text (first draft) vs `git log` at dispatch | the L1 re-read of the context before writing the ready file | the context names the measured revision `4b10ddd1` and the later tip `3ce0ba03` separately; the spec was regenerated and `run` re-validated before the ready file was written |
| an edit with an empty `PUT` body was applied as a block deletion and emptied this round's new lesson file (uncommitted; nothing landed) | the edit tool's warning ("Interpreted an empty `PUT` body as deletion"); the file was 0 bytes on the next check | the next `wc -c` after the edit | the file was rewritten in full from the same text, with the real-lane wrong-pin line corrected to the direct run. Rule: a delete is `CUT N*`, never an empty `PUT`; check the file after every edit that the tool flags |
| a negative claim ("the v4 counter uses no `splitlines`") was written without its sweep and was false; the sweep then showed the numstat parser still calls it, and a repository-local `core.quotePath=false` makes that parser miscount a deletion (a new named limit) | `grep -n splitlines census/round-55/c1-counter.py` → lines 14, 149 (docstring), 227 (numstat), 478 (selftest reader); scratch probe, `splitlines records: 3 counted: 2` | the sweep, run before the claim was landed into the knowledge entry (CORPUS: a negative claim carries its sweep) | the claim is scoped to the filing surface with its sweep recorded; the numstat limit is measured, disclosed, and routed to r56 |
| the receipt unknown-key pattern's first-character class was narrowed from v3's `[A-Z0-9_]` to `[A-Za-z]` while the key case was widened; no differential against v3's accepted shapes was run before the freeze, so `1KEY=x`, `_KEY=x` and `2=x` (refused by v3) pass under v4 | reviewer02 RD-A, reproduced in `receipt-key-differential.txt` and `receipts/A28.txt` (v3 exit 1 `RECEIPT-UNKNOWN-KEY`, v4 exit 0) | reviewer02's differential over the real-lane fixture commits (not the frozen matrix, which has no such shape) | not fixed in-round (frozen bytes); reported as a no-harm failure for the operator's ruling; r56 first-character class `[A-Za-z0-9_]` with a red-before fixture. Rule: a regex change is run as a differential against the previous version's accepted and refused shapes before the freeze |
| the R6 repair (the pair scan skips lines hidden by `hidden_lines()`) inherited the comment branch's any-indent `<!--` opener, so a four-space-indented `<!--` line hides a real overstatement: v3 exit 1, v4 exit 0 (a v3→v4 regression on the C1 surface; no committed fixture covers it) | sentinel01 S55-S2, confirmed by the L1: `census/round-55/records/probe-s2-pair-indent-comment.txt` | sentinel01's v3-arm differential over attack shapes (the frozen matrix has no indented-opener row) | not fixed in-round (frozen bytes); reported as a harm on C1 for the operator's ruling; r56: apply the CommonMark ≤3-space start rule to the comment branch, with a red-before fixture and a v3 differential |
| the pre-flight receipt `c1-real-lane-base-preflight.txt` was run with the r53 spot-check base (`fe12daad`) in its `--base` argument, not the prereg's `f056aaa0` | critic N14; the receipt's own `--base` field | the critic's reading of the receipt header against the prereg Base line | ERRATUM-R55-4; the claim legs use the right base; the pre-flight is not claim evidence |
| the control files carry the lines `PRISTINE FAIL C1V4-COUNTER-ABSENT` and `PRISTINE FAIL C2V4-COUNTER-ABSENT` as text no counter prints: the same mistake as r54 ERRATUM-R54-3, written again after that erratum was filed | critic N13; `census/round-55/controls/c{1,2}-control-donothing.txt` vs the observed `cat-file-rc=128` | the critic's verbatim-discipline check (the r54 erratum was in the lesson the L1 read at round start, not in the control template) | ERRATUM-R55-3; r56 controls print observed output only |

## Named limits carried into r56

From the prereg "Named limits carried into v4", plus limits the round found by construction:

- The frozen fixture F7-FF uses vertical tab, not form feed (ERRATUM-R55-1); the form-feed shape has
  no committed fixture until r56.
- The zone stays frozen at 32 chars (a token beyond it still forces exit 2 when it is the only
  annotation on the line); pointer exemption is path-like but `x.md:1` still exempts a line (disclosed).
- Pair annotations are scanned in LOG.md and corpus/README.md only (AF4c); an orphaned pair filing
  whose annotation moved has no finding of its own (AF4e).
- CR-only line endings are one line; the HTML comment class is line-level, not CommonMark HTML blocks.
- The receipt binds bytes and consistency, not execution; FLEET_HEAD is format-checked, not resolved;
  unknown `# KEY=VALUE` lines in the capture header are ignored; free-form comments without tabs are
  accepted (NL-2).
- DELETED-LINES parses git numstat with `splitlines()` (`census/round-55/c1-counter.py`, the numstat
  reader). The counter disables only global and system git config, so a repository-local
  `core.quotePath=false` lets a raw U+0085 reach the parser: measured in scratch, a NEL-named
  deletion record splits and is not counted (`splitlines records: 3 counted: 2`). Routed to r56: a
  counter version that parses numstat on `\n` only, shown red-before on a fixture carrying that
  path. Default `core.quotePath` is safe (measured: git C-quotes the names and each record is one line).
- `--scratch` is an alias of `--work` in both counters; the builder's `--work` still accepts a relative
  path (r54 S4), not repaired (named limit, not a claim surface).
- Standing holds, unchanged: certification OFF, K5 HELD, NAMESPACE and reap holds; the open L0 rulings
  (credential-shaped names refuse-vs-redact; the `ignored`-column derivation) and the r46 mass-id-drift
  L0 (assimilation held). The r54 C1-admission L0 is answered by the closure's admission and is not
  reopened here.

## Wave findings (wave w1: 12 seats; evidence in `.ufo/waves/round-55/w1/<seat>/`, copied to `census/round-55/wave/`)

Wave shape: one v1 wave, 12 seats (scout 1, executor 3, scribe 1, reviewer 2, critic 1, mutation-tester 1,
sentinel 1, connector 1, revenger 1). Attack roles (reviewer, critic, mutation-tester) 4 of 12 (33%, ≥25%);
connectors 1 (≤2); band 8–16; the L1 holds the canonical planner seat. Dispatch file
`.ufo/waves/round-55/w1-dispatch.json`; results `w1-results.json` at WAVE-DONE.

Seat by seat (verdict · what it attacked · what it changed):

- **executor01** (C1 reproduction): AGREE on all four steps. Pinned selftest `27/27`; the wrong builder pin refuses (exit 2); four-row matrices per arm byte-equal to the committed v3/v4 matrices; real lane byte-equal to `c1-tip.txt`. No change made.
- **executor02** (C2 reproduction): AGREE on all four steps. Pinned selftest `15/15` including FA9 (rc 1) and FB4 (rc 2); matrix rows byte-equal; real lane exit 0; the wrong pin rc 1 `TOOL-SHA-ARG-MISMATCH` and the uppercase pin rc 2 `TOOL-SHA-ARG-MALFORMED` reproduced. No change made.
- **executor03** (standing receipts): the landing-suite counter (`census/round-46/c1-counter.py`) prints `SUMMARY assertions=580 mismatches=76 registered=76 corrected=0 exempted=0 unfiled=0` at both `4b10ddd1` and the wave tip `3ce0ba03` (identical); the r53 v2 counters reproduce their committed verdicts 10/10; the r52 counters exit 0.
- **scout01** (recon): every frozen pin verified at the measured revision; every routed item of r54 mapped to a committed fixture or selftest arm (unmapped 0 of 17).
- **scribe01** (S278 re-open): PASS — live fetch HTTP 200 with no redirect, 648964 bytes, sha256 byte-equal to the capture; the four located quotes and word counts re-checked. It found that the new entry's `source:` line cites S277 while S277's `used-by` cell did not name the entry (the Q62 K1 rule). Fixed by dropping the S277 id from the entry's `source:` line (the S277 link stays in prose); the S278 recheck changed to `on-release` to match its sibling python-docs rows. Replay with the registry instrument at its correct `--list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804`: `SUMMARY k1=2 k2=0 mismatches=2` at both `3ce0ba03` and the round's landing, the two pre-existing items (S146, S110), none from this round.
- **critic01** (falsification): both claims SURVIVE the literal kill rules; no FALSIFIED; no vacuity (the v3-arm acceptance rows exit 0); controls re-run. Named limits N1–N15 (N1 highest; below).
- **mutation01** (kill power): all 14 C1 mutants killed by their named fixture (each exit 0→1 or 1→0 with the named finding). C2: 3 of 23 survive and are recorded here, not patched: C2-15b (a print-only probe, equivalent for the detector), and C2-17/C2-18 (deleting the FA9 or FB4 arm from the selftest still prints `SELFTEST pass cases=14`: the selftest does not assert that every expected row ran).
- **reviewer01** (C1 attack, 66 states): 41 CommonMark-consistent or counter-internal, 17 routed-defect proposals, 7 named-limit confirmations, 1 render-inconclusive. The routed families are in the list below; the highest-severity is the pair-filing family (N1 = D14/D15).
- **reviewer02** (C2 attack, 54 real-lane fixture commits, each run under v4 and v3): the frozen kill rule holds on the committed bytes. It found **RD-A, a regression of a v3 check** (see below) and four routed items (RD-B to RD-E).
- **revenger01** (r54 routed-item audit, 27 items): INSTRUMENTED 21, REPAIRED-BY-DISCLOSURE 2, OPEN 3 (S4 builder accepts a relative `--work`; S5 the v4 docstring still carries the phrase `PRISTINE FAIL` that the counter never prints; N6 the exit-code legend is not a named limit). §5.1 mechanism instrumented (criterion now Q109). §5.2 instrumented: 0 unnamed kill rows in the v4 matrices.
- **connector01**, **sentinel01**: recorded at WAVE-DONE (see the addendum below).

### The two findings that decide the verdicts

**RD-A (C2 — a regression of a v3 check, reproduced by reviewer02).** The v3 unknown-key pattern accepted a leading digit or underscore (`[A-Z0-9_]`), so `1KEY=x`, `_KEY=x` and `2=x` were refused as `RECEIPT-UNKNOWN-KEY`. The v4 pattern requires a letter first (`[A-Za-z]`), so those lines now pass silently (exit 0). The cause is mine: I narrowed the first-character class while widening the key case, and I did not run a differential against v3's accepted shapes before freezing. The frozen kill list does not name these shapes, so the predicate still holds; but a shape v3 refused now passes, which the no-harm rule counts. **C2 is therefore not clean under the admission bar, and the operator rules.** The lane's proposal for r56: the first-character class `[A-Za-z0-9_]` with a red-before fixture for `_KEY=x` and `2=x`.

**N1 / D14 / D15 (C1 — a false pass on the filing surface, carried from v3).** A pair filing (`R53-CORRECTION`) inside a fenced block or an HTML comment in SCORECARD.md counts as filed: `pair_filings` is built from every match with no `hidden_lines` check, while single `R52-CORRECTION` filings are refused in fences (F4, F7, F8, F9). An overstated LOG.md or README annotation can therefore be "filed" by a documentation example. v3 has the same hole; v4 does not close it, and the frozen kill rule names committed fixtures only. C1 verifies on its predicate; N1 is the highest-severity named limit and the first r56 item.

### Routed to r56 (none applied in-round; frozen bytes unchanged)

1. RD-A: first-character class of the receipt unknown-key pattern, with a red-before fixture for `_KEY=x` and `2=x`.
2. N1 / D14 / D15: hide-check the pair-filing grammar (pair filings inside fences and comments are refused, as single filings are).
3. A09–A13 (reviewer01): closers followed by exotic whitespace (VT, FF, NEL, LS, FS): `str.rstrip()` closes a fence that CommonMark keeps open; the closer rule must follow CommonMark (spaces and tabs only).
4. E09/E10 (reviewer01): a fence inside a list item hides nothing; CommonMark treats it as code.
5. C04/C07 (reviewer01): an unannotated first anchor occurrence with an annotated second one reads INERT (an over-refusal; the R2 rule should judge the occurrence that carries the annotation).
6. N4 (critic): the pointer token `\w.\w{1,5}:\d` also exempts a ratio such as `2.5:1` (ERRATUM-R55-2).
7. N2, N3, D07/D08, D12, D16, B07, F01 (reviewer01/critic): only the first pair annotation per line is scanned; prose counts (`274 => 275`, `274 to 275`) and the separators `=>` and `—>` are invisible; a pair without the `corpus/` prefix is not scanned; a 4-space-indented pair line is an over-refusal; a bare filing with trailing text is silently unlexed (UNFILED with no FINDING id); `\d` accepts non-ASCII digits.
8. RD-B, RD-C, RD-D, RD-E (reviewer02): KV-shaped receipt lines outside the key grammar are silent (`KEY-1=x`, `KEY.1=x`, `KEY=x y`, `KEY=`); the capture header's known keys are stricter than the receipt's; a malformed expected TSV crashes the selftest with a traceback instead of rc 2; the selftest wildcard `-` skips the finding check.
9. Selftest harness (mutation01): assert that every row of the expected TSV ran (C2-17 and C2-18 survive today).
10. Revenger OPEN items: S4 (the builder's `--work` relative path), S5 (the `PRISTINE FAIL` phrase in the counter docstrings), N6 (the exit-code legend as a named limit).
11. Receipts (critic N15): `c1-tip.txt`, `c2-tip.txt`, `c2-r54-capture-preflight.txt` print no exit code; r56 receipts print `EXIT=`.
12. The form-feed fixture (ERRATUM-R55-1) and the numstat `\n`-only parse (the repository-local `core.quotePath=false` limit): a new frozen counter version with its own prereg.

### Errata (append-only; the frozen prereg, controls and receipts are not edited)

- **ERRATUM-R55-2** — PTR wording. The lesson's named limits, the knowledge text and the SKILL section say the pointer exemption is "path-like" or "extension-bearing paths only". The regex `(?:[A-Za-z0-9_.\-]+/)*[A-Za-z0-9_.\-]+\.[A-Za-z0-9]{1,5}:\d` requires only a dot before the colon and a digit after it, so a ratio (`2.5:1`) and a bare `x.md:1` exempt a line (critic N4; reproduced by c1-P1b and c1-P1c). Corrected reading: a token with a dot before the colon and a digit after. The timestamp repair (F22) stands.
- **ERRATUM-R55-3** — `census/round-55/controls/c1-control-donothing.txt` and `c2-control-donothing.txt`: the lines `PRISTINE FAIL C1V4-COUNTER-ABSENT` and `PRISTINE FAIL C2V4-COUNTER-ABSENT` are hand-written labels; no counter prints them. The observed output is `cat-file-rc=128`, which the same control records. Same class as ERRATUM-R54-3 (critic N13).
- **ERRATUM-R55-4** — `census/round-55/records/c1-real-lane-base-preflight.txt` was run with `--base fe12daad2549f534650d406ebdbac9113d59313f` (the r53 spot-check base) by mistake. The claim's legs (`c1-tip.txt`) use `--base f056aaa031bb65de27e7fa5daa38b0d4a443aedc`, as the prereg states. The pre-flight is not claim evidence; the critic re-ran the tip at `fe12daad` and it exits 0, so no verdict moves (critic N14).
- **ERRATUM-R55-5** — the scope of the C2 real-lane receipt: `c2-tip.txt` was first written against a receipt whose ENTRIES cell was empty (see Mistakes); the corrected receipt is at `4b10ddd1` and the `c2-tip.txt` in the tree is the corrected run.

### Named limits of the frozen v4 bytes that the wave confirmed (not routed as defects)

- N5 (critic): two annotation sites only (SCORECARD.md and `census/round-51/preregistration.txt`); the same anchor elsewhere is not instrumented.
- N7, N8, N10: first unknown receipt key only; a beyond-zone sole annotation exits 2; pair annotations outside LOG.md and corpus/README.md are invisible (all disclosed).
- N9: "the zone is evaluated after every occurrence" should read "every in-zone annotation" (wording).
- N11: v4 changes the F10 SUMMARY counts (`mismatches` 2→1, `filed` 2→1) because a straddling site is skipped in the count; exit and finding are unchanged, so no frozen kill is touched. Recorded here as an unlisted behaviour change.
- N12: `run-matrix.sh` takes the second token of the first FINDING line without checking it is an id (a capture-header typo yields `column`); the §5.2 rule holds for the committed rows by convention, not by the taker.

### Addendum — connector01 and sentinel01 (settled after a time-box; all 12 seats returned output, none dead)

- **connector01** (sibling-overlap scan, three surfaces): line numbering — the mechanism overlaps with
  sibling lanes, the contract does not. Two sibling defects of the S1 class, measured by the seat and
  routed to their owning lanes (not edited here): kaidoku `tools/round-59/annotation-audit.py` (splitlines
  finds a form-feed-prefixed annotation that the LF-only anchor misses) and chousa
  `tools/corpus/evidence/round50/stale-count-check.py` (splitlines FAIL, LF-only PASS: a verdict flip).
  Receipt grammar: no sibling overlap. Declared count: the problem class overlaps with kaidoku r59/r60; the
  grammar, unit and scope are disjoint. PTR: no sibling breakage; one fleet flip v3→v4 (kasegi LOG.md:1667,
  pair 18->19 vs 92 rows, out of scope). Proposal P1 (not applied): widen the C2 receipt key charset to
  hyphens (`FOO-BAR` passes silently today; `FOOBAR` is named) as a next-round amendment with its own freeze.
- **sentinel01** — verdict **CONDITIONAL PASS**: sound on every surface the prereg claims, lane/fleet clean of
  seat mutation; no finding invalidates either claim; no frozen byte edited. Findings:
  - **S55-S1 (HIGH, carried from v3, not a v4 regression).** A single NUL byte in a correction file makes git
    report the file as binary: numstat emits `-\t-`, the counter maps it to deletions=-1 (DELETED-LINES), and
    with the file unchanged base→rev the bogus correction is silently unjudged (exit 0). One byte flips the
    verdict. Receipt: `census/round-55/wave/w1/S55sentinel01/receipts/attacks-nul.txt`. Routed to r56: refuse a
    binary numstat entry by name (DELETIONS-UNREADABLE-BINARY) instead of reading -1.
  - **S55-S2 (MEDIUM, a v3→v4 REGRESSION caused by the R6 repair).** A four-space-indented `<!--` line before
    an overstatement hides the overstatement from the pair scan under v4 (exit 0), while the frozen v3 refuses
    it (exit 1). My R6 change made the pair scan skip hidden lines, and `hidden_lines()` opens an HTML comment
    at any indent. Confirmed by the L1 at landing (receipt `census/round-55/records/probe-s2-pair-indent-comment.txt`:
    v3 exit 1 UNFILED-SOURCES-ANNOTATION, v4 exit 0). No committed fixture covers it. This is a harm on C1.
  - **S55-S3 (MEDIUM, named limit).** Corrections outside the lexing tolerance (4-space indent, a tab, nested
    `<!--`) do not lex and are never audited: unjudged rather than refused.
  - **S55-S4 (LOW, mitigated).** Without `-B`, the builder import writes `__pycache__` inside the lane, outside
    `--work`; gitignored, all committed invocations use `-B`.
  - **S55-S5 (LOW, named).** An unknown receipt key with an EMPTY value (`# BUILDHOST=`) is silently ignored
    (the KV regex requires a non-empty value).

### No-harm status (the admission bar: every claim verifies and no axis is harmed)

- **C1 (calibration 7): verifies on its frozen predicate; a harm is recorded.** S55-S2 is a v3→v4 regression: a
  real overstatement that v3 refuses is accepted by v4 on the four-space-indent shape. The frozen kill rule does
  not name the shape, so the predicate holds, but the no-harm rule does not.
- **C2 (coverage 8): verifies on its frozen predicate; a harm is recorded.** RD-A: v3 refuses `1KEY=x`, `_KEY=x`,
  `2=x` as unknown keys; v4 passes them (the first-character narrowing, see Mistakes).
- Both regressions are reported as trades for the operator's ruling. Neither is fixed in-round: the frozen bytes
  cannot change, and an amendment is a new round with its own prereg. The honest stop rule applies to progression.

### Mistake class exposed by the wave (both regressions)

Two of the regressions share one cause: a changed check was not run as a differential against the previous
version's accepted and refused shapes before the freeze (RD-A: the key first-character class; S55-S2: the
pair-scan hide). The lesson's rule is now explicit: every changed check runs as a v3/v4 differential over
the carry-over and attack shapes before the freeze, and the differential's rows are committed as a receipt.
