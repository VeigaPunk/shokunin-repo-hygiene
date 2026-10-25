STATUS: PASS

# DraftSourcesRows — SOURCES rows for the six sources the two adopted entries cite

Seat `L1Souji22.DraftSourcesRows` (leaf, no subagent dispatch). Lane: souji, round 22,
attempt 2 (hyaku), wave w1. Base lane revision `4edb25dfe262515d0da63224bbba71e02e36cba5`;
lane HEAD when this draft was written `2a130b4`. Nothing was edited: no registry file, no
git/jj write, no campaign tool run in `/home/vgpnk/Projects/shokuknow`, no cleanup, no
deletion authority. Full command/output transcript:
`.ufo/waves/round-22/attempt2/w1/evidence/DraftSourcesRows.txt`.

## 1. The draft block (append-only; header + six rows, nothing else)

Column order read from `corpus/SOURCES.md:19`:
`id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S-NEW-noreplace-probe | souji round-2 RENAME_NOREPLACE probe, vendored — lanes/souji/round2/evidence/noreplace_probe.py, byte-exact copy at census/round-22/attempt2/sources/vendor-noreplace-probe.out (sha256 1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5) | own-work | A | whether renameat2 RENAME_NOREPLACE is implemented on the devices this fleet's repositories live on — this host's five probed directories only, not the upstream support schedule | the five device lines of the vendored probe output (/var/tmp, /home/vgpnk/Projects/shokunin, /home/vgpnk/Projects/shokuknow on btrfs; /dev/shm on tmpfs; /tmp on xfs) plus the kernel line 7.2.11-arch1-1; the file carries no date line, so 2026-10-23 is the round-2 campaign's provenance and not snapshot text | on every one of the five probed devices NOREPLACE_existing reads -1(EEXIST) while plain_overwrite reads 0(ok), so the no-clobber refusal held where it was measured and a plain rename overwrote the existing target | mined | 2026-10-25 | 90d | corpus/knowledge/quarantine-staging-no-copy-r23.md |
| S-NEW-rename-noreplace | rename(2), Linux man-pages 6.19 (2026-02-08) — https://man7.org/linux/man-pages/man2/rename.2.html | docs | A | atomic no-overwrite and atomic-swap primitives for quarantine staging, with the per-filesystem support schedule; not a receipt format and not this host's devices (the vendored probe row holds those) | § DESCRIPTION flags RENAME_EXCHANGE and RENAME_NOREPLACE, the incompatibility sentence and the filesystem list; snapshot census/round-22/attempt2/sources/man7-rename.2.txt lines 143-167, snapshot footer Linux man-pages 6.19 2026-02-08 | RENAME_NOREPLACE returns an error instead of overwriting an existing newpath, cannot be employed together with RENAME_EXCHANGE, and requires filesystem support (ext4 3.15; btrfs, tmpfs and cifs 3.17; xfs 4.0; many more in 4.9) | mined | 2026-10-25 | 90d | corpus/knowledge/quarantine-staging-no-copy-r23.md |
| S-NEW-mv-no-copy | mv(1), GNU coreutils — https://man7.org/linux/man-pages/man1/mv.1.html | docs | A | the mv --no-copy and mv --exchange staging verbs only, not the across-filesystem copy-then-remove behaviour S025 holds and not this host's devices | § OPTIONS --exchange and --no-copy; snapshot census/round-22/attempt2/sources/man7-mv.1.txt lines 75-76 and 90-91, snapshot footer GNU coreutils 9.11 April 2026 | --no-copy means do not copy if renaming fails, so the failure is reported rather than satisfied by copying; --exchange exchanges source and destination | mined | 2026-10-25 | 90d | corpus/knowledge/quarantine-staging-no-copy-r23.md |
| S-NEW-gio-trash-cli | gio(1), GIO commandline tool (glib2 2.90.1-1, Arch core) — https://man.archlinux.org/man/gio.1.en | docs | A | the read side of a per-item origin record — how a trash item's original location is listed and restored, plus the named irreversible alternative; not the on-disk layout (S022) and not the API contract (S-NEW-gio-file-trash) | § COMMANDS trash --list and --restore, and § COMMANDS remove; snapshot census/round-22/attempt2/sources/arch-gio.1.txt lines 443-444 and 566-572, Arch package core/glib2 version 2.90.1-1 | gio trash --list lists files in the trash with their original locations and --restore restores a file from trash to its original location, recreating the original directory when it does not exist; gio remove removes files irreversibly and points at trash for the reversible way | mined | 2026-10-25 | 180d | corpus/knowledge/quarantine-origin-record-fields-r24.md |
| S-NEW-gio-file-trash | GLib GIO, g_file_trash() method reference — https://docs.gtk.org/gio/method.File.trash.html | docs | A | the contract of the trash call a per-item origin record would be produced by — recoverability and the unsupported-mount refusal; not the on-disk layout (S022) and not the CLI read side (S-NEW-gio-trash-cli) | § Description, the recover-it-before-emptying sentence and the system-mount G_IO_ERROR_NOT_SUPPORTED paragraph; snapshot census/round-22/attempt2/sources/gtk-filetrash.txt lines 405-409, page header Library Version 2.91.0 | the call is documented recoverable — the user can recover the file before emptying the trashcan — and trashing is disabled for system mounts by default, so the call can return G_IO_ERROR_NOT_SUPPORTED | mined | 2026-10-25 | 180d | corpus/knowledge/quarantine-origin-record-fields-r24.md |
| S-NEW-statx-identity | statx(2), Linux man-pages 6.19 (2026-02-08) — https://man7.org/linux/man-pages/man2/statx.2.html | docs | A | the identity and origin fields a per-item record can carry (inode, link count, creation time, mount id) and the constants that request them; not a duplicate-detection algorithm | § DESCRIPTION struct statx fields stx_ino, stx_nlink, stx_btime, stx_mnt_id; § CONSTANTS STATX_BTIME and STATX_MNT_ID_UNIQUE; snapshot census/round-22/attempt2/sources/man7-statx.2.txt lines 79-106 and 237-243, snapshot footer Linux man-pages 6.19 2026-02-08 | stx_ino is the inode number, stx_nlink the number of hard links, stx_btime the creation timestamp and stx_mnt_id the mount id, whose unique form is requested with STATX_MNT_ID_UNIQUE and is available since Linux 6.8 | mined | 2026-10-25 | 180d | corpus/knowledge/quarantine-origin-record-fields-r24.md |

**Document→id map (the preregistration's "re-pointed by DOCUMENT" rule applied to the
staged package's campaign ids).** The adopted entries already cite *lane* ids, so the
staged candidate numbers are a mapping, not text to copy:

| staged | document | lane id (already landed) |
|---|---|---|
| S124 | round-2 noreplace probe output, vendored | S109 |
| S116 | rename(2), man-pages 6.19 | S110 |
| S115 | mv(1), GNU coreutils | S111 |
| S137 | gio(1), glib2 2.90.1 | S112 |
| S126 | GLib GIO `g_file_trash()` | S113 |
| S117 | statx(2), man-pages 6.19 | S114 |
| — | FreeDesktop Trash Spec (**pre-existing** S022) | S022, not duplicated |

## 2. Evidence actually executed

Schema and allowed sets (read from the lane registry, not assumed):

```
$ grep -n '^| id | source' corpus/SOURCES.md
19:| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
$ awk -F'|' '/^\| S[0-9]{3} /{gsub(/^ +| +$/,"",$9); print $9}' corpus/SOURCES.md | sort | uniq -c
     91 mined
     15 queued
      8 rejected
$ awk -F'|' '/^\| S[0-9]{3} /{gsub(/^ +| +$/,"",$11); print $11}' corpus/SOURCES.md | sort | uniq -c
      6 180d / 7 365d / 5 90d / 1 on-change / 1 on-correction / 94 on-release
```

Quote re-derivation, one command per snapshot, all six observed in this session:

```
$ grep -n -E 'no-copy|exchange' census/round-22/attempt2/sources/man7-mv.1.txt
75: --exchange
76: exchange source and destination
90: --no-copy
91: do not copy if renaming fails
$ grep -n 'coreutils [0-9]' man7-mv.1.raw   -> 202:GNU coreutils 9.11  April 2026  MV(1)

$ sed -n '140,167p' .../man7-rename.2.txt
143 RENAME_EXCHANGE / 148 RENAME_NOREPLACE
149-150 "Don't overwrite newpath of the rename. Return an error if newpath already exists."
152-153 "RENAME_NOREPLACE can't be employed together with RENAME_EXCHANGE."
155-167 filesystem list: ext4 3.15; btrfs, tmpfs and cifs 3.17; xfs 4.0; many more in 4.9
$ grep -n 'man-pages [0-9]' man7-rename.2.raw -> 399:Linux man-pages 6.19 2026-02-08 rename(2)
$ grep -c 'renameat2' .../man7-rename.2.txt -> 9

$ grep -n -E 'stx_ino|stx_nlink|stx_btime|stx_mnt_id' .../man7-statx.2.txt
79 nlink "Number of hard links" / 83 ino "Inode number" / 92 btime "Creation" / 106 mnt_id "Mount ID"
237 STATX_BTIME / 240 STATX_MNT_ID (since Linux 5.8) / 243 STATX_MNT_ID_UNIQUE (since Linux 6.8)

$ sed -n '440,450p;566,572p' .../arch-gio.1.txt
443-444 "This command removes files irreversibly. ... see the trash command."
567-568 "List files in the trash with their original locations."
570-572 "Restore a file from trash to its original location. ... If the original
        directory doesn't exist, it will be recreated."
$ grep -n -E '<dd>2\.' arch-gio.1.raw -> 604:<dd>2.90.1-1</dd>

$ sed -n '405,409p' .../gtk-filetrash.txt
405-406 "Sends file to the “Trashcan”, if possible. This is similar to deleting it,
        but the user can recover it before emptying the trashcan."
407-409 "Trashing is disabled for system mounts by default ..., so this call can
        return the G_IO_ERROR_NOT_SUPPORTED error."
$ grep -n -E 'API Version|Library Version' .../gtk-filetrash.txt -> 59:2.0 / 62:2.91.0

$ cat .../vendor-noreplace-probe.out   (6 lines)
5 device lines: btrfs x3, tmpfs x1, xfs x1 — each NOREPLACE_existing=-1(EEXIST), plain_overwrite=0(ok)
+ "kernel: 7.2.11-arch1-1"     and NO date line (grep '2026' -> no match)
$ sha256sum .../vendor-noreplace-probe.out
1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5
```

Base-revision / free-id proof (read-only git):

```
$ git show 4edb25d:corpus/SOURCES.md | grep -oE '^\| S[0-9]{3} ' | tail -3
| S106 / | S107 / | S108
$ git show 4edb25d:corpus/SOURCES.md | grep -c '^| S109 '   -> 0
$ git log --oneline -S'| S109 |' -- corpus/SOURCES.md | head -3
a211e4d round-22: declared-evidence audit tool, assimilation entries and gate checker
```

Conformance of the block above as written into the evidence file (11 columns ⇒ `NF == 13`
when split on the separator; an embedded literal pipe would raise it):

```
$ awk -F'|' '/^\| S-NEW-/{n=NF; bad=0; for(i=2;i<NF;i++){c=$i; gsub(/^ +| +$/,"",c); if(c=="") bad=1} printf "%s fields=%d empty=%d\n", $2, NF, bad}' DraftSourcesRows.txt
 S-NEW-noreplace-probe  fields=13 empty=0
 S-NEW-rename-noreplace  fields=13 empty=0
 S-NEW-mv-no-copy  fields=13 empty=0
 S-NEW-gio-trash-cli  fields=13 empty=0
 S-NEW-gio-file-trash  fields=13 empty=0
 S-NEW-statx-identity  fields=13 empty=0
$ awk '/^\| S-NEW-/{if(index($0,"\\|")>0) print "ESCAPED-PIPE: "$2}' DraftSourcesRows.txt
(no output)
$ awk -F'|' '/^\| S-NEW-/{for(i=2;i<=12;i++)gsub(/^ +| +$/,"",$i); printf "%s | %s | %s | %s\n",$2,$9,$10,$11}' DraftSourcesRows.txt
S-NEW-noreplace-probe | mined | 2026-10-25 | 90d
S-NEW-rename-noreplace | mined | 2026-10-25 | 90d
S-NEW-mv-no-copy | mined | 2026-10-25 | 90d
S-NEW-gio-trash-cli | mined | 2026-10-25 | 180d
S-NEW-gio-file-trash | mined | 2026-10-25 | 180d
S-NEW-statx-identity | mined | 2026-10-25 | 180d
```

No cell is empty, `status` is in the registry's `{mined, queued, rejected}`, `opened` is
the ISO date `2026-10-25` on every row, `recheck` is `NNd` on every row.

## 3. Normalization decisions (each one quoted; nothing silently changed)

- **N1 — placeholder ids.** The item requires `S-NEW-<slug>`; no numeric id is asserted by
  this draft. Slugs are per document: `noreplace-probe`, `rename-noreplace`, `mv-no-copy`,
  `gio-trash-cli`, `gio-file-trash`, `statx-identity`. The numeric landing (`S109–S114`) is
  recorded only as a mapping (§1), not as a claim that the draft wrote it.
- **N2 — unverifiable digest dropped.** Staged S124 carried `probe sha256 11df88f1…` for
  `lanes/souji/round2/evidence/noreplace_probe.py`. That script is **not in this lane** (only
  the vendored output is), so the digest cannot be re-derived here and is not a record a
  reader could check. Kept instead: the vendored output's own digest, **measured** by me
  (`1634d206…8bb5`).
- **N3 — `own-work` source names the in-lane bytes.** Rewritten to name both the campaign
  origin and the byte-exact in-lane copy, so the row's evidence pointer resolves inside
  this lane instead of pointing into a read-only sibling repo.
- **N4 — unverifiable host claim dropped.** Staged S115 anchor ended "host coreutils 9.12
  `man mv` lists the same two options". That is a host-man observation, not snapshot text,
  and I did not re-run `man mv`. Replaced by the snapshot's own footer locator
  ("GNU coreutils 9.11 April 2026"), which the `.raw` shows at line 202.
- **N5 — `used-by` re-pointed to real paths.** The staged cells named
  `corpus/knowledge/quarantine-staging-no-copy.md` and
  `corpus/knowledge/quarantine-origin-record-fields-r23.md`. Both were checked and are
  **ABSENT** in this lane (`quarantine-staging-no-copy-r23.md` and
  `quarantine-origin-record-fields-r24.md` are the files that exist). Each row now names
  exactly the adopted entry whose frontmatter cites it. I did **not** write both entries
  into every cell: only one entry cites a given row, and a second name would be a citation
  the bytes do not support.
- **N6 — teaches completed from the page.** Staged S116 omitted "RENAME_NOREPLACE can't be
  employed together with RENAME_EXCHANGE"; restored, because the r23 entry's own
  "does NOT establish" section leans on that distinction.
- **N7 — statx precision.** "unique since Linux 6.8" is attached to `STATX_MNT_ID_UNIQUE`
  (line 243), not to the field (line 106, present since 5.8).
- **N8 — anchor de-quoted where the page uses typographic quotes.** The gtk snapshot writes
  `“Trashcan”`; the staged `"Sends file to the 'Trashcan', if possible"` would not be a
  byte-equal quote. The anchor therefore locates the sentences positionally, and the exact
  bytes stay in the entry's Gate (where all four Gate ADMIT quotes re-verified here).
- **N9 — teaches narrowed to the page's modality.** Staged "on system mounts it returns
  `G_IO_ERROR_NOT_SUPPORTED` instead of removing the file" became "trashing is disabled for
  system mounts by default, so the call **can** return `G_IO_ERROR_NOT_SUPPORTED`". The
  snapshot says "can return" and "disabled ... by default"; it never says "instead of
  removing".
- **N10 — emphasis stripped.** `**recoverable**`, `**refuse rather than delete**`,
  `**with their original locations**` removed: the registry's teaches cells are plain prose,
  and emphasis adds no fact.
- **N11 — pipes.** No cell contains a literal `|` and none contains an escaped `\|`;
  option names are plain or backticked, and no cell needed quoting. Verified mechanically
  (`NF=13` on all six, escaped-pipe scan empty).
- **N12 — recheck cadence aligned to the citing entry.** The r23 entry states "recheck: 90d —
  re-open ...{man7-rename.2,man7-mv.1}.txt and the vendored probe output"; the r24 entry
  states "recheck: 180d — re-open ...{arch-gio.1,gtk-filetrash,freedesktop-trash,
  man7-statx.2}.txt". Probe/rename/mv carry `90d`, gio/File.trash/statx carry `180d`. The
  staged `on-release — ...` was replaced because a snapshot-bound row has a calendar
  cadence, not a release trigger.
- **N13 — `opened = 2026-10-25`** on all six, matching both entries' `verified-at` and the
  snapshot directory's round.
- **N14 — kind/tier unchanged** (`docs`/A for the four pages, `own-work`/A for the probe),
  matching the lane's own precedent for these pages.
- **N15 — S022 cited, not duplicated, not edited** (`corpus/SOURCES.md:42`).

## 4. Staged rows deliberately left out, and why

The package holds **134 staged rows (S109…S242)**; exactly six are cited by the two adopted
entries. The adopted-row rule admits only cited rows, so the other 128 are not appended.
Called out explicitly because they are the *tempting* near-misses:

- **staged S125** (`statx(2)` mount-id uniqueness) — the r24 entry cites S114 for the
  identity fields; S125's narrower mount-id wording is uncited, and its unique-id caveat is
  already in S114's anchor.
- **staged S133** (round-3 `r24-renameat2-probe`, 8 paths) — a second device list; the r23
  entry reuses the round-2 vendored probe, so S133 is a duplicate ground, not a new one.
- **staged S146** (GVFS `trashitem.c` reader) and **S152** (`gio/glocalfile.c` writer) —
  on-disk record shape and write sequence; uncited, and S022 already holds the layout.
- **staged S158/S159/S173** (POSIX `O_EXCL`/`rename`/`fsync`) — record atomicity and
  durability; uncited, and the record-format decision remains the operator's.
- **staged S109–S114, S123, S130–S135, S141–S143, S147–S148, S151, S153–S155, S160–S161,
  S165–S166, S176–S177, S185, S194–S195** — git auto-maintenance, worktree-prune and
  garbage-census rows for the F1/F2 themes; a different ground.
- **staged S118, S122, S136, S138–S140, S144–S150, S156–S157, S162–S164, S167–S172,
  S174–S175, S178–S184, S186–S193, S196–S242 as staged** — duplicate-taxonomy, hosted and
  self-hosted service, locale-variant and community rows; none cited.
- **S022 is not in the package at all**; the registry's own row was cited by the r24 entry,
  so it is neither duplicated nor rewritten.

## 5. Bounded findings (executed vs source-inferred marked)

- **F1 (executed).** The six rows are **already landed**. Base `4edb25d` ends at S108;
  `S109–S114` appear at HEAD, added by `a211e4d`, for exactly these six documents. This
  draft is therefore a normalization check of that landing. An appender must reuse
  S109–S114 and must not create a second set.
- **F2 (executed).** Version skew inside the snapshot set: `gtk-filetrash.txt` declares
  **Library Version 2.91.0**, `arch-gio.1` is **glib2 2.90.1-1**, and the r24 entry's
  `verified-at` says "glib2 2.90.1 gio(1)". Harmless for the quoted sentences (checked),
  but the two snapshots are not one GLib release.
- **F3 (executed).** The vendored probe output has **no date line**; its `2026-10-23` run
  date is campaign provenance. A future Gate that quotes a date from these bytes would fail
  its own verbatim check. My row records the date as provenance, in the anchor prose.
- **F4 (executed, reported not fixed).** Divergences between the re-derived bytes and the
  already-committed rows — editing committed registry bytes is outside a draft seat:
  - `S110` teaches lists "btrfs and tmpfs 3.17" and **omits cifs**, which the snapshot names
    at line 161 ("btrfs, tmpfs, and cifs (Linux 3.17)").
  - `S111` teaches ends "..., on any filesystem"; neither the page nor the probe states
    "any filesystem" (the probe covers five directories), and the row's own scope disclaims
    the across-filesystem behaviour.
  - `S112` teaches says `--restore` "consumes exactly that location"; the page says a
    `trash://` URI is expected and that a missing original directory **is recreated**.
  - `S113` teaches says the call "returns `G_IO_ERROR_NOT_SUPPORTED` rather than deleting";
    the page says it **can** return the error and that trashing is **disabled for system
    mounts by default**.
- **X1 (executed; source-inferred consequence).** `S022`'s `used-by` names only
  `corpus/knowledge/trash-spec-restorable-quarantine.md`, although the r24 entry now cites
  S022 in its frontmatter. Extending that cell is an **edit** of an existing row, which the
  adopted-row rule does not authorize for this seat — recorded as a curation item for the
  appender.

## 6. Out of scope / not done

No registry edit, no git or jj write, no commit/fetch/push (the two git calls are `git show`
and `git log -S`), no campaign tool in `shokuknow`, no mutating cleanup, no process
signalling, no protected-namespace read, no subagent dispatch. No tool was installed or
upgraded (nothing was needed; no pacman transaction, consistent with the host-wide pause).

Artifacts:
- report — `.ufo/waves/round-22/attempt2/w1/DraftSourcesRows.md`
- evidence — `.ufo/waves/round-22/attempt2/w1/evidence/DraftSourcesRows.txt`
