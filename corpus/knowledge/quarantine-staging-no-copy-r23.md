source: S109 — souji round-2 noreplace probe, vendored byte-exact at census/round-22/attempt2/sources/vendor-noreplace-probe.out (sha256 1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5); not re-run in this lane
source: S110 — https://man7.org/linux/man-pages/man2/rename.2.html
source: S111 — https://man7.org/linux/man-pages/man1/mv.1.html
verified-at: 2026-10-25 — Linux man-pages 6.19 (2026-02-08) snapshots opened this round; host coreutils 9.12; kernel 7.2.11-arch1-1
recheck: 90d — re-open census/round-22/attempt2/sources/{man7-rename.2,man7-mv.1}.txt and the vendored probe output
ground: F4 — restorable quarantine (the staging primitive: no-clobber rename)

# A no-clobber staging primitive exists on the five devices this fleet's repositories live on — and `mv --no-copy` is the portable fallback

## Claim (F4, sourced + one vendored measurement)

**What this entry is not:** the primitive's *semantics* are already held by
`corpus/knowledge/quarantine-same-filesystem-rename.md` (S025: `mv --no-copy`
as the fail-closed guard; an observed `renameat2(…, RENAME_NOREPLACE)`). This
entry adds (a) the man-page statement of the refusal and its per-filesystem
support schedule (S110/S111) and (b) a **vendored, five-device availability
observation** (S109) with the provenance stated. No tool or format change is
made or authorized here.
`renameat2(RENAME_NOREPLACE)` and `mv --no-copy` both turn "the destination
already exists" into a failure instead of a silent overwrite. That is the
primitive a quarantine staging step needs before it is allowed to move a
payload at all: the audit's own rule is *dry-run by default, quarantine
before delete*, and a staging move that can overwrite an existing quarantine
artifact violates it.

1. **The no-clobber flag is specified as a refusal.**
   "RENAME_NOREPLACE Don't overwrite newpath of the rename. Return an error if
   newpath already exists." (S110, § DESCRIPTION, `flags` argument.) The same
   page states that the flag needs per-filesystem support and lists ext4 3.15,
   btrfs and tmpfs 3.17, xfs 4.0 — a *precondition*, not a fact about this host.
2. **`mv --no-copy` is the portable spelling of the same refusal.**
   "do not copy if renaming fails" (S111, § DESCRIPTION, option `--no-copy` — the page has no OPTIONS heading). Without it,
   GNU `mv` may fall back to copy+remove, which turns a cross-device staging
   step into a copy the lane cannot verify atomically.
3. **The five-device measurement is vendored, not this lane's execution.**
   The probe output copied byte-exact into
   `census/round-22/attempt2/sources/vendor-noreplace-probe.out`
   (sha256 `1634d206…8bb5`, produced 2026-10-23 by the
   `corpus-expansion-1` staging lane, kernel 7.2.11-arch1-1) reports for
   `/var/tmp` (btrfs), `/home/vgpnk/Projects/shokunin` (btrfs),
   `/home/vgpnk/Projects/shokuknow` (btrfs), `/dev/shm` (tmpfs) and `/tmp`
   (xfs): `NOREPLACE_existing=-1(EEXIST)` and `plain_overwrite=0(ok)`. Every
   device the lane works on therefore implements the flag, and the difference
   is the flag rather than the harness.

## What this does NOT establish
- **The measurement is a vendored, point-in-time observation** of five
  directories on one kernel, produced by another lane. This lane did not
  re-run the probe this round; a later mount, another mount namespace or a
  container root could differ. A tool must still degrade explicitly (fall
  back to `mv --no-copy`) rather than assume the flag.
- **`RENAME_NOREPLACE` is not `RENAME_EXCHANGE`**, and the two cannot be
  combined (S110).
- The probe does not test `RENAME_WHITEOUT`, overlayfs semantics, or a
  filesystem that rejects the flag with `EINVAL`.
- It says nothing about the **per-item origin record** a staging step needs;
  that is `corpus/knowledge/quarantine-origin-record-fields-r24.md`.
- No staging tool is changed by this entry. It removes a blocker; it grants
  no new deletion or move authority.

## Lane link and consequence
F4's next step named "`mv --no-copy` staging" as an operator tool change. The
blocker was never the semantics (S110/S111 hold them) but whether the primitive
exists on the fleet's own filesystems. On the five vendored devices it does, so
the change can proceed without a degraded path, and the remaining work is the
record format, not the primitive.

## Gate

url: https://man7.org/linux/man-pages/man2/rename.2.html
snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
opened: 2026-10-25

- ADMIT: "RENAME_NOREPLACE Don't overwrite newpath of the rename. Return an error if newpath already exists." — § DESCRIPTION flags — reason: the refusal semantics this entry's staging claim depends on — snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
- ADMIT: "RENAME_NOREPLACE requires support from the underlying filesystem." — § DESCRIPTION flags — reason: names the precondition the five-device measurement tests — snapshot: census/round-22/attempt2/sources/man7-rename.2.txt
- ADMIT: "do not copy if renaming fails" — § DESCRIPTION, option --no-copy — reason: the portable fallback this entry recommends when the flag is unavailable — snapshot: census/round-22/attempt2/sources/man7-mv.1.txt
- REJECT: staged entry quarantine-staging-no-copy-r24 (same primitive, a second device list, no new refusal semantics or field) — reason: duplicate ground; the r23 entry already records the five-device measurement and the package adds an eight-mount list without a consequence this lane's staging plan would change — flip: a measurement on a filesystem or mount namespace the r23 entry did not cover, plus a consequence a staging tool would change.
