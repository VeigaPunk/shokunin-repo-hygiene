# R92ReviewerC2 — C2 falsification review (committed bytes)

Lane `souji-shokunin`, read-only. Scratch `/fast/scratch/hyaku/souji-r92/R92ReviewerC2/` deleted before yield; text logs copied to seat dir `R92ReviewerC2/` (`fix-after.log`, `fix-control.log`, `fix-forgery.log`, `k4.log`). No tool installs (nothing needed). Lane working tree untouched by this seat (two untracked files `census/round-92/records/m1-cleanup-fail-check.txt`, `plans/round-92.md` pre-existed from other seats; never staged).

## 1. Independent SUMMARYs (re-derived locally from committed bytes)

Hashes confirmed: tool `fc0e35c2...`, before `21e5c740...`, fixture `2c9bd76c...`, probe `9dac4cde...` — all match prereg pins.

- **After arm:** `SUMMARY cases=20 tool_pass=20 before_pass=16` exit 0. Before arm red on exactly KFF14, KFF15, KFF16, KFF18 (all others pass both arms).
- **Control (r91 tool as both arms):** `SUMMARY cases=20 tool_pass=16 before_pass=16` exit 1. Matches committed `c2-control-r91-tool-both-arms.txt` byte-for-byte, including `# KFF18 ... unfaithful=28`.
- **Forgery probe:** `FORGERY-SUMMARY forgeries=5 rejected=5 positive=pass` exit 0. F1 rejected via KFF16+KFF18, F2 via KFF16, F3 via KFF11+KFF18, F4 via KFF17+KFF18, N0 via KFF14/15/16/18. (First run errored with `FileExistsError` because the scratch dir pre-existed — probe requires a non-existent `--work`; rerun with clean dir succeeded. Probe defect vs misuse: caller error, not a claim defect; noted in §6.)
- **r87 K4 regression:** `SUMMARY rows=12 mismatches=0 errors=0` exit 0.

Numbers in the stated wording all re-derive. §5 attacks the wording, not the numbers.

## 2. Payloads A/B — byte-by-byte derivation (210 bytes both forms)

Fixture form and task form coincide in alignment: `fatal: inv ` (11 bytes, fixture) + 99×`a` puts `F0` at offset 110, `0x80` at 111; task form `a*110` puts `F0` at 110, `0x80` at 111. Default limit 200 → `head=100`, `keep=99`, `t0=len-99=111`. UTF-8 bytes: A = `F0 80 61 C2 85` (offsets 110–114), B = `F0 80 61 62 85` (110–114).

**Filed tool (both payloads):** `_straddling_sequence(raw,111)` = `None` → `t` stays 111. Candidates: `(110,112)=F0 80` invalid start, `(110,113)=F0 80 61` reject (3rd byte not continuation), `(110,114)=F0 80 61 C2` reject, `(109,…)` start on `a` → 2+-byte slices decode len≠1. So the ill-formed lead absorbs nothing. Cells (task form):

- A: `a×100 + … + \x80a\u0085 + b×95` → head prefix ✓, tail suffix ✓.
- B: `a×100 + … + \x80ab\x85 + b×95` → prefix ✓, suffix ✓. Cells differ (u0085 vs x85).

**r91 tool (both payloads):** `raw[111]=0x80` continuation → walks back `i=110`, `raw[110]=0xF0` lead, `need=4`, `end=114 > t=111` → returns `min(114,len)=114`. No check that bytes 111–113 are continuations. `t=114` splits the *next* sequence: in A `raw[114]=0x85` (orphan byte → `\x85`), in B `raw[114]=0x85` (raw byte → `\x85`). Both render the identical tail `…\x85bbbb…` (`before` A vs B cells byte-identical, tail suffix violated — `full.endswith(tail)==False` in A, respelling proven). Prereg sentence "so an ill-formed lead just before the tail cut absorbed bytes of the following well-formed sequence and printed its continuation with the raw byte's spelling" is **true**, with the mechanism made precise: the tail logic moved because `raw[t]` was a continuation and the declared structural length overshot into a later sequence; the *head* logic, by contrast, requires all declared bytes to be continuations (`_cut_head` line 237) and would not move here. So the defect is tail-specific and the prereg text does not overclaim a head defect.

Note: wording "absorbed bytes" — the elided middle in A contains `F0 80 61 C2` (110–113); the well-formed `C2 85` lost its lead to the elided region. Correctly described.

## 3. `_straddling_sequence` vs Unicode Table 3-7 / S355

Docstring claim: "the candidate bytes must decode strictly to exactly one character, which applies every row of Unicode Table 3-7". **True** — for UTF-8, `strict` success + exactly one character is equivalent to "one well-formed sequence": any strictly-decodable 1-character byte string is a well-formed sequence by definition, and every well-formed sequence decodes to exactly 1 character. Empirically verified (exit-printed table, seat dir copy `fix-*.log` context; script run inline at review time):

| class | bytes | strict 1-char |
|---|---|---|
| ASCII | `41` | yes |
| C2 80/85, DF BF | — | yes |
| C0 AF, C1 BF | — | **no** (invalid start) |
| E0 A0 80 | | yes |
| E0 80 80 | | **no** (invalid continuation) |
| ED 9F BF | | yes |
| ED A0 80, ED BF BF (surrogates) | | **no** |
| F0 90 80 80, F3 BF BF BF | | yes |
| F0 80… | | **no** |
| F4 8F BF BF (U+10FFFF) | | yes |
| F4 90 80 80 (beyond) | | **no** |
| F5…, FE, FF | | **no** |
| lone 80/85, truncated C2 / E2 82 / F0 90 80 | | **no** |

Second-byte endpoints exhaustively: E0 `9F/A0/BF/C0` → F/T/T/F; ED `7F/80/9F/A0` → F/T/T/F; F0 `8F/90/BF/C0` → F/T/T/F; F4 `7F/80/8F/90` → F/T/T/F. Every prereg-listed ill-formed class (C0/C1, F5..FF, E0 80..9F, ED A0..BF, F0 80..8F, F4 90..BF, missing continuation) is correctly rejected by Python's strict decoder. Loop bounds (`start ∈ cut-1..cut-3`, `end ∈ cut+1..start+4`) cover all straddling lengths 2–4; no 1-byte seq can straddle. Loop prefers smallest `end` for `start=cut-1`: harmless — a lead's length is determined by its first byte, so a 2-byte and a 3/4-byte decode starting at the same byte cannot both succeed.

**D86 sentence check** ("ill-formed subsequences do not overlap minimal well-formed ones; S355 §3.9 D86"): the filed code implements it only insofar as candidate slices are tested in isolation; on the A/B payloads the outcome matches D86 (ill-formed `F0 80` stands alone, `C2 85` untouched). But consider: cut inside an ill-formed run *adjacent* to a well-formed sequence on the other side — e.g. `raw=F0 80 61 C2 85`, cut=4 (inside `C2 85`): returns `(3,5)` and tail moves to 5, eliding byte… in the *tail* direction for a head cut this elides `C2` into the middle-side but keeps `85` only if tail lands after. That's exactly Table-3-7 behaviour (the candidate `C2 85` IS well-formed). No violation found.

## 4. Case-by-case reading (KFF13–KFF18, plus forgery set)

- **KFF14/KFF15:** discriminate correctly (before fails both, filed passes both; pair check also requires cells differ). Tests what prereg says: odd-bird pair A=character/B=byte. Could they pass without the claimed property? A tool special-casing `F0 80` exactly (forgery F1) passes KFF14/KFF15 but is caught by KFF16/KFF18. A tool that moves the cut only when `raw[t]==0x80 and raw[t-1]==0xF0` without moving for other leads — same as F1. No pass-without-property found beyond the stated-limit hardcode (see §6).
- **KFF16:** E0 80 80 across tail cut (t0=111): before returns `t=113` (structural 3+… elides both `0x80`s — `x80` count 0, fail); filed keeps `t=111`, both `0x80`s spelled `x80` ×2 and `u0085` ×1. Tests overlong E0 row. Catches ranges-less cont-only repair (F2). Prereg wording "the cut must not swallow it as a three-octet sequence" is accurate: before swallows via *elision* — wording says "swallow", not "respell", so no misdescription.
- **KFF17:** U+20AC across head cut (h=100, seq (99,102)). **Before also passes** (verified: `before head=99` identical to filed). This is a regression guard against breaking head movement, **not evidence for the C2 repair**. Prereg text "(a U+20AC across the head cut)" claims no before-red for KFF17, and the CONTROL sentence lists only KFF14/15/16/18 as red — so stated wording is still accurate. Flagged here only so nobody cites KFF17 as discriminating evidence.
- **KFF18:** 29,700 = 22 offsets × 15 × 15 tokens × 3 lengths × 2 builds; head is prefix / tail is suffix of `_escape_text(_decode_record(raw))`. Before: `unfaithful=28`; filed: 0. This is the strongest case: tokens include all ill-formed classes (C0 AF, C1 BF, E0 80 80, ED A0 80, F4 90 80 80, F5 80, lone 85, FF, truncated F0 80/E0/E2 82). Any tool missing one class's range check should fail some payload. No hypothetical survives: F3 (no tail) fails KFF18, F4 (no head) fails KFF18.
- **KFF13:** AST-based `defs==0 and calls==0`; self-check (spaced def detected, docstring ignored) verified correct direction. Evasion probe: appending `exec("def _one_line(text):\n    return text")` to the filed tool yields `tool_pass=20 before_pass=16` exit 0 while a runtime `_one_line` exists. **But** the prereg wording restricts the claim to "no function definition named `_one_line`, no call whose callee is named `_one_line`" *in the parsed tool source* — the exec string is not a parsed `FunctionDef`, so literal wording holds. Recorded as residual risk (§6), not a wording falsification.
- Others (KFF1–KFF12, KFC1–2): inherited cases, not C2-discriminating; verified they pass both arms, consistent with brief. KFF11 (nelcut) is R91-era; filed passes, F3 fails it. The brief only asked KFF13–KFF18; SKIPPED-detail not needed as all verified.

## 5. Falsification list

**FALSIFIES-WORDING: none found.** Every sentence checked against committed bytes holds:

1. "moves a cut only across ONE well-formed UTF-8 sequence" — verified incl. edge probes (ASCII cuts never move; boundary cuts at (0,2)/(2,4) correctly `None`; double-seq `C2 85 C2 85` cut=2 `None`).
2. "no C0/C1/F5..FF lead, no E0 80..9F overlong, no ED A0..BF surrogate, no F4 90..BF beyond U+10FFFF, every continuation present" — all rows empirically match Python strict.
3. A/B cell descriptions — verified byte-identically.
4. "KFF13 becomes an ast check with a fixture self-check (rc 2 otherwise)" — verified.
5. "KFF18 … 29,700 deterministic payloads … head is a prefix and its tail a suffix" — count and offsets (84–117 via second build) verified.
6. Control sentence "KFF14, KFF15, KFF16 and KFF18 red, EXIT 1" — exact.

**NO-FALSIFICATION** record: I attempted to refute each sentence above by (a) re-running all four predicate commands, (b) hand-deriving A/B cuts on both tools, (c) exhaustive endpoint testing of Table 3-7 rows against the decoder, (d) fuzzing `_straddling_sequence` boundaries (double patterns, truncated tails, edge cuts 0/len), (e) crafting the KFF13 exec evasion (passes the AST check but literal "parsed source" wording survives), (f) checking whether any of the 5 named forgeries is misdescribed (all rejected with the claimed failing-case sets). Only cheaper wording nits survive as residual risks, below.

## 6. Residual risks (not falsifications)

1. **KFF13 evasion:** a runtime `_one_line` hidden in `exec("...")` passes the AST check 20/20. Literal wording ("in the parsed tool source") is not falsified, but "the dead escape-first helper *stays deleted*" (fixture docstring spirit) is weaker than semantic absence. A full-`ast`-parse of string literals would close it.
2. **Stated limit (iii) stands:** a tool that hardcodes cells per payload still passes any finite fixture; KFF18's 29,700 payloads bound but do not close this. No new attack mounted — attempting a hardcoded tool costs one working reimplementation of the property itself.
3. **Prefix/suffix scope:** KFF18 is measured, not proven, for all payloads (prereg limit (i) says exactly this). My boundary fuzz is illustrative, not a proof.
4. **Probe CLI footgun:** `c2-forgery-probe.py` requires `--work` to not exist (fatal `FileExistsError` instead of the clean rc=2 used for /tmp / non-empty checks) — cosmetic; reproduced and recovered.
5. **Unused SKIPPED:** none — all 4 SUMMARYs, A/B derivation, decoder table, and KFF13–KFF18 were read end-to-end (fixture `score()`, `case_sweep`, `case_source`, `main`; tool `_straddling_sequence`, `_cut_head`, `_cut_tail`, `_one_line_bytes`, `_escape_text`, `_decode_record`, plus the single call site at line 453 with default `limit=200`).

---
C2 review complete. No committed-byte falsification of the stated wording; residual risks listed for L1 disposition.
