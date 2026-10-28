source: S253 Python `codecs` error handlers (https://docs.python.org/3/library/codecs.html#error-handlers; snapshot census/round-40/sources/codecs.html, sha256 023ec448648e7089efe4b4c25a167e491fa7f93d1cbf116662c6596e71158a4c; installed interpreter Python 3.14.8)
verified-at: 2026-10-28 — Python 3.14.8 on kernel 7.2.11-arch1-1; read-only (the record bytes were written under a scratch root; no lane record was touched)
recheck: 365d — re-read the `replace` handler entry after a Python release: `python3 -c "print(b'a\xffb'.decode('utf-8','replace'))"`
ground: F1 — git-native housekeeping vs receipts (the record-file contract the lane's F1 worktree-drift detector parses)

# An undecodable byte in a drift record becomes U+FFFD, and the schema accepts it

## Claim (F1, sourced)

Python's `replace` error handler replaces an undecodable byte with the replacement character:
"Replace with a replacement marker. On decoding, use U+FFFD, the official REPLACEMENT CHARACTER"
(S253, `codecs` § Error Handlers, the `replace` entry; snapshot
`census/round-40/sources/codecs.html`).

`tools/souji-worktree-drift.py` decodes its record with exactly that handler
(`raw = b"".join(chunks).decode("utf-8", "replace")`), so an undecodable byte inside a `REPO` name
does NOT make the record malformed: the census schema accepts any non-tab name
(`ROW = re.compile(r"^REPO\t(?P<name>[^\t]+)\t...")`), and the record row survives with U+FFFD in the
name. The repository is then reported ABSENT, because no work tree carries that name.

## Why this is worth a knowledge entry

The branch was invisible to every committed fixture, and the obvious guess is wrong in both
directions:

- a byte inside a `REPO` name is ACCEPTED (the schema does not constrain the name) → the drift row
  is ABSENT, not a refusal;
- a byte inside a COMMENT line is tolerated completely — the line is skipped before the schema is
  checked → the record parses and the run reports its normal summary.

A counter or a fixture that assumes "invalid bytes ⇒ RECORD-MALFORMED" would be wrong on both.

## Evidence

`python3 -B tests/fixtures/r40-drift-record-branches.py` → `SUMMARY cases=8 pass=8 fail=0` at the
audited revision; the two paired cases are `case-invalid-utf8-in-repo-name` (rc 1, `ABSENT`) and
`case-invalid-utf8-in-comment` (rc 0, `record_repos=2`) — see
`census/round-40/records/c3-after.txt`.

## Limits

- The claim is about the `replace` handler and this record schema; a different handler (`ignore`,
  `surrogateescape`) yields a different reading, and the r40 C3 battery scores that difference as
  mutant M17.
- The entry says nothing about a record whose bytes are not valid UTF-8 at all as a whole file; the
  tool decodes the concatenation of its chunks, so a byte split across a 64 KiB chunk boundary is
  still decoded as one stream.
- No lane record was read or written while this was measured; the fixture wrote its own bytes under
  a scratch root and removed it.

## Round 40 wave-2 source/fixture correction (append-only)

S253's quoted text was spliced and not verbatim at the cited page; S256 gives the exact
`codecs.replace` decoding clause. The tool's decoded U+FFFD behavior is supported by S256 plus the
tool's `decode(..., "replace")` implementation, but the r40 fixture only asserted the resulting
`ABSENT` class, not the U+FFFD character itself. W2 mutation probes showed alternate non-fatal
decoders can satisfy both invalid-byte cases; see `corpus/lessons/round-40.md` M40-4. This entry's
behavioral claim is code-inspected and bounded, not fully isolated by the fixture.
