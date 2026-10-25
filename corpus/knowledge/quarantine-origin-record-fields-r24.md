source: S112 — https://man.archlinux.org/man/gio.1.en (glib2 2.90.1)
source: S113 — https://docs.gtk.org/gio/method.File.trash.html (GLib GIO)
source: S114 — https://man7.org/linux/man-pages/man2/statx.2.html
source: S022 — https://specifications.freedesktop.org/trash/latest/ (Trash spec layout, already in this registry)
verified-at: 2026-10-25 — glib2 2.90.1 gio(1); GIO method reference; Linux man-pages 6.19; all three snapshots opened this round
recheck: 180d — re-open census/round-22/attempt2/sources/{arch-gio.1,gtk-filetrash,freedesktop-trash,man7-statx.2}.txt
ground: F4 — restorable quarantine (the read side of a per-item origin record)

# A per-item origin record must carry the original path, because that is what restore consumes

## Claim (F4, sourced — amends the round-2 record entries)
The lane already holds the trash *layout* (S022, § 6 Contents of a trash
directory: `info/<name>.trashinfo` with `Path` and `DeletionDate`, written
before the payload moves). The *write contract* is taken from S113, which this
round mints: the trash call is documented recoverable and can refuse with
`G_IO_ERROR_NOT_SUPPORTED` instead of deleting. What was missing is the
**read side**: which field a restore actually consumes.

1. **The original location is the load-bearing field.** `gio trash --list`
   "List files in the trash with their original locations." and
   `gio trash --restore` "Restore a file from trash to its original location."
   (S112, § COMMANDS `trash`). The record is unusable without the original
   path, and the spec makes it a required key: "The key “Path” contains the
   original location of the file/directory" (S022). The restore path recreates
   a missing original directory, so the record does not need the directory to
   still exist.
2. **The irreversible alternative is named, which is why a receipt-gated
   quarantine is possible at all.** The same manual documents `gio remove` as
   removing files irreversibly and points at `trash` for a reversible one
   (S112). A documented reversible primitive is what makes "quarantine before
   delete" enforceable rather than advisory.
3. **The record's identity fields are available, not invented.** `statx`
   exposes `stx_ino`, `stx_nlink`, `stx_btime` and `stx_mnt_id` as distinct
   fields (S114, § DESCRIPTION struct statx), so a per-item record can carry
   inode, link count, creation time and mount id without shelling out to a
   text parser.

## What this does NOT establish
- **This still does not specify souji's record format.** It fixes what any
  restorable record must carry (the original path) and what the reference
  implementations do with it. The field list, its order, and the atomicity
  guarantee between "the record is written" and "the payload is moved" remain
  the operator's design.
- **`gio trash` is not necessarily the mechanism souji would use.** It is the
  reference *behaviour* of a recoverable move, cited for the field it needs.
- **`DeletionDate` is not a retention policy.** S022 fixes its format
  (`YYYY-MM-DDThh:mm:ss`), not who may empty the trash or when.
- The campaign's r23 record entry (package file
  `merge/souji/knowledge/corpus/knowledge/quarantine-origin-record-fields-r23.md`,
  not adopted in this lane, so it has no lane path) is **not replaced** by this
  one; this entry adds the restore-side requirement that the r23 entry lacked.
  It also does not replace S022's layout entry.

## Lane link and consequence
F4's next step is "per-item origin records (trashinfo-style)". This entry turns
that from a format question into a field requirement: a quarantine item without
its original path is not restorable, so the staging tool must write the record
first and must refuse to move the payload if the record cannot be written.

## Gate

url: https://man.archlinux.org/man/gio.1.en
snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
opened: 2026-10-25

- ADMIT: "List files in the trash with their original locations." — § COMMANDS trash --list — snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
- ADMIT: "Restore a file from trash to its original location. A URI beginning with trash:// is expected here." — § COMMANDS trash --restore — snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
- ADMIT: "Sends file to the “Trashcan”, if possible. This is similar to deleting it, but the user can recover it before emptying the trashcan." — § Description — snapshot: census/round-22/attempt2/sources/gtk-filetrash.txt
- ADMIT: "The key “Path” contains the original location of the file/directory" — § 6 Contents of a trash directory, key/value list — snapshot: census/round-22/attempt2/sources/freedesktop-trash.txt
- ADMIT: "The key “DeletionDate” contains the date and time when the file/directory was trashed." — § 6 Contents of a trash directory, key/value list — snapshot: census/round-22/attempt2/sources/freedesktop-trash.txt
- ADMIT: "__u64 stx_ino; /* Inode number */" — § DESCRIPTION struct statx — snapshot: census/round-22/attempt2/sources/man7-statx.2.txt
- REJECT: staged entry quarantine-staging-no-copy-r24 (same primitive, second device list, no new field or refusal semantics) — reason: duplicate ground; the r23 entry already recorded the five-device measurement and this package adds an eighth-mount list without a new consequence for the lane; flip: a measurement on a filesystem or mount namespace the r23 entry did not cover, plus a consequence the staging tool would change.
