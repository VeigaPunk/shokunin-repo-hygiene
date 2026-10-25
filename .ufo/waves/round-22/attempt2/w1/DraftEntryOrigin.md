STATUS: PASS

# DraftEntryOrigin — lane-format draft of the per-item origin record entry (restore side)

Scope: one deliverable — a lane-format knowledge entry at
`corpus/knowledge/quarantine-origin-record-fields-r24.md`, adapted from
`/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-origin-record-fields-r24.md`.
No corpus file was created or edited; the draft lives in this report.

## Executed evidence

### E1 — target path state (executed)

```
$ git log -1 --format='%ci %s' a211e4d
2026-10-25 03:42:51 -0300 round-22: declared-evidence audit tool, assimilation entries and gate checker
$ git rev-parse HEAD
3216c1998fe04d7e23793ffd4e135bd37c3a11f4
$ git merge-base --is-ancestor 4edb25dfe262515d0da63224bbba71e02e36cba5 HEAD; echo $?
0
$ git status --short corpus/knowledge
(no output)
```

`corpus/knowledge/quarantine-origin-record-fields-r24.md` is already committed
(introduced by `a211e4d`, today 03:42:51) and the worktree is clean for
`corpus/knowledge`. The draft below is therefore the **pre-adoption** form the
assignment asks for; landing it is a replacement, not a first write.

### E2 — the flag entry the source amends (executed)

```
$ git cat-file -e 4edb25dfe262515d0da63224bbba71e02e36cba5:corpus/knowledge/quarantine-origin-record-fields-r23.md
fatal: path 'corpus/knowledge/quarantine-origin-record-fields-r23.md' does not exist in '4edb25dfe262515d0da63224bbba71e02e36cba5'
$ git cat-file -e HEAD:corpus/knowledge/quarantine-origin-record-fields-r23.md
fatal: path 'corpus/knowledge/quarantine-origin-record-fields-r23.md' does not exist in 'HEAD'
$ git log --oneline --all -- corpus/knowledge/quarantine-origin-record-fields-r23.md
(no output, exit 0)
```

The lane has never had a file at that path. The flag the source amends exists
in the staged package
(`/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-origin-record-fields-r23.md:41,46`)
and, lane-side, in `corpus/knowledge/trash-spec-restorable-quarantine.md:35`
(the trashinfo format is an operator decision). The draft names both and carries
the absence as an executable receipt; the committed entry states the same
qualification at `:48-51` but without the check.

### E3 — every quoted span verified against a snapshot saved this round (executed)

Snapshots read (opened this seat, committed at `a211e4d`, sha256):

```
546462a5aa6769a86d7a634434088a874f06c7725b0c3ec0600ac81b5031a12d  arch-gio.1.txt
8bed4dac2aacf3de7b58fcc3ce5e3d6baf6a98841700b59c3ad152c3fd8673c9  gtk-filetrash.txt
024ddcbfc8f5fb5fa57da2ae8366ab891ab620f04c4e02ef124a3fe4063b9c99  freedesktop-trash.txt
9fb42e56248f95dec409744fb93102e7bc477c701fcadfac4093eb8528da965b  man7-statx.2.txt
```

Whitespace-collapsed containment check (same squash the gate tool applies),
one line per span:

```
OK  words= 9 arch-gio.1.txt [COMMANDS trash OPTIONS --list] :: List files in the trash with their original locations.
OK  words= 9 arch-gio.1.txt [COMMANDS trash OPTIONS --restore] :: Restore a file from trash to its original location.
OK  words=10 arch-gio.1.txt [COMMANDS trash OPTIONS --restore] :: If the original directory doesn’t exist, it will be recreated.
OK  words=18 arch-gio.1.txt [COMMANDS remove] :: This command removes files irreversibly. If you want a reversible way ...
OK  words= 7 gtk-filetrash.txt [Description] :: Sends file to the “Trashcan”, if possible.
OK  words=16 gtk-filetrash.txt [Description] :: This is similar to deleting it, but the user can recover it before emp...
OK  words=10 freedesktop-trash.txt [section 6] :: The key “Path” contains the original location of the file/directory
OK  words=13 freedesktop-trash.txt [section 6] :: The key “DeletionDate” contains the date and time when the file/direct...
OK  words=10 freedesktop-trash.txt [section 6] :: the implementation MUST create the corresponding file in $trash/info f...
OK  words=15 freedesktop-trash.txt [section 6] :: On Unix-line systems this is done by generating a filename, and then o...
OK  words=13 freedesktop-trash.txt [section 6] :: If that succeeds the creation was atomic (at least on the same machine
OK  words=15 freedesktop-trash.txt [section 6 Important] :: A filename in the $trash/files directory MUST NEVER be used to recover
OK  words= 8 man7-statx.2.txt [DESCRIPTION struct statx] :: __u32 stx_nlink; /* Number of hard links */
OK  words= 6 man7-statx.2.txt [DESCRIPTION struct statx] :: __u64 stx_ino; /* Inode number */
OK  words= 6 man7-statx.2.txt [DESCRIPTION struct statx] :: struct statx_timestamp stx_btime; /* Creation */
OK  words= 6 man7-statx.2.txt [DESCRIPTION struct statx] :: __u64 stx_mnt_id; /* Mount ID */
misses= 0
```

Live URLs were **not** re-fetched by this seat; the bytes above are the
round's committed snapshots. Version claims used in the draft are themselves
in the snapshots: `census/round-22/attempt2/sources/arch-gio.1.txt:618-622`
(`core/glib2` / `Version: 2.90.1-1`) and
`freedesktop-trash.txt:102` (`Publication Date: 2014-01-02, Version: 1.0`).

### E4 — registry state (executed)

```
$ grep -cE "^\| S[0-9]{3,}" corpus/SOURCES.md
114
$ grep -oE "^\| S[0-9]{3,}" corpus/SOURCES.md | grep -oE "S[0-9]+" | sort -V | tail -1
S114
```

Next free id is **S115**. `S022` already exists and is cited, not duplicated
(the draft keeps `S022` real and uses `S-NEW-<slug>` placeholders for the three
unregistered documents).

## Draft (deliverable)

````markdown
source: S-NEW-gio1-trash — https://man.archlinux.org/man/gio.1.en — § COMMANDS `trash` (OPTIONS `--list`, `--restore`) and the `remove` synopsis; glib2 2.90.1-1
source: S-NEW-gtk-filetrash — https://docs.gtk.org/gio/method.File.trash.html — § Description
source: S022 — https://specifications.freedesktop.org/trash/latest/ — Publication Date 2014-01-02, Version 1.0, § 6 Contents of a trash directory; already in this registry — cited, not duplicated
source: S-NEW-statx — https://man7.org/linux/man-pages/man2/statx.2.html — § DESCRIPTION struct statx
verified-at: 2026-10-25 — glib2 2.90.1-1 `gio(1)`, GIO File.trash reference, Trash spec 1.0 and man-pages 6.19 as committed under census/round-22/attempt2/sources/ (commit a211e4d); every quoted span below re-checked whitespace-collapsed against those snapshots this round
recheck: 180d — re-open census/round-22/attempt2/sources/{arch-gio.1,gtk-filetrash,freedesktop-trash,man7-statx.2}.txt
ground: F4 — restorable quarantine (the restore side of a per-item origin record: the field a restore consumes)

# A per-item origin record must carry the original path, because restore consumes it

## Claim (F4, sourced — amendment, by addition, to the round-2 flag entry)
The round-2 flag entry stopped at the open question: no per-item record format
is specified for a souji quarantine, and the format stays with the operator
(staged `quarantine-origin-record-fields-r23.md:41,46`; the lane's own form of
that flag is `trash-spec-restorable-quarantine.md:35`). This entry answers only
the part of that question the reference behaviour can answer: which field a
**restore** consumes. Every double-quoted span below appears verbatim
(whitespace-collapsed) in the snapshot named by its Gate row, at the locator
given beside it.

1. **The original location is the load-bearing field.** `gio trash --list`
   gives "List files in the trash with their original locations." (§ COMMANDS
   `trash`, OPTIONS `--list`), and `gio trash --restore` gives "Restore a file
   from trash to its original location." (§ COMMANDS `trash`, OPTIONS
   `--restore`). The Trash spec makes the same field a required key: "The key
   “Path” contains the original location of the file/directory" (§ 6). A
   record without that path is not restorable; every other field discussed
   here is optional *to restore*.
2. **The original directory need not survive.** The same manual: "If the
   original directory doesn’t exist, it will be recreated." (§ COMMANDS
   `trash`, OPTIONS `--restore`). What restore requires is the recorded path,
   not the continued existence of its parent.
3. **A path derived from the payload is not a substitute for the field.** The
   spec's Important paragraph forbids it: "A filename in the $trash/files
   directory MUST NEVER be used to recover the original filename" (§ 6,
   Important). That is the read-side reason souji's installed quarantine —
   which keeps the repo-relative path in the staged name and writes no per-item
   record (`trash-spec-restorable-quarantine.md:32`) — needs the explicit
   field, not a naming convention.
4. **The reversible alternative is documented, which is what makes a
   receipt-gated quarantine a choice rather than a wish.** "This command
   removes files irreversibly. If you want a reversible way to remove files,
   see the trash command." (§ COMMANDS `remove`).
5. **The write contract and the layout are already held — as reference
   behaviour, not as souji's design.** GIO's trash call is recoverable by
   design and refuses where it cannot comply: "Sends file to the “Trashcan”,
   if possible." and "This is similar to deleting it, but the user can recover
   it before emptying the trashcan." (§ Description). The spec fixes the
   ordering reference: "the implementation MUST create the corresponding file
   in $trash/info first", "On Unix-line systems this is done by generating a
   filename, and then opening with O_EXCL." — with the atomicity scoped to the
   record's own creation: "If that succeeds the creation was atomic (at least
   on the same machine)" (§ 6). Nothing there specifies the gap between writing
   a record and moving a payload.
6. **Identity fields are available, not required by restore.** `statx(2)`
   exposes what a record *could* carry: "__u64 stx_ino; /* Inode number */",
   "__u32 stx_nlink; /* Number of hard links */", "struct statx_timestamp
   stx_btime; /* Creation */", "__u64 stx_mnt_id; /* Mount ID */" (§ DESCRIPTION
   `struct statx`). A restore consumes the path; these identify the item only
   if the operator decides the record should.

**What is fixed, and what stays the operator's design.** Fixed: a restorable
record carries the original path (1–3). Not fixed by any source here: the field
list beyond that path, the field order, the serialisation, and the guarantee
between "the record is written" and "the payload is moved" — those remain the
operator's design. The spec's info-first / `O_EXCL` order (5) is the reference
*behaviour* a design should be measured against, not a commitment souji has
made.

**`gio trash` is the reference behaviour, not necessarily souji's mechanism.**
Nothing here says souji should shell out to `gio`. It is cited for two
properties a recoverable move must have: a listing that returns the original
location, and a restore that consumes it.

## What this does NOT establish
- **It does not specify souji's record format**: not the field list beyond the
  original path, not the order, not the serialisation, and not the
  record-written/payload-moved atomicity. Those remain the operator's design.
- **`gio trash` is not necessarily the mechanism**, and a souji receipt is not
  a `.trashinfo`: the spec's file is a trash format, a receipt would be a
  different artefact with different fields. GIO is cited as the reference
  behaviour for the field it needs.
- **`DeletionDate` is not a retention policy.** The spec fixes the value's
  shape — "The key “DeletionDate” contains the date and time when the
  file/directory was trashed." (§ 6) — not who may empty the store, or when.
- **It does not establish which statx fields any given filesystem or kernel
  fills**, nor that a record should carry them.
- **It changes no tool and grants no move or deletion authority.** The staging
  tool change remains an operator decision
  (`trash-spec-restorable-quarantine.md:35`).

## Amendment note — which entry this amends, and which it does not
- **Amends, by addition:** the round-2 flag entry
  `quarantine-origin-record-fields-r23.md`, whose two open items are at lines
  41 and 46 of the staged package
  (`/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-origin-record-fields-r23.md`).
  That entry keeps its layout, refusal and identity-field content and its
  operator-owned-format conclusion; this entry adds only the restore-side field
  requirement it lacked. It is not replaced.
- **Why the staged path is named:** this lane has no file at
  `corpus/knowledge/quarantine-origin-record-fields-r23.md`. The path is absent
  at base `4edb25d` and at `3216c19` (`git cat-file -e` exits 128 both times)
  and has no lane history (`git log --all -- <path>` is empty). The flag is
  therefore named by its staged path, and by its lane-side form at
  `corpus/knowledge/trash-spec-restorable-quarantine.md:35`.
- **Does not replace:** `corpus/knowledge/trash-spec-restorable-quarantine.md`
  (S022 layout, write order, no-overwrite), the staged r23 entry itself, or
  `corpus/knowledge/quarantine-staging-no-copy-r23.md` (the staging primitive).
  No other corpus file is replaced or restated.

## Lane link and consequence
F4's next step is per-item origin records (trashinfo-style). This narrows it:
the record must carry the original path, and a payload whose origin exists only
in its staged name is not restorable. The format, the order and the
record↔payload guarantee stay with the operator; this entry does not grant the
staging-tool change.

## Gate

url: https://man.archlinux.org/man/gio.1.en
snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
opened: 2026-10-25

- ADMIT: "List files in the trash with their original locations." — § COMMANDS trash OPTIONS --list — snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
- ADMIT: "Restore a file from trash to its original location." — § COMMANDS trash OPTIONS --restore — snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
- ADMIT: "If the original directory doesn’t exist, it will be recreated." — § COMMANDS trash OPTIONS --restore — snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
- ADMIT: "This command removes files irreversibly. If you want a reversible way to remove files, see the trash command." — § COMMANDS remove — snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
- ADMIT: "Sends file to the “Trashcan”, if possible." — § Description — snapshot: census/round-22/attempt2/sources/gtk-filetrash.txt
- ADMIT: "This is similar to deleting it, but the user can recover it before emptying the trashcan." — § Description — snapshot: census/round-22/attempt2/sources/gtk-filetrash.txt
- ADMIT: "The key “Path” contains the original location of the file/directory" — § 6 Contents of a trash directory — snapshot: census/round-22/attempt2/sources/freedesktop-trash.txt
- ADMIT: "The key “DeletionDate” contains the date and time when the file/directory was trashed." — § 6 Contents of a trash directory — snapshot: census/round-22/attempt2/sources/freedesktop-trash.txt
- ADMIT: "the implementation MUST create the corresponding file in $trash/info first" — § 6 Contents of a trash directory — snapshot: census/round-22/attempt2/sources/freedesktop-trash.txt
- ADMIT: "On Unix-line systems this is done by generating a filename, and then opening with O_EXCL." — § 6 Contents of a trash directory — snapshot: census/round-22/attempt2/sources/freedesktop-trash.txt
- ADMIT: "If that succeeds the creation was atomic (at least on the same machine)" — § 6 Contents of a trash directory — snapshot: census/round-22/attempt2/sources/freedesktop-trash.txt
- ADMIT: "A filename in the $trash/files directory MUST NEVER be used to recover the original filename" — § 6 Contents of a trash directory, Important — snapshot: census/round-22/attempt2/sources/freedesktop-trash.txt
- ADMIT: "__u64 stx_ino; /* Inode number */" — § DESCRIPTION struct statx — snapshot: census/round-22/attempt2/sources/man7-statx.2.txt
- ADMIT: "__u32 stx_nlink; /* Number of hard links */" — § DESCRIPTION struct statx — snapshot: census/round-22/attempt2/sources/man7-statx.2.txt
- ADMIT: "struct statx_timestamp stx_btime; /* Creation */" — § DESCRIPTION struct statx — snapshot: census/round-22/attempt2/sources/man7-statx.2.txt
- ADMIT: "__u64 stx_mnt_id; /* Mount ID */" — § DESCRIPTION struct statx — snapshot: census/round-22/attempt2/sources/man7-statx.2.txt
- REJECT: the lane inference that the staged repo-relative path is the origin record (`tools/souji-quarantine.sh` keeps it; `trash-spec-restorable-quarantine.md:32`) — reason: § 6 Important makes the payload name unusable for recovery, so a path-encoded origin is not restorable and the record must be written — flip: write the original path into a per-item record first, and present a payload without a record as the spec's emergency case rather than reconstructing a path from the staged name.
````

## Findings (bounded)

- **F1 (executed) — the target path is already committed.** The r24 entry
  exists at HEAD `3216c19` (introduced `a211e4d`, today 03:42:51) and registry
  rows `S112`–`S114` (`corpus/SOURCES.md:132-134`) point at it. The draft is
  therefore pre-adoption; land it only by substituting the placeholders with
  `S115`–`S117` (next free id `S115`) plus the already-present `S022`, then
  re-running `tools/souji-gate-check.py`. Landing it verbatim would overwrite
  committed bytes while three registry rows cite the path.
- **F2 (executed) — the r23 path is absent, and the committed entry now says so
  without a receipt.** `corpus/knowledge/quarantine-origin-record-fields-r23.md`
  does not exist at base `4edb25d`, at HEAD, or anywhere in lane history (`git
  cat-file -e` exit 128 twice; `git log --all --` empty). The committed entry
  qualifies this at `:48-51` (the campaign package file is "not adopted in this
  lane, so it has no lane path"); the draft keeps that qualification and adds
  the executable receipt (both `cat-file -e` calls and the empty `--all`
  history) instead of asserting it. Note the file changed under this seat: the
  pre-`a211e4d` bytes read at 03:36 named the lane path without the
  qualification; the committed bytes read at 03:50 do qualify it.
- **F3 (executed, tool read) — placeholder blindness in the gate tool.**
  `tools/souji-gate-check.py:39` is
  `SOURCE_RE = re.compile(r"^source:\s*(S\d{3,})", re.M)`, so `S-NEW-<slug>`
  lines are invisible to check 5: the draft's cited set is `["S022"]` only.
  The tool cannot detect an unregistered new source behind a placeholder, so
  adoption must replace placeholders *before* the gate run, and a green gate on
  a placeholder draft is not evidence that the sources are registered.
- **F4 (executed) — quote fidelity.** All 16 Gate spans are present verbatim
  (whitespace-collapsed) in the four snapshots and all are ≤18 words (limit
  25). Version claims used in the draft are in the snapshots themselves
  (`arch-gio.1.txt:618-622`, `freedesktop-trash.txt:102`). Live URLs were not
  re-fetched by this seat; snapshot bytes carry the quotes.
- **F5 (executed) — sources for placeholders.** The three new documents are the
  gio(1) man page, the GIO `File.trash` method reference, and `statx(2)`; the
  Trash spec is cited as the existing `S022` rather than adopted a second time,
  per the adopted-row rule.

- **F6 (executed comparison, judgment flagged for main) — one deliberate
  divergence from the committed entry.** The committed entry's Lane link turns
  the record-first ordering into an obligation ("the staging tool must write
  the record first and must refuse to move the payload if the record cannot be
  written", `:56-58`), while the source reserves order and atomicity for the
  operator. The draft keeps ordering as reference behaviour plus the operator's
  design and states the consequence as a property (a payload whose origin is
  only in its staged name is not restorable). Both readings are defensible: the
  obligation follows from restorability, but it is a design commitment the
  source does not make. Reported as a divergence, not as a defect.

## Out of scope / not done
- No corpus file created or edited; no `git`/`jj` writes; no registry edit; no
  tool install; no service restart; no deletion authority created.
- The committed gate tool was **not** run against a file for this draft (no
  file was created). The draft was validated in-process against the same
  regexes and against the snapshot bytes (E3); a real gate run is the landing
  step, after id substitution.
- Nothing was fetched from the network by this seat; nothing outside this
  report and `.../w1/evidence/DraftEntryOrigin.md` was written.

Report: .ufo/waves/round-22/attempt2/w1/DraftEntryOrigin.md
