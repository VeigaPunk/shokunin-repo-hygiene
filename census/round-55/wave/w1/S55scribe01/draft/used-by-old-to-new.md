# DRAFT — the used-by old→new line for the round-55 lesson's `## Gate`

Drafted by seat S55scribe01 (scribe), 2026-11-03. For the L1 to integrate into
`corpus/lessons/round-55.md` `## Gate`. **Not applied by this seat** — the lane's
`corpus/SOURCES.md` was not written by this seat.

## Why a used-by change is needed at all

`corpus/knowledge/splitlines-line-model.md` (the new r55 entry) cites **S277** in its
front-matter `source:` line — the verbatim text is:

```
source: S278 — Python 3.12 library reference, str.splitlines (…). Consumer of the fence
grammar admitted in S277 (corpus/knowledge/correction-filing-fence-grammar.md), which it
extends to one line model.
```

`corpus/QUALITY.md` **Q62** makes the citation bidirectional: *every S-id an entry's
front-matter `source:` lines cite must be a row that lists that entry in `used-by`.* The
instrument that checks it is `tools/souji-registry-agreement.py` (K1), whose
`cited-not-in-used-by` arm prints one line per disagreement.

S277's `used-by` cell in the current `corpus/SOURCES.md` lists only the r54 entry, so
until the cell is changed the K1 check at the r55 landing revision prints:

```
K1 cited-not-in-used-by S277 corpus/knowledge/splitlines-line-model.md
```

**Measured by this seat** (the tool's own K1 logic, replayed read-only over the working
tree; the tool itself reads committed revs only, so the seat could not run it against the
still-unlanded new entry — receipt `../receipts/k1-bidirectional-receipt.txt`).

## The line to land (old → new)

- **old:** S277 `used-by` = `corpus/knowledge/correction-filing-fence-grammar.md`
- **new:** S277 `used-by` =
  `corpus/knowledge/correction-filing-fence-grammar.md, corpus/knowledge/splitlines-line-model.md`

In the lesson's `## Gate`, in the house shape of the r54 precedent
(`corpus/lessons/round-54.md`, the S276 reuse bullet):

```
- Reuse (no new row, used-by cell changed): **S277** — CommonMark spec 0.31.2, § 4.5
  Fenced code blocks and § 4.6 HTML blocks, "A code fence is a sequence of at least three
  consecutive backtick characters (`) or tildes (~)." (17 words). Grounds the fence and
  HTML-comment half of the one line model; the new r55 entry
  (`corpus/knowledge/splitlines-line-model.md`) is the consumer of the S277 grammar and
  extends it to the line-numbering half. Status changes old→new, logged here as required:
  S277 `used-by` `corpus/knowledge/correction-filing-fence-grammar.md` →
  `corpus/knowledge/correction-filing-fence-grammar.md, corpus/knowledge/splitlines-line-model.md`
  (the new entry cites S277 in its `source:` line, so Q62's bidirectional rule requires
  the cell to name it). S278 landed as `mined` in the same commit that lands its citing
  entry (`corpus/knowledge/splitlines-line-model.md`); `queued` → `mined`.
  No other existing row's status, recheck or used-by cell changed.
```

## The L1's landed lesson currently says the opposite — the conflict, verbatim

`corpus/lessons/round-55.md:38-40` (landed by the L1 while this seat was measuring):

```
- Reuse: **S277** (CommonMark 0.31.2 §4.5/§4.6) and **S276** (gitignore PATTERN FORMAT) are
  cited by the r54 knowledge entries and unchanged this round. No status, recheck or used-by cell of an
  existing row changed. The S278 row's used-by is `corpus/knowledge/splitlines-line-model.md`.
```

The last sentence of that bullet ("The S278 row's used-by is …") is right. The middle
sentence ("No status, recheck or **used-by** cell of an existing row changed") is **wrong**,
because the new entry's `source:` line cites S277 and Q62 requires the reciprocal cell.

Re-verified by this seat against the tree as it stands after that landing: the K1 delta is
still exactly `K1 cited-not-in-used-by S277 corpus/knowledge/splitlines-line-model.md`
(receipt `../receipts/k1-bidirectional-receipt.txt`).

**Two ways to close it — the L1's choice, not this seat's:**

- (a) change the S277 cell as above and rewrite the reuse bullet to log the old→new change
  (the r54 precedent for S276; the house-shaped bullet is in this file); or
- (b) drop the S277 citation from the new entry's front-matter `source:` line — the entry
  already names S277 in its prose and in its "What this entry does not establish" section, so
  the S277 fence-grammar link stays legible, and the K1 arm goes quiet.

## Rows whose status does NOT change

- **S278** is a **new** row (not yet in the registry at HEAD; the seat's working tree has
  it drafted). It lands `mined` together with its citing entry — the r54 precedent for
  S277. There is no old→new for S278 itself, because it had no prior registry cell.
- **S277** status stays `mined`; its `recheck` cell stays `on-release`. Only its `used-by`
  cell changes.

## The two pre-existing K1 disagreements are NOT this round's

The same replay also prints two disagreements that are **already present at HEAD**
(`3ce0ba036275f3bbd7a74bde1fecd7ec60f4c58f`) and are therefore **not** caused by the
r55 landing. They are recorded here so the L1 does not attribute them to the S278 work:

```
K1 cited-no-row S146 corpus/knowledge/origin-record-format-gvfs-r40.md
K1 cited-not-in-used-by S110 corpus/knowledge/quarantine-restore-path-reoccupied.md
```

Both are pre-existing lane state; the r55 round does not touch either row or entry. The
L1 decides whether to route them (they are out of this seat's scope).
