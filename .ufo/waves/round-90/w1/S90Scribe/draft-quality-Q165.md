# Draft — QUALITY.md criterion Q165 (souji r90, seat S90Scribe)

Target: `corpus/QUALITY.md`, in a NEW section `## Round 90 criteria` appended after the `## Round 89 criteria`
section (which ends at line 410 with Q164; the file is 410 lines at lane tip `fd25bfc5`).

**Numbering.** The next free id is **Q165**: `grep -o '^| Q1[0-9][0-9] ' corpus/QUALITY.md | sort -u | tail -5`
reads `Q160 Q161 Q162 Q163 Q164`, and `grep -c "Q165" corpus/QUALITY.md` reads **0**. Q165 has never been used.

**Section format** (copied from the r88/r89 sections at lines 400-404 and 406-410):

```
## Round 90 criteria

| id | criterion | applies-to | test | lesson |
|---|---|---|---|---|
| Q165 | … |
```

> **READ THIS FIRST — the L1's landed narrowing changes what Q165 may say.** While this seat was drafting, the L1
> landed `plans/round-90.md` **A1** and **A4**, which narrow the C2 claim's *certification clause*, and **A5(c)**,
> which narrows what the fixture binds. A1's narrowed sentence is explicit:
>
> > *"The fixture's substring counts do NOT certify the word 'injective' on their own: a mutant that doubles the
> > U+0085 branch survives them (S90Sentinel H1). The injectivity evidence is the independent brute-force probe, not
> > the kill rule; the missing doubled-spelling conjuncts (`count(bs*2+"u0085")==0`, `count(bs*2+"x85")==0`) are
> > routed to r91."*
>
> and A4 adds: *"the KILL RULE's 'each one physical line' is not enforced"*, and A5(c): *"the fixture measures the
> pair; the deletion is measured by grep and load, not by the fixture."*
>
> **So Q165 must NOT say the fixture certifies injectivity, and must NOT lean on the fixture for the one-physical-
> line clause or for the dead-code deletion.** The row below is written to that constraint: the criterion's own
> requirement is that the pair be **MEASURED** — and A1 tells the lane what "measured" must mean for the criterion to
> be worth anything (a substring count is not a measurement of injectivity). The criterion below therefore requires
> a measurement that **separates the character from its own escaped literal**, and names the r90 fixture's measured
> weakness as the thing a future population must close.

## The row (paste-ready)

```
| Q165 | Extends Q164 and Q163 (they stand), and adds the clause A1 of the r90 round exposed: a record cell's escaping rule is only injective on a byte/character pair if the MEASUREMENT can separate the character from its own escaped literal. The two paths must reach the cell separately and carry distinct spellings — a byte that was not valid UTF-8 arrives through `surrogateescape` as the lone surrogate U+DC80-U+DCFF and takes `\\xNN` with its ORIGINAL byte value, while the character that DECODES to those same bytes (U+0085 NEL, encoded as `\\xc2\\x85`) takes `\\uNNNN`. The pair is MEASURED, not asserted, and the measurement must DISCRIMINATE: a bare substring count does not (the r90 fixture's `count(bs+"u0085")==1 and count(bs+"x85")==0` is satisfied by the escaped literal `\\u0085`, which CONTAINS the substring `\\u0085`, so a mutant that doubles the U+0085 branch's backslash passes the fixture 12/12 — S90Sentinel H1). A population therefore binds the pair only when it also asserts the ABSENCE of the doubled spelling (`\\u0085` / `\\x85` with the backslash doubled) and asserts the two cells DIFFER, and when the "one physical line" clause is enforced on the CELL rather than on the row count (the r90 fixture counts MISMATCH rows, so a raw newline inside the K4 detail passes 12/12). The injectivity evidence is a direct comparison of the two rendered cells (`_escape_text("\\u0085")` vs `_escape_text("\\udc85")`, or a brute-force sweep over the alphabet), not the count. Stated limits: the property claimed is the enumerated pair, not the whole cell (a stderr differing only inside the elided middle still renders identically, and a raw window cut INSIDE the two-byte encoding of U+0085 renders the surviving byte `\\x85`); `_escape_record` (path bytes) is unchanged and byte-based, so a path's U+0085 bytes already print `\\xc2\\x85`; the dead escape-first helper `_one_line` is measured by `grep -c 'def _one_line('` → 0 plus the module-load check, NOT by the fixture (a tool that keeps `_one_line` still scores `tool_pass=12`, S90Critic/A5(c)); and no universal injectivity over arbitrary byte/character pairs is claimed. | every lane tool that writes a record cell whose escaping rule can receive both an undecodable byte and the character that decodes to the same bytes; every escaping rule with a `\\xNN` arm; every population that claims to bind such a pair | `python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-90/controls/c2-before-tool.py --work <empty>` must print `SUMMARY cases=12 tool_pass=12 before_pass=10` and EXIT 0; the r89 bytes as BOTH arms read `tool_pass=10 before_pass=10` (KFF9 and KFF10 fail on both arms because their details are identical), EXIT 1 — and that pair is NOT by itself sufficient evidence of injectivity: the r90 fixture's doubled-backslash mutant passes it 12/12, so the pair's injectivity must additionally be shown by a direct comparison of the two rendered cells (`_escape_text("\\u0085")` = `\\u0085` vs `_escape_text("\\udc85")` = `\\x85`) | corpus/lessons/round-90.md; corpus/knowledge/nel-byte-character-pair.md; plans/round-90.md A1 and A4; S353, S348, S351 |
```

## Why this criterion is written this way (each clause against the lane's own rules)

| clause | grounded in |
|---|---|
| "Extends Q164 and Q163 (they stand)" | Q164 is the r89 criterion (raw-first bound + `surrogateescape` decode); Q163 is the r88 criterion (the cell is ONE escaped line). Neither is rewritten: a criterion is superseded by a new row that NAMES the row it replaces, never rewritten (`corpus/QUALITY.md:16-18`). Q165 names the two it extends and does not restate them. |
| "the byte and the character arrive by DIFFERENT paths" | the filed tool, `tools/souji-record-agreement.py` `_escape_text`: the surrogate arm `elif 0xDC80 <= o <= 0xDCFF: out.append("\\x%02x" % (o - 0xDC00))` and the character arm `elif o in (0x85, 0x2028, 0x2029): … out.append("\\u%04x" % o)`. Before the repair the character arm was `elif o < 0x20 or o == 0x7F or o == 0x85:` (`census/round-90/controls/c2-before-tool.py`), which printed `\\x85` for BOTH. |
| "a bare substring count does not [certify injectivity]" | **the L1's landed A1** (S90Sentinel H1, `S90Sentinel/mut/mutant.py` sha256 `5ec2e925…74a6`): the fixture's KFF9 check is `count(bs+"u0085")==1 and count(bs+"x85")==0`, and the escaped literal `\\u0085` CONTAINS the substring `\\u0085`, so a one-token mutant that doubles the U+0085 branch's backslash passes the r90 fixture 12/12 EXIT 0, the r89 fixture 10/10 and the r87 12-row counter. The r89 KFF6/KFF7 pair HAD the missing conjunct (`count(bs*2+"xff")==0`); the r90 pair dropped it. |
| "asserts the ABSENCE of the doubled spelling … and asserts the two cells DIFFER" | A1's routed fix, verbatim: "the missing doubled-spelling conjuncts (`count(bs*2+"u0085")==0`, `count(bs*2+"x85")==0`) are routed to r91." The "cells DIFFER" conjunct is the fixture's existing pair check (`_nel_ok`), which A0.1 disclosed runs on BOTH arms. |
| "the 'one physical line' clause is enforced on the CELL rather than on the row count" | **A4's second instrument gap**: "a variant that appends a raw newline inside the K4 detail passes 12/12 because `len(rows)==1` counts MISMATCH rows and the fixture reads the row's fifth cell only." |
| "The injectivity evidence is a direct comparison of the two rendered cells" | **A1's own wording**: "The injectivity evidence is the independent brute-force probe, not the kill rule"; S90Sentinel probe6 brute-forces 14 single characters and every 2-character string over that alphabet and finds zero collisions, and `_escape_text("\u0085")` is `\u0085` while `_escape_text("\udc85")` is `\x85`. |
| "a raw window cut INSIDE the two-byte encoding of U+0085 renders the surviving byte `\x85`" | **A4's narrowed sentence**: "The character spelling holds when both bytes of U+0085 survive the raw window; a window cut inside the encoding renders the remaining byte as `\x85`, which no window can avoid. The fixture's KFF9/KFF10 payloads are short and do not exercise the boundary, so this clause is stated, not measured." |
| "the dead escape-first helper `_one_line` is measured by grep and load, NOT by the fixture" | **A5(c)**: "a tool that applies only the U+0085 spelling and keeps `_one_line` still scores `tool_pass=12 before_pass=10` EXIT 0. … the fixture measures the pair; the deletion is measured by grep and load, not by the fixture, and a fixture row for it is routed to r91." |
| "a rule that merely escapes the CHARACTER leaves the pair on one spelling and is a defect, not a boundary" | the r89 A2 narrowing carried into a criterion: the r89 lesson routed the collision to r90 rather than filing it as a limit (`corpus/lessons/round-89.md` "Routed to round 90"). |
| the test column names the frozen command AND BOTH arms AND says the pair is not sufficient | the lane's rule (Q161/Q164 style): a test is the command a reader re-runs, and the control arm is what the claim is measured AGAINST. The frozen C2 counter is `python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-90/controls/c2-before-tool.py --work <empty>`; this seat re-ran it on the committed bytes and read `SUMMARY cases=12 tool_pass=12 before_pass=10`, EXIT 0. The before-both-arms control reads `tool_pass=10 before_pass=10`, EXIT 1 (the prereg's DO-NOTHING CONTROL receipt `census/round-90/records/prefreeze-c2-control.txt`, re-run by this seat and matching it cell for cell). |
| the lesson column | `corpus/lessons/round-90.md` (the L1 has landed that file) — the r89 lesson's `## Mistakes` rows are M1-M3 and the r90 file's are M1-M3, and the QUALITY convention here is a FILE pointer (`corpus/lessons/round-88.md`, `corpus/lessons/round-89.md` in Q163/Q164), so a file pointer is the safe form. The knowledge entry and the plan amendments are cited alongside it because they carry the measurement. |

## What this seat did NOT check

- Whether the L1 wants Q165 to also carry a clause about the **stripper/offset convention** (the same S353 quote
  reads 71402 under the lane's committed r63 stripper, 82360 as a character offset under one drop-tags variant, and
  82357 as a byte offset under the scout's rule — the L1 has resolved this by quoting **no offset** in the S353
  anchor cell, which is the right call). That is a source-verifiability question, not a record-cell criterion, and
  this seat did not widen the criterion to cover it.
- Whether the L1 wants Q165 to restate the **r91-routed** items (the doubled-spelling conjuncts, the boundary row,
  the dead-code fixture row). The criterion names them as what a future population must add, which is the criterion's
  job; landing the ROWS is r91's.
- The `QUALITY.md` census/state of the landed file: this seat did not edit `corpus/QUALITY.md`, so any post-landing
  validation is the L1's.
