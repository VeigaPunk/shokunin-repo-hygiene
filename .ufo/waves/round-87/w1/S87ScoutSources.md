# S87ScoutSources — souji round 87 w1, seat S87ScoutSources (source scout)

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (lane id `souji`). Seat `S87ScoutSources`,
wave 1 of round 87.
Scope owned: `.ufo/waves/round-87/w1/S87ScoutSources/` only, plus this report file. No lane
file, no MANIFEST.json, no `.ufo/state/*`, no `.scratch/*`, no git/jj mutation in the lane, no
sibling-lane file touched, no fleet-root tracked file written.
Scratch: `/fast/scratch/hyaku/souji-r87/S87ScoutSources/` (deleted before yield; receipts
copied into the seat dir first — `git-status.txt`, `git-grep.txt`, `git-config.txt`,
`git-status.adoc`, `SHA256SUMS`, `duplicate-url-check.txt`).

**Candidates file: `.ufo/waves/round-87/w1/S87ScoutSources/candidates.md`** — per-row id, title,
url, access date, tier, class, status, used-by, roff line, quote (≤25 words), admit/reject +
reason, duplicate-URL check.

## Verdict

**TWO admits, ONE reject. Both admits were already drafted in the lane's working tree before
this seat ran, so this seat's contribution is the independent re-open plus two findings against
those drafts — both of which the L1 has since applied — and two residuals that remain.**

- **ADMIT `S346`** — git-status(1) as installed, the `-z` spelling rule. **Confirmed on
  content.** The row's anchor was re-pointed by the L1 to the `Pathname Format Notes and -z`
  section (roff 1102) on this seat's recommendation (§1). **Residual (§1a):** the scope cell
  still labels roff 1102 as `Porcelain Format Version 1`; it is `Porcelain Format Version 2`.
- **ADMIT `S347`** — git-grep(1) as installed, `-F`/`--fixed-strings` (roff 212). **Confirmed
  on content.** The anchor now declares its ASCII apostrophe fold and names both capture
  spellings, matching the r86 house convention (§2). **Residual (§2a):** `S346`'s anchor names
  two representations at once ("rendered quote, roff markup removed"); it should name one.
- **REJECT `S348`** — git-config(1) `core.quotePath`, with the flip condition of §4. The
  L1's restatement of the reject reason matches this seat's ground and is confirmed accurate
  (§5). **Residual (§5):** the rejection lives in the knowledge entry, not in the registry;
  this seat's candidates file proposes the row as `S348` so the rejection is kept where the
  registry's 30 other rejected rows live.

Host: `git version 2.56.0`; `pacman -Q git` → `git 2.56.0-1`; both captures carry
`.\"    Source: Git 2.56.0`.

## 0. What the pages are, and that they are the ones both claims rest on

| page | installed path | `.gz` sha256 | capture sha256 | capture |
|---|---|---|---|---|
| git-status(1) | `/usr/share/man/man1/git-status.1.gz` | `ed2ef058…bd46` | `52d34e3a41e59a1683ac36ab7013a63e8701bfd687ab98c7630419676a2b2d95` | `census/round-87/srcs/git-status.1` |
| git-grep(1) | `/usr/share/man/man1/git-grep.1.gz` | `ab2c8762…1ed7` | `52603128b427d0cd8d2bfdc10790958a9d34b8762abc3a3d870504ac3b5b14a6` | `census/round-87/srcs/git-grep.1` |

Both captures are byte-identical to `gunzip -c` of the installed page (`cmp` → 0) and both
already existed in the lane tree; this seat did not write or overwrite them. Both served URLs
were checked reachable this round: `https://git-scm.com/docs/git-status` → **HTTP 200**,
`https://git-scm.com/docs/git-grep` → **HTTP 200**.

Why these two pages are load-bearing for this round's two claims:

- **C2** rests on the `-z` stream spelling. `tools/souji-record-agreement.py:514` runs
  `git_bytes(root, "status", "--porcelain", "-z")` and `tools/souji-receipt-write.py:364` runs
  `status --porcelain -z`; the claim says a path carrying a newline is "parsed raw instead of
  in git's C-quoted spelling". git-status(1)'s `-z` paragraph is the page that says the `-z`
  form does no quoting and no backslash-escaping — the "raw" half of that sentence.
- **C1** rests on the declaration search being a literal search.
  `census/round-87/c1-pointer-counter.py:249` runs `git(root, "grep", "-h", "-F", "-I", "-e",
  target, rev, "--", *AUTHORITY)`; the pattern is a **path**. git-grep(1)'s `-F` paragraph is
  the page that says the pattern is taken literally rather than as a regex, which is what
  keeps `.` and `/` in a path from matching other paths.

## 1. FINDING — `S346`'s anchor named the wrong section (scope misattribution) — CORRECTED IN THE WORKING TREE, with one residual

**This finding was raised by this seat against the row as first drafted and the L1 has since
corrected it.** The row as first drafted read:

> `OPTIONS `-z`, roff line 698 of the capture`

**Roff line 698 is not in OPTIONS.** The page's section chain, read from the capture's own
heading macros:

```
 41: .SH "OPTIONS"          <- OPTIONS runs to
262: .SH "OUTPUT"
668: .SS "Porcelain Format Version 1"   <- line 698 falls here
701: .SS "Porcelain Format Version 2"   <- line 1102 falls here
```

Line 698 sits inside `.SS "Porcelain Format Version 1"` (which begins at 668), not in OPTIONS.
The genuine OPTIONS `-z` entry is at **roff 211–217** and carries different text:

```
211 \fB\-z\fR
213 Terminate entries with
214 \fINUL\fR, instead of
215 \fILF\fR\&. This implies the
216 \fB\-\-porcelain=v1\fR
217 output format if no other format is given\&.
```

So the drafted row cited a line number from one section and a section name from another. The
*quote* was correctly located at 698; the *label* was wrong. Confirmed independently against the
upstream source at tag v2.56.0 (`Documentation/git-status.adoc`, fetched from
raw.githubusercontent.com): the `-z` paragraph is at adoc line 282, inside
`Porcelain Format Version 1` (adoc 268), which sits under `OUTPUT` (adoc 161) — and `OPTIONS`
(adoc 26) is a different top-level section.

The scope cell compounded it: it said the `--untracked-files` section's Pathname Format Notes
restate the same rule, but

- the `--untracked-files` **option** is at roff 86 (`\fB\-u\fR[…], \fB\-\-untracked\-files\fR[…]`),
  inside OPTIONS;
- the `Pathname Format Notes and -z` **section** is at roff 1099, inside
  `.SS "Porcelain Format Version 2"` (701) — upstream adoc line 423, a `^^^` subsection of
  `Porcelain Format Version 2` (295), nowhere near the `--untracked-files` option and nowhere
  near `.SH "UNTRACKED FILES AND PERFORMANCE"` (1116).

**Current state of the row (working tree, after the L1's correction):** the anchor is now

> `SS` Pathname Format Notes and -z, roff line 1102 of the capture (rendered quote, roff markup removed): "pathnames are printed as is and without any quoting and lines are terminated with a NUL (ASCII 0x00) byte"

— the re-anchor this seat recommended — and the scope cell now names all three locations
correctly (the `Pathname Format Notes and -z` section at roff 1102, the OPTIONS `-z` entry at
roff 211–217 for the NUL termination, and the roff 698 paragraph inside `Porcelain Format
Version 1` for the no-quoting rule). **The section misattribution is resolved.**

### 1a. RESIDUAL — the scope cell still names the wrong `.SS` for the section it now anchors

The revised scope cell reads:

> "(scope: `Porcelain Format Version 1` `SS` Pathname Format Notes and -z, roff 1102; …)"

But roff 1102 is inside **`.SS "Porcelain Format Version 2"`** (line 701), not
`Porcelain Format Version 1` (line 668). The scope cell now pairs the correct *line* with the
wrong *section* — the same class of defect as the drafted row, one level down. The anchor cell
(`SS` Pathname Format Notes and -z, roff line 1102) and the scope cell disagree about which
`Porcelain Format Version` owns line 1102. The correct label is
`.SS "Porcelain Format Version 2"`.

*(This is a labelling defect in the scope cell only; it does not change what the row teaches or
where its quote sits.)*

## 2. FINDING — quote byte-fidelity: the house convention, and what the current rows say

The house convention, established by the r86 rows and their own seat's captures, is that the
quote is located in the **rendered** capture and the anchor says "rendered line N"; where the
sentence wraps, the anchor **says so**. I verified this against
`.ufo/waves/round-86/w1/S86ScoutSources/`:

| r86 row | anchor | byte-exact in that seat's rendered `.txt`? |
|---|---|---|
| S341 | "rendered line 119 of the capture" | **yes** |
| S343 | "rendered lines 26-27 of the capture" | yes, after whitespace normalisation (it wraps) |
| S345 | "rendered lines 79-80 of the capture (the sentence wraps; justified spacing normalised)" | yes, after whitespace normalisation |

Both r86 rows that needed it **say so in the anchor**. The r87 rows as first drafted did
neither: `S346` cited a *roff* line while quoting a *rendered* sentence, and `S347` used a bare
ASCII apostrophe where the render carries U+2019 and the roff carries `don\(cqt`.

**`S346` as first drafted** — recorded quote: *"filenames containing special characters are not
specially formatted; no quoting or backslash-escaping is performed"*. It is **absent from both
captures** as written:

- in the roff capture the text is `backslash\-escaping` (bytes `5c 2d` — a roff escaped
  hyphen); the recorded quote has a bare `-` (byte `2d`);
- in the rendered capture the line breaks mid-word (`con‐` / `taining`, U+2010 HYPHEN) and the
  spacing is justified (double spaces), so the recorded string is absent there too.

**`S347`** — recorded quote: *"Use fixed strings for patterns (don't interpret pattern as a
regex)."* The apostrophe is the problem: it is U+2019 (`e2 80 99`) in the render and `\(cqt`
(`5c 28 63 71 74`) in the roff. The recorded quote uses a **bare ASCII apostrophe** (`27`) —
a third spelling present in neither capture. The r86 house row S343, on the same page family,
preserved the U+2019 form.

**Impact:** low on its own — no claim's wording turns on a hyphen or an apostrophe. But
CORPUS.md rule 1 makes the located quote the grounding evidence for the row.

### 2a. Current state — both rows now declare their fold; one residual remains

The L1 has since amended both anchors to **declare** the transformation, which is what the
house convention asks for:

- `S346` anchor: "`SS` Pathname Format Notes and -z, roff line 1102 of the capture
  **(rendered quote, roff markup removed)**: *"pathnames are printed as is and without any
  quoting and lines are terminated with a NUL (ASCII 0x00) byte"*" — verified: this quote **is**
  byte-exact against the roff line 1102 with the roff markup removed (`\fB`, `\fNUL`, `\-`,
  `\&` stripped). It is **not** byte-exact against the *rendered* capture, because the render
  wraps the sentence across lines 505–506 with a leading tab (`…and lines\n\t are terminated
  with a NUL…`); it matches the render only after whitespace normalisation.
- `S347` anchor: "OPTIONS `-F`, roff line 212 of the capture **(the filed quote is the ASCII
  fold of the rendered line: the capture's bytes carry `don\(cqt`, the rendered page U+2019)**"
  — verified: the roff bytes at line 212 do carry `don\(cqt`, and the render does carry U+2019.
  **The declaration is accurate**, and the ASCII apostrophe is now explicitly named as a fold
  rather than presented as the page's own byte.

**Residual on `S346`:** its anchor says "rendered quote, roff markup removed" — the two
clauses are in tension. The quote is byte-exact against the **roff** line with markup removed,
and only whitespace-normalised against the **render**. The r86 house precedent for a wrapping
sentence (S345) says which representation it used: *"(the sentence wraps; justified spacing
normalised)"*. Suggest the anchor read *"roff line 1102 of the capture, roff markup removed"* —
or, if the render is the intended source, *"rendered lines 505–506, justified spacing
normalised"* — so the declaration names one representation, as S345 does.

## 3. The two admits are already in the working tree — confirmations, not re-filings

At HEAD the registry's highest id is **S345** and it carries **268** rows; the working tree
carries **270** rows with **S346** and **S347** added (uncommitted,
`git status --porcelain corpus/SOURCES.md` → ` M corpus/SOURCES.md`). The next unused id is
**S348**.

(The lane's `refs/heads/master` advanced twice more under this seat — `89d36922` →
`b0a64c94` → `1556010b` — on C2 counter/mechanism work. `corpus/SOURCES.md` was **not**
touched by those commits: the registry's highest id at HEAD is still S345 and the working-tree
delta is still exactly the two pending rows. The `duplicate-url-check.txt` receipt in the seat
dir records the HEAD sha it was run against.)

I re-opened both pages from the installed man pages independently and reproduce each pending
row's capture bytes, roff line and sentence. **The two admits are confirmed on content.** The
corrections in §1 and §2 were raised by this seat and have since been applied by the L1 in the
working tree; §1a and §2a are the two residuals that remain after those corrections.

## 4. The reject — git-config(1) `core.quotePath` (row `S348`)

Located: roff 3564 (`core\&.quotePath`), body 3566–3568, rendered lines 1870–1873 of
`git-config.txt` (6958 lines). Quote (19 words) — byte-exact against **neither** capture as
written: the render justifies its spacing and wraps the sentence across lines 1871–1873, and
the roff carries `double\-quotes` / `backslash\-escaping`. It is byte-exact against roff line
3568 with the roff markup removed:

> "will quote \"unusual\" characters in the pathname by enclosing the pathname in double-quotes and escaping those characters with backslashes"

**Reject, on this ground:** the lane consumes the `-z` form, and `core.quotePath` does not
affect that form's spelling. The K4 arm reads `status --porcelain -z`
(`tools/souji-record-agreement.py:514`) and the receipt writer reads `status --porcelain -z`
(`tools/souji-receipt-write.py:364`); the quoted rule governs the **line** form, which the
lane's C1/C2 measurements do not consume. What the page adds beyond the `core.quotePath`
cross-reference that `S346`'s recommended anchor already carries is only the **default and
the value range** ("The default value is true"; which bytes count as unusual; `false` stops
bytes > 0x80 being unusual) — a scope the lane has no decision to make.

**Flip condition:** admit when a round must decide **which quoting rule a caller's
`core.quotePath` selects for the line form** — i.e. a consumer that parses git's C-quoted
output. The lane has such consumers outside this round's claims: the receipt writer's
`git status --porcelain` line-form reads (`tools/souji-receipt-write.py:603,715`) and
`tools/souji-idx-repair.py`'s `porcelain()` unquoter (line 91). A round that must decide
whether a non-ASCII byte arrives quoted or raw there needs this page's default-and-values
paragraph, which no registry row carries.

## 5. FINDING — the pending reject's stated reason was inaccurate; restated by the L1 since

The knowledge entry `corpus/knowledge/machine-parsed-path-spelling.md` originally rejected
this page with the reason:

> "S346 already carries the quoting rule and the config page only names where the rule is
> configured; admitting it would duplicate a scope without adding a decision."

Read against the actual page, **"only names where the rule is configured" was not true**. The
page states the rule itself — that git encloses the pathname in double-quotes and escapes
those characters with backslashes "in the same way C escapes control characters (e.g. `\t`
for TAB, `\n` for LF, `\\` for backslash)" — and then the default and the value range. So the
page is not a pointer to a rule; it is a statement of the rule, with a different scope from
`S346` (the line form's spelling vs. the `-z` form's).

**The L1 has since restated the reject** in the knowledge entry's Gate, and the restatement is
accurate and matches this seat's §4 ground:

> "The page states the line form's escape rule itself (double quotes; C-style escapes for TAB,
> LF and backslash) and then its default and value range, so it is not merely a pointer. It is
> **REJECTED** on the narrower ground that this lane consumes the `-z` form, whose spelling the
> variable does not affect: the row would add no decision for the surface the lane parses.
> **Flip:** a round that starts parsing the line form, or must decide which spelling a
> caller's `core.quotePath` selects, needs this row and its default/value paragraph."

**The correction is confirmed and the finding is closed.** One residual note for the L1: the
reject is currently recorded in the **knowledge entry**, not as a **registry row**. The
registry's rejected-row convention (CORPUS.md: `status` — `rejected` (kept — a rejection is
evidence of taste)) is a row with `teaches` reading `REJECTED: <reason>; flip: <what would
change the verdict>`, and the registry already carries **30** such rejected rows (S030, S032,
S044, S048, S090, S097, S103, S106, S127, S227–S229, S235, S238, S243, S246, S262, S265,
S267, S269, S281, S285, S287, S289, S305, S309, S330, S336, S338, S344). This seat's
candidates file proposes that row as **`S348`** with the §4 reason and flip condition in the
`REJECTED: …; flip: …` shape, so the rejection is kept in the registry where a reader will
look for it and where the census can see it.

## 6. Duplicate-URL check

Run against `corpus/SOURCES.md` at HEAD and in the working tree (full output in the seat dir's
`duplicate-url-check.txt`):

```
HEAD=2   WT=2   https://git-scm.com/docs/git-status
HEAD=0   WT=0   https://git-scm.com/docs/git-grep
HEAD=7   WT=7   https://git-scm.com/docs/git-config
HEAD=1   WT=2   /usr/share/man/man1/git-status.1.gz
HEAD=0   WT=1   /usr/share/man/man1/git-grep.1.gz
HEAD=0   WT=0   /usr/share/man/man1/git-config.1.gz
```

- **`S346` (git-status) — collides.** The served URL is already on 2 rows (S044 rejected,
  S302 mined) under different scopes; the installed path is already on 1 row (S338, rejected).
  This is the census's `W04 duplicate url … across scopes` class — a warning, not a finding —
  and the same collision class the r86 `git-ls-files` rows already carry (S341 against S292).
- **`S347` (git-grep) — no collision.** The served URL `git-scm.com/docs/git-grep` is on **0
  rows** at HEAD and in the working tree, and the installed path on **0 prior rows**. First row
  in the registry on this document.
- **`S348` (git-config, rejected) — collides on the served URL**, already on 7 rows (S042,
  S057, S238, S297, S299, S308, S310). `scripts/sources-census.sh:646` exempts rejected rows
  from the within-scope `E04` check, so a rejected row on this URL raises no `E04`.

**Note for the L1:** `scripts/sources-census.sh`'s `url_of()` extracts only an `https?://` URL
from the `source` cell, so the installed-man-path rows (`S341`…`S347`) are **invisible to the
census's duplicate-URL check** — `validate` reports no `W04` for any of them. The path-based
collisions above are therefore only visible to a grep of the capture path, which is why the
r86 seat kept its own `duplicate-url-check.txt`. The round's
`census/round-87/records/sources-census-{before,after}.txt` are byte-identical and mention
neither `S346` nor `S347`; that is the expected census result for these two rows, not a
signal that they were checked.

## 7. Limits of this seat's evidence

- The served web pages were **checked reachable** (HTTP 200 each) but **not fetched and
  byte-hashed**; the quotes are located in the **installed** pages, and the rows cite the
  installed path (the r86 convention for an installed-page row). The upstream
  `Documentation/git-status.adoc` at tag v2.56.0 **was** fetched and is used in §1 only to
  confirm the section hierarchy, which it confirms independently of the roff macros.
- A rejected row's `teaches` cell must read `REJECTED: <reason>; flip: <what would change the
  verdict>` (CORPUS.md). The §4 reason and flip condition are written to that shape; the L1
  files the row.
- This seat did not touch `corpus/SOURCES.md`, `corpus/knowledge/`, the counter, the battery
  or the tool, and made no git or jj mutation. The lane tree moved under this seat mid-session
  (the L1 committed `578cbf2c` and `89d36922`, advancing `refs/heads/master` to `89d36922`);
  §1–§5 were re-verified against the bytes current at the end of this seat's run.
- **No tool install was needed or performed** for this seat; the task used only `git`,
  `gunzip`, `man`, `col`, `curl`, `sha256sum`, `cmp` and `python3` as already present on the
  host. Nothing was installed, so there is no tool/version/channel record to file.
