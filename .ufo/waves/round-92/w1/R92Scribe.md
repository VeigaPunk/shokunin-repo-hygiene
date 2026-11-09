# R92Scribe report (souji r92, seat w1): round-lesson Mistakes, QUALITY draft, S355 Gate skeleton

Verdict: NO-FALSIFICATION for C1 and C2 (what I tried is listed below). Drafts only: no product code, no commit,
no git mutation, no edit to frozen instruments. One process finding (M4) is routed to L1, not decided here.
Receipts: `.ufo/waves/round-92/w1/R92Scribe/receipts/` (text only). Scratch `/fast/scratch/hyaku/souji-r92/R92Scribe/`
removed before yield. Tooling: none installed; read-only `git show`, python3, awk, grep only.

## Experiments run (all under the seat dir receipts)

- E1 residue check on the survivor search (stub harness, 47 ids from census/round-92/c1-targets.json, --jobs 4):
  filed `census/round-92/c1-survivor-search.py` -> `residue_w_dirs=0 residue_bytes=1617492`
  (`receipts/run-filed.txt`, `receipts/residue.txt`); same script with the `shutil.rmtree(os.path.join(d, "w"))` line
  removed (`receipts/search-no-delete.py.txt`) -> `residue_w_dirs=47 residue_bytes=189617492` (`receipts/run-no-delete.txt`).
  The stub is `receipts/stub.py` (writes 4 MB per run, not 0.7 GB; the check counts directories, not real clone bytes).
- E2 NF1r reproduction on the pristine counter (`census/round-87/c1-pointer-counter.py`, sha256 fd0a8e24...):
  65-row population `receipts/pop65.tsv` = the filed r92 population plus NF1 with id NF1r and expect_rc 0, run with
  `receipts/harness65-pinonly.py.txt` (the filed harness with one added POP_PINS entry for the 65-row sha; nothing
  else changed). Output `receipts/run-nf1r.txt`: `ROW NF1r where=lane rev=BASE item=P19 class=TOKEN expect=REFUSED/0
  got=REFUSED rc=1 match=no`, `SUMMARY rows=65 mismatches=1 accepted=0 refused_true=0 errors=0`. This reproduces the
  discarded probe `census/round-92/controls/nf1r-draft-probe.txt` and confirms prereg STATED LIMIT (ii); it does not
  falsify it. (The forge-file write that produces MISMATCH is harness line 492; I read it, I did not isolate the
  counter's exit-code path, so "rc 1 on every forge row" rests on the rows measured here: LP3 and NF1r.)
- E3 counting rule (Q167 below) on the population files: forge-path rows with a non-dash expect_rc not equal to 1:
  `census/round-91/c1-false-rows.tsv` = 0, `census/round-92/c1-false-rows.tsv` = 0, `receipts/pop65.tsv` = 1.
- E4 provenance (read-only git): `git show 44d45b44:census/round-92/c1-survivor-search.py` (sha 8755b53f...) has the
  per-tree rmtree at line 89; `git show 1d015a2d:...` (sha c393d941..., the filed script) has it at line 104. The diff
  between them adds the --timeout/hung kill, the ambiguous/hung counters, the `SEARCH`/`SKIP` lines and `--ids`; the
  scoring path is otherwise unchanged. The pre-freeze feasibility receipt `census/round-92/controls/c1-feasibility-r92-prefreeze.txt`
  was run with 8755b53f; its header says so only implicitly (`# search sha256=8755b53f...`). Documented, no action.
- E5 S355 locators (`census/round-92/srcs/unicode-ch3.txt`, one line): the D86 quote occurs once, starting at byte
  133992 (`grep -b` of "do not overlap with minimal" = 134026, offset of "do not"); "Table 3-7. Well-Formed UTF-8 Byte
  Sequences" heading at byte 141263 (`grep -b`). Both captures re-hash as recorded in SOURCES.md S355 (html f9e158a6...,
  428731 bytes; text 545d4e42..., 215485 bytes).

## Mistakes

Format: class · evidence pointer · captured-by · fix (with the check that can fail).

- M1 · class: fan-out runner keeps every per-mutant lane clone (no delete after scoring). Evidence: the 260 x ~0.7 GB =
  185 GB figure is stated in `census/round-92/preregistration.txt` (INHERITED paragraph) and `.ufo/waves/round-92/build-spec.py:106`;
  both are orchestrator-sourced, the attempt-1 script is uncommitted (its header sha 00609b8d in
  `census/round-92/records/c1-search-r91-attempt1-header.txt`), so the figure is [INFERENCE], not measured in the lane.
  The mechanism is in-repo: each harness run clones the lane into its `--work` (`census/round-92/c1-false-row-harness.py`
  build_fixture, `git clone --shared`), and the search passes that `--work` down per mutant. · captured-by: the orchestrator message (outside the lane) and the attempt-2
  amendment recorded in the prereg. · fix: `shutil.rmtree(os.path.join(d, "w"), ignore_errors=True)` after scoring, on
  the hung and scored paths (`census/round-92/c1-survivor-search.py:104`). Shown able to fail: `receipts/residue.txt`
  (E1): with the line removed the same run leaves 47 `w` trees, with it 0. Check: `find WORK -mindepth 2 -maxdepth 2 -name w -type d | wc -l`
  must print 0 after every search run.

- M2 · class: an expectation column read as an exit assertion that the harness encodes as a forge status (the cell
  `REFUSED/0` reads as "counter exits 0", the forge writer writes MISMATCH whenever the rc cell is non-dash). Evidence:
  `census/round-92/controls/nf1r-draft-probe.txt` (`ROW NF1r ... expect=REFUSED/0 got=REFUSED rc=1 match=no`, SUMMARY
  mismatches=1); `census/round-92/c1-false-row-harness.py:492`; reproduced in `receipts/run-nf1r.txt` (E2). · captured-by:
  the pre-freeze probe (red on the pristine counter) and then the harness read; prereg STATED LIMIT (ii) records it. ·
  fix: the row was dropped before freeze and the limit stated; Q167 turns the cause into a count. Shown able to fail:
  the Q167 command prints 1 on `receipts/pop65.tsv` and 0 on both the r91 and r92 populations (E3).

- M3 · class: an instrument trusted a lead byte's declared length (the tail cut moved by C0-DF 2 / E0-EF 3 / F0-F7 4), so
  an ill-formed lead before the cut absorbed the next well-formed sequence. Evidence: `corpus/lessons/round-91.md` M3;
  `.ufo/waves/round-91/w1/R91ExecC2Tool/repro-cut-tail-split.txt`; `.ufo/waves/round-91/w1/R91Scribe/cut-edge-probe.txt`;
  the r91 tool's `_cut_tail` at `census/round-92/controls/c2-before-tool.py:242`. · captured-by: attack seats R91ExecC2Tool
  and R91Scribe, independently; the frozen r91 predicate (KFF11) used only a valid payload and stayed green. · fix: a
  strict-decode `_straddling_sequence` (Table 3-7 by decode, `tools/souji-record-agreement.py:218-233`) used by
  `_cut_head` and `_cut_tail` (`:235-250`). Shown able to fail: `census/round-92/controls/c2-control-r91-tool-both-arms.txt`
  reads the r91 tool red on KFF14, KFF15, KFF16 and KFF18 (`tool_pass=16`); the filed tool passes 20/20
  (`census/round-92/records/c2-after.txt:29`).

- M4 (process, routed to L1, not decided here) · class: a predicate command states a job count above the seat cap.
  Evidence: `census/round-92/preregistration.txt:46` (`--jobs 8`), `census/round-92/records/c1-after.txt` (`--jobs 8`),
  `census/round-92/records/c1-search-r91-full.txt` (`--jobs 10`), `.ufo/waves/round-92/build-spec.py:80` ("--jobs 4 at most").
  · captured-by: this seat's read of the spec against the prereg. · fix options for L1: record a wave amendment that
  states the job count the predicate was run with, or change the cap in the spec. Check: `grep -o -- '--jobs [0-9]*'
  census/round-92/preregistration.txt` must not exceed the cap in force. Effect on the SUMMARY counts is unmeasured
  ([INFERENCE]: the search's `hung` count is timing-sensitive under load).

## QUALITY criterion draft (next free number after Q166)

| id | criterion | applies-to | test | lesson |
|---|---|---|---|---|
| Q167 | A pinned population's non-dash `expect_rc` cell is asserted only on a row whose judging path has been measured to produce that exit code. A forge-path row (`where` = `lane` or `fixture`) is written to a forge file whose status is MISMATCH whenever its cell is non-dash (`census/round-92/c1-false-row-harness.py:492`); every such row measured so far exits 1 (LP3, NF1r). A forge row with any other cell value (NF1r: `REFUSED` with `0`) is red on the pristine counter by construction and is refused in the candidate population before freeze, not discovered by a probe after it. | population + harness pairs in calibration batteries | `awk -F'\t' '!/^#/ && NF>0 && ($2=="lane" \|\| $2=="fixture") && $9!="-" && $9!="1"' POP \| wc -l` must print 0. Measured: r91 population 0, r92 population 0, NF1r candidate (`.ufo/waves/round-92/w1/R92Scribe/receipts/pop65.tsv`) 1 (E3); the NF1r run (`receipts/run-nf1r.txt`) shows the same row red on the pristine counter. | `census/round-92/controls/nf1r-draft-probe.txt`; `corpus/lessons/round-91.md` (M3 class: a declared count trusted over the measured outcome) |

Note on scope: `SUMMARY mismatches=1` already caught NF1r; what the probe lacked was the reason. Q167 moves the reason
into a count that runs on the candidate population before the probe does.

## Gate skeleton: S355 (for the L1 gate block; reject-sample slot left open)

- id: S355
- title: The Unicode Standard, Version 18.0.0, Chapter 3 Conformance, §3.9 Unicode Encoding Forms (D84a-D86, Table 3-7 Well-Formed UTF-8 Byte Sequences)
- URL: https://www.unicode.org/versions/latest/core-spec/chapter-3/ (redirects to https://www.unicode.org/versions/Unicode18.0.0/core-spec/chapter-3/)
- access date: 2026-11-08
- capture: `census/round-92/srcs/unicode-ch3.html` sha256 f9e158a640c88cb0aebf60e5f724ea4f957eca539c620fb1e161cb6c8f8fb22e (428731 bytes); text `census/round-92/srcs/unicode-ch3.txt` sha256 545d4e42cd9647dbaafcdb250c01a15f6b21a4614331006db63f7b475ca5e6f1 (215485 bytes, one line)
- quote (13 words, occurrence 1 in the text capture): "Ill-formed code unit subsequences do not overlap with minimal well-formed code unit subsequences."
- locator: `census/round-92/srcs/unicode-ch3.txt` line 1, byte offset 133992; the sentence sits in the §3.9 block immediately before D87 (the knowledge entry attributes it to D86)
- secondary locator (Table 3-7 heading): byte offset 141263, "Well-Formed UTF-8 Byte Sequences"
- reject-sample slot: `[OPEN: R92ScoutSources proposal, not drafted by this seat]`
- used-by: `corpus/knowledge/utf8-window-well-formed-cut.md`; census row S355 already in `corpus/SOURCES.md:294`

## Named limits, dispositions, and falsification check

- NO-FALSIFICATION. C1: E2 reproduces the stated limit (ii) and nothing more. C1's 47-kill and control counts were not
  re-run (that is the verifier seats' job). C2: no artifact of this seat touched the tool or fixture; E5 re-derives the
  S355 locator only.
- Not a falsification, recorded: M1's 185 GB figure is orchestrator-sourced; M4 is a process conflict between the
  prereg predicate text and the wave cap, not a claim sentence; E4's feasibility-hash difference is documented in the
  control file.
