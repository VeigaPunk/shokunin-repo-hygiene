source: S212 — IEEE Std 1003.1-2024 (POSIX.1-2024) · open() — https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html
source: S213 — IEEE Std 1003.1-2024 (POSIX.1-2024) · rename() — https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html
verified-at: 2026-10-25 — Issue 8 pages fetched this run; snapshot SHA-256 `57b770918aa3e0c25186972675df8c96da119cf4b973335ed4487405e260dc3a` (open.html), `06671610134b0a52cdf4dcdaf382f72fef85ef51088b8a52b8679c7f03829318` (rename.html)
recheck: 365d — re-fetch both Issue 8 pages (the standard is revised on a multi-year cycle)
ground: F4 — restorable quarantine (the POSIX guarantees a per-item origin record needs: exclusive creation and atomic publication)

# The origin record needs O_EXCL and rename, not rollback

## Claim (F4, sourced at the specification)

The previous F4 entries (S022, S146, S152, S210, S211) established the record's
shape and GLib's writer. This entry supplies the specification behind them:
the two POSIX guarantees a per-item origin record's write path depends on.

**Exclusive creation is atomic.** With `O_CREAT|O_EXCL`, `open()` shall fail if
the file exists, and the existence check and the creation are a single atomic
step with respect to other threads executing `open()` on the same name. A
second writer for the same item therefore gets `[EEXIST]` — the collision is
detectable, never silent, and no lock is needed to keep the record unique.

**Publication is atomic, and a failure leaves the target untouched.** The
specification requires that the action of `rename()` be atomic, and that if it
fails for any reason other than `[EIO]`, any file named by `new` shall be
unaffected. A record can therefore be published by writing a private file and
renaming it into place: a reader never sees a half-written record, and a failed
publish leaves the previous target in place.

Together the two primitives form the scheme: create the record exclusively,
write it privately, rename it into place. Uniqueness comes from `O_EXCL`,
visibility comes from `rename`, and the failure mode of each is a detectable
error rather than a torn file.

## What this does NOT establish

- It does not specify the record's content or format — that is held at S022
  (FreeDesktop shape) and S146 (GVFS reader), with GLib's writer at S152.
- It does not say the platform provides these guarantees; a platform without
  `O_EXCL` or with a non-atomic `rename` needs a different mechanism.
- It does not cover the payload: moving the payload and publishing its record
  are two operations; POSIX makes each atomic, not the pair.
- It does not re-decide the lane's rollback discipline; it only removes the
  need for a rollback of the record itself.

## Gate

url: https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html
url: https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html
snapshot: census/round-28/sources/open.html
snapshot: census/round-28/sources/rename.html
opened: 2026-10-25

- ADMIT: "creation of the file if it does not exist shall be atomic with respect to other threads executing" — § DESCRIPTION, O_EXCL — reason: exclusive creation is one atomic step, so a per-item origin record needs no lock (S212) — snapshot: census/round-28/sources/open.html
- ADMIT: "If the <i>rename</i>() function fails for any reason other than [EIO], any file named by <i>new</i> shall be unaffected." — § DESCRIPTION — reason: a failed publish leaves the target untouched (S213) — snapshot: census/round-28/sources/rename.html
- ADMIT: "That specification requires that the action of the function be atomic." — § RATIONALE — reason: publication by rename is atomic (S213) — snapshot: census/round-28/sources/rename.html
- REJECT: staged S216 (Breitinger et al., IFIP DF 2014, approximate-matching thresholds) — reason: an F3 near-duplicate taxonomy row, not an F4 origin-record primitive; flip: only reconsider under F3 when the `duplicate`-class decision opens.
