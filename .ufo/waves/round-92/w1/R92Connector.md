# R92Connector — cross-claim / cross-lane scan and the planning data-walk

Seat: connector (leaf; no dispatch). Lane: souji-shokunin. Round: 92 (attempt 2). Lane base
`5339b2ac79f81aa446f6a2cd4700321cf4982fd3`; pinned instruments `P1 44d45b44`, `P2 1d015a2d`, freeze `F e8d31f06`.
Contract read first: `census/round-92/preregistration.txt` (frozen). Nothing below widens a sentence in it.

Evidence durability: every argument, output line and reproducer in this report lives under
`.ufo/waves/round-92/w1/R92Connector/` and this file. Scratch `/fast/scratch/hyaku/souji-r92/R92Connector/` was
created empty and removed before yield (nothing was written to it). No clone, no git/jj mutation, no write outside
the seat dir and this report.

---

## 0. Evidence map (what can be re-run)

| artifact | path | result |
|---|---|---|
| RFC 3629 §4 vs Unicode Table 3-7 comparison | `.ufo/waves/round-92/w1/R92Connector/rfc4-vs-table37.py` | EXIT 0 |
| its receipt | `.ufo/waves/round-92/w1/R92Connector/rfc4-vs-table37.receipt.txt` | `RANGE-TABLES identical=True` / `SWEEP sequences=4207580 disagreements=0 accepted_by_len={1: 128, 2: 3840, 3: 122880, 4: 1048576}` / `VERDICT same_set=True … IDENTICAL` |

Pins re-derived on the working tree before any claim about them (all match the preregistration):

```
fc0e35c208331de8ce568de3543b330c470e0a80336652f94d575dc242137a75  tools/souji-record-agreement.py
21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c  census/round-92/controls/c2-before-tool.py
fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b  census/round-87/c1-pointer-counter.py
f66341fc2867f6b5dbd8515a717747370c700fd31bf7aaa497a292ca65027c51  census/round-92/c1-false-rows.tsv
5a8f608787aa47700dd3b76e99a9f9618a335a8cc4af448cab119993dee13e05  census/round-92/c1-targets.json
2c9bd76c77c609bfaf2fd1a86a5bd022fc8549cd58bc2f198a029e3ea90feeae  tests/fixtures/r92-k4-flagfail.py
f9e158a640c88cb0aebf60e5f724ea4f957eca539c620fb1e161cb6c8f8fb22e  census/round-92/srcs/unicode-ch3.html
```

No tool was installed or upgraded for this seat (none was needed; no `pacman`, `uv tool` or binary install ran).

Captures used: `census/round-91/srcs/rfc3629.txt` (RFC §4 at LF lines 275-291, the §4 NOTE at 293-296) and
`census/round-92/srcs/unicode-ch3.txt` (one 214,657-character line; Table 3-7 caption at character offset 140,695,
the "Table 3-7 lists all of the byte sequences…" sentence at 140,040, the disallowed-bytes sentence at 141,393, the
D86 partition sentence at 133,443).

---

## 1. Sibling overlap — does any sibling own UTF-8 window/excerpt cutting, surrogateescape excerpt helpers, or a
mutation-census harness?

Scan: `grep -rIl` over `/home/vgpnk/Projects/shokunin/*-shokunin/` (read-only; `.git`, `.ufo`, `.jj` excluded) for
`surrogateescape`, `_cut_tail`/`_cut_head`, `elide`, `excerpt`, `def _snippet`/`_clip`/`window`, `mutant`/
`mutation`, `false-rows`, `souji-record-agreement`, `_straddling_sequence`, then reading each candidate hit.

| sub-surface | owner outside souji? | nearest sibling code, and why it is not this surface |
|---|---|---|
| UTF-8 window/excerpt **byte** cut with a sequence-boundary rule | **no** | `kaidoku-shokunin/tools/round-33/disk-command-audit.py:84` `_snippet`, `kama-shokunin/tools/round44-release-recheck-audit.py:182` and `…round46…:209` `excerpt`, `kotodama-shokunin/tools/harness/claims-freshness.py:994,1598` `_clip` all slice a **decoded `str`** (or a list of lines). A `str` slice cannot split a UTF-8 sequence, so none has the hazard and none validates a boundary. `chousa-shokunin/tools/capture-text.py` cuts OOXML/OLE byte streams by format, not by text window. |
| `surrogateescape` (or equivalent) **excerpt** helper that spells cut bytes as `\xNN` | **no** | `chousa-shokunin/tools/lane-preflight.py:169` (`encode('utf-8','surrogateescape').decode('utf-8','backslashreplace')` on a whole string), `…/argv-witness.py:280`, `…/mechanism-witness.py:239`, `…/search-rerun.py:266,285,363,427,581` (line-wise search and byte-order sorting), `kaidoku-shokunin/tools/round-39..42/sqfs-list.py` (filesystem names). Every one is a whole-value round-trip or a line search; none bounds a window and none respells a byte because a cut fell inside it. |
| mutation-census / mutant-survivor harness | **yes, different design** | `kaidoku-shokunin/tools/round-67/mutation-battery.py` applies two named mutations, runs each mutant's own `--selftest`, and *asserts the exit code* (`…:195` `{"exit": p.returncode, …}`, `…:313` `"survived": st["exit"] == 0`, `…:370-382` before/after rc). `kama-shokunin/tools/round58-c1-counter.py:68` and `…/round59-c1-counter.py:109` derive the verdict from the exit code (`{0: "accept", 1: "reject"}.get(p.returncode, "error")`). Neither consumes a *false-row population* file; neither owns or references souji's instruments (`grep` for `souji-record-agreement`, `_straddling_sequence`, `false-rows` finds only one lesson-table cell, below). |

**Verdict.** No sibling owns any of the three surfaces; nothing is duplicated and nothing has to be reconciled. The
one cross-lane touch is a lesson, not code: `kaidoku-shokunin/corpus/lessons/round-70.md:34` (M70-5) records the same
*family* failure — "the structural validators accepted invented passing arms, kills with green rc, ok-true-over-
false-arms" — which corroborates §2 but is not an implementation to reuse. Adjacency (`SCORECARD.md` row) is
therefore unchanged by this scan, and R91Connector §2's conclusion ("no sibling owns the surface") still holds at
r92.

---

## 2. Cross-claim pattern — "an instrument asserted the shape, not the success/whole"

C1's gap is "a row asserted the FORGE marker but no exit code"; C2's gap is "a cut trusted a lead byte's declared
length". The same assertion shape recurs across the lane's r8x/r9x instruments:

### A. Marker asserted, exit code not asserted (C1 family)

`census/round-92/c1-false-row-harness.py:463` and `:484` are the whole match rule:

```python
ok = got == exp_got and (exp_rc == "-" or p.returncode == int(exp_rc))
```

so a row with the default `-` binds only the `FORGE <fid>` marker class. Population census (rows are 10-column TSV;
column 9 is `expect_rc`; `dash` = rows that assert no exit code):

| population | rows | `expect_rc` `-` | rc-asserting rows |
|---|---|---|---|
| `census/round-80/c1-false-rows.tsv` | 18 | 17 | 1 (rc=1) |
| `census/round-81/c1-false-rows.tsv` | 25 | 24 | 1 (rc=1) |
| `census/round-82/c1-false-rows.tsv` | 32 | 31 | 1 (rc=1) |
| `census/round-83/c1-false-rows.tsv` | 36 | 35 | 1 (rc=1) |
| `census/round-84/c1-false-rows.tsv` | 44 | 43 | 1 (rc=1) |
| `census/round-85/c1-false-rows.tsv` | 47 | 46 | 1 (rc=1) |
| `census/round-86/c1-false-rows.tsv` | 49 | 48 | 1 (rc=1) |
| `census/round-87/c1-false-rows.tsv` | 51 | 50 | 1 (rc=1) |
| `census/round-88/c1-false-rows.tsv` | 53 | 51 | 2 (rc=1) |
| `census/round-89/c1-false-rows.tsv` | 57 | 53 | 4 (rc=1) |
| `census/round-90/c1-false-rows.tsv` | 58 | 53 | 5 (rc=1) |
| `census/round-91/c1-false-rows.tsv` | 63 | 56 | 7 (rc=1: LP3 LD1 LD1b LD2 LD2b LD1c LD3) |
| `census/round-92/c1-false-rows.tsv` (= r91 + 1 comment + LD4r) | 64 | 56 | 7 (rc=1) + **LD4r (rc=0)** |

The failure mode is structural, not one missing row: every rc-asserting row through r91 is a *refusal* row, so the
success polarity is never bound and a counter that exits 1 on success passes all twelve populations. r92 fixes the
instance (one rc=0 row) and not the family: the dash default is still the default at
`census/round-92/c1-false-row-harness.py:463,484`, so any future population copied from r91 re-opens the gap.

### B. `rc=` printed, never asserted (C2 family)

| instrument | prints rc at | asserts rc? |
|---|---|---|
| `census/round-85/c2-k4-counter.py` | `:233` (`… rc={p.returncode} …`) | no — the only `returncode` test is the fixture's `git` call at `:68` |
| `census/round-86/c2-k4-counter.py` | prints per row | no — only `:70` (fixture `git`) |
| `census/round-87/c2-k4-counter.py` | `:337` (`ROW … rc={p.returncode} …`) | no — only `:88` (fixture `git`); `ok` is computed from the marker hits alone (`:300-341`) |
| `census/round-87/c2-byte-arm.py` | `:219` | no — only `:68` |
| `census/round-83/c2-tree-walk-counter.py` | `:304` | **yes** — `:315` `ok = exited and rc == 0 and …` |
| `census/round-92/c2-forgery-probe.py` | `:82,100` | **yes** — `rc == 0 …` positive arm, `rc == 1 …` per forgery |
| `tests/fixtures/r92-k4-flagfail.py` | `:172-181` (`subprocess.run` of the tool) | **no** — only the `git` fixture call's rc is tested (`:139`); the case condition is the parsed `MISMATCH\tK4` cells, so a tool that prints correct cells and exits non-zero passes `tool_pass=20` |

So the K4 counter family (r85-r87) reports the tool's exit code as a *label* while binding only the marker lines —
the C2-side twin of C1's gap. In r92 only the forgery probe binds polarity (`:82,100`); the fixture runs the tool as
a subprocess and compares cells without testing `p.returncode`, and the r85-r87 counters are frozen and were re-used
as the r87 K4 regression, whose `SUMMARY rows=12 mismatches=0` therefore cannot see a tool that prints the right rows
and exits non-zero. The C2 claim does not claim a tool exit code, so this is a family observation, not a defect in
the stated wording.

### C. Structural length (or offset) without well-formedness validation

| instrument | site | what it trusts |
|---|---|---|
| `census/round-92/controls/c2-before-tool.py` (the r91 tool) | `_utf8_seq_need` `:216-224`, `_cut_tail` `:242-256` | the lead's class (C0-DF→2, E0-EF→3, F0-F7→4) only: `need` bytes are moved without decoding, so a truncated `F0 80` before the cut reaches into the next well-formed sequence. This is the C2 gap. |
| `census/round-90/controls/c2-before-tool.py` | `_one_line_bytes` `:212-229` | raw byte offset, no boundary move at all — the prior instance (a sequence is cut and its bytes escape). |
| `census/round-91/variants/keep-helper-tool.py`, `…/double-backslash-tool.py`, `…/raw-newline-tool.py` | `_utf8_seq_need` `:216-224`, `_cut_head` `:227-240`, `_cut_tail` `:242-256` | the same lead-length table plus a *continuation-only* check (`all(0x80 <= b <= 0xBF for b in raw[i:end])`, `:237`): `E0 80 80` (overlong), `ED A0 80` (surrogate), `F0 80 …` and `F4 90 …` all pass as "a sequence", i.e. exactly the four second-byte rows Table 3-7 exists to add. Three r91 wave variants still carry it; they are wave artifacts, not filed instruments, but they are the obvious "before" arms for a later round. |
| `tests/fixtures/r91-k4-flagfail.py` (r91) | KFF13 | asserted a *substring* of the tool source, not the AST property (r91 spot-check §2; fixed in r92, see §3 item 2). |
| `census/round-87/c2-k4-counter.py` | row `KN2` `:302-320` | asserts the printed writer digest tracks the bytes (a shape), never the tool's exit code. |

### Cross-claim reading

Both claims' gaps are instances of one assertion shape — *a marker/structural claim stands in for the property that
matters* (success polarity on one side; whole-sequence well-formedness on the other). The r92 instruments close the
stated instances; the family survives in (A) the dash default and (B) the frozen K4 counters, and those are named in
the r93 draft (§3) rather than in the claim wording.

---

## 3. Planning data-walk — r91 spot-check routed items 1-5, and the r93 draft

Routed items are `corpus/lessons/round-91-verifier-spotcheck.md` §7; the L1's dispositions are
`plans/round-92.md` A0.7. Status below is *evidence* status, not measurement status: the C1/C2 predicate numbers are
the wave's to produce.

| # | routed item (r91 §7) | status | evidence in this round |
|---|---|---|---|
| 1 | `_cut_tail` must validate the whole declared sequence before moving; add head-cut and invalid-lead rows; A/B as a case pair | **ANSWERED** | `tools/souji-record-agreement.py:216-248` — `_straddling_sequence` returns a straddling `(start,end)` only when `raw[start:end].decode("utf-8","strict")` is exactly one character (every Table 3-7 row); `_cut_head`/`_cut_tail` move only on that. Rows: `tests/fixtures/r92-k4-flagfail.py:57-61` (KFF14 invcutA, KFF15 invcutB as the A/B pair with a differ check at `:443-447`, KFF16 overlong, KFF17 head cut, KFF18 sweep) and `CASES` `:372-377`; the before-arm control is `census/round-92/controls/c2-before-tool.py` (sha `21e5c740…`, the r91 tool). |
| 2 | KFF13 by `ast`, both directions as cases | **ANSWERED** | `tests/fixtures/r92-k4-flagfail.py:264-272` (ast walk for a `def _one_line` and a `_one_line` call), self-check at `:413-416` exits 2 unless a spaced `def _one_line (` is detected and a docstring mention is not flagged; KFF13 is `("KFF13","decl",False,None)` `:372`. |
| 3 | the alternative-edit survivor search never ran; add LD4 `rc=0` | **ANSWERED (instrument level)** | search `census/round-92/c1-survivor-search.py` (per-mutant tree deleted once scored, `--ids`, `--timeout`); row 64 `LD4r … MOVED 0` in `census/round-92/c1-false-rows.tsv:67` (file sha `f66341fc…`), the seven r91 rc rows all `1` (§2 A). The 47/47 measurement is the wave's, not this seat's. |
| 4 | re-gate RFC 3629 before any validity claim; ground range checks on §4 syntax, not S354's §3-only scope | **PARTLY** — the evidence is now complete (§4), the filed form is not | `plans/round-92.md` A0.7 re-gates validity to Unicode Table 3-7/D86 (S355, `corpus/SOURCES.md:294`, knowledge entry `corpus/knowledge/utf8-window-well-formed-cut.md`) and keeps S354's §3 as the sequence unit. But no §4 capture/row is filed (`grep -rn '3629\|§4' census/round-92 tests/fixtures/r92-k4-flagfail.py tools/souji-record-agreement.py` finds only the §3 sentence in the tool docstring), so "ground on §4 syntax" is met by *identity* (this seat, §4 below), not by a filed §4 row. |
| 5 | population header hygiene — inherited comment lines should name the r90/r91 rows | **ANSWERED in substance; historical prefix unchanged** | `census/round-92/c1-false-rows.tsv:66` names every row's round: "the r91 63-row population byte-for-byte (r87-r89 rows; r90 LD2b; r91 LD1c LD3 LD4 NF6i2 NF6j), plus ONE exit-polarity row (r92 LD4r)…". Lines 1-2 still self-describe as the r87/r82 populations; they cannot be rewritten without breaking the pinned sha, and line 66 corrects them for any reader who reaches it. |

### Draft — `### Planned (r93)` (for the L1's SCORECARD edit; no claim wording is widened)

- **C1 (calibration):** classify or bind the 77 residual survivors (`census/round-92/records/c1-residual-survivors.json`)
  and say which are equivalent mutants (stated limits i, iv); bind the *forge return* named in stated limit ii — it is
  unbound because the harness writes a non-dash `expect_rc` into the forge file as a MISMATCH expectation
  (`census/round-92/controls/nf1r-draft-probe.txt`), so the fix is a separate exit-expectation channel (a harness
  change or a non-forge row type), not a row; extend the census beyond single-token operator edits (limit iv) only if
  a row class justifies it; make the exit polarity a required field (see §6).
- **C2 (operability):** a mirror invalid-lead case on the **head** cut (KFF17 covers the valid U+20AC head cut; no
  case yet puts an ill-formed lead before the head cut, which is where `_cut_head` moved on r91 variants' weaker
  check); measure the prefix/suffix property on a *boundary-class* sweep rather than only the KFF18 token grid (the
  §4 sweep in this seat is the shape: every scalar encoding plus every boundary class of the four second-byte rows);
  keep U+FFFD substitution explicitly out of scope (limit iv).
- **Instruments (both axes):** the three r91 tool variants
  (`census/round-91/variants/{keep-helper,double-backslash,raw-newline}-tool.py`) still move a cut on a lead length
  plus a continuation-only check; either retire them as "before" arms or re-point them at a strict-decode helper
  (§2 C).
- **Carried (unchanged, from `SCORECARD.md` `### Planned (r92)` "Carried"):** p2 basename granularity, p3 the
  punctuation lookahead, p7 `_regular`'s symlink leg, p8 `token_ok`'s hyphen marker, the `fleet:` symlink leg, the
  battery `--only`/`--expect-killed` stale defaults, the r85/r86 C2 list (pid-reuse row, parent-before-child,
  termign-fork/p5-late-term, strace-robust settle), `_regular` pathspec framing, the quarantine intro-blob digest row,
  the r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04, the r17 240 s runners. Plus, from §2: the
  r85-r87 K4 counters' print-only `rc=`.

---

## 4. RFC 3629 §4 vs Unicode Table 3-7 — do they define the same well-formed set?

### Quoted lines (primary captures, read-only)

`census/round-91/srcs/rfc3629.txt` §4 (LF lines 275-291; the ABNF is split by the page break at 282-285):

```
   UTF8-octets = *( UTF8-char )
   UTF8-char   = UTF8-1 / UTF8-2 / UTF8-3 / UTF8-4
   UTF8-1      = %x00-7F
   UTF8-2      = %xC2-DF UTF8-tail
   UTF8-3      = %xE0 %xA0-BF UTF8-tail / %xE1-EC 2( UTF8-tail ) /
                 %xED %x80-9F UTF8-tail / %xEE-EF 2( UTF8-tail )
   UTF8-4      = %xF0 %x90-BF 2( UTF8-tail ) / %xF1-F3 3( UTF8-tail ) /
                 %xF4 %x80-8F 2( UTF8-tail )
   UTF8-tail   = %x80-BF
```

and the §4 NOTE (LF lines 293-296):

```
   NOTE -- The authoritative definition of UTF-8 is in [UNICODE].  This
   grammar is believed to describe the same thing Unicode describes, but
   does not claim to be authoritative.  Implementors are urged to rely
   on the authoritative source, rather than on this ABNF.
```

`census/round-92/srcs/unicode-ch3.txt` (single line; offsets into that text), Table 3-7 caption and rows at offset
140,695:

```
Table 3-7. Well-Formed UTF-8 Byte Sequences  Code Points First Byte Second Byte Third Byte Fourth Byte
U+0000..U+007F 00..7F
U+0080..U+07FF C2..DF 80..BF
U+0800..U+0FFF E0 A0 ..BF 80..BF
U+1000..U+CFFF E1..EC 80..BF 80..BF
U+D000..U+D7FF ED 80.. 9F 80..BF
U+E000..U+FFFF EE..EF 80..BF 80..BF
U+10000..U+3FFFF F0 90 ..BF 80..BF 80..BF
U+40000..U+FFFFF F1..F3 80..BF 80..BF 80..BF
U+100000..U+10FFFF F4 80.. 8F 80..BF 80..BF
```

(with the capture's own note: "cases where a trailing byte range is not 80..BF are shown in bold italic … These
exceptions to the general pattern occur only in the second byte of a sequence", and, offset 141,393: "As a
consequence of the well-formedness conditions specified in Table 3-7 , the following byte values are disallowed in
UTF-8: C0–C1, F5–FF"). The partition rule C2 rests on, D86 at offset 133,443: "Ill-formed code unit subsequences do
not overlap with minimal well-formed code unit subsequences."

### Result

The script transcribes both definitions as per-position range tables, asserts every transcribed token occurs in the
captured text (so the transcription is pinned to the capture, not to memory), and then:

```
RANGE-TABLES identical=True
SWEEP sequences=4207580 disagreements=0 accepted_by_len={1: 128, 2: 3840, 3: 122880, 4: 1048576}
CASE C0 80 (overlong NUL, RFC §3 example): rfc=False tbl=False py=False
CASE E0 80 80 (KFF16 overlong): rfc=False tbl=False py=False
CASE ED A0 80 (surrogate): rfc=False tbl=False py=False
CASE F4 90 80 80 (beyond U+10FFFF): rfc=False tbl=False py=False
CASE F5 80 80 80 (lead F5): rfc=False tbl=False py=False
CASE C2 85 (U+0085): rfc=True tbl=True py=True
CASE F0 90 8C 82 (U+10302): rfc=True tbl=True py=True
CASE F0 80 61 C2 85 (KFF14 tail): rfc=False tbl=False py=False
CASE truncated C2: rfc=False tbl=False py=False
CASE truncated F0 90: rfc=False tbl=False py=False
VERDICT same_set=True sweep_disagreements=0 boundary_disagreements=0 IDENTICAL
EXIT=0
```

Sweep composition: every scalar value U+0000…U+10FFFF encoded (1,114,112 sequences, minus surrogates), plus the
exhaustive 2-byte sweep (65,536) and 3-byte sweep over every candidate lead (C2-EF × 65,536 tails), plus the
ill-formed boundary classes enumerated at their free parameters (leads C0/C1/F5-FF with every tail; the four
second-byte row exceptions E0 80..9F, ED A0..BF, F0 80..8F, F4 90..BF; lone continuation bytes; every truncated
prefix of every scalar encoding at the row boundaries). `accepted_by_len` double-counts across passes; it is printed as
a corroboration, not as a partition of the byte space.

### Verdict

**The two define the same well-formed byte set** — the range tables are identical position by position, and a real
strict decoder agrees with both on every sequence tried (0 disagreements). They are **not the same specification
surface**, and the difference is exactly the one C2 depends on:

1. **§4 is a whole-string grammar.** `UTF8-octets = *( UTF8-char )` says a *string* is valid iff it partitions into
   `UTF8-char`s; it has no term for the sequence a cut lands inside. Table 3-7 with D84a-D86 supplies the *minimal
   well-formed code unit subsequence* and the partition rule ("Ill-formed code unit subsequences do not overlap with
   minimal well-formed code unit subsequences"). C2's cut rule — which single sequence straddles the cut — is
   expressible in Table 3-7/D86 and not in §4 alone.
2. **§4 disclaims authority** for exactly this reason ("does not claim to be authoritative. Implementors are urged to
   rely on the authoritative source").
3. Consequence for the routed item: **range checks grounded on §4 are byte-identical to Table 3-7-grounded range
   checks** (proved above), so the r92 tool's strict-decode rule and a §4 range check agree on every candidate — but
   §4 syntax alone cannot state "do not consume the successor bytes of the next well-formed sequence", which is the
   sentence the r91 defect violated. r92 grounds that sentence on S355 (Unicode), not on §4; both are consistent, and
   the claim's own words ("strict decode = every Unicode Table 3-7 row; S355") name the right authority.

---

## 5. Falsification ledger

**NO-FALSIFICATION.** What I tried, and why nothing in the round cache or instruments contradicts a stated sentence:

- C1 numbers my scan could touch: 63 r91 rows, exactly 7 asserting an exit code and **all 7 are rc=1** (so "no r91
  row asserts exit code 0 on success" holds); the r92 population is the r91 file plus exactly one comment line and
  `LD4r` (diff `65a66,67`), sha `f66341fc…`; the harness's match rule is the one the claim describes
  (`census/round-92/c1-false-row-harness.py:463,484`); the counter is unchanged (`fd0a8e24…`).
- C2 sentences my sweep could touch: strict decode accepts exactly Table 3-7's sequences and rejects C0/C1/F5-FF,
  overlong E0 80 80, surrogate ED A0 80, F4 90 80 80 and every truncated prefix; the fixed tool's rule is
  strict-decode-exactly-one-character (`tools/souji-record-agreement.py:225-232`); the KFF14 payload
  `F0 80 61 C2 85` contains exactly one well-formed sequence (`C2 85`), so "an ill-formed lead absorbed bytes of the
  next well-formed sequence" is a true description of the r91 behaviour, not a rewritten one.
- Nothing here narrows or widens a claim; §2's family observations are about *other* instruments (r85-r87 counters,
  r91 variants, the dash default), none of which the claims name as bound.

One honesty note (not a falsification, and already a stated limit): the K4 regression the C2 predicate names
(`census/round-87/c2-k4-counter.py`) cannot see a tool that prints the right marker rows and exits non-zero, and the
r92 fixture compares cells without testing the tool's return code (§2 B); only the forgery probe binds polarity
(`census/round-92/c2-forgery-probe.py:82,100`). The claim as worded (`SUMMARY rows=12 mismatches=0 errors=0`,
`tool_pass=20`) is therefore true without binding the tool's success polarity — consistent with the claim, which
never asserts an exit code for the tool.

---

## 6. One bounded proposal (connector role)

**Evidence.** §2 A and B: the C1 harness's `expect_rc == "-"` short-circuit (`census/round-92/c1-false-row-harness.py:463,484`)
is the default on 56 of 64 r92 rows, and the r85-r87 K4 counters print `rc=` without ever testing it
(`census/round-87/c2-k4-counter.py:337` vs `:300-341`). r92 kills one mutant (`LD4r`), not the class.

**Move.** In r93, make exit polarity a *required* field rather than a default: (i) the C1 harness refuses a
population in which a row whose expected verdict is a resolving class carries `expect_rc "-"` (or, minimally,
requires at least one `rc=0` row per run), and (ii) a **new** K4 counter (the r85-r87 files are frozen and must not be
edited) computes `ok` including `p.returncode`. Affected axes: **calibration** (a mutant that exits non-zero on
success can no longer survive any population built on the row type) and **operability** (the K4 counter binds the
tool's success polarity it currently only prints). Nothing else moves: instruments only, no claim wording, no
SCORECARD number.

**Risks.** (a) The harness writes a non-dash `expect_rc` into the forge file as a MISMATCH expectation
(prereg stated limit ii; `census/round-92/controls/nf1r-draft-probe.txt`), so requiring rc on *forge* rows would go
red on the pristine counter — the requirement must apply to lane/ledger rows, or the exit expectation must travel in a
separate channel. (b) A mandatory rc=0 row couples every future population to the counter's success path; a
legitimate counter redesign then updates the row, it does not widen a claim. (c) Editing the frozen r85-r87 counters
is forbidden, so the K4 change must land as a new instrument, not as a patch to the regression the C2 predicate
names.

**Verification.** Re-run the r92 predicate unchanged (must stay `SUMMARY cases=20 tool_pass=20 before_pass=16`,
`FORGERY-SUMMARY forgeries=5 rejected=5 positive=pass`, `SUMMARY rows=12 mismatches=0 errors=0`), then run the new
counter under two populations: (1) a counter that exits 1 on success must be **killed** on the new population and
(2) must **survive** on the r92 population — that pair is what proves the row-type requirement, not the row content,
does the work.
