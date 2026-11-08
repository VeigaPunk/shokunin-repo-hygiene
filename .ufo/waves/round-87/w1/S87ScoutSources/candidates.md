# S87ScoutSources — source candidates (round 87 w1)

Seat: `S87ScoutSources`. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (lane id `souji`).
Scope owned: `.ufo/waves/round-87/w1/S87ScoutSources/` + this file + the seat report
`.ufo/waves/round-87/w1/S87ScoutSources.md`. No lane file, no MANIFEST.json, no `.ufo/state/*`,
no `.scratch/*`, no git/jj mutation in the lane, no sibling-lane file touched.
Scratch: `/fast/scratch/hyaku/souji-r87/S87ScoutSources/` (deleted before yield).

Host: `git version 2.56.0` (`pacman -Q git` → `git 2.56.0-1`). Installed man pages opened
2026-11-08 from `/usr/share/man/man1/`:

| page | .gz sha256 | decompressed capture sha256 | capture |
|---|---|---|---|
| `/usr/share/man/man1/git-status.1.gz` | `ed2ef058a1f0232b49d3b24f344b546de06971b58c4a6abd791630321c4fbd46` | `52d34e3a41e59a1683ac36ab7013a63e8701bfd687ab98c7630419676a2b2d95` | `census/round-87/srcs/git-status.1` |
| `/usr/share/man/man1/git-grep.1.gz` | `ab2c8762115193484c86835ab1762d0ab4075914b21fe06f0ee051a2c4011ed7` | `52603128b427d0cd8d2bfdc10790958a9d34b8762abc3a3d870504ac3b5b14a6` | `census/round-87/srcs/git-grep.1` |

Both captures are byte-identical to `gunzip -c` of the installed page (`cmp` → 0). Both already
exist in the lane tree at `census/round-87/srcs/`; this seat did not write or overwrite them.

Rendered text for locating quotes: `MANWIDTH=100 man git-status | col -b` and
`MANWIDTH=100 man git-grep | col -b` (586 and 301 lines), plus
`MANWIDTH=100 man git-config | col -b` (6958 lines). Captures of all three renders are in this
seat dir (`git-status.txt`, `git-grep.txt`, `git-config.txt`) and are hashed in `SHA256SUMS`.

---

## Row A — `S346` (ADMIT) — git-status(1): the `-z` format paragraph

| field | value |
|---|---|
| id | `S346` (next unused id at HEAD; `S347` is row B) |
| title | git-status(1) — the alternate `-z` output format |
| url | `https://git-scm.com/docs/git-status` (served page; not fetched this round — see limits) |
| installed path | `/usr/share/man/man1/git-status.1.gz`, git 2.56.0-1 |
| access date | 2026-11-08 |
| tier | A |
| class | docs |
| status | mined (pending the L1's integration) |
| used-by | `corpus/knowledge/machine-parsed-path-spelling.md` |
| roff line | **1102** (capture `census/round-87/srcs/git-status.1`, sha256 `52d34e3a…`); the `Pathname Format Notes and -z` section, heading at 1099 |
| section | `.SS "Porcelain Format Version 2"` (line 701) — see Residual 1 |
| quote (19 words) | "pathnames are printed as is and without any quoting and lines are terminated with a NUL (ASCII 0x00) byte" |
| admit/reject | **ADMIT** — grounds C2's "parsed raw instead of in git's C-quoted spelling" |
| duplicate-URL check | see §Duplicate-URL check |

**The anchor location — the `Pathname Format Notes and -z` section, roff lines 1099–1104,
`.SS "Porcelain Format Version 2"` (701):**

```
1099 \fBPathname Format Notes and -z\fR
1102 When the \fB\-z\fR option is given, pathnames are printed as is and without any quoting and lines are terminated with a \fINUL\fR (ASCII 0x00) byte\&.
1104 Without the \fB\-z\fR option, pathnames with "unusual" characters are quoted as explained for the configuration variable \fBcore\&.quotePath\fR (see \fBgit-config\fR(1))\&.
```

Rendered (lines 503–509):

```
     Pathname Format Notes and -z

	 When the -z option is given, pathnames are printed as is and without any quoting and lines
	 are terminated with a NUL (ASCII 0x00) byte.
```

> "pathnames are printed as is and without any quoting and lines are terminated with a NUL (ASCII 0x00) byte"

19 words. This sentence carries the `-z` rule *and* the `core.quotePath` cross-reference in
one place, and it is the section the page's own OPTIONS entry points at — which is why it is
the better anchor for a row whose scope is "`-z` guarantees about a path's spelling", and why
it makes row C's `core.quotePath` cross-reference visible.

**Byte-fidelity.** The quoted sentence is **byte-exact against roff line 1102 with the roff
markup removed** (`\fB`, `\fNUL`, `\-`, `\&` stripped) — verified. It is **not** byte-exact
against the *rendered* capture, where the sentence wraps across lines 505–506 with a leading
tab; it matches the render only after whitespace normalisation.

**History of this row (findings, see report §1–§2).** As first drafted the row read
`OPTIONS `-z`, roff line 698` with the quote *"filenames containing special characters are not
specially formatted; no quoting or backslash-escaping is performed"*. Two defects: roff 698 is
inside `.SS "Porcelain Format Version 1"` (line 668), **not** OPTIONS (whose genuine `-z`
entry is at 211–217, with different text); and that quote is absent from both captures as
written (the roff has `backslash\-escaping`; the render breaks mid-word `con‐`/`taining` and
justifies its spacing). The scope cell also misattributed the `Pathname Format Notes and -z`
section to `--untracked-files` — that is an OPTIONS **option** at roff 86, while the section is
inside `Porcelain Format Version 2`. The L1 has since re-anchored the row to roff 1102, which
is this seat's recommendation, and has corrected the `--untracked-files` attribution.

**Residual 1 (still open).** The scope cell reads *"`Porcelain Format Version 1` `SS`
Pathname Format Notes and -z, roff 1102"* — but roff 1102 is inside `.SS "Porcelain Format
Version 2"` (line 701). The anchor cell and the scope cell disagree about which
`Porcelain Format Version` owns line 1102; the correct label is `Porcelain Format Version 2`.

**Residual 2 (still open).** The anchor's parenthetical reads *"(rendered quote, roff markup
removed)"* — two representations at once. The quote is byte-exact against the **roff** line
with markup removed, and only whitespace-normalised against the **render**. The r86 house
precedent for a wrapping sentence (S345) names one representation: *"(the sentence wraps;
justified spacing normalised)"*. Suggest *"roff line 1102 of the capture, roff markup
removed"*, or *"rendered lines 505–506, justified spacing normalised"*.

```
1099 \fBPathname Format Notes and -z\fR
1102 When the \fB\-z\fR option is given, pathnames are printed as is and without any quoting and lines are terminated with a \fINUL\fR (ASCII 0x00) byte\&.
1104 Without the \fB\-z\fR option, pathnames with "unusual" characters are quoted as explained for the configuration variable \fBcore\&.quotePath\fR (see \fBgit-config\fR(1))\&.
```

Rendered (lines 503–509) and byte-exact in the rendered capture:

> "pathnames are printed as is and without any quoting and lines are terminated with a NUL (ASCII 0x00) byte"

19 words. This sentence carries the `-z` rule *and* the `core.quotePath` cross-reference in
one place, and it is the section the page's own OPTIONS entry points at. It is the better
anchor for a row whose scope is "`-z` guarantees about a path's spelling", and it is the row
that makes row C's `core.quotePath` cross-reference visible.

---

## Row B — `S347` (ADMIT) — git-grep(1): `-F` / `--fixed-strings`

| field | value |
|---|---|
| id | `S347` |
| title | git-grep(1) — `-F` / `--fixed-strings` |
| url | `https://git-scm.com/docs/git-grep` (served page; not fetched this round — see limits) |
| installed path | `/usr/share/man/man1/git-grep.1.gz`, git 2.56.0-1 |
| access date | 2026-11-08 |
| tier | A |
| class | docs |
| status | mined (pending the L1's integration) |
| used-by | `corpus/knowledge/machine-parsed-path-spelling.md` |
| roff line | 212 (capture `census/round-87/srcs/git-grep.1`, sha256 `52603128…`) |
| section | `.SH "OPTIONS"` — correct as recorded |
| quote (11 words) | "Use fixed strings for patterns (don’t interpret pattern as a regex)." |
| admit/reject | **ADMIT** — grounds C1's declaration search being a literal search |
| duplicate-URL check | see §Duplicate-URL check |

**Located quote, roff line 212**, under the option tag at roff 210
(`\fB\-F\fR, \fB\-\-fixed\-strings\fR`):

```
210 \fB\-F\fR, \fB\-\-fixed\-strings\fR
211 .RS 4
212 Use fixed strings for patterns (don\(cqs interpret pattern as a regex)\&.
```

Rendered line 121 of `git-grep.txt`:

```
	 Use fixed strings for patterns (don’t interpret pattern as a regex).
```

**Byte-fidelity.** The apostrophe is U+2019 (`e2 80 99`) in the render and `don\(cqt` in the
roff (`5c 28 63 71 74`). The filed quote uses a **bare ASCII apostrophe** (`27`) — a third
spelling present in neither capture. The r86 house row S343 keeps the U+2019 form.

**History of this row (finding, see report §2).** The row as first drafted carried the ASCII
apostrophe with no declaration; the L1 has since amended the anchor to say so explicitly —
*"the filed quote is the ASCII fold of the rendered line: the capture's bytes carry `don\(cqt`,
the rendered page U+2019"* — which matches the r86 house convention of declaring the fold
(S343, S345) and is **accurate in every part** (verified: the roff bytes do carry `don\(cqt`
and the render does carry U+2019). **No residual on this row.**

**Why this page grounds C1.** `_declared` in `census/round-87/c1-pointer-counter.py:249` runs
`git(root, "grep", "-h", "-F", "-I", "-e", target, rev, "--", *AUTHORITY)`. The pattern is a
**path** (`corpus/.../round-79-collision.md`, `.ufo/quarantine/.../lemma-stub`). Under a regex
reading `.` and `/` are metacharacters and the pattern matches other paths; only `-F` makes
the search literal. The TQ1 row rides on that.

---

## Row C — `S348` (REJECT) — git-config(1): `core.quotePath`

| field | value |
|---|---|
| id | `S348` (next unused id) |
| title | git-config(1) — `core.quotePath` |
| url | `https://git-scm.com/docs/git-config` |
| installed path | `/usr/share/man/man1/git-config.1.gz`, git 2.56.0-1 (.gz sha256 `d6fce9a86a91b82f15fb0644b6899b7bb43e91d5bc016a26aa286117dfbfd64f`) |
| access date | 2026-11-08 |
| tier | A |
| class | docs |
| status | rejected |
| used-by | — |
| roff line | 3564–3578 (capture `git-config.1`, in this seat dir) |
| section | `core.quotePath` (a `.PP`/`.RS` variable entry under the CONFIGURATION section) |
| quote (19 words) | "will quote \"unusual\" characters in the pathname by enclosing the pathname in double-quotes and escaping those characters with backslashes" |
| admit/reject | **REJECT** — see reason below |
| flip condition | see below |

**Located quote.** The variable's entry begins at roff 3564 (`core\&.quotePath`); the quoted
sentence is the first clause of the body at roff 3566–3568:

```
3566 Commands that output paths (e.g.
3567 \fIls\-files\fR,
3568 \fIdiff\fR), will quote "unusual" characters in the pathname by enclosing the pathname in double\-quotes and escaping those characters with backslashes in the same way C escapes control characters (e.g.
```

Rendered lines 1870–1873 of `git-config.txt` (the sentence spans three rendered lines, with
justified spacing). **Byte-fidelity:** the 19-word quote above is **not** byte-exact against
the rendered capture — the render justifies its spacing (`characters  with`, `backslash  in`)
and wraps the sentence across lines 1871–1873, so the recorded string matches only after
whitespace normalisation. In the roff capture the text is `double\-quotes` and
`backslash\-escaping` (roff escaped hyphens, bytes `5c 2d`), so the quote as written is
byte-exact against **neither** capture; it is byte-exact against roff line 3568 with the roff
markup removed.

**REJECT reason.** The registry already carries `core.quotePath`'s *decision content* in a
different row's scope, and this page adds a scope the lane does not need:

1. The quoted sentence describes how git spells a path **in the line form** — the very spelling
   row A's page says the `-z` form does *not* produce. The lane's K4 arm and the receipt
   writer both read the `-z` form (`tools/souji-record-agreement.py:514`,
   `tools/souji-receipt-write.py:364`), so the quoted rule governs a form the lane does not
   consume.
2. The row the reject would compete with (`S346`) is the one that names the spelling the lane
   *does* consume, and the pending knowledge entry `corpus/knowledge/machine-parsed-path-spelling.md`
   already carries that content — including the `core.quotePath` cross-reference, quoted from
   the `Pathname Format Notes and -z` section (row A's recommended anchor), not from
   git-config(1).
3. The page's only *additional* content over that cross-reference is the **default and the
   value range** ("The default value is true"; the byte set counted unusual; `core.quotePath`
   false stops bytes > 0x80 being unusual) — a scope the lane has no decision to make: the
   lane pins `core.quotePath` nowhere and reads the `-z` form, whose spelling
   `core.quotePath` does not affect.

**Flip condition.** Admit when a round must decide **which quoting rule a caller's
`core.quotePath` selects for the line form** — i.e. a consumer that parses git's
C-quoted output (the `--porcelain` line form at `tools/souji-receipt-write.py:603,715`, or
`tools/souji-idx-repair.py`'s `porcelain()` unquoter at line 91) and must know whether a
non-ASCII byte arrives quoted or raw. That page's "default and values" paragraph is what
such a round would need, and it is not in this row.

**Note on the pending reject's stated reason.** The pending knowledge entry's Gate rejects
this page with the reason "S346 already carries the quoting rule and the config page only
names where the rule is configured". Read against the actual page, that reason is not
accurate: the page does not merely *name* where the rule is configured, it states the rule
itself (the quoting, the enclosing in double-quotes, the backslash escaping) and then the
default and the value range. The reject conclusion can stand on a narrower and correct
ground — the lane consumes the `-z` form, whose spelling this variable does not affect — but
the pending reason should be restated before the row is filed.

---

## Duplicate-URL check

The census's `url_of()` extracts the **first `https?://` URL** in the `source` cell and
normalises host case; the installed-path rows of r86/r87 put the path in the `source` cell, so
their URL key is the served URL if one is present, else empty. Both commands were run
against `corpus/SOURCES.md` at HEAD and in the working tree.

```
HEAD=2   WT=2   https://git-scm.com/docs/git-status      (S044 rejected, S302 mined)
HEAD=0   WT=0   https://git-scm.com/docs/git-grep        (no row anywhere — no collision)
HEAD=7   WT=7   https://git-scm.com/docs/git-config      (S042,S057,S238,S297,S299,S308,S310)
HEAD=1   WT=2   /usr/share/man/man1/git-status.1.gz       (S338 rejected, + S346)
HEAD=0   WT=1   /usr/share/man/man1/git-grep.1.gz         (S346's neighbour: S347 only — no prior row)
HEAD=0   WT=0   /usr/share/man/man1/git-config.1.gz       (no row — no collision)
```

- **Row A (`S346`, git-status):** the served URL `git-scm.com/docs/git-status` is already on
  **2 rows** (S044, rejected; S302, mined) under different scopes, and the installed path
  `/usr/share/man/man1/git-status.1.gz` is on **1 row** (S338, rejected — "status-versus-index
  comparison"). So the row **collides on URL** with S044/S302 (across scopes) and with S338
  (same installed path, different scope). Under `scripts/sources-census.sh` this is the
  `W04 duplicate url … across scopes` class — a warning, not a finding — and it is the same
  collision the r86 `git-ls-files` rows (S341 against S292) already carry. The pending
  `SOURCES.md` working tree shows ` W04` for the served-URL rows and no `E04`.
- **Row B (`S347`, git-grep):** the served URL `git-scm.com/docs/git-grep` appears on **0
  rows** at HEAD and in the working tree, and the installed path on **0 prior rows**. **No
  collision.** This is the first row in the registry on this document.
- **Row C (`S348`, git-config, rejected):** the served URL `git-scm.com/docs/git-config` is
  already on **7 rows** (S042, S057, S238, S297, S299, S308, S310) across distinct scopes.
  Rejected rows are exempt from the census's within-scope `E04` check
  (`scripts/sources-census.sh:646`), so a rejected row on this URL raises no `E04`; it would
  raise `W04` only, which is the same warning class as the seven existing rows.

## Verdict

**TWO admits, ONE reject.** Both admits were already drafted in the lane's working tree before
this seat ran; this seat re-opened both pages independently from the installed man pages,
confirmed the two rows' content, and raised two defects against the drafts which the L1 has
since applied. Two residuals remain (§ row A).

- **ADMIT** `S346` — git-status(1) as installed, the `-z` spelling rule, anchored on the
  `Pathname Format Notes and -z` section at roff 1102. **Confirmed on content.** Residuals:
  the scope cell still labels roff 1102 `Porcelain Format Version 1` (it is
  `Porcelain Format Version 2`), and the anchor names two representations at once.
- **ADMIT** `S347` — git-grep(1) as installed, `-F`/`--fixed-strings` (roff 212). **Confirmed
  on content; no residual.** The anchor now declares its ASCII apostrophe fold and names both
  capture spellings, matching the r86 house convention.
- **REJECT** `S348` — git-config(1) `core.quotePath`, with the `REJECTED: …; flip: …` reason
  and flip condition above. The L1's restatement of the reject reason in the knowledge entry
  is accurate and matches this seat's ground.

The two admits are the pages both claims rest on: C2's "parsed raw instead of in git's
C-quoted spelling" (row A) and C1's declaration search being a literal search (row B). The
reject is the third page the seat was asked to judge, and the lane consumes the `-z` form
whose spelling that variable does not affect.

**Not filed by this seat.** This seat writes only its own seat dir and its report; it does not
edit `corpus/SOURCES.md`, `corpus/knowledge/`, the counters or the tool, and makes no git or jj
mutation. The L1 owns integration of rows `S346`/`S347` and the proposed `S348`.
