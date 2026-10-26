# SwarmScribe25 — SOURCES rows S216–S219, search-log note, Paths line

## Status

STATUS: PASS — four rows, one search-log note and one Paths line drafted and schema-checked in
scratch, every cell written from bytes opened this run; one frozen-contract ordering conflict
(finding 1) is reported rather than resolved by this seat.

## Evidence

Lane read at `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (HEAD; preregistration commit on base
`691dd29211c53d0ef94fa072394cb9c8a69fe92e`). `corpus/SOURCES.md` at HEAD is blob
`9af347a485bb0bb40d26e156406d96c46564f7d1` and the working tree copy is unmodified
(`git status --porcelain -- corpus/SOURCES.md corpus/knowledge census/round-29` printed nothing).

```
$ curl -sS -o <file> -w '%{http_code} %{size_download}\n' <url>
statx.2 200 33125   sha256 2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e
link.2  200 19883   sha256 9cb197a7abe32a459bb3dbe96f67d906ff199e0f9d5f19f41a3a05e46cea1ec9
cmp.1   200 9791    sha256 5c68e8d874e987391e7679dd2637f953b90087076bffe6de18c40db86cd046a3
broder  200 254930  sha256 da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b

$ curl -sS -o /dev/null -w '%{http_code} %{size_download} %{url_effective}\n' -L https://doi.org/10.1109/SEQUEN.1997.666900
202 0 https://ieeexplore.ieee.org/document/666900/

$ curl -sS https://api.crossref.org/works/10.1109/SEQUEN.1997.666900   # 200, 3063 bytes, sha256 f1aeff86…
container-title: Proceedings. Compression and Complexity of SEQUENCES 1997 (Cat. No.97TB100171)
event: Compression and Complexity of SEQUENCES 1997, Salerno, Italy; page: 21-29; issued: null

Footers as served:
statx.2.html:587  Linux man-pages 6.19            2026-02-08
link.2.html:310   Linux man-pages 6.19            2026-02-11
cmp.1.html:156    diffutils 3.12.26-bbc1         August 2026
```

Quotes used in the rows, each re-checked verbatim against the fetched bytes after joining the
page's line wraps, each ≤25 words and containing no pipe: "The number of hard links on a file."
(statx.2 § DESCRIPTION, stx_nlink); "The inode number of the file." (stx_ino); "This new name may be
used exactly as the old one for any operation" (link.2 § DESCRIPTION, lines 100-101); "Exit status
is 0 if inputs are the same, 1 if different, 2 if trouble." (cmp.1 § DESCRIPTION, lines 113-114);
"resemblance r(A, B) and their containment c(A, B) that seem to capture well the informal notions of
“roughly the same” and “roughly contained.”" (broder abstract); "We calculated our clusters based on
a 50% resemblance." (broder § 1).

Schema census, run on a scratch copy of the lane file plus the four rows (two independent rebuilds
under `/var/tmp/souji-r29-SwarmScribe25/`), using the frozen commands from CORPUS.md § Census:

```
rows 143            (139 + 4)
malformed (NF!=13)  0
duplicate ids       none
enum violations     none
tier inflation      none
used-by existence   missing: duplicate-verdict-identity.md
                    missing: duplicate-verdict-byte-equality.md
```

Merge-package scan (`/home/vgpnk/Projects/shokuknow/merge/souji`, read-only): 9 entries carry
`ground: F3`, citing 13 distinct staged row ids (S117 S118 S122 S136 S145 S151 S162 S172 S178 S179
S213 S216 S217); 2 included, 7 excluded, reasons in the delivery's search-log note.

## Findings

1. **The frozen preregistration fixes the four row ids in a different order than the two entry
   files and this seat's assignment.** `census/round-29/records/preregistration.txt:9` reads "Four
   new rows S216-S219 (statx, link, cmp, Broder via the author-hosted PDF" — i.e. S217 link,
   S218 cmp, S219 Broder. The entries the L1 must land read
   `.ufo/waves/round-29/w1/deliver-duplicate-verdict-identity.md:2` "source: S217 — A. Z. Broder,
   On the resemblance and containment of documents, SEQUENCES 1997" and
   `deliver-duplicate-verdict-byte-equality.md:1` "source: S219 — cmp(1), GNU diffutils". This
   seat's assignment matches the entries, and the rows were drafted that way. No counter is
   affected (still 4 rows, ids S216–S219, rows 139→143, F3 entries 0→2), but the L1 must either
   land the permutation with a logged amendment-free note, or re-point the entries' front matter
   and Gate blocks. This seat does not choose between them.
2. **Staged S122's anchor date is wrong.** `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:20`
   says "Linux man-pages 6.19 (2026-02-08)"; the served page's footer says
   `Linux man-pages 6.19            2026-02-11` (`link.2.html:310`). S218 carries 2026-02-11.
3. **Appending staged S117's `used-by` verbatim would add 2 to the C1 counter's k1.**
   `SOURCES.append.md:15` names `corpus/knowledge/quarantine-origin-record-fields-r23.md` (absent
   from the lane) and `corpus/knowledge/quarantine-origin-record-fields-r24.md` (present, but its
   `source:` lines cite S022, S112, S113, S114 and never S216). K1 counts a used-by path that does
   not exist or does not name the row id.
4. **Staged S118's venue attribution is unsupported by any byte opened this run.**
   `SOURCES.append.md:16` says "IEEE Symposium on Foundations of Computer Science / SEQUENCES
   1997"; the preprint's face (`broder97resemblance.pdf` page 1) names the title, the author and
   DEC Systems Research Center only, and the Crossref record gives "Proceedings. Compression and
   Complexity of SEQUENCES 1997", Salerno, Italy, pp. 21-29 with a null issued date. S217 drops FOCS
   and cites Crossref for the venue.
5. **Staged S136 mislabels the page family and the version.** `SOURCES.append.md:34` says
   "Linux man-pages (diffutils 3.12.26, August 2026)"; the page is GNU diffutils served by man7 and
   its footer reads `diffutils 3.12.26-bbc1` / August 2026 (`cmp.1.html:156`). S219 carries the
   bbc1 version string and no "Linux man-pages" label.
6. **Six staged ids in the F3 set are not free in the lane.** S117 → lane `git-prune(1)`, S118 →
   lane Qiita garbage-collection note, S122 → lane `builtin/count-objects.c` at v2.56.0, S213 →
   lane POSIX.1-2024 `rename()`; staged S216 and S217 are this round's new ids for statx and
   Broder. The numbers reach text only in the two excluded entries
   `near-duplicate-literature-identity-r33.md` (staged S213) and
   `near-duplicate-threshold-source-r34.md` (staged S216, S217), so no landing citation is
   affected. This is guard input, not a guard proof.
7. **The Broder snapshot hash in the entries does not match a `pdftotext -layout` decode of the
   same PDF.** Both entries record the decoded text as sha256 `3ba1e117…`; this seat's decode of
   `da122799…` hashes `ddf97f6b12f7e7e4b4c9643a44eb4979f1fdd09d109250cc100eba0600e2fd7a`. The quoted
   sentence is verbatim in the decode either way, but the L1 should commit the exact decode the
   entries hashed (or restate their `verified-at` line), otherwise the Gate hash is not re-derivable
   from the committed file at `census/round-29/sources/`.
8. **These rows must not land without the two entries.** On the scratch tree the frozen
   mined-used-by check reports exactly two missing paths, which are the two entry files; landing
   the rows first would add 2 to k1 and break C1's zero target.
9. **S216 reuses lane S114's URL under a narrower scope.** S114 already grounds statx identity
   fields for the F4 origin record (`corpus/SOURCES.md:135`). S216 is scoped to the duplicate-verdict
   test and names S114 for the field list. Precedent for two scopes on one URL: S036/S049,
   S042/S057, S045/S059, S128/S215. If a reviewer prefers one row, the alternative is widening
   S114's `used-by`, which is an append-only-loggable cell change, not a new row.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-sources-rows.md` — rows S216–S219 in the 11-column schema, the
  search-log note, the Paths line, the collision note, and the cell-by-cell diff against staged
  S117 S118 S122 S136.

Scratch `/var/tmp/souji-r29-SwarmScribe25/` removed at seat end. This seat wrote nothing else, ran
no git mutation, and read outside `souji-shokunin/` only `CORPUS.md` and the read-only merge
package under `/home/vgpnk/Projects/shokuknow/merge/souji/`.
