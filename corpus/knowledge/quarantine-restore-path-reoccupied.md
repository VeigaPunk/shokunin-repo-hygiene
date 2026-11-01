source: S268 — https://man7.org/linux/man-pages/man2/renameat2.2.html (capture census/round-46/sources/renameat2-located-quote.txt; re-opened live 2026-10-31 by the r46 landing session)
source: S110 — https://man7.org/linux/man-pages/man2/rename.2.html (re-opened 2026-10-30, capture census/round-46/sources/rename2-reopen.txt; first opened 2026-10-25)
verified-at: 2026-10-30 — Linux man-pages pages as served 2026-10-30 and re-opened live 2026-10-31; no host kernel probe is made or claimed
recheck: 90d — re-open https://man7.org/linux/man-pages/man2/renameat2.2.html and the two captures under census/round-46/sources/
ground: F4 — restorable quarantine (restore-side collision semantics)

# A restore into a reoccupied origin path silently replaces the occupant under plain rename(2) — a receipt-gated restore must refuse or rename aside on EEXIST

## Claim (F4, sourced; no tool change, no receipt class, no deletion authority)

**What this entry is:** the restore-side completion of F4's staging semantics.
`quarantine-staging-no-copy-r23.md` holds the *into-quarantine* direction (the
no-clobber staging move). This entry holds the *out-of-quarantine* direction:
what happens when a restore puts an artifact back onto an origin path that
something else has occupied in the meantime.

1. **Plain rename(2) replacement is atomic and silent.**
   "If newpath already exists, it will be atomically replaced" — so that
   "there is no point at which another process attempting to access newpath
   will find it missing" (S110, § DESCRIPTION, re-open capture
   census/round-46/sources/rename2-reopen.txt). A restore that issues a plain
   rename onto a reoccupied origin therefore *overwrites the occupant with no
   error and no window*: the data the occupant held is gone, and the restore
   looks successful.
2. **RENAME_NOREPLACE turns the same move into a refusal.**
   "Don't overwrite newpath of the rename. Return an error if newpath already
   exists." (S268, § DESCRIPTION, `flags` argument, capture
   census/round-46/sources/renameat2-located-quote.txt). The error is spelled
   out: "EEXIST flags contains RENAME_NOREPLACE and newpath already exists."
   (S268 § ERRORS, re-open capture rename2-reopen.txt). The flag needs
   per-filesystem support (S268 § DESCRIPTION; S110's schedule) and cannot be
   combined with RENAME_EXCHANGE (S268).
3. **The lane consequence: a receipt-gated restore must be no-clobber.**
   The audit's own law is *dry-run by default, quarantine before delete*. A
   restore is the inverse of quarantine; if the origin path was reoccupied,
   blindly restoring would destroy a file the lane does not own a receipt
   for. So the restore primitive this ground requires is: attempt
   `renameat2(..., RENAME_NOREPLACE)`; on `EEXIST`, either refuse the restore
   (leave the quarantined artifact in place, surface the collision) or rename
   the returning artifact aside — never overwrite the occupant. Where the
   flag is unsupported, the fallback is an explicit pre-check plus
   `link(2)`/`rename(2)` composition or refusal, not a bare rename(2).

## What this does NOT establish
- **No tool change and no receipt class are made or authorized.** The lane's
  restore tooling is operator-owned; this entry only names the filesystem
  fact a future design must respect.
- **Per-filesystem support is a precondition, not a fact about any host.**
  S268/S110 state the support schedule; this entry runs no kernel probe and
  claims nothing about NTFS or the Windows host the fleet currently lands on.
- `RENAME_NOREPLACE` is not `RENAME_EXCHANGE`, and the two cannot be combined
  (S268). An exchange-based restore is a different design with different
  residue, not covered here.
- The HELD entry `quarantine-same-filesystem-rename.md` keeps its own limits;
  nothing here re-opens its `/dev/shm` device holding.
- Deletion, certification and cross-domain authority are unchanged:
  certification OFF, K5 HELD, NAMESPACE/reap holds unchanged.

## Lane link and consequence
F4's restore direction previously had no sourced collision semantics: the
staging entry (r23) covered moves *into* quarantine only. With S268 opened,
the restore side has the same shape of ground: the refusal primitive exists
and is spelled at the syscall level, so a future restore-tool proposal can be
written against EEXIST handling instead of against folklore. The remaining
operator decisions (receipt format, restore-tool change) stay open exactly as
the r23 entry left them.

## Gate

url: https://man7.org/linux/man-pages/man2/renameat2.2.html
snapshot: census/round-46/sources/renameat2-located-quote.txt
opened: 2026-10-30
re-opened live 2026-10-31 by the r46 landing session (HTTP 200, quotes
re-verified verbatim on the served page).

- ADMIT: "Don't overwrite newpath of the rename. Return an error if newpath already exists." — § DESCRIPTION, RENAME_NOREPLACE flag — reason: the refusal semantics the restore-side no-clobber requirement rests on — snapshot: census/round-46/sources/renameat2-located-quote.txt
- ADMIT: "If newpath already exists, it will be atomically replaced" — § DESCRIPTION, plain rename(2) paragraph — reason: names the silent-replacement hazard of an unguarded restore — snapshot: census/round-46/sources/rename2-reopen.txt
- ADMIT: "EEXIST flags contains RENAME_NOREPLACE and newpath already exists." — § ERRORS, renameat2 additional errors — reason: the exact errno a receipt-gated restore branches on — snapshot: census/round-46/sources/rename2-reopen.txt
- REJECT: staged candidate trash-spec restore-collision rule (S269) — reason: https://specifications.freedesktop.org/trash-spec/latest/ served the freedesktop 404 page on 2026-10-30 (census/round-46/sources/trash-latest-404.txt), so no spec text exists at this access to ground any rule — flip: a later access serves the spec and its restore/expunge section addresses occupied original paths.
