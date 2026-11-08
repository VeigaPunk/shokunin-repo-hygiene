# A machine-parsed path stream carries raw names; the record a human reads needs its own escaping

source: S346 (git-status(1) `-z`), S347 (git-grep(1) `-F`); scored against tools/souji-record-agreement.py and
tools/souji-receipt-write.py at round 87.
verified-at: git 2.56.0-1, python 3.14 (the lane's tools), 2026-11-08.
recheck: 90d, or on any git minor bump (the `-z` contract is stable; the quoting rule is not).

Round 87 (C2 KN3, C1 TQ1). Ground: S346 (git-status(1) `-z`), S347 (git-grep(1) `-F`).

## What the two streams promise

`git status --porcelain` and `git status --porcelain -z` are the same status field and two different path
encodings. The line form quotes a path that carries a newline, a tab or another "unusual" character through
`core.quotePath`'s rule; the NUL form does not quote or backslash-escape at all (S346, roff line 698). A tool that
parses the line form with `line[3:]` therefore receives a *spelling of the path*, not the path: for a file named
`bad<LF>name.txt` it records `"bad\nname.txt"` — quotes and a two-character `\n` — and a reader who pastes that
into a shell names a different file. A tool that parses the NUL form receives `bad<LF>name.txt`, and a reader who
prints it raw gets two physical lines for one record.

So the two duties are separate and both are needed: **parse raw** (`-z`), **render escaped** (the tool's own
C-escape for the record cell). The lane's K4 arm learned both in opposite order — r86 escaped the FORGED detail
while still reading the quoted line form (C2 KN3's before arm), and r87 moved the parse to the NUL form and kept
the escape.

The NUL form's own shape carries one trap: a rename record is `R  <new>\0<old>\0`, and the second field has no
status pair. A parser that takes every field as a record names the old path with its first three characters cut off.
The skip must be decided by the **status letters**, not by the field's shape: a content test for "two characters and
a space" admits an old path that happens to begin that way (`my file.txt` reads as status `my`, and the record names
a file that does not exist), which round 87's wave measured on the first `-z` implementation and the receipt writer
already avoids by skipping on `R`/`C` (`tools/souji-receipt-write.py`, its `_porcelain_paths`). Skip exactly one field
after a record whose status contains `R` or `C`; the record itself already reaches the key.

## What a declaration search promises

`_declared` in `census/round-87/c1-pointer-counter.py` decides whether a committed line names both a token and its
quarantine path. It calls `git grep -F -e <target>`; `-F`/`--fixed-strings` takes the pattern literally instead of
as a regex (S347, roff line 212). That matters because the patterns are *paths*: `corpus/.../round-79-collision.md`
and `.ufo/quarantine/.../lemma-stub` both contain `.` and `/`, and a regex reading of `.` matches any character, so
a regex search would find declarations for paths the row never names. The literal search is the load-bearing half;
the `_whole` boundary test is the other (a path that is a substring of a longer path is not a declaration of the
short one).

## Boundary

This entry records encoding contracts of two installed git pages and the lane's own repair. It is not a claim that
every control byte is escaped (only newline, tab and CR are), not a claim that a rename's old path is named by the
status arm's own row (it is named by the rename record), and not a claim that a fixed-string search proves the
declaration's intent.

## Gate

- **S346 — git-status(1) as installed** (git 2.56.0-1, `/usr/share/man/man1/git-status.1.gz`, capture
  `census/round-87/srcs/git-status.1` sha256 `52d34e3a…`, opened 2026-11-08). Quote, OPTIONS `-z`, roff line 698:
  "filenames containing special characters are not specially formatted; no quoting or backslash-escaping is
  performed". **ADMIT**, `docs`, tier A, `mined` — it grounds C2 (a) KN3's decision rule. Duplicate-URL check: the
  installed page is cited by S302 and S341 for other scopes; this row names the `-z` spelling rule only.
- **S347 — git-grep(1) as installed** (same git, `/usr/share/man/man1/git-grep.1.gz`, capture
  `census/round-87/srcs/git-grep.1` sha256 `52603128…`, opened 2026-11-08). Quote, OPTIONS `-F`, roff line 212:
  "Use fixed strings for patterns (don't interpret pattern as a regex)." **ADMIT**, `docs`, tier A, `mined` — it
  grounds the declaration search C1's TQ1 row rides on.
- **Rejected — git-config(1) `core.quotePath`** (same git, `/usr/share/man/man1/git-config.1.gz`, opened
  2026-11-08). The page states the line form's escape rule itself (double quotes; C-style escapes for TAB, LF and
  backslash) and then its default and value range, so it is not merely a pointer. It is **REJECTED** on the narrower
  ground that this lane consumes the `-z` form, whose spelling the variable does not affect: the row would add no
  decision for the surface the lane parses. **Flip:** a round that starts parsing the line form, or must decide which
  spelling a caller's `core.quotePath` selects, needs this row and its default/value paragraph.
