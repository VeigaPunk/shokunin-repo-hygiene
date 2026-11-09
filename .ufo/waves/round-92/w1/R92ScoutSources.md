# R92ScoutSources report (souji r92, wave w1, seat scout)

Status: complete. Verdict: FALSIFIES-WORDING (one sentence, the S355 anchor cell). Claim content not falsified.

Receipts: `.ufo/waves/round-92/w1/R92ScoutSources/` (`fetch-receipt.txt`, `check_s355.py`, `check_s355.out`).
Scratch: `/fast/scratch/hyaku/souji-r92/R92ScoutSources/` created for the live capture and deleted before yield.
Tools: none installed or upgraded. No subagents dispatched.

## 1. Fetch receipt and cmp

- URL: https://www.unicode.org/versions/latest/core-spec/chapter-3/
- Access date: 2026-11-09
- HTTP 200; final URL http://www.unicode.org/versions/Unicode18.0.0/core-spec/chapter-3/ (same versioned page the S355 row records)
- Size 428731 bytes; sha256 f9e158a640c88cb0aebf60e5f724ea4f957eca539c620fb1e161cb6c8f8fb22e
- Captured to scratch, then `cmp census/round-92/srcs/unicode-ch3.html <live>`: **IDENTICAL** (exit 0). Sha256 of the filed capture is the same.
- Tool hash confirmed for the record: tools/souji-record-agreement.py sha256 fc0e35c2... (matches the prereg).

## 2. S355 row check

- Row parses as **11 cells** when split on `|`; the header also has 11 columns; no `|` inside any cell.
- Sentence `Ill-formed code unit subsequences do not overlap with minimal well-formed code unit subsequences.`: **13 words**; **1 occurrence** in the whitespace-normalized tag-stripped text. It sits inside the **D86** definition paragraph (after "D86 Well-formed UTF-8 code unit sequence: ..."), so the section claim is correct.
- Anchor `id="G7404"`: **INCORRECT as stated.** In the capture, `id="G7404"` wraps the heading "3.9 Unicode Encoding Forms" (HTML offset 250884), not Table 3-7. G7404 is referenced 4 times, all to the §3.9 heading: a navigation link at offset 15641 (the "8 Surrogates" entry), a cross-reference "(See Section 3.9, Unicode Encoding Forms)" at 249697, the `id` at 250884, and its permalink at 250949. The "Table 3-7. Well-Formed UTF-8 Byte Sequences" caption sits under `id="G27506"` (caption at offset 278897).

### FALSIFIES-WORDING

- Sentence (corpus/SOURCES.md, row S355, anchor cell): `Table 3-7 anchor id="G7404" in the capture`
- Reproducer: `.ufo/waves/round-92/w1/R92ScoutSources/check_s355.py` → `check_s355.out` keys `G7404_wraps` ("...3.9 Unicode Encoding Forms...") and `table37_caption_text` / `nearest_id_before_table37` (`G27506`).
- Scope: this falsifies the row's anchor citation only. It is a source-locator sentence, not a claim predicate. The Table 3-7 content itself is verified below. The L1 should record the correct anchor (`id="G27506"`) as an amendment, not silently.

## 3. Knowledge entry vs Table 3-7

Table 3-7 rows, parsed from the capture (the table starts at offset 279018):

| Code points | First | Second | Third | Fourth |
|---|---|---|---|---|
| U+0000..U+007F | 00..7F | | | |
| U+0080..U+07FF | C2..DF | 80..BF | | |
| U+0800..U+0FFF | E0 | A0..BF | 80..BF | |
| U+1000..U+CFFF | E1..EC | 80..BF | 80..BF | |
| U+D000..U+D7FF | ED | 80..9F | 80..BF | |
| U+E000..U+FFFF | EE..EF | 80..BF | 80..BF | |
| U+10000..U+3FFFF | F0 | 90..BF | 80..BF | 80..BF |
| U+40000..U+FFFFF | F1..F3 | 80..BF | 80..BF | 80..BF |
| U+100000..U+10FFFF | F4 | 80..8F | 80..BF | 80..BF |

Entry statements against the table:

1. "C0, C1 and F5..FF never start a sequence": **consistent.** No table row has C0, C1 or F5..FF as a lead. The table does not say "never" literally; the fact is implied by the exhaustive lead column. Strict-decode check (below) agrees.
2. "after E0 the second byte must be A0..BF": **consistent**, row `U+0800..U+0FFF | E0 | A0..BF | 80..BF`.
3. "after ED it must be 80..9F": **consistent**, row `U+D000..U+D7FF | ED | 80..9F | 80..BF`.
4. "after F0 it must be 90..BF": **consistent**, row `U+10000..U+3FFFF | F0 | 90..BF | 80..BF | 80..BF`.
5. "after F4 it must be 80..8F": **consistent**, row `U+100000..U+10FFFF | F4 | 80..8F | 80..BF | 80..BF`.
6. Rationale clauses (E0 80..9F overlong; ED A0..BF surrogate; F4 90+ beyond U+10FFFF): arithmetic consequences of the table, **consistent**.
7. D86 quote in the entry: verbatim match of the capture sentence (13 words, one occurrence).

Decode cross-check (`check_s355.py`, `decode_table_mismatches`): for every one-byte input (256), every two-byte input (65 536), every three-byte input (16 777 216), and every four-byte input with lead F0..FF and bytes 2..4 drawn from a boundary set (17 535 232 candidates in total), "strict UTF-8 decode yields exactly one character" equals "matches one Table 3-7 row": **0 mismatches**. Limit: the four-byte check samples bytes 3 and 4 at boundaries {00,7F,80,8F,90,9F,A0,BF,C0,C1,F4,F5,FF}, not exhaustively. This supports the C2 wording "strict decode = every Table 3-7 row"; it does not falsify it.

## 4. Reject sample (proposed; grounds nothing this round claims)

- Source: The Unicode Standard 18.0.0, Chapter 3, §3.9, D93b "Maximal subpart of an ill-formed subsequence" (same chapter; the U+FFFD substitution section).
- URL: https://www.unicode.org/versions/latest/core-spec/chapter-3/ (final: .../Unicode18.0.0/core-spec/chapter-3/)
- Access date: 2026-11-09 (same capture, sha256 f9e158a6...)
- Quote (18 words): "This definition of the maximal subpart is used in describing how far to advance processing when making substitutions"
- Locator: §3.9 D93b; capture text census/round-92/srcs/unicode-ch3.txt, normalized offset 145946; occurs once.
- Reason it grounds nothing here: D93b governs how far a U+FFFD substitution advances. The lane tool escapes bytes (`backslashreplace`, see tools/souji-record-agreement.py lines 212, 285, 419–420, 674, 695) and never substitutes U+FFFD. The cut rule is Table 3-7 well-formedness, not maximal-subpart advance. No claim in the r92 wording uses U+FFFD.
- Flip condition: if the tool or any claim starts substituting U+FFFD for ill-formed bytes, or asserts that a cut lands on a maximal-subpart boundary, then D93b and Tables 3-8..3-11 become grounding and need a fresh located check before use.

## Verdict

- NO-FALSIFICATION of C2's Table 3-7 content (the table, the entry's five facts, and the strict-decode equivalence all agree).
- FALSIFIES-WORDING: the S355 anchor sentence `id="G7404"` as the Table 3-7 anchor (correct anchor: `id="G27506"`). Reproducer: `.ufo/waves/round-92/w1/R92ScoutSources/check_s355.py`.
- C1 is outside this seat's scope.
