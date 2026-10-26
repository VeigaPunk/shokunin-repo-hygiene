## Status
STATUS: PASS — all 8 assigned C1 items (L13-L20) now have honest record bindings; the frozen counter reads
MATCH for each twice in a scratch clone, and two forced control rows read RECORD-MISMATCH.

## Evidence

Base lane **9f17a1ef571f3a510a51ac233d7cf50ac0c871fc**, list-rev **1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525**,
measured tip **1b811368461785040e955f41f9c97e62f61fd67c** (`SCORECARD.md` byte-identical to base:
`git diff --stat 9f17a1e..1b81136 -- SCORECARD.md` empty).

Base state of the eight items (red before), `--only` on the lane:

```
ITEM	L13	SCORECARD.md:163	literal=12/9	base-cell	binding=-	UNBOUND
ITEM	L14	…	literal=12/0	…	UNBOUND
ITEM	L15	…	literal=69/0	…	UNBOUND
ITEM	L16	SCORECARD.md:164	literal=61/0	…	UNBOUND
ITEM	L17	…	literal=11/0	…	UNBOUND
ITEM	L18	…	literal=15/0	…	UNBOUND
ITEM	L19	SCORECARD.md:165	literal=27/27	…	UNBOUND
ITEM	L20	…	literal=6/27	…	UNBOUND
SUMMARY items=8 bound_run=0 bound_record=0 unbound=8 mismatches=8 partial=1 rev=1b811368461785040e955f41f9c97e62f61fd67c
```

Proof (scratch clone, origin removed, rows appended under `### Round 31 capability-cell supersessions`,
commit `1edc8240a1a7ff5eb5e1a148d2c01f83bd253c2c`; run twice, byte-identical output):

```
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-capability-cells.py --root /fast/scratch/hyaku/souji-r31/C1BindC/c \
  --rev 1edc8240a1a7ff5eb5e1a148d2c01f83bd253c2c --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc \
  --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 --only L13,L14,L15,L16,L17,L18,L19,L20 \
  --scratch /fast/scratch/hyaku/souji-r31/C1BindC/cnt
ITEM	L13	SCORECARD.md:163	literal=12/9	superseded	binding=record	MATCH	census/round-18/final-verification-4800fd7.json
ITEM	L14	SCORECARD.md:163	literal=12/0	superseded	binding=record	MATCH	census/round-18/final-verification-4800fd7.json
ITEM	L15	SCORECARD.md:163	literal=69/0	superseded	binding=record	MATCH	census/round-18/final-verification-4800fd7.json
ITEM	L16	SCORECARD.md:164	literal=pass=61\tfail=0	superseded	binding=record	MATCH	census/round-18/final-verification-4800fd7.json
ITEM	L17	SCORECARD.md:164	literal=total=11\tfailed=0	superseded	binding=record	MATCH	census/round-18/final-verification-4800fd7.json
ITEM	L18	SCORECARD.md:164	literal=total=15\tfailed=0	superseded	binding=record	MATCH	census/round-18/final-verification-4800fd7.json
ITEM	L19	SCORECARD.md:165	literal=total=27	pass=27	superseded	binding=record	MATCH	census/round-21/reason-after.txt
ITEM	L20	SCORECARD.md:165	literal=total=27	pass=6	superseded	binding=record	MATCH	census/round-21/reason-oracle-before.txt
SUMMARY items=8 bound_run=0 bound_record=8 unbound=0 mismatches=0 partial=1 rev=1edc8240a1a7ff5eb5e1a148d2c01f83bd253c2c
rc=0
```

Control (second base clone, forced rows, commit `ec827f76260539553ec195e6f4da524a8fef1171`):

```
ITEM	L13	SCORECARD.md:163	literal=12/9	superseded	binding=record	RECORD-MISMATCH	census/round-18/c1-matrix-4800fd7.json
ITEM	L16	SCORECARD.md:164	literal=61/0	superseded	binding=record	RECORD-MISMATCH	census/round-18/final-verification-4800fd7.json
SUMMARY items=2 bound_run=0 bound_record=0 unbound=0 mismatches=2 partial=1 rc=1
```

Record blobs are unchanged base→tip: `final-verification-4800fd7.json` `0d37a0567b0e87e8407fff24c68800bd4cd4251d`,
`reason-after.txt` `d9b25a31519ce56d6a354b5fd48ba69b696df396`,
`reason-oracle-before.txt` `69dd849885e9c4c139ecd9dd888c7de054241434`.

## Findings

1. **Lines 163-165 admit no `run:` row.** Their cells (`SCORECARD.md:163`, `:164`, `:165` at base) name no
   `tools/` or `tests/fixtures/` script whose basename stem occurs on the line, so the counter's stem rule
   would return `BAD-ROW(run-shape)`; all eight items are record bindings.
2. **Line 163's own cited record cannot carry its literal.** The cell says `` `census/round-18/c1-matrix-4800fd7.json` (12/9 failed →12/0) ``,
   but that file is field-serialized (`"failed": 0`, `"total": 12`) and has no slash form — proven by control
   row L13 = `RECORD-MISMATCH`. The honest record is `census/round-18/final-verification-4800fd7.json`, the r18
   acceptance record whose `matrix-final` check ran `run-matrix.py --changed 4800fd7… --output …/c1-matrix-4800fd7.json`
   and kept that run's stdout: `r18-bounded=12/9fail` (r17-base), `r18-bounded=12/0fail` and `selftest=69/0fail`
   (changed arm at 4800fd7). Same measurement, same measured revision, recorded in a form the counter can read.
3. **Line 164's counts exist only in JSON-escaped form.** The record prints them as
   `SELFTEST\tpass=61\tfail=0`, `SUMMARY\ttotal=11\tfailed=0`, `SUMMARY\ttotal=15\tfailed=0` with a two-byte
   backslash-`t` separator, so L16-L18 restate the counts in the record's own notation (multisets 61/0, 11/0, 15/0
   preserved); the plain slash forms are absent (control L16 = `RECORD-MISMATCH`).
4. **Lines 165's two counts come from two receipts.** `27/27` is the post-repair canary receipt the cell cites,
   `census/round-21/reason-after.txt` line 29 (`total=27`, `pass=27`, `fail=0`, `leaks=0`, `base_leaks=19`);
   `6/27` is the same 27-case canary run against the old tool, `census/round-21/reason-oracle-before.txt` line 49
   (`total=27`, `pass=6`, `fail=21`, `leaks=19`), committed in the r21 repair commit `4d5bf78`. Both use real
   U+0009 separators, so L19/L20 literals carry a real tab between `total=27` and the `pass=` field.
5. **Integration hazard.** The eight rows are byte-sensitive: L16-L18 contain a literal backslash-`t`, L19-L20 a
   real tab. The delivery file's block hashes to
   `da4e633283777d4fab3b7e44a4c37d73b4d763abd6d16770ffead6f25cdebea6`; if a paste turns either separator into a
   space, five items revert to mismatch and one to `BAD-ROW`.
6. **Arrow movement for C1 is real but partial.** These eight move the base tally `unbound=22` by -8 and
   `bound_record` by +8; the remaining 14 unbound literals are other seats' scope. The full 41-item run is
   unrun by me (my proof used `--only`, SUMMARY `partial=1`).

## Risks / notes

- Full-section counter after the L1 appends to the real `SCORECARD.md` is the acceptance gate; not run here.
- The L13-L15 record swap is accepted by the frozen counter and leaves the base cell untouched (append-only), but
  the L1 should be aware the cell's cited matrix JSON cannot satisfy its own literal — a r32 cleanup candidate, not
  a r31 predicate change.
- Tooling: none installed or upgraded this seat (no pacman, no uv/npx; nothing needed).

## Deliveries

- `.ufo/waves/round-31/w1/deliver-c1-bind-L13-L20.md` — verbatim append block (bytes verified, hash above),
  per-item rationale with located quotes, base/proof/control transcripts.
