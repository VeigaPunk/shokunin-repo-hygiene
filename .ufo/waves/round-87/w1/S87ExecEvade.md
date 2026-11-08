# S87ExecEvade — false-green hunt: both frozen counters (round 87, wave 1, seat)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin (base 5e288bb3152328f371325d0bf4fee7309d629991).
Report path: .ufo/waves/round-87/w1/S87ExecEvade.md. Receipts and edited instrument bytes:
.ufo/waves/round-87/w1/S87ExecEvade/.

Question this seat answers: can a counter/tool that LOST a clause or property still score the frozen instrument's
green? Every measurement uses the frozen instrument bytes; the nine preregistration hashes were re-measured before
use and all match:

  c1-false-rows.tsv b066fa0f… (51)   c1-items.tsv ce80195d…   c1-mutants.json 9368b342…
  c1-pointer-counter.py fd0a8e24…    c1-false-row-harness.py d6f4e612…   c1-clause-battery.py b0c1472b…
  c2-k4-counter.py 4e2b7c06…         controls/c2-before-base-tool.py cf875367…
  controls/souji-receipt-write.py 70bbf1c2…

Baselines re-measured with the exact claim commands (fresh --work dirs):

  C1 after   ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0 ;
             ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0 ;
             SUMMARY mutants=10 sets=r86,r87 killed_r86=8 killed_r87=10 killed_total=18 ; EXIT 0.
             (m12 and m16 both killed=no on r86; receipt c1-baseline.txt)
  C2 after   SUMMARY rows=12 mismatches=0 errors=0, EXIT=0 (c2-filed.txt; filed tool sha256 0ad9e3bf…).
  C2 before  SUMMARY rows=12 mismatches=3 errors=0, EXIT=1; KN1/KN2/KN3 named=no, the other nine rows match
             (c2-before.txt) — the control reproduces exactly.

Method: every C1 edit keeps all ten frozen mutant `old` texts present exactly once (the battery REFUSES otherwise,
EXIT 2; checked statically before every run), and is scored with
`python3 -B census/round-87/c1-clause-battery.py --counter <edit> --work <fresh> --only r86,r87 --expect-killed 18`.
Every C2 edit is scored with
`python3 -B census/round-87/c2-k4-counter.py --tool <edit> --work <fresh>` where the edited tool sits beside a copy
of the filed writer (the counter resolves and copies it). Edited bytes are retained as c1v-*.py / c2v-*.py.

## 1. C1 — the clause battery

| # | counter edit (sha256) | clause dropped | exit | pristine arms | kills | property actually present? | false-green verdict |
|---|---|---|---|---|---|---|---|
| 1 | c1v-before-half.py (dd56f846) | `_whole` before-byte half: `before_ok = True` | 0 | r86 49/0/0, r87 51/0/0 | 8 + 10 = 18 | NO | **GREEN-WITH-ABSENCE** (disclosed unrowed: the prereg already carries this half) |
| 2 | c1v-len-half.py (839e9607) | `len(want) <= len(have)` removed from the live `_capture_ok` return (old text retained dead) | 0 | r86 49/0/0, r87 51/0/0 | 8 + 10 = 18 | NO | **GREEN-WITH-ABSENCE** (disclosed unrowed; additionally the clause is semantically redundant — see F3) |
| 3 | c1v-never-error.py (5a77d9a2) | the R0 diagnostic: `return "ERROR"` → `return "UNRESOLVED"` (counter never returns ERROR) | 2 | r86 49/0/0, r87 51/1/0 (NE1 red) | 0 (INVALID) | NO | **RED** — NE1 binds the ERROR class; battery prints pristine_r87=red, score=invalid |
| 4 | c1v-special-case.py (163fe3cc) | both new rows short-circuited before the rules: I87E→ERROR, L06/lemma-stub→QUARANTINED | 1 | r86 49/0/0, r87 51/0/0 | 8 + 8 = 16 | NO (neither clause is consulted for its row) | **RED** — m12 and m16 both survive; 16 != 18, EXIT 1 |
| 5 | c1v-sum-game.py (63359282) | TQ1 short-circuited AND the counter aborts when its own source no longer contains the live token-on-line text | 0 | r86 49/0/0, r87 51/0/0 | 9 + 9 = 18 | NO for TQ1's binding (m16 alive on the 51-row population) | **GREEN per EXIT while a mutant survives** (see F1) |

Reading of row 5: m12's "kill" is `errors=49` / `errors=51` with `mismatches=0` — the self-source check makes every
invocation of the mutated counter exit nonzero, so the harness records errors, not a row mismatch; m16 is
killed=no on BOTH populations; SUMMARY prints killed_r86=9 killed_r87=9 killed_total=18 and the command exits 0
because `--expect-killed 18` only sums. The claim's stated numbers are killed_r86=8 / killed_r87=10.

What each passing edit would let through:
- Row 1: `_whole` accepts a needle whose occurrence is preceded by a path byte [code reading].
  `_whole(b"target/path", b"xtarget/path ")` goes False→True, so a QUARANTINED declaration naming `xtarget/path`
  satisfies the whole-path guard for `target/path`. No frozen row exercises it (the prereg says so; this measures it).
- Row 2: nothing observable — see F3; the clause is redundant, so no row ever could have bound it.
- Row 5: a counter that never runs the TQ1 row against `_whole`'s punctuation clause and that manufactures a kill
  by self-inspection can satisfy the frozen command's exit code. The knob is not the clause.

## 2. C2 — the K4 counter

| # | tool edit (sha256) | property dropped | exit | matching rows | property actually present? | false-green verdict |
|---|---|---|---|---|---|---|
| 0 | filed tool (0ad9e3bf) | — | 0 | 12/12 (mismatches=0) | yes (a) (b) (c) | baseline |
| 0b | controls/c2-before-base-tool.py (cf875367) | all three | 1 | 9/12; KN1/KN2/KN3 mismatch | no | **RED** (control reproduces) |
| 1 | c2v-const-digest.py (1c532239) | header digest is the constant 70bbf1c2… | 1 | 11/12; KN2 mismatch (writer_sha == appended_sha) | NO | **RED** — KN2 binds: the printed digest must equal the named file's content sha and change when a byte is appended |
| 2 | c2v-hardcoded-attr.py (3a4847e1) | no-verdict detail hard-coded to `AttributeError: writer failure not captured` | 0 | 12/12 (mismatches=0) | NO — the writer's stderr is never carried | **GREEN-WITH-ABSENCE (HIGH per assignment)** — see F4 |
| 3 | c2v-drop-newline.py (c60c61cb) | the status arm drops every record whose raw path carries a newline | 1 | 11/12; KN3 has no row (k4=0) | NO | **RED** — KN3 requires the row to exist |
| 4 | c2v-quote-strip.py (44c501b8) | `--porcelain -z` reverted to `git status --porcelain`; only the two quote characters are stripped | 0 | 12/12 (mismatches=0) | NO for (a): the read is the r86 line form, not -z | **GREEN-WITH-ABSENCE (HIGH per assignment)** — see F5 |
| 5 | c2v-quote-strip-hardcoded.py (9598dae7) | (a) reverted to the quoted line form AND (c) hard-coded | 0 | 12/12 (mismatches=0) | NO for (a) and (c); (b) present | **GREEN-WITH-ABSENCE (HIGH per assignment)** — both witnesses compose |

What each passing edit would let through:
- Row 2 (hard-coded detail): every writer failure that is not an `AttributeError` is misreported as one. Measured
  reproducer with a ValueError stub: the filed tool's K4 detail is
  `… no verdict (exit 1: ValueError: S87ExecEvade repro: the real writer failure is ValueError); tracked bytes are
  unverified`, while the green variant's detail is `…(exit 1: AttributeError: writer failure not captured)…` even
  though the stub's stderr last line is ValueError. The "LAST non-empty stderr line, not the first 200 characters"
  property is never exercised by KN1; KN1 checks only that the substring `AttributeError` appears somewhere in the
  detail.
- Row 4 (line form + quote stripping): KN3's exact cell is ambiguous. For a newline path, the `-z` record is the raw
  path C-escaped (`bad\nname2.txt`), and git's quoted spelling with the quote characters stripped is the SAME
  bytes (`\n` is already the two-byte escape). So the row cannot distinguish "parsed raw" from "quoted spelling
  read". For paths whose C-quoted spelling differs from the C-escape of the raw path the record is wrong and the
  counter still green. Measured on a fixture with literal-backslash and literal-quote names:
  filed `-z` records `back\slash.txt` and `quo"te.txt`; the green line-form variant records `back\\slash.txt` and
  `quo\"te.txt` (nonexistent paths). The claim's (a) mechanism (`--porcelain -z`) is absent in this green tool.
  Receipt c2-property-absence.txt.
- Row 5: a single green tool that lacks both (a)'s mechanism and (c) while KN2 proves only that (b) names and
  tracks the writer's bytes.

## 3. Findings

F1 (C1, MEDIUM — instrument exit). `--expect-killed 18` checks only the SUM of kills. Measured witness: EXIT 0 with
killed_r86=9 / killed_r87=9 while m16 survives BOTH populations (51-row included) and m12's "kill" is an error
(49/51 errors), manufactured by the counter inspecting its own source. The frozen kill rule says a mutant not
killed on the 51-row population makes the battery EXIT 1; the battery's code returns 0 whenever the total equals 18,
so it does not implement that rule for a self-inspecting subject. The battery also writes each mutant counter to
`<work>/mut/<mutant-id>.py`, so a subject can read the mutant id from its own path and branch (code reading of
census/round-87/c1-clause-battery.py, not separately exercised). Mitigation: the L1 should parse SUMMARY and enforce
killed_r86=8 AND killed_r87=10, not EXIT alone; or pin the subject counter's sha in the battery.
F2 (C1, LOW — already stated). The `_whole` before-byte half can be dropped with the battery fully green (8/10/18,
EXIT 0). This is exactly the unrowed clause the preregistration carries; the measurement confirms the blind spot and
adds nothing new to the stated wording.
F3 (C1, MEDIUM — correction to the carried debt). The `len(want) <= len(have)` half of `_capture_ok` is not merely
unrowed: it is semantically redundant. When len(want) > len(have), Python clamps `have[-len(want):]` to the whole
`have`, so `have[-len(want):] == want` is already False by length; when len(want) <= len(have) the conjunct is a
no-op. Exhaustive check over {a,b} lists of lengths 0..4: 0 differing (want, have) cases. Dropping it from the live
return leaves the battery identical (row 2 above). No future population row can ever bind it; the prereg's "stays
unrowed and is carried" should be retired as redundant rather than owed a row.
F4 (C2, HIGH per assignment — instrument coverage). A tool whose no-verdict detail hard-codes
`AttributeError: writer failure not captured` scores 12/12, EXIT 0, while property (c) is absent: the writer's last
non-empty stderr line is never carried. KN1 binds the substring, not the property. The prereg's stated limit ("KN1
proves the last stderr line survives, not that every failure shape is legible") does not disclose this: a failure
shape whose last line IS legible (ValueError) is still misnamed.
F5 (C2, HIGH per assignment — instrument coverage). A tool that keeps `git status --porcelain` (the r86 line form)
and merely strips the two surrounding quote characters scores 12/12, EXIT 0. KN3 binds the exact record cell, and for
a newline path the quoted spelling minus quotes is byte-identical to the C-escaped raw path, so the row cannot see
the difference. The consequence is not hypothetical: backslash and quote paths are recorded as their C-quoted
spelling (`back\\slash.txt`, `quo\"te.txt`) while the `-z` tool records the raw names; the §2e defect class survives
under a green counter. The claim's (a) says the status read IS `--porcelain -z`; this green tool's read is not.
F6 (C2, HIGH composition). F4+F5 in one tool: 12/12, EXIT 0, with (a)'s mechanism and (c) both absent.

Wording check (Amendment 59). The C1 claim's numbers reproduce exactly on the filed counter bytes (row 0 of the
baseline; hashes re-measured), and the C2 claim's numbers reproduce exactly on the filed tool bytes. Nothing here
falsifies the sentences about the FILED bytes. What the wave's artifacts do falsify is the instruments' reach:
the C1 battery's encoded exit rule (F1) and the C2 counter's ability to certify (a)'s mechanism and (c) (F4-F6).
A verifier who treats EXIT 0 / rows=12 as the certificate would accept a rule that is gone. Recommended routing:
(a) keep the C1 claim, but have the verifier read the per-set SUMMARY and add F3 to the carried list as redundant;
(b) keep the C2 claim about the filed bytes, but do NOT present the 12 rows as certifying (a)'s mechanism or (c)
without the code/word reading that the counter cannot supply.

## 4. Evidence

Seat directory .ufo/waves/round-87/w1/S87ExecEvade/:
  c1-baseline.txt, c1-before-half.txt, c1-len-half.txt, c1-never-error.txt, c1-special-case.txt,
  c1-sum-game.txt — full battery outputs (header pins, ARM lines, MUTANT lines, SUMMARY, RC).
  c2-filed.txt, c2-before.txt, c2-const-digest.txt, c2-hardcoded-attr.txt, c2-drop-newline.txt,
  c2-quote-strip.txt, c2-quote-strip-hardcoded.txt — full counter outputs (ROW lines, SUMMARY, EXIT).
  c2-property-absence.txt — ValueError-vs-AttributeError reproducer and the -z vs line-form record comparison
  (fixture: literal-backslash, literal-quote and newline names; git toplevel asserted; fixed identity).
  c1v-before-half.py, c1v-len-half.py, c1v-never-error.py, c1v-special-case.py, c1v-sum-game.py — edited counters.
  c2v-const-digest.py, c2v-hardcoded-attr.py, c2v-drop-newline.py, c2v-quote-strip.py,
  c2v-quote-strip-hardcoded.py — edited tools (each ran with a copy of the filed writer beside it; the writer bytes
  are unchanged, sha 70bbf1c2…).

Scratch: all clones, fixtures, mutant work dirs and edited-byte work copies lived under
/fast/scratch/hyaku/souji-r87/S87ExecEvade and were deleted before yield; receipts were copied into the seat
directory first. No scratch left behind. No lane file outside this seat's write scope was modified; no git/jj state
was mutated; no tool installs were needed.
