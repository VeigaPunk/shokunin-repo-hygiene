# Round 88 — amendments to the frozen claims (pre-file falsification)

Written before the round report was filed. The frozen wording lives in `census/round-88/preregistration.txt`
(commit `f74092b24bbddf2e5259977c254c91b7a6b71160`, F) and is not edited here: each amendment records what the round's
own artifacts falsified in that wording, and the narrower sentence the round now puts its name to. Numbers are
re-derived on committed bytes by non-author seats and by the L1; records under `census/round-88/records/` and the
wave's reports under `.ufo/waves/round-88/w1/`.

Wave evidence root: `.ufo/waves/round-88/w1/`. Instruments and controls: P
`e60ea25f6dc6d988bbdd713a2d00718f5915e29d`.

## A0 — instrument and chronology corrections (before or during data; not amendments to a claim)

- **A0.1 — two after arms were first executed before F landed, so those runs are not claim evidence.** The C1
  battery was first run on the r88 instruments at 07:52 (the `bat1` scratch; killed at its 300 s deadline before it
  printed a summary) and the C2 fixture on the final tool bytes at 07:53; F landed at 08:02 (committer time). The
  filed receipts are post-F re-runs: `census/round-88/records/c1-after.txt` and `records/c1-dead-belt.txt` (started
  08:05) and `records/c2-after.txt` (08:05). The pre-freeze C2 run's numbers happen to agree with the filed run
  (`tool_pass=7 before_pass=3`); the pre-freeze pair is disclosed here and is not used as evidence (r63 M2's class,
  r87 A0.2).
- **A0.2 — the counter under test is the frozen r87 counter, unchanged.** The round changes the population
  (`census/round-88/c1-false-rows.tsv`, 53 rows), the mutants (12 filed + 1 belt member) and the harness (the R11
  fixture revision and the `where=ledger` row type), never a resolution rule. `census/round-87/c1-pointer-counter.py`
  sha256 `fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b` at P and at F; the earlier plan to copy it
  into the r88 directory was dropped in the build (a byte-identical copy is dead weight, and a copy would need its
  own pin for no measured gain). The belt note the SCORECARD plan asked the counter to carry lives in this plan and
  the prereg instead, because the counter's bytes are unchanged.
- **A0.3 — the `_capture_ok` `len(want) <= len(have)` arm is a belt, and the belt is measured, not asserted.** The
  13-member `census/round-88/c1-mutants-dead.json` scores `m19-len-half` as a survivor on both sets
  (`records/c1-dead-belt.txt`); the prereg records it as a belt, not a row. The arm is not deleted because the frozen
  `m14-short-shape` mutant's `old` text and the round's own `m18` edit both depend on the surrounding function bytes;
  deleting it would invalidate a filed mutant for a measured-zero verdict change (r87 A10 D2b's disposition).
- **A0.4 — the before census is a reconstruction at the lane base, and says so.** The S348/S349 rows were appended
  before the round-start census ran, so `census/round-88/records/sources-census-before.txt` validates
  `git show 7defe9c5:corpus/SOURCES.md` with `--file` inside a read-only symlink mirror of the lane (the `--file` form
  resolves `used-by` under the file's parent; the script's `--root` form reads the live tree only). It reads
  `file ok`, EXIT 0, with the base's 87 pre-existing `W04` warnings; the after run reads `souji ok`, EXIT 0
  (`records/sources-census-after.txt`). Registry 270 → 272.

## A1 — C1: the harness change is a judgement change for the ledger row, and the belt is measured, not proved

- **Artifact:** `.ufo/waves/round-88/w1/S88Critic.md` C1-a and C1-b (the critic built each row and measured the
  batch).
- **Frozen wording falsified (in part):** the prereg's "Harness change (disclosed)" paragraph ends "No judgement
  code changed; the row type only builds the duplicate-ledger input and parses the counter's own `LEDGER-REFUSED
  id=<item>` line and exit code." That sentence contradicts itself: deciding a row's verdict from the marker and the
  exit code IS judgement code, and the r87 harness cannot score LD1 at all (unknown `where` is FATAL). The C1 kill
  count is still a counter-clause kill — the counter's `_ledger` guard decides — but it is measured by a harness
  branch added this round, not by the unchanged harness.
- **Narrowed sentence:** *No judgement code changed for lane and fixture rows; LD1 adds one `where=ledger` judgement
  branch (duplicate-ledger build plus `LEDGER-REFUSED` marker and exit-code check), and the m17 kill is a
  counter-clause kill measured by that new harness code.*
- **Artifact (C1-b):** the belt run `records/c1-dead-belt.txt` (`m19-len-half killed=no` on both sets) plus the
  critic's reading of `_capture_ok`.
- **Frozen wording falsified (in part):** "measures the third DEAD" reads as a categorical claim; the measurement is
  two frozen populations. The half is entailment-redundant given `have[-len(want):] == want` (a slice equality needs
  `len(have) >= len(want)`), but the round's evidence is the two population arms, not a proof over all inputs.
- **Narrowed sentence:** *m19-len-half survives both sets on the frozen populations (empirically dead on those
  inputs; the half is entailment-redundant given `have[-len(want):] == want`, but the round claims only the measured
  belt, not a proof for all inputs).*

## A2 — C2: the 200-character bound is the excerpt, not the whole K4 cell

- **Artifact:** `.ufo/waves/round-88/w1/S88Critic.md` C2-a, and `S88ExecC2.md` §"Excerpt arithmetic" (the measured
  cell): `_one_line` returns exactly 200 characters (head 100 + `…` + tail 99), while the full detail string is
  `the index-flag read failed (<200>); tracked bytes are unverified` = 259 characters.
- **Frozen wording falsified (in part):** "The resulting K4 detail is ONE physical line of at most 200 excerpted
  characters" invites the reading "the detail is ≤200 characters". It is not; the fixture's own `case_long` bound is
  `<= 260`.
- **Narrowed sentence:** *The K4 FLAGFAIL excerpt (`_one_line`) is bounded at 200 characters; the full K4 detail
  string with its `the index-flag read failed (…) ; tracked bytes are unverified` wrapper is 259 characters on the
  long case (the fixture's bound is `<= 260`).*

## A3 — C2: the escape set is C0/DEL/NEL/LS/PS, not every C1 control

- **Artifact:** `.ufo/waves/round-88/w1/S88Critic.md` C2-e: `_escape_text` escapes `o < 0x20`, `0x7F` and `0x85`
  (plus U+2028/U+2029), so U+0080–U+0084 and U+0086–U+009F pass raw; KFF4's single `0x85` byte arrives through
  `backslashreplace` as the literal text `\x85`, so the fixture does not exercise the `chr(0x85)` arm.
- **Frozen wording falsified (in part):** the C2 sentence says "C0/C1 controls, NEL and U+2028/U+2029 printed as
  escapes". The C1 control block is wider than the one C1 code point the tool escapes.
- **Narrowed sentence:** *The FLAGFAIL escaping covers C0, DEL, NEL (U+0085) and U+2028/U+2029 — not all C1
  controls; U+0080–U+0084/U+0086–U+009F pass `_escape_text` raw, and the KFF4 case does not exercise the text-level
  NEL arm (its `0x85` byte arrives as backslashreplace literal text).*

## A4 — Sources: S348 overlaps S278 by page content, and S349's word count was one high

- **Artifact:** `.ufo/waves/round-88/w1/S88ScoutSources.md` §1 (the overlap) and its
  `repro-c1-control.py`; the scout re-fetched both captures (`S278`'s 3.12 page and `S348`'s 3.14 page) and reports
  the rendered boundary tables byte-identical.
- **Disposition: S348 is kept; no S350 is added.** S278 (Python 3.12 `stdtypes.html#str.splitlines`, opened
  2026-11-03) carries the same documented fact for the hidden-line-numbering consumer; S348 carries the page of the
  **host's** Python (3.14.8, the version the knowledge entry's recheck names) for the escaping consumer. The
  version and the consumer are the two cells that differ; the census sees no `E04` (the scopes differ) and S278 stays
  as filed (append-only). A third row for the same page (the scout's proposed S350) is not added: it would be
  registry weight, not knowledge.
- **Correction, before filing:** the S349 row and the knowledge entry said the `b64decode` quote is 16 words; it is
  15 (`len(q.split())` on the filed sentence). Both cells are corrected in this round's new bytes; the quote itself
  is unchanged.

## A5 — C2: the tool's docstrings were corrected after the wave spawned; the receipts were re-run on the new bytes

- **Artifact:** `.ufo/waves/round-88/w1/S88Simplifier.md` hash table and `S88ExecC2.md` hash list, both naming
  `tools/souji-record-agreement.py c0604b4a…`; the filed tool is now `3e1fc030…`.
- **What changed and why:** after the wave spawned, the `_one_line` docstring was corrected from "a C0/C1 control
  byte" to "an LF/TAB/CR, a C0 control byte, DEL, NEL or U+2028/U+2029 … the C1 block beyond NEL is not escaped"
  (A3's narrowing, in code). The executable path did not change; the C2 after receipt
  (`records/c2-after.txt`) and the r87 12-row regression (`records/c2-k4-regression.txt`) were re-run on the new
  bytes and report the same numbers (`cases=7 tool_pass=7 before_pass=3`, EXIT 0; `rows=12 mismatches=0`, EXIT 0).
- **Second correction (same class, the connector's D6):** the K4 docstring line still described the read as
`git status --porcelain`, not `--porcelain -z`; it is now corrected, and the C2 after and regression receipts were
re-run once more on the final bytes (`tools/souji-record-agreement.py` sha256 `4042218f…`, commit `f62eeb85…`).
**Consequence for the wave's evidence:** the seats' hash verification names the pre-change bytes. Their
  behavioural verdicts stand for the code path (the diffs are docstrings); the filed receipts bind `4042218f…`.

## A6 — documentation corrections the scribe measured (F1/F3/F4), the connector's D4/D6, and the routed docstring

- **Artifact:** `.ufo/waves/round-88/w1/S88Scribe.md` F1/F3/F4 and its `quote-verification-receipt.txt`.
- **F1 (provenance overclaim) — corrected.** The Round-88 provenance paragraph said the quote "was checked
  byte-for-byte against the capture"; the quote is not a byte substring of the HTML capture (tags and line breaks sit
  inside the sentence). It now says the quote was checked against the RENDERED text (tags stripped, whitespace
  collapsed) and counts 18 words, which is what the receipt records.
- **F3 (teaches vs quote) — narrowed, not re-quoted.** S348's `teaches` cell asserted a boundary list the 18-word
  quote does not enumerate. The cell now says the boundary table immediately below the quote lists the entries (the
  quote locates the table; it does not enumerate it). The alternative (widen the quote to the 25-word table excerpt)
  would have lost LS/PS anyway; the narrowed cell keeps the filed quote and its word count honest.
- **F4 (Q161's stale tail clause) — corrected in Q163.** Q163 said "Extends Q161 and Q159 (they stand)", but Q161's
  tail-only clause contradicts the code, which has kept both ends since the r87 `89d36922` repair. Q163 now says it
  extends Q159 and corrects that clause by naming it. The tool's own `_stderr_tail` docstring still says "leading
  ellipsis"; it is routed to r89 because changing the tool's bytes again would invalidate the C2 receipts for a
  comment-only change (A5's class). The connector's D6 (the K4 docstring said `--porcelain`, not `--porcelain -z`) IS
  corrected on the final bytes because it misdescribes the read a reader acts on, with the receipts re-run (A5).
- **The connector's D4 — the missing rejected SOURCES row — is closed by S350**, not by S349: S350 is
  git-config(1)'s `core.quotePath`, opened this round from the installed page (capture
  `census/round-88/srcs/git-config.1` sha256 `f158d47e…`, roff line 3564, a 19-word located quote), REJECTED with its
  flip (a round that starts parsing the line form). The earlier report sentence that credited S349 for D4 was wrong
  and is corrected.

## A7 — C1: LD1's kill is the missing marker (not an exit-code delta), and two cosmetic cells are held

- **Artifact:** `.ufo/waves/round-88/w1/S88ExecC1.md` §2/§5 (hand-driven pristine/mutant/control runs at R11 and
  the duplicate ledger).
- **Finding (LOW, documentation):** `census/round-88/c1-mutants.json`'s m17 note says "the counter exits 0" under the
  mutant. Measured: the mutant's exit stays **1**, because the appended `ABSENT` row wins and the counter refuses P01
  as "exists under the fleet root" (`resolved=34`); what changes is the missing `LEDGER-REFUSED id=P01` marker (and
  P01's status, FLEET→REFUSED). The filed kill rule is phrased correctly — the harness requires the marker AND
  `rc=1`, and the marker is the sole discriminator — so the claim is not falsified, but the note overstates an
  exit-code delta.
- **Narrowed sentence:** *Under m17 the duplicate is accepted (no `LEDGER-REFUSED` marker; P01's status flips and the
  run's exit stays 1 because the appended ABSENT row refuses P01 under the fleet root); the LD1 row's discrimination
  is the marker, not an exit-code delta.* The mutant file is not edited: its sha256 is pinned by the battery's
  receipts header and a note-only change would invalidate three filings for a measured-zero verdict change. The
  corrected sentence lives here and in the lesson.
- **Cosmetic, held:** the r88 population file's header comment still opens "souji r87 C1 population" (inherited
  text); fixing it changes the pinned population sha for no verdict change. Held to r89 with the same class as the
  `_stderr_tail` docstring (A6).

## A8 — C1: each new row binds ONE spelling of its clause, and four unrowed sibling legs are named

- **Artifact:** `.ufo/waves/round-88/w1/S88MutCounter.md` §2–§4 and §7 (F1/F2/F3/F4), with its `probes*.txt` and
  `variants*.json` receipts.
- **F1 (HIGH, NF6g):** the R11 declaration precedes the L06 token with `x` (alphanumeric). A single edit of the same
  line that narrows the before-guard to alphanumerics (`m18b`) survives both pinned populations; at function level
  pristine refuses all eight `PATHCH` predecessor classes, `m18b` flips seven and keeps the alnum one. So NF6g binds
  the alnum spelling of the before-byte half, and the `/`-predecessor row (`NF6h`) would bind the classic
  word-boundary spelling. The prereg's limits named "not every declaration shape", not this class.
- **F2 (HIGH, LD1):** the filed duplicate is class-different (`FLEET`→`ABSENT`) but target-equal (`-`). An id-only,
  target-keyed duplicate rule (`m17b`) survives both sets; the class+target rule (`m17d`) is killed and the
  different-target counterfactual (`LD1b`) turns `m17b` red. So LD1 binds one duplicate spelling.
- **F3/F4 (MEDIUM):** the `_ledger` malformed-row guard (`len(r) < 3`, `m17c`) and `_whole`'s multi-occurrence loop
  (`m18d`, first-occurrence-only) are unrowed; `LD2` and `NF6i` are their measured designs.
- **F5/F6/F7 (LOW/INFO):** `_regular`'s `fleet:` symlink leg is a second spelling of carried p7; `_whole`'s `,` `;`
  `:` punctuation members are dead (only `.` is in `PATHCH`, so `x1` is an equivalent mutant — no row can bind them);
  the `LEDGER-REFUSED` marker is shared by three legs (malformed, duplicate, unknown id), so a counter that refused
  the same id for another reason would pass LD1.
- **Narrowed sentence:** *Each new row binds ONE spelling of its clause: NF6g's predecessor is alphanumeric (`x`), so
  the row discriminates the alnum guard (`m18b` survives) while pristine refuses all eight PATHCH predecessor classes
  at the function level; LD1's appended duplicate is class-different but target-equal, so an id-only/target-keyed
  duplicate (`m17b`) survives. The `_ledger` malformed-row guard (`m17c`) and `_whole`'s multi-occurrence loop
  (`m18d`) stay unrowed, and the `LEDGER-REFUSED` marker does not distinguish its three legs. NF6h, NF6i, LD1b and
  LD2 (S88MutCounter §7) are carried to r89.*
- **Carried to r89 (measured designs, not landed):** `NF6h` (slash predecessor), `NF6i` (token twice, later whole),
  `LD1b` (different-target duplicate), `LD2` (2-column row); plus the four r87-carried spellings p2/p3/p7/p8 and the
  `fleet:` symlink leg.

## A9 — C2: the escape-first excerpt is injective on text, not on raw bytes, and its head budget is spent on escapes

- **Artifact:** `.ufo/waves/round-88/w1/S88Sentinel.md` §4 F1/F2 and its `receipts/probe_c2g-final-bytes.txt`,
  `probe_head.txt`; §3's marker-prefix note; F3/F4 carries.
- **F1 (MEDIUM, r88-introduced):** the parent's `raw.decode('utf-8', 'backslashreplace')` maps an undecodable byte to
  the four characters `\xff`, and `_escape_text` then doubles the backslash; a raw `0xFF` byte and the literal four
  characters `\xff` therefore render byte-identically. `_escape_text` is injective on TEXT (the sentence the prereg
  states), but the composed decode+escape pipeline is not injective on the writer's raw stderr. Measured: raw byte
  `0xFF` vs literal `\xff` → SAME DETAIL; r87's control collided on a different pair.
- **F2 (LOW–MEDIUM, r88-introduced):** `_one_line` escapes first and then keeps head-100/…/tail-99 of the ESCAPED
  text. Each control byte costs four characters, so 25 leading control bytes consume the whole head and the exception's
  type name falls outside both ends (`names_AttributeError=False` for 25/30/40 leading SOH). The filed KFF3 shape (a
  400-character line with no leading controls) still holds; this is a class the fixture does not exercise.
- **Marker prefix (LOW):** the harness's `LEDGER-REFUSED id=<item>` test is `startswith`, so a refusal for `P011`
  would satisfy `P01`'s marker; no such id exists in the frozen ledgers, so the frozen configuration cannot bite.
- **F3/F4 (inherited, carried):** a writer inside the audited tree can write the child's stdout directly and forge
  `CLEAN`, removing the K4 refusal entirely (S85Sentinel F5 limit; r88 neither introduced nor worsened it); the
  status-failed and no-verdict branches still use `_stderr_tail` and can put a raw control byte in a cell (explicitly
  outside C2's limits).
- **Narrowed sentence:** *The FLAGFAIL detail is injective on the decoded TEXT, not on the raw stderr: a byte that is
  not valid UTF-8 and the literal spelling of that byte render identically. The 200-character excerpt is measured on
  the ESCAPED text, so the head keeps a leading exception name only while the leading bytes are printable — 25 or more
  leading control bytes (`\xNN` each) consume the head and the name can fall outside both ends. The harness's
  `LEDGER-REFUSED` marker is a prefix match, so a `P011`-style id would satisfy `P01`'s marker (no such id in the frozen
  ledgers).* The F3 forged-`CLEAN` fail-open and the sibling branches' raw stderr stay the declared F5/limit carries.
- **Carried to r89 (measured remediations):** bound the RAW payload first and escape the window (fixes F1 and F2
  together); use `surrogateescape` (or escape raw bytes as `_escape_record` does); exact id match in the harness
  marker; a forged-`CLEAN` fail-closed test for F3; `_stderr_tail` escaping for the sibling branches (F4).
