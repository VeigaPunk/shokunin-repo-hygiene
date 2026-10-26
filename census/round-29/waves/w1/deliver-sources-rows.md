# deliver-sources-rows — S216–S219, search log note, Paths line (round 29, w1)

Seat `SwarmScribe25`. Lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`; preregistration
`b8cb4b31ce80e2e3314b88e85d40ea9873180804`. Every cell below was written from bytes opened by
this seat on 2026-10-25, not from the staged package. Insertion points and the cell-by-cell
diff against the staged rows are at the end; the L1 lands the rows.

## Provenance of this delivery

Fetched live this run into `/var/tmp/souji-r29-SwarmScribe25/` (scratch, removed at seat end):

| file | url | http | bytes | sha256 |
|---|---|---|---|---|
| statx.2.html | https://man7.org/linux/man-pages/man2/statx.2.html | 200 | 33125 | 2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e |
| link.2.html | https://man7.org/linux/man-pages/man2/link.2.html | 200 | 19883 | 9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9 |
| cmp.1.html | https://man7.org/linux/man-pages/man1/cmp.1.html | 200 | 9791 | 5c68e8d874e987391e7679dd2637f953b90087076bffe6de18c40db86cd046a3 |
| broder.pdf | https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf | 200 | 254930 | da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b |
| crossref.json | https://api.crossref.org/works/10.1109/SEQUEN.1997.666900 | 200 | 3063 | f1aeff86715e715c42426e616a74bb01356b6b4e5a18094e77ed74b0dbc69fad |

```
$ curl -sS -o /dev/null -w '%{http_code} %{size_download} %{url_effective}\n' -L https://doi.org/10.1109/SEQUEN.1997.666900
202 0 https://ieeexplore.ieee.org/document/666900/
```

The DOI landing page still returns 202 with a zero-byte body, which is why S217's `source` cell
carries the author-hosted PDF: that is the address whose bytes this seat actually read.

Release lines, read out of the fetched page footers (not from the staged rows):

```
statx.2.html:587: Linux man-pages 6.19            2026-02-08
link.2.html:310:  Linux man-pages 6.19            2026-02-11
cmp.1.html:156:   diffutils 3.12.26-bbc1         August 2026                         CMP(1)
```

Note the link(2) date: the staged row says 2026-02-08, the served page says **2026-02-11**.

## Rows — append to the `## Registry` table

Insert directly after the S215 row (`corpus/SOURCES.md:160`), before the blank line and `## Paths`;
the four lines below are the whole block, and no other table in this file uses the `| S<id> |`
shape.

| S216 | statx(2) — https://man7.org/linux/man-pages/man2/statx.2.html | docs | A | the inode-number and hard-link-count pair as the identity test a duplicate verdict applies (one inode, several names); not the origin-record field list (S114 holds that) and not a duplicate-detection algorithm | § DESCRIPTION struct statx, the stx_ino and stx_nlink field descriptions; page footer release line "Linux man-pages 6.19", dated 2026-02-08 | `stx_ino` names the inode and `stx_nlink` counts the hard links on it, so a verdict can compare inode numbers rather than path strings and read a link count above one as one file carrying several names | mined | 2026-10-25 | on-release — re-read the man-pages 6.x `statx(2)` page | corpus/knowledge/duplicate-verdict-identity.md |
| S217 | A. Z. Broder, On the resemblance and containment of documents — https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf | paper | B | resemblance and containment as the vocabulary a near-duplicate verdict would have to name; similarity over token sets, not filesystem byte equality, and not a threshold | § Abstract; § 2 "Definitions as set intersection problems"; author-hosted nine-page preprint naming Andrei Z. Broder, DEC Systems Research Center; the Crossref record for DOI 10.1109/SEQUEN.1997.666900 gives "Proceedings. Compression and Complexity of SEQUENCES 1997", Salerno, Italy, pp. 21-29, proceedings year 1997, with no issued date in that record; doi.org answered 202 with a zero-byte body on 2026-10-25 | the paper's own clustering ran at a 50% resemblance over 30 million web documents, so resemblance is a sampled measure over token shingles rather than an oracle for byte equality | mined | 2026-10-25 | 365d — re-fetch the author-hosted PDF, compare its sha256, and re-read § Abstract and § 2 | corpus/knowledge/duplicate-verdict-identity.md, corpus/knowledge/duplicate-verdict-byte-equality.md |
| S218 | link(2) — https://man7.org/linux/man-pages/man2/link.2.html | docs | A | the kernel statement that a second name for an existing file is not a copy, so two paths are not two files; not a duplicate-detection algorithm | § DESCRIPTION, the link() paragraph beginning "This new name may be used exactly as the old one for any operation"; page footer release line "Linux man-pages 6.19", dated 2026-02-11 | neither name is the original, so no path can be designated the canonical copy and a verdict must compare inodes instead of choosing between two names | mined | 2026-10-25 | on-release — re-read the man-pages 6.x `link(2)` page | corpus/knowledge/duplicate-verdict-identity.md, corpus/knowledge/duplicate-verdict-byte-equality.md |
| S219 | cmp(1) — https://man7.org/linux/man-pages/man1/cmp.1.html | docs | A | the byte-equality primitive and its three-valued exit contract that a duplicate verdict is defined against; not a duplicate-detection algorithm and not a threshold | § DESCRIPTION "Compare two files byte by byte" and the exit-status sentence; page footer release line "diffutils 3.12.26-bbc1", August 2026 | trouble is exit 2, a third documented outcome beside same and different, so a verdict that folded it into "different" would record an unreadable file as a non-duplicate | mined | 2026-10-25 | on-release — re-read the man7 cmp(1) page after a diffutils release | corpus/knowledge/duplicate-verdict-byte-equality.md |

### Field notes a reviewer will want

- **S216 does not duplicate S114.** Lane S114 is the same URL scoped to "the identity fields a
  per-item origin record can carry (inode, link count, creation time, mount id)", used by
  `quarantine-origin-record-fields-r24.md`. S216 is scoped to the *test* a duplicate verdict
  applies, and its scope cell names S114 for the field list. Precedent for two scopes on one URL:
  the pairs S036/S049, S042/S057, S045/S059 and S128/S215.
- **S217 is tier B by curation, not by source class.** SOURCES-CONTRACT-v1 would allow A for an
  "original paper"; the scope here is borrowed vocabulary, and the paper is not authoritative for
  the filesystem verdict it is borrowed into. The `teaches` cell says what it does establish.
- **The mutual exclusivity of used-by matches the two entries.** The identity entry's front matter
  cites S216/S217/S218; the byte-equality entry's cites S219/S218/S217. So S216 and S219 each name
  one entry and S217/S218 name both. Appending a staged used-by verbatim would break the C1
  counter (see changes below).
- **Snapshot pins.** The Gate blocks of the two entries cite
  `census/round-29/sources/{statx.2.html,link.2.html,cmp.1.html,broder97resemblance.txt}`. The
  hashes above are what the L1 should record. One caveat for the L1: the entries record the
  Broder *decoded text* as sha256 `3ba1e117…`; this seat's `pdftotext -layout` decode of the same
  PDF hashes `ddf97f6b12f7e7e4b4c9643a44eb4979f1fdd09d109250cc100eba0600e2fd7a`, so the snapshot
  must be the exact decode the entries hashed, or the entries' `verified-at` line must be
  re-stated. The PDF bytes themselves (`da122799…`) are the stable pin.

## Search log note — insert under `## Search log`

**Round-29 F3 duplicate-verdict row re-grounding (2026-10-25).** Question: which pages actually
ground the identity test, the byte-equality oracle and the similarity vocabulary that the two F3
entries cite, and which staged F3 material can be re-grounded on sources opened this round? Where:
`/home/vgpnk/Projects/shokuknow/merge/souji/` read-only (`SOURCES.append.md` rows S117, S118, S122,
S136, and every `ground: F3` entry under `knowledge/corpus/knowledge/`), then live: man7 `statx(2)`,
`link(2)`, `cmp(1)`, the author-hosted Broder PDF at Princeton, and the Crossref record for DOI
10.1109/SEQUEN.1997.666900 (doi.org itself answered 202 with a zero-byte body). Identified 9 staged
F3 entries citing 13 staged row ids, screened 9; included 2 entries on 4 new rows S216–S219,
re-grounded from staged S117, S118, S122 and S136; excluded 7 entries together with the 9 staged row
ids that ground only them — four state a threshold or an operating point
(near-duplicate-threshold-r28, -operating-point-r28, -threshold-source-r34, -relations-r29), which
is document-similarity ground outside PROVINCE F3's byte-identical scope; one fixes a bibliography
and no claim (near-duplicate-literature-identity-r33); two record an operator decision or its
deferral rather than a fact (duplicate-receipt-class-decision-r25, -r26); one
(duplicate-verdict-taxonomy-r24) is re-grounded as the byte-equality entry without its threshold
framing. Stop: the four locators were opened and quoted, and they state filesystem identity and
byte equality only; no source states a similarity threshold for this lane, so the scan stops at the
package's F3 set plus those four locators.

Counts are reproducible from this seat's own reading, run 2026-10-25 from
`/home/vgpnk/Projects/shokuknow/merge/souji` (read-only):

```
$ grep -rlE '^ground: F3' knowledge/ | wc -l
9
$ grep -hE '^source: S' $(grep -rlE '^ground: F3' knowledge/) | grep -oE '^source: S[0-9]+' | sort -u | wc -l
13
$ grep -hE '^source: S' $(grep -rlE '^ground: F3' knowledge/) | grep -oE '^source: S[0-9]+' | sort -u | tr '\n' ' '
S117 S118 S122 S136 S145 S151 S162 S172 S178 S179 S213 S216 S217
```

Of those 13 staged ids, four (S117, S118, S122, S136) ground the two admitted entries and become
S216–S219; the other nine ground only excluded entries.

## Paths line — insert at the end of `## Paths`

- F3 duplicate verdicts, re-grounded — S216 → S218 → S219 → S217: the inode and link-count test
  first, then the kernel statement that a second name is not a copy, then the byte-equality oracle
  with its third outcome; last the similarity vocabulary, tier B, which licenses no filesystem
  verdict. These four rows support the two round-29 F3 entries and create no receipt class and no
  threshold.

## Collision note for the L1 (guard input, not a guard proof)

The staged ids in the F3 set are not free in the lane. Six of the 13 collide with an existing lane
row or with a row this delivery creates:

| staged id | staged subject | collides with |
|---|---|---|
| `S117` | statx(2) | lane S117 = git-prune(1) |
| `S118` | Broder 1997 | lane S118 = Qiita GC note |
| `S122` | link(2) | lane S122 = builtin/count-objects.c at v2.56.0 |
| `S213` | HAL API record | lane S213 = POSIX.1-2024 rename() |
| `S216` | Web Archive HAL chapter | this delivery's S216 = statx(2) |
| `S217` | Unpaywall record | this delivery's S217 = Broder 1997 |

The two entries that carry the collision into text are `near-duplicate-literature-identity-r33.md`
(cites staged S213) and `near-duplicate-threshold-source-r34.md` (cites staged S216 and S217); both
entries are excluded from this round's admit set, so no citation of theirs lands. If a later round
admits them, those citations must be re-pointed by document, not by number. The guard proof itself
belongs to the L1's scratch indented row.

## Cell changes against the staged rows, and why

Staged ids are campaign-register ids from `merge/souji/SOURCES.append.md`. Three of the four are
already occupied in the lane (S117, S118, S122) and the fourth (S136) is not the next free id, so
all four rows are renumbered.

### Staged S117 → lane S216 (statx)

- `id` S117 → S216. Lane S117 is already `git-prune(1)`; an appended S117 would be a duplicate id.
- `source` "statx(2) — Linux man-pages 6.19 (2026-02-08) — URL" → "statx(2) — URL". The contract
  puts the revision in `anchor`, and the lane does not carry a page's date twice (see S114).
- `scope` narrowed: the staged text claimed "identity and origin fields a duplicate verdict **and
  an origin record** must distinguish", which lands on lane S114's ground. Now scoped to the
  identity test and pointing at S114 for the field list.
- `anchor` staged "§ DESCRIPTION struct statx fields stx_ino, stx_nlink, stx_btime, stx_mnt_id; §
  CONSTANTS ...; Linux man-pages 6.19 (2026-02-08)" → the two field descriptions this row teaches
  from, plus the footer release line as the page prints it.
- `teaches` rewritten. The staged cell restated the row's own scope and repeated the link(2) fact
  that belongs to S218; the new cell is the learner benefit (compare inodes, read a link count).
- `opened` 2026-10-23 → 2026-10-25: the source was opened by this seat this round.
- `used-by` staged "duplicate-verdict-identity.md, quarantine-origin-record-fields-r23.md,
  quarantine-origin-record-fields-r24.md" → `duplicate-verdict-identity.md` only. One staged path
  does not exist anywhere in the lane (`quarantine-origin-record-fields-r23.md`), and the other
  (`quarantine-origin-record-fields-r24.md`) is the F4 origin-record entry whose `source:` lines
  cite S022, S112, S113 and S114 — never S216. Appending the staged cell verbatim would therefore
  add 2 to the C1 counter's k1: one absent path, one path that does not name the row id.

### Staged S118 → lane S217 (Broder)

- `id` S118 → S217. Lane S118 is the Qiita garbage-collection row.
- `source` "On the resemblance and containment of documents — https://doi.org/10.1109/..." → the
  author-hosted PDF. The DOI landing page returns 202 with zero bytes (re-observed this run), so the
  DOI cannot be the address of a row whose claim rests on bytes; it is noted in `anchor` instead.
- `scope` restricted to vocabulary. The staged cell said the taxonomy is what "a `duplicate` receipt
  class would have to name"; it now says what the paper does and does not license, and excludes the
  threshold question explicitly.
- `tier` kept at B, now with a reason a reviewer can test: the paper is authoritative for
  resemblance and containment, not for a filesystem verdict.
- `anchor` staged "§ 2 ...; IEEE Symposium on Foundations of Computer Science / SEQUENCES 1997, DOI
  ...". The FOCS attribution is not supported by any byte this seat opened: the preprint's face
  names no venue, and the Crossref record gives "Proceedings. Compression and Complexity of
  SEQUENCES 1997", Salerno, Italy, pp. 21-29. Now `§ Abstract` is added (the quote lives there) and
  the venue comes from Crossref.
- `teaches` rewritten: the staged cell stated the resemblance/containment distinction, which is the
  scope restated. The new cell is the grounded learner benefit — 50% resemblance over 30 million
  documents is a sampling result, so it is not an equality oracle.
- `opened` 2026-10-23 → 2026-10-25. `recheck` now names the PDF re-fetch, not a DOI re-resolve.
- `used-by` staged "duplicate-verdict-identity.md, duplicate-verdict-taxonomy-r24.md" →
  `duplicate-verdict-identity.md, duplicate-verdict-byte-equality.md`: the taxonomy entry is
  excluded from this round's admit set, and the byte-equality entry does cite S217.

### Staged S122 → lane S218 (link)

- `id` S122 → S218. Lane S122 is `builtin/count-objects.c` at v2.56.0.
- `source` "link(2) — Linux man-pages 6.19 (2026-02-08) — URL" → "link(2) — URL" (same reason as
  S216).
- `anchor` date corrected **2026-02-08 → 2026-02-11**: the served page's footer says 2026-02-11. The
  staged row carried statx's date.
- `teaches` rewritten: the staged cell repeated the scope ("two paths are not two files") and quoted
  a sentence with a nested apostrophe; the new cell is the consequence a reader can use — no
  canonical copy exists.
- `opened` 2026-10-23 → 2026-10-25.
- `used-by` "duplicate-verdict-identity.md, duplicate-verdict-taxonomy-r24.md" → the two admitted
  entries (the excluded taxonomy path is absent in the lane, which would have added 1 to k1).

### Staged S136 → lane S219 (cmp)

- `id` S136 → S219. Lane S136 is an unused id (the registry's gaps run 133–151 and 153–209), but
  the four rows take S216–S219, the next unused ids after S215, so the appended block stays
  contiguous.
- `source` "cmp(1) — Linux man-pages (diffutils 3.12.26, August 2026) — URL" → "cmp(1) — URL".
  "Linux man-pages" is the wrong family label: man7 serves this page from GNU diffutils and prints
  `diffutils 3.12.26-bbc1` in its footer. The version line moved to `anchor`.
- `anchor` kept the exit-status sentence but added the `§ DESCRIPTION` byte-by-byte line it hangs
  on, and states the footer as the page prints it (`diffutils 3.12.26-bbc1`, August 2026) rather
  than the staged "diffutils 3.12.26".
- `teaches` rewritten: the staged cell restated "three-valued oracle", the scope's own words. The
  new cell gives the consequence — trouble must be its own outcome, not "different".
- `opened` 2026-10-23 → 2026-10-25; `recheck` 365d → on-release, because the page tracks diffutils
  releases and the lane's cadence for man7 pages is on-release.
- `used-by` "duplicate-verdict-taxonomy-r24.md" → `duplicate-verdict-byte-equality.md`, the only
  admitted entry that cites S219, and the staged path is absent in the lane (1 more k1).

Cells left unchanged in all four rows: `kind` (docs, docs, docs, paper), `status` (mined), and
S218's `scope` in substance.

## Schema self-check (run on a scratch copy, never on the lane file)

A scratch copy of the lane's committed `corpus/SOURCES.md` plus these four rows (two independent
rebuilds), using the frozen census commands from CORPUS.md § Census:

```
rows                         143          (base 139, +4)
malformed rows (NF!=13)      0
duplicate ids                (none)
enum violations              (none)
tier-inflation               (none)
```

The `mined`-row used-by existence check will still report `duplicate-verdict-identity.md` and
`duplicate-verdict-byte-equality.md` as `missing:` until the L1 lands the two entries in the same
change — expected, and the reason the rows must not be landed alone.
