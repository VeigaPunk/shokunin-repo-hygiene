# SwarmExecutor07 — Exec-C2Entries report (round 28, w1)

## Status

STATUS: PASS — both admitted F4 knowledge-entry drafts authored (`origin-record-exclusivity-r28.md`, `origin-record-durability-r28.md`), each with `source:`/`verified-at:`/`recheck:`/`ground:` front matter, a scoped claim body, and a `## Gate` block with admits using the EXACT quotes from `census/round-28/records/posix-quotes.tsv` (verified verbatim in this run's POSIX snapshots, `<i>` tags preserved) and rejects from the staged package. Full file contents delivered below and as delivery files in this directory; byte-exact POSIX snapshot copies delivered under `snapshots/` for the L1 to place at `census/round-28/sources/`. Entry drafts are NOT written into `corpus/knowledge/` (L1 integrates). No S215/S119 handling in this seat's deliverables (rejects are S216/S138; C2 frozen counter untouched).

## Evidence

- Fetch (2026-10-25, decision-time): `curl -fsSL https://pubs.opengroup.org/onlinepubs/9799919799/functions/{open,rename,fsync}.html` → `open.html` 40401 B sha256 `57b770918aa3e0c25186972675df8c96da119cf4b973335ed4487405e260dc3a`; `rename.html` 26407 B sha256 `06671610134b0a52cdf4dcdaf382f72fef85ef51088b8a52b8679c7f03829318`; `fsync.html` 10474 B sha256 `5c2975abbb2d65fcad92a4da5241f4f4001f0e5d8cf57f752d9486073ca49747`. Copies in `snapshots/` (byte-identical, sha256 rechecked).
- Quote source: `census/round-28/records/posix-quotes.tsv` (5 rows). Every tsv quote verified verbatim (grep -F, including `<i>` tags) against the snapshot bytes: open.html "creation of the file if it does not exist shall be atomic with respect to other threads executing" (18 words); rename.html "If the <i>rename</i>() function fails for any reason other than [EIO], any file named by <i>new</i> shall be unaffected." (19); rename.html "That specification requires that the action of the function be atomic." (11); fsync.html "system crash or other failure that all data up to the time of the <i>fsync</i>() call is recorded on the disk." (21); fsync.html "It is explicitly intended that a null implementation is permitted." (10). All ≤25 words, no `|` inside any quote.
- Lane registry currently ends at S211 (`corpus/SOURCES.md:156`), so S212/S213/S214 are the next free lane ids — consistent with the frozen preregistration C2 text (S212=open(), S213=rename(), S214=fsync(); status=mined; used-by exactly the admitted entries; C2 frozen row count 138).
- Staged-package rejects: S216 (Breitinger et al., IFIP DF 2014 — `SOURCES.append.md` row S216, duplicate-threshold paper, F3) and S138 (Qiita community Git GC notes — row S138, community-reclamation, F1/F2). Both present in the staged set `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md`.

## Findings

1. Exclusivity claim scoped to what S212/S213 establish: exclusive creation via `O_CREAT|O_EXCL` is one atomic step (EEXIST to a second writer, no lock needed); `rename()` publication is atomic and a failure leaves the target untouched except `[EIO]`. Limits stated: no format/content claim (S022/S146/S152 hold those), no platform-availability claim, no record+payload pair atomicity, no rollback re-decision.
2. Durability claim scoped to what S214 establishes: `fsync()` forces a physical write and records all data up to the call on the disk; the standard explicitly permits a null implementation where non-volatile storage cannot be assured, so durability is the platform's to promise, not the record's. Limits stated: no content/order, no pair atomicity, fsync not mandated, host guarantee not established, no rollback re-decision.
3. Gate admits mirror the citation rows exactly (S212/S213 in exclusivity entry; S214 in durability entry), each with the tsv-exact quote, snapshot path `census/round-28/sources/<page>.html`, and `opened: 2026-10-25`. The initial drafts used rendered/plain versions; corrected to the tsv quotes (with `<i>` tags) after the parent relay pointed at `posix-quotes.tsv`.
4. Rejects are out-of-scope staged candidates with reason + flip: S216 (duplicate-verdict row) in the exclusivity entry; S138 (community-reclamation row) in the durability entry. No S215/S119 references in this seat's deliverables; no counter/predicate touched.
5. `verified-at: 2026-10-25`; `recheck: 365d`; `ground: F4` per corpus entry format.

## Delivery files (in this directory)

- `origin-record-exclusivity-r28.md` (full contents below)
- `origin-record-durability-r28.md` (full contents below)
- `snapshots/open.html`, `snapshots/rename.html`, `snapshots/fsync.html` (byte-exact Issue 8 pages; place at `census/round-28/sources/`)

---

## origin-record-exclusivity-r28.md

```
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
```

## origin-record-durability-r28.md

```
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
```

## Attack log

None — this seat authored the two entries; no counter/predicate/target is contested. Parent-relay corrections applied: Gate quotes made byte-exact from `posix-quotes.tsv`; no S215 appended (frozen C2 row count 138 untouched) and no S119 disposition by this seat.
