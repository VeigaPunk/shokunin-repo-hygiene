source: S214 — IEEE Std 1003.1-2024 (POSIX.1-2024) · fsync() — https://pubs.opengroup.org/onlinepubs/9799919799/functions/fsync.html
verified-at: 2026-10-25 — Issue 8 page fetched this run; snapshot SHA-256 `5c2975abbb2d65fcad92a4da5241f4f4001f0e5d8cf57f752d9486073ca49747` (fsync.html)
recheck: 365d — re-fetch the Issue 8 fsync page (the standard is revised on a multi-year cycle)
ground: F4 — restorable quarantine (the durability guarantee a published origin record needs, and the limit on what any guarantee can promise)

# Atomicity is not durability, and durability is the platform's to promise

## Claim (F4, sourced at the specification)

The exclusivity entry (S212/S213) established that `O_EXCL` creation and
`rename()` publication are atomic: they govern what a reader sees, and when.
Neither says the record survives a crash. `fsync()` is the primitive that does,
and the specification draws its own limits.

**`fsync()` is the durability primitive.** It is intended to force a physical
write of data from the buffer cache and to assure that after a system crash or
other failure, all data up to the time of the call is recorded on the disk.

**The standard permits a null implementation.** Where the system cannot assure
non-volatile storage under any circumstances — or is highly fault-tolerant and
the functionality is not required — a null implementation is explicitly
permitted, and what the user can expect is deferred to the conformance
document.

So the third primitive completes the scheme — create exclusively, write
privately, flush, rename into place — and draws its boundary: a souji
record's crash-safety is bounded by the platform's guarantee, and cannot be
asserted from the record's own structure. A receipt that claims durability must
claim the platform's, not its own.

## What this does NOT establish

- It does not specify the record's content or the order in which the payload
  and the record are published.
- It does not make the record-and-payload pair atomic; a crash between the
  payload write and the record rename still leaves a payload without a record,
  or a record without a payload.
- It does not say a receipt must call `fsync()` — that is an implementation
  choice this entry makes available, not a requirement it imposes.
- It does not establish that the lane's host provides the guarantee; the
  specification explicitly permits a null implementation.
- It does not re-decide the lane's rollback discipline.

## Gate

url: https://pubs.opengroup.org/onlinepubs/9799919799/functions/fsync.html
snapshot: census/round-28/sources/fsync.html
opened: 2026-10-25

- ADMIT: "system crash or other failure that all data up to the time of the <i>fsync</i>() call is recorded on the disk." — § RATIONALE / durability — reason: fsync is the durability primitive (S214) — snapshot: census/round-28/sources/fsync.html
- ADMIT: "It is explicitly intended that a null implementation is permitted." — § RATIONALE / null implementation — reason: durability is the platform's to promise, not the record's (S214) — snapshot: census/round-28/sources/fsync.html
- REJECT: staged S138 (Qiita community Git GC notes) — reason: a community-reclamation row bearing on F1/F2, not on the F4 origin-record primitives; flip: only reconsider if an F4 consumer needs community corroboration of a POSIX page.
