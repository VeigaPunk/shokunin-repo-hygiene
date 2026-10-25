# DraftGates — Gate blocks for the two adopted knowledge entries (C2, restorable-quarantine staging)

Item: L1Souji22.DraftGates · round 22, attempt 2 (hyaku) · lane `souji`
Drafted: 2026-10-25 · base revision `4edb25dfe262515d0da63224bbba71e02e36cba5` (as frozen in
`.ufo/waves/round-22/attempt2/preregistration.txt`; this seat read it, did not re-derive it)
Targets (draft only — no corpus file was written or edited by this seat):

- `corpus/knowledge/quarantine-staging-no-copy-r23.md` (no-clobber rename primitive)
- `corpus/knowledge/quarantine-origin-record-fields-r24.md` (per-item origin record, restore side)

## 1. Provenance used

Quotes were taken only from the snapshot-seat artifacts under this directory
(`.ufo/waves/round-22/attempt2/w1/evidence/`). Each Gate names the committed census path because
that is the file the frozen checker (`tools/souji-gate-check.py`, `snapshot_dir`
`census/round-22/attempt2/sources`) opens.

| evidence file | evidence sha256 | census file | census sha256 | relation |
|---|---|---|---|---|
| `snap-rename2.txt` (15799 B) | `88cba52e7f5ee81985c34a33a3d4112ce0fecd377da5d0665ca7adb76c9631c4` | `man7-rename.2.txt` (12570 B) | `74c30ae25e76818ab25d9da03a12247f94eceb92be2e1d6c46c70d868b67bbaf` | bytes differ (different stripper); every quoted span equal after whitespace collapse |
| `snap-mv1.txt` (4610 B) | `18dc9c2185fbf2b8839e780b2a9a88fdf392ffeff311785086c807a5aa4e6687` | `man7-mv.1.txt` (4813 B) | `2fd2b0a7c3fd04021352778016a64db91ade9ba7ab75b7873d0abb36f298b677` | bytes differ; quoted spans equal after whitespace collapse |
| `snap-gio1.txt` (12125 B) | `cc4af34906f691370d4a1ea51ceae378b697a3673001a5150e0bb1543dd56f68` | `arch-gio.1.txt` (12626 B) | `546462a5aa6769a86d7a634434088a874f06c7725b0c3ec0600ac81b5031a12d` | bytes differ; quoted spans equal after whitespace collapse |
| `snap-trashspec.txt` (24788 B) | `aa21fdcbc8f7226e1e05cac5ab89818abb0ad4b9dd9743a8f42b231a99b99511` | `freedesktop-trash.txt` (25138 B) | `024ddcbfc8f5fb5fa57da2ae8366ab891ab620f04c4e02ef124a3fe4063b9c99` | bytes differ; quoted spans equal after whitespace collapse |
| `snap-statx2.txt` (19724 B) | `ca14c31f6608b6e91ba019aa434ad7d49c90ad8bb6411d4421a744b1f2a05f1b` | `man7-statx.2.txt` (19343 B) | `9fb42e56248f95dec409744fb93102e7bc477c701fcadfac4093eb8528da965b` | bytes differ; quoted spans equal after whitespace collapse |
| `snap-filetrash.txt` (4140 B) | `23fb07ce8ca4946f49a78b7a3d00f7bcba45ec246219b5d47432b6d6d2a86c5e` | `gtk-filetrash.txt` (4904 B) | `8bed4dac2aacf3de7b58fcc3ce5e3d6baf6a98841700b59c3ad152c3fd8673c9` | bytes differ; quoted spans equal after whitespace collapse |

Raw captures are byte-identical in both locations (measured with `sha256sum`):

- `snap-rename2.raw` = `man7-rename.2.raw` = `8772946a809a0db54f4854f200908f10bee758ea452e8df5efd955bc3b8e6e57`
- `snap-mv1.raw` = `man7-mv.1.raw` = `d20b49ad254a0c791f788920218f60da657a2f8ef765ba681a0f63fd2053ed0c`
- `snap-gio1.raw` = `arch-gio.1.raw` = `3e7876d838c665f9afbd4e36c4fb7c022e946a44fccba7789b230ccb57419e84`
- `snap-trashspec.raw` = `freedesktop-trash.raw` = `353442d2ed3db0ff0c59632796214df56ba24973621f2e7899711921ee454ae4`
- `snap-statx2.raw` = `man7-statx.2.raw` = `2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e`
- `snap-filetrash.raw` = `gtk-filetrash.raw` = `a5af1920b16444e0a03d30fcf77de0389533bcedb7243175c915b34c38c21cf3`
- `vendor-noreplace-probe.out` = `1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5` (vendor row, not quoted below)

Snapshot seat reports present at draft time: `SnapRename2.md`, `SnapMv1.md`, `SnapGio1.md`,
`SnapStatx2.md`, `SnapTrashSpec.md`, `SnapFileTrash.md`, plus `SnapManifest.md`.

## 2. Verification method (executed)

The checker's own `squash()` (`re.sub(r"\s+", " ", t).strip()`) was imported from
`tools/souji-gate-check.py` and applied to the whole snapshot body; each candidate span was tested
for substring presence in both the evidence `.txt` and the census `.txt`. Word counts are
`squash(q).split()` lengths, i.e. the number the checker compares against 25.

| # | span (abridged) | words | evidence file | census file | result |
|---|---|---|---|---|---|
| 1 | RENAME_NOREPLACE … newpath already exists. | 14 | snap-rename2.txt | man7-rename.2.txt | BOTH |
| 2 | RENAME_NOREPLACE requires support from the underlying filesystem. | 7 | snap-rename2.txt | man7-rename.2.txt | BOTH |
| 3 | do not copy if renaming fails | 6 | snap-mv1.txt | man7-mv.1.txt | BOTH |
| 4 | List files in the trash with their original locations. | 9 | snap-gio1.txt | arch-gio.1.txt | BOTH |
| 5 | Restore a file from trash to its original location. … | 17 | snap-gio1.txt | arch-gio.1.txt | BOTH |
| 6 | The key “Path” contains the original location … | 10 | snap-trashspec.txt | freedesktop-trash.txt | BOTH |
| 7 | The key “DeletionDate” contains the date and time … | 13 | snap-trashspec.txt | freedesktop-trash.txt | BOTH |
| 8 | Sends file to the “Trashcan”, if possible. … | 23 | snap-filetrash.txt | gtk-filetrash.txt | BOTH |
| 9 | __u64 stx_ino; /* Inode number */ | 6 | snap-statx2.txt | man7-statx.2.txt | BOTH |

## 3. Gate blocks (insertion-ready)

### A — `corpus/knowledge/quarantine-staging-no-copy-r23.md`

```
## Gate

url: https://man7.org/linux/man-pages/man2/rename.2.html
snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
opened: 2026-10-25

- ADMIT: "RENAME_NOREPLACE Don't overwrite newpath of the rename. Return an error if newpath already exists." — § DESCRIPTION flags — reason: verbatim in the named snapshot and it states the refusal (error instead of overwrite) that the staging step needs — snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
- ADMIT: "RENAME_NOREPLACE requires support from the underlying filesystem." — § DESCRIPTION flags — reason: verbatim in the named snapshot and it makes per-device support a precondition, not an assumption — snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
- ADMIT: "do not copy if renaming fails" — § OPTIONS --no-copy — reason: verbatim in the named snapshot; without it mv may fall back to copy+remove across devices — snapshot: census/round-22/attempt2/sources/man7-mv.1.txt
- REJECT: register-slice row S123 (souji round2, class payload-absent) — the row offers a man-page SYNOPSIS sentence as evidence of what a local trigger probe printed; reason: the payload r23-trigger-prune.out contains 0 occurrences of the span and its own bytes are only id=... verdict=PASS lines, while the span sits in git-worktree(1) SYNOPSIS line 12, so the citation names the wrong source class and cannot support a claim about probe output — flip: re-cite the span against git-worktree(1) and cite the probe only for its PASS lines.
```

### B — `corpus/knowledge/quarantine-origin-record-fields-r24.md`

```
## Gate

url: https://man.archlinux.org/man/gio.1.en
snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
opened: 2026-10-25

- ADMIT: "List files in the trash with their original locations." — § COMMANDS trash --list — reason: verbatim in the named snapshot; the listing field is the original location the restore consumes — snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
- ADMIT: "Restore a file from trash to its original location. A URI beginning with trash:// is expected here." — § COMMANDS trash --restore — reason: verbatim in the named snapshot; restore is defined by the original location, so the record cannot omit it — snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
- ADMIT: "The key “Path” contains the original location of the file/directory" — § 6 Contents of a trash directory, key/value list — reason: verbatim in the named snapshot; the spec makes the original path a required record key — snapshot: census/round-22/attempt2/sources/freedesktop-trash.txt
- ADMIT: "The key “DeletionDate” contains the date and time when the file/directory was trashed." — § 6 Contents of a trash directory, key/value list — reason: verbatim in the named snapshot; it is the second required key and it is a timestamp, not a retention policy — snapshot: census/round-22/attempt2/sources/freedesktop-trash.txt
- ADMIT: "Sends file to the “Trashcan”, if possible. This is similar to deleting it, but the user can recover it before emptying the trashcan." — § Description — reason: verbatim in the named snapshot; it is the documented recoverability the receipt-gated quarantine relies on — snapshot: census/round-22/attempt2/sources/gtk-filetrash.txt
- ADMIT: "__u64 stx_ino; /* Inode number */" — § DESCRIPTION struct statx — reason: verbatim in the named snapshot; identity fields are exposed directly, not parsed from text — snapshot: census/round-22/attempt2/sources/man7-statx.2.txt
- REJECT: register-slice row S123 (souji round2, class payload-absent) — the row offers a man-page SYNOPSIS sentence as evidence of what a local trigger probe printed; reason: the payload r23-trigger-prune.out contains 0 occurrences of the span and its own bytes are only id=... verdict=PASS lines, while the span sits in git-worktree(1) SYNOPSIS line 12, so the citation names the wrong source class and cannot support a claim about probe output — flip: re-cite the span against git-worktree(1) and cite the probe only for its PASS lines.
```

## 4. Parser validation (executed, read-only)

The frozen module was imported with `importlib` and its own `check_entry()` was called on the two
draft blocks (fixture frontmatter `source: S109/S110/S111` and `source: S112/S113/S114/S022`,
`verified-at: 2026-10-25`) written to `/var/tmp/draftgate-r23.md` and `/var/tmp/draftgate-r24b.md`
— outside the lane tree; these are scratch, not evidence:

```
check_entry(root, "/var/tmp/draftgate-r23.md",  "2026-10-25", "census/round-22/attempt2/sources") -> (True, [])
check_entry(root, "/var/tmp/draftgate-r24b.md", "2026-10-25", "census/round-22/attempt2/sources") -> (True, [])
```

For contrast, the same checker on the currently landed corpus entries printed:

```
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
exit=0
```

## 5. REJECT grounding (executed)

- Register row (`/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md:172`):
  `| souji | round2 | S123 | payload-absent | lanes/souji/round2/evidence/r23-trigger-prune.out | git worktree prune [-n] [-v] [--expire <expire>] | cited source, companion URLs and local artifacts were all checked; the quote is in none of them |`
- Payload `/home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-trigger-prune.out`
  (1043 B) reads as `git_version=…`, eight `id=SOUJI-R23-TRIGGER-… verdict=PASS` lines, a
  `SUMMARY` PASS line and provenance comments. Its only `prune` occurrence is the provenance
  string `produced by fixtures/r23-trigger-prune.sh`; no SYNOPSIS text.
- `grep -c -F 'git worktree prune [-n] [-v] [--expire <expire>]' <payload>` → `0`.
- The span is real but belongs to the manual: `MANWIDTH=80 man -P cat git-worktree | sed -n '12p'`
  → `     git worktree prune [-n] [-v] [--expire <expire>]` under `SYNOPSIS` (line 6).
- Lane verdict already recorded: `S123  refused  quote absent from cited fixture r23-trigger-prune.sh and its .out (0 matches); synopsis is git-worktree(1):12` (`census/round-22/attempt2/slice-verdicts.tsv`).

So the defect class is a wrong-source citation (a man-page sentence offered as an observation of a
local probe), not fabrication and not a mis-transcription. Both Gate blocks reject it on that
ground and name the flip.

## 6. Slot status

No `PENDING-SNAPSHOT` slot: all six snapshot `.txt` files cited above existed when the blocks were
finalised (`snap-gio1.txt` was absent at the 03:45 listing and landed at 03:46; every quote was
re-verified after it appeared).
