# Deliver — C3 append block: four rows, lane ids S216–S219

Paste target: `corpus/SOURCES.md`, at the end of the `## Registry` table — after the S215
row and before the blank line that precedes `## Paths`. Append only: no existing row is
touched (CORPUS rule 2). Lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`.

Land-order constraint: every `used-by` path must exist at the same commit (else
`sources-census.sh validate` reports E11 on the new rows). Land
`corpus/knowledge/duplicate-verdict-identity.md` and
`corpus/knowledge/duplicate-verdict-byte-equality.md` in the same commit as these rows.

## Rows

```markdown
| S216 | statx(2) — Linux man-pages 6.19 (2026-02-08) — https://man7.org/linux/man-pages/man2/statx.2.html | docs | A | the identity fields a duplicate verdict must distinguish — inode number and hard-link count — plus the per-item origin fields; not the origin-record scope S114 holds and not a detection algorithm | § DESCRIPTION struct statx fields stx_ino, stx_nlink, stx_btime, stx_mnt_id; § CONSTANTS STATX_MNT_ID_UNIQUE (since Linux 6.8); Linux man-pages 6.19 (2026-02-08), page fetched 2026-10-25, sha256 2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e | stx_ino is the inode number and stx_nlink the number of hard links, so two names for one inode are not two files; stx_btime and stx_mnt_id are the origin fields a receipt records | mined | 2026-10-25 | 365d | corpus/knowledge/duplicate-verdict-identity.md |
| S217 | On the resemblance and containment of documents — https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf | paper | B | the resemblance and containment vocabulary a duplicate verdict must name, two measures each a number between 0 and 1; document similarity from a web-crawling study, not filesystem verdicts and not a threshold recommendation | Abstract p.1 and § 2 Definitions as set intersection problems p.2; author-hosted PDF, 9 pages, fetched 2026-10-25, sha256 da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b; the DOI 10.1109/SEQUEN.1997.666900 landing page answered HTTP 202 with a zero-byte body on 2026-10-25 | resemblance r(A,B) and containment c(A,B) are two distinct measures, each a number between 0 and 1, so duplicate is a thresholded family of verdicts rather than a single predicate | mined | 2026-10-25 | 365d | corpus/knowledge/duplicate-verdict-identity.md, corpus/knowledge/duplicate-verdict-byte-equality.md |
| S218 | link(2) — Linux man-pages 6.19 (page dated 2026-02-11) — https://man7.org/linux/man-pages/man2/link.2.html | docs | A | the kernel statement that two names may refer to one file, so a duplicate verdict must compare inodes rather than path names; not the linkat differences and not an origin-record claim | § DESCRIPTION link() creates a new link; page dated 2026-02-11 in man-pages 6.19, fetched 2026-10-25, sha256 9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9 | both names refer to the same file and it is impossible to tell which name was the original, so a duplicate verdict must compare inodes, not path names | mined | 2026-10-25 | 365d | corpus/knowledge/duplicate-verdict-identity.md, corpus/knowledge/duplicate-verdict-byte-equality.md |
| S219 | cmp(1) — Linux man-pages (diffutils 3.12.26-bbc1, August 2026) — https://man7.org/linux/man-pages/man1/cmp.1.html | docs | A | the byte-equality primitive and its three-valued exit contract that a duplicate verdict is defined against; not a duplicate-detection algorithm and not a threshold | § DESCRIPTION exit-status sentence; page generated 2026-08-03 from diffutils 3.12.26-bbc1, fetched 2026-10-25, sha256 5c68e8d874e987391e7679dd2637f953b90087076bffe6de18c40db86cd046a3 | cmp compares byte by byte and exits 0 when the inputs are the same, 1 when different and 2 on trouble, so byte-identical has a precise three-valued oracle | mined | 2026-10-25 | 365d | corpus/knowledge/duplicate-verdict-byte-equality.md |
```

## Renumber map (by document, never by arithmetic)

| campaign id in `merge/souji/SOURCES.append.md` | lane id | document |
|---|---|---|
| S117 | S216 | statx(2) man page |
| S118 | S217 | Broder, On the resemblance and containment of documents |
| S122 | S218 | link(2) man page |
| S136 | S219 | cmp(1) man page |

The campaign ids S117/S118/S122/S136 **and** S216/S217/S218/S219 are already used in the
package for other documents (campaign S216 is a Breitinger et al. chapter, S217 an
Unpaywall record, S218/S219 two git docs at v2.45.0). Lane ids S216–S219 were free
(`in_lane_registry=0`, 0–3-space pattern), so the adopted rows take them and every entry
citation is re-pointed by document.

## Normalization applied (campaign schema -> fleet/census schema)

- 11 columns, `NF=13` verified for each of the four rows; zero escaped or literal `|` in any
  cell, so anchors and teaches were rewritten in this seat's words.
- `status` `mined`; `opened` `2026-10-25`; `recheck` `365d` for all four.
- `used-by` lists exactly the admitted entries that cite the row: S216 -> identity entry;
  S217, S218 -> identity **and** byte-equality; S219 -> byte-equality only.
- Broder's locator is the author-hosted PDF, because the DOI landing page is unusable
  (`HTTP 202`, `content-length: 0`, 0 bytes downloaded, 2026-10-25).

Recheck prose stripped from the campaign rows (recorded here, not in the registry):

| lane id | campaign recheck cell | normalized |
|---|---|---|
| `S216` | `on-release — re-read the man-pages 6.x statx(2) page` | `365d` |
| `S217` | `365d — re-resolve the DOI and re-read § 2` | `365d` (DOI re-resolution is unexecutable; the PDF is the locator) |
| `S218` | `on-release — re-read the man-pages 6.x link(2) page` | `365d` |
| `S219` | `365d — re-fetch the man7 cmp(1) page` | `365d` |

The two `on-release` cadences were replaced by `365d` as instructed; note this is a
*tightening* (an on-release recheck is never overdue, a 365d one is).

## Gate quotes (each opened by this seat on 2026-10-25, <= 25 words, no pipe character)

| id | location | quote |
|---|---|---|
| `S216` | statx(2) § DESCRIPTION, `struct statx` member comment | `stx_ino; /* Inode number */` |
| `S216` | statx(2) § CONSTANTS, `STATX_MNT_ID_UNIQUE` | `STATX_MNT_ID_UNIQUE Want unique stx_mnt_id (since Linux 6.8)` |
| `S217` | Broder PDF, Abstract p.1 | `their resemblance r(A, B) and their containment c(A, B) that seem to capture well the informal notions of “roughly the same” and “roughly contained.”` |
| `S218` | link(2) § DESCRIPTION, last sentence of the hard-link paragraph | `it is impossible to tell which name was the original` |
| `S219` | cmp(1) § DESCRIPTION, closing paragraph | `Exit status is 0 if inputs are the same, 1 if different, 2 if trouble.` |

## Fetched-byte digests (identical to `.ufo/waves/round-29/w1/sources/SHA256SUMS`)

| file | sha256 |
|---|---|
| statx.2.html | `2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e` |
| link.2.html | `9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9` |
| cmp.1.html | `5c68e8d874e987391e7679dd2637f953b90087076bffe6de18c40db86cd046a3` |
| broder97resemblance.pdf | `da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b` |

If the snapshots land at `census/round-29/sources/<file>`, an anchor may cite that path; the
digests above are the ones those files must carry.

## Expected validator result after landing

`sources-census.sh validate --file <lane>/corpus/SOURCES.md` -> exit 0, `ok`, and exactly
one new warning: `W04 S216 duplicate url man7.org/linux/man-pages/man2/statx.2.html across
scopes` (S114 holds the same URL under the origin-record scope). No E03 and no E04: the ids
are free and S216's scope string differs from S114's, so the URL+scope pair is new.
