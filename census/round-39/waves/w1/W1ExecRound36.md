# W1ExecRound36 — R16 (`census/round-39/c1-items.tsv` row `R39-C1-16`) fact establishment (round 39, wave 1)

Seat: W1ExecRound36 (executor, lane `souji-shokunin`)
Assignment: establish the facts behind routed defect R16 — was `corpus/lessons/round-36.md:23`
rewritten in place, which commit wrote it, and what appended-correction shape satisfies r37 routed
defect 4 without editing frozen bytes.

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
Lane HEAD at measurement start and end: `2201778e7736af82e7d8a42dec2494f115bf3923` (read-only;
unchanged, working tree clean for this file).
Contract row (frozen, not edited):
`R39-C1-16<TAB>corpus/lessons/round-36.md<TAB>R39-C1-16<TAB>in-place,correction,line-23<TAB>-`
(`census/round-39/c1-items.tsv:22`).

No file in the lane was written except this report. No git/jj mutation was run anywhere. No scratch
tree remains: `/fast/scratch/hyaku/souji-r39/W1ExecRound36` was created, never used for a write, and
removed (`rmdir` + verified absent). No tool was installed or upgraded.

---

## 0. Summary of facts (each grounded in §1–§7)

| Question | Answer |
|---|---|
| Was line 23 rewritten in place? | **Yes.** One line deleted, one line added inside `@@ -20,7 +20,7 @@`: `cases=20 pass=20 fail=0` → `cases=21 pass=21 fail=0`. |
| Which commit wrote the current line 23? | **`d30476d`** (round-37 A1/A2, 2026-10-28 12:28:09 −0300, `souji-shokunin <souji@shokunin.local>`). `92a65fa` (round-36 rebuild, 11:33) wrote the superseded `cases=20` bytes at that line. |
| Did r37's own settlement block allow it? | **No.** `e987a27` (12:21) appended the r37 block with the sentence "The original sentence is left byte-verbatim; this row is the correction."; `d30476d` (12:28) deleted that sentence **and** rewrote line 23. Two-part rewrite, seven minutes later. |
| Did r38 touch the file? | **No.** `git diff --numstat ca4369a fcdecaa -- corpus/lessons/round-36.md` is empty (rc 0). Matches the r38 spot-check's own `harmed` row (`round-38-verifier-spotcheck.md:107`: "`corpus/lessons/round-36.md` byte-identical"). |
| Is R16 still owed today? | **Formally closed, materially partial.** `c0b007b` (round 39, 14:51) appended 4 lines at 174–176 carrying anchor `R39-C1-16`, so the frozen `has_token` predicate for this item reads CLOSED at HEAD (§6). The appended row misattributes the rewriter and omits the superseded bytes, the rewriting commit, the receipt and the deleted byte-verbatim sentence (§8). |

---

## 1. Line 23, located and numbered

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=15 && NR<=30 {printf "%4d\t%s\n", NR, $0}' corpus/lessons/round-36.md
  15	  94b5e96ab72b40622449af2dfe7c5b6d73118176` must read `dangling=0 mismatches=0` with
  16	  `kill_tested>0 kill_violations=0`; the resolution clause is carried by the strict probe in
  17	  `census/round-36/records/c1-strict-paths.txt`. Base control (`c1-control-base.txt`):
  18	  `grounded=19 mapped=18 dangling=0 mismatches=1`, rc 1 (the r35 entry
  19	  `corpus/knowledge/fleet-prune-numerator-r35.md` carried `ground: F1` and no map row named it).
  20	- **C2 operability (score 8).** The pre-report gate enforces the round-report contract in seven
  21	  predicates, proved by a fixture whose cases each isolate one predicate and whose controls are
  22	  rejected. Target (after A1–A3):
  23	  `python3 -B tests/fixtures/r36-report-gate.py` → `cases=21 pass=21 fail=0 control=STUB-REJECTED`,
  24	  rc 0; `bash tests/fixtures/r27-pre-report-gate.sh` → `cases=4 pass=4
  25	  control=FALSE-GREEN-REJECTED`, rc 0. Base control (`c2-control-base.txt`): no checker at base
  26	  (`git cat-file -e` rc 128) and the base gate scores `cases=11 pass=0 fail=11`.
  27	- **C3 coverage (score 8, capability acquisition).** F1's fleet worktree-registration numerator
  28	  becomes a re-runnable surface: `tools/souji-worktree-drift.py` re-measures every repository a
  29	  committed census record names, read-only, and reports the drift. Target (after A2+A4):
  30	  `python3 -B tests/fixtures/r36-worktree-drift.py` → `cases=12 pass=12 fail=0
```
(Also run first as the literal `sed -n '15,30p'` form, same 16 lines, no numbers.)

**Verdict V1: PASS** — line 23 is the C2 Claims target cell, `cases=21 pass=21 fail=0 control=STUB-REJECTED`, inside the `- **C2 operability (score 8).**` bullet. The file is 176 lines (`wc -l` → `176 corpus/lessons/round-36.md`).

---

## 2. History of the file

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%h %ad %s' --date=short -- corpus/lessons/round-36.md
c0b007b 2026-10-28 round-39: C1 — 14 routed-defect corrections, r39 lesson with Gate/Mistakes, three source rows, gate-registry rows
d30476d 2026-10-28 round-37 A1/A2: pin the register, receipt-bound citations, selftest-arm cells; drift hardlink/parent-swap nofollow walk, property env-witness, measured case
e987a27 2026-10-28 round-37: C2 drift-tool write envelope (whitelisted git env, root containment, O_NOFOLLOW json) + C3 exact-field discrimination fixture + C1 receipt corrections
5f0dd45 2026-10-28 round-36: A6 (live_regs consistency, phantom flag, fixture --work refusal) and lesson findings from wave 1
92a65fa 2026-10-28 round-36: rebuild corpus/lessons/round-36.md in full after a truncated write; record the class in ## Mistakes
007ab53 2026-10-28 round-36: report-contract gate + F1 drift detector (A1-A4), coverage-map repair, QUALITY Q80-Q82, registry corrections
```

**Verdict V2: PASS** — six commits touch the file; the last three are the ones that matter for R16
(`92a65fa` rebuild, `e987a27` append, `d30476d` rewrite), plus `c0b007b` for the r39 append.

---

## 3. The contract window `ca4369a..fcdecaa` (r37 spot-check → r38 landing)

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --numstat ca4369a fcdecaa -- corpus/lessons/round-36.md
(no output)
rc=0
```

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse ca4369a fcdecaa
ca4369a9296011644636711a624da6a8074e8e2a
fcdecaaf293f0fee3c39cc148ae91389e04ef63c
$ git log -1 --format='%h %ad %s' --date=iso ca4369a
ca4369a9296011644636711a624da6a8074e8e2a
2026-10-28 13:14:41 -0300
round-37 verifier spot-check (integrator, hyaku): non-author admit/reject
$ git log -1 --format='%h %ad %s' --date=iso fcdecaa
fcdecaaf293f0fee3c39cc148ae91389e04ef63c
2026-10-28 14:19:51 -0300
round-38: intermediate measurement records as historical evidence
```

Line 23 is identical at both endpoints:
```
$ git show ca4369a:corpus/lessons/round-36.md | sed -n '23p'
  `python3 -B tests/fixtures/r36-report-gate.py` → `cases=21 pass=21 fail=0 control=STUB-REJECTED`,
$ git show fcdecaa:corpus/lessons/round-36.md | sed -n '23p'
  `python3 -B tests/fixtures/r36-report-gate.py` → `cases=21 pass=21 fail=0 control=STUB-REJECTED`,
```

**Verdict V3: PASS** — the file is byte-identical across the r37-spot-check→r38-landing window. The
rewrite therefore **predates** the spot-check commit (it is not an r38 event), and r38 neither
repaired nor repeated it — exactly R16's premise ("`git diff` confirms the file untouched this
round, so the debt is open, not repeated", `round-38-verifier-spotcheck.md:211-213`).

---

## 4. Which commit wrote line 23

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin blame -L 20,26 --date=short -- corpus/lessons/round-36.md
92a65fa (souji-shokunin 2026-10-28 20) - **C2 operability (score 8).** The pre-report gate enforces the round-report contract in seven
92a65fa (souji-shokunin 2026-10-28 21)   predicates, proved by a fixture whose cases each isolate one predicate and whose controls are
92a65fa (souji-shokunin 2026-10-28 22)   rejected. Target (after A1–A3):
d30476d (souji-shokunin 2026-10-28 23)   `python3 -B tests/fixtures/r36-report-gate.py` → `cases=21 pass=21 fail=0 control=STUB-REJECTED`,
92a65fa (souji-shokunin 2026-10-28 24)   rc 0; `bash tests/fixtures/r27-pre-report-gate.sh` → `cases=4 pass=4
92a65fa (souji-shokunin 2026-10-28 25)   control=FALSE-GREEN-REJECTED`, rc 0. Base control (`c2-control-base.txt`): no checker at base
92a65fa (souji-shokunin 2026-10-28 26)   (`git cat-file -e` rc 128) and the base gate scores `cases=11 pass=0 fail=11`.
```
**Line 23 is the single line in that paragraph attributed to `d30476d`; every neighbour line is
`92a65fa`.** Blame alone is not the fact, so the bytes at each revision:

```
$ git show 92a65fa:corpus/lessons/round-36.md | sed -n '23p'
  `python3 -B tests/fixtures/r36-report-gate.py` → `cases=20 pass=20 fail=0 control=STUB-REJECTED`,
$ git show 0d974ff:corpus/lessons/round-36.md | sed -n '23p'
  `python3 -B tests/fixtures/r36-report-gate.py` → `cases=20 pass=20 fail=0 control=STUB-REJECTED`,
$ git show d30476d:corpus/lessons/round-36.md | sed -n '23p'
  `python3 -B tests/fixtures/r36-report-gate.py` → `cases=21 pass=21 fail=0 control=STUB-REJECTED`,
$ git show cb443f5:corpus/lessons/round-36.md | sed -n '23p'
  `python3 -B tests/fixtures/r36-report-gate.py` → `cases=21 pass=21 fail=0 control=STUB-REJECTED`,
$ git show HEAD:corpus/lessons/round-36.md | sed -n '23p'
  `python3 -B tests/fixtures/r36-report-gate.py` → `cases=21 pass=21 fail=0 control=STUB-REJECTED`,
```

```
$ git -C … diff 0d974ff cb443f5 -- corpus/lessons/round-36.md
@@ -20,7 +20,7 @@ before any after-data). Frozen contract: `census/round-36/preregistration.txt` (
 - **C2 operability (score 8).** The pre-report gate enforces the round-report contract in seven
   predicates, proved by a fixture whose cases each isolate one predicate and whose controls are
   rejected. Target (after A1–A3):
-  `python3 -B tests/fixtures/r36-report-gate.py` → `cases=20 pass=20 fail=0 control=STUB-REJECTED`,
+  `python3 -B tests/fixtures/r36-report-gate.py` → `cases=21 pass=21 fail=0 control=STUB-REJECTED`,
@@ -165,3 +165,8 @@ Changed in place, old → new:
+## Correction (r37, 2026-10-28)
+
+R37-C1-7 — … `SUMMARY cases=21 pass=21 fail=0 control=STUB-REJECTED` …
+The Claims line is corrected in place (the prereg's in-place branch for current lesson cells); this block records the settlement and names the receipt. …
$ git diff --numstat 0d974ff cb443f5 -- corpus/lessons/round-36.md
6	1	corpus/lessons/round-36.md
```

Pickaxe confirms direction (which commits changed the occurrence count of each value):
```
$ git log -S'cases=20 pass=20 fail=0' --format='%h %ad %s' --date=short -- corpus/lessons/round-36.md
d30476d 2026-10-28 round-37 A1/A2: pin the register, receipt-bound citations, selftest-arm cells; drift hardlink/parent-swap nofollow walk, property env-witness, measured case
92a65fa 2026-10-28 round-36: rebuild corpus/lessons/round-36.md in full after a truncated write; record the class in ## Mistakes
$ git log -S'cases=21 pass=21 fail=0' --format='%h %ad %s' --date=short -- corpus/lessons/round-36.md
d30476d 2026-10-28 round-37 A1/A2: pin the register, receipt-bound citations, selftest-arm cells; drift hardlink/parent-swap nofollow walk, property env-witness, measured case
e987a27 2026-10-28 round-37: C2 drift-tool write envelope (whitelisted git env, root containment, O_NOFOLLOW json) + C3 exact-field discrimination fixture + C1 receipt corrections
```
(`e987a27`'s `cases=21` hit is the appended settlement block text, not line 23 — see §5.)

**Verdict V4: PASS** — the current line 23 bytes were written by **`d30476d`** (2026-10-28
12:28:09 −0300), replacing `92a65fa`'s / `0d974ff`'s `cases=20 pass=20 fail=0` with
`cases=21 pass=21 fail=0`. The rewrite is one deleted + one added line; the other +5 lines in that
range are the appended r37 block.

---

## 5. The defect is two-part: `e987a27` appended correctly, `d30476d` then rewrote both

```
$ git -C … show e987a27 --format='%h %s' -- corpus/lessons/round-36.md
e987a27 round-37: C2 drift-tool write envelope (whitelisted git env, root containment, O_NOFOLLOW json) + C3 exact-field discrimination fixture + C1 receipt corrections

@@ -165,3 +165,8 @@ Changed in place, old → new:
+## Correction (r37, 2026-10-28)
+
+R37-C1-7 — the Claims section above quoted a count for the C2 fixture that no receipt ever carried. Settlement: `census/round-36/records/c2-after.txt` at `1e771ed` carries `SUMMARY cases=21 pass=21 fail=0 control=STUB-REJECTED` (amendment A7 refreshed it), and the base control line stays `cases=11 pass=0 fail=11`.
+The original sentence is left byte-verbatim; this row is the correction. The other never-true citations … are reconciled in `SCORECARD.md` …
```

```
$ git -C … show d30476d --format='%h %s' -- corpus/lessons/round-36.md
@@ -20,7 +20,7 @@
-  `… `cases=20 pass=20 fail=0 control=STUB-REJECTED`,
+  `… `cases=21 pass=21 fail=0 control=STUB-REJECTED`,
@@ -169,4 +169,4 @@
-The original sentence is left byte-verbatim; this row is the correction. …
+The Claims line is corrected in place (the prereg's in-place branch for current lesson cells); this block records the settlement and names the receipt. …
```

**Verdict V5: PASS** — r37 routed defect 4 is reproduced exactly: `e987a27` landed the append-only
remedy ("left byte-verbatim"), and `d30476d` seven minutes later (i) rewrote the claim line in place
and (ii) deleted the byte-verbatim sentence that made the append legitimate. The deletion is the
part the spot-check's "one deleted line" understates.

---

## 6. Current state at HEAD: the frozen predicate reads CLOSED

The landed r39 append (commit `c0b007b`, "round-39: C1 — 14 routed-defect corrections, …"):
```
$ git -C … show c0b007b --format='%h %s' -- corpus/lessons/round-36.md
@@ -170,3 +170,7 @@
+
+### R39 append-only correction (round 39, 2026-10-28)
+
+R39-C1-16 — correction owed since r37 routed defect 4: line-23 of this lesson was rewritten in-place by a later integration instead of being corrected by an appended block, which is the defect r37 routed and r38 left open. The superseded sentence stays in history; this appended correction records it, and from this round an in-place edit of a lesson is a routed defect rather than a documentation choice.
```

Predicate replay with the **frozen counter's own** `has_token` (no local re-implementation), over
`git show HEAD:corpus/lessons/round-36.md`:
```
$ python3 -B -c "…importlib census/round-39/c1-counter.py… has_token over the R39-C1-16 lines…"
hits= 1
must {'in-place': True, 'correction': True, 'line-23': True}
mustnot- False
```
And the tokens are on one physical line (line 176), each as a whole token:
```
$ for t in 'in-place' 'correction' 'line-23' 'R39-C1-16'; do printf "%s=" "$t"; grep -c -- "$t" <<<"$(sed -n '176p' corpus/lessons/round-36.md)"; done
in-place=1
correction=1
line-23=1
R39-C1-16=1
```
Additions only since base and freeze:
```
$ git -C … diff --numstat ca4369a HEAD -- corpus/lessons/round-36.md
4	0	corpus/lessons/round-36.md
$ git -C … diff --numstat ed30b7f HEAD -- corpus/lessons/round-36.md
4	0	corpus/lessons/round-36.md
$ git -C … diff --numstat b769bfb HEAD -- corpus/lessons/round-36.md
4	0	corpus/lessons/round-36.md
$ git -C … status --porcelain corpus/lessons/round-36.md
(no output — clean)
```
Grounding for the corrected value (never re-run; the receipt is the evidence):
```
$ git -C … show 1e771ed:census/round-36/records/c2-after.txt | grep -n "SUMMARY\|cases="
6:SUMMARY cases=21 pass=21 fail=0 control=STUB-REJECTED
10:cases=4 pass=4 control=FALSE-GREEN-REJECTED
14:SUMMARY cases=9 pass=9 fail=0
```
**Verdict V6: PASS (predicate) / FLAGGED (content).** `R39-C1-16` is CLOSED by the frozen predicate
at HEAD (anchor hit=1, all three `must` tokens whole-token true on that line, no `mustnot`; the byte
delta since `ca4369a`, `ed30b7f` and `b769bfb` is `4 0`, i.e. append-only). The line-23 value
`cases=21 pass=21 fail=0 control=STUB-REJECTED` equals `census/round-36/records/c2-after.txt:6` at
`1e771ed`, so the number itself is grounded.

---

## 7. Frozen bytes untouched by this seat

`b769bfb` (freeze) and `ed30b7f` (lane base) are both ancestors of HEAD; the file differs from each
by the same 4 added lines and 0 deletions (§6). No `census/round-39/preregistration.txt`,
`c1-items.tsv`, `*-items.tsv`, spec JSON or frozen receipt was read-write-opened by this seat; this
report is the only write.

---

## 8. The exact appended-correction shape that satisfies r37 routed defect 4

The obligation, quoted verbatim from the two sources:
- r37 spot-check defect 4 (`corpus/lessons/round-37-verifier-spotcheck.md:158-162`): "**In-place
  corpus rewrite.** `corpus/lessons/round-36.md:23` was rewritten in place (`cases=20` → `cases=21`
  …). CORPUS.md requires corrections as new entries, never rewrites. Keep the settlement block, but
  land the correction as an appended entry in r38 rather than a rewrite."
- r38 spot-check R16 (`corpus/lessons/round-38-verifier-spotcheck.md:211-213`): "No appended
  correction for the in-place rewrite of `corpus/lessons/round-36.md:23`; … Land the appended entry
  in r39."
- rule (`/home/vgpnk/Projects/shokunin/CORPUS.md:53`): "**Corrections are new entries, never
  rewrites.** …"

Shape (all conditions required; **additions only**, and line 23, lines 20–26 and 169–172 must stay
byte-identical):

1. **One appended section** at end of file (`##`/`###` heading, then a blank line) — nothing above
   it edited. Post-condition: `git diff --numstat <base> <landing> -- corpus/lessons/round-36.md`
   reads `<N>\t0` with `N>=1`, and `git diff <base> <landing> -- corpus/lessons/round-36.md`
   contains no `-` line except the `---` header.
2. **One anchor line** (a single physical line) that contains, as whole alphanumeric-bounded tokens,
   the anchor `R39-C1-16` **and** all three `must` tokens `in-place`, `correction`, `line-23`. This
   is the frozen predicate (`census/round-39/c1-counter.py:15-17`, `has_token` at 86-98; a line that
   splits the tokens across two physical lines reads OPEN).
3. **Named provenance on/after that line**, because the defect is a provenance loss, not a number
   loss:
   - superseded bytes and their delta: ``cases=20 pass=20 fail=0`` → ``cases=21 pass=21 fail=0`` at
     `corpus/lessons/round-36.md:23`;
   - the rewriting commit: `d30476d` (round-37 A1/A2, 2026-10-28 12:28:09 −0300,
     `souji-shokunin <souji@shokunin.local>`), verified by
     `git diff 0d974ff cb443f5 -- corpus/lessons/round-36.md` = one deleted + one added line;
   - the grounding receipt: `census/round-36/records/c2-after.txt:6` at `1e771ed`, `SUMMARY
     cases=21 pass=21 fail=0 control=STUB-REJECTED`, base control `cases=11 pass=0 fail=11`;
   - the **deleted** byte-verbatim sentence, quoted: "The original sentence is left byte-verbatim;
     this row is the correction." (`e987a27`), and the sentence that replaced it, «The Claims line is
     corrected in place (the prereg's in-place branch for current lesson cells)» (`d30476d`,
     still standing at `corpus/lessons/round-36.md:172`);
   - the rule restored: `CORPUS.md:53`.
4. **Supersession clause**: an explicit sentence that the r37 block's "corrected in place" sentence
   and line 23's in-place provenance are superseded by this row and left byte-verbatim from here on
   (append-only settlement — the shape `e987a27` used and `d30476d` destroyed).

Concrete candidate (verbatim; the anchor line deliberately carries all four tokens):

```markdown
### R39 correction — r37 routed defect 4 settled (round 39, 2026-10-28)

R39-C1-16 — in-place correction of line-23, recorded as an appended entry: `corpus/lessons/round-36.md:23` was rewritten in place by `d30476d` (round-37 A1/A2, 2026-10-28 12:28:09 −0300, author `souji-shokunin <souji@shokunin.local>`), which replaced `cases=20 pass=20 fail=0` with `cases=21 pass=21 fail=0` and, in the same commit, deleted the r37 settlement's sentence "The original sentence is left byte-verbatim; this row is the correction." (`e987a27`).
The corrected value is grounded, not reassigned: `census/round-36/records/c2-after.txt:6` at `1e771ed` reads `SUMMARY cases=21 pass=21 fail=0 control=STUB-REJECTED`, and the base control stays `cases=11 pass=0 fail=11`.
`CORPUS.md:53` ("Corrections are new entries, never rewrites") is the rule this row restores: line 23's provenance and the r37 block's sentence at line 172 are superseded here, left byte-verbatim, and are not to be edited again.
```

Checks that the shape must pass after landing (all three are already reproducible today except the
added provenance):
```
$ git diff --numstat <base> <landing> -- corpus/lessons/round-36.md        # → "<N>\t0"
$ git diff <base> <landing> -- corpus/lessons/round-36.md | grep -c '^-[^-]'   # → 0
$ python3 -B census/round-39/c1-counter.py --root <lane> --rev <landing> \
    --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv   # item leg: R39-C1-16 CLOSED
```

---

## 9. Residuals and risks this seat hands to the L1

1. **The landed r39 row misattributes the rewriter.** Line 176 says the rewrite was done "by a later
   integration". Measured: the rewriting commit is `d30476d`, authored
   `souji-shokunin <souji@shokunin.local>` inside the round-37 A1/A2 wave; the integrator commit in
   that range (`0d974ff`, `protocol-shokunin`, 11:49) still carries `cases=20` at line 23. The frozen
   `must` tokens do not test this, so the item closes while the sentence stays wrong — a
   fresh-instance of the round's own calibration class.
2. **The landed row omits all provenance** — superseded bytes, rewriting commit, receipt path:line,
   and the deleted byte-verbatim sentence. R16's remedy is an appended *correction*; a row that
   asserts "the superseded sentence stays in history" without naming it leaves the reader to
   re-derive §4 and §5 by hand.
3. **Standing contradiction inside the file.** Line 172 still reads "The Claims line is corrected in
   place (the prereg's in-place branch for current lesson cells)" — the sentence `d30476d`
   substituted for the byte-verbatim promise. Under `CORPUS.md:53` it is itself a superseded
   statement; the safe remedy is an appended clause naming it (shape item 4), never an edit of it.
4. **r37 asked for r38, r39 delivered.** The obligation was "land the correction as an appended entry
   in r38"; r38's numstat window is empty (§3), and the append landed in `c0b007b` (round 39,
   14:51). Content satisfied, round named by the routing missed by one — disclose, do not re-word.
5. **`census/round-39/cells.tsv` does not exist yet** (`ls census/round-39/` → `c1-counter.py
   c1-items.tsv c2-counter.py c3-counter.py make-cells.py preregistration.txt records`), so the full
   `SUMMARY items=16 open=0 register_cells>=6 …` line cannot be measured by this seat; the item leg
   was verified by predicate replay only (§6). That measurement belongs to the C1 seat, not here.

---

## 10. Instrument and hygiene record

- Tools installed/upgraded: **none**.
- Scratch: `/fast/scratch/hyaku/souji-r39/W1ExecRound36` created with `mkdir -p`, unused, removed
  with `rmdir`, verified absent (`SCRATCH-REMOVED`). Nothing written under `/tmp`.
- Git: read-only only (`log`, `show`, `diff`, `diff --numstat`, `blame`, `rev-parse`, `status`,
  `merge-base --is-ancestor`, and `-S` pickaxe). No `add/commit/stash/checkout/switch/reset/pull/
  push`, no `jj`. No `git -C "$D"` fixture was needed, so none was created.
- Python: `python3 -B` only (no bytecode written); `census/round-39/c1-counter.py` loaded read-only
  via `importlib` to reuse its frozen `has_token`.
- Files written: this report only.
