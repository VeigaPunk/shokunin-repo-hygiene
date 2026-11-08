# S87Scribe — draft knowledge section for `corpus/knowledge/`

Seat: S87Scribe (scribe). Draft for the L1 to integrate. Nothing committed; no lane file edited. Target file
name proposed below; the section body is the deliverable.

## Integration note for the L1 (read first)

The lane's working tree ALREADY carries an untracked `corpus/knowledge/machine-parsed-path-spelling.md`
(mtime 2026-11-08 06:45, i.e. after the wave started; 57 lines; titled "A machine-parsed path stream carries raw
names; the record a human reads needs its own escaping"). It covers the same `-z` ground as the section drafted
below AND the `-F`/declaration-search half, and its `## Gate` section already lists the S346 and S347 rows. The
SOURCES `used-by` cell of BOTH new rows names that file, so the cheap integration is one file, not two.

Two consequences for the L1 (this seat's recommendation, not a decision):

1. **Do not file a second file with the same ground.** If the drafted section below is wanted as a separate file,
   `corpus/SOURCES.md`'s S346 `used-by` cell must name it too, and the S347 half of the existing file must not
   restate the `-z` ground. The lane's rule 4 says expansion is knowledge, not rows; two entries carrying the same
   `-z` clause is the duplicate scope the corpus census reports as a warning class.
2. **The existing file has no `source:` / `verified-at:` / `recheck:` front-matter.** The lane's dominant knowledge
   convention is those three lines, and `corpus/QUALITY.md` Q1 (`applies-to: knowledge`) tests exactly that: "the
   entry's `verified-at:` names a version; its `recheck:` runs on the host version". The drafted section below
   carries them, so the simplest integration that satisfies Q1 is to REPLACE the existing file's first section with
   the section below (keeping its `-F` half and its `## Gate` section), or to ADD the front-matter to the existing
   file. Either way the L1 must not end up with a `verified-at:`-less entry.

Recommended target path if it is filed as its own file: `corpus/knowledge/machine-parsed-status-stream.md`.

---

## Draft section body (40 lines; the `##` headings are the entry's own)

```markdown
source: S346 — git-status(1) as installed (git 2.56.0-1, `/usr/share/man/man1/git-status.1.gz`; capture
census/round-87/srcs/git-status.1 sha256 52d34e3a41e59a1683ac36ab7013a63e8701bfd687ab98c7630419676a2b2d95,
opened 2026-11-08); the lane's own r86 entry `corpus/knowledge/filter-filemode-witness.md` §r86 (the C-escaped
record path) and `corpus/lessons/round-86.md` M2 / Q159.
verified-at: 2026-11-08, git 2.56.0 on this host — the installed page decompressed byte-for-byte to the capture
(`gzip -dc /usr/share/man/man1/git-status.1.gz | cmp - census/round-87/srcs/git-status.1`), the `-z` paragraph read
at roff line 698 and the Pathname Format Notes at roff lines 1099-1104, and both encodings of one newline-carrying
path observed live in a scratch fixture (`?? "bad\nname.txt"` in the line form, `?? bad<LF>name.txt` in the `-z`
form).
recheck: `gzip -dc /usr/share/man/man1/git-status.1.gz | cmp - census/round-87/srcs/git-status.1 && grep -nF
'filenames containing special characters are not specially formatted' census/round-87/srcs/git-status.1` must print
the capture line 698, and the same `cmp`+`grep` pair must still hold for `census/round-87/srcs/git-grep.1`; then
re-run `python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work <scratch>` and read
KN3 `named=yes` (the record cell is the C-escaped raw path, not git's quoted spelling).

# A machine-parsed status stream carries raw names

`git status --porcelain` and `git status --porcelain -z` are the same status field in two different path encodings,
and a parser reads a different NAME from each.

## What the NUL form guarantees

With `-z`, "filenames containing special characters are not specially formatted; no quoting or backslash-escaping is
performed" (S346, OPTIONS `-z`, roff line 698): the stream carries the path's raw bytes, each field terminated by a
NUL, with a space still separating the status pair from the first filename. The same page's Pathname Format Notes
(roff lines 1099-1104) say it twice: with `-z` "pathnames are printed as is and without any quoting".

## What the line form guarantees instead

Without `-z`, "pathnames with \"unusual\" characters are quoted as explained for the configuration variable
core.quotePath" (S346, same capture, roff line 1104). So the line form does not carry a path either: it carries git's
C-QUOTED SPELLING of one. Measured in a scratch fixture, one untracked file named `bad<LF>name.txt` is `?? "bad\nname.txt"`
in the line form and `?? bad<LF>name.txt` in the `-z` form. A parser that takes `line[3:]` of the line form therefore
records the spelling `"bad\nname.txt"` — quotes and a two-character `\n` — which is not a name any reader can act on.

## The record-format rule that follows

Parse raw, render escaped: the tool reads the NUL form and the record a human reads carries the tool's own escaping.
The lane's r86 entry already owns the reader's half — a path name is not a safe detail string, so a detail carrying
one is C-escaped and one record stays one physical line (`corpus/knowledge/filter-filemode-witness.md` §r86;
`corpus/lessons/round-86.md` M2, Q159) — and r87 moved the parse to the NUL form and kept the escape. The two duties
are separate: the parser's escaping is ABSENT in the `-z` form, which is exactly why the reader's cannot be.

## What this does not cover

The `-z` form's own shape carries one trap: a rename record is `XY <new>\0<old>\0` and the second field has no status
pair. Skipping it by CONTENT (asking whether the third byte looks like a separator) is not a record-structure rule —
measured on the lane's committed bytes, a rename whose old path has a space at byte 2 makes the tool emit a phantom
row naming the old path's tail. Skip by the STATUS LETTER (`R`/`C`), as the receipt writer does. And the escaping
stays the tool's own: only newline, tab and CR are escaped, so another control byte still lands raw in the record.
```

### Line count of the drafted section body

The block above is 40 lines including the three front-matter lines and the five `##` headings; the section body
proper (from `# A machine-parsed status stream carries raw names` to the end) is 30 lines. Both are inside the
<=40-line bound the seat spec sets.

### Citations the L1 should check before filing

- S346 is the only SOURCES row the section leans on; the `-F`/git-grep half is deliberately NOT in this section (it
  belongs to the existing `machine-parsed-path-spelling.md` file or a sibling entry).
- The r86 entry is cited twice: `corpus/knowledge/filter-filemode-witness.md` §r86 (the record-format rule) and
  `corpus/lessons/round-86.md` M2 with Q159 (the criterion that carries it). Both exist at the lane tip: the §r86
  section header is at `corpus/knowledge/filter-filemode-witness.md:388`, and Q159 is at `corpus/QUALITY.md:395`.
- The `-z`/line-form measurement in "What the line form guarantees instead" was taken by this seat in a scratch
  fixture (`/fast/scratch/hyaku/souji-r87/S87Scribe/`, deleted before yield); the raw bytes are in
  `.ufo/waves/round-87/w1/S87Scribe/quote-verification.txt` §2-3.
- The rename-phantom sentence is not a new claim of this seat's: S87ExecC2 measured the same class independently
  (their F3). This seat reproduced it on the lane's COMMITTED bytes before reading their report; the reproducer is
  in `quote-verification.txt` §7. The L1 should cite ONE source for it (S87ExecC2's F3) rather than two.
