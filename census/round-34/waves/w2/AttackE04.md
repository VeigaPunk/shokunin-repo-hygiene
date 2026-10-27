# AttackE04 — adversarial falsification of the W1 finding for C1 item E04 (souji r34 w2)

Seat: SwarmReviewer08. Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Base 9c76c7222a8abff027af42e37f0d160d52526bba; freeze / re-pin 2b0171e2071fdc9c16a69bed12b0d040e574d8c8. Read-only: no lane file, frozen item, predicate, or counter byte was altered. Scratch: /fast/scratch/hyaku/souji-r34/e04 (112 KB).

## Status

W1's E04 finding is **CONFIRMED, not falsified** — with one rule-shape observation, not a defect.

1. The calibration defect is real: SCORECARD.md:21 (base 9c76c72) states the round-28 landing gate reads `rc 2` / `SUMMARY findings=0 checked_reg=52` at `de478b483db66a8d8ff2d627cde1ccce6e21a014`, but the post-r30 gate at the same pinned rev exits 1 with `SUMMARY findings=19 ... checked_reports=61` (reproduced; committed do-nothing record `census/round-34/records/controls-c1-do-nothing.txt:27`).
2. W1's claim that the frozen `same` (value-drift) branch is unusable is **provably correct**: at every pre-r30 revision the gate's `COULD-NOT-EVALUATE` warning lands on stderr, and the counter appends stderr after stdout (`census/round-34/c1-counter.py:239,304`), so the run's last digit-bearing line is the warning (it embeds the 40-hex rev), never the SUMMARY. No revision can satisfy the original `(exit=2, predicate)` pair — I searched for a bypass and found none (Attack log A4).
3. W1's proposed restatement row (deliver-c1-E04.md:42) passes every engine check individually verified against committed bytes: argv-correction branch (`rrun != "same"`), cause fec846dd1781a414ae3a7d71d2d8fa2fb17900eb is the **unique** first writer of the row's exact line text (`git log -S` over SCORECARD.md returns only fec846dd), ancestor of --list-rev, line absent at parent de478b48 / byte-equal at cause, row's argv already fails at the cause (executed: rc=2, warning-last). No honest rule-conforming route was missed; the encoding is effectively unique.

## Evidence

### Frozen inputs

- Item row, `census/round-34/c1-items.tsv:43` (columns per :12-13):
  `E04 | SCORECARD.md:21 | exit=2 | pred="SUMMARY findings=0 checked_reg=52" | files=tools/souji-landing-gate.py | at={REV} | argv="python3 -B tools/souji-landing-gate.py --root . --rev de478b483db66a8d8ff2d627cde1ccce6e21a014 --round 28 --fleet-root /home/vgpnk/Projects/shokunin"`
- Restatement contract: `census/round-34/preregistration.txt:48-56` (row cells; cause must be EXECUTED — value drift: original holds at cause's parent, fails at cause; argv correction: cause wrote the row and the row's argv already fails at the cause; append-only; Q76 prior-binding → AGREE). Amendment A1 (`preregistration.txt:138-141`): corrected-argv rows are evaluated with the corrected argv at --rev; foreign-script corrections are BAD-ROW; a restated statement must equal the run's collapsed LAST digit-bearing line. No amendment relaxes cause discipline.
- Committed do-nothing record, `census/round-34/records/controls-c1-do-nothing.txt:27`:
  `ITEM	E04	MISMATCH	original	rc=1 expect_exit=2 predicate fails last=SUMMARY findings=19 checked_reg=52 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=19 status_lines=58 carry_heading=0 checked_reports=61 load=11.85`

### Committed facts (all checked, no execution needed)

- `SCORECARD.md:21` is byte-identical at base 9c76c72 and at --list-rev 2b0171e2 (the `C1 Q57/Q59 pointer findings` row); at parent de478b48 line 21 differs (`after at 765fe8bd…` tail); at fec846dd it is byte-equal to the list-rev line (`diff` of the two `git show … | sed -n 21p` outputs: empty).
- `git log --format=%H -S'measured at \`de478b483db66a8d8ff2d627cde1ccce6e21a014\`' -- SCORECARD.md` → only `fec846dd1781a414ae3a7d71d2d8fa2fb17900eb` (unique first and only writer).
- `git merge-base --is-ancestor fec846dd… 2b0171e2…` → 0 (ancestor). `git rev-parse fec846dd^1` = de478b48.
- fec846dd touches: `SCORECARD.md`, `census/round-28/records/c1-after.tsv`, `c2-after.tsv`, `c3-after.tsv` — no tools/ file, which is exactly why a `same`-cell row for this cause would be BAD-ROW(cause touches none of the item files) (`c1-counter.py:285-287`).
- Q76: `git show 2b0171e2:SCORECARD.md | grep '| E04 |'` → no match (no prior correction binds E04).
- Counter mechanics: stdout+stderr concatenated with stderr last (`c1-counter.py:225-227` capture, `:239` and `:304` `lines = out.splitlines() + err.splitlines()`); last digit-bearing line = last line containing any digit (`:110-111`); `same`-cell rows take the value-drift branch (:284-291), backticked-run rows take the argv-correction branch (:292-300); restated statement must equal the collapsed last digit-bearing line (:311-313).
- Pre-r30 gate (blob `fec846dd:tools/souji-landing-gate.py`): report scan is single-prefix tree scan `.ufo/waves/round-<N>/*.md` (:469-474) raising `EvalError("no .md reports under %s at %s" % (prefix, rev))` — the message embeds the rev; `COULD-NOT-EVALUATE\t<error>` goes to **stderr** (:1167), SUMMARY to stdout (:1152-1166).
- At de478b48: 0 committed `.md` under `.ufo/waves/round-28/`, 61 under `census/round-28/waves/` (`git ls-tree -r de478b48 --name-only | grep -c …`) — the r31 union fix (`9c76c72:tools/souji-landing-gate.py:57,511`) is what makes the modern gate see the capture.
- Gate stability: `git log --oneline 9c76c72..51acb5fb -- tools/souji-landing-gate.py` → 0 commits; C1's touched list (`preregistration.txt:68-70`) cannot touch tools/.

### Executed reproductions (bounded probes; commands verbatim)

Scratch `/fast/scratch/hyaku/souji-r34/e04`; `git -C <lane> cat-file blob fec846dd…:tools/souji-landing-gate.py > pre30-gate.py` (2326 lines). Lane untouched (gate git calls are read-only ls-tree/cat-file; TMPDIR pointed at scratch).

Probe 1 — pre-r30 gate bytes at the pinned rev (this is also the run the engine makes at the cause in `holds(..., cause)`):
```
env -i PATH=/usr/bin:/bin HOME=/root GIT_CONFIG_NOSYSTEM=1 TMPDIR=/fast/scratch/hyaku/souji-r34/e04 \
  python3 -B pre30-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev de478b483db66a8d8ff2d627cde1ccce6e21a014 --round 28 --fleet-root /home/vgpnk/Projects/shokunin
→ rc=2
  stdout: SUMMARY\tfindings=0\tchecked_reg=52\tchecked_changed=0\tchecked_pins=13\tchecked_measured=3\tchecked_markers=0\tstatus_lines=0\tcarry_heading=0\tchecked_reports=0
  stderr: COULD-NOT-EVALUATE\tno .md reports under .ufo/waves/round-28/ at de478b483db66a8d8ff2d627cde1ccce6e21a014
```
Combined order (stdout then stderr) ⇒ last digit-bearing line = the stderr warning ⇒ original predicate `SUMMARY findings=0 checked_reg=52` fails although rc matches. Original therefore fails at de478b48 (fec846dd's parent), at 7b16731, and at fec846dd — value drift is unexecutable at any cause; the argv-correction branch is the only executable route. (Same reading at 7b16731 was W1's probe, deliver-c1-E04.md:14-20; mine is at the fec846dd bytes, which govern the engine's `holds` at the cause.)

Probe 2 — current gate bytes (base == tip through 51acb5fb) at the same pinned rev:
```
env -i PATH=/usr/bin:/bin HOME=/root GIT_CONFIG_NOSYSTEM=1 TMPDIR=/fast/scratch/hyaku/souji-r34/e04 \
  python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev de478b483db66a8d8ff2d627cde1ccce6e21a014 --round 28 --fleet-root /home/vgpnk/Projects/shokunin
→ rc=1, stderr empty
  stdout: 19 × LG-SEAT-UNCARRIED census/round-28/waves/w1/*.md … then
          SUMMARY\tfindings=19\tchecked_reg=52\tchecked_changed=0\tchecked_pins=13\tchecked_measured=3\tchecked_markers=19\tstatus_lines=58\tcarry_heading=0\tchecked_reports=61
```
This is exactly W1's restated statement and exit, and it matches the committed do-nothing ITEM line (controls-c1-do-nothing.txt:27). Output is provenance-stable: both gates read committed bytes via ls-tree/cat-file at the pinned rev (base gate docstring :21-22, :511), so the reading does not depend on the --root checkout state (my --root was the lane worktree at HEAD adac8bbc79a7; output byte-matches W1's fresh-clone readings and the committed controls).

Not executed by me: the full counter end-to-end on an appended row (W1 ran it; deliver-c1-E04.md:40-44 reports `ITEM E04 AGREE restated rc=1 expect_exit=1 statement is the run's last digit-bearing line …`). My confirmation is per-check analytic (each engine condition verified against committed bytes and the probe runs above), plus W1's executed engine run. A 77 MB lane clone exceeded this wave's scratch ceiling, so I did not re-run it.

## Findings

1. **CONFIRMED (W1 E04 blockage claim):** the frozen `same`/value-drift branch cannot bind E04 at any cause — the pre-r30 gate's digit-bearing COULD-NOT-EVALUATE line always trails the SUMMARY under the counter's stderr-last concatenation (`c1-counter.py:239,304`; pre-r30 gate `fec846dd:tools/souji-landing-gate.py:469-474,1167`). Executed, not inferred (Probe 1).
2. **CONFIRMED (W1 proposed repair valid):** the deliver-c1-E04.md:42 row passes every frozen check — 7 cells parse (no ` | ` inside cells); exit 1 = executed rc; statement byte-equals the executed collapsed last digit-bearing line (Probe 2); argv names the row's own script (`souji-landing-gate.py`); cause full40, ancestor of --list-rev, wrote the row's line (absent at parent, byte-equal at cause), row's argv already fails at the cause (rc=2 but predicate-fail on the warning-last line, Probe 1); Q76 clean; A1(a) evaluates the row with its (unchanged) argv at --rev.
3. **NO MISSED ROUTE:** (a) a `same`-cell row is impossible twice over — fec846dd touches none of the item's files (`c1-counter.py:285-287`) and the original holds at no parent anywhere (pre-r30: warning-last; post-r30: rc 1 ≠ 2; the gate's error text always embeds the rev, so no digit-free-error state exists that would let the stdout SUMMARY be last); (b) the mechanism cause 68447afef62e4761249af55a2467657f04046537 cannot serve the argv-correction branch because it does not touch SCORECARD.md (touches only `census/round-30/records/c2-fixture-red-before.txt`, `tests/fixtures/r30-landing-gate-discovery.py`, `tools/souji-landing-gate.py`), so "cause wrote the row's line" fails; (c) fec846dd is the unique first writer (`git log -S`, single hit); (d) given the gate's deterministic output, `(exit=1, statement=SUMMARY findings=19 …)` is the only agreeing (exit, statement) pair. W1's row is effectively the unique rule-conforming repair.
4. **RULE-SHAPE OBSERVATION (not a W1 defect):** the counter keys the cause branch on the row's run-cell *form* (`same` vs backticked), not on whether the argv actually differs; an argv-correction row may carry an argv identical to the frozen one. The frozen text (preregistration.txt:49-53, A1 :138-141) and the junk controls (preregistration.txt:66) do not forbid this, and here it is the only executable encoding — but a future auditor could reasonably require an exit/statement-only drift to ride a value-drift cause. Worth one line in the round lesson; it does not invalidate E04.
5. **Minor narrative gap (non-blocking):** W1's reason cites "68447af: rc 1 findings=19 on the same rev de478b48" as executed. I verified source-level support only (the r30 gate already references the census capture, 14 hits in `68447af:tools/souji-landing-gate.py`) and did not execute at 68447af. The claim is not load-bearing for the row's validity.

## Attack log

- A1. Wrong where-cell? No — SCORECARD.md:21 is the `C1 Q57/Q59 pointer findings` row at base and at list-rev (byte-identical), so the engine's `line_text` is the row W1 quotes.
- A2. Cause not first writer / line present at parent? Falsified the W1 claim attempt — parent's line 21 differs, cause's is byte-equal, `git log -S` shows fec846dd is the only commit ever introducing the text.
- A3. Cause not an ancestor / bad parent? `merge-base --is-ancestor` → ancestor; `fec846dd^1` = de478b48.
- A4. Value-drift route W1 missed? Exhausted: original needs rc=2 AND SUMMARY-last. Pre-r30 gate always emits the digit-bearing warning on stderr (Probe 1, executed at the exact cause bytes); post-r30 gate never exits 2 on this rev (Probe 2: rc=1); a digit-free error message (which would leave the stdout SUMMARY last) is unreachable because every report-scan error embeds the rev and no other EvalError path fires for round 28 at de478b48. No such revision exists.
- A5. `same`-cell encoding? Blocked twice: cause-touches-item-files fails (fec846dd touches no tools/) and original-at-parent=True is unreachable (A4).
- A6. Mechanism cause 68447af via argv-correction? Blocked: it did not write the row's line (no SCORECARD.md in its touched files).
- A7. Q76 prior binding? None at list-rev (`grep '| E04 |'` empty).
- A8. Measurement artifact? At base the mismatch survives any stream-ordering choice: rc 1 ≠ 2 and findings=19 ≠ 0 independently fail the original row; the committed do-nothing record and Probe 2 agree.
- A9. Statement drift at landing/tip? Gate unchanged base→51acb5fb (0 commits), findings derive from pinned-rev committed bytes, C1's touched list cannot touch tools/ or census/round-28 — reading stable.
- A10. Amendments loosening the rules? A1 strictly tightens (argv override, file-naming check, last-digit-line binding); no relaxation affects E04.

## Deliveries

- This report: `.ufo/waves/round-34/w2/AttackE04.md`.
- Seat report: `.ufo/waves/round-34/w2/SwarmReviewer08.md` (same verdict, condensed).
- Scratch: `/fast/scratch/hyaku/souji-r34/e04/` (112 KB: pre30-gate.py, probe stdout/stderr captures). No lane file, frozen artifact, or other repository was modified; no commits or pushes.
