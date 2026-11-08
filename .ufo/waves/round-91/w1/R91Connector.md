# R91Connector — sibling overlap, prior art, and the bounded r92 data-walk

Seat: R91Connector (connector, leaf — no dispatch). Lane `souji-shokunin`, lane base
`681f6c72b242d410d0e8654efadb2a1553fb111d`, instruments P1 `7fb865d8`, P2 `d287d3de`, freeze F `a703bcb7`
(lane tip at every observation in this report). Read-only on the lane: nothing committed, no git/jj state
touched, no filed instrument modified. Scratch `/fast/scratch/hyaku/souji-r91/R91Connector` deleted
before yield; every receipt copied to `.ufo/waves/round-91/w1/R91Connector/receipts/` first.

Method: read the frozen prereg, the lane's `corpus/knowledge/` frontier entries, `corpus/QUALITY.md`,
the `SCORECARD.md` Planned blocks r84-r91, the r90 non-author spot-check, `plans/round-91.md`, and the
sibling lanes' `corpus/QUALITY.md` + `corpus/SOURCES.md` + `corpus/knowledge/` under
`/home/vgpnk/Projects/` (read-only). Three probes, all read-only, all receipted: an invalid-lead cut
probe over the frozen tool's own helpers, a discrimination run of the r91 fixture against a
range-aware variant, and a line-model count on the S354 capture.

**Headline.** One real seam (F1): the C2 word *valid* is unbound — the filed tool and an RFC-conformant
variant both score `cases=15 tool_pass=15 before_pass=14`, so the fixture cannot tell them apart. No
number in either predicate moves. Everything else is locator/record hygiene, plus one explicit
contradiction with the scout's §2.

---

## 1. Overlap table — prior boundary / decoding / excerpt rules

| rule (as admitted) | first recorded | carrier | disposition after this round |
|---|---|---|---|
| a cell is escaped **before** it becomes a record field; one physical line | r55 (the numbering model) → r86 (a path field) → r88 (the K4 cell) | `corpus/knowledge/splitlines-line-model.md`, `machine-parsed-path-spelling.md` (r87), `one-escaped-diagnostic-line.md` (r88); Q159, Q163 | unchanged; r91 adds no clause and narrows none |
| the escape set is the **whole** `str.splitlines()` boundary list (CR, LF, CRLF, VT, FF, FS/GS/RS, NEL, LS, PS) | r88 | `one-escaped-diagnostic-line.md`; Q163 | unchanged |
| bound the **raw bytes first**, then escape | r89 (measured r88 by S88Sentinel F2) | `decode-escape-order.md`; Q164 | unchanged; this round keeps head-100/…/tail-99 of raw content |
| decode with `surrogateescape` so a bad byte keeps `\xNN` and a literal backslash is doubled | r89 | `decode-escape-order.md`; Q164 | unchanged |
| a byte and the **character that decodes to those bytes** take distinct spellings (`\x85` vs `\u0085`) | r90 (S90Reviewer2 F1) | `nel-byte-character-pair.md`; Q165 | unchanged; r91's rule only *preserves* this pair at a cut |
| **cut a raw window on UTF-8 sequence boundaries** (head backs off a partial sequence; tail advances past continuations whose lead the middle elided) | **r91 — new, no prior round recorded it** | `corpus/knowledge/utf8-window-sequence-boundary.md` (uncommitted at time of writing), Q166 (uncommitted), S354 | new layer; it narrows nothing above it |
| an undecodable byte in a **drift record** becomes U+FFFD and the schema accepts it | r40 | `drift-record-invalid-utf8-r40.md`; S253 | untouched — different reader, different decoder, no shared code path |

Chain, in one line: r55 (numbering) → r88 (cell escaping) → r89 (bound-first + injective decode) →
r90 (byte/character spelling pair) → r91 (sequence-boundary cut). Each round added a conjunct; none was
superseded. The only cross-entry seam this round exposes is **which line model a registry locator uses**
(r55 vs the new S354 row) — see F2.

## 2. Sibling-ownership verdict

Scanned every sibling lane's `corpus/QUALITY.md`, `corpus/SOURCES.md` and `corpus/knowledge/` under
`/home/vgpnk/Projects/` (19 lanes with a corpus). Three scopes named in the brief:

- **UTF-8 cut boundaries — NOT owned by any sibling.** No sibling registry or knowledge entry names
  RFC 3629 or a sequence-boundary cut. Nearest neighbours, all a different duty: `kake-shokunin`
  (`surrogateescape` for hashing file content under non-UTF-8 names), `mado-shokunin`
  (`portal-keyfile-bytes-r93.md`, byte-exact decode of a keyfile), `kama-shokunin` (r23: `surrogateescape`
  for lane log records), `chousa-shokunin` (`claim-record-fields-r33.md`, JSON escape *parsing*). None
  of them cuts an excerpt. **Route: souji keeps it; nothing to hand over.**
- **Escaped-detail injectivity — owned by souji only** (Q164/Q165/Q166). chousa's JSON escape row is a
  parser-side duty, not a renderer-side one. **No contested scope.**
- **Ledger row-width rules — same *class*, different registries, no shared file.**
  `kumitate-shokunin/corpus/knowledge/round-gate-registry-shape.md` (its own census `NF==13`) and
  `kengaku-shokunin/corpus/knowledge/registry-argv-and-flag-audit.md` (`columns == 8` on its instrument
  registry) both refuse a row of the wrong width; souji's `len(r) != 3` / `len(r) == 2` is its own r77
  four-column pointer ledger. **Verdict: no sibling owns it; do not route.** Adjacency note only — a
  shared criterion is premature because the shapes differ (souji's ledger *accepts* 3 or 4 columns and
  the question is which reading refuses which).

No sibling lane is doing this round's work, and nothing this lane does should be moved out.

## 3. Findings

### F1 — MEDIUM-HIGH, wording: *valid* is unbound; both readings of the sequence rule score 15/15

The frozen tool's `_utf8_seq_need` (`tools/souji-record-agreement.py:216`) tests **structure only**:

```
0xC0–0xDF → 2   0xE0–0xEF → 3   0xF0–0xF7 → 4   else 0
```

RFC 3629 §3 — the claim's own ground — excludes four of those shapes: `C0`/`C1` can only encode an
overlong, `E0 80..9F` and `F0 80..8F` are overlong, `ED A0..BF` is a UTF-16 surrogate, `F4 90..BF` is
above U+10FFFF, and §3's table states "the rows of the table are mutually exclusive, i.e., there is only
one valid way to encode a given character" (capture lines 208-210). §1's explicit list "The octet values
C0, C1, F5 to FF never appear" sits at capture line 131 — **outside** S354's declared scope ("§3's
sequence definition only"), which is itself a boundary worth knowing.

Measured (receipt `receipts/invalid-lead-probe.txt`, probe `probe2.py`, both copied here):

| payload, 201 bytes, sequence straddling the head cut at 100 | r91 filed tool (head) | r90 before-tool (head) |
|---|---|---|
| valid `C2 85` at 99 | `…xxxx` (both octets dropped) | `…xxx\xc2` |
| overlong `C0 80` at 99 | `…xxxx` | `…xxx\xc0` |
| overlong `C1 BF` at 99 | `…xxxx` | `…xxx\xc1` |
| overlong `E0 80 80` at 98 | `…xxxx` | `…\xe0\x80` |
| surrogate `ED A0 80` at 98 | `…xxxx` | `…\xed\xa0` |
| overlong `F0 80 80 80` at 97 | `…xxxx` | `…\xf0\x80\x80` |
| out-of-range `F4 90 80 80` at 97 | `…xxxx` | `…\xf4\x90\x80` |
| illegal lead `F5 80 80 80` at 97 | `…xxxx` | `…\xf5\x80\x80` |

Tail side (pair at 101/102): `_cut_tail` returns 103 (2-octet), 104 (3-octet), 105 (4-octet) for **every**
row of that table — i.e. the continuation of an *invalid* lead is advanced past, not kept, for all seven
invalid shapes.

The discrimination test (`receipts/range-aware-variant-fixture.txt`, variant
`receipts/tool_range_aware.py`, sha256 `c57aa224a8e526daae1c16ecf91976d524615c88e8bf5084f07df3ec329584f4`):
I patched **only** `_utf8_seq_need` to `0xC2–0xDF → 2, 0xE0–0xEF → 3, 0xF0–0xF4 → 4, else 0` — i.e. the
RFC-conformant reading, which *keeps* those bytes with their `\xNN` spellings — and ran the filed fixture
on it:

```
SUMMARY cases=15 tool_pass=15 before_pass=14
EXIT=0
```

identical to the filed tool. **The fixture cannot distinguish the two readings.** So:

- the prereg's clause "a continuation byte with no lead stays and keeps its `\xNN` spelling" and Q166's
  "an invalid continuation with no lead stays" are **asserted, not measured** — unbound in the Q154/Q156
  sense (neither reading carries a row);
- the tool's own docstring is directly false for seven shapes: `_cut_head` "Only a VALID split … is
  moved; an invalid lead byte stays and escapes as itself" — an invalid lead byte does not stay;
- **no number moves.** KFF11 uses the valid `C2 85`; all 15 cases pass on both readings; predicate (a)
  (b) (c) and controls (i)/(ii) are unaffected.

Cost of closing it: 2 fixture rows (head and tail with `C0 80`, expecting the retained spellings) + the
four range checks in `_utf8_seq_need` (~8 lines). One receipt each way. Because `tools/` and
`tests/fixtures/` are frozen this round, the in-round action is wording (name the predicate), the code
action is r92 — see §4 row 1.

### F2 — MINOR, locator: the S354 row's capture lines are LF-based and the row does not say so

Receipt: computed in §5's commands. The capture has **787 newlines and 14 form feeds**; LF gives 788
parts, `str.splitlines()` gives **801**. The quoted sentence sits at

- **LF lines 183-185** (what the registry row and the scout both wrote), and
- **`str.splitlines()` lines 186-188** (shift +3 from the three form feeds above it: LF lines 59, 115, 171).

**Explicit contradiction with R91ScoutSources §1/§2.** That report states "Byte shape of the capture:
787 newlines, 0 CRLF, 0 bare CR, 0 non-ASCII bytes, 14 form feeds" and then "the 'lines' in the registry
row are unambiguous" (scout's emphasis). It is *not* unambiguous: the scout counted LF lines and its own
byte census lists the 14 form feeds that make the splitlines index differ. This does not falsify any
sentence of C1 or C2 — it falsifies the scout's *unambiguous* sentence and reproduces the r54/r55 defect
("two numberings that must agree") in miniature. Cheapest repair: add "(LF-based)" to `S354`'s locator
cell and to the entry's `verified-at:`.

### F3 — NOTE, record hygiene: the r91 population's header is byte-identical to r90's

`cmp` on the first two lines of `census/round-90/c1-false-rows.tsv` and `census/round-91/c1-false-rows.tsv`
prints `IDENTICAL`. They describe "the r86 49-row population … plus two rows" and "the r81 25-row
population"; neither names the r90 LD2b row or the five r91 rows. The five new rows are described only in
their own final field. Not a falsification — I verified the prereg's number sentence independently:
prefix byte-equal (`bytes91[:len(bytes90)] == bytes90` → True), **58** data rows in r90 and **63** in r91
(2 leading comment lines in each; `'\n'` counts 60/65). Inherited from r90, so if a sibling reports it,
record it as carried state, not an r91 regression.

### F4 — NOTE, durability/ordering: at F neither `S354` nor the knowledge entry existed; the capture did

- `git cat-file -e a703bcb7:corpus/knowledge/utf8-window-sequence-boundary.md` → absent (rc 128);
- `git show a703bcb7:corpus/SOURCES.md | grep -c S354` → **0**;
- `census/round-91/srcs/rfc3629.txt` **is** in P1 and its sha256 is `a2a3a39457d30420c812f87a38cc2b9194832f6982ef17e619de7d816879d6a6`, 33856 bytes — equal to the row's cell.

The working tree now carries `M corpus/SOURCES.md`, `M corpus/QUALITY.md`, `?? corpus/knowledge/utf8-window-sequence-boundary.md`
(mtimes 13:20:07 / 13:20:07 / 13:19:59), and `census/round-91/records/` is still **untracked**. So C2's
"sourced claim" sentence becomes true only when the L1 commits those four paths. A0.8 names the wave dir;
the tracking duty must also cover `corpus/SOURCES.md`, `corpus/QUALITY.md`, `corpus/knowledge/…` and
`census/round-91/records/`.

### F5 — NOTE, precision: LD1c is 3-of-4 fields equal, not byte-identical

`census/round-91/c1-false-row-harness.py:433` appends
`P01\tFLEET\t-\tr91 LD1c identical duplicate (class and target equal)`; the frozen base row
(`census/round-77/c2-pointer-ledger.tsv:2`) is `P01\tFLEET\t-\toperator scope file under the fleet root,
not lane bytes`. The prereg's parenthetical `P01<TAB>FLEET<TAB>-` names exactly the three equal fields, so
the sentence is exact **if read with its parenthesis**; "IDENTICAL" alone overstates. No verdict moves —
the kill is on the duplicated id, which is equal.

### F6 — negative finding (saves a round): `_stderr_tail` needs no sequence rule

`_stderr_tail` (`tools/souji-record-agreement.py:335-353`) cuts a **decoded `str`** at 200 characters and
inserts a one-character ellipsis, so it cannot split a UTF-8 sequence and its bound is characters, not
octets. C2 STATED LIMITS (i) is correct for the right reason; r92 should not spend a claim on it.

## 4. r92 candidate list (bounded to r92; status + cheapest next measurement)

| # | candidate | carried since | status at r91 close | cheapest next measurement |
|---|---|---|---|---|
| 1 | bind F1's reading: head/tail rows for an invalid-but-structured lead (`C0 80`), tool keeps `\xc0\x80` | new (r91 F1) | unbound; both readings 15/15 | add 2 rows + 4 range checks in `_utf8_seq_need`; `python3 -B tests/fixtures/r92-k4-flagfail.py --tool … --before census/round-91/controls/c2-before-tool.py --work <empty>` — one run, and the r90/r91 arms must not move |
| 2 | the boundary **sweep** at every cut position (payload × h=1..200 × t=1..200) | r91 STATED LIMITS (iii) | unmeasured | one loop asserting "neither spelling, no orphan continuation, no growth" on two fixed payloads; 1 receipt |
| 3 | KFF13's scan semantics (false-fail on a docstring mention; false-green on `def _one_line (` with a space) | new (R91ExecC2Fixture §5) | reported; partially inside C2 STATED LIMITS (ii) (false-green only) | already measured by that seat; r92 needs only the *decision*: anchor the scan (`^\s*def _one_line\(` + call sites via `ast`) or narrow the clause |
| 4 | forged-`CLEAN` fail-open (S88Sentinel F3) | r91 Planned (C2), not frozen | unmeasured | 1 fixture case: writer prints `CLEAN` over a diverged tree; expect a K4 row |
| 5 | K4 record-level arms H2a-H2c (FORGED/REFUSED/no-verdict) | r91 Planned (C2) | readability debt, unmeasured | 3 counter rows |
| 6 | battery `--only` / `--expect-killed` stale defaults | r90 (as filed in r89) | carried | run the r91 battery with `--only r91` and no `--expect-killed`; record what it prints |
| 7 | `fleet:` symlink leg | r90 | carried | 1 population row |
| 8 | p2 basename, p3 punctuation lookahead, p7 `_regular` symlink leg, p8 `token_ok` hyphen marker | r89 (3 rounds) | carried | one clause-dropping mutant each, scored on r91's 63 rows **before** any row (Q162); this is 4 mutants, 1 battery run |
| 9 | pid-reuse, parent-before-child, termign-fork/p5-late-term, strace-robust settle | r84/r85 (**7 rounds**) | carried, never measured | each is one counter row; pid-reuse needs the starttime re-check separated from the kill |
| 10 | `_regular` pathspec framing, quarantine intro-blob digest, r79 gate re-measurement, check-4 300 s, r76 K03/K04, r17 240 s runners | r84 (7 rounds) | carried | **r79 gate re-measurement is one command on committed bytes** — take it first |
| 11 | C1 named unrowed surfaces: `_capture_ok` `m19`, `q1`/`q1b`, `line.isdigit()`, 4+-column and CRLF rows | r90 STATED LIMITS (iv) | unrowed **by claim** | score a clause-dropping mutant on the 63 rows first; a survivor needs a row, a kill does not |

Recommendation (bounded, one round): r92 takes **1 + 2** (both close a clause that is currently asserted
and both are one receipt each), plus **10's r79 gate re-measurement** because it is a single command.
Row 9 should be either measured or explicitly retired with a reason — seven consecutive carries is the
lane's oldest ladder and it has never had a receipt.

## 5. Dedup and unattacked loci

**Duplicates of a prior round** (report them as carried, not new):

- F2 is an *application* of r55's one-line-model rule (`splitlines-line-model.md`); the rule is not new.
- F3 duplicates the r90 population header state (the r90 file is equally stale).
- R91ExecC2Fixture's KFF13 finding is **not** a duplicate — but its false-green half is inside C2
  STATED LIMITS (ii) ("KFF13 is a static source scan, so a dynamic caller constructed outside the source
  text is not exhaustively excluded"). Only the false-**fail** direction and the spaced-`def` false-green
  are residue beyond the frozen limit. Recording the whole finding as new would overstate it.
- The scout's "occurrence count 1 only de-wraps" note duplicates r90 A4's offset lesson (`nel-byte-character-pair.md`
  quotes no offset for the same reason); it is a measurement note, correctly not filed as a defect.

**Loci this round does not attack** (named, so r92 does not rediscover them as gaps):

- `_escape_record` (path bytes, `:144`) — byte-based, unchanged, outside the claim (STATED LIMITS i).
- `_stderr_tail` — see F6.
- the invalid-lead shapes of F1 — asserted, no row.
- the every-cut-position sweep — STATED LIMITS (iii).
- the forged-`CLEAN` fail-open and the H2a-H2c arms — planned, not in the frozen predicate.
- C1's `_capture_ok` `m19`, `q1`/`q1b`, `line.isdigit()`, 4+-column and CRLF shapes — STATED LIMITS (iv).

## 6. FALSIFIES-WORDING

**Exact sentence I put under this heading** — `census/round-91/preregistration.txt`, C2 CLAIM:

> "`_cut_head` backs off a valid partial sequence; `_cut_tail` advances past continuations whose lead the
> middle elided; a continuation byte with no lead stays and keeps its `\xNN` spelling"

**Why it is a wording matter and not a number matter.** The word *valid* is doing no work: the tool's test
is "initial octet in C0-F7 with its continuation count", which admits overlongs, UTF-16 surrogates,
code points above U+10FFFF and the illegal `F5-F7` leads. For those shapes the continuation of an invalid
lead does **not** stay — `_cut_tail` advances past it (measured: 103/104/105 for 2/3/4-octet shapes) and
`_cut_head` elides the lead the r90 tool printed. The claim cites RFC 3629 §3 as its ground, and §3's
own table plus "only one valid way to encode a given character" (capture lines 208-210) is what makes
those shapes invalid — so the sentence is true only on a reading its own source excludes.

**Reproducers.**

- `.ufo/waves/round-91/w1/R91Connector/receipts/invalid-lead-probe.txt` (probe `probe2.py`): the eight-row
  table above, `_cut_head` / `_cut_tail` returns and both excerpt spellings.
- `.ufo/waves/round-91/w1/R91Connector/receipts/range-aware-variant-fixture.txt`: the range-aware variant
  scores `SUMMARY cases=15 tool_pass=15 before_pass=14` / EXIT 0 — the fixture does not discriminate.

**Strength.** Predicate (a) still prints `SUMMARY cases=15 tool_pass=15 before_pass=14` EXIT 0 on the
filed bytes; (b) and (c) and controls (i)/(ii) do not touch this code path. The falsification is of the
claim's *description* of its own cut rule, and of Q166's "an invalid continuation with no lead stays",
which is unmeasured. It is a narrowing, not a stop: the suggested amendment is to name the predicate —
"a structurally well-formed sequence (an initial octet 0xC0-0xF7 with its continuation count); a
continuation whose lead is absent or incomplete stays and keeps its `\xNN` spelling" — and to carry the
four range checks to r92 (§4 row 1).

**FALSIFIES-NUMBER: none.** Every number I re-derived agrees with the prereg: 63 rows = 58 byte-equal +
5 (`prefix-equal True`, data rows 58/63); population sha256 `fdc3d238…`; capture sha256 `a2a3a394…`,
33856 bytes; quote 25 words, occurrence count 1 (de-wrapped); tool sha256 `21e5c740…`; before-tool
sha256 `d095b52f…`.

## 7. Commands run (all read-only, all under my scratch or `-B`)

```
# population identity
python3 -B  # prefix-equal True; data rows 58 / 63; 2 comment lines each
# line model (F2)
t=open('census/round-91/srcs/rfc3629.txt',encoding='utf-8').read()
t.count('\n')            # 787      len(t.split('\n'))  # 788     len(t.splitlines())  # 801
# quote under both models
LF line of 'initial octet has the n higher-order' → 184   splitlines → 187   (file has 14 FF; 3 above the quote)
# F1 probes
python3 -B .ufo/waves/round-91/w1/R91Connector/probe2.py
python3 -B tests/fixtures/r91-k4-flagfail.py --tool <range-aware variant> \
  --before census/round-91/controls/c2-before-tool.py --work <empty>
# F4
git cat-file -e a703bcb7:corpus/knowledge/utf8-window-sequence-boundary.md   # absent
git show a703bcb7:corpus/SOURCES.md | grep -c S354                          # 0
```

## 8. Tooling / hygiene

No tool installed or upgraded; pacman untouched; no host sysctl touched; no git/jj mutation anywhere (the
only git commands were `cat-file`, `show`, `log`, `ls-tree`, `status --porcelain`, `rev-parse`). Wrote
only `R91Connector.md`, `R91Connector/` and my scratch; scratch deleted before yield.
