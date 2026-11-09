# R93ScoutSources — souji round 93 (scout, sources)

Seat: R93ScoutSources (scout). Lane: souji-shokunin, base 91c9bcb1041b18be154ca466ac3c047ac7862fe1.
Access date: 2026-11-09 (UTC 03:48). Verdict: **NO-FALSIFICATION** (source-level facts; no sentence of C1 or C2 falsified).

## 1. Fetch receipt and cmp verdict

- `curl -sSL https://encoding.spec.whatwg.org/` → HTTP 200, final URL `https://encoding.spec.whatwg.org/`, 591022 bytes.
- sha256 (live) `e1421f1791b202717883c452a6267129ce5fb3ca13652e5022a2b6d2a11fc262`
- sha256 (`census/round-93/srcs/encoding.html`) `e1421f1791b202717883c452a6267129ce5fb3ca13652e5022a2b6d2a11fc262`
- `cmp` → identical (exit 0). The live document has not changed since the round's capture, so the §8.1.1 decoder steps are unchanged (nothing to diff).
- Receipt text: `.ufo/waves/round-93/w1/R93ScoutSources/fetch-receipt.txt`. The fetched copy lived in scratch and was deleted.

## 2. S356 row check (corpus/SOURCES.md)

- The row is unique (`| S356 |` occurs once). The naive split on `|` gives 11 cells, and the line has 12 `|` characters (one per cell boundary), so no `|` sits inside a cell. The row parses as 11 cells. Row text: `.ufo/waves/round-93/w1/R93ScoutSources/s356_row.txt`.
- Quoted sentence in cell 5: `"If byte is 0xE0, then set UTF-8 lower boundary to 0xA0. If byte is 0xED, then set UTF-8 upper boundary to 0x9F."`
  - **22 words** (whitespace split). Confirmed.
  - **Occurs once** in the whitespace-normalized, tag-stripped capture text. Confirmed.
- Location: `id="utf-8-decoder"` appears exactly once, on the `<h4>` for §8.1.1 "UTF-8 decoder" (capture offset of the h4 is in the 3672 HTML line range). Confirmed.
- Cell 6 also quotes `utf-8-decoder` (the id), which is a 1-word quote and is not the sentence. Not a problem.
- "Last Updated": the capture reads `Last Updated 19 October 2026`. Matches the row's "Last Updated 19 October 2026". Confirmed.
- Cell 8 date `2026-11-09` and cell 9 `365d` are consistent with the prereg's "opened 2026-11-09 / recheck 365d". Confirmed.
- No cell-level discrepancies.

## 3. Entry-vs-source check: corpus/knowledge/utf8-cut-position-reference.md

Source (§8.1.1, `id="utf-8-decoder"`, quoted from the normalized text):

- Leads: `0xC2 to 0xDF Set UTF-8 bytes needed to 1.` / `0xE0 to 0xEF ... Set UTF-8 bytes needed to 2.` / `0xF0 to 0xF4 ... Set UTF-8 bytes needed to 3.` / `Otherwise Return error .`
- Boundaries: `If byte is 0xE0, then set UTF-8 lower boundary to 0xA0. If byte is 0xED, then set UTF-8 upper boundary to 0x9F.` and `If byte is 0xF0, then set UTF-8 lower boundary to 0x90. If byte is 0xF4, then set UTF-8 upper boundary to 0x8F.`
- Out-of-range: `If byte is not in the range UTF-8 lower boundary to UTF-8 upper boundary , inclusive: ... Return error .`
- Reset after each continuation: `Set UTF-8 lower boundary to 0x80 and UTF-8 upper boundary to 0xBF.`

Entry statement → source:

| Entry fact | §8.1.1 | Match |
|---|---|---|
| lead 0xC2..0xDF needs one continuation | `0xC2 to 0xDF Set UTF-8 bytes needed to 1.` | yes |
| 0xE0..0xEF needs two | `0xE0 to 0xEF ... Set UTF-8 bytes needed to 2.` | yes |
| 0xF0..0xF4 needs three | `0xF0 to 0xF4 ... Set UTF-8 bytes needed to 3.` | yes |
| any other lead is an error | `Otherwise Return error .` | yes |
| first continuation 0x80..0xBF except E0 lower 0xA0 | `If byte is 0xE0, then set UTF-8 lower boundary to 0xA0.` | yes |
| ED upper 0x9F | `If byte is 0xED, then set UTF-8 upper boundary to 0x9F.` | yes |
| F0 lower 0x90 | `If byte is 0xF0, then set UTF-8 lower boundary to 0x90.` | yes |
| F4 upper 0x8F | `If byte is 0xF4, then set UTF-8 upper boundary to 0x8F.` | yes |
| every later continuation 0x80..0xBF | `Set UTF-8 lower boundary to 0x80 and UTF-8 upper boundary to 0xBF.` (reset after each accepted continuation) | yes |
| a byte outside the current boundaries ends the attempt | `If byte is not in the range ... Return error .` | yes |

Result: every decoder fact the entry states matches §8.1.1 exactly, including the four boundaries. The entry's own derivation (the one well-formed sequence that can straddle a cut, "at most one", and the head/tail cut movement) is not a §8.1.1 statement. It is labeled as derived from S356 and S355, and I did not check S355, so I make no claim about it. [INFERENCE] only for that derived part.

## 4. Reject sample (one)

- **URL:** https://encoding.spec.whatwg.org/#utf-8-decoder
- **Access date:** 2026-11-09 (capture sha256 e1421f17…; the same bytes as the live fetch in §1).
- **Quote (21 words):** "A byte order mark has priority over a label as it has been found to be more accurate in deployed content."
- **Locator:** §8.1.1 "UTF-8 decoder", `id="utf-8-decoder"`, the first sentence of the section (capture offset 204059). The same sentence occurs a second time at offset 306772, under §14.2.1 "shared UTF-16 decoder"; the locator is the §8.1.1 occurrence.
- **Reason it grounds nothing r93 claims:** The sentence is about label and BOM precedence at the decode entry point, and it says the BOM handling is "not part of the UTF-8 decoder algorithm". The round's knowledge entry and the KFF19 reference cut are the byte-at-a-time decoder steps only. Neither C1 (counter edits to the false-row ledger) nor C2 (excerpt cut position) reads a BOM or a label. The S356 row's own scope excludes "BOM sniffing, labels".
- **Flip condition:** The sample becomes grounding if a claim or fixture is widened to the decode / UTF-8 decode entry point (BOM stripping or label precedence on input), or if the Living Standard moves the BOM rule into the §8.1.1 decoder steps. Either change requires re-rating the sample.

## 5. Falsification

- FALSIFIES-WORDING: none found.
- FALSIFIES-NUMBER: none found. The 22-word count, the single occurrence, the 11-cell row, and the 19 October 2026 date all match.
- NO-FALSIFICATION (source level): every §8.1.1 fact stated in the knowledge entry and the S356 quote matches the live and captured text.

## 6. Tooling and scope

- No tool installed or upgraded. The round needed none.
- No files written outside the seat dir and the report. Scratch `/fast/scratch/hyaku/souji-r93/R93ScoutSources/` (holds the fetched copy and the normalized text) is deleted before yield.
- Seat receipts: `.ufo/waves/round-93/w1/R93ScoutSources/` (`fetch-receipt.txt`, `s356_row.txt`, `s818_section_811.txt`, `s356_check.py`).

## Checks for the L1 to run (not run by this seat)

- The `s356_check.py` script re-derives the cell count, the 22-word quote, the single occurrence and the id match from `census/round-93/srcs/encoding.html` and `corpus/SOURCES.md`. Running it once is enough.
