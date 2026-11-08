# R91Scribe — round 91, wave 1 (scribe seat)

Lane: `souji-shokunin` (id souji), round 91. Seat: `R91Scribe` (scribe). Lane base `681f6c72b242d410d0e8654efadb2a1553fb111d`;
HEAD at start and end of this seat: `a703bcb760ecdb22ec7df06af3059f219ebb95cf` (F, the preregistration alone).
Write scope: `.ufo/waves/round-91/w1/R91Scribe/` and this report only. The lane was read read-only; no git/jj
mutation, no commit, no push, no edit of `census/round-91/`, `tests/fixtures/`, `tools/`, `corpus/`, `plans/`,
`.ufo/state/`, `.scratch/` or `.ufo/watchdog.log`. No tool was installed (none needed).

Deliverables (all ready to paste, no placeholder text):

| # | draft | path |
|---|---|---|
| 1 | S354 registry row (11 cells) | `.ufo/waves/round-91/w1/R91Scribe/draft-s354-row.md` |
| 2 | `corpus/knowledge/utf8-window-sequence-boundary.md` (40 lines) | `.ufo/waves/round-91/w1/R91Scribe/draft-knowledge-entry.md` |
| 3 | next QUALITY criterion (Q166, 5 cells) | `.ufo/waves/round-91/w1/R91Scribe/draft-quality-q166.md` |
| 4 | `## Mistakes` for `corpus/lessons/round-91.md` (M1, M2) | `.ufo/waves/round-91/w1/R91Scribe/draft-lesson-mistakes.md` |

Receipts: `quote-verification.txt` (S354 quote), `kff11-before-vs-after.txt` (KFF11 before/after cell),
`cut-edge-probe.txt` (the falsifier below), `tree-s354-row.txt` / `tree-q166-row.txt` (read-only copies of the
uncommitted working-tree drafts I found).

## FALSIFIES-WORDING

**Sentence (C2 CLAIM, `census/round-91/preregistration.txt`):** "The filed tool moves BOTH cuts to sequence
boundaries before decoding (`_cut_head` backs off a valid partial sequence; `_cut_tail` advances past continuations
whose lead the middle elided; a continuation byte with no lead stays and keeps its `\xNN` spelling), grounded on S354
(RFC 3629 §3: a sequence is an initial octet plus its continuation octets)."

**Reproducer:** `.ufo/waves/round-91/w1/R91Scribe/cut-edge-probe.txt`, case 2. Payload
`b"A"*101 + b"\xe0" + b"\x85\xc2\x85" + b"B"*96` (201 bytes; indices 101=`0xE0`, 102=`0x85`, 103=`0xC2`, 104=`0x85`).
The requested tail cut is index 102 (the `0x85` continuation of the invalid `0xE0` lead); `_cut_tail` returns 104,
which is the continuation octet of a VALID U+0085 (`C2 85` at 103-104) whose lead the advance itself elided. The
tail therefore starts on a continuation, the cut is NOT a sequence boundary, and the cell prints the raw-byte
spelling:

```
  len: 201 tail requested: 102 byte at cut: 0x85
  _cut_tail -> 104 (moved)
  cell: 'AAAA…\\x85BBBB…'
  cell count \x85: 1  \u0085: 0
```

This is the same collapse the claim says the repair removes: a character whose lead is elided prints exactly like a
raw `0x85`. It also violates the fixture clause the claim says KFF11 enforces ("the boundary case renders neither
spelling") if that clause is applied to this payload: `\x85` is present. The fixture does not carry this shape, so
**no predicate NUMBER moves** (KFF11 still reads `tool=pass before=fail`, `SUMMARY cases=15 tool_pass=15
before_pass=14`); this is a wording falsification under Amendment 59, not a number change. No stated limit covers it:
limit (iii) bounds the boundary case to "one payload at one cut position" and calls a sweep at other CUT POSITIONS an
attack item — this is a different PAYLOAD at the same cut position, and limit (i) says the repair covers
`_one_line_bytes`, which is the function probed.

Mechanism: `_cut_tail` computes `end = i - 1 + need` once, from the continuation run at the requested cut, and
returns it without checking that the octets it skips are continuations and without re-checking the new start. Case 3
of the same receipt shows the direct consequence: `b"A"*101 + b"\xe0\x85" + b"B"*98` skips `0x85` and `0x42` (`B`),
a non-continuation, so the cell keeps 97 of the payload's 98 `B`s. Case 2 shows the same skip landing on the
continuation of another sequence.

Second, narrower wording gap in the same sentence: `_utf8_seq_need` accepts `0xC0`/`0xC1` as 2-octet leads although
RFC 3629 §4 gives `UTF8-2 = %xC2-DF UTF8-tail` (capture lines 278-279). Cases 4 and 5 show an overlong `C0 85` pair
elided whole by the tail (case 4) and by the head (case 5); "backs off a **valid** partial sequence" is not enforced
strictly. This one does not collapse the Q165 pair in the probes (both spellings stay absent).

No C1 artifact was produced by this seat; nothing here touches C1.

## Draft 1 — S354 row (paste after S353 in `corpus/SOURCES.md`)

Row file: `.ufo/waves/round-91/w1/R91Scribe/draft-s354-row.md` (11 cells: id, source, kind `docs`, tier `A`, scope,
anchor, teaches, status `mined`, opened 2026-11-08, recheck `365d`, used-by
`corpus/knowledge/utf8-window-sequence-boundary.md`).

Quote verification, pasted commands and outputs (`quote-verification.txt`):

```
$ q="In a sequence of n octets, n>1, the initial octet has the n higher-order bits set to 1, followed by a bit set to 0."
$ printf "%s\n" "$q" | wc -w
25
$ printf "%s" "$q" | wc -c
115
$ printf "%s" "$q" | sha256sum
f51f5180cfb90120639ebc155c5d487a9d1fcbc7297e8c27062f59a743518442  -
$ tr -s "[:space:]" " " < census/round-91/srcs/rfc3629.txt | grep -o -F "$q" | wc -l
1
$ awk "NR>=183 && NR<=185" census/round-91/srcs/rfc3629.txt
   the remaining 7 bits being used to encode the character number.  In a
   sequence of n octets, n>1, the initial octet has the n higher-order
   bits set to 1, followed by a bit set to 0.  The remaining bit(s) of
$ curl -sSL --max-time 60 -o <scratch>/rfc3629.live.txt -w "HTTP=%{http_code} bytes=%{size_download}\n" \
    https://www.rfc-editor.org/rfc/rfc3629.txt
HTTP=200 bytes=33856
$ sha256sum <scratch>/rfc3629.live.txt census/round-91/srcs/rfc3629.txt
a2a3a39457d30420c812f87a38cc2b9194832f6982ef17e619de7d816879d6a6  <scratch>/rfc3629.live.txt
a2a3a39457d30420c812f87a38cc2b9194832f6982ef17e619de7d816879d6a6  census/round-91/srcs/rfc3629.txt
$ cmp <scratch>/rfc3629.live.txt census/round-91/srcs/rfc3629.txt && echo BYTE-IDENTICAL
BYTE-IDENTICAL
normalized-span==quote: True
```

25 words (≤25), occurrence count 1, capture lines 183-185, and the live URL re-serves the capture byte for byte.

## Draft 2 — knowledge entry (40 lines)

Path `.ufo/waves/round-91/w1/R91Scribe/draft-knowledge-entry.md`. It states the sequence-as-unit rule (RFC 3629 §3,
S354), why a raw-byte window must cut on a boundary, the `surrogateescape` interaction (`U+DC80–U+DCFF` → `\xNN`),
the head/tail repair as the RULE, a Boundary line, and a Gate block (URL, access date 2026-11-08, 25-word located
quote, admit tier A / `mined` / S354). The Boundary line names the measured residual from the falsifier above so the
entry does not assert what the r91 tool does not do.

## Draft 3 — QUALITY criterion Q166

Path `.ufo/waves/round-91/w1/R91Scribe/draft-quality-q166.md`. Rule: both cuts on UTF-8 sequence boundaries before
decoding; the head ends before the initial octet of a sequence the cut would split; the tail starts after the last
continuation of the sequence whose lead the middle swallowed **and re-checks the new start**; a continuation with no
lead stays as `\xNN`; the bound stays 202 octets. Test: the r91 fixture command (`KFF11 tool=pass before=fail`,
`SUMMARY cases=15 tool_pass=15 before_pass=14`, EXIT 0; the r90 tool as both arms `tool_pass=14 before_pass=14`,
EXIT 1). The lesson cell names the re-check as unrowed and points at the case-2 probe. The working tree already
carries an uncommitted Q166 draft (see Findings); mine differs in the re-check clause and the residual pointer.

## Draft 4 — `## Mistakes`

Path `.ufo/waves/round-91/w1/R91Scribe/draft-lesson-mistakes.md`. Two rows, both from
`corpus/lessons/round-90-verifier-spotcheck.md` §1 and §7:

- **M1** class: a cited path that does not exist (`census/round-90/claims.json` vs the real
  `.ufo/waves/round-90/claims.json`). Evidence: the spot-check; `git ls-tree -r 93c7e6dc -- census/round-90/claims.json`
  prints nothing while `git ls-tree -r 93c7e6dc -- .ufo/waves/round-90/claims.json` prints
  `100644 blob c85c1660…  .ufo/waves/round-90/claims.json`. Captured-by: the non-author spot-check (the pre-file gate
  resolves only ledger `artifact` cells under the wave dir, so prose citations are outside its check). Fix: resolve
  every cited path with `git ls-tree -r <tip> -- <path>` and require NON-EMPTY output (`ls-tree` exits 0 on no match).
- **M2** class: an unowned count (7/12 vs the prereg's 6/12 vs the addendum's 5/12; no definition named). Evidence:
  the spot-check; `.ufo/waves/round-90/w1-spec.json` `items[].role`. Fix: name the definition and print the
  recomputation; the pasted command prints `seats 12 four-role 5 prereg 6 ATTACK_ROLES 7` (re-run by this seat).

## Findings

- **F1 (HIGH, falsifies C2 wording).** `_cut_tail` does not re-check its new start (filed tool sha256
  `21e5c740…`): an invalid multi-octet lead followed by a valid sequence at the cut leaves the tail on a
  continuation and the cell prints `\x85` (`cut-edge-probe.txt` case 2). Minimal repair shape (not applied, instruments frozen): loop the advance while
  `raw[t]` is a continuation and its lead lies before `t`, so the tail can only stop on a non-continuation or on a
  continuation with no lead. A fixture case carrying this payload (e.g. KFF14) would fail the filed tool today and
  bind the repair.
- **F2 (MEDIUM, wording gap).** `_utf8_seq_need` accepts `0xC0`/`0xC1` (and the coarse `0xE0`/`0xF0` ranges) as
  leads although RFC 3629 §4's ABNF is stricter (`UTF8-2 = %xC2-DF UTF8-tail`, `UTF8-3 = %xE0 %xA0-BF UTF8-tail` …,
  capture lines 278-291). Cases 4-5 show an overlong `C0 85` pair elided whole by the tail (case 4) and by the head
  (case 5); the head's "valid partial sequence" is therefore structural, not RFC-valid. No pair collapse measured.
- **F3 (LOW, record).** The uncommitted working-tree Q166 row ends its criterion with the clause "the bound stays
  202 octets and shortens only." — a truncated sentence (`tree-q166-row.txt`). If the L1 keeps the tree row, the
  clause needs completing; my draft replaces it.
- **F4 (LOW, record).** The uncommitted working-tree entry `corpus/knowledge/utf8-window-sequence-boundary.md` is 53
  lines, over the 40-line bound this seat was given; it also states the repair without the measured residual. My
  draft is 40 lines and carries the residual.
- **F5 (NOTE, agreement).** The uncommitted working-tree S354 row agrees with my verification on every immutable
  cell (id, source bytes/URL/sha/capture, kind `docs`, tier `A`, status `mined`, opened 2026-11-08, recheck `365d`,
  used-by) and on the quote (25 words, occurrence 1, capture lines 183-185); it differs only in scope/anchor detail
  and teaches wording. My draft adds the live re-open and the octet-table locator.

## Working-tree state observed (read-only, not mine)

At seat start and at seat end, `git status --porcelain` reads exactly:

```
 M corpus/QUALITY.md
 M corpus/SOURCES.md
?? census/round-91/records/
?? corpus/knowledge/utf8-window-sequence-boundary.md
```

These are other seats'/the L1's uncommitted bytes; I did not edit, stage or revert them. `census/round-91/records/`
holds `c1-after.txt`, `c2-after.txt`, `c2-k4-regression.txt`, `c2-variants-r91.txt`; the `c2-after.txt` receipt reads
`SUMMARY cases=15 tool_pass=15 before_pass=14`, EXIT 0, and `c2-variants-r91.txt` reads `SUMMARY variants=3
fixture=r91 detected=3`, EXIT 0.

## Out of scope / not done

- No C1 measurement, no C2 predicate re-run as evidence (the filed receipts are the evidence; my probes target the
  wording, not the numbers).
- No repair of `tools/souji-record-agreement.py`, no fixture case added, no amendment written: instruments are frozen
  and the L1 owns `plans/round-91.md`.
- No commit, push, or git/jj mutation anywhere; no fleet-root or sibling-lane file touched.
- Scratch `/fast/scratch/hyaku/souji-r91/R91Scribe/` was created for the live re-fetch and the probes and is deleted
  before this report is final; the receipts were copied into the seat dir first.
- No tool installed or upgraded.
