## Status
STATUS: PASS — page opened this run (read tool, raw HTML, plus one curl copy for line numbers, scratch removed); all asked quotes located. Verdict on the staged entry: 3 defects to fix before landing (see Findings 8-10), rest supported.

## Evidence
- Read: `https://man7.org/linux/man-pages/man2/statx.2.html` (raw HTML, 690 lines). Line numbers below are raw-HTML lines of that fetch (`curl -sL`, 33125 bytes, sha256 `2a47fe319c5894d7d907b5ac03ced8cf64fb786bab69c12d276e90ba18359e8e`; scratch deleted; no snapshot written, per assignment).
- Cross-check command: `grep -nE 'stx_ino|stx_nlink|stx_btime|stx_mnt_id|STATX_MNT_ID|STATX_BTIME|man-pages 6.19|...' p.html` (outputs quoted below).
- Staged entry read: `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/duplicate-verdict-identity.md` (65 lines, read-only).
- Tools installed: none.

## Findings
1. **Version/date line** — footer line 587: `Linux man-pages 6.19            2026-02-08                       statx(2)`. Colophon (SEE ALSO..COLOPHON): "This page was obtained from the tarball man-pages-6.19.tar.gz fetched from ... on 2026-09-09." HTML rendering footer: "HTML rendering created 2026-09-09". HISTORY: "Linux 4.11, glibc 2.28." STANDARDS: "Linux."
2. **stx_ino** — DESCRIPTION, struct (l.97): `__u64 stx_ino;         /* Inode number */`. DESCRIPTION field list (l.334): "stx_ino: The inode number of the file."
3. **stx_nlink** — DESCRIPTION, struct (l.93): `__u32 stx_nlink;       /* Number of hard links */`. Field list (l.322): "stx_nlink: The number of hard links on a file."
4. **stx_btime** — DESCRIPTION, struct (l.106): `struct statx_timestamp stx_btime;  /* Creation */`. Field list (l.355): "stx_btime: The file's creation timestamp." Mask list (l.251): "STATX_BTIME            Want stx_btime". No "since Linux" attached to btime/STATX_BTIME.
5. **stx_mnt_id** — DESCRIPTION, struct (l.120): `__u64 stx_mnt_id;      /* Mount ID */`. Field list (l.373-377): "If using STATX_MNT_ID, this is the mount ID of the mount containing the file." Mask list (l.254): "STATX_MNT_ID           Want stx_mnt_id (since Linux 5.8)".
6. **STATX_MNT_ID_UNIQUE** — DESCRIPTION mask list (l.257): "STATX_MNT_ID_UNIQUE    Want unique stx_mnt_id (since Linux 6.8)". Field list (l.379-383): "this is the unique mount ID of the mount containing the file ... It is guaranteed to not be reused while the system is running." Version attached: **Linux 6.8**.
7. **btime may be unsupported?** Yes, but only via the page's general rule, not a btime-specific sentence. DESCRIPTION, "The returned information" (l.289-291): "If a filesystem does not support a field or if it has an unrepresentable value ..., then the mask bit corresponding to that field will be cleared in stx_mask even if the user asked for it". Also (l.~276): "the kernel may return fields that weren't requested and may fail to return fields that were requested, depending on what the backing filesystem supports." The literal phrase "support varies by filesystem" occurs only on STATX_DIOALIGN (l.256), STATX_SUBVOL (l.259), STATX_WRITE_ATOMIC (l.264), STATX_DIO_READ_ALIGN (l.266); it is NOT attached to STATX_BTIME, STATX_INO, STATX_NLINK or STATX_MNT_ID. No sentence says "btime may be unsupported" in those words.
8. **Hard links and file identity** — the statx page has NO statement that a hard-linked pair shares an inode or that inode compare decides identity. Nearest words: stx_nlink "The number of hard links on a file."; STATX_ATTR_IMMUTABLE (l.467-470): "no hard links can be created to this file"; stx_dev_major/minor (l.364-366): "The device on which this file (inode) resides." — i.e. the page ties the inode to a device, so an inode number alone is not a cross-filesystem identity (the entry's identity prose omits stx_dev_*; its lane rule `stat -c '%d:%i'` has it). The "two names, one file" statement is in link(2) (S122), not statx(2); I did not open link(2) this run.

### Claim -> page supports? (staged entry duplicate-verdict-identity.md)
| # | Entry claim (line) | statx(2) supports? | Note |
|---|---|---|---|
| a | `stx_ino; /* Inode number */` in struct (l.34) | yes | l.97, whitespace collapsed |
| b | `stx_nlink; /* Number of hard links */` (l.34-35) | yes | l.93 |
| c | `stx_btime; /* Creation */` (l.39) | yes | l.106 |
| d | `stx_mnt_id; /* Mount ID */` (l.39-40) | yes | l.120 |
| e | `STATX_MNT_ID_UNIQUE` available since Linux 6.8 (l.40, 52) | yes | l.257 |
| f | source cite "§ CONSTANTS STATX_BTIME, STATX_MNT_ID_UNIQUE" (l.2) | **no** | the page has no CONSTANTS heading. Sections: NAME, LIBRARY, SYNOPSIS, DESCRIPTION, RETURN VALUE, ERRORS, STANDARDS, HISTORY, SEE ALSO, COLOPHON. Both constants sit in the DESCRIPTION `mask` list. Fix to "§ DESCRIPTION (mask constants)". |
| g | version "Linux man-pages 6.19 (2026-02-08)" (l.2, 5) | yes | footer l.587 |
| h | hard-link count distinguishes "one file with two names" from "two independent copies"; makes it a count question (l.35-37) | partial | page only says nlink is "the number of hard links on a file"; the distinguishing role is [INFERENCE] by the entry author. Also nlink>1 alone does not prove two given paths are the same file; that needs dev+ino equality |
| i | verdict must "compare inodes" (l.31-32) | partial | page ties an inode to a device (l.364-366); inode number alone is per-filesystem. link(2), not statx, carries the "same file" statement |
| j | `stx_btime` support is filesystem-dependent; "statx(2) notes that fields may simply be absent" (l.47-48) | yes (general rule) / partial (btime-specific) | l.289-291 covers absent fields generally; no btime-specific sentence |
| k | "the man page marks other fields with 'support varies by filesystem'" (l.48-49) | yes | l.256, 259, 264, 266 — and not btime, so "other" is accurate |
| l | "No claim is made that creation time is available everywhere" (l.49-50) | yes | consistent with l.289-291 |
| m | `stx_mnt_id` identifies the mount, not the file (l.51) | yes | l.373-374 "mount ID of the mount containing the file" |
| n | uniqueness guarantee "only arrived in Linux 6.8" (l.51-52) | yes | l.257 and l.381-382 "guaranteed to not be reused while the system is running" |
| o | "a receipt that keys on it must record the kernel version it assumed" (l.52-53) | no (design advice) | not on the page; page does not require it. It is a lane recommendation and should be labelled as such, not as page-derived |
| p | "fields may simply be absent" support (l.47) vs a stx_mask check | partial | the page's actual mechanism is the stx_mask bit being cleared (l.289-291); entry does not name stx_mask. Optional precision |

## Findings (defects to route to the L1)
9. DEFECT-1 (location l.2 of entry): `§ CONSTANTS` heading does not exist on the 6.19 page; a Gate/provenance line citing it will not resolve for a reader. Replace with `§ DESCRIPTION` (mask constants list) and cite the exact quote for STATX_MNT_ID_UNIQUE: "STATX_MNT_ID_UNIQUE    Want unique stx_mnt_id (since Linux 6.8)" (whitespace collapses to a single space).
10. DEFECT-2 (entry l.31-37): the identity rule is stated with `stx_ino` + `stx_nlink` only; the page pairs the inode with the device ("The device on which this file (inode) resides."). Add `stx_dev_major/stx_dev_minor` (or the lane's `%d:%i`) or a reader may compare inode numbers across filesystems. Not a statx claim failure; an omission against the page.
11. DEFECT-3 (entry l.52-53): the "must record the kernel version" sentence reads as page-derived; it is not. Mark as the entry's recommendation.
12. Gate-quote candidates (each <=25 words, no pipe): "stx_ino: The inode number of the file." / "STATX_MNT_ID_UNIQUE    Want unique stx_mnt_id (since Linux 6.8)" / "If a filesystem does not support a field ... the mask bit corresponding to that field will be cleared in stx_mask" — the last is >25 words if run on; trim to "the mask bit corresponding to that field will be cleared in stx_mask even if the user asked for it" (19 words).

## Deliveries
None (report only; no snapshot written — another seat pins it). Scratch `/var/tmp/souji-r29-SwarmScout32` removed.
