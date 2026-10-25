# Connector evidence — sibling-overlap scan (souji r22 attempt2)

Seat: L1Souji22.Connector. Read-only scan; no lane outside souji was written to,
no git/jj write was run, no cleanup was executed. Base lane revision
4edb25dfe262515d0da63224bbba71e02e36cba5.

All blocks below are executed observations unless marked `[source-inferred]`.

## E1 — fleet census of candidate lanes

```
$ ls -d /home/vgpnk/Projects/shokunin/*-shokunin/ | wc -l
21
```
Lanes: audio, chousa, game-dev-2d, game-dev-3d, kagi, kaidoku, kake, kama,
kasegi, kengaku, kotoba, kotodama, kumitate, lore, mado, mori, revenger,
souji, tabi, tameshi, tsukuroi.

## E2 — exact-URL search over every lane's corpus/SOURCES.md and corpus/knowledge

Scope exactly as the item states: each lane's `corpus/knowledge/` and
`corpus/SOURCES.md`.

```
$ for u in man7.org/linux/man-pages/man2/rename man7.org/linux/man-pages/man1/mv \
           man7.org/linux/man-pages/man2/statx docs.gtk.org/gio \
           man.archlinux.org/man/gio specifications.freedesktop.org \
           git-scm.com/docs/git-prune; do grep -rn -F "$u" */corpus/ ; done
```

Results (only souji appears; siblings produced zero rows):

| URL | holding files (lane:path:line) |
|---|---|
| https://man7.org/linux/man-pages/man2/rename.2.html | souji:corpus/SOURCES.md:130 (S110); souji:corpus/knowledge/quarantine-staging-no-copy-r23.md:2,5,62,63,66,67 |
| https://man7.org/linux/man-pages/man1/mv.1.html | souji:corpus/SOURCES.md:131 (S111); souji:corpus/knowledge/quarantine-staging-no-copy-r23.md |
| https://man7.org/linux/man-pages/man2/statx.2.html | souji:corpus/SOURCES.md:134 (S114); souji:corpus/knowledge/quarantine-origin-record-fields-r24.md:3,6,31,33,68 |
| https://docs.gtk.org/gio/method.File.trash.html | souji:corpus/SOURCES.md:133 (S113); souji:corpus/knowledge/quarantine-origin-record-fields-r24.md:2 |
| https://man.archlinux.org/man/gio.1.en | souji:corpus/SOURCES.md:132 (S112); souji:corpus/knowledge/quarantine-origin-record-fields-r24.md:1,59 |
| https://specifications.freedesktop.org/trash/latest/ | souji:corpus/SOURCES.md:42 (S022, mined 2026-10-19); souji:corpus/knowledge/trash-spec-restorable-quarantine.md:1,3; souji:corpus/knowledge/quarantine-origin-record-fields-r24.md:4; souji:corpus/lessons/round-12.md:283 |
| https://git-scm.com/docs/git-prune | **none** — zero files in any lane's corpus (`grep -rl 'git-prune' */corpus/ → NONE`) |

Whole-corpus cross-check (all file types, not only .md) reproduced the same
exclusivity, e.g.:

```
$ grep -rl 'man1/mv\.1\.html' */corpus/    -> souji only
$ grep -rl 'method\.File\.trash\.html' */corpus/ -> souji only
$ grep -rl 'freedesktop\.org/trash' */corpus/    -> souji only
$ grep -rl 'git-prune' */corpus/                 -> NONE
```

Sibling URL families that are *near misses* but not the cited documents
(`man.archlinux.org/man/{pacman.8,systemd.exec.5,access.2,...}`,
`man7.org/.../man2/{open.2,...}`, `git-scm.com/docs/{git-gc,git-fsck,git-fetch}`)
therefore carry no same-URL row.

## E3 — staged package inventory

```
$ ls /home/vgpnk/Projects/shokuknow/merge/souji
MERGE-REPORT.json  MERGE-REPORT.md  SOURCES.append.md  knowledge/
$ ls knowledge/corpus/knowledge | wc -l
68
$ grep -cE '^\| S[0-9]+' SOURCES.append.md
134
$ grep -oE '^\| S[0-9]+' SOURCES.append.md | sort -V | head -1 ; ... | tail -1
S109 ... S242
```

Staged F4-candidate files and digests (sha256, first 12):

```
quarantine-staging-no-copy.md            951dbdddafe1
quarantine-staging-no-copy-r23.md        f13fb769c418
quarantine-staging-no-copy-r24.md        109a2a6bed4e
quarantine-origin-record-fields-r23.md   a2b46cf83652
quarantine-origin-record-fields-r24.md   0fb78aef7929
origin-record-durability-r28.md          04c1ce2627f4
origin-record-exclusivity-r28.md         1c321e53ab29
origin-record-format-gvfs-r26.md         18fd4ecd92a4
origin-record-mechanism-set-r33.md       8bd42fbddf0d
origin-record-writer-r27.md              3e6a298efbff
```

Not byte copies: the two adopted lane entries differ from their staged
namesakes.

```
$ sha256sum corpus/knowledge/quarantine-staging-no-copy-r23.md \
            /home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-staging-no-copy-r23.md
0081e83045a9...  corpus/knowledge/quarantine-staging-no-copy-r23.md      (4848 B)
f13fb769c418...  .../merge/souji/.../quarantine-staging-no-copy-r23.md   (3490 B)

$ sha256sum corpus/knowledge/quarantine-origin-record-fields-r24.md \
            /home/vgpnk/Projects/shokuknow/merge/souji/.../quarantine-origin-record-fields-r24.md
b92f8118ab9c...  corpus/knowledge/quarantine-origin-record-fields-r24.md (5299 B)
0fb78aef7929...  .../merge/souji/.../quarantine-origin-record-fields-r24.md (3665 B)
```

Lane files add a frontmatter block (own `source:` ids, `verified-at`,
`recheck`, `ground:`) and their own `## Gate`; the staged files carry the
campaign ids instead (`S124/S116/S115` for staging, `S137/S126/S117/S022` for
the record).

## E4 — id-space collision (post-mint)

```
$ grep -oE '^\| S[0-9]+' corpus/SOURCES.md | wc -l
114
$ grep -E '^\| S(109|110|111|112|113|114) ' corpus/SOURCES.md
S109  souji round-2 RENAME_NOREPLACE probe, vendored
S110  rename(2), man-pages 6.19
S111  mv(1), GNU coreutils
S112  gio(1), GIO commandline tool
S113  GLib GIO g_file_trash() method reference
S114  statx(2), man-pages 6.19

$ grep -E '^\| S(109|110|111|112|113|114) ' \
    /home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md
S109  git-fetch(1)                                  https://git-scm.com/docs/git-fetch
S110  git/git v2.56.0 builtin/fetch.c ...           https://github.com/git/git/blob/v2.56.0/builtin/fetch.c
S111  git/git v2.56.0 builtin/pull.c                https://github.com/git/git/blob/v2.56.0/builtin/pull.c
S112  git-count-objects(1)                          https://git-scm.com/docs/git-count-objects
S113  git-fsck(1)                                   https://git-scm.com/docs/git-fsck
S114  git-prune(1)                                  https://git-scm.com/docs/git-prune
```

Same id string, different document, six times. The lane lesson's collision
receipt is:

```
corpus/lessons/round-22.md:318-321
  "... enforced by the frozen collision step (`assimilation/collisions` is
   empty: reg 108 ids, staged 134 ids, 0 collisions)."
```

`reg 108 ids` is the registry *before* this round minted S109–S114; the staged
range starts at S109. So "0 collisions" holds for the pre-mint range only.

The collision is visible inside the lane tree without reading the campaign:

```
$ cat census/round-22/attempt2/slice-verdicts.tsv | head -1
S114	accepted	snapshot git-scm git-prune 2026-10-25: sentence present, ...
```
that row's S114 is `git-prune(1)`, while `corpus/SOURCES.md` S114 is `statx(2)`
— same round, same directory tree, two documents under one id.

## E5 — slice id extraction and verdict coverage (my own reproduction)

```
$ python3 -B -c "re.compile(r'S\d{3,}') over quarantine-slice; compare to TSV col1"
slice ids: ['S114','S123','S124','S126','S131','S133','S138','S118']
T= 8 verdict rows= 8
missing from verdicts: []
extra verdict ids: []
```

Raw slice bytes:

```
$ cat -A census/round-22/attempt2/quarantine-slice
 S114   `payload-absent` $
 ...
 S118`   the cited source could not be fetched, so no quote was checked $
```

The malformed S118 line still yields id `S118` because `SLICE_ID_RE =
re.compile(r"S\d{3,}")` (tools/souji-gate-check.py:45) is unanchored and stops
before the backtick; the trailing prose is ignored. Coverage is 8/8 today, but
the regex would also accept any `S<digits>` appearing in free prose
[source-inferred from tools/souji-gate-check.py:137-168].

## E6 — committed snapshot inventory (git-prune absent)

```
$ ls census/round-22/attempt2/sources/
arch-gio.1.raw           arch-gio.1.txt
freedesktop-trash.raw    freedesktop-trash.txt
gtk-filetrash.raw        gtk-filetrash.txt
man7-mv.1.raw            man7-mv.1.txt
man7-rename.2.raw        man7-rename.2.txt
man7-statx.2.raw         man7-statx.2.txt
vendor-noreplace-probe.out
$ ls census/round-22/attempt2/sources/ | grep -i prune
(none)
```

The S114 slice verdict cites "snapshot git-scm git-prune", but no git-prune
snapshot exists in the lane's committed snapshot directory; the pointer
resolves outside the lane. Not evidence of fabrication — the campaign snapshot
tree was not read (out of scope), so this is an unresolvable-in-lane pointer,
not a failed quote.

## E7 — F4 coverage-map table state

```
$ sed -n '42p' corpus/README.md
| F4 restorable quarantine, file-system semantics | frontier, entries held |
  `knowledge/trash-spec-restorable-quarantine.md`, `knowledge/quarantine-same-filesystem-rename.md` |

$ grep -n 'quarantine-staging-no-copy\|quarantine-origin-record' corpus/README.md
429:- `knowledge/quarantine-staging-no-copy-r23.md` — ...
432:- `knowledge/quarantine-origin-record-fields-r24.md` — ...
```
The frontier table row still says "entries held" and lists two files; the two
new entries appear only in the round-22 prose section.

## E8 — in-lane claim duplication with the HELD K5 entry

```
$ sed -n '1,40p' corpus/knowledge/quarantine-same-filesystem-rename.md
source: S025 https://www.gnu.org/software/coreutils/manual/html_node/mv-invocation.html
  (para 3 "..."; `--no-copy`); S024 ...
- "GNU `mv` first tries `renameat2(…, RENAME_NOREPLACE)`."
- "`mv --no-copy` turns the cross-device case into a hard failure (exit 1, source untouched)"
```
Round-22's adopted staging entry states as its novelty (§Claim) the
no-clobber rename plus `mv --no-copy` ("... and `mv --no-copy` is the portable
fallback"). The `mv --no-copy` half is already carried by the HELD S025 entry;
the genuinely new parts are the rename(2) per-filesystem support schedule
(S110) and the vendored five-device probe (S109).

## E9 — r24 entry's "already holds" wording

```
corpus/knowledge/quarantine-origin-record-fields-r24.md:12-14
  "The lane already holds the trash *layout* (S022: ...) and the *write
   contract* (S113: the trash call is documented recoverable and refuses
   rather than deleting)."
```
S113 is minted in this same round (`corpus/SOURCES.md:133`, mined 2026-10-25),
so the entry attributes pre-existing knowledge to a row created alongside it.
Not coverable by C1's frozen enum (which reads SCORECARD.md only), so this is
reported as a finding, not as a C1 mismatch.

## E10 — peer-reported S131 class change (not adjudicated here)

`L1Souji22.Slice131` reports S131 as `refused` (citation-class defect; payload
absent from the cited r23-worktree-census.out, span belongs to
git-worktree(1)), against the committed TSV row `S131 accepted`. Both are one
frozen class; V=T either way. Recorded as a live divergence, not resolved by
this seat.
