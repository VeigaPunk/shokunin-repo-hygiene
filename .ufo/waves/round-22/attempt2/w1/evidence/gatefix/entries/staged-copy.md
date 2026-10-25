
source: S124 — lanes/souji/round2/evidence/noreplace_probe.py — 5 devices, kernel 7.2.11-arch1-1; evidence sha256 1634d206…; probe sha256 11df88f1…
source: S116 — https://man7.org/linux/man-pages/man2/rename.2.html — § DESCRIPTION flags, RENAME_NOREPLACE, RENAME_EXCHANGE — Linux man-pages 6.19 (2026-02-08)
source: S115 — https://man7.org/linux/man-pages/man1/mv.1.html — § OPTIONS `--no-copy`, `--exchange` — GNU coreutils 9.11 (April 2026)
verified-at: 2026-10-23 — host coreutils 9.12; man-pages 6.19 (2026-02-08); kernel 7.2.11-arch1-1
recheck: 90d — re-run `python3 lanes/souji/round2/evidence/noreplace_probe.py` (expect 5 devices, EEXIST on an existing target) (ran 2026-10-23)
ground: F4 — restorable quarantine (the staging primitive is now VERIFIED on this fleet's filesystems)

# `RENAME_NOREPLACE` is available on every device this fleet uses

## Claim (F4, measured)
S116 gave the *upstream support schedule* for `renameat2(RENAME_NOREPLACE)` —
ext4 3.15, btrfs/tmpfs/cifs 3.17, xfs 4.0 — which is a per-filesystem
precondition, not a fact about this host. This entry measures it.

1. **Every device the lane touches implements it.** The probe called
   `renameat2(AT_FDCWD, a, AT_FDCWD, b, RENAME_NOREPLACE)` directly via
   `ctypes` on five directories: `/var/tmp` (btrfs),
   `/home/vgpnk/Projects/shokunin` (btrfs), `/home/vgpnk/Projects/shokuknow`
   (btrfs), `/dev/shm` (tmpfs) and `/tmp` (xfs). On **all five**:
   - renaming to a **non-existent** target succeeded (return 0), and
   - renaming onto an **existing** target failed with **`EEXIST`**, and
   - a plain `renameat2` with flags 0 onto the same existing target
     **succeeded** (overwrote), confirming the difference is the flag and
     not the test harness.
2. **So a no-clobber quarantine staging step is available fleet-wide** and
   need not degrade on these filesystems. The btrfs, tmpfs and xfs support
   all post-date the S116 schedule entries, so the measurement agrees with
   the upstream documentation rather than contradicting it.
3. **`mv --no-copy` remains the portable fallback** (S115): it turns a failed
   rename into a *failure* rather than a silent copy+remove, on any
   filesystem, without needing `renameat2` at all.

## What this does NOT establish
- **The probe is a point-in-time measurement** of five directories on one
  kernel. A filesystem mounted later, a different mount namespace, or a
  container with a different root could differ. The tool must still degrade
  explicitly rather than assume the flag.
- **`RENAME_NOREPLACE` is not `RENAME_EXCHANGE`**, and the two cannot be
  combined (S116). Nothing here establishes that an exchange-based staging
  design is available.
- The probe does not test **`RENAME_WHITEOUT`**, overlayfs semantics, or
  behaviour on a filesystem where the flag is unsupported (the expected
  failure there is `EINVAL`).
- This says nothing about the **per-item origin record** that a staging step
  would need to write; that is `corpus/knowledge/quarantine-origin-record-fields-r23.md`.

## Lane link and consequence
F4's next step named "`mv --no-copy` staging" as an operator tool change.
The blocker for that change was never the semantics (S115/S116 hold them) but
the question of whether the primitive exists on the fleet's own filesystems.
It does — on all five devices probed — so the tool change can proceed without
a degraded path, and the remaining work is the record format, not the
primitive.
