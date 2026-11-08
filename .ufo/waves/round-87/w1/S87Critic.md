# S87Critic — C1/C2 wording attacks (round 87, w1)

Seat: S87Critic (critic, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Round: r87, prereg F `6ed2d368dc416f6409ac181e0ea45e23da82f89e`; lane base `5e288bb3152328f371325d0bf4fee7309d629991`.
This seat made **no lane edit, no commit/fetch/push, no git/jj mutation**: its only writes are this report,
`receipts/` beside it, and `/fast/scratch/hyaku/souji-r87/S87Critic/` (deleted before yield).

Timeline/provenance (the lane moved under the review): tip `6e502c5c` → `578cbf2c` → `89d36922` → `b0a64c94`
during the seat. The filed tool `tools/souji-record-agreement.py` measured `0ad9e3bf…` (commit `6e502c5c`),
`c2b0784e…` (`578cbf2c`), and `821e3703…` (final, commit `b0a64c94`); an intermediate uncommitted worktree version
`aac9a9ed…` was also measured. Every measurement below names its tool sha. The final `records/c2-after.txt` names
`821e3703…`, and the tip carries those bytes — the earlier provenance gap (a receipt naming an uncommitted tool) is
closed. The L1's `plans/round-87.md` A4/A7 already integrate several attacks below; each item says so.

## 0. Measurements

### 0.1 Instrument hashes

All nine frozen hashes re-measured and match (`receipts/instrument-hashes.txt`): `c1-false-rows.tsv b066fa0f…`,
`c1-items.tsv ce80195d…`, `c1-mutants.json 9368b342…`, `c1-pointer-counter.py fd0a8e24…`,
`c1-false-row-harness.py d6f4e612…`, `c1-clause-battery.py b0c1472b…`, `c2-k4-counter.py 4e2b7c06…`,
`controls/c2-before-base-tool.py cf875367…`, `controls/souji-receipt-write.py 70bbf1c2…`.

### 0.2 C1 after battery, independent re-run

    python3 -B census/round-87/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
      --work /fast/scratch/hyaku/souji-r87/S87Critic/after --only r86,r87 --expect-killed 18

`receipts/c1-after-recheck.txt`: `ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0`;
`ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0`; every mutant killed=yes on r87; `m12` and `m16`
killed=no on r86 and killed=yes on r87; `SUMMARY mutants=10 sets=r86,r87 pristine_r86=ok pristine_r87=ok
killed_r86=8 killed_r87=10 killed_total=18`; `EXIT=0`. The claim's numbers re-derive exactly.

### 0.3 Which row kills each new mutant (51-row population)

* `m12-token-on-line`: exactly one red row, `NE1` (`expect=ERROR`, `got=REFUSED`) — `receipts/rows-m12.out`.
* `m16-nf6b-punct`: exactly one red row, `TQ1` (`expect=QUARANTINED`, `got=REFUSED`) — `receipts/rows-m16.out`.

No other row moves under either mutant (mismatches=1; every other row match=yes).

### 0.4 C2 counter

* `rows=12 mismatches=0 errors=0`, EXIT 0 on tool `0ad9e3bf…` (`receipts/c2-after-0ad9e3.txt`), on `c2b0784e…`
  (`receipts/c2-after-c2b0784e.txt`), and on the final `821e3703…` (`receipts/c2-after-821e3703.txt`).
* Frozen before receipt: `rows=12 mismatches=3`, exactly KN1/KN2/KN3 (`census/round-87/controls/c2-before.txt`).
* The nine r85/r86 rows print identical `k4=`, `named=`, `match=` and `k4rows=` cells in the before receipt and in
  every after run.

### 0.5 Probes

`receipts/probe.out` (hermetic tiny repos, kits under the seat scratch): stub writer printing `STUB-STDOUT-NOISE` then
raising `AttributeError`; stub writer raising with a 400-character message; staged rename with source `ab cd.txt`;
`_stderr_tail` and the rename parse across tool revisions (`receipts/stderr-tail-across-revisions.txt`).

## 1. Numbered wording attacks

### 1. TQ1 binds only the line-end spelling of the punctuation clause — NARROW (covered by A4/p3)

*Sentence:* “the `_whole` sentence-end punctuation disjunct (S85MutCounter m16) … the following byte is one of
`.` `,` `;` `:` **and the byte after it is not a path character**”; limit “the two new rows bind exactly one clause
each”.

*Artifact:* `receipts/m16b.out` — a single-edit mutant that keeps the punctuation branch and drops only the
`after[1] not in PATHCH` conjunct:

    after_ok = (not after or after[0] not in PATHCH
                or after[:1] in (b".", b",", b";", b":"))

Battery on both populations: pristine `49/0` and `51/0` green; `MUTANT m16b-after1-only pop=r86 killed=no …
pop=r87 killed=no`; `killed_r86=0 killed_r87=0`; EXIT 0. TQ1's token is immediately before the final period, so
`len(after) < 2` decides and the `after[1]` conjunct is never reached; NF6b's target `other-stub` is followed by
`.bak`, but its token independently fails on `ignore-p6repo`.

*Recommendation:* **NARROW** — add to the C1 limits: “TQ1 binds only the sentence-end punctuation acceptance at the
line end (`len(after) < 2`); the `after[1] not in PATHCH` conjunct is not rowed — a single-edit mutant dropping only
that conjunct survives both populations (S87Critic `m16b-after1-only`: killed_r86=0 killed_r87=0, pristine 49/0 and
51/0, EXIT 0) — and stays carried.” **Status:** the L1's `plans/round-87.md` A4 already records this as S87MutCounter
p3 (the same edit, independently measured there); my receipt corroborates it. No further action if A4 is filed.

### 2. A strictly weaker counter passes the same battery — NARROW (covered by A7 C1-2)

*Sentence:* “The lane's false-row population is the instrument that certifies the pointer counter's rule”; “kills all
TEN frozen single-edit mutants … EXIT 0”.

*Artifact:* `receipts/w1.out` and `receipts/w1-diff.txt` — the filed counter with exactly one change,
`if entry is None: return "UNRESOLVED", ""` → `return "ERROR", "token not on the base line"` (sha `0cfa151c…`),
scored by the frozen battery: pristine green on both populations, all ten killed, `killed_r86=8 killed_r87=10
killed_total=18`, EXIT 0 — identical to the filed counter. Structural reason: every harness row calls
`judge(..., (cls, target), ...)` with its forge entry, so the `entry is None` / UNRESOLVED branch is unreachable from
any row, and the counter's own exit on the un-ledgered item population is not part of any ROW expectation (all
r86/r87 `exp_rc` are `-`).

*Recommendation:* **NARROW** — add to the limits: “the battery certifies the ten frozen mutants only; the
item-is-unledgered UNRESOLVED verdict is unreachable from any row, so a counter that answers ERROR for every
unledgered item passes both populations.” **Status:** A7 C1-2 quotes this limit verbatim from `w1.out`; no further
action.

### 3. “the lane base” names the wrong commit — NARROW (covered by A7 C1-3)

*Sentence:* “plus TQ1 and NE1 at the new fixture revision R10 / **the lane base**”.

*Artifact:* harness `BASE = e65538e73c7f1a8f7570bc24a2215da8a90043f3` (`c1-false-row-harness.py:99`; docstring
“the r79 lane base, unchanged”); lane rows are judged at `(lane, BASE)` (`:341`); the row file's column is `BASE`;
the round-87 lane base is `5e288bb3…` (prereg line 2); the R0 blob comes from the item population's base
`705fa1385c4ccec23811cfa57104046ec6587258` (counter `POPS`). NE1 is judged at `e65538e…`, not at `5e288bb3…` and not
at `705fa138…`.

*Recommendation:* **NARROW** — “TQ1 at fixture rev R10; NE1 at the harness's frozen `BASE`
`e65538e73c7f1a8f7570bc24a2215da8a90043f3` (the r79 lane base; the round-87 lane base `5e288bb3` is not a C1 rev),
its R0 blob read at the item population's base `705fa1385c4ccec23811cfa57104046ec6587258`.” **Status:** A7 C1-3
carries it.

### 4. The R0 guard's other two conjuncts are unrowed and were not carried — NARROW (covered by A7 C1-4)

*Sentence:* “the R0 guard's token-on-line half (S85MutCounter m12)”; carried list “m17 duplicate-id, the `_whole`
before-byte half, the `len(want) <= len(have)` half”.

*Artifact:* the guard is `if not (line.isdigit() and 0 < int(line) <= len(blob) and token in blob[int(line) - 1])`;
NE1's declared line 3166 is a digit inside the blob, so only the third conjunct is exercised (PASS: it is the sole
red row under m12, `receipts/rows-m12.out`). The `isdigit()` and in-range conjuncts are exercised by no row — NE1 is
the only ERROR-expect row in every C1 population (`grep -P '\tERROR\t'` matches only
`census/round-87/c1-false-rows.tsv`).

*Recommendation:* **NARROW (low)** — add them to the carried list. **Status:** A7 C1-4 carries it.

### 5. TQ1 is load-bearing for m16; an NF6e-style row cannot substitute — PASS

*Artifact:* `receipts/rows-m16.out` — on the 51 rows the only mismatch under m16 is TQ1; the frozen before receipt
shows m16 alive on the 49 rows. NF6e is judged at R2 where the late declaration is written at R3 (absent), and its
token appears inside `.gitignore-p6repo` (a path byte after the token, which the punctuation disjunct does not help).
The declaration is synthetic fixture text, as the stated limit says.

### 6. The growth 49→51 moves exactly two kills — PASS

*Artifact:* `receipts/c1-after-recheck.txt` + the frozen before receipt. The eight r86 mutants are killed on both
populations with identical mismatch counts (`m6 1/1`, `m7 1/1`, `m8 2/2`, `m9 4/4`, `m10 1/1`, `m11 1/1`, `c7 1/1`,
`m14 1/1`); m12 and m16 are alive on 49 rows and killed on 51 by exactly NE1 and TQ1. The growth moves no other kill.

### 7. Population composition and the counter diff are as stated — PASS

* `grep -v '^#' census/round-86/c1-false-rows.tsv` vs the first 49 data rows of the r87 file: identical and in order
  (51/49 data rows); the r87 items file is the r86 four rows byte-for-byte plus I87E; the ledger is byte-identical
  (`7cbb28c9…` in both rounds); `c1-items.tsv` sha `ce80195d…` matches the pin.
* `diff -u census/round-86/c1-pointer-counter.py census/round-87/c1-pointer-counter.py`: exactly the new `POPS` entry
  and `r[4] not in ("REFUSED", "MISMATCH", "ERROR")` (plus docstring); no resolution rule, class, message or branch
  changed.
* NE1's item is well formed: at `705fa138`, LOG.md line 3165 carries `census/round-84/records/c1-after.txt`, line 3166
  does not, so R0 (and only R0) yields ERROR.

### 8. The no-verdict detail preferred the writer's stdout — NARROW (fixed on the final bytes; A5 F4/A7)

*Sentence:* “(c) When the delegated writer produces no verdict, the K4 detail carries the writer's LAST non-empty
**stderr** line”.

*Artifact:* `receipts/probe.out` — kit writer prints `STUB-STDOUT-NOISE` and then raises
`AttributeError: STUB-EXCEPTION-WAS-HERE`; on the pre-fix bytes the K4 detail is
`the receipt writer produced no verdict (exit 1: STUB-STDOUT-NOISE); tracked bytes are unverified`, with no
`AttributeError`. The pre-fix code selected `_stderr_tail(out or proc.stderr)`; the final `821e3703…` selects
`_stderr_tail(proc.stderr if proc.stderr.strip() else out)` (`tools/souji-record-agreement.py:310`), and the control
kit without the stdout print carries the exception either way.

*Recommendation:* **NARROW** (wording) — “the last non-empty line of the writer's stderr, or of its output when
stderr is empty”. **Status:** fixed in the final bytes and covered by A5 F4 / A7 C2-1/C2-2; the filed receipt names
`821e3703…`.

### 9. A >200-character last line lost the exception's type name on the filed bytes — NARROW (fixed; A3/A7)

*Sentence:* “(c) … carries the writer's LAST non-empty stderr line — where an exception names itself — instead of the
first 200 characters”.

*Artifact:* `receipts/stderr-tail-across-revisions.txt` — on `0ad9e3bf…` (`6e502c5c`) and `c2b0784e…` (`578cbf2c`),
`_stderr_tail` keeps `…` + the last 199 characters: a 400-character `AttributeError: yyy…` line yields a
200-character detail with **no** `AttributeError`, and a tool-level long stub against `578cbf2c` prints exactly that.
The final `821e3703…` keeps the head 100 + `…` + the last 99 (`has_AttributeError=True`), and the wave's KB4 row
measures it.

*Recommendation:* **NARROW** — “a ≤200-character excerpt of the last non-empty line: the whole line when short; when
longer, its first 100 and last 99 characters with an ellipsis at the cut, so an exception's type name survives.”
**Status:** fixed and covered by A3/A7; the report must cite the `821e3703…` receipt.

### 10. The prereg's header limit “committed bytes” is false — PASS on the plan's corrected limit

*Sentence (prereg limit):* “the header binds the writer's **committed** bytes at run time, not the execution of that
program.”

*Artifact:* KN2 in `receipts/c2-after-821e3703.txt` — first digest `70bbf1c2…`; after appending one **uncommitted**
comment line, `1b8ecf32…`. The header tracks the on-disk bytes at print time. `plans/round-87.md` A1's named limit
already says the correct thing (“the writer bytes read at run start; a writer replaced between the header read and
the compile is not caught”).

*Recommendation:* **PASS** if the report uses A1's sentence; do not repeat “committed bytes”. (The residual point —
the header does not bind the bytes the delegated subprocess compiles, nor the execution — is A1's.)

### 11. The rename-skip parenthetical holds only on the repaired bytes — PASS on the final bytes

*Sentence:* “the -z form's second NUL field of a rename is skipped; the rename record itself already reaches the key”.

*Artifact:* `receipts/probe.out` and `receipts/c2-after-c2b0784e.txt`. On `0ad9e3bf…` the skip was a content test
(`len(rec) < 4 or rec[2:3] != " "`), and a staged rename whose **source** is `ab cd.txt` produced a phantom
`cd.txt` / `uncommitted-path` / `ab` row (raw `-z`: `R  x.txt\0ab cd.txt\0`); independent corroboration S87ExecC2 F3.
Commit `578cbf2c` replaces the test with the status letters `R`/`C` (skip exactly one field); the probe, run on
`aac9a9e…` whose skip logic is byte-identical to `c2b0784e…`/`821e3703…` (the later edits are the record escape, the
stderr preference and comments, by diff), shows only the destination row, and the 12-row counter is green on the
final bytes (`receipts/c2-after-821e3703.txt`). The final comment names the skipped field the ORIGINAL name (A5 F6);
the pre-fix comment called it “the new name”, which was wrong.

*Recommendation:* **PASS** on `578cbf2c`/`821e3703…` or later; if the `0ad9e3bf…` receipt were filed, **NARROW** the
parenthetical to “skipped when the record's status letters are R/C”. **Status:** the final receipt is `821e3703…`;
A5 F6 corrects the comment.

### 12. Provenance of the tool bytes and the `_stderr_tail` comment attribution — NARROW (one note open)

*Sentence:* “on the filed tool bytes”.

*Artifact:* the final `census/round-87/records/c2-after.txt` names `821e3703…`; `git show refs/heads/master:tools/
souji-record-agreement.py` at tip `b0a64c94` is `821e3703…` — the receipt is reproducible from the commit. The round's
instrument-hash list (the nine hashes this seat was given) does not include the tool; the report should state the tool
sha explicitly (A5 does: “Final tool bytes: `821e3703…` at commit R4”). **Still open:** the comment at
`tools/souji-record-agreement.py:224` reads `# r87 wave repair (S87Critic): …` for the both-ends `_stderr_tail` edit.
This seat made no lane edit; if the comment credits the finding, write “S87Critic finding, repaired by `<seat>`”;
if it credits the editor, it is wrong and should name the actual author (the final file already credits F4 to
S87Reviewer at line 308 and the other repairs to S87ExecC2).

*Recommendation:* **NARROW** — correct the comment's attribution (a code-comment fix, not claim wording).

### 13. The header's path cell is printed raw — NARROW (low; not yet covered)

*Sentence:* “(b) The tool prints one header line `# writer path=… sha256=…`”.

*Artifact:* `writer_binding()` returns `f"# writer path={K4_TRUTH_WRITER} sha256={digest}"` with no escaping. A copy
of the tool beside a writer whose path contains a newline breaks the one-line property, and the counter's KN2 regex
`^# writer path=(\S+) sha256=` also rejects a path containing a space. The filed tool's path has neither, so the
filed receipt is one line.

*Recommendation:* **NARROW (low)** — add to the limits: “the header path cell is printed raw; the one-line property
assumes a path with no newline (the KN2 parse assumes no whitespace).”

## 2. Disposition summary

| # | Attack | Verdict | Where it stands |
|---|--------|---------|-----------------|
| 1 | punctuation clause's `after[1]` half unrowed (m16b) | NARROW | A4 (S87MutCounter p3) + this receipt |
| 2 | weaker counter passes the battery (W1) | NARROW | A7 C1-2 |
| 3 | “the lane base” names the wrong commit | NARROW | A7 C1-3 |
| 4 | R0's `isdigit`/range conjuncts unrowed | NARROW (low) | A7 C1-4 |
| 5 | TQ1 load-bearing / NF6e cannot substitute | PASS | measured |
| 6 | growth moves exactly two kills | PASS | measured |
| 7 | composition + counter diff as stated | PASS | measured |
| 8 | no-verdict detail preferred stdout | NARROW | fixed on `821e3703…`; A5 F4/A7 |
| 9 | >200-char line lost the exception type | NARROW | fixed on `821e3703…`; A3/A7 |
| 10 | “committed bytes” header limit | PASS | A1's corrected limit |
| 11 | rename-skip parenthetical | PASS | final bytes `821e3703…`; A5 F6 |
| 12 | tool-byte provenance / comment attribution | NARROW | receipt reproducible; comment attribution open |
| 13 | raw header path | NARROW (low) | open (limit only) |

No attack reaches WITHDRAW: the claim's numbers re-derive on the frozen instruments, and the falsified sentences are
narrowings the round can (and mostly already did) record. The two remaining pre-file items are (12) the comment
attribution at `tools/souji-record-agreement.py:224` and (13) the header-path limit; neither changes the claims'
numbers.

## 3. Scratch disclosure

Scratch `/fast/scratch/hyaku/souji-r87/S87Critic/` (battery work dirs, mutant copies, probe kits, tiny repos, tool
revision copies) is deleted before yield; every receipt cited above is copied under
`.ufo/waves/round-87/w1/S87Critic/receipts/`. Nothing was left behind.
