# AttackE05 — adversarial falsification of W1's C1 E05 finding

Seat: SwarmCritic09 (round 34 souji wave w2). Target: W1 `deliver-c1-E05.md`.
Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`; base `9c76c7222a8abff027af42e37f0d160d52526bba`;
frozen list rev `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`; W1 cause `fec846dd1781a414ae3a7d71d2d8fa2fb17900eb`.

## Status

**W1 finding UPHELD.** The alleged do-nothing defect is real and independently reproduced; the frozen
six-case predicate cannot hold at base under any honest measurement; the proposed
argv-correction restatement (`2>/dev/null`, statement `cases=15 pass=15 control=TAMPER-REJECTED`,
cause `fec846dd…`) conforms to every frozen rule I traced in `census/round-34/c1-counter.py`; and I
found **no honest rule-conforming route W1 missed**. Two minor evidence-quality defects in W1's
deliverable (a wrong quoted list hash; a loose paraphrase of an r33 registry row) do not change the
verdict. The mismatch is best characterised as a *measurement artifact of the counter's out+err
concatenation rule combined with a stale registry literal*, exactly as W1 diagnosed.

## Evidence

Frozen item (byte-identical at worktree and at list-rev blob; `census/round-34/c1-items.tsv:44`,
7-column layout per header `c1-items.tsv:10-14`):

```
E05	SCORECARD.md:23	0	cases=6 pass=6 control=TAMPER-REJECTED	tests/fixtures/r28-wave-evidence-capture.sh	{REV}	bash tests/fixtures/r28-wave-evidence-capture.sh
```

SCORECARD.md:23 at base (`git show 9c76c72:SCORECARD.md`) is the r28 "C3 evidence capture" row quoting
`fixture cases=6 pass=6 control=TAMPER-REJECTED` and the command ``bash tests/fixtures/r28-wave-evidence-capture.sh``.

Frozen counter rules actually applied (`census/round-34/c1-counter.py`):

- `lines = out.splitlines() + err.splitlines()` — **stderr is appended after stdout** (`c1-counter.py:304`, also `:239`).
- `last_digit_line` = last line containing `\d` (`c1-counter.py:110-112`).
- Statement agreement: `collapse(last_digit_line(lines)) == target` (`c1-counter.py:312-313`).
- Restatement checks: 7 cells after id; corrected argv must contain `os.path.basename(f)` of a row file (`:267`);
  cause must be an ancestor of list-rev (`:275`); the list-rev line text must be absent at the cause's
  parent blob and present at the cause blob (`:286-299`); the row's own frozen argv must FAIL at the cause (`:300`).
- Docstring `c1-counter.py:21-24`: argv-correction requires the cause to have written the row's line,
  the row's own argv to fail at the cause, and the corrected argv to run the row's own script.

Tool usage banner at base (`tools/souji-wave-evidence-capture.sh:88-95`) — the string `full40` in
`<full40>` supplies the digits that make this stderr line "digit-bearing":

```
Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]
```

Fixture contract at base (`tests/fixtures/r28-wave-evidence-capture.sh:15` and final printf):
`Prints cases=15 pass=<n> control=TAMPER-REJECTED` — the six-case literal is **unreachable at base**.

My bounded probes (scratch `/fast/scratch/hyaku/souji-r34/SwarmCritic09`, shared-objects clone, sparse
checkout of `tests/` + `tools/` only, 17 MB total, under the 50 MB ceiling; exact counter env:
`env -i PATH=/usr/bin:/bin TMPDIR=<fresh> GIT_CONFIG_NOSYSTEM=1 HOME=$HOME LANG=C.UTF-8 bash -c …`,
cwd = clone root):

1. **Base `9c76c72`, frozen argv** — rc=0; stdout's last line `cases=15 pass=15 control=TAMPER-REJECTED`;
   stderr (verbatim, 11 lines) ends with the 5-line usage banner preceded by
   `error: source directory not found: …/lane-2/.ufo/waves/round-26` (negative-case diagnostics from
   cases 2/13/14 of the fixture). Applying the counter's own rule (`out lines + err lines`, last
   digit-bearing): last = the usage banner. **Reproduces W1's quoted do-nothing ITEM exactly**
   (`last=Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]`),
   predicate `cases=6 pass=6 control=TAMPER-REJECTED` fails. Files: `probe1/stdout.txt`, `probe1/stderr.txt`.
2. **Base `9c76c72`, W1 corrected argv `bash tests/fixtures/r28-wave-evidence-capture.sh 2>/dev/null`** —
   rc=0; stderr = 0 bytes; last digit-bearing line = `cases=15 pass=15 control=TAMPER-REJECTED`,
   exactly the proposed statement. Statement match and exit match both hold.
   Files: `probe2/stdout.txt`, `probe2/stderr.txt` (empty).
3. **Cause parent `de478b483db66a8d8ff2d627cde1ccce6e21a014`, frozen argv** — rc=0; stdout's last line
   `cases=6 pass=6 control=TAMPER-REJECTED` (the old six-case fixture passes fully on stdout); last
   digit-bearing line of out+err = `error: source directory not found: …/lane-2/.ufo/waves/round-26` →
   frozen predicate FAILS at the parent too. Files: `probe-parent/stdout.txt`, `probe-parent/stderr.txt`.
4. **Cause `fec846dd1781a414ae3a7d71d2d8fa2fb17900eb`, frozen argv** — identical failure mode:
   stdout last `cases=6 pass=6 control=TAMPER-REJECTED`, out+err last digit line = the lane-2 error
   path → predicate FAILS at the cause. Files: `probe-cause/stdout.txt`, `probe-cause/stderr.txt`.

Non-execution verifications (read-only git inspection):

- `git blame -L 23,23 9c76c72 -- SCORECARD.md` → `fec846d` wrote SCORECARD.md:23 (matches W1).
- Judge's cause-line test: list-rev line 23 text `LINE-IN-PARENT: NO`, `LINE-IN-CAUSE: YES`.
- `git merge-base --is-ancestor fec846dd… 2b0171e…` → ancestor (exit 0).
- Q76 grep on base SCORECARD.md: exactly 3 hits for `SCORECARD.md:23`, all `R29-CORRECTION` prose at
  lines 295-297; line 297 explicitly disclaims the fixture literal ("the … fixture line
  `cases=6 pass=6 control=TAMPER-REJECTED` are working-tree and tool-run claims and are not re-derived
  here from committed bytes"). No prior correction row binds the cell → frozen literal stands, so the
  do-nothing mismatch is genuine and not already-AGREE under Q76. Matches W1's supersession grep.
- r33 registry row SCORECARD.md:314 at base is the full "committed-bytes wave-evidence capture (r29)" row
  recording `` `bash tests/fixtures/r28-wave-evidence-capture.sh` `cases=15 pass=15 control=TAMPER-REJECTED` (base tool 8/15) `` —
  same argv, same 15-case stdout outcome as W1's restated statement (substance confirmed; W1's
  printed mini-row `| L38 | … |` is a paraphrase, see Findings 6b).
- W1's simulation receipt (sim commit `b54a50e…` → `ITEM E05 AGREE restated … last=cases=15 pass=15
  control=TAMPER-REJECTED`): **not re-run by me** — the `RestateC1s6` scratch was cleaned and a full
  `--no-local` clone (~77 MB) exceeds the 50 MB scratch ceiling. Instead I traced `judge()` line by
  line against the frozen code and reproduced every input to it with probes 1-4 (see Findings 4).
  [INFERENCE, labeled]: the receipt is consistent with the frozen judge given my verified inputs.

## Findings

1. **The defect is real (reproduced, not inference).** At base with the frozen argv, the counter's
   last digit-bearing line (out+err) is the tool's usage banner, so the frozen statement
   `cases=6 pass=6 control=TAMPER-REJECTED` cannot match. Independently of the stderr question, the
   six-case literal is unreachable at base: the committed fixture's final line is hard-coded
   `cases=15 pass=%s control=TAMPER-REJECTED` (`tests/fixtures/r28-wave-evidence-capture.sh` final printf).
2. **No value-drift cause exists (reproduced).** At both the cause `fec846dd` and its parent `de478b4`,
   the era-correct fixture passes fully on stdout (old six-case layout prints exactly
   `cases=6 pass=6 control=TAMPER-REJECTED`) — the SCORECARD claim was literally true on stdout when
   written — yet the frozen predicate still fails under the counter's out+err rule because negative-case
   stderr diagnostics (lane-2 error path) supersede the summary. This is a measurement artifact, not a
   behaviour regression; W1's "no value-drift cause" claim is confirmed.
3. **W1's diagnosis is materially accurate.** "the fixture writes its negative-case diagnostics to
   stderr after the summary, and the counter reads out+err" — confirmed verbatim by probe 1. Minor
   wording quibble only: the do-nothing `last=` is the usage banner itself (digit supplied by
   `full40`), not "a stderr lane path, then the usage banner"; the lane-2 error path is the last
   digit-bearing stderr line *before* the banner. The quoted ITEM line is exactly right.
4. **The proposed correction is rule-conforming under the frozen judge (traced + reproduced).**
   For row `| E05 | SCORECARD.md:23 | restated | 0 | `bash tests/fixtures/r28-wave-evidence-capture.sh
   2>/dev/null` | `cases=15 pass=15 control=TAMPER-REJECTED` | fec846dd1781a414ae3a7d71d2d8fa2fb17900eb | <reason> |`:
   - 7 cells after id ✓; `where` equals the item's `SCORECARD.md:23` ✓; kind `restated` ✓; exit `0` ✓.
   - Corrected argv contains basename `r28-wave-evidence-capture.sh` of the row file (`c1-counter.py:267`) ✓.
   - Statement is backticked, contains a digit, and equals the corrected run's collapsed last
     digit-bearing line (`c1-counter.py:312-313`, probe 2) ✓.
   - Cause is full40, an ancestor of list-rev (merge-base exit 0) ✓; reason non-empty ✓; cause has a parent ✓.
   - Cause-wrote-line: list-rev line 23 absent at parent blob, present at cause blob (grep test above) ✓.
   - Row's own frozen argv FAILS at the cause (probe 4) ✓ — and as a bonus the same failure at the
     parent rules out any value-drift framing (probe 3).
   - Measured run (corrected argv) rc=0 = stated exit ✓.
5. **No honest rule-conforming route was missed.** Alternatives, all checked against the frozen code:
   - *Keep frozen argv, restate statement to the usage banner*: mechanically satisfiable (it IS the
     last digit line), but it would assert as the registry's claimed outcome a tool usage diagnostic
     from a deliberately-triggered negative case — false provenance; dishonest. W1 correctly avoided it.
   - *Keep frozen argv, bind the lane-2 error path*: not judge-conforming — that line is not the last
     digit-bearing line (the banner supersedes it).
   - *Any argv reproducing `cases=6 pass=6` at base*: impossible — the 15-case layout is in the
     committed fixture bytes; no CLI mode restores six cases.
   - *Value-drift restatement*: unavailable (Finding 2).
   - `2>/dev/null` runs the row's own script unchanged and aligns the measurement with the fixture's
     documented stdout contract (fixture header: "Prints `cases=15 pass=<n> control=TAMPER-REJECTED`"),
     corroborated by the r33 registry row (SCORECARD.md:314). This is the minimal, honest correction.
6. **Minor evidence-quality defects in W1's deliverable (do not affect the verdict):**
   a. The quoted "Counter bytes at --list-rev: sha256 `1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`"
      does **not** match the committed bytes: `git show 2b0171e:census/round-34/c1-items.tsv | sha256sum`
      = `5de3678206dcc091d2a2f911f0fe085021c90431d1e40edeea9dd15765b06127`, and the worktree file is
      byte-identical to that blob (diff empty, 78 lines both). The E05 row content W1 quotes is
      verbatim-correct; only the hash is wrong/unverifiable.
   b. The r33 row is quoted as a tidy mini-row `| L38 | SCORECARD.md:314 | cases=15 pass=15 | run: … |`;
      the actual base line 314 is the full r29 capability row (same argv and outcome recorded). Substance
      stands; the citation format is a paraphrase.
   c. W1's simulation receipt (b54a50e) was not independently re-executable under my scratch ceiling;
      I verified its inputs instead (Finding 4). Labeled inference, consistent.

## Attack log

- Read W1 deliverable, frozen TSV row 44, counter docstring + judge/holds mechanics. Established the
  out+err concatenation rule and last-digit-line predicate.
- First attack vector: "the usage banner has no digits, so W1's quoted do-nothing `last=` is
  impossible" — **defeated by probe**: `full40` in `<full40>` supplies `4` and `0`; computed last
  digit line = the banner exactly as W1 quoted. W1's record reproduced.
- Second vector: "maybe the old fixture fails differently at the cause / a value-drift cause exists" —
  defeated by probes 3-4: era-correct fixture passes on stdout at both parent and cause; predicate
  fails at both under out+err.
- Third vector: "maybe `2>/dev/null` is judge-rejected or dishonest" — defeated by judge trace
  (`c1-counter.py:267,275,286-300,304-313`) and probe 2: all checks pass; the measurement aligns with
  the fixture's own stdout contract and prior registry practice.
- Fourth vector: "maybe an honest route keeping the frozen measurement basis exists" — exhausted the
  mechanical alternatives (banner binding, error-path binding, six-case argv, value drift); all
  dishonest, non-conforming, or impossible.
- Fifth vector: Q76 — could a prior R29-CORRECTION already bind the cell (making the frozen literal
  stale-and-superseded, or conversely making W1's restatement a duplicate authority)? Grep of base
  SCORECARD.md: 3 prose corrections, none binds the fixture literals; line 297 explicitly disclaims
  them. Q76 clean.
- Scratch hygiene: sparse shared clone (17 MB) + four probes; no lane writes; no frozen-artifact
  mutation; probe outputs retained under `/fast/scratch/hyaku/souji-r34/SwarmCritic09/`.

## Deliveries

- This report: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w2/AttackE05.md`
- Seat report: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w2/SwarmCritic09.md`
- Probe evidence (scratch, retained): `/fast/scratch/hyaku/souji-r34/SwarmCritic09/probe{1,2,-parent,-cause}/{stdout.txt,stderr.txt}`
- Verdict: **W1 finding confirmed; no missed honest route; two minor evidence-quality defects flagged.**
