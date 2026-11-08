# S87Scribe — draft QUALITY.md criterion (Q-line)

Seat: S87Scribe (scribe). Draft for the L1 to integrate into `corpus/QUALITY.md`. Nothing committed; no lane file
edited.

## The rule this row carries

A diagnostic that truncates from the FRONT of a traceback is a defect. The last non-empty stderr line is where an
exception names itself; the first N characters of a traceback are the frame list (`Traceback (most recent call
last):` and the paths), which name nothing.

## Numbering decision for the L1 (read first)

The lane's working tree ALREADY carries this criterion as **Q161**, written at 06:50 during the wave. It is
uncommitted (`git diff corpus/QUALITY.md` shows `+Q161` and `+Q162` as the only additions). Two facts about it:

- **Its content is the rule this seat was asked to draft.** `corpus/QUALITY.md:397` reads: "A diagnostic that reports
  another process's failure truncates from the END, never from the front: the last non-empty stderr line is where an
  exception names itself, while the first 200 characters of a traceback are the frame list … A tool that delegates a
  check to a subprocess and reports \"no verdict\" prints that tail, bounded, with a leading ellipsis when the line
  itself is cut."
- **Its row SHAPE is wrong for this file.** The lane's table is `| id | criterion | applies-to | test | lesson |`
  (5 cells), and the file's own rules say "every criterion cites the lesson that produced it". Q161 as written has
  **4** cells: the `lesson` pointer is missing. (Q162, added beside it, has the same defect: 4 cells.) Every other
  row in the file has 5 cells except Q8/Q10/Q12/Q36/Q37/Q38/Q55/Q125/Q158 (6), Q14/Q151/Q152 (7), Q60 (8) and
  Q148/Q149 (3, a pre-existing pair that also lacks `applies-to`/`test`).

**Recommendation: do not add a second row.** File the criterion ONCE, in the lane's 5-cell shape. Two options for
the L1:

- **(a) Amend the uncommitted Q161 in place** — it is not yet committed, so it is not under the append-only rule
  (`corpus/QUALITY.md`: "a criterion is superseded by a new row that names the row it replaces, never rewritten"), and
  the row only needs its `lesson` cell filled. **This is the recommended path.**
- **(b) Leave Q161 as it is and file this seat's row as Q163** — then two rows carry the same rule, which the lane's
  own numbering style does not want and which a reader cannot tell apart. Only choose this if the L1 prefers the
  exact text below over Q161's; in that case Q163 must open "Supersedes Q161 —" and Q161's row must say so, per the
  file's rule.

This seat does not make that call; the L1 owns integration. Both texts are below so either path is one edit away.

## Draft row, in the lane's numbering style (5 cells)

Number: **Q161** if option (a) is taken (amending the uncommitted row); **Q163** if option (b) is taken, opening
"Supersedes Q161 — ".

| id | criterion | applies-to | test | lesson |
|---|---|---|---|---|
| Q161 | A diagnostic that reports another process's failure truncates from the END, never from the front: the last non-empty stderr line is where an exception names itself, while the first 200 characters of a traceback are the frame list (`Traceback (most recent call last):` and the paths). A tool that delegates a check to a subprocess and reports "no verdict" prints that tail, bounded, with a leading ellipsis when the line itself is cut. | every lane tool that reports a delegated process's failure through a record detail | `python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work <scratch>` must print KN1 `named=yes`; the base bytes (`census/round-87/controls/c2-before-base-tool.py`) must print `named=no` | corpus/lessons/round-87.md (C2 — the r86 routed defect `S86ExecK4` §2b answered here); `.ufo/waves/round-86/w1/S86ExecK4.md` §"Diagnostic defect (routed, low)" and its routed pointer at `souji-record-agreement.py:229-230` |

(The `lesson` cell is the only part of Q161's working-tree text this seat changes; the criterion, applies-to and test
cells above are Q161's own wording, re-read from `corpus/QUALITY.md:397`.)

## Why the lesson pointer is what it is

- The r86 wave's executor routed the defect: `.ufo/waves/round-86/w1/S86ExecK4.md:126` — "**Diagnostic defect
  (routed, low):** the message truncates the writer's stderr to 200 characters, so the operator sees `Traceback (most
  recent call last):` and never learns *which* attribute is missing." Its routed pointer is at `:379`
  ("`souji-record-agreement.py:229-230` truncates the writer's stderr to 200 chars; the (b) failure hides
  `AttributeError: … _flag_refusal`").
- The round-87 assignment names it: the seat spec lists "(C2) S86ExecK4 2b/2e/3b2: stderr-prefix truncation, the
  quoted status arm, the unbound writer delegation" among the r86 routed debts this round answers. The round's
  preregistration repeats it at `census/round-87/preregistration.txt` (C2 (c): the K4 detail carries the writer's
  LAST non-empty stderr line "instead of the first 200 characters, which can end inside the traceback frame list").
- The r87 lesson is the round's own lesson; its `## Measured` C2 paragraph is the round's record of the repair
  (`corpus/lessons/round-87.md`, "C2 (operability)"), and its `## Mistakes` M6 row is the round's own account of the
  `-z` repair's harm. **Note for the L1:** the r87 lesson has NO mistake row for the stderr truncation itself (the
  r86 routed defect was answered by the C2 repair commit `6e502c5c`, not by a mistake). If the L1 wants the lesson
  pointer to name a `## Mistakes` row, the lesson needs one appended; otherwise the pointer names the lesson's C2
  measured paragraph, which is what the draft above does.

## Independent verification of the row's test cell (this seat's own measurement)

The test cell's two halves were re-measured by this seat against the lane's COMMITTED bytes (the tip commit
`6e502c5c`, tool blob `4244ac26…`, sha256 `0ad9e3bf…`) — not against the worktree, which carries S87ExecC2's
later repair. Hermetic fixtures under this seat's scratch root (not /tmp); no lane byte read or written.

- **Filed side (KN1 `named=yes`).** A copy of the committed tool with a stub writer beside it (the stub raises
  `AttributeError` where the delegated byte-truth check would run, exactly the counter's `STUB_WRITER`) on a
  one-commit fixture:

      $ python3 -B <committed tool bytes> --root "$D" --rev "$(git -C "$D" rev-parse HEAD)" | grep '^MISMATCH\tK4'
      MISMATCH	K4	.	stat-cache-concealed	the receipt writer produced no verdict (exit 1: AttributeError: r87 KN1 stub: no truth helper); tracked bytes are unverified

  The exception names itself: `AttributeError` is in the detail.

- **Base side (KN1 `named=no`).** The lane-base tool bytes (`census/round-87/controls/c2-before-base-tool.py`,
  sha256 `cf875367…`) with the same stub writer beside it:

      MISMATCH	K4	.	stat-cache-concealed	the receipt writer produced no verdict (exit 1: Traceback (most recent call last):

  The detail ends INSIDE the traceback's frame list and never reaches the `AttributeError` line — the front
  truncation, exactly the defect the row forbids.

- The sealed counter's own reading of both arms was re-run by this seat as well and reads `SUMMARY rows=12
  mismatches=0 errors=0` / `EXIT=0` on the filed bytes and `mismatches=3` on the base bytes (see
  `quote-verification.txt` §6 for the full row list).

## One caution for the L1 (not a blocker)

The test cell names `tools/souji-record-agreement.py`, whose worktree bytes moved during the wave (S87ExecC2's
repair: sha256 `c2b0784e…` in the worktree vs `0ad9e3bf…` at the tip commit). The criterion is about the RULE, not
about a digest, so the row stays valid either way; but the L1 should re-file the C2 after receipt against whatever
tool bytes it commits, and the row's test cell should keep naming the counter (the frozen instrument) rather than a
tool digest that moves.
