# S87Scribe — round 87 drafts for the L1 (Gate rows, knowledge section, QUALITY criterion)

Status: COMPLETE — four files delivered in the seat dir; nothing committed; no lane file edited.

Seat: S87Scribe (scribe). Lane `souji-shokunin`, round 87, wave 1. Drafts only: no committed file is edited, no
git/jj mutation, no fleet/sibling-lane file touched, no MANIFEST/.ufo/state/.scratch/watchdog write.

## Deliverables

| file | what it is |
|---|---|
| `.ufo/waves/round-87/w1/S87Scribe/gate-rows.md` | the `## Gate` rows for S346 and S347 (registry row cell by cell, tier/class/status/used-by, ≤25-word located quote with roff line), plus the contract checks and one wording fix for the L1 |
| `.ufo/waves/round-87/w1/S87Scribe/knowledge-machine-parsed-status-stream.md` | the draft knowledge section "a machine-parsed status stream carries raw names" (≤40 lines) with the `source:`/`verified-at:`/`recheck:` front-matter, plus an integration note on the entry that already exists in the tree |
| `.ufo/waves/round-87/w1/S87Scribe/quality-q-line.md` | the draft QUALITY criterion (5-cell row in the lane's style) with the numbering decision and its own independent verification |
| `.ufo/waves/round-87/w1/S87Scribe/quote-verification.txt` | the quote-verification receipt: capture line number, quote, grep of the capture, capture-vs-installed byte comparison, the instrument-hash re-measure, and the two findings |

## What was verified

- **Both quotes, byte for byte.** S346's quote is a byte-exact substring of `census/round-87/srcs/git-status.1`
  roff line 698 after the standard roff unescaping (`\-` -> `-`, `\&.` -> `.`); S347's quote is the ASCII fold of
  `census/round-87/srcs/git-grep.1` roff line 212 (the capture's raw bytes carry `don\(cqt` and `\&.`; the filed
  quote has U+0027, the rendered page has U+2019). Both captures are byte-identical to the DECOMPRESSED installed
  man pages (`gzip -dc … | cmp -` → identical), so the capture is the installed page. Word counts 15 and 11,
  inside the ≤25-word contract rule.
- **All eleven frozen instrument hashes re-measure equal** (population, items, mutants, counter, harness, battery,
  C2 counter, base tool, writer) plus the two source captures. No mismatch.
- **SOURCES contract census on the tree**: rows 270, malformed 0, tier A=257/B=10/C=3, status mined=226/queued=14/
  rejected=30, no duplicate ids, no enum or tier-inflation violations, no `mined` row naming a non-existent
  `used-by` path. The two new rows carry all 11 columns with in-vocabulary values (`kind=docs`, `tier=A`,
  `status=mined`, `recheck=90d` — a value 12 other rows already use).
- **C2 after arm re-derived** on the lane's bytes: `SUMMARY rows=12 mismatches=0 errors=0`, EXIT 0, KN1/KN2/KN3
  `named=yes`.
- **The QUALITY row's test cell measured independently** against the COMMITTED tip bytes (`0ad9e3bf…`): the filed
  tool's K4 detail ends with `AttributeError: r87 KN1 stub: no truth helper`; the lane-base tool's ends with
  `Traceback (most recent call last):` — the front truncation the row forbids.

## Findings

**F1 (low, quote fidelity) — the S347 anchor quote is not byte-identical to the capture under any reading.**
The capture's raw bytes are `Use fixed strings for patterns (don\(cqt interpret pattern as a regex)\&.`; the
rendered page reads `don’t` (U+2019); the filed anchor reads `don't` (U+0027). The filed quote is an ASCII fold of
the rendered line, and the anchor cell does not say so — unlike the lane's own S345, which records "the sentence
wraps; justified spacing normalised". Recommended fix in `gate-rows.md`. Nothing in C1/C2 turns on it: the quote
grounds `teaches`, which is true of the page either way.

**F2 (HIGH, the lane's committed tool bytes) — the `-z` status arm mis-parses a rename's second NUL field.**
The C2 stated wording (preregistration.txt:78-79, and the frozen limit at :111-112) says "the `-z` form's second NUL
field of a rename is skipped". The committed tip (6e502c5c, tool blob `4244ac26…`, sha256 `0ad9e3bf…`) skips it by
a CONTENT test at its line 476 (`if len(rec) < 4 or rec[2:3] != " ": continue`). For a rename's second field the
third byte is just the third byte of the OLD path, so an old path with a space at byte 2 passes the test and is
mis-read as a status record. Reproducer (hermetic, no lane byte touched, `git -C "$D" rev-parse --show-toplevel`
asserted before the first commit):

    $ git -C "$D" mv "my file.txt" "new.txt"
    $ git -C "$D" status --porcelain -z | od -c
    0000000   R           n   e   w   .   t   x   t  \0   m   y       f   i
    0000020   l   e   .   t   x   t  \0
    $ python3 -B <committed tool bytes> --root "$D" --rev <HEAD> | grep '^MISMATCH\tK4'
    MISMATCH	K4	new.txt	uncommitted-path	R
    MISMATCH	K4	file.txt	uncommitted-path	my

The second row is SPURIOUS: `file.txt` does not exist, and the detail `my` is the old path's first two bytes read as
a status pair. Control: an old path with no space at byte 2 (`oldname.txt`) yields ONE row, so the defect is
specific, not to renames in general. On the same fixture the lane-base bytes emit ONE row with git's quoted
spelling (`"my file.txt" -> new.txt`) — so the committed tip trades one wrong spelling for a different wrong
spelling PLUS a spurious row. S87ExecC2 measured the same class independently (their F3) and the lane's
worktree already carries their repair (skip by the `R`/`C` STATUS LETTERS, which this seat confirmed emits the
single correct row). This seat reproduced it on the COMMITTED bytes before reading their report. The L1 must
re-file the C2 after receipt against whatever tool bytes it commits, and the Gate sentence must name the skip's RULE
(status letter), not a content test.

**F3 (MEDIUM, a knowledge entry in the tree teaches the defective rule).**
`corpus/knowledge/machine-parsed-path-spelling.md` (untracked, 06:45) advises: "Guard on the status pair
(`rec[2:3] == " "`, two status characters before it) and skip the field that fails the guard". That is exactly the
content heuristic F2 measures as defective. The receipt writer does it structurally
(`tools/souji-receipt-write.py:244-259`, skip the next field when the status letter is `R`/`C`), and this seat
confirmed the writer's `_porcelain_paths` returns `{b'my file.txt', b'new.txt'}` on the F2 fixture — no phantom. The
drafted knowledge section replaces the advice with the status-letter rule; the L1 must take that edit, or the entry
teaches a rule the lane's own committed bytes violate.

**F4 (low, one knowledge entry of 55 has no front-matter).** `machine-parsed-path-spelling.md` is the ONLY file in
`corpus/knowledge/` without `source:`/`verified-at:`/`recheck:` lines, and `corpus/QUALITY.md` Q1 (`applies-to:
knowledge`) tests exactly that ("the entry's `verified-at:` names a version; its `recheck:` runs on the host
version"). The drafted section carries the three lines.

**F5 (low, a Q-row shape).** The lane's QUALITY table is 5 cells (`id | criterion | applies-to | test | lesson`) and
its rules say every criterion cites the lesson that produced it. The uncommitted Q161 and Q162 (`corpus/QUALITY.md`
:397-398) have 4 cells each — the `lesson` pointer is missing. The draft in `quality-q-line.md` supplies it
(`corpus/lessons/round-87.md` C2; `.ufo/waves/round-86/w1/S86ExecK4.md` §"Diagnostic defect (routed, low)" and its
routed pointer). Because Q161 is UNCOMMITTED, amending it in place is not an append-only violation; the L1 should
amend rather than add a second, near-duplicate row.

**F6 (info, an integration overlap the L1 must resolve).** The lane's working tree already carries
`corpus/knowledge/machine-parsed-path-spelling.md` (57 lines), whose `## Gate` section repeats the S346/S347 rows and
whose scope covers the `-z` ground this seat was asked to draft. Both SOURCES rows' `used-by` cells name that file.
Filing this seat's section as a SECOND file with the same ground would create a duplicate scope; the cheapest
integration is one file (replace its first section with the drafted one, keeping its `-F` half and its Gate, or add
the front-matter to it). The drafted section is deliberately scoped to the STATUS STREAM only, so the `-F`/declaration
half stays where it is.

**F7 (info, the lane's tool bytes moved under the counter).** The C2 after receipt in
`census/round-87/records/` and the lesson's C2 paragraph named tool sha256 `0ad9e3bf…` (the committed tip). The lane
WORKTREE's tool now reads `c2b0784e…` (S87ExecC2's repair, applied during the wave). This seat's own counter re-run
read the worktree bytes; the L1 must re-file the after receipt against the bytes it commits. The counter's 12-row
instrument reads green on both byte sets' KN rows. **CLOSED by the L1:** the tip moved to `b0a64c94` ("round-87:
reviewer corrections … receipts re-filed on the final tool bytes"), the tool blob is `821e3703…`, and the re-filed
`census/round-87/records/c2-after.txt` names that same digest — which IS at a commit. Re-derived green by this seat
on the final bytes (12 rows, mismatches=0, EXIT=0).

## Disposition of F1-F7 (L1, 2026-11-08)

The L1 dispositioned all six findings this seat raised before the wave's repairs landed: F2/F7 repaired and
committed (`89d36922`, `b0a64c94`), F3 taken in substance into the knowledge entry (the skip is now decided by the
status letters, with `my file.txt` named as the measured counterexample), F4 front-matter added, F5 Q161/Q162
amended to the 5-cell shape with lesson pointers, F1 the S347 anchor cell now says the quote is the ASCII fold, and
F6 resolved by keeping one knowledge file. The L1 cites this seat's quote-verification receipt in the round's Gate.

**What that repair introduced is F8-F10 below — measured on the L1's FINAL committed bytes, after its repair.**

**F8 (HIGH, the L1's committed bytes) — the FORGED-detail branch's escape is NOT injective: one concealment row can
name two different paths with one spelling.** The landing repair made the STATUS arm's escape injective
(`_escape_record()` at `tools/souji-record-agreement.py:142-162`: the backslash is doubled FIRST and every byte
outside printable ASCII becomes `\xNN`). Measured on the committed bytes (`821e3703…`), the STATUS arm is correct:

    MISMATCH	K4	x\ny.txt	uncommitted-path	??
    MISMATCH	K4	x\\ny.txt	uncommitted-path	??

But the FORGED-detail branch — the `stat-cache-concealed` row, i.e. the arm that carries the concealment class the
C2 claim is about (KF1/KF2/KF3) — still uses the OLD escape at `tools/souji-record-agreement.py:305`
(`.replace("\n","\\n").replace("\t","\\t").replace("\r","\\r")`), which does NOT double the backslash. Measured with
the two names TRACKED and forged under the index stat cache (the counter's own `forge_index_stat` helper, used
read-only):

    MISMATCH	K4	.	stat-cache-concealed	RECEIPT-WORKTREE-STAT-CONCEALED: 2 tracked path(s) … (x\ny.txt, x\ny.txt) …

Two DIFFERENT paths, one spelling: the row names a file that does not exist and cannot tell the two concealed
paths apart. The writer's own detail is unambiguous before the tool's escape (`(x\ny.txt, x\\ny.txt)`), so the
collision is introduced by line 305, not by the writer. This is the class A3 says it closed ("the record escape
doubles the backslash first … so the record is injective"); the repair reached the STATUS arm and not this one.

**F9 (MEDIUM, the L1's committed bytes) — the same arm escapes no other control byte, so a raw VT splits the record.**
Line 305 covers only `\n`, `\t`, `\r`; a VT (0x0b) in a TRACKED path's name lands RAW in the detail (measured: the
record bytes carry `t \v n a m e . t x t`). 0x0b is a `str.splitlines()` separator, so a line-oriented consumer reads
that row as two lines — the class Q159 names. The STATUS arm does not have it (the same name reads `vt\x0bname.txt`),
so the two arms of one row set still spell one path two ways, which is what A3's "one path has one spelling in both
arms" names as closed.

**F10 (info, wording) — the prereg's frozen stated limit no longer describes the filed tool.** The prereg says
(frozen, `census/round-87/preregistration.txt:112`) "only newline, tab and CR are C-escaped, so another control byte
still lands raw in the record". That was true of `6e502c5c` and of `578cbf2c`; it is now true of NEITHER arm of the
committed bytes (the STATUS arm escapes every non-printable byte as `\xNN`; the FORGED arm escapes none). The prereg
cannot be edited, so the narrowed limit belongs in the plan's amendments and the lesson — the L1's call as planner.

**Why neither frozen instrument caught F8/F9.** `census/round-87/c2-byte-arm.py` KB5 exercises the STATUS arm only
(it creates two UNTRACKED names); no row of either instrument carries a control byte in a TRACKED name reaching the
FORGED-detail branch. Both instruments re-derive green on the committed bytes — the 12-row counter reads
`rows=12 mismatches=0 errors=0` EXIT 0 and the byte-arm probe `rows=7 mismatches=0` EXIT 0 (re-run by this seat).

## Gates this seat did not touch

C1's counting arms and the C2 before arm were NOT re-derived by this seat beyond the one C2 after-arm cross-check
recorded above — the C1 arms belong to the executor and mutation-tester seats; this seat's drafts neither widen nor
narrow either claim's wording. No preregistration sentence was edited. No amendment is proposed: the two wording
issues this seat measured (F2's parenthetical, F1's quote fidelity) are the L1's to reconcile in
`plans/round-87.md`, and F2's repair is already in the lane worktree.

## Tooling

(none installed — no pacman, no uv/npx/binary fetch, no sysctl, no sudo; the tooling directive's channel order was
not needed for this seat's read-only work.)

## Scratch and hygiene

Scratch roots `/fast/scratch/hyaku/souji-r87/S87Scribe/` and `/fast/scratch/hyaku/souji-r87/S87Scribe2/` (fixture
clones, probe kits, the tip-tool byte copies, the counter work dirs) are deleted before this yield; every receipt a
claim rests on is copied into the seat dir first (`quote-verification.txt` holds the byte comparisons, the row
lists and the greps). Nothing was left behind.

Every fixture repo was created with `git -C "$D" init -q`; every later git call names `-C "$D"` explicitly;
`git -C "$D" rev-parse --show-toplevel` was asserted equal to `$D` before the first commit; the identity was set
through `GIT_AUTHOR_*`/`GIT_COMMITTER_*` (or `-c user.name/-c user.email`) inside the fixture only; no `git commit`
ran outside a fixture. No `git fetch`/`push` ran anywhere; no lane git/jj state was mutated; no process this seat did
not start was signalled; the L1 was messaged by id (SoujiR87) and agent://all was never used.

## Checks the main agent / L1 should run

1. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat` — confirm this seat changed nothing outside
   `.ufo/waves/round-87/w1/S87Scribe/`.
2. **F8/F9 — the open item.** The FORGED-detail branch at `tools/souji-record-agreement.py:305` still uses the
   pre-repair escape (no backslash doubling, no `\xNN` for other control bytes), while the STATUS arm uses the new
   injective `_escape_record()` at `:142`. Measured on the committed bytes `821e3703…`: a tracked `x<LF>y.txt` and a
   tracked `x\<n>y.txt`, both forged under the index stat cache, produce ONE concealment row whose detail reads
   `(x\ny.txt, x\ny.txt)` — two different paths, one spelling — and a tracked `vt<VT>name.txt` lands a raw 0x0b in
   the detail. Neither frozen instrument covers it (KB5 is UNTRACKED-only). The repair is one call: route line 305
   through `_escape_record()` as well, or have the writer emit byte-escaped names.
3. **F10 — the wording.** The prereg's frozen limit sentence (`:112`, "only newline, tab and CR are C-escaped, so
   another control byte still lands raw in the record") no longer describes the filed tool; the narrowed limit
   belongs in `plans/round-87.md` and the lesson (the prereg itself may not be edited).
4. Take the `machine-parsed-path-spelling.md` edit from `knowledge-machine-parsed-status-stream.md` (F3, F4) rather
   than filing a second entry (F6) — **DONE by the L1**; amend Q161's missing `lesson` cell (F5) — **DONE**.
