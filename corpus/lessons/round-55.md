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
