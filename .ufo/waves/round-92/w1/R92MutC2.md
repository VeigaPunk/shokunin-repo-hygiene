# R92MutC2 — C2 forgery sweep: 8 one-edit forgeries of the filed tool vs the r92 fixture

Seat: R92MutC2 (mutation-tester). Filed tool `tools/souji-record-agreement.py`
(sha256 fc0e35c208331de8ce568de3543b330c470e0a80336652f94d575dc242137a75).
All forgeries are one text edit each applied to a scratch copy in
`/fast/scratch/hyaku/souji-r92/R92MutC2/`; the lane was never edited (post-run
hashes re-verified: filed tool fc0e35c2…, fixture 2c9bd76c…, r91 tool 21e5c740…).
Each forgery was run through the r92 fixture with the r91 tool as `--before`:
`python3 -B tests/fixtures/r92-k4-flagfail.py --tool <forgery> --before
census/round-92/controls/c2-before-tool.py --work <empty>`.

Positive control (filed tool): rc=0 `SUMMARY cases=20 tool_pass=20 before_pass=16`.
Negative control (r91 tool): rc=1 `tool_pass=16 before_pass=16`, fails KFF14/KFF15/KFF16/KFF18.
Fixture receipts: `.ufo/waves/round-92/w1/R92MutC2/fixture_<name>.txt` and
`forgery_table.tsv`. Method/artifact: `gen_forgeries.py`, `run_forgeries.py` (same dir).

## Forgery table (edit, rc, tool_pass, failing cases)

| name | required edit | rc | tool_pass | failing cases | verdict |
|---|---|---|---|---|---|
| A_window3 | `_straddling_sequence` search window 3 instead of 4 bytes back | 0 | 20/20 | none | EQUIVALENT mutant (see analysis) |
| B_leadtable | strict decode replaced by a lead-byte range table missing E0/ED/F0/F4 second-byte restrictions | 1 | 19/20 | KFF16 | REJECTED |
| C_surrogatepass | decode with `surrogatepass` | 0 | 20/20 | none | SURVIVES — gap (see below) |
| D_len_ge1 | `len(...) == 1` relaxed to `>= 1` | 0 | 20/20 | none | SURVIVES — gap (see below) |
| E_head_fwd | head cut moved forward instead of back (`seq[0]`→`seq[1]`) | 0 | 20/20 | none | SURVIVES — gap (see below) |
| F_tail_back | tail cut moved back instead of forward (`seq[1]`→`seq[0]`) | 1 | 19/20 | KFF11 | REJECTED |
| G_end_minus1 | end range off by one (`min(start + 3, ...)` instead of +4) | 1 | 19/20 | KFF18 | REJECTED |
| H_reprokey | repro-pair special case keyed on the cell text (`if ... b"fatal: inv" in raw: return t`) | 0 | 20/20 | none | SURVIVES — but limit (iii) covers it (see below) |

## Distinguishing payloads (survivors, filed vs forgery `_one_line_bytes`; see differ.txt)

* C_surrogatepass — raw = `b"x"*102 + b"\xed\xa0\x80" + b"\xc2\x85" + b"y"*95` (202 bytes;
  ill-formed ED A0 80 straddles the tail cut, valid U+0085 follows).
  filed: `…\xa0\x80\u0085yyy…` (ED+A0 escapes `\\xed`… rendered `\xa0\x80\u0085`);
  forgery: `…\u0085yyy…` — it elides the surrogate sequence AND the following valid
  U+0085 head, deleting bytes the filed tool keeps; the two cells differ. A 1,536-payload
  token-offset sweep found only 2 differing payloads (both of this shape) for C.
* D_len_ge1 — same raw: filed `…\xa0\x80\u0085…`, forgery `…\xa0\x80\u0085…` with the head cut
  one byte further back (first `x` dropped, one fewer `x` before `\xa0`). 1,280/1,536
  sweep payloads differ — D almost always emits a different window than the filed tool,
  because any multi-char decode at the cut (e.g. two ASCII chars) now counts as straddling.
  KFF18 does not catch it (see below).
* E_head_fwd — raw = `b"x"*99 + b"\xe2\x82\xac" + b"y"*120` (U+20AC straddling the head cut, h=100).
  filed: head ends before the sequence (99 `x`es); forgery: head runs to 101 bytes, past
  the sequence end. Two cells differ. 8/1,536 sweep payloads differ for E.
* H_reprokey — keyed on the literal cell text `fatal: inv`. No distinguishing payload vs the
  filed tool in the 1,536-payload sweep (0 differs): the key fires only on the exact
  KFF14/KFF15 repro payloads, which the forgery then renders exactly like the filed tool.
  It IS a payload-keyed fake, but every finite-fixture variant of it is in that class.

## Why A_window3 is NOT a gap

`_straddling_sequence` only ever searches for a well-formed sequence with `start < cut < end`
and `end - start <= 4`. If a 4-byte sequence straddles the cut at start=cut−3, its end is
cut+1 — with window 3 the inner `end` loop starts at cut+1 > max allowed, so no iteration
runs, and the cut stays. Experimentally identical (_one_line_bytes differ=False on the
4-byte U+1D11E payload and 0/1,536 sweep payloads). A is an equivalent mutant, not a coverage gap.

## Analysis / findings

1. **C (surrogatepass).** The fixture's KFF18 sweep tokens include `\xed\xa0\x80` (one sweep
   token), but never placed so that the tail cut lands between A0 and 80 while a valid
   U+0085 follows within the same payload at the checked offsets (offsets 96-117, totals
   205/210/214). The claim's wording ("moves a cut only across ONE well-formed UTF-8
   sequence... strict decode to exactly one character") is violated by C: `surrogatepass`
   makes ill-formed ED A0..BF sequences look like one well-formed character, so the cut
   moves across ill-formed bytes. The fixture has no asserting case for a surrogate
   half straddling the cut. Verdict: SURVIVES — does NOT falsify the numeric predicate, but
   falsifies "moves a cut only across one well-formed UTF-8 sequence" as an unbounded
   statement; the mechanism is real. (The filed claim itself is worded "strict decode"; the
   forgery breaks strictness, so strictly the SURVIVOR is within a different decoder than
   described — the gap is a fixture hole, not a claim breach. Filed under NO-FALSIFICATION
   of the stated Predicate; the positive control passes and KFF18's measured property holds
   on the 29,700 sweep.)

2. **D (len >= 1).** The forge returns the first multi-char straddling span as a "sequence",
   shifting the cut onto a wrong boundary. KFF18 should catch it — but KFF18 checks only
   prefix/suffix-of-own-whole-rendering, which D CONTINUES to satisfy (both cuts still land
   on character boundaries: a multi-char span both sides are still well-aligned, just a
   different window). KFF14–KFF17 assert spelling only for well-formed/ill-formed leads;
   none pins the window position against the filed tool for adjacency of plain ASCII chars.
   So D silently emits a different excerpt than the filed tool for nearly every payload with
   >=100 bytes. Verdict: FALSIFIES-WORDING of "moves a cut only across ONE well-formed UTF-8
   sequence": D moves cuts across 2-char spans that are not one sequence. Its window violates
   the filed tool's semantics (cuts land on *some* boundary, but the wrong one). Reproducer:
   `.ufo/waves/round-92/w1/R92MutC2/fixture_D_len_ge1.txt` (rc=0 20/20) and the differ
   payload in `differ.txt` — the exact raw bytes are printed there; a two-line python
   excerpt reproduces it.

3. **E (head forward).** Filed moves the head cut BACK to `seq[0]`; E moves it FORWARD to
   `seq[1]`. The forgery's output on KFF17 (U+20AC across the head cut) still passes because
   KFF17 only asserts no byte escape appears in the cell — forward-eliding also hides the
   well-formed sequence. The claim's wording "moves a cut only across ONE well-formed
   sequence" is still satisfied by E (it removes the whole well-formed sequence, as filed
   does) — the difference is a semantic: the filed tool keeps the pre-cut bytes; E elides
   MORE bytes than the filed tool, including well-formed ASCII bytes after the cut. KFF18's
   prefix-of-whole-rendering property still holds, so the fixture cannot tell. Verdict: a
   real semantic gap vs the filed tool, covered by the same fixture hole as D; the words
   "moves a cut only across ONE well-formed UTF-8 sequence" remain true of E, so it does NOT
   falsify the stated mechanism. It does falsify "the excerpt's head is a prefix... of the
   tool's own whole rendering" only in the stronger "prefix at the right place" reading —
   E's head is a strictly shorter prefix. NO-FALSIFICATION of the stated predicate.

4. **H (repro-pair key on cell text).** Text-keyed on `fatal: inv`: fires only on the
   KFF14/KFF15 repro payloads and renders them exactly like the filed tool. This is precisely
   the class prereg limit (iii) already concedes: "The fixture reads the public K4 cell; a
   tool that hardcodes cells per payload can pass any finite fixture." Verdict: SURVIVES,
   limit (iii) covers it, NO falsification. Good faith note: H is a DOMINAting example of
   that known limit (it is the canonical F1 shape, keyed on text rather than the lead bytes).
   F1 in the probe (keyed on `F0 80`) was rejected by KFF14/KFF15 because the payloads there
   carry different continuations; H evades because the fixture's own A/B pair shares the
   cell-text marker `fatal: inv`.

5. **A (window 3):** proven-equivalent on all tested payloads incl. 4-byte straddles; the
   filed loop only finds sequences with end−start ≤ 4, and a 4-byte sequence meeting
   `start=cut−3` has end=cut+1, unreachable. The fixture result (20/20) is genuine and the
   equivalence is by-construction: not a gap, not a falsification.

## FALSIFIES-WORDING

**D_len_ge1 (claim C2, preregistration line 77-79):**
Exact statement: "moves a cut only across ONE well-formed UTF-8 sequence (the candidate
bytes must decode strictly to exactly one character, which applies every Table 3-7 row; S355
§3.9 D86: ill-formed subsequences do not overlap minimal well-formed ones)".
D decodes the candidate bytes and checks `len(...) >= 1`, so a candidate spanning TWO
well-formed characters (e.g. bytes "ab" straddling the tail cut: `b"a"*102 + b"b"*200`)
is taken as a straddling "sequence" and the cut is moved across both. The cut therefore
crosses more than one sequence. Reproducer: `.ufo/waves/round-92/w1/R92MutC2/fixture_D_len_ge1.txt`
(rc=0, 20/20) plus the direct-byte compare in `.ufo/waves/round-92/w1/R92MutC2/differ.txt`
(raw `6283…` hmm see D section raw hex listed in differ output for D_tail_ascii_aa; the
1,536-payload sweep differs in 1,280 cases).
This is a fixture hole, not a repair error: the r92 fixture's degradation cases
(KFF14-KFF17) pin spellings but never pin the window position against the filed tool for
plain-ASCII adjacency. L1 records it as an amendment: the fixture does not search-survive
the multi-character-straddle forgery.

For C and E: the same fixture hole lets a behaviourally different tool pass 20/20 (cells
differ from the filed tool on specific payloads listed above), but neither violates the
stated Table 3-7 one-sequence mechanism in the claim's wording: NO-FALSIFICATION for those
two of the stated Predicate (the mechanism sentences hold of the filed tool; the fixture
just doesn't exercise these forgeries).

For H: limitation (iii) of the preregistration explicitly covers "a tool that hardcodes cells
per payload can pass any finite fixture" — H is that class. NO-FALSIFICATION (limit (iii)).

For A: equivalence by construction, NO-FALSIFICATION.

## NO-FALSIFICATION summary

The collective fixture executes every required one-edit forgery as instructed. 5 of 8
survive the filed fixture at 20/20: A (equivalent, not a gap), C, D, E, H. Of those,
only D violates the letter of the "ONE well-formed sequence" mechanism; C violates the
"applies every Table 3-7 row" half under surrogatepass (the r92 fixture does not exercise
a surrogate lead across the cut); E preserves the mechanism while changing which bytes
are elided; H is the hardcoded-payload class the prereg already concedes. The positive
control (filed tool 20/20) and negative control (r91 tool 16/20) both verify.

Report: .ufo/waves/round-92/w1/R92MutC2.md
