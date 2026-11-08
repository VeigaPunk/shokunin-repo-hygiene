# S87Reviewer — independent review, souji round 87 (C1 calibration 7, C2 operability 8)

Seat: S87Reviewer (leaf; no subagent dispatch, no commit, no push, no lane mutation). Everything below is
re-derived from `git clone --shared` clones at the named revisions and from commands this seat ran; the L1's
receipts are compared against those runs, never used as the only source. Scratch:
`/fast/scratch/hyaku/souji-r87/S87Reviewer` (removed at yield; outputs copied into this seat directory).

## Anchors (the lane moved during the review)

| role | commit | committer (-0300) | content |
|---|---|---|---|
| lane base | `5e288bb3152328f371325d0bf4fee7309d629991` | 06:25:43 | r86 closed (spot-check) |
| P | `77ccef7c5de2ad015f28da70fd58e1156c0f5b73` | 06:47:24 | census/round-87 instruments, controls, both before receipts, `records/c1-c8-measured.txt` |
| F | `6ed2d368dc416f6409ac181e0ea45e23da82f89e` | 06:47:35 | `census/round-87/preregistration.txt` ALONE (diff P..F = that file only) |
| R1 (first C2 repair) | `6e502c5c05fd3ca4193883921ef0c9b79a7d36a7` | 06:47:45 | `tools/souji-record-agreement.py` (+40/−8) |
| R2 (wave repair 1) | `578cbf2c9e5f88aa3e264fdee718b89062e3c034` | 07:00:16 | tool bytes/rename/CR repair; 3-row byte arm; `records/c2-after.txt` |
| R3 (wave repair 2) | `89d369227ae8d89f9f014ff72cc1eb61ed606706` | 07:03:02 | injective `\xNN` record escape, bytes delegated read, both-ends stderr; 5-row arm; receipts refiled |
| R4 (final tool; reviewer corrections) | `b0a64c943e22acc70da46ec8c9e688e842a42be4` | 07:07:30 | no-verdict detail prefers stderr (F4), rename comment names the original (F6), c8 mutant filed (F8); receipts refiled |
| R5 (evidence layer; tool unchanged `821e3703…`) | `1556010bcd91bb803f4859135047329572948392` | after R4 | byte arm grows KB6/KB7 (quote / ValueError binders); A8 names the 12-row counter's reach; c8 record re-filed |

Ancestry is linear: base → P → F → R1 → R2 → R3 → R4 → R5. C1 instruments are byte-identical at F and R5, so the F
anchor is also the final anchor for every C1 number. The tool bytes are unchanged from R4 to R5. C2 numbers are re-derived at R4 and the R5 receipts re-file the same
tool `821e3703…` (`tools/souji-record-agreement.py` sha256
`821e37033bf244916f047431387eb65a165442ef1d92c5219a19214d48fb3023`). The lane tip was re-checked at the end of the
review at R5 `1556010b…`; `records/c2-after.txt` and the byte-arm receipts are committed, `records/c1-after.txt` is
still untracked (`git cat-file -e HEAD:…` rc 1).

## Verdicts

**C1 — AGREE.** On the frozen instruments (`c1-false-rows.tsv`, `c1-items.tsv`, `c1-mutants.json`,
`c1-pointer-counter.py`, `c1-false-row-harness.py`, `c1-clause-battery.py`, all byte-identical at F and R5), my own
runs reproduce every number in the stated sentence: pristine `pop=r86 rows=49 mismatches=0 errors=0 exit=0`, pristine
`pop=r87 rows=51 mismatches=0 errors=0 exit=0`, all ten mutants killed on the 51 rows, `killed_r86=8 killed_r87=10
killed_total=18`, EXIT 0; and the do-nothing arm `--only r86 --expect-killed 8` gives `killed_r86=8`, with
`m12-token-on-line` and `m16-nf6b-punct` the only two `killed=no`, EXIT 0. The eight r86 mutants are byte-identical
and in order; the two new rows/mutants are exactly TQ1↔m16 and NE1↔m12; the r87 population is the r86 49 data rows
byte-for-byte in order plus those two; `c1-ledger.tsv` is the r86 ledger byte-for-byte
(`7cbb28c9…`). A4's narrowing (the two rows bind one *spelling* of each clause; the mutation-tester's p2/p3
spellings survive and are carried unrowed) is honest and is the reason this verdict is "agree with A4", not "agree
with the unqualified clause-level sentence"; see F1 and A4.

**C2 — AGREE.** At the final filed tool (R4, `821e3703…`) the frozen 12-row counter gives `SUMMARY rows=12
mismatches=0 errors=0`, EXIT 0, with KN1 named (detail contains `AttributeError`), KN2 bound (printed writer digest
equals the live writer and changes when one comment byte is appended), KN3 exact (`bad\nname2.txt` /
`uncommitted-path` / `??`), and KH1/KH2 clean. The control arm (counter `4e2b7c06…` on
`controls/c2-before-base-tool.py` `cf875367…`, byte-identical to the r86 filed tool, with the byte-identical writer
`70bbf1c2…` beside it) gives `mismatches=3` on exactly KN1/KN2/KN3 and `mismatches=0` on the nine r85/r86 rows, EXIT 1
— reproduced independently and matching the committed `controls/c2-before.txt`. The verdict is "agree" with two
open wording caveats (F2/F3): the final tool is four repairs beyond the frozen instrument bytes, the frozen limit
"only newline, tab and CR are C-escaped" is superseded by the wave's own `\xNN` escape, and for lines longer than 200
characters the detail is a 200-character both-ends compaction of the last line, not the whole line. Both are
disclosed in the L1's plan (A1–A5); neither changes a counted number. The code/ledger corrections this review
raised were landed while the review ran: F4/F6/F8 at R4, F5/F7 in the plan. R5 (tool unchanged) adds A8: the
12-row counter cannot certify the *mechanism* — a tool with a hard-coded `AttributeError` detail, or a line-form tool
that strips only git's quotes, scores 12/12 — and the byte arm's KB1/KB6/KB7 bind those mechanism layers. The frozen
C2 sentences concern the filed bytes and hold; my independent run of the committed seven-row arm (sha
`6495b048…`) on the final tool gives `rows=7 mismatches=0`, EXIT 0.

## Instrument binding (prereg vs committed bytes)

Hashes recomputed from `git cat-file -p <rev>:<path>`; F, R2, R3 and R4 agree for every row.

| path | prereg sha256 | at F | at R4 | match |
|---|---|---|---|---|
| `census/round-87/c1-false-rows.tsv` (51 rows) | `b066fa0f…620` | `b066fa0f…620` | `b066fa0f…620` | yes |
| `census/round-87/c1-items.tsv` (5 items, base `705fa138`) | `ce80195d…2e9` | same | same | yes |
| `census/round-87/c1-mutants.json` (10 members) | `9368b342…132` | same | same | yes |
| `census/round-87/c1-pointer-counter.py` | `fd0a8e24…20b` | same | same | yes |
| `census/round-87/c1-false-row-harness.py` | `d6f4e612…aef` | same | same | yes |
| `census/round-87/c1-clause-battery.py` | `b0c1472b…aeb` | same | same | yes |
| `census/round-87/c2-k4-counter.py` | `4e2b7c06…9e` | same | same | yes |
| `census/round-87/controls/c2-before-base-tool.py` | `cf875367…ddc` | same | same | yes |
| `census/round-87/controls/souji-receipt-write.py` | `70bbf1c2…efa` | same | same | yes |

Checked beyond the table:

* r86 population `census/round-86/c1-false-rows.tsv` = `79db70f6…561` (49 data rows) at F and R4; r86 mutants file
  has 8 members and the r87 first eight are object-identical (`json` compare). Each of the ten `old` strings occurs
  exactly once in the r87 counter (battery would EXIT 2 otherwise; also checked directly).
* `c1-items.tsv`: the r86 four item lines are unchanged; the only addition is `I87E LOG.md 3166
  census/round-84/records/c1-after.txt f:6d432b…`. `git show 705fa138:census/round-84/records/c1-after.txt` hashes
  to `6d432b47…54bc`; the token is on LOG.md **3165** of base `705fa138`, not 3166, so the item's only reachable
  verdict is the R0 diagnostic ERROR — verified.
* Counter diff r86→r87 = docstring + exactly one `ITEMS` pin (`ce80195d…`, base `705fa138`, 5 items) + the forgery
  expectation set `("REFUSED","MISMATCH")` → `("REFUSED","MISMATCH","ERROR")`. No resolution rule, class, message or
  branch line changed. Harness diff = docstring + one `POP_PINS` pin + one `POPS` entry + fixture R10 + rev label
  `R10` + the forge expectation cell (`ERROR` when the row expects it). Battery diff = docstring + one `PINS` entry +
  retargeting the r86 path to `census/round-86/` + the `--only` help string. `c1-ledger.tsv` diff vs r86 = empty.
* Pin failure is real: appending one row to a copy of the 51-row population makes the harness print
  `C1-HARNESS-FATAL: population sha256 a60e766e… is not a pinned population` and exit 2.
* Third candidate: my own suffix-dropping mutant of `_capture_ok`
  (`return bool(want) and len(want) <= len(have)`) scored on the r86 population gives `rows=49 mismatches=1`, the
  mismatching row `NF12c` (`expect=REFUSED got=MOVED`), matching `records/c1-c8-measured.txt`. The negative result
  re-derives; its receipt binds a scratch mutant digest (`55a5f46f…`) whose bytes are now filed (F8).

## Chronology (git history only)

| check | command | result |
|---|---|---|
| before receipts added | `git log --all --diff-filter=A -- census/round-87/controls/c1-before.txt` (and `c2-before.txt`) | added at P `77ccef7c` |
| before receipts at F | `git cat-file -e 6ed2d368:<path>` | both present |
| before receipts unchanged to R4 | `git diff 77ccef7c HEAD -- …/c1-before.txt` | empty (c1); c2 differs only in the scratch clone-path header line, numbers identical |
| F is prereg alone | `git diff --name-status 77ccef7c 6ed2d368` | `A census/round-87/preregistration.txt` only |
| after C2 receipt | `git cat-file -e HEAD:census/round-87/records/c2-after.txt` | present; added at R2, refiled at R3 and R4 (final: tool `821e3703…`) |
| after C1 receipt | `git cat-file -e HEAD:census/round-87/records/c1-after.txt` (HEAD = R5) | **MISSING**; `git log --all --diff-filter=A --` that path is empty: never added on any ref |
| pre-freeze after runs | `stat` | `controls/prefreeze/c1-after-prefreeze.txt` 06:47:19, `c2-after-prefreeze.txt` 06:41:25 — both before F's committer time 06:47:35 |

Consequences, stated plainly:

* The **before** receipts are committed at P, F's parent, and carried unchanged to R4. Proven from history.
* The **C2 after** receipt is committed after F (R2/R3). Proven from history.
* The **C1 after** receipt is not in any commit. Git history alone therefore cannot prove it was produced after F.
  It exists as a worktree file (mtime 07:02:30, 42 lines, `SUMMARY … killed_r86=8 killed_r87=10 killed_total=18`,
  `AFTER-EXIT:0`) and is **byte-identical** to `controls/prefreeze/c1-after-prefreeze.txt`, whose mtime (06:47:19)
  precedes F (06:47:35) by 16 s. The L1's plan A0.2 discloses that the first after runs preceded F and says the filed
  receipts are re-runs; the re-run is deterministic, so byte identity is expected, but the artifact does not by
  itself evidence the re-run. Finding F1.
* Plan A0.2 says "F landed 06:58"; git says F's committer time is 06:47:35 (P 06:47:24, R1 06:47:45). The disclosure's
  clock is wrong; its conclusion (pre-freeze after runs) still holds. Finding F5.

## Number-by-number reconciliation (both frozen sentences)

C1 sentence (preregistration.txt, lines 12–21):

| number | carried by | my re-derivation |
|---|---|---|
| 51 rows / r87 population | `c1-false-rows.tsv` 51 data rows, pin `b066fa0f…` | yes (51 non-comment rows; first 49 diff-empty vs r86) |
| r86 49 rows byte-for-byte, in order | `diff` of non-comment rows r86 vs r87[1..49] | empty |
| `TQ1 and NE1 at R10 / lane base` | rows: TQ1 `fixture R10 r78 L06 … QUARANTINED`; NE1 `lane BASE r87 I87E … ERROR` | yes |
| pristine r86 `mismatches=0 errors=0` | `controls/c1-before.txt`; `records/c1-after.txt` | my before run: `rows=49 mismatches=0 errors=0 exit=0`; independent after run: see below |
| pristine r87 `51 mismatches=0 errors=0` | `records/c1-after.txt` | independent after run: see below |
| ten mutants, `killed_r86=8 killed_r87=10 killed_total=18`, EXIT 0 | `records/c1-after.txt` (`AFTER-EXIT:0`) | independent after run: see below |
| do-nothing control `killed_r86=8`, m12/m16 alive, EXIT 0 | `controls/c1-before.txt` (`BEFORE-EXIT:0`) | my before run: `SUMMARY mutants=10 sets=r86 pristine_r86=ok killed_r86=8 killed_total=8`, EXIT 0; the two `killed=no` rows are m12 and m16 |

No number in the C1 sentence is missing from the receipts, with the caveat that the after numbers are carried by an
untracked file (F1) and that the "after" run that produced them is byte-identical to the pre-freeze run (F1/F5).

C2 sentence (preregistration.txt, lines 63–80):

| number | carried by | my re-derivation |
|---|---|---|
| 12-row counter | `ROWS` length 12; `SUMMARY rows=12` | yes |
| after `rows=12 mismatches=0 errors=0`, EXIT 0 | `records/c2-after.txt` (final: tool `821e3703…`) | my run on `821e3703…` with writer `70bbf1c2…` beside it: 12/0/0, EXIT 0 |
| before `mismatches=3` on KN1/KN2/KN3, nine rows unchanged, EXIT 1 | `controls/c2-before.txt` | my run on `cf875367…` with the control writer: `SUMMARY rows=12 mismatches=3 errors=0`, EXIT 1; the nine r85/r86 rows `match=yes`; KN1/KN2/KN3 `named=no` |
| `sha256 cf875367…, byte-identical to the r86 filed tool` | control file; `git show 5e288bb3:tools/souji-record-agreement.py` | both hash `cf875367…` |
| writer `70bbf1c2…` beside it | control writer; `git show 5e288bb3:tools/souji-receipt-write.py`; filed writer at R4 | all three hash `70bbf1c2…` |
| KN1 detail names `AttributeError` | after receipt `named=yes` | my final-tool probe: detail `the receipt writer produced no verdict (exit 1: AttributeError: …)`; a 400-char message keeps both ends and still contains `AttributeError` |
| KN2 header digest = writer sha, changes on one appended comment byte | after receipt `writer_sha=70bbf1c2a92e appended_sha=1b8ecf328ed3` | my run: same two values |
| KN3 record exactly `bad\nname2.txt`, class `uncommitted-path`, detail `??` | after receipt; `EXACT` in the counter | my run: K4 row `bad\nname2.txt / uncommitted-path / ??`, one physical line (`cat -A`) |
| before KN3 quoted form `"bad\nname2.txt"` | `controls/c2-before.txt` | my before run: `k4rows=['"bad\\nname2.txt"|uncommitted-path']` |
| no concealed row on the lane tree at the round tip | kill rule | my run of the final tool on the lane at R4: zero `stat-cache-concealed`/`index-flag-concealed` rows (19 `uncommitted-path` rows for the round's uncommitted work; `receipts/c2-lane-selfrun-r4.txt`) |

## Findings by severity

**MEDIUM**

* **F1 — the C1 after receipt is not in git, and its bytes are identical to the pre-freeze run.** At R3 and again at
  R4 `records/c1-after.txt` is untracked (`git cat-file -e` missing, `git log --all --diff-filter=A` empty) while
  `records/c2-after.txt` is committed. Its 4344 bytes are byte-identical to
  `controls/prefreeze/c1-after-prefreeze.txt` (mtime 06:47:19, before F 06:47:35). The claim's after numbers
  therefore rest on an untracked worktree file plus the disclosed pre-freeze twin; a reader cannot tell from history
  that the after run happened after F. Fix is in the L1's integration scope: commit `records/c1-after.txt` (the
  round's evidence commit already carries the C2 after receipts). Reproducer:
  `git cat-file -e HEAD:census/round-87/records/c1-after.txt` → rc 1.

**LOW**

* **F2 — frozen C2 limit superseded by the wave's own artifacts.** Preregistration: "only newline, tab and CR are
  C-escaped, so another control byte still lands raw in the record." The final tool's `_escape_record` doubles `\`
  and spells every byte outside printable ASCII as `\xNN` (verified: `0xff-name.txt` → `\xff-name.txt`; KB5's two
  names stay distinct). Plan A3 declares the final limits and the prereg is (correctly) not edited, but the round
  report must cite A3 when it repeats the frozen limit, or the limit reads false.
* **F3 — claim (c)'s long-line shape failed at R2 and is fixed only at R3.** On the R2 tool (`c2b0784e…`), the byte
  arm's KB4 (400-char exception message) gave `named=no`: the tail-only 200-character cut lost `AttributeError`
  (the exception type is at the line's start). R3 keeps both ends (100 + `…` + 99) and KB4 passes. The frozen
  sentence says "carries the writer's LAST non-empty stderr line"; for >200-character lines the final tool carries a
  200-character both-ends compaction of that line, not the line. A3 discloses the repair; the filing should carry
  A3's phrase rather than restate the frozen sentence unqualified.
* **F4 — `_stderr_tail(out or proc.stderr)` preferred stdout. FIXED at R4.** A delegated stub writer that printed one
  line to stdout and then raised produced the detail `the receipt writer produced no verdict (exit 1: stub stdout
  noise from writer module)` — the `AttributeError` was not named. Reproducer: copy the tool to a kit, write a
  `souji-receipt-write.py` whose module body prints and whose `_truth_refusal` raises `AttributeError`, run the tool
  on any repo. R4's `_stderr_tail(proc.stderr if proc.stderr.strip() else out)` names the exception in the same
  reproducer (`receipts/c2-stdout-preference-fixed-r4.txt`); plan A5 records the fix.
* **F5 — plan A0.2 clock. FIXED in the plan.** A0.2 originally said "F landed 06:58"; F's committer time is
  `2026-11-08 06:47:35 -0300` (P 06:47:24, R1 06:47:45). The current A0.2 reads "F's committer time 06:47:35,
  corrected per S87Reviewer F5"; the conclusion (pre-freeze after runs) was right all along.
* **F6 — code comment mislabelled the rename pair. FIXED at R4.** The R1–R3 comment said a rename's second NUL field
  is "the new name"; `git status --porcelain -z` on a staged rename emits `R  new.txt\0old.txt\0` (verified with
  `xxd`): the first field is the destination, the second the original. R4's comment says "the ORIGINAL name … git
  puts the destination first"; the skip logic was already correct. The frozen sentence never mislabelled the field.
* **F7 — plan A1/A2 cited stale four-row results. FIXED in the plan.** A1/A2 now read `rows=5 mismatches=5` and
  `rows=5 mismatches=0`, matching the final receipts at `controls/c2-byte-arm-before.txt` /
  `records/c2-byte-arm-after.txt`; the four-row intermediates were the same probe before KB5/KB4 were added.

**INFO**

* **F8 — third-candidate receipt bound a scratch digest. FIXED at R4.** `records/c1-c8-measured.txt` names counter
  `sha256 55a5f46f…` at `/fast/scratch/hyaku/souji-r87/c8.py`; at R4 the mutant bytes are filed at
  `census/round-87/controls/c1-mutant-c8-capture-suffix.py`, sha256 `55a5f46f…` exactly. I ran the filed file on the
  r86 population: `rows=49 mismatches=1`, row `NF12c` (`expect=REFUSED got=MOVED`), reproducing the receipt
  (`receipts/c1-c8-filed-mutant-mine.txt`). The mutant is a post-F control artifact, not a frozen instrument.
* **F9 — instrument pins hold.** Tampered population → harness EXIT 2 `C1-HARNESS-FATAL`; battery pins the same
  hashes; each mutant `old` occurs exactly once; the eight r86 mutants are object-identical and in order.
* **F11 — A8's counter-reach limit (INFO, named).** The 12-row counter's rows bind the observed outputs, not the
  mechanism: S87ExecEvade's F4/F5/F6 show a hard-coded `AttributeError` detail and a quote-stripping line-form tool
  both score 12/12. The byte arm's KB6 (`quo"te.txt`) and KB7 (`ValueError` on a 400-char line) bind the mechanisms;
  my run of the committed seven-row arm on the final tool is 7/0. This is a limit of the counter, not a number in the
  claim; the claim's sentences about the filed bytes hold.
* **F10 — lane self-run.** The final tool over the lane at R4 reports `keys=4 records=4 occurrences=18
  mismatches=20` (EXIT 1, expected: uncommitted work) with **19** K4 rows, all class `uncommitted-path`, and
  **zero** `stat-cache-concealed`/`index-flag-concealed` rows — the frozen kill rule's condition holds. Receipt:
  `receipts/c2-lane-selfrun-r4.txt`.

## Residual risk and verification gaps

* C1's after arm is verified here by my own run at F's instruments (see independent-run block below) and by the
  filed receipt; because the instruments never changed after P, the anchor is unambiguous. The unresolved item is
  durability/chronology (F1), not arithmetic.
* C2's target moved four times (R1 → R2 → R3 → R4). Numbers above are re-derived at R4; the earlier repairs' own
  defects (F2/F3/F4) are disclosed in the plan, and F4's fix is verified on the R4 bytes. If the lane moves again
  after this report, the C2 numbers must be re-derived on the new tool hash; the counter and control bytes are
  unchanged, so the delta is confined to `tools/souji-record-agreement.py`.
* The header binds the writer bytes read at run start; a writer swapped between the header read and the compile is
  still not caught (the frozen limit says so). The C2 counter's KN2 checks digest-vs-live-bytes at read time only.
* A4's p2/p3 mutants are not rows; they are declared unrowed and carried. My verdict agrees with the amended
  sentence, not with a reading of the frozen C1 sentence as "the clauses are fully bound".

## Independent runs (commands executed by this seat)

Runtime: Python 3, `-B`; work dirs under `/fast/scratch/hyaku/souji-r87/S87Reviewer`, never `/tmp`.

C1 after (F clone): `python3 -B census/round-87/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py
--work <empty> --only r86,r87 --expect-killed 18` → EXIT 0; `ARM pristine pop=r86 rows=49 mismatches=0 errors=0
exit=0`; `ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0`; all ten `MUTANT-PAIR` rows `killed=yes` on
r87, with `m12-token-on-line` and `m16-nf6b-punct` the only two `killed=no` on r86; `SUMMARY mutants=10
sets=r86,r87 pristine_r86=ok pristine_r87=ok killed_r86=8 killed_r87=10 killed_total=18`.

C1 before (F clone): `… --only r86 --expect-killed 8` → EXIT 0; `ARM pristine pop=r86 rows=49 mismatches=0 errors=0
exit=0`; `MUTANT-PAIR m12-token-on-line … killed=no …`; `MUTANT-PAIR m16-nf6b-punct … killed=no …`;
`SUMMARY mutants=10 sets=r86 pristine_r86=ok killed_r86=8 killed_total=8`.

C2 after (R4): counter `4e2b7c06…` on tool `821e3703…` → `SUMMARY rows=12 mismatches=0 errors=0`, EXIT 0; KN1/KN2/KN3
`named=yes`; KH1/KH2 `k4=0`. Also re-derived at R3 (`aac9a9ed…`) and R2 (`c2b0784e…`): 12/0/0 at both.
C2 before (R4): counter on `controls/c2-before-base-tool.py` → `SUMMARY rows=12 mismatches=3 errors=0`, EXIT 1;
mismatches are exactly KN1/KN2/KN3; the nine r85/r86 rows `match=yes`.
Committed seven-row arm (sha `6495b048…`) on tool `821e3703…` with `70bbf1c2…` beside it: KB1–KB7 all `match=yes`
→ `SUMMARY rows=7 mismatches=0`, EXIT 0 (also reproduced with my five-row snapshot `713badd7…`): KB1 `\xff`
named, KB2 `cr\r` named, KB3 destination only, KB4 `AttributeError` named, KB5 two distinct spellings → `SUMMARY
rows=5 mismatches=0`; on the R2 tool (`c2b0784e…`) KB4/KB5 fail (`rows=5 mismatches=2`).
F4 probe: stdout-print stub on the R4 tool → detail names `AttributeError` (on R1–R3 it carried only the stdout line).
C1 candidate: independent suffix-dropping `_capture_ok` mutant on the r86 population → `rows=49 mismatches=1`, row
`NF12c`; the R4-filed mutant `55a5f46f…` gives the same row and summary.
