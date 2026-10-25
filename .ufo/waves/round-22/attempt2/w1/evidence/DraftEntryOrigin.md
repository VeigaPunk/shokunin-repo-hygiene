# DraftEntryOrigin — evidence receipt

Item: lane-format draft of `corpus/knowledge/quarantine-origin-record-fields-r24.md`
(restore side of a per-item origin record), adapted from the staged package entry.
Deliverable: `.ufo/waves/round-22/attempt2/w1/DraftEntryOrigin.md` (draft lives there;
no corpus file created).

All commands below were run from `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Run date: 2026-10-25. No network fetch, no write outside this file and the report,
no git/jj write.

## 1. Snapshot provenance (the only bytes quoted in the draft)

Committed at `a211e4d` (2026-10-25 03:42:51 -0300,
`round-22: declared-evidence audit tool, assimilation entries and gate checker`).
Read this seat; **not** re-fetched from the live URLs.

```
$ sha256sum census/round-22/attempt2/sources/{arch-gio.1.txt,gtk-filetrash.txt,freedesktop-trash.txt,man7-statx.2.txt}
546462a5aa6769a86d7a634434088a874f06c7725b0c3ec0600ac81b5031a12d  census/round-22/attempt2/sources/arch-gio.1.txt
8bed4dac2aacf3de7b58fcc3ce5e3d6baf6a98841700b59c3ad152c3fd8673c9  census/round-22/attempt2/sources/gtk-filetrash.txt
024ddcbfc8f5fb5fa57da2ae8366ab891ab620f04c4e02ef124a3fe4063b9c99  census/round-22/attempt2/sources/freedesktop-trash.txt
9fb42e56248f95dec409744fb93102e7bc477c701fcadfac4093eb8528da965b  census/round-22/attempt2/sources/man7-statx.2.txt
```

Version claims carried in the draft are themselves in these snapshots:

```
$ sed -n '618,622p' census/round-22/attempt2/sources/arch-gio.1.txt
 Package name:
 core/glib2
 Version:
 2.90.1-1
$ grep -n "Publication Date" census/round-22/attempt2/sources/freedesktop-trash.txt
102:Publication Date: 2014-01-02, Version: 1.0
```

## 2. Quote verification (16/16)

Method: whitespace-collapse (`re.sub(r"\s+", " ")`, strip) of the whole snapshot,
then substring test of the collapsed quote — the same squash
`tools/souji-gate-check.py` applies in check 4. `lines=` is the line at which the
collapsed quote completes (multi-line spans end there).

```
OK  words= 9  arch-gio.1.txt          lines=564  [COMMANDS trash OPTIONS --list]
OK  words= 9  arch-gio.1.txt          lines=568  [COMMANDS trash OPTIONS --restore]
OK  words=10  arch-gio.1.txt          lines=570  [COMMANDS trash OPTIONS --restore]
OK  words=18  arch-gio.1.txt          lines=444  [COMMANDS remove]
OK  words= 7  gtk-filetrash.txt       lines=405  [Description]
OK  words=16  gtk-filetrash.txt       lines=406  [Description]
OK  words=10  freedesktop-trash.txt   lines=409  [section 6 Contents of a trash directory]
OK  words=13  freedesktop-trash.txt   lines=425  [section 6 Contents of a trash directory]
OK  words=10  freedesktop-trash.txt   lines=450  [section 6 Contents of a trash directory]
OK  words=15  freedesktop-trash.txt   lines=454  [section 6 Contents of a trash directory]
OK  words=13  freedesktop-trash.txt   lines=455  [section 6 Contents of a trash directory]
OK  words=15  freedesktop-trash.txt   lines=390  [section 6 Important]
OK  words= 8  man7-statx.2.txt        lines=79   [DESCRIPTION struct statx]
OK  words= 6  man7-statx.2.txt        lines=83   [DESCRIPTION struct statx]
OK  words= 6  man7-statx.2.txt        lines=92   [DESCRIPTION struct statx]
OK  words= 6  man7-statx.2.txt        lines=106  [DESCRIPTION struct statx]
misses= 0
```

Longest span 18 words, limit 25. Two spans carry typographic quotes (`“Path”`,
`“Trashcan”`, `“DeletionDate”`), not ASCII `"`, so the gate's `QUOTE_RE`
(`"([^"]{2,400})"`) delimits them correctly.

## 3. Draft predicate dry-run (executed, in-process)

The draft was extracted from the fenced block of `w1/DraftEntryOrigin.md` and run
through the **same regexes** as `tools/souji-gate-check.py`
(`QUOTE_RE`, `SOURCE_RE`, `SNAPSHOT_RE`, `LOCATOR_RE`, `ADMIT_RE`, `REJECT_RE`,
`REASON_RE`, and the same snapshot-containment squash). This is a reimplementation
dry-run, **not** the committed tool reading a file: no draft file exists to point
the tool at, and the contract forbids creating one.

```
opened: ['2026-10-25']
gate rows verified: 16
cited: ['S022'] dangling: []
admit: 16 reject: 1
reject-no-reason: []
fails: []
```

Consequence for the landing step (finding F3 in the report): `SOURCE_RE` is
`^source:\s*(S\d{3,})`, so the three `S-NEW-<slug>` lines are invisible to
check 5. The draft passes only because `S022` is the one real id it cites; a
placeholder draft can go green while its new sources are unregistered.

## 4. Real gate tool, read-only baseline (executed)

Run against the already-committed entry, to confirm the parser, the snapshot
paths and the slice set this draft relies on:

```
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/quarantine-origin-record-fields-r24.md \
    --snapshot-dir census/round-22/attempt2/sources \
    --slice census/round-22/attempt2/quarantine-slice \
    --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0
exit=0
```

This validates the harness and the snapshot path set; it does **not** validate the
draft (different id set, no file).

## 5. The flag entry and its lane path

```
$ git cat-file -e 4edb25dfe262515d0da63224bbba71e02e36cba5:corpus/knowledge/quarantine-origin-record-fields-r23.md
fatal: path 'corpus/knowledge/quarantine-origin-record-fields-r23.md' does not exist in '4edb25dfe262515d0da63224bbba71e02e36cba5'
$ git cat-file -e HEAD:corpus/knowledge/quarantine-origin-record-fields-r23.md
fatal: path 'corpus/knowledge/quarantine-origin-record-fields-r23.md' does not exist in 'HEAD'
$ git log --oneline --all -- corpus/knowledge/quarantine-origin-record-fields-r23.md
(no output, exit 0)
```

`HEAD` is `3216c1998fe04d7e23793ffd4e135bd37c3a11f4`; base
`4edb25dfe262515d0da63224bbba71e02e36cba5` is an ancestor
(`git merge-base --is-ancestor` exit 0). The committed r24 entry
(`corpus/knowledge/quarantine-origin-record-fields-r24.md:48-51`) qualifies the
same fact — the campaign package file is not adopted in this lane and has no
lane path — but states it without a check. The draft carries the check (both
`cat-file -e` calls above plus the empty `--all` history).

Note: the file changed between this seat's two reads. The bytes read at 03:36
(pre-`a211e4d`) named `corpus/knowledge/quarantine-origin-record-fields-r23.md`
unqualified; the committed bytes read at 03:50 carry the qualification. Only the
committed read is cited above.

## 6. Registry state

```
$ grep -cE "^\| S[0-9]{3,}" corpus/SOURCES.md
114
$ grep -oE "^\| S[0-9]{3,}" corpus/SOURCES.md | grep -oE "S[0-9]+" | sort -V | tail -1
S114
```

Next free id: S115. Rows S112–S114 already exist
(`corpus/SOURCES.md:132-134`) and point at the committed r24 path, so the draft
keeps `S022` real and leaves `S-NEW-gio1-trash`, `S-NEW-gtk-filetrash`,
`S-NEW-statx` as placeholders for adoption at S115–S117.

## 7. Limits of this receipt

- Live https URLs were not fetched this seat; quotes are from the committed
  snapshots named above. `opened: 2026-10-25` in the draft refers to the round's
  snapshot capture (`a211e4d`), not to a fetch by this seat.
- The 16/16 result proves byte presence of the quoted spans, nothing about
  whether the surrounding prose reads them correctly.
- Nothing here asserts the draft is admitted: admission requires the real gate
  run after id substitution, plus the registry append.
