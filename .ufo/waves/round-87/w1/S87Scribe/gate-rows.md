# S87Scribe — draft `## Gate` rows for the round-87 lesson (S346, S347)

Seat: S87Scribe (scribe). Draft for the L1 to integrate into `corpus/lessons/round-87.md` `## Gate`. Nothing in
the lane was edited; this file and the seat's report are the only writes (plus the scratch under
`/fast/scratch/hyaku/souji-r87/S87Scribe/`, deleted before yield).

Contract: `SOURCES-CONTRACT-v1` (`.ufo/waves/kaika/SOURCES-CONTRACT-v1.md`). Rule 1: "The round lesson's `## Gate`
records, for every new row, the URL, the access date, and a ≤25-word quote with its location grounding `teaches`."
Rule 2: a row is append-only; only `status`, `recheck` and `used-by` change in place.

Registry census on the lane's working-tree `corpus/SOURCES.md` (the L1's own file, uncommitted at the time of
this draft): rows 270, malformed 0, tier A=257 B=10 C=3, status mined=226 queued=14 rejected=30, no duplicate ids,
no enum/tier-inflation violations, no `mined` row naming a non-existent `used-by` path. `268 → 270` for the two
appended rows.

---

## Draft rows to place in `corpus/lessons/round-87.md` `## Gate`

Replace the existing two bullets with these (the wording below is what this seat verified; the URL/access-date/
located-quote triple rule-1 requires is present in each).

- **S346 — git-status(1) as installed** (git 2.56.0-1, `/usr/share/man/man1/git-status.1.gz`, capture
  `census/round-87/srcs/git-status.1` sha256 `52d34e3a41e59a1683ac36ab7013a63e8701bfd687ab98c7630419676a2b2d95`,
  opened 2026-11-08). Quote, OPTIONS `-z`, roff line 698: "filenames containing special characters are not specially
  formatted; no quoting or backslash-escaping is performed". **ADMIT**, `docs`, tier A, `mined` — it grounds C2's KN3
  decision rule: the line form hands a parser git's quoted spelling, the NUL form hands it the bytes. Duplicate-URL
  check: the installed page is already cited by S044, S302 and S338 for other scopes (S338 is the rejected
  status-versus-index row); this row carries one clause none of them holds.
- **S347 — git-grep(1) as installed** (same git, `/usr/share/man/man1/git-grep.1.gz`, capture
  `census/round-87/srcs/git-grep.1` sha256 `52603128b427d0cd8d2bfdc10790958a9d34b8762abc3a3d870504ac3b5b14a6`,
  opened 2026-11-08). Quote, OPTIONS `-F`, roff line 212: "Use fixed strings for patterns (don't interpret pattern as
  a regex)." **ADMIT**, `docs`, tier A, `mined` — `_declared` in `census/round-87/c1-pointer-counter.py:249` runs
  `git grep -h -F -I -e <target>`; the patterns are PATHS (`corpus/.../round-79-collision.md`,
  `.ufo/quarantine/.../lemma-stub`), and a regex reading of `.` matches other paths, so the literal search is the
  load-bearing half of the declaration search TQ1 rides on. Duplicate-URL check: `git-grep(1)` is cited by no other
  row.

### Registry rows (the two `corpus/SOURCES.md` rows, cell by cell)

Both rows are already present in the lane's working-tree `corpus/SOURCES.md` (lines 307-308) with all 11 columns
populated; this seat verified each cell against the contract and against the captures.

**S346**

| cell | value |
|---|---|
| id | `S346` |
| source | git-status(1) as installed (git 2.56.0-1, /usr/share/man/man1/git-status.1.gz; capture census/round-87/srcs/git-status.1 sha256 52d34e3a41e59a1683ac36ab7013a63e8701bfd687ab98c7630419676a2b2d95, roff line 698, opened 2026-11-08) |
| kind | `docs` |
| tier | `A` |
| scope | what `-z` guarantees about a path's spelling in the status stream (scope: the alternate `-z` format paragraph; the `--untracked-files` section's Pathname Format Notes restate the same rule) |
| anchor | OPTIONS `-z`, roff line 698 of the capture: "filenames containing special characters are not specially formatted; no quoting or backslash-escaping is performed" |
| teaches | a machine parser that reads the line form receives git's C-quoted spelling of a path with a newline or a tab, and the `-z` form receives the raw bytes; the record a human reads therefore needs its own escaping, because the parser's is absent |
| status | `mined` |
| opened | 2026-11-08 |
| recheck | `90d` |
| used-by | corpus/knowledge/machine-parsed-path-spelling.md |

**S347**

| cell | value |
|---|---|
| id | `S347` |
| source | git-grep(1) as installed (git 2.56.0-1, /usr/share/man/man1/git-grep.1.gz; capture census/round-87/srcs/git-grep.1 sha256 52603128b427d0cd8d2bfdc10790958a9d34b8762abc3a3d870504ac3b5b14a6, roff line 212, opened 2026-11-08) |
| kind | `docs` |
| tier | `A` |
| scope | what `-F`/`--fixed-strings` asks the search to do (scope: the `-F` option paragraph only; `-I` and the `-e` accumulation are out of scope here) |
| anchor | OPTIONS `-F`, roff line 212 of the capture: "Use fixed strings for patterns (don't interpret pattern as a regex)." |
| teaches | a declaration search that names a path containing `.` or `+` is a literal search only when the pattern is taken as a fixed string; under a regex reading the same pattern matches other paths |
| status | `mined` |
| opened | 2026-11-08 |
| recheck | `90d` |
| used-by | corpus/knowledge/machine-parsed-path-spelling.md |

### Contract checks this seat ran on the two rows

- 11 columns each, no `|` inside a cell (contract table header).
- `kind` ∈ the enum (`docs`); `tier` ∈ {A,B,C}; `status` ∈ {queued,mined,rejected}; `opened` is an ISO date;
  `recheck` is a cadence (`90d` — a value 12 other rows already use).
- `mined` requires ≥1 path in `used-by`; both name `corpus/knowledge/machine-parsed-path-spelling.md`, which exists
  in the lane working tree.
- Rule 1: URL/path, access date and a ≤25-word located quote are all present; quote word counts are 15 (S346) and 11
  (S347), inside the ≤25-word bound.
- Rule 2: neither row changes an existing row's immutable cells; the two `mined` rows are appends.

### One wording fix the L1 should take (F1, low)

The S347 anchor's quote uses the ASCII apostrophe `don't` (U+0027). The capture's raw roff bytes are
`don\(cqt` and the rendered page reads `don’t` (U+2019); the ASCII form appears in NEITHER the raw capture nor the
rendered page. The lane's own precedent for a rendered quote (S345) says so in the anchor cell: "the sentence wraps;
justified spacing normalised". The S346 quote needs no such note (it is a byte-exact capture substring after the
standard roff unescaping `\-` -> `-`, `\&.` -> `.`).

Recommended edit to the S347 anchor cell — add the normalisation, as S345 does:

    OPTIONS `-F`, roff line 212 of the capture (the rendered apostrophe U+2019 folded to ASCII `'`, the roff
    `\&.` folded to `.`): "Use fixed strings for patterns (don't interpret pattern as a regex)."

Nothing in the C1/C2 claim wording turns on this: the quote grounds `teaches`, and `teaches` is true of the page
under either spelling. It is a citable-quote fidelity fix, not a falsification.

---

## Knowledge rows note (for the L1's Gate paragraph)

Both admitted rows are cited by `corpus/knowledge/machine-parsed-path-spelling.md` (the r87 knowledge entry, drafted
in the lane working tree at 06:45). The Gate's closing sentence may keep its current form:

    Both admitted rows are cited by `corpus/knowledge/machine-parsed-path-spelling.md`.

One consistency note for the L1 (F3, low): the knowledge entry's own `## Gate` section repeats the same two quotes
in a second place (`corpus/knowledge/machine-parsed-path-spelling.md` `## Gate`), and the SOURCES row's `used-by`
cell names that entry. That is the lane's normal shape (the entry cites its rows, the row names its entry), and the
census's `mined`-row `used-by`-exists check passes. No change needed; noted so the L1 knows the quote text now lives
in three places and any edit must be applied to all of them.
