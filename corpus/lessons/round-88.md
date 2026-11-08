# Round 88 — the two r87-carried clauses get one binding each; the K4 FLAGFAIL detail becomes one escaped line

Lane base `7defe9c5fee3df07e403666bdeccfb88428ef729` (r87 closed by the non-author spot-check
`corpus/lessons/round-87-verifier-spotcheck.md`). Instruments and controls P
`e60ea25f6dc6d988bbdd713a2d00718f5915e29d`; the preregistration alone F
`f74092b24bbddf2e5259977c254c91b7a6b71160`. Wave evidence: `.ufo/waves/round-88/w1/`; receipts:
`census/round-88/records/` and `census/round-88/controls/`.

## Gate

Sources opened this round (each read here; ids continue the registry after S347):

- **S348 — Python 3.14 `str.splitlines` line boundaries** (https://docs.python.org/3.14/builtins/stdtypes.html#str.splitlines,
  requested `/3.14/library/stdtypes.html` and served after one 301; HTTP 200, 774910 bytes, sha256
  `5abdd8b9ceeda2c3e94d8f95e32d9853d6f35d35844514727aa440cac98eda42`, capture
  `census/round-88/srcs/str-splitlines.html`, opened 2026-11-08). Quote, the paragraph under the anchor: "This
  method splits on the following line boundaries. In particular, the boundaries are a superset of universal
  newlines." (18 words). **ADMIT**, `docs`, tier A, `mined` — it grounds C2's one-physical-line rule and names every
  boundary the escape set must cover, including NEL and U+2028/U+2029. Duplicate-URL check: `stdtypes.html` is cited by
  S061 (`str.lstrip`) and S105 (boolean numeric equality) for other scopes; this row names the boundary list only.
- **S350 — git-config(1) `core.quotePath` as installed** (git 2.56.0-1, `/usr/share/man/man1/git-config.1.gz`;
  capture `census/round-88/srcs/git-config.1` sha256 `f158d47e…`, roff line 3564, opened 2026-11-08). Quote: "will
  quote "unusual" characters in the pathname by enclosing the pathname in double-quotes and escaping those
  characters with backslashes" (19 words). **REJECTED** on scope: the page states the line form's escape rule, and
  this lane parses the `-z` form (S346). **Flip:** a round that starts parsing the line form, or must decide which
  spelling a caller's `core.quotePath` selects. This closes the r87 spot-check's D4 (the rejected row the previous
  round's Gate never wrote).
- **S349 — Python 3.14 `base64`** (https://docs.python.org/3.14/library/base64.html, HTTP 200, 61731 bytes, sha256
  `09b0682de6052bc8a77eb14655add2f2a80e286b08a60a51050da750ea43f984`, capture
  `census/round-88/srcs/base64.html`, opened 2026-11-08). Quote, `b64decode`: "Decode the Base64 encoded
  bytes-like object or ASCII string s and return the decoded bytes." (16 words). **REJECTED** on scope: the frame is
  the lane's own transport choice; the page states the encoding and `validate`, not a record-format rule the lane
  reuses, and S348 carries the enforceable property. **Flip:** a round that must decide padding or validation
  semantics for an untrusted *external* base64 payload.

Curation decision (plans A4): S348 overlaps S278 (Python 3.12 `stdtypes.html#str.splitlines`, opened 2026-11-03)
by page content — the scout re-fetched both and found the rendered boundary tables byte-identical. S348 is kept
because its page is the host's Python (3.14.8) and its consumer is the escaping rule, while S278's is the
hidden-line numbering; no third row (the proposed S350) was added, and S278 stays as filed. S349's quote word count
was corrected to 15 before filing.

Census: before (reconstructed at the lane base, `census/round-88/records/sources-census-before.txt`) `file ok`,
EXIT 0, 87 pre-existing `W04` warnings, 270 rows; after (`…-after.txt`) `souji ok`, EXIT 0, 88 W04 warnings (the new
S350 duplicate-URL line), 273 rows. Registry `270 → 273` (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`). Three rows added, one admitted,
two rejected; no `E0x`.

## Measured

- **C1 (calibration 7).** Population `census/round-88/c1-false-rows.tsv` sha256
  `b710e368de862a72bc430610003d3cdf1499bea1b6e4ff2325417a1d388a68c3` (53 rows = the r87 51 byte-for-byte, in order,
  plus NF6g at R11 and LD1). Counter under test `census/round-87/c1-pointer-counter.py` sha256 `fd0a8e24…` (unchanged
  bytes). After (`census/round-88/records/c1-after.txt`): `ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0`,
  `ARM pristine pop=r88 rows=53 mismatches=0 errors=0 exit=0`, `m17-duplicate-id` and `m18-whole-before`
  `killed=yes` on r88 and `killed=no` on r87, `SUMMARY mutants=12 sets=r87,r88 pristine_r87=ok pristine_r88=ok
  killed_r87=10 killed_r88=12 killed_total=22`, EXIT 0. Before (`census/round-88/controls/c1-before.txt`): the same
  battery and mutants on the r87 population alone, `killed_r87=10` with `m17-duplicate-id killed=no` and
  `m18-whole-before killed=no`, EXIT 0. Belt (`records/c1-dead-belt.txt`): the 13-member set,
  `m19-len-half killed=no` on both sets, `SUMMARY mutants=13 … killed_r87=10 killed_r88=12`, EXIT 0.
- **C2 (operability 8).** Fixture `tests/fixtures/r88-k4-flagfail.py` sha256 `aa79133a…`; tool under test
  `tools/souji-record-agreement.py` sha256 `c0604b4a…`; before bytes `census/round-88/controls/c2-before-tool.py`
  sha256 `e1b00e8a…`. After (`records/c2-after.txt`): seven `CASE … tool=pass`, `SUMMARY cases=7 tool_pass=7
  before_pass=3`, EXIT 0. Before (`controls/c2-before.txt`, the r87 tool as both arms): `tool_pass=3 before_pass=3`,
  KFF2/KFF3/KFF4/KFF5 fail, EXIT 1. No regression: the r87 12-row counter on the filed tool reads
  `SUMMARY rows=12 mismatches=0 errors=0`, EXIT 0 (`records/c2-k4-regression.txt`).

## Narrowed before filing (plans/round-88.md A1–A8)

The wave's critic measured four sentences the frozen prereg states more widely than the instruments enforce: the
harness's `where=ledger` branch IS judgement code for LD1 (the "No judgement code changed" sentence contradicted
itself); the belt is empirical on two frozen populations, not a proof over all inputs; the 200-character bound is
the excerpt, not the whole 259-character K4 cell; and `_escape_text` covers C0/DEL/NEL/LS/PS, not every C1 control
(U+0080–U+0084 and U+0086–U+009F pass raw, and KFF4's single `0x85` byte reaches the escape as literal
`backslashreplace` text). Each narrowing is recorded in the plan; the prereg is not edited. The scribe's audit added three documentation
corrections (plan A6): the provenance paragraph now says the quote was checked against the RENDERED capture, S348's
`teaches` cell no longer asserts a list the quote does not enumerate, and Q163 corrects Q161's stale tail-only clause;
the tool's `_stderr_tail` docstring is routed to r89. The executor's hand-driven triple added A7 (LD1's kill is the
missing marker, not an exit-code delta) and the mutation-tester's sweep added A8 (each new row binds one spelling:
NF6g the alnum predecessor, LD1 the target-equal duplicate; NF6h/NF6i/LD1b/LD2 and the `_ledger` malformed-row and
`_whole` multi-occurrence legs are carried).

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | chronology: both after arms were run once before F landed | the pre-freeze runs at 07:52 (battery `bat1`, killed at its 300 s deadline) and 07:53 (C2 fixture); F's committer time 08:02; filed receipts are the post-F runs at 08:05 | the freeze-before-scoring rule (r63 M2) and the commit timestamps it leaves | disclosed in `plans/round-88.md` A0.1; the pre-freeze pair is not evidence; the filed receipts were re-run after F with the same numbers |
| M2 | instrument defect caught pre-freeze: the first KFF2 predicate asserted `"  File " not in out`, which is false on the correct escaped detail because the escaped traceback still spells `  File` | the first fixture run read `CASE KFF2 tool=fail` on the tool's correct detail (`the index-flag read failed (Traceback…\n  File "w"…\nAttributeError: boom\n)`) | running the fixture once before freezing it, and reading the detail rather than the verdict | the predicate now asserts only `"\n  File " not in out` (no RAW traceback line); the fixture is re-run and every case passes on the filed bytes |
| M4 | documentation overstatement: the m17 mutant note says the counter "exits 0" while the measured exit stays 1 (the appended ABSENT row refuses P01 under the fleet root); the kill is the missing marker | `.ufo/waves/round-88/w1/S88ExecC1.md` §2/§5; the hand-driven control run | the executor's hand-driven pristine/mutant/control triple, which read the exit code as well as the marker | plan A7 records the corrected sentence; the mutant file is not edited because its sha is pinned by three receipts for a measured-zero verdict change |
| M3 | build decision recorded as a mistake: the plan first copied the r87 counter into `census/round-88/`, which would have created a second counter to pin for no measured gain | the copy existed at 07:46 and was removed before P; the prereg and A0.2 say the counter under test is the frozen r87 bytes | the lane's own "one instrument, one pin" convention | the copy and its item-file copy were removed before P; `census/round-88/` carries only the population, mutants, harness and battery |
