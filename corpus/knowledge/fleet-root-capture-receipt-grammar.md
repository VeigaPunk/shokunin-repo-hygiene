source: S276 — gitignore(1) manual, PATTERN FORMAT, comment lines (https://git-scm.com/docs/gitignore; anchor section "PATTERN FORMAT", served bytes sha256 8b10cfe3d03aabce47fb5259b00d6ac7071d9c2c034d6b4410cbc2abaa983fcd, accessed 2026-11-03); the fleet-root capture counter census/round-53/c2-counter.py (v2)
verified-at: 2026-11-03 — capture census/round-53/records/fleet-root-census.tsv (ENTRIES=49, FLEET_HEAD 6e312f2e…, TOOL_SHA256 e7e79952…; run receipt census/round-53/records/fleet-root-census-run.txt in the RECEIPT_VERSION=1 grammar); located quote census/round-53/sources/s276-located-quote.txt (9 words, "A line starting with # serves as a comment."); page capture census/round-53/sources/s276-gitignore-page.html (50560 bytes, sha256 8b10cfe3…fcd)
recheck: python3 -B census/round-53/c2-counter.py --root <lane> --rev <full40> --capture census/round-53/records/fleet-root-census.tsv --receipt census/round-53/records/fleet-root-census-run.txt --scratch DIR (the committed capture verifies: SUMMARY entries=49 rows=49 … receipt=ok sorted=ok, exit 0)

# Fleet-root capture receipt grammar (read-only capture, receipt-bound)

## What this entry is

The grammar of the fleet-root census capture and its run receipt, and the three checks the
round-53 counter (v2) added on top of the round-52 counter (v1). The capture is a read-only,
dry-run TSV of the fleet root's top-level entries; the receipt is the machine-readable block
that says which tool bytes, which fleet head and which capture bytes the take is. The
counter is the instrument that decides whether a committed capture plus its committed
receipt verify.

## The RECEIPT_VERSION=1 grammar

The receipt carries a machine-readable block of exactly five keys, one per line, each line
shaped `# KEY=VALUE` (the counter's own matcher is the full-line regex
`# (RECEIPT_VERSION|TOOL_SHA256|FLEET_HEAD|CAPTURE_SHA256|ENTRIES)=(\S+)`):

| key | form | must agree with |
|---|---|---|
| RECEIPT_VERSION | `1` | the literal string `1`; any other value is a malformed receipt |
| TOOL_SHA256 | 64-hex | the sha256 of `tools/souji-fleet-root-census.py`'s bytes at the measured revision, AND the capture header's `TOOL_SHA256` |
| FLEET_HEAD | 40-hex | the capture header's `FLEET_HEAD` |
| CAPTURE_SHA256 | 64-hex | the sha256 of the capture's own committed bytes |
| ENTRIES | decimal integer | the capture header's `ENTRIES` AND the recounted number of data rows |

Any deviation from the shape (a missing key, an extra key, a duplicated key, a non-hex or
non-decimal value) is `RECEIPT-MALFORMED`; any value that disagrees with the bytes it names
is `CAPTURE-RECEIPT-MISMATCH`. Both are exit 1.

The round-53 take, as committed:

```
# RECEIPT_VERSION=1
# TOOL_SHA256=e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b
# FLEET_HEAD=6e312f2ecd1378c122e08bbbc9a00eff582d0cf6
# CAPTURE_SHA256=922112361cdd257451e2f62820815ce19493c7d94d06c73c1b40f5dc9756f904
# ENTRIES=49
```

## The three checks v2 added (the r52 named limits, closed)

1. **ROWS-UNSORTED** — data rows must be in ascending byte order of name. The v1 counter
   never looked at order, so a reversed capture verified. The v2 counter compares each row's
   name bytes against the previous row's and fails with `ROWS-UNSORTED` on any descent.
2. **COMMENT-AMBIGUOUS-NAME** — a comment line shaped like a 6-field data row is refused.
   The v1 counter read such a line as a comment and lost the row silently. The v2 counter
   fails with `COMMENT-AMBIGUOUS-NAME`. The v2 matcher is `^#\S*(\t\S+){5}$`, so it fires on
   a `#`-leading row whose name has no whitespace; see the named limits for the shape it
   does not cover.
3. **CAPTURE-RECEIPT-MISMATCH** (with `RECEIPT-MALFORMED`) — a capture verifies only against
   its RECEIPT_VERSION=1 run receipt. The v1 counter bound the capture to the committed tool
   bytes and the grammar, but not to a run: a hand-written capture with the right tool bytes
   verified. The v2 counter adds the receipt binding described above.

Every r52 check carries over unchanged: the header grammar (TOOL_SHA256 equals the tool
bytes at the revision, FLEET_HEAD is 40-hex, ENTRIES equals the row count and is at least 1,
one COUNT line per class matching the recount), the row grammar (6 tab-separated fields,
unique name without `/`, name != `.git`, frozen enumerations, the frozen class rule,
disposition `report-only` only for untracked-stray), and `removal_proposed == 0`.

## Why the gitignore '#' rule grounds the comment-ambiguity refusal

gitignore(1), section PATTERN FORMAT, says (located quote, 9 words — full receipt in
`census/round-53/sources/s276-located-quote.txt`):

> A line starting with # serves as a comment.

The same paragraph then states git's own escape for the case at hand: a pattern that is
meant to begin with a hash must have a backslash put in front of the first hash (17 words,
also verified a substring of the same captured bytes).

The fleet-root capture grammar is a plain TSV: a leading `#` marks a comment line, and the
grammar defines **no escaping** for a `#`-leading name. So a `#`-leading data row in a
capture is ambiguous — it reads as a comment, and the entry it claimed to carry disappears
from the census without any row recording that anything was lost. The capture grammar
therefore cannot carry such a name at all: the v2 counter refuses the capture fail-closed
with `COMMENT-AMBIGUOUS-NAME` rather than guess which reading was meant. The refusal is
the grammar's own rule, and the located quote is what grounds it: a `#`-leading line is a
comment in the reference grammar, and a format with no escape for it has no second reading
to fall back on. (Measured scope of the refusal: the v2 matcher recognises a `#`-leading
row only when the name has no whitespace — see the named limits.)

This is the S276 grounding for the C2 comment-ambiguity refusal. The page does not define
the capture grammar, the five-key receipt, or the counter's finding ids; those are the
lane's own instrument (`census/round-53/c2-counter.py`) and preregistration
(`census/round-53/preregistration.txt`, claim C2).

## Named limits (disclosed, not fixed)

- The receipt binds **consistency, not authenticity**. It proves that the receipt, the
  capture's committed bytes and the tool's committed bytes agree with each other. It does
  not prove that a run happened: a hand-written receipt whose digests match still verifies.
  This is the same trust level as the r52 committed-bytes rule, unchanged.
- **ENTRIES remains the tool's own count.** A capture that silently omits an entry and
  lowers `ENTRIES`/`COUNT` accordingly is undetectable from the committed bytes alone; the
  r52 limit stands, carried into v2. The receipt cannot repair it either: the receipt's
  `ENTRIES` must agree with the capture, so a lowered count is self-consistent.
- `FLEET_HEAD` is format-checked (40-hex) and cross-checked between the receipt and the
  capture header, but it is not resolved against the fleet repository. An optional live
  check stays out of the counter by design.
- The v1 counter remains the standing do-nothing control for the r52 capture: v2 is not
  retrofitted to `census/round-52/records/fleet-root-census.tsv`.
- **The comment-ambiguity refusal is narrower than "a `#`-leading row".** Measured with
  the frozen v2 counter over four throwaway fixtures (receipt
  `census/round-53/sources/s276-comment-shape-matrix.txt`): the v2 matcher
  `^#\S*(\t\S+){5}$` recognises a `#`-leading DATA row only when the row's first field
  contains no whitespace. A `#`-leading row whose name contains a space is read as an
  ordinary comment and is silently dropped — and when `ENTRIES`/`COUNT` are struck to
  match the rows that survive, the capture verifies green (v2 exit 0). The
  `ENTRIES`-remains-the-tool's-own-count limit above is what covers that residue, but the
  refusal itself does not fire on that shape. The committed tool can emit such a row: it
  refuses only names containing a tab or newline, so a top-level entry named `#odd dir`
  is emitted verbatim (measured). Named limit, disclosed, routed to the next round; the
  frozen counter bytes are not edited.

## The census is a dry run

Nothing in this grammar removes, moves or proposes for removal anything. A flagged entry
is an operator decision with its own receipt. The counter asserts `removal_proposed == 0`.
