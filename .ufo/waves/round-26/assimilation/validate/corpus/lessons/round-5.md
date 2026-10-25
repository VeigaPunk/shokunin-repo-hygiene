# Round 5 — verification gate
Admitted: V1 calibration (verdict audit), V2 coverage (missed-items),
V3 operability (regression + fixes).
The round's purpose was finding defects; it found them; all material ones
were corrected in-round. 0 unresolved contradictions at closure.

## Material findings (all corrected or dispositioned in-round)

1. **Symlink false-SAFE class (both tools)** — `dir_digest` used
   `find -type f`, silently omitting symlinks: a source tree with
   `alias.md -> payload.md` and no alias in the vault verified
   SAFE(moved-to-obsidian). Reproduced by judges S63/S64. Fix: any
   symlink in a digest scope → fail closed (`symlink-present`).
   Verified: reproduction probe now refuses; selftests 24/24 + 35/35.
2. **Local-master pushed fallback (both tools)** — zero remote-tracking
   refs → SAFE(pushed) from `refs/heads/master`, which cannot establish
   pushed. Fix: no remote-tracking ref → `pushed-unverifiable`. The r2
   spec text permitting the fallback is amended in this round.
   Verified: local-master probe now NOT-SAFE(pushed-unverifiable).
3. **r1 false-SAFE row (logs_tier.txt)** — recorded SAFE(pushed) after
   the file was already deleted (delete commit a1b44b1 predates the census
   commit; the r1 parent correction checked introducing-commit ancestry
   but not existence). No operational impact (r3 re-cut; absent from the
   96-row actionable list). Correction entry in LOG; procedure fix:
   pushed corrections must re-verify existence at correction time.
4. **Pin risk (r3 follow-up)** — the 3 gd2d named-branch registrations
   were unlocked post-prune, leaving them bare-prune-eligible. Re-locked
   durably (r5); disposition rides on game-dev-2d pushing wt-r98/99/100.

## Process findings (recorded, no fix claimed)

- r1 commit 652b6f8 inserted a LOG.md section mid-file — an append-only
  violation (historical; procedure now: LOG entries append at EOF).
- r4's "vault read-only throughout" claim conflicts with a sibling seat's
  harness launching the Obsidian app during adversarial tests (config
  metadata rewritten; no vault content touched). Disclosed in the r5
  report; r4's verdicts are unaffected (all probes read-only by design).
- SKILL.md receipt guidance drifted from the installed tools — routed to
  the next content round (not silently patched mid-verification).

## Calibration measurement

Auditor-vs-lane verdict agreement: ~all audited verdicts reproduce; the
3 material findings above were caught by non-author judges and corrected
same-round. r5 demonstrates the fleet's verification loop closes.
