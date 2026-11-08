# Round 87 — amendments to the frozen claims (pre-file falsification)

Written before the round report was filed. The frozen wording lives in `census/round-87/preregistration.txt`
(commit `6ed2d368dc416f6409ac181e0ea45e23da82f89e`, F) and is not edited here: each amendment records what the
round's own artifacts falsified in that wording, and the narrower sentence the round now puts its name to. Numbers
are re-derived on committed bytes by non-author seats and by the L1; records under `census/round-87/records/` and the
wave's reports under `.ufo/waves/round-87/w1/`.

Wave evidence root: `.ufo/waves/round-87/w1/`.

## A0 — instrument and chronology corrections (before or during data; not amendments to a claim)

- **A0.1 — the C1 candidate `_capture_ok` row was measured already bound and is not in the population.** The round
  started from the r87 plan's three candidate arms. Before the population was frozen, the candidate mutant
  `c8-capture-suffix` (the suffix comparison `have[-len(want):] == want`) was scored on the r86 49-row population
  and came back **killed** (`rows=49 mismatches=1`, the mismatching row `NF12c`):
  `census/round-87/records/c1-c8-measured.txt`. The planned NF-Z row would therefore have been padding; it was
  removed from the population and the mutant set before F, and the prereg's C1 paragraph records the negative
  result. Population 51 rows, mutants 10 — the two rows/mutants that remain are TQ1↔m16 and NE1↔m12.
- **A0.2 — the first after runs were produced before F landed, so they are not claim evidence.** Both after arms
  were first executed while the freeze was being written (C1 at 06:47:19, C2 the same minute; F's committer time 06:47:35, corrected per S87Reviewer F5). Those bytes are
  kept at `census/round-87/controls/prefreeze/` and are **not** filed as the claim's after-state; the filed receipts
  `records/c1-after.txt` and `records/c2-after.txt` are re-runs executed after F. The two runs' numbers agree
  (C1 `killed_r86=8 killed_r87=10 killed_total=18`; C2 `rows=12 mismatches=0`) — which is the only thing the pre-freeze
  pair is used for, disclosed rather than hidden (r63 M2's class).
- **A0.3 — the 12th seat is a simplifier, not a labrat.** The wave validator's `SWARM_ROLES`
  (`~/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs:265`) does not include `labrat`, so the planned dead-arm probe
  rides `S87Simplifier` (a permitted role) and the dead-arm hypothesis is stated there instead.
- **A0.4 — the C2 counter's KN3 row needed a triple, not a pair.** The first KN3 implementation compared `(record,
  class)` and read the class cell as if it carried the two status characters; in this tool the status characters are
  the *detail* cell (`bad("K4", path, "uncommitted-path", rec[:2])`). The row now compares all three cells exactly.
  Before that fix the after arm read `mismatches=1` on KN3 with the correct record present — a counter defect, not a
  tool defect; both before and after receipts were re-filed on the corrected counter bytes (sha256
  `4e2b7c06…`).

## A1 — C2: the wave's sentinel/executor found the first `-z` implementation strictly worse than the line arm; repaired in-round and measured outside the frozen counter

- **Artifact:** `.ufo/waves/round-87/w1/S87ExecC2.md` (HIGH-1, MEDIUM-1, MEDIUM-2) and the probe built from its repro,
  `census/round-87/c2-byte-arm.py`. Before the repair (`census/round-87/controls/c2-first-repair-tool.py`, the
  `6e502c5c` bytes, now filed at five rows by A3): `SUMMARY rows=5 mismatches=5` — KB1 an untracked path named with a raw `0xff` byte raised
  `UnicodeDecodeError` inside `git()`'s text-mode read, so the tool printed **no counts line and no K4 row at all**
  (a genuine uncommitted change became invisible — worse than the quoted spelling the line arm produced); KB2 a CR in
  a path was translated to LF by the text-mode read and the record said `\n`; KB3 a staged rename whose *source* name
  begins `ab ` produced a phantom `src.txt` row because the second NUL field was admitted by a content test.
- **Frozen wording:** not falsified — the claim's sentence speaks of a path carrying a **newline**, and the frozen
  12-row counter keeps its contract (`rows=12 mismatches=0` on the repaired bytes). What the wave falsified is the
  *implementation*, not the sentence.
- **Repair (landed):** `git_bytes()` runs the same pinned environment/argv with the stream left as bytes; the status
  arm decodes at the record boundary with `backslashreplace`, so a non-UTF-8 byte becomes `\xff` in the record; the
  rename/copy skip is decided by the status letters (`R`/`C`) and skips exactly one field; a CR survives as CR and is
  escaped as `\r`. After (final five-row probe, A3): `SUMMARY rows=5 mismatches=0`, EXIT 0
  (`census/round-87/records/c2-byte-arm-after.txt`), against `mismatches=5`, EXIT 1 before (`census/round-87/controls/c2-byte-arm-before.txt`). Commit `578cbf2c`; the
  four-row probe (KB4 the long exception message) is A2's.
- **Named limit (unchanged by the repair):** only newline, tab and CR are escaped; another control byte is written raw
  inside the record (the `backslashreplace` spelling covers only bytes that are not valid UTF-8). The header binds the
  writer bytes read at run start; a writer replaced between the header read and the compile is not caught.

## A3 — C2: two advisories the executor's follow-up measured on the repaired bytes; both closed

- **Artifact:** `.ufo/waves/round-87/w1/S87ExecC2.md` §7 (follow-up on the repaired bytes) and its receipts under
  `S87ExecC2/receipts/followup/`. Advisory 1: a manual escape that leaves a literal backslash alone is **not
  injective** — a name holding a real LF and a name holding the two bytes `\` `n` both print `x\nname.txt`, while the
  line arm's git-quoted spelling distinguishes them. Advisory 2: `truth_refusal` still read the delegated writer's
  stdout in text mode, so the FORGED detail for a forged CR-named file printed `cr\nname.txt` while the status arm
  printed `cr\rname.txt` — one name, two spellings.
- **Frozen wording:** neither advisory touches the claim's sentence (it names a **newline** path and a **last stderr
  line**); both are implementation defects the round closes rather than carries.
- **Repair (landed):** `_escape_record()` works on BYTES — `\` is doubled first, LF/TAB/CR become `\n`/`\t`/`\r`, every
  other byte outside printable ASCII becomes `\xNN` — so the record is injective and a reader can recover the exact
  bytes. The delegated subprocess is read with `capture_output` and decoded at the boundary, so one path has one
  spelling in both arms. Probe row KB5 (two names, one real LF and one literal `\` `n`) reads two distinct records on
  the repaired bytes and two identical ones on the first repair: `census/round-87/records/c2-byte-arm-after.txt`
  `rows=5 mismatches=0`, `census/round-87/controls/c2-byte-arm-before.txt` `rows=5 mismatches=5`. Commit `89d36922`.
- **Named limits (final):** the record is a byte spelling, not the name's display form (a non-ASCII name shows as its
  `\xNN` bytes); only the four shapes the probe carries are rows; the header binds the writer bytes read at run start.

## A4 — C1: each new row binds ONE spelling of its clause, and the mutation-tester measured the other spelling unrowed

- **Artifact:** `.ufo/waves/round-87/w1/S87MutCounter.md` §3/§3b and its receipts under `S87MutCounter/`.
  Two alternative single edits of the same clauses survive BOTH pinned populations:
  **p2** (`os.path.basename(token) in blob[int(line)-1]` — the token-on-line guard at basename granularity) and
  **p3** (the punctuation disjunct with the `.`-member kept but the `after[1] not in PATHCH` lookahead dropped).
  NE1's declared line carries neither the full token nor its basename, so p2 still reports `ERROR` on NE1; TQ1's
  period sits at line end, so `len(after) < 2` satisfies p3 too. The seat's direct and differential probes show both
  are reachable and unrowed (a synthetic blob line carrying only the basename flips `ERROR`→`UNRESOLVED` under p2; a
  both-legs declaration flips `REFUSED`→`QUARANTINED` under p3).
- **Frozen wording falsified (in part):** the C1 sentence says the two clauses "get their rows" and its limits name
  the `len(want) <= len(have)` half and the `_whole` **before**-byte half. It does not say the two new rows bind a
  *single spelling* of each clause, and p2/p3 are the other spellings of the very clauses the round certifies.
- **Two more survivors the seat's §4 measured, which the frozen limits did not name:** **p7** (`_regular`'s mode
  whitelist — a *symlink* range member is accepted when the whitelist is dropped; NF8 binds only the directory leg)
  and **p8** (`token_ok`'s hyphen marker — dropping `-` from `">\\-"` is unexercised because NF-S forges I85T with
  class `BOGUS`, refused by the class enum first). **p6** (`bool(want)` in `_capture_ok`) is measured **dead** over
  161,472 quantity-qualified pairs and 181,945 synthetic probes, so it is retired rather than carried.
- **Amended sentence:** *each new row binds ONE spelling of its clause: TQ1 binds the punctuation disjunct's
  `.`-member at line end and NE1 binds the token-on-line guard's whole-token spelling. The population does not bind
  the `after[1]` lookahead half (p3), the basename granularity (p2), `_regular`'s symlink leg (p7), `token_ok`'s
  hyphen marker (p8), m17's duplicate ledger id, `_whole`'s before-byte half or `_capture_ok`'s
  `len(want) <= len(have)` half; all seven are reachable-and-unrowed except p6 (`bool(want)`), which is measured
  dead, and all seven are carried to r88 with `S87MutCounter`'s receipts as the measurement that names them.*

## A5 — C2: the reviewer's three code/ledger corrections, landed before filing

- **Artifact:** `.ufo/waves/round-87/w1/S87Reviewer.md` F4/F6/F8. **F4:** the no-verdict detail preferred the
  delegated process's stdout, so a stub that printed one line and then raised left the exception unnamed; the detail
  now prefers stderr when it carries anything (measured: the byte arm's KB4 row and the 12-row counter re-filed on the
  new bytes). **F6:** the code comment called a rename's second NUL field "the new name"; git puts the destination
  first and the second field is the ORIGINAL name — the skip logic was already right, the comment is corrected.
  **F8:** `records/c1-c8-measured.txt` named a scratch counter digest; the mutant bytes are now filed at
  `census/round-87/controls/c1-mutant-c8-capture-suffix.py`, sha256 `55a5f46f…`, exactly the digest the receipt names.
- **Frozen wording:** none falsified; F2/F3's limits are superseded by A3's (the record is an injective byte spelling,
  and the detail is a both-ends compaction of an over-long last line), which the report cites.
- Final tool bytes: `821e3703…` at commit `R4`; 12-row counter `rows=12 mismatches=0`, byte arm `rows=5
  mismatches=0`, both re-filed.

## A6 — C1: the third-candidate record is re-filed byte-bound (S87ExecC1 F1) and the after receipt is committed

- **Artifact:** `.ufo/waves/round-87/w1/S87ExecC1.md` finding 1: `records/c1-c8-measured.txt` named a scratch harness
  digest (`4e29500a…`) that is neither the r86 harness nor the filed r87 one, so the record could not be re-derived
  from committed bytes. **Repair:** the record was re-produced on the filed instruments (harness `d6f4e612…`,
  population `79db70f6…`) against the filed mutant bytes
  `census/round-87/controls/c1-mutant-c8-capture-suffix.py` (`55a5f46f…`, the digest the record already named):
  `SUMMARY rows=49 mismatches=1`, the mismatching row NF12c. Same verdict, now re-derivable.
- **Artifact:** S87ExecC1 finding 2 and S87Reviewer F1 — `records/c1-after.txt` was untracked. It is committed with
  this round's integration commit, so the after numbers have a history.
- **Frozen wording:** unchanged; the negative result and the after arm are the same numbers as filed.

## A7 — the critic's wording gates: three C1 limits the frozen sentence leaves unnamed, and the C2 sentences the
## final bytes require

- **C1-2 (structural).** The harness's forge always supplies a ledger entry, so `judge`'s `entry is None → UNRESOLVED`
  branch is unreachable from every row: the filed counter with that branch replaced by the R0 diagnostic scores
  `killed_r86=8 killed_r87=10 killed_total=18`, EXIT 0, pristine green — identical to the filed counter
  (`S87Critic` receipts `w1.out`). **Limit:** *the battery certifies the ten frozen mutants only; the item-is-unledgered
  UNRESOLVED verdict is unreachable from any row, so a counter that answers ERROR for every unledgered item passes both
  populations.*
- **C1-3 (naming).** "NE1 at the lane base" is wrong: the harness judges `where=lane` rows at its own frozen
  `BASE = e65538e7…` (the r79 lane base), while NE1's R0 blob comes from the item population's base
  `705fa138…`; the round-87 lane base `5e288bb3…` is not a C1 rev. **Amended naming:** *TQ1 at fixture revision R10;
  NE1 at the harness's frozen BASE `e65538e7…`, its R0 blob read at the item population's base `705fa138…`.*
- **C1-4 (R0's other conjuncts).** NE1's declared line is a digit inside the blob, so only the `token in
  blob[int(line)-1]` conjunct is exercised; a counter dropping `line.isdigit()` or `0 < int(line) <= len(blob)`
  survives the same way m12 did. **Limit:** *the R0 guard's `isdigit()` and in-range conjuncts are unrowed too.*
- **C2-1/C2-2 (final bytes).** The detail prefers the delegated process's **stderr** when it carries anything
  (`S87Reviewer` F4, landed), and an over-long last line is carried as a both-ends compaction, not verbatim.
  **Amended sentence:** *when the delegated writer produces no verdict, K4 reports the last non-empty line of the
  writer's stderr (or of its output when stderr is empty), compacted from both ends when the line exceeds the bound.*
- **C2-4/C2-7 (final bytes).** The rename parenthetical holds because the skip is decided by the status letters `R`/`C`
  (on `0ad9e3bf…` it was a content test — `S87ExecC2`, `S87Scribe` F2), and the record cell is an injective byte
  spelling (`\` doubled, LF/TAB/CR named, other non-printable bytes as `\xNN`), not "only newline, tab and CR".
  Both sentences are A3's/A5's, and this round files them; the prereg's limits are superseded and not edited.

## A8 — C2: the mechanism layers the 12-row counter cannot see are bound by the byte arm's KB1/KB6/KB7 (S87ExecEvade
## F4–F6)

- **Artifact:** `.ufo/waves/round-87/w1/S87ExecEvade.md` F4/F5/F6: a tool whose no-verdict detail hard-codes
  `AttributeError` scores 12/12 while (c) is absent; a tool that keeps `git status --porcelain` and strips only the
  wrapping quotes scores 12/12 while (a) is absent (for a newline path the quoted-minus-quotes spelling equals the raw
  one). **The counter's reach is the finding**, not the filed bytes — the claim's sentences about the filed bytes hold.
- **Bound instead by the byte arm, three layers deep** (`census/round-87/c2-byte-arm.py`, seven rows):
  - **KB6** requires the record of a name holding a `"` to be `quo"te.txt`; the line-form tool records `"quo\"te.txt"`
    (`controls/c2-byte-arm-lane-base.txt`), so (a)'s mechanism is bound where (a) is absent.
  - **KB1** requires `\xff-name.txt`; the line-form tool records `"\377-name.txt"` — git's C-quoting is octal, the
    record's escape is hex, so a quote-stripping line-form tool cannot pass.
  - **KB7** requires the detail to name `ValueError` (a 400-character message); a hard-coded `AttributeError` fails
    it, and the first repair's prefix cut fails it too (`controls/c2-byte-arm-before.txt`, `named=no`).
  - The filed bytes read `SUMMARY rows=7 mismatches=0` (`records/c2-byte-arm-after.txt`); the lane-base tool
    `mismatches=6` and the first-repair bytes `mismatches=6` (KB6 passes there because that layer is already `-z`).
- **C1 limit (S87ExecEvade F1/F3).** The battery's exit checks only the *sum* of kills; the claim's evidence is the two
  per-set counts in the SUMMARY line (`killed_r86=8 killed_r87=10`), which a reader re-derives, and a subject that
  reads its own mutant path can branch — a named limit, not a claim number. And `_capture_ok`'s
  `len(want) <= len(have)` conjunct is **semantically redundant** (Python's negative slice clamps; 0 differing cases
  over the exhaustive {a,b} sweep), so it is retired as redundant rather than carried to r88.

## A9 — C2: the sentinel's four delegation-seam defects, all closed on the final bytes (and re-probed with its own repro)

- **Artifact:** `.ufo/waves/round-87/w1/S87Sentinel.md` and its `repro.py` (run against the filed bytes `e1b00e8a…`).
  **F1 (HIGH) — TOCTOU:** the header digest was a separate `open()` from the bytes `truth_refusal` compiled, so a
  writer swapped in between was named by one digest and ran as another (measured window 0.020 s, not a micro-race).
  **Closed:** `writer_binding()` stores the digest it printed and the bootstrap reports the digest of the bytes it
  actually compiled; a disagreement returns `RECEIPT-WRITER-SWAPPED`. `repro.py --probe TOCTOU` now reads
  `EVIL writer ran: False`, `BOUND? yes`.
  **F2 (MEDIUM) — CLEAN-spoof:** a writer that printed `CLEAN` and then died was read as a clean verdict (fail-open).
  **Closed:** the token counts only with a zero exit (`repro.py --probe CLEAN` now yields a refusal detail).
  **F3 (MEDIUM) — REFUSED-inject:** the writer's `SystemExit` code was interpolated raw, so a code carrying a newline
  and a `MISMATCH<TAB>K4` line injected a forged row. **Closed:** the payload is escaped and single-lined
  (`repro.py --probe INJECT` now sees 1 row).
  **F4 (LOW/MEDIUM) — DETAIL-tear:** the detail cell carried U+2028/U+2029 raw, tearing one record for a
  `splitlines()` reader. **Closed:** `_escape_text` names U+0085/U+2028/U+2029 and `_escape_record` decodes the UTF-8
  forms of the two separators (`repro.py --probe SPLITLINES` `torn? False`, `--probe ESCAPE` distinct).
- **Frozen wording:** unchanged; the claim's sentences still hold on the filed bytes, and the fixes are strictly
  refusals where the tool previously accepted.
- **Receipts re-filed on `e1b00e8a…`:** 12-row counter `rows=12 mismatches=0`; byte arm `rows=10 mismatches=0`; the
  two before arms `mismatches=3` (12 rows) and `mismatches=8` (10 rows, lane-base and first-repair layers).

## A10 — C1: the simplifier's deletion audit, all six dispositions held to r88 (S87Simplifier)

- **Artifact:** `.ufo/waves/round-87/w1/S87Simplifier.md` and its `receipts/d2.patch`. **D2** (`bool(want)` in
  `_capture_ok`, `c1-pointer-counter.py:360`) is measured **DEAD** — both arms `49/0/0` and `51/0/0`, killed 8/10, and
  a per-mutant mismatch vector identical to the filed counter's, over 268k structured + 60k random + 24.2M enumerated
  shapes. **D1** (`or len(got) < 2`) is dead in logic (0 differences) but deleting it makes the frozen mutant
  `m14-short-shape` unappliable (battery EXIT 2, `edit occurs 0 times`). **D2b** (`len(want) <= len(have)`) is dead
  and battery-clean but the prereg's stated limits name it "carried", so landing it now would falsify the round's own
  sentence. **D3** (`_whole`'s before-byte half) is **NOT dead**: a live semantic clause, unrowed (3,984 of 20,000
  random `_whole` flips). **D4** (`tt == tk`) has no executable remnant. **D5** (the P04/P07 pins) are load-bearing
  (zeroing either gives harness EXIT 2).
- **Disposition: none lands this round.** The counter's bytes are what the filed receipts and the round's instrument
  hash line name; deleting D2 now would invalidate them for a measured-zero gain. All six are carried to r88, with
  D2's patch and D1's m14-retargeting requirement as the starting point, and D3 flagged as needing a *row*, not a
  deletion.
