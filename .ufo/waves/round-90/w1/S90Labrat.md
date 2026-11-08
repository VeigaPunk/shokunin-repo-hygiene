# S90Labrat — round 90 labrat probe: byte/character spelling collisions in the K4 decode+escape pipeline

Seat S90Labrat (leaf, attack band; no subagents, no peer messages). Measured at lane rev
`fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f` (F, the preregistration alone; lane base `bd760432df2cc3ba6c5f1ccc540b050fe2ac09e2`).
Python 3.14.8, `sys.getfilesystemencoding()` = utf-8. Sweep wall time 0.053 s + 0.178 s + 0.432 s = 0.66 s, plus 2.48 s for the
full-Unicode closure (well under the 300 s bound). No tool installed or upgraded. No lane file edited, no git/jj mutation; receipts
are in `.ufo/waves/round-90/w1/S90Labrat/`, scratch `/fast/scratch/hyaku/souji-r90/S90Labrat/` deleted before yield.

Convention: strings shown as Python `repr` in backticks — `\x85` is the four characters backslash,x,8,5; a bare `\x85` in prose is
the same four characters, never the byte.

## 0. Objects measured (sha256, read-only from the lane)

| role | path | sha256 |
|---|---|---|
| after: filed r90 tool | `tools/souji-record-agreement.py` | `d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561` |
| before: r89 filed bytes | `census/round-90/controls/c2-before-tool.py` | `f6fce6d147165d1baf3d8d0343f46c1ab913b23947f3edaa28b61cdd6caa18dd` |
| fixture (read, NOT run) | `tests/fixtures/r90-k4-flagfail.py` | `d44172132f0a0c707d47e9522df8502f8d84859eb3e82d13e09809450c94aeaa` |

Provenance checks (read-only git): `git show bd760432…:tools/souji-record-agreement.py | sha256sum` = `f6fce6d1…` — the "before"
control is exactly the lane-base tool bytes; `git show HEAD:tools/souji-record-agreement.py | sha256sum` and the working-tree file
both = `d095b52f…`. `has_one_line` at import: `False` (after), `True` (before).

Method: each arm was copied to scratch, the copy's sha256 asserted equal to the lane file, and only the copy was loaded with
`importlib` (`probe.py` asserts this before every arm load). All lane accesses were reads.

## 1. Exhaustive spelling map (128 single bytes × 128 code points, per arm)

Domains verified, not assumed:

- all 128 single bytes `0x80..0xFF` are invalid UTF-8, and `_decode_record` maps each to exactly one surrogate
  `U+DC80..U+DCFF` in the same order (`all_128_single_bytes_invalid->surrogate->\xNN: True` on both arms);
- all 128 code points `U+0080..U+00FF` encode as a 2-byte `C2`/`C3` sequence (`c2 80..bf` for `U+0080..U+00BF`, `c3 80..bf` for
  `U+00C0..U+00FF`).

### Table A — what each source spells

| arm | 128 raw single bytes `0x80..0xFF` | 127 of the code points | `U+0085` | distinct spellings of the 256 sources |
|---|---|---|---|---|
| **after** | `\x80` … `\xff`, one-to-one (`b` ↦ `\xNN`) | the character itself (passthrough) | `\u0085` | **256 / 256** |
| **before** | `\x80` … `\xff`, identical to after | the character itself (passthrough) | `\x85` | **255 / 256** |

The 127 passthrough characters are `U+0080..U+0084` and `U+0086..U+00FF`. Full 513-row receipt: `spelling-table.tsv`.

### Table B — pairs that render identically (byte vs code point)

| arm | identical cross-domain pairs | spelling |
|---|---|---|
| **after** | **0** | — |
| **before** | **1**: raw byte `0x85` ↔ CHARACTER `U+0085` | `\x85` (4 chars) |

No intra-domain duplicates on either arm (128 distinct byte spellings; 128 distinct character spellings). The cross table was also
computed over **all 256 bytes `0x00..0xFF`** × the 128 code points: after 0 pairs, before 1 pair (same one). (The ASCII bytes
`0x00..0x7F` cannot pair with this character range at all: the character side starts at `U+0080`.)

### Table C — delta

| source | before | after |
|---|---|---|
| `U+0085` | `\x85` | `\u0085` |
| every other one of the 255 sources | — | byte-for-byte identical |

`changed_sources=1`, `flipped_to_distinct=1`, `new_collisions=0`.

### Table D — the frozen KFF9/KFF10 payloads through the helper the FLAGFAIL branch calls (`_one_line_bytes`)

Payloads exactly as `tests/fixtures/r90-k4-flagfail.py:69-70`: `b"fatal: nel \xc2\x85 marker\n"` (KFF9) and
`b"fatal: nel \x85 marker\n"` (KFF10). These are the same bytes the tool's `FLAGFAIL` branch base64-decodes and hands to
`_one_line_bytes` (filed tool line 406).

| arm | KFF9 cell | KFF10 cell | cells differ | each one physical line |
|---|---|---|---|---|
| **after** | `'fatal: nel \\u0085 marker\\n'` — 1× `\u0085`, 0× `\x85`, no raw NEL | `'fatal: nel \\x85 marker\\n'` — 1× `\x85`, 0× `\u0085`, no raw NEL | **yes** | yes |
| **before** | `'fatal: nel \\x85 marker\\n'` | `'fatal: nel \\x85 marker\\n'` | **no** | yes |

On the r89 bytes the two materially different delegated stderrs share one cell (KFF9 fails its own check and the pair check);
on the r90 bytes they are distinct cells, each with exactly one spelling and zero of the other. This reproduces the claim's
pre-freeze control content at the helper level. I did **not** run the fixture end-to-end (§6).

## 2. Boundary cases (both arms unless stated)

1. **Valid UTF-8 character above U+07FF.** Decode-first holds: the character never decomposes into bytes. `U+0800` (`e0 a0 80`) →
   `'ࠀ'`; `U+4E2D` → `'中'`; `U+1F600` (4-byte) → `'😀'` — passthrough. `U+2028`/`U+2029` → `\u2028`/`\u2029` (unchanged in both arms).
   1935 valid code points in `U+0080..U+FFFF` have byte `0x85` inside their UTF-8 encoding; **the only one that does not pass
   through is `U+0085` itself** — e.g. `U+0105` (`c4 85`) → `'ą'`, never `\x85`.
2. **A lone continuation byte.** `0x85` → `\x85`; `0x80` → `\x80`; `0xbf` → `\xbf`; truncated lead `0xC2` → `\xc2`; `0xC2` + ASCII
   `A` → `\xc2A` (per byte, no false decode). All 1006 distinct truncated prefixes of `0x85`-bearing sequences escape per byte.
   Same on both arms.
3. **A surrogate already in the input (`U+DC85` as text).** `_escape_text("\udc85")` = `\x85` — **identical to the raw byte `0x85`
   spelling, on BOTH arms** (likewise `U+DC80`→`\x80` … `U+DCFF`→`\xff`; 128 identities `U+DC80..U+DCFF` ↔ raw bytes `0x80..0xFF`).
   This is a residual non-injectivity of `_escape_text` **as a function on arbitrary `str`**, unchanged by r90, and it is outside
   the pipeline's reachable inputs: `_decode_record` = `raw.decode("utf-8", "surrogateescape")` produces `U+DC85` only for the
   invalid raw byte `0x85`; the other two `_escape_text` feeders (filed lines 396 and 411) receive `backslashreplace`-decoded text,
   which yields ASCII `\xNN` for an invalid byte (verified: no lone surrogate for any byte `0x80..0xFF`) and passes a valid `U+0085`
   as the character (after: `\u0085`). No feeder passes lone surrogates. So case 3 does not falsify C2's wording (raw byte vs
   character) but bounds it: injectivity is a property of the pipeline, not of `_escape_text` alone.
4. **An empty cell.** `_escape_text(_decode_record(b""))` = `''` (0 chars) on both arms; `_one_line_bytes(b"")` = `no stderr` on both.
   No non-empty input in the swept domain escapes to the empty string (0 hits), so the empty cell is unique.

## 3. Closure checks beyond the required sweep

- **Length-2 unique decodability** over the same 256-token set: after 65536/65536 distinct outputs, 0 colliding; before 65025
  distinct, 509 colliding outputs = **514 unordered colliding sequence pairs**, every one of the form
  (`byte 0x85` | `char U+0085`) + X or X + (`byte 0x85` | `char U+0085`). The single token collision was the sole generator; the
  repair removes all derived identities.
- **Prefix-freeness**: 0 violations on both arms (no token spelling is a prefix of another), so length-2 unique decodability plus
  prefix-freeness implies unique decodability for every concatenation length.
- **Full-repertoire cross-check**: all 1,112,064 non-surrogate code points against all 256 raw single-byte spellings — after
  **0** identities, before exactly **1** (`U+0085` ↔ `0x85`). Qualification: for `cp < 0x80` the raw byte and the code point are
  the *same datum* (`0x41` is `U+0041`), so those self-identities are excluded as noise; no exclusion applies to any byte
  `0x80..0xFF` (a raw byte there is never the character's own UTF-8 encoding). Also **0 physical-line violations** for the escaped
  output of every code point, per arm: `_escape_text` output is always one line over the whole repertoire.
- **Line-boundary census** (embedded test `("a"+ch+"b").splitlines()` — a single-char test is invalid because a trailing break
  yields one element; `probe2`'s `SPLITLINES` line used the invalid form and is superseded by this one): exactly 10 embedded
  splitters — `U+000A U+000B U+000C U+000D U+001C U+001D U+001E U+0085 U+2028 U+2029`. In `U+0080..U+00FF` only `U+0085`.
  The `U+000B/U+000C/U+001C..U+001E` members are `< 0x20` and already `\xNN`-escaped in both arms, so `U+0085` was the only C1
  character needing, and the only one having, a spelling rule.
- **Dead-helper check** (`grep -c 'def _one_line('`): filed **0** (and 0 matches for `_one_line(`; `_one_line_bytes` appears only at
  its def line 216 and its one call site line 406; module imports cleanly, `hasattr(module, "_one_line")` = False). Before: 1 def
  at line 297 and **0** call sites — dead in the r89 bytes too.

## 4. Residual identities outside the swept domain (disclosed, not new, not caused by r90)

- **Elided middle** (prereg C2 stated limit ii): `_one_line_bytes(limit=200)` keeps 100 head + 99 tail raw bytes and inserts one
  `U+2026`. Two >200-byte stderrs identical in head and tail and differing only in the dropped middle render identically —
  demonstrated: 249-byte `A*100 B*50 C*99` and 202-byte `A*100` + `e2 80 a6` + `C*99` yield the same cell on both arms; a
  tail-changed input yields a different cell. Identical on both arms.
- **Marker-vs-data cannot add a cross-truncation identity**: a window carrying the marker at the join plus 99 tail chars needs
  ≥202 raw bytes, so any input that would spell the truncated cell verbatim is itself truncated by the same rule.
- `_escape_record` (path bytes, the claim's limit i) was not probed; it is unchanged and byte-based per the claim.

## 5. Verdict (falsifiable)

**The r90 repair makes exactly ONE pair go from identical to distinct: raw byte `0x85` ↔ CHARACTER `U+0085` (`\x85` on both arms →
`\x85` vs `\u0085`). Not more.** Evidence: (a) 0 cross-domain identical pairs remain on the after tool over the exhaustive 128×128
table, the all-256-byte cross table, and the full 1,112,064-code-point cross-check; (b) exactly 1 of the 256 sources changes
spelling and it is `U+0085`; (c) 0 new collisions at token or length-2 composition level; (d) all 128 byte spellings are
byte-for-byte unchanged; (e) no prefix-freeness violation and no line-splitting escape appears. Falsifiers looked for and not found:
a second after-arm cross pair; a spelling change on any source other than `U+0085`; a collision of the new `\u0085` with
`\u2028`/`\u2029` or with any passthrough; a non-prefix-free token pair. The one token collision was also the sole source of the
514 derived length-2 identities, all of which vanish.

Scope: this is an independent probe of the spelling map, **not** a run of the C2 predicate `tests/fixtures/r90-k4-flagfail.py`
(other seats measure that); it neither confirms nor replaces `cases=12 tool_pass=12 before_pass=10`. It also does not touch C1.

## 6. Evidence chain — commands and exact tails

```
$ sha256sum tools/souji-record-agreement.py census/round-90/controls/c2-before-tool.py tests/fixtures/r90-k4-flagfail.py
d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561  tools/souji-record-agreement.py
f6fce6d147165d1baf3d8d0343f46c1ab913b23947f3edaa28b61cdd6caa18dd  census/round-90/controls/c2-before-tool.py
d44172132f0a0c707d47e9522df8502f8d84859eb3e82d13e09809450c94aeaa  tests/fixtures/r90-k4-flagfail.py

$ git rev-parse HEAD
fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f
$ git show bd760432df2cc3ba6c5f1ccc540b050fe2ac09e2:tools/souji-record-agreement.py | sha256sum
f6fce6d147165d1baf3d8d0343f46c1ab913b23947f3edaa28b61cdd6caa18dd  -
$ git show HEAD:tools/souji-record-agreement.py | sha256sum
d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561  -
$ git status --porcelain
 M SCORECARD.md
 M corpus/README.md
 M corpus/SOURCES.md
?? census/round-90/records/c1-after.txt
?? census/round-90/records/c2-after.txt
?? census/round-90/records/prefreeze-c1-both.txt
?? census/round-90/srcs/tr13.html
?? corpus/knowledge/nel-byte-character-pair.md
?? plans/round-90.md
   (pre-existing working-tree changes of other seats; not read, not touched by this seat)

$ grep -c 'def _one_line(' tools/souji-record-agreement.py
0
$ grep -n '_one_line(' tools/souji-record-agreement.py
(none)
$ grep -n '_one_line_bytes' tools/souji-record-agreement.py
216:def _one_line_bytes(raw: bytes, limit: int = 200) -> str:
406:        return (f"the index-flag read failed ({_one_line_bytes(raw)}); "
$ grep -c 'def _one_line(' census/round-90/controls/c2-before-tool.py
1
$ grep -n '_one_line(' census/round-90/controls/c2-before-tool.py
297:def _one_line(text: str, limit: int = 200) -> str:
   (zero call sites)
```

`python3 -B probe.py` (0.053 s, EXIT 0) — arms, sweep, delta:

```
ARMS {"after": {"file_sha256": "d095b52f…", "has_one_line": false,
                "escape_text_src_sha256": "810133c8007a453c1cf1732400c14aeffb92c1dc5ea4075071a8c1188b5a0fbb"},
      "before": {"file_sha256": "f6fce6d1…", "has_one_line": true,
                "escape_text_src_sha256": "57cebc263c5a4ca553ad6a8e387841addd9550b6de1a8cca674dbf459ed05762"}}
ARM after n_bytes=128 n_chars=128 cross_pairs=0 shared_spellings=0 distinct=256
ARM before n_bytes=128 n_chars=128 cross_pairs=1 shared_spellings=1 distinct=255
  PAIR 0x85   U+0085   -> '\\x85'
  SHARED '\\x85' <- byte:0x85,char:U+0085
DELTA changed_sources=1
  CHANGED char:U+0085  before='\\x85' after='\\u0085'
PAIR-DELTA before=1 after=0 flipped_to_distinct=1 new_collisions=0
  FLIPPED 0x85 U+0085
```

`python3 -B probe2.py` (0.178 s, EXIT 0) — all-256 cross table, KFF replication, composition, surrogate-text, empty:

```
PY 3.14.8 fsenc=utf-8
ARM after copy=/fast/scratch/hyaku/souji-r90/S90Labrat/copy-after.py sha256=d095b52f…
ARM before copy=/fast/scratch/hyaku/souji-r90/S90Labrat/copy-before.py sha256=f6fce6d1…
CROSS-ALL after pairs=0
CROSS-ALL before pairs=1 0x85/U+0085='\\x85'
KFF after KFF9=True KFF10=True pair_ok=True
   KFF9  cell='fatal: nel \\u0085 marker\\n'
   KFF10 cell='fatal: nel \\x85 marker\\n'
KFF before KFF9=False KFF10=True pair_ok=False
   KFF9  cell='fatal: nel \\x85 marker\\n'
   KFF10 cell='fatal: nel \\x85 marker\\n'
COMPOSE after pairs=65536 two_token_collisions=0 one_vs_two=0
COMPOSE before pairs=65025 two_token_collisions=509 one_vs_two=0
SURROGATE-TEXT after identities=128 all_identical=True first=0x80 last=0xff
SURROGATE-TEXT before identities=128 all_identical=True first=0x80 last=0xff
EMPTY after nonempty_inputs_escaping_to_empty=0 empty_input_escape='' one_line_bytes_empty='no stderr'
EMPTY before nonempty_inputs_escaping_to_empty=0 empty_input_escape='' one_line_bytes_empty='no stderr'
```

`python3 -B probe3.py` (0.432 s, EXIT 0) — line census, 0x85-bearing chars, truncation, prefix-freeness:

```
SPLITLINES-V2 embedded_splitters=10 U+000A U+000B U+000C U+000D U+001C U+001D U+001E U+0085 U+2028 U+2029
SPLITLINES-V2 in_U+0080..U+00FF=U+0085
CHARS-CONTAINING-0x85 count=1935
  ARM after passthrough_all=False deviations=[(133, 'c285', '\\u0085')]
  ARM before passthrough_all=False deviations=[(133, 'c285', '\\x85')]
TRUNCATED 0x85-bearing prefixes=1006 all_per_byte_escaped=True
TOKENS after n=256 distinct_len1=256 distinct_len2=65536 prefix_violations=0 len2_colliding_outputs=0 len2_colliding_pairs=0
TOKENS before n=256 distinct_len1=255 distinct_len2=65025 prefix_violations=0 len2_colliding_outputs=509 len2_colliding_pairs=514
```

`probe4` (truncation identity, EXIT 0): `p1(249 B)==p2(202 B, ellipsis at join): True`, `p1==p3(tail changed): False`, both arms.
`probe5` (full Unicode, 2.48 s, EXIT 0):

```
BYTE-SPELLINGS after=256 before=256
UNICODE after codepoints=1112064 byte_collisions=0  line_violations=0
UNICODE before codepoints=1112064 byte_collisions=1 U+0085<->0x85('\\x85') line_violations=0
```

Receipts in `.ufo/waves/round-90/w1/S90Labrat/` (`SHA256SUMS` there): `probe.py`, `probe2.py`, `probe3.py`, `probe-out.txt`,
`probe2-out.txt`, `probe3-out.txt`, `probe4-out.txt`, `probe5-out.txt`, `probe-results.json` (full 513-row map),
`probe3-results.json`, `spelling-table.tsv`, `copy-after.py` (`d095b52f…`), `copy-before.py` (`f6fce6d1…`).

## 7. What I could NOT check

- The frozen C2 predicate/fixture was not run end-to-end: the fake-writer subprocess framing, the MISMATCH-row parsing and the
  `SUMMARY cases=12 tool_pass=12 before_pass=10` number belong to other seats. My KFF9/KFF10 result is at the `_one_line_bytes`
  helper level with the fixture's exact payload bytes.
- `_escape_record` (path bytes) not probed (outside this seat; the claim states it unchanged).
- I did not brute-force the full cross product of all 1.1M code points against all 1.1M code points; I did the full code-point range
  against the 256 raw-byte spellings, plus the byte sweep against `U+0080..U+00FF`, plus all 1935 code points whose encoding
  contains `0x85`.
- No real delegated stderr was exercised; all inputs were constructed. No network, no host service, no credentials touched.
- The lane working tree carries other seats' modifications/untracked files (`SCORECARD.md`, `corpus/*`, `census/round-90/records/*`,
  `plans/round-90.md`); I neither read nor wrote them beyond the `git status` listing above.

## 8. Scratch / tooling / write scope

- Wrote only this report and `.ufo/waves/round-90/w1/S90Labrat/*`; scratch `/fast/scratch/hyaku/souji-r90/S90Labrat/` removed at
  yield (nothing left behind).
- No git/jj mutation anywhere; no fixture repo created (nothing needed `git -C`); no pacman, no installs (Python 3.14.8 was
  already present); no sibling-lane or fleet-root file touched.
