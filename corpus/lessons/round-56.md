# Round 56 — the correction-filing counter v5 (over-hide and silent-pass repairs) and the receipt-key counter v5

Fresh-start reading: not applicable (round 56 of a lane with no streak block). The r55 non-author
verifier spot-check (`corpus/lessons/round-55-verifier-spotcheck.md`, verdict rejected-harmed) routed
two v3→v4 regressions (S55-S2 pair-scan hide, RD-A receipt-key class) and the r55 routed items.
Both regressions are repaired in a NEW frozen counter version (v5 / v5), each shown able to fail on
its own fixture. The frozen v4 bytes are unchanged; the v4 arm is the before instrument.

Claims (frozen in `census/round-56/preregistration.txt`, freeze commit in LOG.md; base
`fafe371694fea41c5d23f63083865d5ccf3f1d36`):

- C1 calibration 7: the annotation-agreement counter v5 (`census/round-56/c1-counter.py`) instruments
  the S55-S2 regression, the N1/D14/D15 pair-filing hole, the S55-S1 NUL shape (silent and binary
  numstat), the ERRATUM-R55-1 form-feed shape, and an over-hide false positive found in this round
  (F29). Kill-power on 3 committed rows (F24, F26, F28), 1 named-finding row (F27), 1 carry-over pin
  (F7-FF2), 1 over-hide repair (F29).
- C2 coverage 8: the capture counter v5 (`census/round-56/c2-counter.py`) instruments RD-A (keys whose
  first character is a digit or underscore) and S55-S5 (an unknown key with an empty value), and a
  selftest row-set check (mutation01 C2-17/C2-18). Kill-power on FC1, FC2, FC3.
- Frontier step: one S277 re-open this round (CommonMark 0.31.2 §4.6), a sourced claim for C1's F26
  and F29 rules. The knowledge entry `corpus/knowledge/correction-filing-html-comment-opener.md` cites it.

No exploratory claim. No assimilation (`considerthese/` does not exist in this lane; shokuknow's
`merge/souji/` stays held by the open r46 L0 question on mass id drift).

## Gate

### S277 — CommonMark spec 0.31.2, §4.6 HTML blocks (re-opened this round, sourced claim)

- URL: https://spec.commonmark.org/0.31.2/ (served page states "Version 0.31.2 (2024-01-28)").
- Access: 2026-11-03, `curl -sSL -o <scratch>/cm-spec.html -w '%{http_code} %{url_effective}\n' https://spec.commonmark.org/0.31.2/` → `200 https://spec.commonmark.org/0.31.2/` (no redirect), 514698 bytes, sha256 `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d` (equal to the S277 row's recorded digest; capture `census/round-56/sources/s277-commonmark-0.31.2.html`).
- Located quotes (tag-stripped, entity-decoded, whitespace-collapsed; each `substring=True`):
  - 19 words — "The block begins with a line that meets a start condition (after up to three optional spaces of indentation)."
  - 8 words — "Start condition: line begins with the string <!--"
  - Word counts computed by `python3 -c "print(len('…'.split()))"` over each quote text.
- Admitted claim basis: C1's F26 (a four-space-indented opener opens no region) and F29 (a mid-line
  mention opens no region) rest on these two quotes. The indentation limit and the start condition
  are the CommonMark rule the knowledge entry records.
- Registry change: S277 `used-by` cell old → new: `corpus/knowledge/correction-filing-fence-grammar.md`
  → `corpus/knowledge/correction-filing-fence-grammar.md, corpus/knowledge/correction-filing-html-comment-opener.md`.
  `status` (`mined`), `recheck` (`on-release`), `opened` (the S277 row's original date) unchanged except
  that `opened` is not re-written (a row is opened once; the re-open is recorded here, not in the row).
- Search log: one bounded fetch of the 0.31.2 page; identified 1, screened 1, included 1, excluded 0.
  Stop rationale: the two quotes state the start condition and its indentation limit exactly. Negative
  claim scoped to the counter's comment rule: no other HTML block type is read by the counter; the sweep
  is `grep -n "<!--" census/round-56/c1-counter.py` (the opener rule and the docstring only).
- Spot-check result: pending the round's non-author closure. The lane does not claim it.

### Candidates considered and rejected this round

- No new SOURCES rows. The round's only fetch was S277 (re-open). Rejected candidates: none opened.
- Reject sample for the discernment check: none exists this round (no new page was opened for
  admission). The non-author check is for the round's one admitted entry.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| over-hide: a prose sentence that mentions the token `<!--` mid-line opened an HTML comment region to end of file, so every later line (including honest corrections) read as "in a fence" | probe on the real `SCORECARD.md`: v4 `hidden_lines` hides line 1378 (`R55-CORRECTION … the four-space-indented \`<!--\` line …`) and every line after it; v4 F29 fixture exit 1 CORRECTION-IN-FENCE on an honest filing (`census/round-56/records/matrix-dryrun/c1-matrix-v4.tsv`) | none — the r55 frozen fixtures had no mid-line mention; found by the v5 real-lane read of the lane's own SCORECARD while the v5 opener was being written | the opener must begin the line (CommonMark start condition 2, ≤3 spaces); F29 shows v4 exit 1 and v5 exit 0 (`matrix-dryrun`). Criterion (for QUALITY, routed to round 57 as Q-candidate): a comment-region rule must be tested against a mid-line mention of its own token |
| a claim row named a fixture as the silent shape of S55-S1 (F27) when v4 already refused it, so the claim would have credited a relabel as a kill | dry-run matrix before freeze: v4 `F27-BINARY-NUMSTAT` exit 1 DELETED-LINES (deletions=-1), the silent shape being the unchanged NUL file in probe A | the pre-freeze dry-run matrix, read row by row against the claim's kill rule | the claim is scoped to the FINDING NAME for F27 (T2), and the silent shape is the new fixture F28 (v4 exit 0 → v5 exit 1, T1). Rule: when a claim says "silent", its fixture must be a v-previous exit 0 |
| the shell's `set -e` and `set -x` persisted across tool calls and aborted a later cell, leaving a half-written absent-control file | the cell's `+ git -C … cat-file …` trace inside `controls/c1-absent`-precursor text (rewritten clean in census/round-56/controls/) | the trace itself in the cell output | the controls were rewritten from observed stderr and rc only; shell options reset with `set +e +x` before each measurement cell |
| a matrix runner dry-run failed with `manifest missing` because the fixture builder was not run into the runner's `selftest/` subdirectory | `run-matrix.sh` error text (rc 2) | the runner's own check | the builder is run with `--work <scratch>/selftest` before the runner; recorded in the prereg Matrix command |

## Named limits carried into r57

- The counters read two annotation sites (SCORECARD.md and census/round-51/preregistration.txt) and pair annotations in LOG.md and corpus/README.md only (inherited from v4).
- The HTML comment rule is line-level: a region runs to the first line containing `-->`, and CommonMark HTML block types other than 2 are not modelled.
- Fence-closer lines are rstripped, so exotic separators after a closing run still close a fence in this grammar; CommonMark allows only spaces and tabs (routed A09–A13 from r55 reviewer01, not instrumented in v5).
- A pair filing inside a fence or a comment no longer files (T1 via F24), but a correction that is valid and visible yet placed in a prose paragraph is still judged by line only.
- F27 pins the finding name, not a silent pass; the binary numstat branch has no silent shape of its own beyond F28.
- The receipt grammar still reports only the FIRST unknown key (r55 named limit, inherited).
- The numstat parse is LF-only (hardening, not a reachable lane verdict).

## Wave findings (after WAVE-DONE)

Main delivered WAVE-DONE for w1: twelve seats settled, twelve result payloads, no dead
seat reported. Evidence is committed at `census/round-56/wave/` (not the ignored live
`.ufo/waves/` paths). Shape: scout 1, connector 1, executor 2, scribe 1, reviewer 2,
critic 1, mutation-tester 2, sentinel 1, revenger 1; attack share 5/12, connector 1.
The L1 holds planner. The prereg's prose role list totals eleven rather than twelve;
the validated dispatch and results are authoritative. No replacement seats.

- **scout01:** all pins match; fixture determinism verified; source census rc 0.
  Full routed-item inventory remains explicit (open list in report).
- **connector01:** seven overlapping numstat/append-only surfaces across kaidoku and
  kama, one exact binary-refusal disposition; no C2 grammar overlap. Existing kaidoku
  and chousa splitlines mechanisms are latent on measured inputs. This is lane-local
  work, not fleet-first. Sibling files were not edited.
- **executor01:** AGREE on C1 selftest 33/33, wrong pin rc 2, official/dry-run matrices,
  T1–T5 TSV-only derivation and real-lane receipt. All four TSVs reproduce byte-exactly.
- **executor02:** AGREE on C2 selftest 18/18, wrong tool pin rc 1, matrices, T1–T3,
  real-lane receipt. Thirteen carry-over C2 rows unchanged.
- **scribe01:** S277 VERIFIED (two live fetches, identical digest, quotes 19/8 words,
  recheck True True, single used-by append). Found the entry's mid-line wording wrong;
  an append-only correction now states that genuine mid-line mentions hide nothing.
- **reviewer01:** ATTACK-FOUND. Twenty-nine attacks: five mechanical narrowing rows,
  of which two demonstrate actual hidden-filing harms, eight shared limits, thirteen
  named refusals, three controls. B4 (NBSP prefix) and C4 (closed multiline inline
  comment) hide both correction tokens in an independent CommonMark render, while v4
  exits 1 CORRECTION-IN-FENCE and v5 exits 0 filed=2. This is a **HIGH no-harm failure**.
  The thirty-three frozen matrix controls still reproduce; no frozen byte is edited.
- **reviewer02:** ATTACK-SURVIVED. Seventy-five receipt shapes: zero narrowing harms,
  eight intended repair-direction results, three relabels. Punctuation/non-ASCII key
  attempts, non-KV NUL and leading BOM remain shared limits, explicitly listed.
- **critic01:** SURVIVED on the finite predicates. An always-zero stub fails detection
  clauses; both real-lane zero-result clauses alone accept it, guarded by the other
  clauses. F7-FF2 is carry-over pinning, not new v5 discrimination. Controls lack the
  exact EXIT trailer convention; original observed-rc:128 bytes remain frozen.
- **mutation01:** 8/10 C1 mutants killed. M1 (secondary PAIR-FILING-HIDDEN emission)
  survives first-finding-only assertions; direct pristine output verifies it, but
  selftest kill power needs all-findings/summary assertions. M7 LF parser survives,
  already de-claimed because the monitored paths are fixed ASCII constants.
- **mutation02:** N1/N2 key regressions killed; FA9/FB4 omission killed by row-set check.
  N3 (removing the row-set loops) survives the ordinary selftest; N3+arm omission
  prints cases=17 exit 0. T6 holds on pristine frozen bytes, but guard self-coverage
  remains a gap. Dotfile over-refusal is caught by the real capture, not selftest.
- **sentinel01:** two MEDIUM findings (quadratic line-number work, unescaped terminal
  control bytes in diagnostics), LOW scratch-symlink/.pyc/memory/attribute limits;
  timeout exception mapping is explicitly INFERENCE, unexecuted. No code-execution
  escape found in tested Git config/attributes shapes. Report contains exact receipts.
- **revenger01:** 41-row r55-item map, every item classified; open work remains routed
  to r57, not silently closed. Frozen r55 counter bytes unchanged.

### Admission / no-harm verdict

C1: finite predicate met, calibration **harmed** by B4/C4. C2: finite predicate met,
coverage improved on the declared finite key surface; no narrowing harm found in its
75-shape differential. Operability unchanged. Whole round: **rejected-harmed**, honest
stop. No operator ruling is assumed and no continuation round is started here.

### Further mistake and criterion

| class | evidence | captured-by | fix |
|---|---|---|---|
| block-start condition mistaken for complete visibility semantics: narrowing to line-start comments repairs F29 but admits real multiline inline comments | reviewer01 B4/C4 paired v4/v5 receipts and CommonMark renders in census/round-56/wave/w1/S56reviewer01/reproduction/ | Q112 differential caught it only after freeze; fixture population had no closed inline-comment control | Q114 below; new counter generation must pin both hidden inline and visible prose cases before scoring. Frozen v5 remains unchanged, and the round reports harmed |
| measurement receipt overwritten after landing | committed landing-suite-standing.txt was a usage-error record, then overwritten by a dirty-tree refusal | executor01 comparison of committed and working bytes | restore original byte-exact; preserve dirty refusal at landing-suite-dirty-refusal.txt; final suite uses a distinct staged receipt |
| context forbade all git mutation while asking seats to build committed fixtures | reviewer01 asked for clarification before probing | seat boundary review | explicit scratch-only builder init/config/add/commit authorization sent to all twelve seats; lane/fleet/sibling mutations stay forbidden |

### Errata to frozen prose (no frozen files changed)

- C1 docstring still claims a prose comment-token mention opens a region: stale v4 text,
  contradicted by implementation and F29. The true v5 behavior is line-start-only.
- Prereg C2 mentions T9, but has T1–T7; this means T6 (row omission).
- Prereg C1 calls F7-FF2 “closed”; read “exact-byte carry-over pinned”, not a new kill.
- C2 matrix has sixteen repository fixtures plus two selftest-only arms (eighteen
  selftest rows). The SCORECARD's “18 receipt rows” before value names selftest scope,
  not the matrix row count.
- The claim receipts at cce21b55 have EXIT=0. Matrix data uses its explicit exit column;
  it is TSV, not a command receipt with an appended EXIT line.

### Tools and self-evaluation

Reviewer01 installed markdown-it-py 4.2.0 and mdurl 0.1.2 via official PyPI/uv into a
scratch venv for independent CommonMark rendering; that venv was deleted. No host
package transaction, service restart or permanent install occurred.

Self-evaluation: accuracy 2/5 (real hidden-filing regression), completeness 4/5 (end-to-end
round and attack evidence, finite scope disclosed), clarity 3/5 (stale frozen docstring
and mismatched T9 label), actionability 4/5 (paired receipts and concrete next predicate),
conciseness 3/5 (large protocol/evidence overhead); mean 3.2. Highest-impact next move:
closed inline-comment negative controls before freezing; then all-findings mutation
assertions. User should see this as a documented rejected round, not an admitted repair.
