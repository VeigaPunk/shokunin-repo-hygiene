# DraftEntryNoCopy — receipts, then the draft

Item: draft the lane-format knowledge entry for the no-clobber staging primitive,
adapted (not copied) from
`/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-staging-no-copy-r23.md`.
Target path (NOT created by this seat): `corpus/knowledge/quarantine-staging-no-copy-r23.md`.

Structure of this file: this receipts block, a planned-id mapping (not part of the
entry), a rule, then the draft verbatim from its first `source:` line to the end of
the file. Nothing below the rule is a receipt.

## Receipts — commands run 2026-10-25, with observed output

Read-only throughout. No probe was executed; nothing was created except this file
and the seat report. Working directory
`/home/vgpnk/Projects/shokunin/souji-shokunin` unless stated.

R1. Source files read (contents, not just digests):

    /home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-staging-no-copy-r23.md
    /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/noreplace_probe.py
    /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/noreplace-probe.out
    census/round-22/attempt2/sources/vendor-noreplace-probe.out
    census/round-22/attempt2/sources/man7-rename.2.txt
    census/round-22/attempt2/sources/man7-mv.1.txt
    corpus/SOURCES.md (rows S109-S111; the only rows cited by any mapping below)
    tools/souji-gate-check.py (checks 1-6, slice predicate, selftest)
    .deepresearch/20261024_064146_r9-tierrules/final_turn_001.md:118 (rejected row)
    /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-trigger-prune.out
    corpus/knowledge/quarantine-origin-record-fields-r24.md (frontmatter shape)
    corpus/QUALITY.md (Q1-Q53 admission bar; Q4 fixture-path rule)

R2. Digests — the vendored lane copy and the shokuknow payload output are the same bytes:

    $ sha256sum census/round-22/attempt2/sources/vendor-noreplace-probe.out \
                /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/noreplace_probe.py \
                /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/noreplace-probe.out
    1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5  census/.../vendor-noreplace-probe.out
    11df88f1f5687e9af93526943d875514d4c6b8e891a998edcc0aab73f1d4739f  .../noreplace_probe.py
    1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5  .../noreplace-probe.out

    $ cmp census/round-22/attempt2/sources/vendor-noreplace-probe.out \
          /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/noreplace-probe.out && echo BYTE_IDENTICAL
    BYTE_IDENTICAL                       # exit 0

R3. Fleet rows counted from the vendored output:

    $ awk -F'\t' 'NF>1 && $2 ~ /^fstype=/{n++} END{print n}' census/round-22/attempt2/sources/vendor-noreplace-probe.out
    5
    $ grep -c 'NOREPLACE_new=0(ok)'        census/round-22/attempt2/sources/vendor-noreplace-probe.out
    5
    $ grep -c 'NOREPLACE_existing=-1(EEXIST)' census/round-22/attempt2/sources/vendor-noreplace-probe.out
    5
    $ grep -c 'plain_overwrite=0(ok)'      census/round-22/attempt2/sources/vendor-noreplace-probe.out
    5
    $ grep -c '^kernel:'                   census/round-22/attempt2/sources/vendor-noreplace-probe.out
    1
    $ grep '^kernel:'                      census/round-22/attempt2/sources/vendor-noreplace-probe.out
    kernel: 7.2.11-arch1-1

R4. Host versions measured this round:

    $ uname -r
    7.2.11-arch1-1
    $ /usr/bin/mv --version | head -1
    mv (GNU coreutils) 9.12
    $ pacman -Qo /usr/bin/mv
    /usr/bin/mv is owned by coreutils 9.12-2
    $ /usr/bin/mv --help | grep -n -E 'no-copy|exchange|no-clobber'
    13:      --exchange
    14:        exchange source and destination
    19:  -n, --no-clobber
    22:      --no-copy
    49:'none' is like the --no-clobber option, in that no files in the

    Note (observed, not a lane claim): in this harness's shell `type -a mv` reports
    `mv is a shell builtin` before `/usr/bin/mv`, and a bare `mv --version` prints
    `mv 0.8.0`. The coreutils binary has to be named as `/usr/bin/mv`.

R5. Snapshot provenance and the exact spans quoted in the Gate:

    $ grep -n "man-pages-6.19" census/round-22/attempt2/sources/man7-rename.2.txt
    382: This page was obtained from the tarball man-pages-6.19.tar.gz
    $ grep -n "coreutils-9.11" census/round-22/attempt2/sources/man7-mv.1.txt
    184: from the tarball coreutils-9.11.tar.xz fetched from
    192:GNU coreutils 9.11 April 2026 MV(1)
    $ grep -n "EEXIST\|EINVAL" census/round-22/attempt2/sources/man7-rename.2.txt
    314: EEXIST flags contains RENAME_NOREPLACE and newpath already exists.
    316: EINVAL An invalid flag was specified in flags.
    318: EINVAL Both RENAME_NOREPLACE and RENAME_EXCHANGE were specified in
    321: EINVAL Both RENAME_WHITEOUT and RENAME_EXCHANGE were specified in
    324: EINVAL The filesystem does not support one of the flags in flags.

    rename.2 snapshot anchors: 148 `RENAME_NOREPLACE`; 149-150 the refusal
    sentence; 152-153 the RENAME_EXCHANGE exclusion; 155-156 the support
    precondition; 155-167 the support schedule; 314 EEXIST; 318 the both-flags
    EINVAL; 324 the unsupported-filesystem EINVAL.
    mv.1 snapshot anchors: 90 `--no-copy`; 91 its description.

R6. Rejected row verified: the campaign payload does not contain the quoted synopsis.

    $ sed -n '118p' .deepresearch/20261024_064146_r9-tierrules/final_turn_001.md
    | `souji` / round2 / S123 | `lanes/souji/round2/evidence/r23-trigger-prune.out` | `git worktree prune [-n] [-v] [--expire <expire>]` |
    $ grep -c "worktree" /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-trigger-prune.out
    0
    $ ls /home/vgpnk/Projects/shokuknow/lanes/souji/round2/evidence/r23-trigger-prune.sh
    ls: cannot access '.../evidence/r23-trigger-prune.sh': No such file or directory   # exit 2

R7. Snapshot files are committed at HEAD (`3216c1998fe04d7e23793ffd4e135bd37c3a11f4`):

    $ git cat-file -e HEAD:census/round-22/attempt2/sources/man7-rename.2.txt   -> tracked_at_HEAD
    $ git cat-file -e HEAD:census/round-22/attempt2/sources/man7-mv.1.txt       -> tracked_at_HEAD
    $ git cat-file -e HEAD:census/round-22/attempt2/sources/vendor-noreplace-probe.out -> tracked_at_HEAD

## Planned id mapping (L1 re-point; NOT part of the entry)

The draft uses `S-NEW-<slug>` placeholders as this item instructs. `SOURCES.md`
already carries the three rows these placeholders name, so the re-point should
replace the placeholder token only and add no row (preregistration: rows that
already exist are cited, not duplicated):

| placeholder in draft | registered id | row evidence read this round |
|---|---|---|
| `S-NEW-noreplace-probe` | `S109` | corpus/SOURCES.md:129 — own-work probe + vendored output, sha256 1634d206…8bb5 |
| `S-NEW-rename2` | `S110` | corpus/SOURCES.md:130 — https://man7.org/linux/man-pages/man2/rename.2.html |
| `S-NEW-mv1` | `S111` | corpus/SOURCES.md:131 — https://man7.org/linux/man-pages/man1/mv.1.html |

Until the re-point, `tools/souji-gate-check.py` fails only its check 5
(`check5-no-source-citation`), because `SOURCE_RE` matches `S<digits>` only.
Every other per-entry check passes as written — measured, see the report.

---

<!-- rule: everything below is the draft entry, verbatim -->
source: S-NEW-noreplace-probe — own-work probe lanes/souji/round2/evidence/noreplace_probe.py (sha256 11df88f1f5687e9af93526943d875514d4c6b8e891a998edcc0aab73f1d4739f) and its output lanes/souji/round2/evidence/noreplace-probe.out (sha256 1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5), byte-identical to census/round-22/attempt2/sources/vendor-noreplace-probe.out; kernel 7.2.11-arch1-1, produced 2026-10-23; read this round, not re-executed in this lane
source: S-NEW-rename2 — https://man7.org/linux/man-pages/man2/rename.2.html — § DESCRIPTION flags, § ERRORS — snapshot census/round-22/attempt2/sources/man7-rename.2.txt (man-pages-6.19.tar.gz)
source: S-NEW-mv1 — https://man7.org/linux/man-pages/man1/mv.1.html — § OPTIONS --no-copy, --exchange — snapshot census/round-22/attempt2/sources/man7-mv.1.txt (coreutils-9.11 page)
verified-at: 2026-10-25 — both snapshots opened this round; host /usr/bin/mv = GNU coreutils 9.12-2 (pacman -Qo /usr/bin/mv); kernel 7.2.11-arch1-1 (uname -r)
recheck: 90d — re-open both snapshots and vendor-noreplace-probe.out, and confirm /usr/bin/mv --help still lists --no-copy; re-run the probe only when the mount set or the kernel changes
ground: F4 — restorable quarantine (the staging primitive: no-clobber rename)

# A no-clobber staging rename exists on all five probed devices, and `mv --no-copy` is the portable fallback

## Claim (F4: sourced semantics, one vendored fleet measurement)

The lane's audit rule is dry-run by default, quarantine before delete. A staging
move that can overwrite an existing quarantine artifact breaks that rule before
any deletion decision is taken, so the primitive has to be a refusal, not a best
effort. Two spellings of that refusal are documented, and one of them has been
measured on this host's filesystem set.

1. **The kernel flag is specified as a refusal, with an explicit per-filesystem
   precondition.** (S-NEW-rename2) § DESCRIPTION, `flags` argument: "Don't
   overwrite newpath of the rename. Return an error if newpath already exists."
   (snapshot lines 148-150.) The same section states the precondition —
   "RENAME_NOREPLACE requires support from the underlying filesystem." — and then
   lists the schedule: ext4 (Linux 3.15); btrfs, tmpfs and cifs (3.17); xfs (4.0);
   many other filesystems in 4.9 (snapshot lines 155-167). § ERRORS names the
   refusal: "EEXIST flags contains RENAME_NOREPLACE and newpath already exists."
   (snapshot line 314.) That is a support *schedule*, not a fact about any host.
2. **The two flags cannot be combined.** § DESCRIPTION: "RENAME_NOREPLACE can't be
   employed together with RENAME_EXCHANGE." (snapshot lines 152-153; § ERRORS
   repeats it as an EINVAL case at snapshot line 318.) A staging design that uses
   the no-clobber rename cannot also use the atomic swap in the same call.
3. **`mv --no-copy` is the portable spelling of the same refusal.** (S-NEW-mv1)
   § OPTIONS `--no-copy`: "do not copy if renaming fails" (snapshot lines 90-91).
   Without it GNU `mv` may fall back to copy+remove, which turns a staging move
   into a copy the lane cannot verify atomically. The option is present in the
   installed binary: `/usr/bin/mv --help | grep -n -E 'no-copy|exchange|no-clobber'`
   prints lines 13-14 (`--exchange`), 19 (`-n, --no-clobber`) and 22 (`--no-copy`)
   on GNU coreutils 9.12-2. (A bare `mv --version` in this harness's shell reports
   a builtin, `mv 0.8.0`; name the binary.)
4. **The fleet side was measured once, by another lane, and is vendored here.**
   The probe calls `renameat2(AT_FDCWD, a, AT_FDCWD, b, RENAME_NOREPLACE)` through
   `ctypes` (`libc.renameat2.argtypes`, `RENAME_NOREPLACE = 1`) and runs three
   steps per directory: rename onto a non-existent target, rename onto an existing
   target with the flag, then a plain `renameat2(..., 0)` onto that same existing
   target. It derives each filesystem type with `stat -f -c %T` and prints
   `platform.release()`. Its five rows are counted in the next section.

## The fleet measurement (vendored output, read this round, not re-executed)

`census/round-22/attempt2/sources/vendor-noreplace-probe.out` is byte-identical to
the shokuknow payload output `lanes/souji/round2/evidence/noreplace-probe.out`:
both are `sha256 1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5`
(`sha256sum` over both paths; `cmp` exits 0). The five rows are:

```
/var/tmp	fstype=btrfs	NOREPLACE_new=0(ok)	NOREPLACE_existing=-1(EEXIST)	plain_overwrite=0(ok)
/home/vgpnk/Projects/shokunin	fstype=btrfs	NOREPLACE_new=0(ok)	NOREPLACE_existing=-1(EEXIST)	plain_overwrite=0(ok)
/home/vgpnk/Projects/shokuknow	fstype=btrfs	NOREPLACE_new=0(ok)	NOREPLACE_existing=-1(EEXIST)	plain_overwrite=0(ok)
/dev/shm	fstype=tmpfs	NOREPLACE_new=0(ok)	NOREPLACE_existing=-1(EEXIST)	plain_overwrite=0(ok)
/tmp	fstype=xfs	NOREPLACE_new=0(ok)	NOREPLACE_existing=-1(EEXIST)	plain_overwrite=0(ok)
kernel: 7.2.11-arch1-1
```

- Five device rows: `awk -F'\t' 'NF>1 && $2 ~ /^fstype=/{n++} END{print n}'
  census/round-22/attempt2/sources/vendor-noreplace-probe.out` prints `5`.
- Five successes on a free target: `grep -c 'NOREPLACE_new=0(ok)' …` prints `5`.
- Five refusals on an occupied target: `grep -c 'NOREPLACE_existing=-1(EEXIST)' …`
  prints `5`.
- Five plain overwrites: `grep -c 'plain_overwrite=0(ok)' …` prints `5`.
- Three filesystems: btrfs ×3, tmpfs ×1, xfs ×1. All three are on the man page's
  supported list (btrfs and tmpfs since 3.17, xfs since 4.0), so the measurement
  agrees with the documented schedule rather than extending it.
- The plain-overwrite column is the control: the same call with flags 0 succeeds on
  the same occupied target, so the `EEXIST` is attributable to the flag and not to
  the harness.
- One of the btrfs rows is the mount this lane's repository tree sits under
  (`/home/vgpnk/Projects/shokunin`). That is a statement about that mount on
  2026-10-23 — not about the repository, not about a container root, and not about
  any mount added later.

Point-in-time: five directories, one kernel (the output's `kernel:` line is
7.2.11-arch1-1, the same kernel `uname -r` reported on 2026-10-25), produced
2026-10-23, not re-executed in this lane.

## What this does NOT establish

- **The probe is a point-in-time measurement** of five directories on one kernel.
  A filesystem mounted later, a different mount namespace, or a container with a
  different root could differ. A tool must still degrade explicitly rather than
  assume the flag.
- **`RENAME_NOREPLACE` is not `RENAME_EXCHANGE`**, and the two cannot be combined
  (S-NEW-rename2). Nothing here establishes that an exchange-based staging design
  is available.
- The probe does not test **`RENAME_WHITEOUT`**, overlayfs semantics, or behaviour
  on a filesystem where the flag is unsupported (the expected failure there is
  `EINVAL`, snapshot line 324).
- It says nothing about the **per-item origin record** a staging step would need;
  that is `corpus/knowledge/quarantine-origin-record-fields-r24.md`.
- **This lane did not execute the probe.** Digest equality proves the vendored copy
  holds the same bytes as the shokuknow payload output; it does not prove
  authorship, currency of the mounted filesystems, or reproducibility today.
- **`mv --no-copy` was verified as an option present in the installed binary's
  help, not as exercised behaviour.** This lane ran no refusal case, and the
  cross-device copy fallback the option suppresses is untested here.
- **Re-running the payload probe is not a Q4-conforming fixture run.** It creates
  and unlinks `probe-a`/`probe-b` inside each probed directory, including two live
  repository roots (`/home/vgpnk/Projects/shokunin`,
  `/home/vgpnk/Projects/shokuknow`). This entry reads the recorded output and does
  not re-execute it; a future re-run needs a scratch-only variant.
- **No staging tool is changed by this entry**, and no move or deletion authority
  is created. It removes a precondition question; the operator change and its
  receipts are separate.

## Lane link and consequence

F4's next step named "`mv --no-copy` staging" as an operator tool change. The
blocker was never the semantics — S-NEW-rename2 and S-NEW-mv1 hold those — but
whether the primitive exists on the filesystems the lane works on. On the five
vendored devices it does, and the plain-overwrite control shows the refusal comes
from the flag. So the change can proceed without a degraded path, and what remains
is the record format, not the primitive.

## Gate

url: https://man7.org/linux/man-pages/man2/rename.2.html
snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
opened: 2026-10-25

- ADMIT: "RENAME_NOREPLACE Don't overwrite newpath of the rename. Return an error if newpath already exists." — § DESCRIPTION flags — snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
- ADMIT: "RENAME_NOREPLACE requires support from the underlying filesystem." — § DESCRIPTION flags — snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
- ADMIT: "RENAME_NOREPLACE can't be employed together with RENAME_EXCHANGE." — § DESCRIPTION flags — snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
- ADMIT: "EEXIST flags contains RENAME_NOREPLACE and newpath already exists." — § ERRORS — snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
- ADMIT: "do not copy if renaming fails" — § OPTIONS --no-copy — snapshot: census/round-22/attempt2/sources/man7-mv.1.txt
- REJECT: campaign row `souji/round2/S123` (`.deepresearch/20261024_064146_r9-tierrules/final_turn_001.md` line 118) cites `lanes/souji/round2/evidence/r23-trigger-prune.out` for the git-worktree prune synopsis — reason: this round `grep -c worktree` over that payload prints 0 and no `r23-trigger-prune.sh` exists in that directory, so the row is a wrong-source citation rather than a fact about the payload; flip: re-cite the synopsis against git-worktree(1) and keep the payload for its own PASS lines.
